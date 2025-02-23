"""
random_file_list.py

This script lists all files in a specified directory in random order and saves the list to a text file.

Usage:
    python random_file_list.py <directory> -o <output_file>

Arguments:
    directory: The directory to scan for files.
    -o, --output: Output file path for the randomized list.

Example:
    python random_file_list.py ~/my_directory -o randomized_files.txt

Dependencies:
    - os
    - random
    - argparse
    - pathlib

Author:
    Jeremy Miller

Date:
    February 23, 2025
"""

import os
import random
import argparse
from pathlib import Path

def list_files_randomly(directory, output_path):
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Shuffle the list randomly
    random.shuffle(files)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write files to output path
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for file_name in files:
                f.write(f"{file_name}\n")
        print(f"Successfully wrote {len(files)} filenames to {output_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="List all files in a directory in random order and save to a text file"
    )
    parser.add_argument(
        "directory",
        help="The directory to scan for files"
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output file path for the randomized list"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert directory to absolute path
    directory = os.path.abspath(args.directory)
    
    # Check if directory exists
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory")
        return
    
    # Process the files
    list_files_randomly(directory, args.output)

if __name__ == "__main__":
    main()