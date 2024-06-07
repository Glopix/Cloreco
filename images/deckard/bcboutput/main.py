#!/usr/bin/env python3

from os import environ

if __name__ == "__main__":
    filterOutput = False
    if environ.get('BENCHMARK_NAME') == "BigCloneEval":
        filterOutput = True

    if filterOutput:
        functionSet = set()
        with open("Functions.txt") as f:
            for line in f:
                line = line.rstrip()
                functionSet.add(line)
    
    with open("../clusters/post_cluster_vdb_125_2_allg_0.70_50") as f:
        parts = []
        for line in f:
            if line == "\n":
                for part in parts:
                    foundpart = False
                    for part2 in parts:
                        if foundpart:
                            print(part + "," + part2)
                        if part == part2:
                            foundpart = True
                parts = []
            else:
                line = line.rstrip()
                splittedLine = line.split()
                splittedFullpath = splittedLine[3].split("/")
                subFolder = splittedFullpath[len(splittedFullpath) - 2]
                fileName = splittedFullpath[len(splittedFullpath) - 1]
                lines = splittedLine[4].split(":")
                startLine = int(lines[1])
                endLine = startLine + int(lines[2]) - 1
                functionIdent = (
                    subFolder + "," + fileName + "," + str(startLine) + "," + str(endLine)
                )
                if filterOutput:
                    if functionIdent in functionSet:
                        parts.append(functionIdent)
                else:
                    parts.append(functionIdent)
