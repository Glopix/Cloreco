#!/usr/bin/env python3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def readAllFunctionInfos():
    functionDict = {}
    with open(BASE_DIR.parent / "tokenizers/block-level/file_block_stats/files-stats-0.stats") as f:
        fileName = ""
        subFolderName = ""
        for line in f:
            line = line.rstrip()
            parts = line.split(",")
            #print(parts)

            if line.startswith("f"):
                filePath = parts[2].strip('"')
                filePathParts = filePath.split("/")
                
                subFolderName = filePathParts[1]
                fileName = filePathParts[2]
            else:
                id = parts[1]
                startline = parts[-2]
                endline = parts[-1]
                functionDict[id] = f"{subFolderName},{fileName},{startline},{int(endline)+3}"
    return functionDict


if __name__ == "__main__":
    functionDict = readAllFunctionInfos()
    with open(
        BASE_DIR.parent / "clone-detector/NODE_1/output8.0/query_1clones_index_WITH_FILTER.txt"
    ) as f:
        for line in f:
            line = line.rstrip()
            parts = line.split(",")
            one = functionDict.get(parts[1])
            two = functionDict.get(parts[3])
            if one is not None and two is not None:
                print(f"{one},{two}")
