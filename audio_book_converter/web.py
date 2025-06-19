import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional

import gradio as gr

from audio_book_converter.converter import AudioBookConverter


# Create a persistent directory for storing converted files within the project
OUTPUT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def process_file(
    file_obj,
    segment_time: int = 300
):
    """Process a single file uploaded through the Gradio interface.
    
    Args:
        file_obj: File object from Gradio (can be bytes or a file-like object)
        segment_time: Time in seconds for each segment
        
    Returns:
        Tuple of (List of file paths, Status message)
    """
    if file_obj is None:
        return [], "Please upload a file first"
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Handle different ways Gradio might provide the file
        if isinstance(file_obj, bytes):
            # For newer Gradio versions that pass bytes directly
            file_name = "uploaded_audiobook.m4a"  # Default name
            temp_file = temp_path / file_name
            with open(temp_file, 'wb') as f:
                f.write(file_obj)
        else:
            # For older Gradio versions that pass file-like objects
            try:
                file_name = file_obj.name
                temp_file = temp_path / file_name
                with open(temp_file, 'wb') as f:
                    f.write(file_obj.read())
                # Reset file pointer
                file_obj.seek(0)
            except AttributeError as e:
                return [], f"Error with file upload: {str(e)}"
            
        # Convert the file
        converter = AudioBookConverter(segment_time=segment_time)
        success, result = converter.convert_file(temp_file)
        
        if not success:
            return [], f"Error: {result}"
        
        # Get list of converted files
        output_dir = Path(result)
        
        # Create a new unique subfolder in our persistent output directory
        timestamp = tempfile.mkdtemp(dir=OUTPUT_DIR)
        persistent_dir = Path(timestamp)
        
        # Copy the converted files to the persistent directory
        converted_files = []
        for mp3_file in sorted(output_dir.glob("*.mp3")):
            # Copy the file to our persistent directory
            dest_file = persistent_dir / mp3_file.name
            shutil.copy2(mp3_file, dest_file)
            converted_files.append(str(dest_file))
        
        status_message = f"Successfully converted to {len(converted_files)} MP3 segments"
        return converted_files, status_message


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
            with gr.Column():
                file_input = gr.File(
                    label="Upload M4A File",
                    file_types=[".m4a"],
                    type="binary"
                )
                segment_time = gr.Slider(
                    label="Segment Time (seconds)",
                    minimum=60,
                    maximum=600,
                    value=300,
                    step=30
                )
                convert_button = gr.Button("Convert to MP3", variant="primary")
                
            with gr.Column():
                output_files = gr.Files(label="Converted Files")
                status = gr.Textbox(label="Status", value="Ready to convert")
        
        convert_button.click(
            fn=process_file,
            inputs=[file_input, segment_time],
            outputs=[output_files, status]
        )
        
        # Add some descriptive text instead of problematic examples
        gr.Markdown("""
        ### How to use:
        1. Upload an M4A audiobook file
        2. Set the desired segment length in seconds (default: 300 seconds = 5 minutes)
        3. Click 'Convert' and wait for the process to complete
        4. Download the converted MP3 files
        """)
        
    return interface


def main():
    """Run the Gradio interface."""
    interface = create_interface()
    # Add our output directory to allowed_paths
    interface.launch(server_name="0.0.0.0", allowed_paths=[str(OUTPUT_DIR)])
    
if __name__ == "__main__":
    main()
