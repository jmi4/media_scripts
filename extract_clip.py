"""
extract_clip.py

This script extracts a clip of specified duration from an MP4 video file, avoiding the first and last 15% of the video.
It uses the moviepy library to handle video processing. Can process either a single file or multiple movies from a directory.

Usage:
    Single file: python extract_clip.py --input <input_file> --output <output_file> [--duration <seconds>]
    Multiple files: python extract_clip.py --source <source_directory> --output <output_directory> --count <number_of_movies> [--duration <seconds>]

Arguments:
    --input: Path to a single input MP4 file
    --output: Path to output file or directory
    --source: Path to source directory containing MP4 files (for multiple files)
    --count: Number of movies to process (for multiple files)
    --duration: Length of clip in seconds (default: 5)

Example:
    python extract_clip.py --input video.mp4 --output clip.mp4 --duration 7
    python extract_clip.py --source ~/videos --output ~/clips --count 10 --duration 5

Dependencies:
    - moviepy
    - argparse
    - os
    - random
    - sys
    - glob

Author:
    Your Name

Date:
    February 25, 2025
"""

import argparse
import sys
from moviepy import VideoFileClip
import random
import os
import glob

def extract_clip(input_file, output_file, duration=5):
    try:
        input_file = os.path.expanduser(input_file)
        output_file = os.path.expanduser(output_file)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        video = VideoFileClip(input_file)
        total_duration = video.duration
        
        if total_duration < (duration / 0.7):  # Ensure there's enough middle 70% for the clip
            raise ValueError("Video is too short for specified duration")
        
        # Avoid first and last 15% (using 70% of middle content)
        buffer_percent = 0.15
        min_start = total_duration * buffer_percent
        max_start = total_duration * (1 - buffer_percent) - duration
        start_time = random.uniform(min_start, max_start)
        end_time = start_time + duration
        
        clip = video.subclipped(start_time, end_time)
        clip.write_videofile(output_file,
                           codec='libx264',
                           audio_codec='aac',
                           logger=None)
        
        video.close()
        clip.close()
        print(f"Extracted {duration}-second clip from {int(start_time // 60)}:{int(start_time % 60):02d} to {output_file}")
        
    except Exception as e:
        print(f"An error occurred with {input_file}: {str(e)}")

def process_multiple_movies(source_dir, output_dir, num_movies, duration=5):
    source_dir = os.path.expanduser(source_dir)
    output_dir = os.path.expanduser(output_dir)
    movie_files = glob.glob(os.path.join(source_dir, "**", "*.mp4"), recursive=True)
    
    if len(movie_files) < num_movies:
        print(f"Warning: Only found {len(movie_files)} movies")
        num_movies = len(movie_files)
    
    selected_movies = random.sample(movie_files, num_movies)
    for i, movie_path in enumerate(selected_movies, 1):
        movie_name = os.path.splitext(os.path.basename(movie_path))[0]
        output_file = os.path.join(output_dir, f"{movie_name}_clip.mp4")
        print(f"Processing movie {i}/{num_movies}: {movie_name}")
        extract_clip(movie_path, output_file, duration)

def main():
    parser = argparse.ArgumentParser(description="Extract clips of specified duration from MP4 files.")
    parser.add_argument("--input", help="Path to a single input MP4 file")
    parser.add_argument("--output", required=True, help="Path to output file or directory")
    parser.add_argument("--source", help="Path to source directory containing MP4 files")
    parser.add_argument("--count", type=int, help="Number of movies to process")
    parser.add_argument("--duration", type=float, default=5, help="Length of clip in seconds (default: 5)")
    
    args = parser.parse_args()
    
    if args.input:  # Single file mode
        if args.source or args.count:
            print("Error: Use either --input for single file or --source/--count for multiple files, not both")
            sys.exit(1)
        extract_clip(args.input, args.output, args.duration)
    elif args.source and args.count:  # Multiple file mode
        process_multiple_movies(args.source, args.output, args.count, args.duration)
    else:
        print("Error: Must provide either --input or both --source and --count")
        sys.exit(1)

if __name__ == "__main__":
    main()