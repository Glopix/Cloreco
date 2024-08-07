"""
functions / the Class in this file are used to execute a run.
This means execution (docker) containers of all clone detector tools specified.
Each container contains a clone detector tool, which will be executed.
Mountpoints are created and used to transfer data (configuration file and result files from the tools and benchmarks) 
between the host and the containers.
"""
from celery.contrib.abortable import AbortableTask
import docker
from flask_sse import sse
from loguru import logger as log
from types import SimpleNamespace
from pathlib import Path
from os import chdir
import project.utils.configFilesParser.configParserFiles as cp
import project.settings as settings
import socket
from shutil import make_archive
from project.utils.configure import configure_redis
import requests.exceptions
from threading import Thread, Event
from time import sleep
from flask import current_app
from project.utils.Run import toolStatistics
  
class ExecuteRun(AbortableTask):

    def __call__(self, containerConfigs: list[dict], runDir: str|Path, benchmarks: list[dict]) -> None:
        runDir = Path(runDir)
        self.runDir = runDir
        self.runID = runDir.name

        self.containerConfigs = containerConfigs
        # sort the list of benchmark dictionaries by the 'name' key
        self.benchmarks = sorted(benchmarks, key=lambda x: x['name'])

        self.archiveName = self.runID
        
        self.configure_logging()

        self.redis = configure_redis()
        # set current run id, task id, directory and log file location in database
        self.redis.set('run.id', str(self.runID))
        self.redis.set('run.task.id', self.request.id)
        self.redis.set('run.directory', str(self.runDir))
        self.redis.set("run.log", str(self.logFile))

        # Create a Docker client
        self.dockerClient = docker.from_env(timeout=300)

        self.currentAppContext = current_app.app_context()

        # host path to the current run directory
        self.hostRunPath = self.get_host_data_path() / "cloneDetection" / "runs" / self.runID

        # save the number of already executed containers in this run
        # will be incremented on each container start
        self.numExecutedContainers = 0

        self.abortHeartbeats = Event()

        self.startup_check()

        # Call the main task logic
        self.start()


    def startup_check(self) -> None:
        if not self.runDir.exists():
            raise FileNotFoundError(f"self.runDir ({self.runDir}) does not exist")
        if not self.containerConfigs:
            raise ValueError(f"self.containerConfigs list is empty")
        if not isinstance(self.containerConfigs, list):
            raise TypeError(f"self.containerConfigs is not a list")
        if not isinstance(self.containerConfigs[0], dict):
            raise TypeError(f"self.containerConfigs list does not contain dicts")
        if not self.benchmarks:
            raise ValueError(f"self.benchmarks list is empty")
        if not isinstance(self.benchmarks, list):
            raise TypeError(f"self.benchmarks is not a list")


    def get_host_data_path(self) -> Path:
        """
        returns a Path object of the 'data' directory, containing the host path (outside of this celery container)
        """

        def get_container_mounts(containerID):
            try:
                container = self.dockerClient.containers.get(containerID) 
                return container.attrs['Mounts']
            except docker.errors.NotFound:
                print("Container not found.")

        containerID = socket.gethostname()

        for mount in get_container_mounts(containerID):
            if "/app/data" in mount['Destination']: 
                return Path(mount['Source'])


    def publish_to_sse(self, msg: str, channel: str="run_logs") -> None:
        """
        send messages to web clients via server-sent events on an (optional) specified channel
        """
        sse.publish({"message": msg}, channel=channel)


    def send_heartbeats(self, abortHeartbeats: Event) -> None:
        """
        every second send heartbeats to the web clients via server-sent events
        as periodic signal to indicate normal operation of this container execution
        via the "container_heartbeats" channel
        """
        with self.currentAppContext:
            while not abortHeartbeats.is_set():
                sleep(1)
                self.publish_to_sse("HEARTBEAT: ExecuteRun", "run_heartbeats")


    def stream_logs(self, containerID: int) -> None:
        """
        send new log entries (stdout of container) to the web clients via server-sent events
        """
        container = self.dockerClient.containers.get(containerID)

        # Get container logs
        for log_line in container.logs(stream=True, follow=True):
            msg = log_line.decode('utf-8')
            with self.currentAppContext:
                self.log.info(msg)


    def send_progress_update(self, status: str, msg: str) -> None:
        """
        send updates about the current progress of execution
        via the "run_progress" channel
        """   
        isExecuted = "True"
        if status in {'error', 'failure', 'aborted', 'finished'}:
            isExecuted = "False"
        elif status == 'running':
            msg = f"{msg} (in {self.currentBenchmark['general']['pretty_name']})"
        
        progressUpdate = {
            "type"           : "container",
            "status"         : status,
            "progressBar"    : "enabled",
            "currentStep"    : self.numExecutedContainers,
            "totalSteps"     : len(self.containerConfigs) * len(self.benchmarks),
            "currentMessage" : msg,
            "isExecuted"     : isExecuted
        }

        self.redis.hset("run.progress", mapping=progressUpdate)

        with self.currentAppContext:
            self.publish_to_sse(progressUpdate, "run_progress")


    def wait_for_container(self, container, detectorName: str) -> bool: 
        """
        wait for:
            a) container execution to finish  or

            b) task abortion
        """
        while(True):
            try:
                # Attempt to wait for the container to finish, with a timeout of 1 second
                container.wait(timeout=2)
                # exit this method, if the container finished execution
                return
            # if the container has not finished, this Exception is raised and will be ignored
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.RequestException as exc:
                print(f"Unexpected error while waiting for the container: {type(exc)} : {exc}")
                log.debug(f"Unexpected error while waiting for the container: {type(exc)} : {exc}")

            # check 'abort' state of this task. Can be set via abort_run() in run.py
            if self.is_aborted():
                self.log.warning(f"Received request from user to cancel this run")
                self.log.warning(f"aborting run and stopping Container '{detectorName}'")
                self.send_progress_update(status="aborted", msg=f"aborting run and stopping Container '{detectorName}'")
                container.stop(timeout=5)
                print("remove container")
                # container.remove() # The container will be removed automatically after it has been stopped. (setting 'auto_remove' : True)
                self.abortHeartbeats.set()
                print("container removed")
                raise Exception("Task aborted")
            

    def create_benchmark_volume(self) -> None:
        """
        create the volume, which will contain the benchmark input dataset (clone files)
        this volume will be shared between this benchmark container and all clone detector tools
        """
        self.log.trace("create shared benchmark volume")

        benchmark = self.currentBenchmark 
        volumeName=f"{self.runID}_benchmark_{benchmark['name']}_shared_volume"

        volume = self.dockerClient.volumes.create(name=volumeName)

        self.currentBenchmark["volume"] = volume
            
           
    def run_benchmark_container(self) -> None:
        """
        Create and run a container for the current benchmark,
        in which the benchmark dataset (clone files) is stored.
        Also, a volume will be created.
        This volume is used to share the benchmark dataset with
        containers that run clone detector tools.
        """
        benchmark = self.currentBenchmark 

        self.send_progress_update(status="running", msg=f"preparing container for benchmark: '{benchmark['general']['pretty_name']}'")

        volume = self.currentBenchmark["volume"]

        containerName = f"{self.runID}-benchmark-{benchmark['name']}"
        containerImage = benchmark["container"]["image"]
        benchmarkPath = benchmark["container"]["benchmark_path"]

        # Define container configuration
        containerConfig = {
            'name'              : containerName,
            'image'             : containerImage,
            #'entrypoint'        : f"bash -c 'while sleep 2; do echo $((i++)); ; done'",
            #'entrypoint'        : settings.benchmarks["startCommand"],
            'volumes'           : {volume.name: {'bind': benchmarkPath, 'mode': 'rw'}},
            'detach'            : True,
            'network_disabled'  : True,
            'auto_remove'       : True  # remove container after it has been stopped
        }

        self.send_progress_update(status="running", msg=f"start benchmark container for benchmark: '{benchmark['general']['pretty_name']}'")
        self.log.trace(f"start benchmark container for benchmark: '{benchmark['general']['pretty_name']}'")
        self.log.trace(f"This might take a while, since the entire benchmark dataset is copied into a volume")

        # Create and start the container
        container = self.dockerClient.containers.run(**containerConfig)

        self.currentBenchmark["container"]["obj"] = container
        container.stop(timeout=5)

    
    def stop_benchmark_container(self) -> None:
        """
        Stop and delete the current benchmark container, 
        where the benchmark dataset (clone files) are stored.
        """
        self.log.trace("stop and remove benchmark container")

        if "obj" in self.currentBenchmark["container"]:
            container = self.currentBenchmark["container"]["obj"]
            container.stop()

        
    def remove_benchmark_volume(self) -> None:
        """
        Remove the current benchmark volume.
        This volume is used to share the benchmark dataset with
        the clone detector tool containers.
        """
        self.log.trace("stop and remove shared benchmark volume")

        try:
            volume = self.currentBenchmark["volume"]
        except KeyError:
            return
              
        try:
            self.dockerClient.volumes.get(volume.name)
        except docker.errors.NotFound:
            # if volume does not exist: done
            return
        
        while True:
            # try to remove volume
            try:
                volume.remove(force=True)
                self.log.trace("Benchmark volume removed")
                return
            except docker.errors.APIError as exc:
                if "volume is in use" in str(exc):
                    print("removing Benchmark volume...")
                else:
                    print(f"Warning: {exc}")
                    print(f"Warning Exception type: {type(exc)}")
                # short time delay to ensure docker recognizes that all linked containers are removed. 
                sleep(1)
                #raise exc

    def _prepare_paths(self, fileName: str, detectorName: str, detector: dict, pathInContainer: str = False) -> SimpleNamespace:
        """
        Prepares and returns the file paths for different environments: this container, the host system,
        and the specified detector's container.

        Parameters:
        - fileName: The name of the file for which paths are being prepared.
        - detectorName: The name of the detector tool, used in constructing paths.
        - detector: A dictionary containing the detector's configuration, specifically its container settings.
        - pathInContainer: Optional. A specific path within the detector's container. If not provided,
                            a default path based on the detector's configuration is used.

        Returns:
        A SimpleNamespace object containing:
        - filename: The name of the file.
        - path: The file's path within this container.
        - hostPath: The file's path on the host system.
        - containerPath: The file's path within the detector's container.

        Note: Ensures the file exists at the specified path within this container by touching it, as Docker does not
        automatically create mount paths.
        """
        
        # only the config files (entrypoint.cfg and tool config) have special paths
        if pathInContainer:
            pathInContainer = Path(pathInContainer)
        else:
            pathInContainer = Path(detector['container']['mountpoint_base']) / fileName

        paths = SimpleNamespace(
            filename        = fileName, 
            # path to file in this container
            path            = str(self.runDir / self.currentBenchmark['name'] / detectorName / fileName),
            # path to file in host system (outside of this container)
            hostPath        = str(self.hostRunPath / self.currentBenchmark['name'] / detectorName / fileName),
            # path to file in the container
            containerPath   = str(pathInContainer)
        )

        # touch the file, because the container mount paths need to exist and will not be created by docker
        Path(paths.path).touch(exist_ok= True)

        return paths
    

    def _prepare_mount_points(self, detectorName: str, detector: dict) -> list:
        """
        Prepares and returns a list of mount points for a Docker container. These mount points include:
        - The benchmark detectClones CSV file
        - The benchmark evaluateTool report file
        - The configuration file for the clone detector tool 
        - The configuration file for the entrypoint script (entrypoint.cfg)
        - A file for verbose logging

        Additionally, it updates the entrypoint script's configuration file with the paths to the
        detectClones CSV file and the evaluateTool report file within the container.

        Parameters:
        - detector_name: The name of the detector tool.
        - detector: A dictionary containing the detector's configuration.

        Returns:
        A list of docker.types.Mount objects configured for the container.
        """

        ## benchmark detectClones csv file
        # <detectorTool>.<detectedClonesFileExtension>
        # e.g.:     NiCad.csv
        csvFilename = f"{detectorName}{settings.benchmarks['detectedClonesFileExtension']}"
        csvFile = self._prepare_paths(csvFilename, detectorName, detector)

        ## benchmark evaluateTool report file
        # <detectorTool>.<reportFileExtension>
        # e.g.:     NiCad.report
        evaluateToolReportFilename = f"{detectorName}{settings.benchmarks['reportFileExtension']}"
        reportFile = self._prepare_paths(evaluateToolReportFilename, detectorName, detector)

        ## config file for clone detector
        # <detectorTool>.<fileExtensionFinal>
        # e.g.      NiCad.cfg
        detectorToolConfigFilename = f"{detectorName}{settings.templateFiles['fileExtensionFinal']}"
        detectorToolConfigFile = self._prepare_paths(detectorToolConfigFilename, detectorName, detector, pathInContainer=detector['container']['mountpoint_detector_config'])

        # config for entrypoint script
        # <detectorTool>.<reportFileExtension>
        # e.g.:     entrypoint.cfg
        entrypointConfigFilename = settings.benchmarks['configFileName']
        entrypointConfigFile = self._prepare_paths(entrypointConfigFilename, detectorName, detector, pathInContainer=detector['container']['mountpoint_entrypoint_config'])


        # write path of .csv file in container to entrypoint.cfg
        entrypointConfig = {"storage": csvFile.containerPath}
        cp.update_config(entrypointConfigFile.path, section=settings.benchmarks['detectClonesSection'], config=entrypointConfig)

        # write path of .report file in container to entrypoint.cfg
        entrypointConfig = {"storage": reportFile.containerPath}
        cp.update_config(entrypointConfigFile.path, section=settings.benchmarks['evaluateToolSection'], config=entrypointConfig)


        # verbose logging file
        verboseLogFilename = "verbose.log"
        verboseLogFile = self._prepare_paths(verboseLogFilename, detectorName, detector)

        # Define mounts
        mounts = [
            # detectClones storage mount (.CSV file) 
            docker.types.Mount( 
                source=csvFile.hostPath, 
                target=csvFile.containerPath, 
                type='bind' ),
            # evaluateTool storage mount (.report file)
            docker.types.Mount( 
                source=reportFile.hostPath, 
                target=reportFile.containerPath, 
                type='bind' ),
            # mount config file of clone detector
            docker.types.Mount( 
                source=detectorToolConfigFile.hostPath, 
                target=detectorToolConfigFile.containerPath, 
                type='bind' ),
            # mount config file of entrypoint.py script (entrypoint.cfg)
            docker.types.Mount( 
                source=entrypointConfigFile.hostPath, 
                target=entrypointConfigFile.containerPath, 
                type='bind', 
                read_only=True ),
            # verbose logging file mount (verbose.log file)
            docker.types.Mount( 
                source=verboseLogFile.hostPath, 
                target=verboseLogFile.containerPath, 
                type='bind' ),
        ]
        return mounts


    def run_container(self, detector: dict) -> None:
        """
        Configures, starts, and manages a Docker container for a given detector. It includes steps to:
        - Create and prepare mount points for the container,
        - Configure the container's settings,
        - Start the container and stream its logs,
        - Wait until the container has stopped or finished execution.

        Parameters:
        - detector: A dictionary containing the detector's configuration.
        """
        # remove file extension
        detectorName = str(detector['detector_config_filename']).split(".", 1)[0]

        prettyDetectorName = detectorName
        detectorName = detectorName.strip(" ")

        self.numExecutedContainers += 1
        self.send_progress_update(status="running", msg=f"preparing container for '{detectorName}'")

        mounts = self._prepare_mount_points(detectorName, detector)
        benchmarkVolume = self.currentBenchmark["volume"].name

        env = {
            "CLONE_DETECTOR_TOOL_NAME"  : prettyDetectorName,
            "BENCHMARK_NAME"            : self.currentBenchmark["name"]
        }

        # Define container configuration
        containerConfig = {
            'name'              : f"{self.runID}-{detectorName}",
            'image'             : detector["container"]["image"],
            #'entrypoint'        : f"bash -c 'while sleep 2; do echo $((i++)); ; done'",
            #'entrypoint'        : f"bash -c 'sleep 5'",
            'entrypoint'        : settings.benchmarks["startCommand"],
            'mounts'            : mounts,
            'volumes'           : {benchmarkVolume: {'bind': '/cloneDetection/benchmark/', 'mode': 'rw'}},
            'environment'       : env,
            'detach'            : True,
            'network_disabled'  : True,
            'auto_remove'       : True  # remove container after it has been stopped
        }

        self.send_progress_update(status="running", msg=f"executing container for '{detectorName}'")
        self.log.info(f"start container for '{detectorName}'")

        # Create and start the container
        container = self.dockerClient.containers.run(**containerConfig)

        # Start streaming logs in the background in separate Thread
        streamLogsThread = Thread(target=self.stream_logs, args=(container.id,), daemon=True)

        streamLogsThread.start()

        # wait till container has stopped/finished execution
        self.wait_for_container(container, detectorName)

        self.send_progress_update(status="running", msg=f"Container run for '{detectorName}' finished")
        self.log.success(f"Container run for '{detectorName}' finished")

        # Stop the container
        try:
            container.stop()
        except docker.errors.NotFound as exc:
            #self.log.error(f"Container {container.name} could not be found.")
            pass
        except docker.errors.APIError as exc:
            print(type(exc))
        #container.remove()


    def configure_logging(self) -> None:
        # configure logging
        self.log = log
        #self.log.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", level="DEBUG")
        self.log.add(self.publish_to_sse, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="TRACE")

        self.logFile = self.runDir / "run.log"
        self.log.add(self.logFile, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="TRACE")
        

    def success(self) -> None:
        """
        In case of no exception/sucessfull run:
        update status in redis, logs and SSE
        create a CSV containing a summary of the report files
        and diagrams of runtime and recall results
        """
        self.redis.set("run.status", "finished")
        self.log.success(f"All container executions of '{self.runID}' completed")

        self.create_statistics()

        self.send_progress_update(status="finished", msg=f"Run '{self.runID}' completed")
        self.log.success(f"Run '{self.runID}' completed")


    def create_statistics(self) -> None:
        """
        create a CSV containing a summary of the report files
        and diagrams of runtime and recall results
        """
        benchmark = self.currentBenchmark['name']

        runBenchmarkDir = self.runDir / benchmark
        # paths to CSV and diagrams
        reportSummaryCSV = self.runDir / benchmark /"summary.csv"
        recallDiagram = self.runDir / benchmark /"recall.svg"
        runtimeDiagram = self.runDir / benchmark / "runtime.svg"


        self.send_progress_update(status="running", msg=f"Creating statistics file and diagram")
        self.log.info(f"Creating statistics file and diagram")
        try:
            toolStatistics.extract_statistics_to_csv(runBenchmarkDir, reportSummaryCSV)
        except Exception as exc:
            self.log.error("Failed to extract statistics from the report file and save it to a csv file.")
            self.log.error("Maybe lines are missing in the report file, created by the evaluateTool command of the benchmark.")
            self.log.error("Error:")
            self.log.error(exc)
            return
        try:
            toolStatistics.create_recall_plot(reportSummaryCSV, recallDiagram, clusterBy="Type")
            toolStatistics.create_runtime_plot(reportSummaryCSV, runtimeDiagram)
        except Exception as exc:
            self.log.error(f"Failed to create statistics file and diagram. Error:")
            self.log.error(exc)


    def aborted(self) -> None:
        """
        If the run is aborted by a user:
        change name of (later created) archive file,
        update status in redis, logs and SSE
        """
        self.archiveName = f"{self.archiveName}---aborted"
        self.remove_benchmark_volume()
        self.redis.set("run.status", "aborted")
        self.send_progress_update(status="aborted", msg=f"Run '{self.runID}' aborted")
        self.log.error(f"Run '{self.runID}' aborted")


    def failure(self) -> None:
        """
        In case of error:
        change name of (later created) archive file,
        update status in redis, logs and SSE
        """
        self.redis.set("run.status", "failed")
        self.send_progress_update(status="error", msg=f"Run '{self.runID}' failed")
        self.log.error(f"Run '{self.runID}' failed")


    def final(self) -> None:
        """
        perform cleanup steps at the end of the run
        """
        self.abortHeartbeats.set()
        self.log.remove()


    def create_archive(self) -> None:
        self.log.info(f"Creating archive for run '{self.runID}': '{self.archiveName}'")

        archivedRunsDir = settings.directories["downloads"]
        chdir(archivedRunsDir)
        make_archive(self.archiveName, "zip", self.runDir)

        self.log.info(f"archive for run '{self.runID}' complete")


    def handle_run_exception(self, exc):
        #self.stop_benchmark_container()
        self.remove_benchmark_volume()

        if str(exc) == "Task aborted":
            self.aborted()
        else:
            self.log.error(exc)
            self.failure()
            raise exc
        

    def run_containers(self):
        """
        This method orchestrates the setup, execution, and cleanup phases for running benchmark containers and their respective detectors.
        
        The workflow for each detector includes:
        - Creating a shared benchmark volume.
        - Running a benchmark container to pupulate the benchmark volume with the clone dataset.
        - Running the specific detector container.
        - Generating/updating the statistic file based on the 'evaluateTool' report of the benchmark in the detector container.
        - Stopping the benchmark container.
        - Removing the shared benchmark volume.
        
        For each detector, a new benchmark volume and container are created to isolate the benchmark files. 
        This prevents modifications by any detector tool, ensuring consistent and comparable results across all detector tool executions.
        """
        for detector in self.containerConfigs:
            self.create_benchmark_volume()
            self.run_benchmark_container()

            self.run_container(detector)
            self.create_statistics()

            self.remove_benchmark_volume()

    def execute_run(self) -> None:
        try:
            for benchmark in self.benchmarks:
                self.currentBenchmark = benchmark
                self.log.info(f"Executing in benchmark: {self.currentBenchmark['general']['pretty_name']}")

                self.run_containers()
            
            self.success()
        except Exception as exc:
            self.handle_run_exception(exc)
            
        #self.create_archive()
    
    def start(self) -> None:
        self.log.info(f"Run '{self.runID}' started")
        # send startup message to SSE progress channel, to notifiy about a new run
        # this results in JS clearing the logs on the website
        self.send_progress_update("startup", "startup")

        self.redis.set("run.status", "started")

        # Start streaming heartbeats in the background in separate Thread
        Thread(target=self.send_heartbeats, args=(self.abortHeartbeats,), daemon=True).start()

        self.execute_run()

        self.final()
