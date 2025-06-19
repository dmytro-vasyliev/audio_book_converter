"""Audio Book Converter package for converting M4A files to MP3 segments."""

__version__ = "0.1.0"

from .converter import AudioBookConverter, convert_and_split_m4a_to_mp3

__all__ = ["AudioBookConverter", "convert_and_split_m4a_to_mp3"]