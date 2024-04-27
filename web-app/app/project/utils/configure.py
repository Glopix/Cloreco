from redis import Redis
import os
from pathlib import Path
from datetime import datetime
import project.settings as settings


def configure_redis() -> Redis:
    return Redis().from_url(os.getenv('FLASK_REDIS_URL'), decode_responses=True)


def get_run_directory(runName: str = "") -> Path:
    """
    "Create" a new directory for a run.
    "Create" means: only a Path object of the new path will be created, not the directory in the filesystem.
    If a runName is specified, this str will be appended to the directory name

    Returns:
        a Path object of the new path, containing the current date, time and runName, e.g.:
        
        call this function at 2023-12-23 13:37:24 with runName="testRun" will result in:

        "/app/project/cloneDetection/runs/2023-12-23___13-37-24_testRun"
    """

    packagePath = Path(__file__).parent.parent
    runDirectoryPath  = packagePath / settings.directories['runs']
    
    # 2023-01-01 15:10:25 -> 2023-01-01_15-10-25
    currentDateTime = datetime.today().strftime('%Y-%m-%d___%H-%M-%S')

    # clean input: remove path in runName, if there is one
    runName = Path(runName).name

    if runName:
        runDirectory = f"{currentDateTime}_{runName}"
    else:
        runDirectory = f"{currentDateTime}"

    # files of current run will be placed in  cloneDetection/runs/<currentDateTime>_<runName>/
    runDirectoryPath  = runDirectoryPath / runDirectory

    return runDirectoryPath
