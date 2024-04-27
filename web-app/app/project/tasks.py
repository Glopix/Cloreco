from celery.contrib.abortable import AbortableTask
from celery import shared_task
from celery.signals import worker_shutting_down
from pathlib import Path
from project.utils.Run.executeRun import ExecuteRun
from project.utils.ImageBuilder.ImageBuilder import ImageBuilder
from project.utils.pages import run as Run

# abort run if this celery worker gets shut down (SIGINT)
@worker_shutting_down.connect
def worker_shutting_down_handler(sig, how, exitcode, ** kwargs):
    msg = Run.abort_run()
    print(msg)


# this method will be part of the base class 'ExecuteRun'
# and will be exectued as a task in a separate celery process.
# This task will execute a run (prepare and start the clone detector tool containers)
@shared_task(bind=True, base=ExecuteRun)
def start_container_runner(self, containerConfigs: list[dict], runDir: str|Path, benchmarks: list[dict]) -> None:
    try:
        self.run(containerConfigs, runDir, benchmarks)
    except Exception as exc:
        self.log.critical("Error in Celery container runner:")
        self.log.critical(exc)
        self.redis.set("run.status", "failed")
        raise exc


# this method will be part of the base class 'ImageBuilder'
# and will be exectued as a task in a separate celery process.
# It is used to build an container image based on given git repository 
# for a new, to be added clone detector tool.
@shared_task(bind=True, base=ImageBuilder)
def build_image_task(self, toolName: str, installDir: str, gitRepoURL: str, jdkVersion: str, distro: str):
    try:
        self.run(toolName, installDir, gitRepoURL, jdkVersion, distro)
    except Exception as exc:
        self.log.critical("Error in Celery container runner:")
        self.log.critical(exc)
        self.redis.set("imageBuild.status", "failed")
        raise exc
    