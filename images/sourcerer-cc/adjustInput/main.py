#!/usr/bin/env python3

import shutil
import sys
from pathlib import Path
from shutil import copyfile
import os

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) !=3:
        print("usage: python adjustInput inputDir outputDir")

    inputDir =sys.argv[1]
    outputDir=sys.argv[2]
    if not outputDir.endswith("/"):
        outputDir=outputDir+'/'

    if (os.path.exists(outputDir)):
        shutil.rmtree(outputDir)
    os.mkdir(outputDir)

    for path in Path(inputDir).rglob('*.java'):
        splittedFile=str(path).split("/")
        subfolder=splittedFile[(len(splittedFile)-2)]
        filename = splittedFile[(len(splittedFile) - 1)]
        copyfile(str(path),outputDir+subfolder+'_'+filename)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
