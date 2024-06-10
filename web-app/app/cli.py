#!/usr/bin/env python3
import argparse
from project.utils.Run import setupRun, executeRun
from project.utils.configure import configure_redis
from project.utils.pages import run


"""
This script can be used to start a Run from the CLI. 
Benchmarks and detector tools to be executed 
need to be specified as options and the config files of each
benchmarks and detector tool need to exist beforehand.
The 

"""

def start(detectorToolsSpecified:list, benchmarksSpecified:list, runDir: str, runName: str):
    """
    Initiates a run with specified benchmarks and clone detector tools.

    This function sets up and starts a run using the provided arguments for 
    benchmarks and clone detector tools. It validates the specified benchmarks 
    and detector tools, ensuring they exist in the setup, and updates the 
    form data accordingly to emulate a submitted web form.

    Args:
        - detectorToolsSpecified (list): List of detector tools to be used and executed in this run.
        - benchmarksSpecified (list): List of benchmarks to be used and executed in this run.

    Raises:
        ValueError: If any of the specified benchmarks or detector tools 
                    could not be found in there respctive directories:
                    data/cloneDetection/benchmarks/     and
                    data/cloneDetection/cloneDetectorTools/workbench/
    
    Example:
        args = argparse.Namespace(detector_tools=['StoneDetector', 'tool2'], benchmarks=['BigCloneEval', 'benchmark2'], runDir='/app/data/cloneDetection/myDir')
        start(args)
    """

    formData = {
        "runName" : runName,
    }

    setup = setupRun.SetupRun(formData, cliMode=True, importDir=runDir)

    selectedBenchmarks = []
    benchmarks = []
    for benchmark in setup.benchmarks:
        if benchmark['name'] in benchmarksSpecified:
            selectedBenchmarks.append((f"{benchmark['filename']}--selected", "on"))
            benchmarks.append(benchmark["name"])
            benchmarksSpecified.remove(benchmark["name"])
    print(f"selected benchmarks: {benchmarks}")
    if benchmarksSpecified:
        raise ValueError(f"These benchmarks could not be found: {benchmarksSpecified}")

    selectedDetectorTools = []
    detectorTools = []
    for detector in setup.detectorTemplates:
        if detector['detectorName'] in detectorToolsSpecified:
            selectedDetectorTools.append((f"{detector['filename']}--selected", "on"))
            detectorTools.append(detector['detectorName'])
            detectorToolsSpecified.remove(detector['detectorName'])
    print(f"selected clone detector tools: {detectorTools}")
    if detectorToolsSpecified:
        raise ValueError(f"These clone detector tools could not be found: {detectorToolsSpecified}")

    for key, value in selectedBenchmarks + selectedDetectorTools:
        formData[key] = value

    setup.formData = formData

    msg = setup.start_run()
    print(msg['message'])
    if msg['type'] == "success":
        # remove the "/app/" path component
        runDirSeenFromHost = setup.runDir.relative_to("/app/")
        print(f"Run directory: {runDirSeenFromHost}")
        print(f"Run log: {runDirSeenFromHost.joinpath("run.log")}")
    else:
        exit(1)

def stop():
    """
    Stops and aborts the currently running Run.
    """
    msg = run.abort_run()
    print(msg['message'])


def main():
    parser = argparse.ArgumentParser(description="Manage Run via CLI")
    parser.add_argument("command", choices=["start", "stop"], 
                        help="Command to execute: start or stop a Run")
    parser.add_argument("--benchmarks", nargs='*', 
                        help="Benchmarks to execute")
    parser.add_argument("--detector-tools", nargs='*', 
                        help="Clone detector tools to execute")
    parser.add_argument("--run-name", type=str, default="", 
                        help="Name of this run")
    parser.add_argument("--directory", type=str, 
                        help=("Path to the directory containing benchmark and detector tool configuration files. "
                          "The contents of this directory will be copied to a new directory under data/cloneDetection/runs/, "
                          "making it accessible via the website. "
                          "Please note: The path IN the container need to be specified, so if your directory is at 'data/cloneDetection/myDir',"
                          "you need to enter '/app/data/cloneDetection/myDir'"
                          "Example template directory: data/cloneDetection/CLI_run_template/")
                          )

    args = parser.parse_args()

    if args.command == "start":
        if not args.directory:
            parser.error("--directory is required when command is 'start'. Example template directory:  /app/data/cloneDetection/CLI_run_template")
        if not args.benchmarks:
            parser.error("--benchmarks is required when command is 'start'")
        if not args.detector_tools:
            parser.error("--detector-tools is required when command is 'start'")
        start(list(args.detector_tools), list(args.benchmarks), args.directory, args.run_name)
    elif args.command == "stop":
        stop()

if __name__ == "__main__":
    main()
