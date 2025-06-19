import os
import subprocess
import argparse


def convert_and_split_m4a_to_mp3(source_folder):
    # Ensure the source folder exists
    if not os.path.isdir(source_folder):
        print(f"Folder '{source_folder}' does not exist.")
        return

    # Iterate through files in the source folder
    for filename in os.listdir(source_folder):
        if filename.endswith(".m4a"):
            # Get full path of the m4a file
            m4a_path = os.path.join(source_folder, filename)
            print(f"Processing file: {m4a_path}")
            # Create a directory for the m4a file
            base_name = os.path.splitext(filename)[0]
            output_folder = os.path.join(source_folder, base_name)
            os.makedirs(output_folder, exist_ok=True)

            # Construct the ffmpeg command to convert and split the m4a file
            ffmpeg_command = [
                "ffmpeg",
                "-i", m4a_path,  # Input file
                "-f", "segment",  # Output format is segmented
                "-segment_time", "300",  # Split every 300 seconds (5 minutes)
                "-c:a", "mp3",  # Set the audio codec to mp3
                os.path.join(output_folder, f"%03d_{base_name}.mp3")  # Output filename pattern
            ]

            # Run the ffmpeg command
            subprocess.run(ffmpeg_command)


def main():
    parser = argparse.ArgumentParser(description='Convert and split m4a files to mp3 format.')
    parser.add_argument('source_folder', type=str, help='Path to the folder containing m4a files')

    args = parser.parse_args()

    convert_and_split_m4a_to_mp3(args.source_folder)


if __name__ == "__main__":
    main()
