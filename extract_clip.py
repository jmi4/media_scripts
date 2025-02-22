"""
extract_clip.py

This script extracts a 3-second clip from an MP4 video file, avoiding the first and last 20 minutes of the video.
It uses the moviepy library to handle video processing. Additionally, it can process multiple movies from a specified
directory and extract clips from them.

Usage:
    python extract_clip.py --source <source_directory> --output <output_directory> --count <number_of_movies>

Arguments:
    --source: Path to the source directory containing MP4 files.
    --output: Path to the output directory where clips will be saved.
    --count: Number of movies to process.

Example:
    python extract_clip.py --source ~/foo/bar --output /Volumes/foo/bar --count 50

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
    February 22, 2025
"""

import argparse
import sys
from moviepy import VideoFileClip
import random
import os
import glob

def extract_clip(input_file, output_file, duration=3, buffer_minutes=20):
    try:
        input_file = os.path.expanduser(input_file)
        output_file = os.path.expanduser(output_file)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        video = VideoFileClip(input_file)
        total_duration = video.duration
        buffer_seconds = buffer_minutes * 60
        
        if total_duration < (2 * buffer_seconds + duration):
            raise ValueError("Video is too short")
        
        min_start = buffer_seconds
        max_start = total_duration - buffer_seconds - duration
        start_time = random.uniform(min_start, max_start)
        end_time = start_time + duration
        
        clip = video.subclipped(start_time, end_time)  # subclip is correct, subclipped was a typo
        clip.write_videofile(output_file,
                           codec='libx264',
                           audio_codec='aac',
                           logger=None)
        
        video.close()
        clip.close()
        print(f"Extracted 3-second clip from {int(start_time // 60)}:{int(start_time % 60):02d} to {output_file}")
        
    except Exception as e:
        print(f"An error occurred with {input_file}: {str(e)}")

def process_multiple_movies(source_dir, output_dir, num_movies):
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
        extract_clip(movie_path, output_file)

def main():
    parser = argparse.ArgumentParser(description="Extract 3-second clips from multiple MP4 files.")
    parser.add_argument("--source", required=True, help="Path to the source directory containing MP4 files.")
    parser.add_argument("--output", required=True, help="Path to the output directory where clips will be saved.")
    parser.add_argument("--count", type=int, required=True, help="Number of movies to process.")
    args = parser.parse_args()
    process_multiple_movies(args.source, args.output, args.count)

if __name__ == "__main__":
    main()