#!/usr/bin/env python3
from pathlib import Path
import sys
import argparse

"""
Some files contain illegal characters , like '\?' in a System.out.println() statement, which results in compile errors.
This script removes these illegal characters.
"""

def parse_args():
    # argument parsing
    parser = argparse.ArgumentParser(description='Sort directories based on their third character.')
    parser.add_argument('-i', '--input-directory', type=str, help='Path to the input directory')
    return parser.parse_args()

def remove_illegal_chars(inputFilePath: Path, outputFilePath: Path =False) -> None:
    """
    Reads Java code from the input file
    and removes illegal characters ('\?')

    Args:
        inputFilePath (Path): The path to the input file containing Java code.
        outputFilePath (Path): The path to the output file to write modified Java code.
    """
    if not outputFilePath:
        outputFilePath = inputFilePath

    with open(inputFilePath, 'r') as file:
        lines = file.readlines()

    outputLines = []
    for line in lines:
        if "System.out.println(" in line:
            line = line.replace("\?","")
        outputLines.append(line)

    with open(outputFilePath, 'w') as file:
        file.writelines(outputLines)


if __name__ == "__main__":
    args = parse_args()
    inputDirPath = Path(args.input_directory)

    for inputdir in inputDirPath.iterdir():
        if inputdir.is_file():
            continue

        processedFiles = 0
        
        for file in inputdir.iterdir():
            remove_illegal_chars(file)
            processedFiles += 1
    
        print(f"Processed {processedFiles} files in {inputdir}/")