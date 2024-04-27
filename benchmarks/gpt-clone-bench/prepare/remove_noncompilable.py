#!/usr/bin/env python3
import argparse
import javalang
import sys
from pathlib import Path


"""
This script checks whether all files in a dataset directory can be parsed with javalang.
Any file that generates parser/syntax/lexer errors will be deleted.
"""

# dont delete files
DRY_RUN = False

def parse_args() -> argparse.Namespace:
        """
        Parses command line arguments.

        Returns:
            command line arguments passed
        """
        parser = argparse.ArgumentParser(
            description="""Remove java files which generate errors in javalang parser.""")
        
        parser.add_argument("-i", "--input", required=True, 
                            help="'standalone' directory with java files from gptCloneBench")
        
        return parser.parse_args()

def check_file(filePath: Path) -> int:
    """
    Check wether a file can be parsed with javalang.
    If not, delete it.

    Args:
        filePath (Path): The path to the Java source file.

    """
    with open(filePath, 'r', encoding='utf-8') as file:
        fileContent = file.read()

    try:
        javalang.parse.parse(fileContent)
        return 0
    except (javalang.parser.JavaSyntaxError, javalang.tokenizer.LexerError) as exc:
        print(f"Delete file {filePath} because of error: {exc}")
        if not DRY_RUN:
            filePath.unlink()
        return 1


def main(directoryPath: str):
    """
    Counts the number of method declarations in all Java source files within a directory,
    using javalang parser. Print the file if the number of methods is not 2.

    Args:
        directoryPath (str): The path to the directory.
    """
    deletedFiles = 0

    javaFiles = Path(directoryPath).rglob('*.java')
    for javaFile in javaFiles:
        deletedFiles += check_file(javaFile)
    
    print(f"number of deleted files: {deletedFiles}")

if __name__ == "__main__":

    args = parse_args()

    directoryPath = args.input
    main(directoryPath)

# vorher: 17058
# nachher: 69
