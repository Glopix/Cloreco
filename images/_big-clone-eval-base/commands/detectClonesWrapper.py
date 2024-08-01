#!/usr/bin/env python3
import argparse
from pathlib import Path
import subprocess
from shutil import rmtree
from os import chdir

# Big Clone Bench / IJaDataset directory: parent directory of this file
BCB_ijadataset_dir = Path(__file__).parent.parent / "ijadataset" / "bcb_reduced"

def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments.

    Returns:
        command line arguments passed
    """
    parser = argparse.ArgumentParser(
        description="""Executes the clone detection tool for IJaDataset in an automated procedure.
                Requires a script that configures and executes the tool, 
                and the scalability limits of the tool in terms of the maximum input size measured in source files.
                Used deterministic input partitioning to overcome scalability limits. 
                Optional, clone detection can be performed manually if desired.""")
    
    parser.add_argument("-b", "--benchmark-parts", required=False, default="all",
                    help=("Specify particular segments of the benchmark dataset for the clone detection tool to process, "
                        "instead of the entire dataset. " 
                        "Use comma-separated values for discrete parts (e.g., '12,3,4') "
                        "or a range for consecutive segments (e.g., '11-17'). " 
                        "Defaults to 'all', indicating the whole dataset. "
                        "Valid segment identifiers are the directory names in the IJaDataset/ directory."))
    
    args, unknown = parser.parse_known_args()
    return args, unknown


def convert_BigCloneBench_directory_input(inputParts: str) -> list:
    """
    Convert user input (entered on the website, stored in a config file entrypoint.cfg) 
    to a list of integers or '' if nothing or 'all' was specified by the user.
    This list of integers is the list of BigCloneBench dataset directories, on which the clone detector tool will be executed.

    Returns:
    list of integers or
    '' if nothing or 'all' was specified by the user
    """
    # split input string by commas and remove any extra whitespace
    inputNumbers = [part.strip() for part in inputParts.split(',')]

    # proceed with all BCB parts if nothing or 'all' was specified by the user
    if 'all' in inputNumbers or inputNumbers == ['']:
        return ""

    outputNumbers = []
    try:
        for part in inputNumbers:
            if '-' in part:
                # handle ranges like "1-8"
                start, end = map(int, part.split('-'))

                # if a range with start > end was entered, e.g.: "5-4"
                # only the start value will be accepted
                if start > end :
                    outputNumbers.append(int(end))
                else:
                    outputNumbers.extend(range(start, end + 1))
            elif part == '':
                continue
            else:
                # handle single integers
                outputNumbers.append(int(part))
    except ValueError:
        print("invalid input for 'benchmark-parts'")
        print("proceeding with all ijadataset parts")
        return ""

    return outputNumbers


def delete_directories_except(parentDir: str, exceptDirs: list) -> None:
    parentDir = Path(parentDir)
    # Get a list of all directories in the directory
    dirs = [dir for dir in parentDir.iterdir() if dir.is_dir()]

    # type conversion: convert all list entries from int to str, to match the types of the 'dirs' list
    exceptDirs = list(map(str, exceptDirs))
    # prepend the base path(parentDir) to each element in the exceptDirs array
    exceptDirs = [parentDir / dir for dir in exceptDirs]

    # Iterate through the directories and delete those not in the specified list
    for dir in dirs:
        if dir not in exceptDirs:
            dirPath = parentDir.joinpath(dir)
            if dirPath.exists():
                # delete the directory and its contents
                rmtree(dirPath)


def exclude_BigCloneBench_directories(benchmarkParts: str) -> None:
    """
    Excludes BigCloneBench directories from the detectTool execution.
    All BigCloneBench directories will be excluded, except the ones specified.
    e.g.: benchmarkParts = "3,4,5" -> all other directories will be excluded

    The exclusion is performed by deleting all BCB directories, except the ones specified.
    e.g.: benchmarkParts = "3,4,5" -> all other directories will be deleted

    If nothing was specified in benchmarkParts, detectTool will be executed on all BigCloneBench directories. 
    Which means no BCB directories need to be deleted
    """

    # on which BigCloneBench directories detectTool should be executed
    executeOnDirs = benchmarkParts
    if benchmarkParts.lower() in {'all', ''}:
        executeOnDirs = ''
    # which BigCloneBench directories will be keeped
    keepDirs = convert_BigCloneBench_directory_input(executeOnDirs)

    # if nothing was specified, detectTool will be executed on all BigCloneBench directories
    # so delete nothing
    if keepDirs == '':
        print(f"executing clone detection on all BCB directories", flush=True)
        return
    else:
        print(f"executing clone detection on these BCB directories: {keepDirs}", flush=True)


    delete_directories_except(BCB_ijadataset_dir, keepDirs)
    return

if __name__ == "__main__":
    args, detectClonesParameter = parse_args()
    benchmarkParts = args.benchmark_parts
    
    exclude_BigCloneBench_directories(benchmarkParts)

    commandsDir = Path(__file__).parent
    chdir(commandsDir)

    # pass through detectClones parameters
    command = ['./detectClones_bce']
    command.extend(detectClonesParameter)

    # start detectClones command
    subprocess.run(command, check=True)


