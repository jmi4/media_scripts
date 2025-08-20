"""
convert_album_to_alac.py

Convert all .m4a files (with FLAC audio) in an album directory to ALAC, preserving metadata.
Optionally move converted files to a destination directory and/or delete source files.

Usage:
    python3 convert_album_to_alac.py <album_directory> [-d <destination_directory>] [-r]

Arguments:
    <album_directory>            Path to the directory containing .m4a files
    -d <destination_directory>   Optional destination directory (album folder will be created inside)
    -r                          Optional flag to remove source files after conversion

Example:
    python3 convert_album_to_alac.py "/Users/YourUser/Music/Band/Album" -d "~/Destination/Music" -r
"""
import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

def get_metadata(input_file):
    """Extract metadata from m4a file using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format_tags=title,artist,album,track,disc,date,album_artist',
        '-of', 'json', str(input_file)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        tags = data.get('format', {}).get('tags', {})
        return tags
    except Exception as e:
        print(f"Warning: Could not extract metadata for {input_file}: {e}")
        return {}

def get_audio_codec(input_file):
    """Get audio codec using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,codec_type',
        '-of', 'json', str(input_file)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                return stream.get('codec_name')
        return None
    except Exception as e:
        print(f"Warning: Could not get codec for {input_file}: {e}")
        return None

def convert_file(input_file, output_file, metadata):
    """Convert m4a file to ALAC using ffmpeg, preserving metadata."""
    cmd = [
        'ffmpeg', '-i', str(input_file), '-c:a', 'alac', '-map', '0:a:0', '-map', '-0:v'
    ]
    for key, value in metadata.items():
        cmd += ['-metadata:s:a:0', f'{key}={value}']
    cmd.append(str(output_file))
    print(f"Converting: {input_file} -> {output_file}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Success: {output_file}")
        return True
    else:
        print(f"Error converting {input_file}: {result.stderr}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert FLAC-in-M4A album to ALAC, preserving metadata.")
    parser.add_argument('album_dir', help='Path to album directory containing .m4a files')
    parser.add_argument('-d', '--dest', help='Destination directory (album folder will be created inside)', default=None)
    parser.add_argument('-r', '--remove', action='store_true', help='Remove source files after conversion')
    args = parser.parse_args()

    album_dir = Path(args.album_dir).resolve()
    if not album_dir.is_dir():
        print(f"Error: Directory '{album_dir}' does not exist.")
        sys.exit(1)

    dest_dir = Path(args.dest).resolve() if args.dest else None
    if dest_dir:
        dest_dir.mkdir(parents=True, exist_ok=True)
        album_name = album_dir.name
        dest_album_dir = dest_dir / album_name
        dest_album_dir.mkdir(parents=True, exist_ok=True)
    else:
        dest_album_dir = album_dir

    m4a_files = sorted(album_dir.glob('*.m4a'))
    if not m4a_files:
        print(f"Error: No .m4a files found in '{album_dir}'.")
        sys.exit(4)

    print(f"Found {len(m4a_files)} .m4a files in {album_dir}")
    processed, failed, skipped = 0, 0, 0
    skipped_files = []

    for input_file in m4a_files:
        if not input_file.is_file():
            print(f"Skipping non-file: {input_file}")
            skipped += 1
            skipped_files.append(str(input_file))
            continue
        if input_file.name.endswith('_alac.m4a'):
            print(f"Skipping already converted file: {input_file}")
            skipped += 1
            skipped_files.append(str(input_file))
            continue
        codec = get_audio_codec(input_file)
        if codec != 'flac':
            print(f"Skipping non-FLAC file: {input_file} (codec: {codec})")
            skipped += 1
            skipped_files.append(str(input_file))
            continue
        metadata = get_metadata(input_file)
        if dest_dir:
            output_file = dest_album_dir / input_file.name
        else:
            output_file = input_file.parent / (input_file.stem + '_alac.m4a')
        if output_file.exists():
            print(f"Skipping file, output already exists: {output_file}")
            skipped += 1
            skipped_files.append(str(input_file))
            continue
        success = convert_file(input_file, output_file, metadata)
        if success:
            processed += 1
            if args.remove:
                input_file.unlink()
                print(f"Deleted source file: {input_file}")
        else:
            failed += 1
            if output_file.exists():
                output_file.unlink()

    print(f"Conversion complete. Processed: {processed}, Failed: {failed}, Skipped: {skipped}")
    if skipped_files:
        print("Skipped files:")
        for f in skipped_files:
            print(f"  {f}")
    print(f"Converted files are in: {dest_album_dir}")
    print("Next steps:")
    print(f"1. Use MusicBrainz Picard to tag the converted files in {dest_album_dir}.")
    print("2. Import into Apple Music via File > Add to Library or copy to ~/Music/Media/Automatically Add to Music.")

if __name__ == '__main__':
    main()
