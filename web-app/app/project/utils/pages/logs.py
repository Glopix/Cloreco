"""
these functions are used by the "Logs" page(s) of the website
and the associated routes in the views.py file
"""
import project.settings as settings
from flask import url_for
from pathlib import Path
from project.utils.configure import configure_redis

def get_log_history(logCategory="run") -> list:
    """
    Retrieve the log history of the latest 'run' or 'imageBuild' activity.

    This function first fetches the location of the log file for the specified category ('run' or 'imageBuild') from a Redis database. 
    It then reads and returns all log entries from the log file located at the retrieved path. 

    If the run status or log file path is not found in the Redis database (indicating no such activity has been executed yet, or the log data is missing),
    the function returns a list containing a single message indicating that no logs are available for the specified category.

    Parameters:
        logCategory (str, optional): The category of logs to retrieve. Defaults to 'run'.
                                Valid options are 'run' for run logs and 'imageBuild' for image build logs.

    Returns:
        list: A list of log entries as strings. Each entry corresponds to a line in the log file.

    Raises:
        ValueError: If logCategory is not one of the expected values ('run' or 'imageBuild').

    Usage Example:
    >>> log_entries = get_log_history("run")
    >>> for entry in log_entries:
    >>>     print(entry)
    """
    if logCategory not in {'run', 'imageBuild'}:
        raise ValueError("logCategory not in {'run', 'imageBuild'}")

    redis = configure_redis()

    logFile = redis.get(f"{logCategory}.log")
    runStatus = redis.get(f"{logCategory}.status")

    if runStatus == None or logFile == None:
        return [f"No {logCategory} has been executed yet."]
    
    logFile = Path(logFile)

    logHistory = ""
    if logFile.is_file():
        with open(logFile, 'r') as log:
            logHistory = [line for line in log]  

    return logHistory

def get_container_progress(logCategory="run") -> dict:
    """
    Retrieve the current progress of a container's execution process.

    This function returns a dictionary representing the current state and progress of a container's execution.
    The returned dictionary varies depending on the logCategory parameter:
      - For "run", it fetches the progress details from a Redis database.
      - For "imageBuild", it returns a dictionary with the status set to "disabled", as the progress tracking
        feature is not supported for the image building process.

    The returned dictionary structure for "run" includes:
      - status (str): Indicates the current status of the container's execution (e.g., "running", "no run", "finished", "aborted").
      - currentStep (int): The current step number in the execution process.
      - totalSteps (int): The total number of steps in the execution process.
      - currentMessage (str): A message about the current step or executed tool.

    In case of "imageBuild", the dictionary contains:
      - status (str): Set to "disabled" indicating that progress tracking is not available.

    Parameters:
        logCategory (str, optional): Specifies the category of logs. Defaults to "run". Valid options are "run" and "imageBuild".

    Returns:
        A dictionary containing progress details or a status indicating the feature is disabled.

    Raises:
        ValueError: If logCategory is not one of the expected values ('run' or 'imageBuild').

    Usage Example:
    >>> progress_info = get_container_progress("run")
    >>> print(progress_info)
    {
        "status"        : "running",
        "currentStep"   : 2,
        "totalSteps"    : 5,
        "currentMessage": "Executing NiCad...",
        "isExecuted"    : True
    }
    """
    if logCategory not in {'run', 'imageBuild'}:
        raise ValueError("logCategory not in {'run', 'imageBuild'}")

    redis = configure_redis()

    # get dict from redis database
    progress = redis.hgetall(f"{logCategory}.progress")

    # is or was a run executed? 
    if progress in [ None, {} ]:
        #print("no progress yet?")

        return {
            "status"      : "no run",
            "currentStep" : 0,
            "totalSteps"  : 0,
            "currentMessage" : "No run has been executed yet.",
            "isExecuted" : "False"
            }

    return progress


def get_SSE_channels(logCategory) -> tuple[str, str, str]:
    """
    Generate and return URLs for Server-Sent Event (SSE) channels based on the specified log category.

    This function creates URLs for three different types of SSE channels:
      - Logs Channel:       For streaming log data.
      - Progress Channel:   For tracking the progress of ongoing processes.
      - Heartbeats Channel: For sending regular heartbeats to indicate activity.

    The specific channels generated depend on the logCategory parameter, which determines the context:
      - "run": Channels for containers where the current run is executed.
      - "imageBuild": Channels for the image building process, typically for building new images from git repositories.

    Parameters:
        logCategory (str): A string specifying the category of logs. Valid values are "run" and "imageBuild".

    Returns:
        Tuple[str, str, str]: A tuple containing the URLs for the logs, progress, and heartbeats channels, respectively.

    Raises:
        ValueError: If logCategory is not one of the expected values ('run' or 'imageBuild').

    Usage Example:
    >>> logs_url, progress_url, heartbeats_url = get_SSE_channels("run")
    """      
    
    match logCategory:
        case "run" | "imageBuild":
            channelPrefix = logCategory
        case _:
            raise ValueError("logCategory not in {'run', 'imageBuild'}")
        
    
    logsChannel = url_for('sse.stream', channel=f"{channelPrefix}_logs")
    progressChannel = url_for('sse.stream', channel=f"{channelPrefix}_progress")
    heartbeatsChannel = url_for('sse.stream', channel=f"{channelPrefix}_heartbeats")

    return logsChannel, progressChannel, heartbeatsChannel
 


