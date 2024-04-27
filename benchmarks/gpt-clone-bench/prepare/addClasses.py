#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
import re

DRY_RUN = False

class AddClass:
    def __init__(self) -> None:
        self.methodCounter = 1
        self.classCounter = 1

    def parse_args(self) -> argparse.Namespace:
        """
        Parses command line arguments.

        Returns:
            command line arguments passed
        """
        parser = argparse.ArgumentParser(
            description="""add Classes to gptCloneBench files""")
        
        parser.add_argument("-i", "--input", required=True, 
                            help="'standalone' directory with java files from gptCloneBench")
        parser.add_argument("-o", "--output", required=False, default=False, 
                            help="(optional) seperate output directory. If this argument is missing, the original files will be overwritten.")
        
        return parser.parse_args()

    def wrap_methods(self, inputFilePath: Path, outputFilePath: Path =False) -> None:
        """
        Reads Java code from the input file,
        wraps the modified code in a class, and writes the result to the output file.
        If no output file is specified, the input file will be overwritten.

        Args:
            inputFilePath (Path): The path to the input file containing Java code.
            outputFilePath (Path): The path to the output file to write modified Java code.
        """
        if not outputFilePath:
            outputFilePath = inputFilePath

        def newClassName(name):
            self.classCounter += 1
            name = name.group(0)
            return f"{name}_{self.classCounter}"

        self.methodCounter = 1
        self.classCounter = 1

        classPattern = r'(?:public\s)?(?:class|interface|enum)\s+([^\s{]+)(?=\s*{)'

        with open(inputFilePath, 'r') as file:
            input = file.read()

        content = input
        # extract all import statements
        imports = re.findall(r'import\s+.*?;\n', content)
        content = re.sub(r'import\s+.*?;\n', '', content)

        content = re.sub(r'\n{4,}', '\n\n\n', content)
        content = content.rstrip("\n")
        content = re.split(r'(?:})\n\n\n', content)
        content = [part + '}' if i < len(content) - 1 else part for i, part in enumerate(content)]
        out = []

        for clone in content:
            if re.findall(classPattern, clone):
                
                out.append(re.sub(classPattern, newClassName, clone))
                #lines = clone.split("\n")
            else:
                out.append(f"class A{self.classCounter} {{ \n" + clone + "\n}\n\n")
                self.classCounter += 1

        publicclassPattern = r'(?:public\s)(?:class|interface|enum)\s+([^\s{]+)(?=\s*{)'

        if not re.findall(publicclassPattern, input):
            out[0] = f"public {out[0]}"

        output = ""
        # insert import statements at start of file
        for imp in imports:
            output += imp
        if imports:
            output += "\n"
        
        for part in out:
            output += part

        if DRY_RUN:
            return
        with open(outputFilePath, 'w') as file:
            file.write(output)
        

    def main(self):
        args = self.parse_args()

        inputDirPath = Path(args.input).absolute()
        if args.output:
            outputDirPath = Path(args.output)
            outputDirPath.mkdir(exist_ok=True)

        for inputDir in inputDirPath.iterdir():
            if inputDir.is_file():
                continue

            if args.output: 
                outputDir = outputDirPath / inputDir.name
                outputDir.mkdir(exist_ok=True)
            processedFiles = 0
            
            for file in inputDir.iterdir():
                if args.output: 
                    outFile = outputDir / file.name
                else: 
                    outFile = False
                self.wrap_methods(file, outFile)
                processedFiles += 1
        
            print(f"Processed {processedFiles} files in {inputDir}/")


if __name__ == "__main__":
    ac = AddClass()
    ac.main()
