#!/usr/bin/env python3
import sys
import os
"""
reads output file of clone detector (.csv)
and counts found clones

at the moment, precision can not be calculated.
Precision = true positives / (true positives + false positives)
false positives is unknown, since many detected clones can be clones, even if they are not in the same file

"""

if __name__ == '__main__':
    alreadyPrinted=set()
    inputfile = sys.argv[1]
    file1 = open(inputfile, 'r')
    count=0
    while True:
        line = file1.readline()
        if not line:
            break
        line=line.rstrip()
        lineSplittet = line.split(",")
        if(lineSplittet[0]!= lineSplittet[4] or lineSplittet[1]!=lineSplittet[5] or lineSplittet[0]+lineSplittet[1] in alreadyPrinted):
            continue
        alreadyPrinted.add(lineSplittet[0]+lineSplittet[1])
        count=count+1
        print(line)
   
   
    print("")
    print(f"clone pairs in {inputfile}: {count}")

    benchmarkDir = sys.argv[2]
    sumFiles = sum([len(files) for r, d, files in os.walk(benchmarkDir)])
    print(f"number of files/clones in gptCloneBench: {sumFiles}")
    print(f"recall: {count/sumFiles}")