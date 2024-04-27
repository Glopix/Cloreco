#!/usr/bin/env python3
import argparse
from pathlib import Path

"""
This script sorts directories in the specified input directory based on their third character, 
moving them to a corresponding subdirectory named after that character.

e.g. input/p032428 will be moved to input/3/p032428

"""

def parse_args():
    # argument parsing
    parser = argparse.ArgumentParser(description='Sort directories based on their third character.')
    parser.add_argument('-i', '--input-directory', type=str, help='Path to the input directory')
    return parser.parse_args()

def sort_directories_by_thirdChar(inputDir: str) -> None:
    inputDir = Path(inputDir)

    if not inputDir.exists() or not inputDir.is_dir():
        print(f"The directory {inputDir} does not exist.")
        return

    # Iterate through each directory in inputDir that starts with 'p'
    for dirPath in inputDir.glob('p*/'):
        # Extract the 3rd character of the directory name
        thirdChar = dirPath.name[2]

        targetSubDir = inputDir / thirdChar

        # Create the target subdirectory if it does not exist
        targetSubDir.mkdir(exist_ok=True)

        # Move the directory into the corresponding subdirectory
        new_path = targetSubDir / dirPath.name
        dirPath.rename(new_path)
        print(f"Moved {dirPath} to {new_path}")

    

if __name__ == "__main__":
    args = parse_args()
    sort_directories_by_thirdChar(args.input_directory)
