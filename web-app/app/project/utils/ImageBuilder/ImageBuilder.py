"""
functions in this file are used to create (docker) images,
based on a given git repository
for later use in the website/Cloreco software
"""
from pathlib import Path
import docker
from flask import current_app
from celery.contrib.abortable import AbortableTask
from ansi2html import Ansi2HTMLConverter
import requests
from flask_sse import sse
from loguru import logger as log
from time import sleep
from threading import Thread, Event
import re

import project.settings as settings
from project.utils.configure import configure_redis


class ImageBuilder(AbortableTask):
    """
    This class is used to build images based on a git repository and user input from the website.
    It can also upload (push) a new build image to the container registry, if the feature is enabled.
    This can be set via env vars in docker-compose.yml

    Note: Tasks of this class cannot be cancelled, although it is based on the 'AbortableTask' class, 
    as it uses the Docker Python SDK, which does not provide a direct method for cancelling a build process once it has been initiated with the build method. 
    The Docker build process runs in the Docker daemon, not in the Python process. 
    Therefore, the build process cannot be interrupted from Python once it has been passed to Docker.
    """

    def __call__(self, toolName: str, installDir: str, gitRepoURL: str, jdkVersion: str, distro: str) -> None:
        self.imageName, self.toolName  = self.convert_to_image_name(toolName)
        self.installDir = Path(installDir.strip())
        self.runnerPath = self.installDir / "runner.sh"
        self.gitRepoURL = gitRepoURL
        self.jdkVersion = jdkVersion
        self.distro     = distro
        self.imageTag   = f"{self.imageName}:latest"

        self.redis = configure_redis()

        # The container image registry must be set via the environment variable 'CONTAINER_REGISTRY_REPOSITORY'.
        # If this variable is not set, no images will be pushed to a registry, and all created images will be stored locally only.
        self.imageRepo     = self.redis.get('container_registry.repository')
        self.imageFullTag  = self.imageTag

        if self.imageRepo:
            # prepend the image repo to the tag
            self.imageFullTag   = f"{self.imageRepo.rstrip('/')}/{self.imageFullTag}"
        else:
            self.imageRepo      = "local"

        self.currentAppContext = current_app.app_context()
        self.myDir = Path(__file__).parent.absolute()

        self.abortHeartbeats = Event()

        # login to the container registry
        # This registry is the registry where the base image for all images is stored
        # All new images will be stored in this registry
        self.dockerClient = docker.from_env()
        self.dockerClient.login(
            username=self.redis.get("container_registry.username"),
            password=self.redis.get("container_registry.password"),
            registry=self.redis.get("container_registry.URL")
        )

        self.configure_logging()
        self.redis.set("imageBuild.log", str(self.logFile))

        # Call the main task logic
        self.start()


    def convert_to_image_name(self, name: str) -> tuple[str, str]:
        """
        Converts a string into:
         - a string compatible with the Docker image format (image name) and
         - a string without (back)slashes, whitespaces, dots and commas (pretty name)

        This function processes the given software name to fit the Docker image naming conventions.
        It involves replacing certain characters, like whitespaces, with underscores or hyphens, 
        removing non-ASCII characters, and replacing uppercase letters.

        Args:
            name (str): The original name of the software.
        Returns:
            tuple: The converted name suitable for Docker image naming as string and a 'pretty' name string.
        """
        # Replace slashes, backslashes and whitespaces with a underscores
        name = re.sub(r'[\/\\\s]', '_', name)
        # Replace dots and commas with hyphens
        name = re.sub(r'[\,\.]', '-', name)
        prettyName = name
        # Remove all characters that are not ASCII letters, numbers, hyphens or underscores
        name = re.sub(r'[^a-zA-Z0-9-_]', '', name)
        # Convert first letter to lowercase
        name = re.sub(r'^([A-Z]+)', lambda x: x.group(1).lower(), name)
        # Convert uppercase letters to lowercase if preceded by a hyphen or underscore
        name = re.sub(r'(?<=[-_])([A-Z]+)', lambda match: match.group(1).lower(), name)
        # Convert uppercase letters to lowercase and prepend with a hyphen
        name = re.sub(r'([A-Z]+)', lambda match: f"-{match.group(1).lower()}", name)

        return name, prettyName


    def publish_to_sse(self, msg: str, channel="imageBuild_logs") -> None:
        """
        send messages to web clients via server-sent events on an (optional) specified channel
        """
        sse.publish({"message": msg}, channel=channel)


    def send_progress_update(self, status: str, msg: str, **kwargs: dict) -> None:
        """
        send updates about the current progress of execution
        via the "imageBuild_progress" channel
        """           
        progressUpdate = {
            "type"           : "imageBuild",
            "status"         : status,
            "progressBar"    : "disabled",
            "msg"            : msg
        }

        for key, value in kwargs.items():
            progressUpdate[key] = value

        self.redis.hset("imageBuild.progress", mapping=progressUpdate)

        with self.currentAppContext:
            self.publish_to_sse(progressUpdate, "imageBuild_progress")


    def send_heartbeats(self, abortHeartbeats: Event) -> None:
        """
        every second send heartbeats to web clients via server-sent events
        as periodic signal to indicate normal operation of this ImageBuilder execution
        via the "imageBuild_heartbeats" channel
        """
        with self.currentAppContext:
            while not abortHeartbeats.is_set():
                sleep(1)
                self.publish_to_sse("HEARTBEAT: ImageBuild", "imageBuild_heartbeats")


    def convert_ansi_to_html_colors(self, line) -> None:
        conv = Ansi2HTMLConverter(inline=False)
        html = conv.convert(line, full=False)
        return html
    
    
    def configure_logging(self) -> None:
        self.log = log
        #self.log.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", level="DEBUG")
        self.log.add(self.publish_to_sse, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="TRACE")

        self.logFile = Path(settings.directories["runs"]) / "ImageBuild" / "imageBuild.log"
        self.logFile.unlink(missing_ok=True)
        self.log.add(self.logFile, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="TRACE")


    def get_build_args(self) -> dict:
        """
        Retrieves and prepares the build arguments required for the ARG's in the Dockerfile.

        Returns:
            A dictionary containing key-value pairs of build arguments.
        """

        buildargs = {
            'BASE_IMAGE' : str(settings.ImageBuilder['baseImage']),
            'INSTALL_DIR': str(self.installDir),
            'GIT_REPO' : self.gitRepoURL,
            'DISTRO' : self.distro,
            'JDK_VERSION' : self.jdkVersion,
            'TOOL_NAME' : self.toolName,
            'RUNNER_SCRIPT_PATH' : str(self.runnerPath),
        }

        self.log.trace(f"arguments extracted from the web form:")
        for key, value in buildargs.items():
            self.log.trace(f"{key}: {value}")

        return buildargs


    def _print_build_log(self, line: dict, filterKeys: list = ["stream"]) -> None:
        """
        Filter out keys from a Docker build log entry (json/dict), 
        and send them as message to log (and SSE stream).
        """
        # Extracting the main message
        message = ' '.join(str(line[key]) for key in filterKeys if key in line)
        if message:
            message = self.convert_ansi_to_html_colors(message)
            self.log.info(message)

        # Extract and print error details if present
        error = line.get('error', '').strip()
        if error:
            if error == "The command '/bin/sh -c bash -c '(set -e; source ./install.sh)'' returned a non-zero code: 1":
                # This error occurs if the user created install.sh script returns an error
                # since this error message could be misleading/confusing for the user, 
                # another error message is displayed instead
                self.log.error(f"Error in: install.sh")
                self.log.error(f"Check for error in the preceding lines, improve your install.sh script and restart the process by submitting your tool repo again.")
            else:
                self.log.error(f"Error: {error}")
                error_detail = line.get('errorDetail')
                if error_detail:
                    self.log.error(f"Error details: {error_detail}")

            raise Exception("build failed")


    def build_image(self) -> None:
        """
        Build a Docker image based on the Dockerfile and additional build arguments.
        """

        # path to 'Dockerfile': in the same directory as this python file
        dockerfilePath = str(self.myDir / "Dockerfile")

        #self.log.info(f"fetching 'install.cfg' from git repository '{self.gitRepoURL}' ")

        # build arguments for dockerClient.api.build()
        buildArgs = {
            'fileobj': open(dockerfilePath, 'rb'),
            'buildargs': self.get_build_args(),
            'rm': True,
            'forcerm': True, # Always remove intermediate containers, even after unsuccessful builds
            'tag': self.imageTag,
            'decode': True,
            'nocache': True
        }

        self.log.info(f"Preparation complete")
        self.log.info(f"image tag: {buildArgs['tag']}")
        self.log.info(f"start image build")

        # build the Docker image
        for line in self.dockerClient.api.build(**buildArgs):
            self._print_build_log(line)

        # set new, full tag for image
        self.log.info(f"set new tag: {self.imageFullTag}")
        image = self.dockerClient.images.get(self.imageTag)
        image.tag(self.imageFullTag)
        # remove old temporary tag
        self.dockerClient.images.remove(self.imageTag)

        self.log.info(f"image build completed")

        
    def upload_image(self) -> None:
        """
        upload (push) a new build image to the container registry, if the feature is enabled.
        This can be set via env vars in docker-compose.yml
        """
        if self.redis.get("container_registry") != "enabled" or self.redis.get("container_registry.upload_new_images") != "enabled":
            self.log.info(f"image '{self.imageFullTag}' will NOT be uploaded/pushed to the container registry")
            return
        
        self.log.info(f"push image '{self.imageFullTag}' to repo: {self.imageRepo}")
        # upload/push Docker image
        for line in self.dockerClient.api.push(self.imageFullTag, stream=True, decode=True):
            self._print_build_log(line, filterKeys=['status', 'progress'])
        

    def success(self) -> None:
        """
        If the image build was successfull:
        log it, send an progress update to make the 'next' button clickable
        end heartbeats
        """
        self.log.success(f"image build successfully finished")
        self.send_progress_update("success", "success", imageURL=self.imageFullTag, toolName=self.toolName)
        self.redis.set("imageBuild.status", "finished")


    def failure(self) -> None:
        """
        If the image build fails:
        log it, send an progress update to prevent the 'next' button to be clickable and
        end heartbeats
        """
        self.log.error(f"image build failed")
        self.send_progress_update("error", "image build failed")
        self.redis.set("imageBuild.status", "failed")

    
    def final(self) -> None:
        """
        perform cleanup steps at the end of image building process
        """
        self.abortHeartbeats.set()
        self.log.remove()

    def start(self) -> None:
        self.log.info(f"image build for '{self.toolName}' started")
        # send startup message to SSE progress channel, to notifiy about a new run
        # this results in JS clearing the logs on the website
        self.send_progress_update("startup", "startup")

        self.redis.set("imageBuild.status", "started")

        # Start streaming heartbeats in the background in separate Thread
        Thread(target=self.send_heartbeats, args=(self.abortHeartbeats,), daemon=True).start()

        try:
            self.build_image()
            self.upload_image()
        except Exception as exc:
            self.failure()
            if 'build failed' in str(exc):
                return
            else:
                self.log.error(exc)
                raise exc

        self.success()

        self.final()



