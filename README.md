# Audio Book Converter

A web application and command-line tool to convert M4A audio books to segmented MP3 files for older MP3 players with limited navigation controls. The tool splits audio files into 5-minute segments by default, making it easy to navigate through audio books on devices with simple controls.

## Features

- Convert M4A files to MP3 format
- Split audio books into customizable segments (default: 5 minutes)
- Web interface with drag-and-drop functionality
- Command-line interface for batch processing
- Support for processing entire directories

## Requirements

- Python 3.7+
- FFmpeg (must be installed on your system)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/audio_book_converter.git
   cd audio_book_converter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure FFmpeg is installed on your system:
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - macOS (with Homebrew): `brew install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Usage

### Web Interface

Start the web interface with:

```bash
python -m audio_book_converter.web
```

Then open your browser to http://localhost:7860 (default Gradio port).

### Command Line

To convert all M4A files in a directory:

```bash
python -m audio_book_converter.cli /path/to/directory
```

You can customize the segment time (in seconds):

```bash
python -m audio_book_converter.cli /path/to/directory --segment-time 180
```

### Use as a Library

```python
from audio_book_converter import AudioBookConverter

# Create a converter with custom segment time (in seconds)
converter = AudioBookConverter(segment_time=300)  # 5 minutes

# Convert a single file
success, output_dir = converter.convert_file("path/to/audiobook.m4a")
if success:
    print(f"Converted files saved to: {output_dir}")
else:
    print(f"Error: {output_dir}")

# Or convert an entire directory
results = converter.convert_directory("path/to/directory")
for filename, (success, result) in results.items():
    print(f"{filename}: {'Success' if success else 'Failed'} - {result}")
```

## Docker Deployment

```bash
# Build the Docker image
docker build -t audio_book_converter .

# Run the container
docker run -p 7860:7860 audio_book_converter
```

## Development

### Running Tests

```bash
pytest
```

To generate a coverage report:

```bash
pytest --cov=audio_book_converter
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
