#!/usr/bin/env python3
"""
create java files with classes, 
since GPTCloneBench files include methods, but no classes
"""
import os
import sys
from os import listdir
from os.path import isfile, join

def changeFunctionName(line: str,id):
    bracketId = line.find("(")
    tmpLine=line[0:bracketId]
    split=tmpLine.split(" ")
    if split[-1]=='':
        functionName=split[-2]
    else:
        functionName=split[-1]
    return line.replace(functionName,functionName+"_"+str(id))


def countOccurences(line, count):
    c1 = line.count("{")
    c2 = line.count("}")
    return (count+c1-c2)


if __name__ == '__main__':
    inputfiles = [ f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1], f))]
    c=0
    os.mkdir(sys.argv[1] + "_o")
    for f in inputfiles:
        inputfile = open(join(sys.argv[1], f), 'r')
        outputfile = open(join(sys.argv[1]+"_o", f), 'w')
        outputfile.write("class A{\n")
        start=True
        count=0
        secondFunction=False
        changecount=0
        while True:
            line = inputfile.readline()
            if (not line):
                break
            if start:
                line=changeFunctionName(line,changecount+1)
                changecount+=1
                start=False
                count = countOccurences(line, count)
                outputfile.write(line)
                continue
            count = countOccurences(line, count)
            outputfile.write(line)
            if count==0 and changecount==1:
                line=inputfile.readline()
                while line=="\n":
                    line = inputfile.readline()
                line = changeFunctionName(line, changecount+1)
                changecount+=1
                outputfile.write(line)
        outputfile.write("}")
        c+=1
    print("done "+str(c))




