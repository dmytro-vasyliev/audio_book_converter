#!/usr/bin/env python3
"""Command-line interface for Audio Book Converter."""

import argparse
import sys
from pathlib import Path

from audio_book_converter import AudioBookConverter


def main():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(
        description='Convert and split M4A files to MP3 format.'
    )
    parser.add_argument(
        'source_folder',
        type=str,
        help='Path to the folder containing M4A files'
    )
    parser.add_argument(
        '--segment-time',
        type=int,
        default=300,
        help='Time in seconds for each segment (default: 300 seconds/5 minutes)'
    )

    args = parser.parse_args()
    source_path = Path(args.source_folder)

    if not source_path.is_dir():
        print(f"Error: '{source_path}' is not a directory.")
        sys.exit(1)

    converter = AudioBookConverter(segment_time=args.segment_time)
    results = converter.convert_directory(source_path)

    if not results:
        print(f"No M4A files found in '{source_path}'.")
        sys.exit(0)

    # Print summary of results
    success_count = 0
    failure_count = 0

    for filename, (success, result) in results.items():
        if success:
            success_count += 1
            print(f"✓ {filename} -> {result}")
        else:
            failure_count += 1
            print(f"✗ {filename}: {result}")

    print(f"\nSummary: {success_count} files converted successfully, {failure_count} failures.")


if __name__ == "__main__":
    main()
