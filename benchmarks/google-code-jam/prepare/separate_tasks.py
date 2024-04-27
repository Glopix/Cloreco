#!/usr/bin/env python3
import argparse
from bs4 import BeautifulSoup
from pathlib import Path
import shutil
"""
This script extracts all java file references from Google Code Jam html files
and copies the java files into a directory that corresponds to the task they are supposed to solve.

It iterates through all HTML files named index*.html, 
parsing each to identify <a> tags with a data-lang="java" attribute, 
indicative of links to Java source files. 
For each Java file referenced, the script calculates its target directory
based on its ordinal position within its parent <tr> element 
and moves the file into a correspondingly numbered subdirectory within the solutions folder. 

"""

def parse_args():
    """
    Parses command line arguments.

    Returns:
        Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="""Extract all java files from Google Code Jam html files and 
        sorts them into a directory that corresponds to the task they are supposed to solve.""")
    
    parser.add_argument("-d", "--directory", required=True, 
                        help="Path to the google code jam directory", default=Path(__file__))
    
    parser.add_argument("-s", "--all-sub-tasks", required=False, action="store_true", 
                        help="""extract all sub tasks (e.g.: A1, A2, A3, B1, B2, C1, C2, C3). 
                        default: extract only the first ones (e.g.: A1, B1, C1)""")
    
    parser.add_argument("-v", "--verbose", required=False, action="store_true", 
                        help="display all copied files")
    
    parser.add_argument("-m", "--min-files", required=False, default=5, type=int,
                        help="""minimum amount of files in a directory. 
                        If a directory has less than this amount of files, it will be deleted.
                        Useful in case a task has no/very few .java file submissions""")
    
    parser.add_argument("-l", "--lang-type", required=False, default="java",
                        help="""Language type of source code file. default: java. 
                        Needs to correspond to the 'data-lang' in .../<round>/index.html file(s).""")
    return parser.parse_args()


def filter_sub_tasks(taskNames: list):
    """
    e.g. 
    input:  ['A1', 'A2', 'A3',   'B1', 'B2',  'C1', 'C2',  'D1', 'D2']
    return: ['A1', False, False, 'B1', False, 'C1', False, 'D1', False]
    """
    # track seen first characters (e.g. 'A' from 'A1')
    seen = set()

    # Modify the list based on the condition
    newTaskNames = []
    for name in taskNames:
        if name[0] not in seen:
            # keep the first occurrence
            newTaskNames.append(name)
            # mark this first character as seen 
            seen.add(name[0])  
        else:
            # replace subsequent occurrences with False
            newTaskNames.append(False)

    return newTaskNames

def process_html_file(htmlFile: Path, subTask: bool, lang: str, verbose: bool) -> None:
    """
    htmlFile:   html file, which will be parsed and used to extract all java files from the 'solutions/' directory
    subTask:    extract all sub tasks (e.g.: A1, A2, A3, B1, B2). default: extract only the first ones (e.g.: A1, B1)
    lang:       Language of source code file. default: java. Needs to correspond to the 'data-lang' in .../<round>/index.html file(s)
    verbose:    print all copied files
    """
    basePath = htmlFile.parent

    with htmlFile.open('r', encoding='utf-8') as file:
        htmlContent = file.read()

    soup = BeautifulSoup(htmlContent, 'html.parser')

    try:
        thead = soup.find('thead').find_all('tr')[2]
    except IndexError as exc:
        print(f"error in: {htmlFile}")
        raise exc

    # remove all empty tr's, so only task names remain
    taskNames = [t.next for t in thead if t.next not in {"\n", "="} and t != "\n"]
    taskNames.sort()

    if not subTask:
        taskNames = filter_sub_tasks(taskNames)

    tbody = soup.find('tbody')
    for tr in tbody.find_all('tr'):
        # find all java files
        javaLinks = tr.find_all('a', {'data-lang': lang})

        for index, javaLink in enumerate(javaLinks):
            if not taskNames[index]:
                continue

            sourceFile = basePath / javaLink['href']
            targetDir = basePath / taskNames[index]
            targetDir.mkdir(exist_ok=True)

            # Copy the file
            if sourceFile.exists():
                shutil.copy(sourceFile, targetDir / sourceFile.name)
                if verbose: print(f'File "{sourceFile}" copied to "{targetDir}/"')
            else:
                print(f'Error: File "{sourceFile}" does not exist.')
                exit(1)


if __name__ == "__main__":
    args = parse_args()

    path = Path(args.directory).resolve()

    # iterate over all index*.html files in the path's subdirectories
    for dir in path.iterdir():
        for htmlFile in dir.rglob('index*.html'):
            # skip this html file if it is in a 'problems' directory
            if 'problems' in htmlFile.parts:
                continue

            process_html_file(htmlFile, subTask= args.all_sub_tasks, lang=args.lang_type, verbose=args.verbose)

            # delete a directory, if it has less than the specified amount of files in it
            # Useful in case a task has no/very few .java file submissions
            for dir in htmlFile.parent.iterdir():
                if dir.is_file(): continue
                fileCount = sum(1 for item in dir.iterdir() if item.is_file())
                if fileCount < args.min_files:
                    shutil.rmtree(dir)


