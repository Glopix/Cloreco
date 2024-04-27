#!/usr/bin/env python3
import argparse
import javalang
import sys
from pathlib import Path

"""
This script counts the number of method declarations in all Java source files within a directory, using javalang parser. 
It print the filepath if the number of methods is not 2,
prints the filepath if parser/syntax/lexer errors occure and
counts how many parser/syntax/lexer errors occured in the whole dataset.

"""

errors = 0

def parse_args() -> argparse.Namespace:
        """
        Parses command line arguments.

        Returns:
            command line arguments passed
        """
        parser = argparse.ArgumentParser(
            description="""Counts the number of method declarations in a Java source file using javalang parser.
            Print the file if the number of methods is not 2.""")
        
        parser.add_argument("-i", "--input", required=True, 
                            help="'standalone' directory with java files from gptCloneBench")
        
        return parser.parse_args()

def count_methods_in_file(filePath: Path):
    """
    Counts the number of method declarations in a Java source file using javalang parser.

    Args:
        filePath (Path): The path to the Java source file.

    Returns:
        int: The number of methods found in the file.
    """
    with open(filePath, 'r', encoding='utf-8') as file:
        fileContent = file.read()

    global errors
    try:
        tree = javalang.parse.parse(fileContent)
        return sum(1 for _ in tree.filter(javalang.tree.MethodDeclaration))
    except javalang.tokenizer.LexerError as e:
        print(f"Lexer error in file {filePath}: {e}")
        errors += 1
        return 0
    except javalang.parser.JavaSyntaxError as exc:
        print(f"Syntax error in file {filePath}: {exc}")
        errors += 1
        return 0

def count_methods_in_directory(directoryPath: str):
    """
    Counts the number of method declarations in all Java source files within a directory,
    using javalang parser. Print the file if the number of methods is not 2.

    Args:
        directoryPath (str): The path to the directory.
    """
    javaFiles = Path(directoryPath).rglob('*.java')
    for javaFile in javaFiles:
        methodsCount = count_methods_in_file(javaFile)
        if methodsCount != 2:
            print(f"{javaFile}: {methodsCount} methods")
    
    global errors
    print(f"errors: {errors}")

if __name__ == "__main__":

    args = parse_args()

    directoryPath = args.input
    count_methods_in_directory(directoryPath)

# before addClasses.py: 17058
# after  addClasses.py: 69
