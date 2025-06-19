import os
import subprocess
import logging
from pathlib import Path
from typing import List, Union, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AudioBookConverter:
    """Converts M4A audio files to MP3 format and splits them into smaller segments.

    This class provides functionality to convert M4A audio files to MP3 format
    and split them into smaller segments, which is useful for loading onto
    devices with limited navigation capabilities.
    """

    def __init__(self, segment_time: int = 300):
        """Initialize the converter with the specified segment time.

        Args:
            segment_time: Time in seconds for each segment (default: 300 seconds/5 minutes)
        """
        self.segment_time = segment_time

    def convert_file(self, input_file: Union[str, Path], output_dir: Optional[Union[str, Path]] = None) -> Tuple[bool, str]:
        """Convert a single M4A file to MP3 segments.

        Args:
            input_file: Path to the input M4A file
            output_dir: Directory where to save the converted files. If None, a directory 
                        with the same name as the input file will be created in the same location.

        Returns:
            A tuple containing (success_status, output_directory)
        """
        input_path = Path(input_file)

        # Check if the file exists and has the correct extension
        if not input_path.exists():
            error_msg = f"Input file does not exist: {input_path}"
            logger.error(error_msg)
            return False, error_msg

        if input_path.suffix.lower() != ".m4a":
            error_msg = f"Input file must be an M4A file, got: {input_path.suffix}"
            logger.error(error_msg)
            return False, error_msg

        # Create output directory if not specified
        if output_dir is None:
            output_dir = input_path.parent / input_path.stem
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True, parents=True)

        # Construct the ffmpeg command
        base_name = input_path.stem
        ffmpeg_command = [
            "ffmpeg",
            "-i", str(input_path),  # Input file
            "-f", "segment",  # Output format is segmented
            "-segment_time", str(self.segment_time),  # Split according to segment_time
            "-c:a", "mp3",  # Set the audio codec to mp3
            "-y",  # Overwrite output files without asking
            str(output_dir / f"%03d_{base_name}.mp3")  # Output filename pattern
        ]

        try:
            # Run the ffmpeg command
            logger.info(f"Processing file: {input_path}")
            result = subprocess.run(
                ffmpeg_command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors='replace'  # Handle non-UTF8 characters in ffmpeg output
            )
            logger.info(f"Successfully converted {input_path} to MP3 segments")
            return True, str(output_dir)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error converting {input_path}: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg

    def convert_directory(self, source_folder: Union[str, Path]) -> Dict[str, Tuple[bool, str]]:
        """Convert all M4A files in a directory to MP3 segments.

        Args:
            source_folder: Path to the folder containing M4A files

        Returns:
            A dictionary mapping filenames to (success_status, output_directory/error_message) tuples
        """
        source_path = Path(source_folder)

        # Ensure the source folder exists
        if not source_path.is_dir():
            logger.error(f"Folder '{source_path}' does not exist.")
            return {}

        results = {}
        # Iterate through files in the source folder
        for file_path in source_path.glob("*.m4a"):
            results[file_path.name] = self.convert_file(file_path)

        return results


def convert_and_split_m4a_to_mp3(source_folder: Union[str, Path], segment_time: int = 300):
    """Convert M4A files in a directory to MP3 segments.
    
    This function maintains backward compatibility with the original script.
    
    Args:
        source_folder: Path to the folder containing M4A files
        segment_time: Time in seconds for each segment (default: 300 seconds/5 minutes)
    """
    converter = AudioBookConverter(segment_time=segment_time)
    return converter.convert_directory(source_folder)