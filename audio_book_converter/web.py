import os
import logging
import tempfile
import shutil
import zipfile
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union

import gradio as gr

from audio_book_converter.converter import AudioBookConverter


# Create a persistent directory for storing converted files within the project
OUTPUT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_zip_archive(files: List[str]) -> str:
    """Create a zip archive containing all the converted files.
    
    Args:
        files: List of file paths to include in the archive
        
    Returns:
        Path to the created zip archive
    """
    if not files:
        return ""
        
    # Create a timestamp for the zip filename
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    zip_path = str(OUTPUT_DIR / f"audiobook_mp3s_{timestamp}.zip")
    
    # Create the zip file
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
            
    return zip_path


def process_with_progress(file_path, segment_time: int = 300):
    """Process a file with progress updates.
    
    Args:
        file_path: Path to the uploaded file from Gradio
        segment_time: Time in seconds for each segment
        
    Yields:
        Progress updates and final results
    """
    if file_path is None:
        yield [], "Please upload a file first", None
        return
        
    # Use the file path directly since we're using type="filepath"
    input_file_path = file_path
    
    # Initial progress update
    yield [], "Starting conversion...", None
    
    # Convert the file - this part takes time, so we'll simulate progress updates
    converter = AudioBookConverter(segment_time=segment_time)
    start_time = time.time()
    
    # Do the actual conversion using the original file path
    success, result = converter.convert_file(input_file_path)
    
    if not success:
        yield [], f"Error: {result}", None
        return
        
    # Get list of converted files
    output_dir = Path(result)
    
    # Create a new unique subfolder in our persistent output directory
    timestamp = tempfile.mkdtemp(dir=OUTPUT_DIR)
    persistent_dir = Path(timestamp)
    
    # Simple delay for UI responsiveness
    time.sleep(0.5)
    
    # Copy the converted files to the persistent directory
    converted_files = []
    # Only get files matching our current naming format to avoid showing files from previous conversions
    for mp3_file in sorted(output_dir.glob("[0-9][0-9][0-9]_*.mp3")):
        # Copy the file to our persistent directory
        dest_file = persistent_dir / mp3_file.name
        shutil.copy2(mp3_file, dest_file)
        converted_files.append(str(dest_file))
    
    # Create a zip archive of all the output files
    zip_path = ""
    if converted_files:
        zip_path = create_zip_archive(converted_files)
        
    # Calculate final elapsed time
    elapsed = time.time() - start_time
    status_message = f"Successfully converted to {len(converted_files)} MP3 segments in {elapsed:.1f} seconds"
    
    # Make sure we're returning proper paths, not booleans
    yield converted_files, status_message, zip_path


def process_file(file_obj, segment_time: int = 300):
    """Process a single file uploaded through the Gradio interface.
    
    Args:
        file_obj: File object from Gradio (filepath string)
        segment_time: Time in seconds for each segment
        
    Returns:
        Tuple of (List of file paths, Status message, Zip archive path)
    """
    # This wrapper function is kept for compatibility
    # Progress handling is done in the actual implementation
    if file_obj is None or file_obj == "":
        return [], "Please upload a file first", None
    
    try:
        # Use the last value from the generator
        results = list(process_with_progress(file_obj, segment_time))
        if not results:
            return [], "Error: No results from conversion process", None
            
        files, message, zip_path = results[-1]
        
        # We don't need the input file path anymore since we removed the audio players
        return files, message, zip_path
    except Exception as e:
        logging.error(f"Error during file processing: {e}", exc_info=True)
        return [], f"Error during conversion: {str(e)}", None


def create_interface():
    """Create and configure the Gradio interface."""

    with gr.Blocks(title="Audio Book Converter") as interface:
        gr.Markdown(
            """
            # 📚 Audio Book Converter
            
            Upload M4A audiobook files and convert them to segmented MP3 files.
            Each file will be split into 5-minute segments by default.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload M4A File",
                    file_types=[".m4a"],
                    type="filepath"  # Use filepath instead of binary for better compatibility
                )
                segment_time = gr.Slider(
                    label="Segment Length (seconds)",
                    minimum=60,
                    maximum=600,
                    value=300,
                    step=30
                )
                convert_button = gr.Button("Convert to MP3", variant="primary")
                status = gr.Textbox(label="Status", value="Idle")

            with gr.Column(scale=1):                
                # Add a row for output files and download all button
                with gr.Row():
                    output_files = gr.Files(
                        label="Converted MP3 Files",
                        type="filepath",
                        interactive=False  # Make non-interactive to avoid upload buttons
                    )

                # Download all button for the zip archive
                download_all = gr.File(
                    label="Download All Files (ZIP)",
                    type="filepath",
                    interactive=False,
                    visible=False  # Start hidden, will be shown after conversion
                )
        
        # Handle file conversion with progress updates and update UI
        def process_and_update_download_all(file_path, segment_time):
            # Check if file is provided
            if file_path is None:
                # No file provided, show error message
                return [], "Please upload a file first", gr.File(value=None, visible=False)
                
            # Process the file and get results
            files, message, zip_path = process_file(file_path, segment_time)
            
            # Update download_all visibility and value
            download_all_visible = zip_path is not None and zip_path != ""
            
            # Return all outputs including visible parameter
            return files, message, gr.File(value=zip_path, visible=download_all_visible)
            
        convert_button.click(
            fn=process_and_update_download_all,
            inputs=[file_input, segment_time],
            outputs=[output_files, status, download_all],
            show_progress=True
        )
        
        # Audio preview functionality has been removed
        # No event handlers needed for file upload or selection
        
        # Add some descriptive text
        gr.Markdown("""
        ### How to use:
        1. Upload an M4A audiobook file
        2. Set the desired segment length in seconds (default: 300 seconds = 5 minutes)
        3. Click 'Convert to MP3' and wait for the process to complete
        4. Click 'Download All Files (ZIP)' to get everything in one file
        """)
        
    return interface


def main():
    """Run the Gradio interface."""
    interface = create_interface()
    # Add our output directory to allowed_paths and enable file sharing
    interface.launch(
        server_name="0.0.0.0", 
        allowed_paths=[str(OUTPUT_DIR)],
        max_threads=10  # Increase threads for better UI responsiveness
    )
    
if __name__ == "__main__":
    main()
