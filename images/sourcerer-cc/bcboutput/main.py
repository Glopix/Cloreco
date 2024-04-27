#!/usr/bin/env python3

def readAllFunctionInfos():
    functionDict = {}
    with open("../tokenizers/block-level/file_block_stats/files-stats-0.stats") as f:
        fileName = ""
        subFolderName = ""
        for line in f:
            line = line.rstrip()
            splittedLine = line.split(",")
            if line.startswith("f"):
                fileNameCompl = splittedLine[2]
                fileNameCompl = fileNameCompl[1 : len(fileNameCompl) - 1]
                fileNameWithoutFolder = fileNameCompl.split("/")[1]
                subFolderName = fileNameWithoutFolder.split("_")[0]
                fileName = fileNameWithoutFolder.split("_")[1]
            else:
                id = splittedLine[1]
                startline = splittedLine[len(splittedLine) - 2]
                endline = splittedLine[len(splittedLine) - 1]
                functionDict[id] = subFolderName+','+fileName+','+startline+','+str(int(endline)+3)
    return functionDict


if __name__ == "__main__":
    functionDict = readAllFunctionInfos()
    with open(
        "../clone-detector/NODE_1/output8.0/query_1clones_index_WITH_FILTER.txt"
    ) as f:
        for line in f:
            line = line.rstrip()
            splittedLine = line.split(",")
            one = functionDict.get(splittedLine[1])
            two = functionDict.get(splittedLine[3])
            if one is not None and two is not None:
                print(one + "," + two)
