import project.settings as settings
from flask import send_file, send_from_directory, redirect, request, jsonify
from pathlib import Path
import os
from datetime import datetime
import zipfile
from shutil import rmtree
from io import BytesIO
import pandas as pd
from project.utils.configure import configure_redis

def input_path_is_valid(path: str|Path) -> bool:
    """
    Safety check: make sure the destination path is a child path of the base (downloads) directory
    to ensure no files outside of the downloads directory can be leaked

    Returns: bool
    """
    baseDir = Path(settings.directories["runs"])

    path = Path(path)
    path = path.resolve()

    if path.is_relative_to(baseDir) and path.exists():
        return True
    else:
        return False

def list_directory_content(directory: str):
    """
    Returns:
     a list of all files and 
     a list of all diagrams in a specified directory,
     a list of dicts, containing the data of the summary.csv file, if there is a summary.csv file in this directory.
    Every entry of the first list contains:
     the path (relativ to the "runs" directory), 
     name, size, modification timestamp and 
     whether or not this entry is a file or a directory.
    """
    files = []
    baseDir = Path(settings.directories["runs"])

    if not directory:
        directory = ""
    directory = Path(directory)

    directoryPath = baseDir / directory

    # safety check: make sure the destination directory is a child directory of the base (downloads) directory
    # to ensure no files outside of the downloads directory can be leaked
    if not input_path_is_valid(directoryPath):
        return None

    # list of diagram files, to be displayed in the web file browser
    diagrams = []

    # data of the summary.csv file. This data will be displayed in an interactive plot in JavaScript on the webclient
    summary = None

    # list all files in the directory
    for file in os.listdir(directoryPath):
        # real file system path
        filePath = directoryPath / file

        # size of the file or directory
        size = get_path_size(filePath)

        # path in the web interface ( example.com/downloads/<directory>/<file> )
        webPath = directory / file

        if filePath.is_dir():
            isDir = True
            if not str(webPath).endswith("/"):
                webPath = f"{webPath}/"
        else:
            isDir = False

        files.append({
                'path': webPath,
                'name': file,
                'size': size,
                'modified': datetime.fromtimestamp(filePath.stat().st_mtime).replace(microsecond=0),
                'is_dir': isDir,
            })
        
        #
        if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', 'svg')):
            diagrams.append(webPath)

        diagrams.sort()

        if file == "summary.csv":
            summary = get_csv_data(filePath)
            #print(summary)

    return files, diagrams, summary

def get_csv_data(csv: Path):
    """
    Returns:
     a list of dicts, containing the data of the specified csv file.
    """

    df = pd.read_csv(csv)
    # convert the DataFrame to a list of dictionary for JSON response
    # The elements of these dictionries are the rows from the csv
    return df.to_dict(orient='records')
    """ e.g.:
    Name,           Runtime,    Type,       numDetected
    StoneDetector,  13.24,      Type-1,     20828
    StoneDetector,  13.24,      Type-2,     3475
    StoneDetector,  13.24,      Type-2 (blind), 242
    ->
    [{'Name': 'StoneDetector', 'Runtime': 13.24, 'Type': Type-1, 'numDetected': 20828},
    {'Name': 'StoneDetector', 'Runtime': 13.24, 'Type': Type-2, 'numDetected': 3475},
    {'Name': 'StoneDetector', 'Runtime': 13.24, 'Type': Type-2 (blind), 'numDetected': 242}]
    """

# Helper function to calculate directory size
def get_path_size(path: Path):
    """
    Calculate the size (in Bytes) of a directory.
    """
    path = Path(path)

    size = 0
    if path.is_file():
        size = path.stat().st_size
    else:
        size = sum(file.stat().st_size for file in path.rglob('*'))

    return size

def serve_file(filePath: str):
    """
    Serve a file as download.
    """
    baseDir = Path(settings.directories["runs"])
    filePath = Path(filePath)
    filePath = baseDir / filePath

    # safety check: make sure the destination file is a child of the base (downloads) directory
    # to ensure no files outside of the downloads directory can be leaked
    if not input_path_is_valid(filePath):
        return None
    
    fileDir = filePath.parent
    file = filePath.name
    
    return send_from_directory(fileDir, file)

def path_download(path: str):
    """
    Serve a path (file or directory) as download.
    If a directory is requested, the directory will be zipped as a in memory zip file.
    """
    baseDir = Path(settings.directories["runs"])
    path = baseDir / path
    fileName = path.name

    if not input_path_is_valid(path):
        return None

    if not path.exists():
        return "Directory not found", 404
    
    if path.is_dir():
        # Create a in memory zip file with the contents of the directory
        zipFile = BytesIO()
        with zipfile.ZipFile(zipFile, mode='w') as z:
            for file in path.rglob('*'):
                z.write(file, arcname=os.path.relpath(file, path))
        zipFile.seek(0)

        # send the in memory zip file to client
        return send_file(
            zipFile,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{fileName}.zip"
        )
    else:
        return send_from_directory(
            path.parent,
            path.name,
            as_attachment=True
        )
    

def path_delete(path: str):
    """
    Delete a path (directory or file)
    """

    redis = configure_redis()

    currentRunDir = redis.get('run.directory')
    runIsRunning = redis.hget('run.progress', 'isExecuted')
    runStatus = redis.get('run.status')

    baseDir = Path(settings.directories["runs"])
    path = baseDir / path

    if not path.exists():
        return "File not found", 404
    
    if not input_path_is_valid(path):
        return "invalid Path", 403

    # dont delete the directory if this is the directory of the current executed run
    if path.is_relative_to(currentRunDir) and runIsRunning == "True" and runStatus!="failed":
        return "This file or directory is currently in use", 423

    if path.is_dir():
        rmtree(path)
        return "Directory deleted", 200
    else:
        path.unlink()
        return "File deleted", 200
