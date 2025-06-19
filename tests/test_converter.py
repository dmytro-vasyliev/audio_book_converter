import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from audio_book_converter import AudioBookConverter


class TestAudioBookConverter(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.converter = AudioBookConverter(segment_time=60)  # 1 minute for faster tests

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def create_dummy_m4a_file(self, filename="test.m4a"):
        """Create an empty file with .m4a extension for testing."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w') as f:
            f.write("dummy content")
        return file_path

    @patch('subprocess.run')
    def test_convert_file_success(self, mock_subprocess_run):
        """Test successful conversion of a single file."""
        # Setup mock
        mock_subprocess_run.return_value = MagicMock(
            returncode=0,
            stdout="mocked stdout",
            stderr="mocked stderr"
        )

        # Create test file
        test_file = self.create_dummy_m4a_file()
        
        # Call the method
        success, result = self.converter.convert_file(test_file)
        
        # Assertions
        self.assertTrue(success)
        expected_output_dir = test_file.parent / test_file.stem
        self.assertEqual(str(expected_output_dir), result)
        
        # Verify ffmpeg was called with correct parameters
        mock_subprocess_run.assert_called_once()
        args, kwargs = mock_subprocess_run.call_args
        cmd = args[0]
        self.assertEqual(cmd[0], "ffmpeg")
        self.assertEqual(cmd[1], "-i")
        self.assertEqual(cmd[2], str(test_file))
        # Find segment_time parameter position
        segment_time_pos = cmd.index("-segment_time") + 1
        self.assertEqual(cmd[segment_time_pos], "60")  # Check segment time

    @patch('subprocess.run')
    def test_convert_file_failure(self, mock_subprocess_run):
        """Test handling of conversion failure."""
        # Setup mock to simulate failure
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="ffmpeg",
            stderr="mocked error"
        )

        # Create test file
        test_file = self.create_dummy_m4a_file()
        
        # Call the method
        success, result = self.converter.convert_file(test_file)
        
        # Assertions
        self.assertFalse(success)
        self.assertIn("Error converting", result)
        self.assertIn("mocked error", result)

    def test_convert_file_nonexistent_file(self):
        """Test handling of non-existent input file."""
        non_existent_file = Path(self.temp_dir) / "nonexistent.m4a"
        
        success, result = self.converter.convert_file(non_existent_file)
        
        self.assertFalse(success)
        self.assertIn("does not exist", result)

    def test_convert_file_invalid_extension(self):
        """Test handling of invalid file extension."""
        invalid_file = Path(self.temp_dir) / "invalid.txt"
        with open(invalid_file, 'w') as f:
            f.write("dummy content")
            
        success, result = self.converter.convert_file(invalid_file)
        
        self.assertFalse(success)
        self.assertIn("must be an M4A file", result)

    @patch('audio_book_converter.converter.AudioBookConverter.convert_file')
    def test_convert_directory(self, mock_convert_file):
        """Test directory conversion."""
        # Create a deterministic response mapping instead of side_effect sequence
        def convert_file_side_effect(input_file):
            filename = Path(input_file).name
            if filename == "file1.m4a":
                return (True, "output_dir1")
            elif filename == "file2.m4a":
                return (True, "output_dir2")
            elif filename == "file3.m4a":
                return (False, "error message")
            return (False, "unexpected file")
            
        mock_convert_file.side_effect = convert_file_side_effect
        
        # Create test directory with files
        Path(self.temp_dir).mkdir(exist_ok=True)
        self.create_dummy_m4a_file("file1.m4a")
        self.create_dummy_m4a_file("file2.m4a")
        self.create_dummy_m4a_file("file3.m4a")
        
        # Create some non-m4a files as well
        with open(Path(self.temp_dir) / "other.txt", 'w') as f:
            f.write("other content")
            
        # Call the method
        results = self.converter.convert_directory(self.temp_dir)
        
        # Assertions
        self.assertEqual(len(results), 3)  # Should have processed 3 m4a files
        self.assertEqual(mock_convert_file.call_count, 3)
        
        # Check results dictionary
        self.assertEqual(results["file1.m4a"], (True, "output_dir1"))
        self.assertEqual(results["file2.m4a"], (True, "output_dir2"))
        self.assertEqual(results["file3.m4a"], (False, "error message"))


if __name__ == '__main__':
    unittest.main()
