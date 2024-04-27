#!/usr/bin/env python3

import argparse
from pathlib import Path
from math import ceil

"""
Divides the total number of files in each subdirectory of a given base path by a specified number, 
creating new subdirectories to distribute the files evenly. This script is useful for managing 
large collections of files by organizing them into more manageable chunks.
"""

def parse_args() -> argparse.Namespace:
        """
        Parses command line arguments.

        Returns:
            command line arguments passed
        """
        parser = argparse.ArgumentParser(description="Split directories into multiple subdirectories, distributing files evenly.")
        parser.add_argument("-i", "--input", "--input-directory", type=Path, required=True,
                            help="Path to the base directory containing subdirectories to split.")
        parser.add_argument("-n", "--number", "--divide-number", type=int, required=True,
                            help="Number by which to divide the number of files in each directory, determining the number of new subdirectories.")

        return parser.parse_args()

def split_directories(basePath: Path, divideBy: int) -> None:
    """
    Splits files from each subdirectory under the specified base path into new subdirectories,
    distributing them based on the divideBy parameter, 
    by calculating the number of files per new subdirectory and moving the files accordingly.

    Parameters:
        basePath (Path): The base directory containing subdirectories to be split.
        divideBy (int): The number by which to divide the total number of files in each subdirectory.  
    """
    for subdir in basePath.iterdir():
        if not subdir.is_dir(): continue
        print(f"splitting directory: {subdir}")

        files = list(subdir.glob("*"))
        totalFiles = len(files)

        if totalFiles == 0: continue
        
        # calculate how many files should go into each new directory
        filesPerDir = ceil(totalFiles / divideBy)

        # create new directories and distribute the files
        for dirIndex in range(divideBy):
            targetDir = basePath / str(dirIndex) / subdir.name
            targetDir.mkdir(parents=True, exist_ok=True)

            movedFiles = 0

            startIndex = dirIndex * filesPerDir
            endIndex = startIndex + filesPerDir

            for file in files[startIndex:endIndex]:
                file.rename(targetDir / file.name)
                movedFiles += 1

            print(f"moved {movedFiles} files from {subdir} to {targetDir}")


if __name__ == "__main__":
    args = parse_args()
    split_directories(args.input, args.number)
