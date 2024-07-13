#!/usr/bin/env python3
# python 3.4+ required for pathlib
import subprocess
from configparser import ConfigParser
from os import environ, chdir
from pathlib import Path
from time import time
from datetime import datetime

# path of the directory of this script
mainDir = Path(__file__).parent

# benchmark command directory
benchmarkCommandsDir = '/cloneDetection/benchmark/commands/'

# benchmark startup script location
benchmarkstartupScript = '/cloneDetection/benchmark/commands/benchmarkStartup.sh'

# read arguments for detectClones and evaluateTool from config file /cloneDetection/entrypoint.cfg
configFile = '/cloneDetection/entrypoint.cfg'

# verbose logging file, used for extra logging of the clone detection tool while detectClones execution
loggingVerboseFile = 'verbose.log'

# sections in config file (entrypoint.cfg) for these commands
evaluateToolSection = 'evaluateTool'
cloneDetectionSection = 'detectClones'

class BenchmarkRunner:
    """
    execute the following commands with paramters:
    - detectClones
    - evaluateTool
    - importClones

    Also executes the tool startup and benchmark startup scripts, if they are present.
    
    """

    def __init__(self) -> None:
        # read arguments for detectClones and evaluateTool from config file 
        self.config = ConfigParser()
        self.config.read(configFile)

        self.runnerScript = self.get_runner_script_path()
        self.env = self.get_logging_verbose_env()

        # report file, created by 'evaluateTool' command
        self.reportFile = self.config.get(evaluateToolSection, 'storage')

        self.assemble_benchmark_commands()


    def get_runner_script_path(self) -> Path:
        """
        get path of clone detector runner script from environmental variable
        """
        try:
            runnerScriptPath = Path(environ['RUNNER_SCRIPT_PATH'])
        except KeyError:
            raise KeyError("Environmental variable 'RUNNER_SCRIPT_PATH' not set")
        
        if not runnerScriptPath.is_file():
            raise FileNotFoundError(f"No file at '{runnerScriptPath}' (from Environmental variable RUNNER_SCRIPT_PATH)")
        
        return runnerScriptPath
        

    def get_logging_verbose_env(self) -> dict:
        """
        If 'logging_verbose' is set in the config file, set the env var for subprocess.run() to the path of the verbose log file.
        """
        loggingVerbose = self.config.get(cloneDetectionSection, 'logging_verbose').strip()
        global loggingVerboseFile
        loggingVerboseFile = mainDir.joinpath(loggingVerboseFile)

        if loggingVerbose in {"True", "true", "on", "On", "Yes", "yes"}:
            msg = "verbose logging: on"
            env = {
                # verbose log file: in the same directory as this script
                'LOGGING_VERBOSE': loggingVerboseFile
            }
        else:
            msg = "verbose logging: off"
            env = {}

        print(msg, flush=True)
        with open(loggingVerboseFile, "a") as file:
            file.write(f"{msg}\n\n")
        return env

    
    def run_tool_startup(self) -> None:
        """
        If 'STARTUP_SCRIPT_PATH' environmental variable is set and the script exists, 
        execute this bash script.
        This script is optional and can be used by the detector tool (creators)
        to perform preparation steps before the "main" execution 
        of the clone detector tool and the benchmark begins.
        """
        try:
            startupScript = Path(environ['STARTUP_SCRIPT_PATH'])
        except KeyError:  # env var not set
            startupScript = self.runnerScript.parent / "startup.sh"
            if not startupScript.is_file(): # startup.sh not in detector tool directory
                print("""(notice) skipping startup script, since environmental variable 'STARTUP_SCRIPT_PATH' is not set and 'startup.sh' is not in the detector tool's directory""")
                return
        
        if not startupScript.is_file():
            print(f"Environmental variable 'STARTUP_SCRIPT_PATH' is set, but there is no file (startup script) at '{startupScript}'")
            print("skipping startup script")
            return
        
        print(f"executing startup script '{startupScript}'")
        
        self.run_command(["bash", startupScript])


    def run_benchmark_startup(self) -> None:
        """
        If the script at 'benchmarkstartupScript' var path exists, execute this bash script.
        This script is optional and can be used by the benchmark (creators)
        to perform preparation steps before the "main" execution 
        of the clone detector tool and BigCloneEval begins.
        e.g. to execute the registerTool command in case of BigCloneEval 
        """
        startupScript = Path(benchmarkstartupScript)
       
        if not startupScript.is_file():
            return
        
        print(f"executing benchmark startup script '{startupScript}'")
        
        self.run_command(["bash", startupScript])


    def assemble_benchmark_commands(self) -> None:
        """
        assemble commands and arguments for benchmark commands
        """
        self.detectClones = [
            './detectClones',
            f"--output={self.config.get(cloneDetectionSection, 'storage')}",
            f"--tool-runner={self.runnerScript}",
            f"--max-files={self.config.get(cloneDetectionSection, 'max_files')}",
        ]
        self.append_options_to_detectTool()

        """
        self.clearClones = [
            './clearClones', 
            '--tool=1'
        ]
        """

        self.importClones = [
            './importClones',
            f"--clones={self.config.get(cloneDetectionSection, 'storage')}",
            "--tool=1"
        ] 

        self.evaluateTool = [
            './evaluateTool',
            '--tool=1',
            f"--output={self.config.get(evaluateToolSection, 'storage')}"
        ]
        self.append_options_to_evaluateTool()

    
    def append_options_to_detectTool(self) -> None:
        additionalOptions = self.config.items(cloneDetectionSection)

        # filter out already set options
        alreadySet = ['storage', 'max_files', 'logging_verbose']
        additionalOptions = [(name, value) for name, value in additionalOptions if name not in alreadySet]

        for option, value in additionalOptions:
            self.detectClones.append(f"--{option}={value}")


    def append_options_to_evaluateTool(self) -> None:
        additionalOptions = self.config.items(evaluateToolSection)

        # filter out already set options
        alreadySet = ['storage']
        additionalOptions = [(name, value) for name, value in additionalOptions if name not in alreadySet]

        for option, value in additionalOptions:
            # append argument if option is not empty
            if value.strip():
                self.evaluateTool.append(f"--{option}={value}")


    def run_and_measure_command(self, command, env={}) -> None:
        """
        Wrapper for run_command() method:
        Runs the specified benchmark command, 
        prints the executed command with all arguments,
        prints and saves the runtime of the command.       
        """
        commandName = command[0].replace("./", "")

        startTime = time()
        self.run_command(command, env, commandName)
        endTime = time()

        # Calculate, save and print the elapsed time
        elapsedTime = endTime - startTime
        runtimeMessage = f"Runtime (s) of {commandName}: {elapsedTime:.2f}"
        self.reportMessages.append(runtimeMessage)
        print(runtimeMessage, flush=True)


    def run_command(self, command, env={}, commandName=None) -> None:
        """
        Runs the specified benchmark command, 
        prints the executed command with all arguments.
        """
        if not commandName:
            if type(command) is list:  # concatenate elements of the 'command' list into a single string
                commandName = ' '.join([str(item) for item in command])
            else:
                commandName = command

        print(f"Start '{command}'", flush=True)

        # show complete command with all arguments
        print(*command, sep=' ', flush=True)

        # capture_output not set --> output to stdout of caller = to docker output
        subprocess.run(command, check=True, env=dict(environ, **env))

        print(f"'{command}' finished", flush=True)


    def insert_lines(self, dst, newLines, lineNumber) -> None: 
        """
        Inserts messages into the report file at the specified line number.
        """
        # read the report file
        with open(dst, 'r') as file:
            lines = file.readlines()

        # Insert the lines at the specified line number
        for i, line in enumerate(newLines):
            if not line.endswith('\n'): 
                line = f"{line}\n"
            lines.insert(lineNumber+i, line)

        # save the modified report file
        with open(dst, 'w') as file:
            file.writelines(lines)


    def run(self) -> None:
        """
        Main method of this class. It runs all BigCloneEval commands (detectClones, clearClones, importClones, evaluateTool)
        and inserts the runtime of each command in report file, which was created by evaluateTool.
        """
        chdir(benchmarkCommandsDir)

        self.run_benchmark_startup()
        self.run_tool_startup()

        # list of messages, which will be inserted into the report file
        self.reportMessages = []

        # add current date and time to the report file (messages)
        currentDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.reportMessages.append(f"Start at: {currentDateTime}")

        # run BigCloneEval commands:
        self.run_and_measure_command(self.detectClones, self.env)
        #self.run_and_measure_command(self.clearClones)
        self.run_and_measure_command(self.importClones)
        self.run_and_measure_command(self.evaluateTool)

        # insert messages (containing the runtime of each command) into the report file at line 4
        self.insert_lines(self.reportFile, self.reportMessages, 4)


if __name__ == "__main__":
    benchmarkRunner = BenchmarkRunner().run()
