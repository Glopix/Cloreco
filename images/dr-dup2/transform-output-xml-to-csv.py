#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET

"""
example input:
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<clones>
    <clone nlines="10" similarity="100">
        <source file="selected/1280642.java" startline="41" startcolumn="5" endline="50" endcolumn="5"/>
        <source file="selected/551501.java" startline="46" startcolumn="5" endline="55" endcolumn="5"/>
        <source file="selected/95284.java" startline="50" startcolumn="5" endline="59" endcolumn="5"/>
    </clone>
</clones>

example output:
selected,1280642.java,41,50, selected,551501.java,46,55
selected,1280642.java,41,50, selected,95284.java,50,59
"""

def parse_clone_pairs(inputPath, outputPath):
    tree = ET.parse(inputPath)
    root = tree.getroot()

    with open(outputPath, "w") as out:
        for clone in root.findall("clone"):
            sources = []
            for source in clone.findall("source"):
                filePath = source.attrib["file"]
                if "/" in filePath:
                    dir_part, file_part = filePath.rsplit("/", 1)
                else:
                    dir_part, file_part = "", filePath
                startline = source.attrib["startline"]
                endline = source.attrib["endline"]
                sources.append(f"{dir_part},{file_part},{startline},{endline}")

            # Write all unique source pairs
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    out.write(f"{sources[i]}, {sources[j]}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Extract clone source pairs from an XML file into a CSV file."
    )
    parser.add_argument("inputFile", help="Path to the input XML file")
    parser.add_argument("outputFile", help="Path to the output CSV file")

    args = parser.parse_args()
    parse_clone_pairs(args.inputFile, args.outputFile)

if __name__ == "__main__":
    main()
