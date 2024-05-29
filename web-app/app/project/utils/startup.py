"""
functions in this file are executed once at the start of Cloreco web platform
"""
from celery.signals import celeryd_after_setup
import sys
from glob import glob
from pathlib import Path
import project.settings as settings
import project.utils.configFilesParser.shellConfigFiles as sc
import project.utils.configFilesParser.configParserFiles as cp
from os import environ
from shutil import copy2
import docker, docker.errors
from project.utils import utils
from project.utils.configure import configure_redis

def check_data_directory() -> None:
    """
    Verifies and prepares the data directory at application startup.

    This function checks the existence of specific directories required for the application to function correctly,
    namely 'benchmarks', 'confTemplates', and 'confWorkbench', located under the /app/data/ path. If any of these
    directories do not exist, it initializes the data environment by copying the default directory structure and
    files from /app/data_default to /app/data/.

    This setup process ensures that the application has all necessary configuration files and benchmark data
    available at startup. It is designed to run once during the application's initialization phase.

    """
    benchmarkDir = Path(settings.directories['benchmarks'])
    confTemplatesDir = Path(settings.directories['confTemplates'])
    confWorkbenchDir = Path(settings.directories['confWorkbench'])

    # copy the default /app/data_default directory to /app/data, if the former directories do not exist
    if not benchmarkDir.exists() or not confTemplatesDir.exists() or not confWorkbenchDir.exists():
        print("The data directory at /app/data/ is empty or is missing directories. Initializing the data environment by copying the default directory structure...")

        dataDir = Path("/app/data/")
        dataDefaultDir = Path("/app/data_default/")
        for file in dataDefaultDir.rglob("*"):
            dst = dataDir / file.relative_to(dataDefaultDir)
            if file.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
            else:
                if not dst.exists():
                    copy2(file, dst)


def validate_config_templates() -> None: 
    """
    Runs once at startup (__init__.py)
    Ensure there are config files for clone detector tools in the templates directory (by default cloneDetection/cloneDetectorTools/templates/ )
    Ensure there are config files in the workbench directory. if not, copy the files from the templates directory into the workbench directory
    Ensure that the arguments in the web.template file is a subset of the arguments in .template file of each clone detector tool
    """

    ##### Step 1: Ensure there are config files for clone detector tools in the templates directory (by default cloneDetection/cloneDetectorTools/templates )
    templDir = settings.directories["confTemplates"]

    # check if there are any template files
    numFiles = len(glob(f"{templDir}/*"))
    if numFiles == 0:
        raise FileNotFoundError(f"no template files found in template Directory {templDir}")

    webTemplateFiles = glob(f"{templDir}/*{settings.templateFiles['fileExtensionWebEdit']}")
    # check if there are any web template files (.cfg.web.template)
    if len(webTemplateFiles) == 0:
        raise FileNotFoundError(f"no web template files ('{settings.templateFiles['fileExtensionWebEdit']}') found in template Directory {templDir}")

    ##### Step 2: Ensure there are config files in the workbench directory. if not, copy the files from the templates directory
    confDir = settings.directories["confWorkbench"]

    #bceFile = f"{confDir}/{settings.BigCloneEval['templateFileName']}"

    descriptionSection = settings.templateFiles['descriptionSection']
    defaultValueSection = settings.templateFiles['defaultValueSection']

    # check if there are any template files in the workbench directory
    # if not, copy the files from the templates directory into the workbench directory
    numFiles = len(glob(f"{confDir}/*"))
    if numFiles == 0:
        utils.copy_config_files_from_template_dir_to_workbench()

    ##### Step 3: Ensure that the arguments in the web.template file is a subset of the arguments in .template file of each clone detector tool

    webTemplateFiles = glob(f"{confDir}/*{settings.templateFiles['fileExtensionWebEdit']}")
    # check if there are any web template files (.cfg.web.template)
    if len(webTemplateFiles) == 0:
        raise FileNotFoundError(f"no web template files ('{settings.templateFiles['fileExtensionWebEdit']}') found in template Directory {confDir}")
    
    for webTemplate in webTemplateFiles:
        # check if base config template (.cfg.template) file exists
        detectorName = webTemplate.split(settings.templateFiles['fileExtensionWebEdit'],1)[0]
        templateBaseFile = Path(f"{detectorName}{settings.templateFiles['fileExtensionBase']}")
        if not templateBaseFile.is_file():
            raise FileNotFoundError(f"base config template {templateBaseFile} not found in template Directory {confDir}")

        # check if all arguments from the web template file (.cfg.web.template) exist in the base config template
        argumentsWebTemplate = utils.read_description_and_defaults(webTemplate, descriptionSection, defaultValueSection)
        arguments = [argument['name'] for argument in argumentsWebTemplate]

        templateBase = sc.read_shell_config_file(templateBaseFile)
        templateBase = [arg.split("=",1)[0] for arg in templateBase]

        if not set(arguments).issubset(templateBase):
            raise Exception(f"Arguments in {webTemplate} needs to be a subset of the arguments in {templateBaseFile} \n(All arguments in {webTemplate} should be included in {templateBaseFile}, which might have additional arguments not present in the first file.")


# execute on celery startup
@celeryd_after_setup.connect
def on_celeryd_startup(sender=None, instance=None, **kwargs):
    """
    Execute checks on startup of celery
    """
    try:
        set_startup_status("The Celery (backend service) container is still starting. Please wait and watch the 'docker compose' output. Reload this page to update this message.", "info")
        check_container_registry_login()
        check_images()
    except Exception as exc:
        set_startup_status(f"""There were errors during the start of the Celery (backend service) container. <br> 
                           Please check the output of 'docker compose'! <br> 
                           Error message: <br>
                           {exc}""", 
                           "error")
        print(exc)
        sys.exit(1)
    else:
        set_startup_status("Startup successful! Runs can now be started.", "success")
        print("Startup successful! Runs can now be started.")


def set_startup_status(statusMsg: str, statusType: str) -> None:
    """
    Set a start status with message and type (e.g. error, success). 
    This status is displayed on the "Home" page, to indicates errors during startup.
    """
    redis = configure_redis()
    status = {
        "message"   : statusMsg,
        "type"      : statusType
    }
    redis.hset('startup_status', mapping=status)


def check_container_registry_login() -> None:
    """
    Checks the login credentials for a container registry and configures Redis based on the availability and validity of these credentials.

    This function retrieves container registry credentials from environment variables. 
    If any required environment variable is missing, it disables container registry functionality in Redis. 
    If the environment variable 'PUSH_CREATED_IMAGES_TO_CONTAINER_REGISTRY' is set and true, it attempts to log in to the specified container registry. 
    On successful login, Redis is updated to reflect that the container registry is enabled. 
    If login fails, the program exits with an error message.

    Environment Variables:
        CONTAINER_REGISTRY_LOGIN_USERNAME:          Username for the container registry.
        CONTAINER_REGISTRY_LOGIN_PASSWORD_TOKEN:    Password or token for the container registry.
        CONTAINER_REGISTRY_URL:                     URL of the container registry.  ( e.g.: ghcr.io )
        CONTAINER_REGISTRY_REPOSITORY:              Container registry with repo    ( e.g.: ghcr.io/user4/myrepo/ )
        PUSH_CREATED_IMAGES_TO_CONTAINER_REGISTRY:  Flag to indicate whether to push images to the container registry.

    Raises:
        SystemExit: If login to the container registry fails.
    """
    redis = configure_redis()

    redis.hset('run.progress', 'isExecuted', "False")

    try:
        username=environ['CONTAINER_REGISTRY_LOGIN_USERNAME']
        password=environ['CONTAINER_REGISTRY_LOGIN_PASSWORD_TOKEN']
        registry=environ['CONTAINER_REGISTRY_URL']
        repository=environ['CONTAINER_REGISTRY_REPOSITORY']
    except KeyError as exc:
        print(f"Environment variable {exc} not found. Push of new created images of clone detector tools to a container registry will not be available.")
        redis.set("container_registry", "disabled")
        return

    redis.set("container_registry", "enabled")
    redis.set("container_registry.username", username)
    redis.set("container_registry.password", password)
    redis.set("container_registry.URL", registry)
    redis.set("container_registry.repository", repository)

    if environ.get('PUSH_CREATED_IMAGES_TO_CONTAINER_REGISTRY', default="False").lower() in ('true', '1', 't', 'yes'):
        client = docker.from_env()
        try:
            client.login(username=username, password=password, registry=registry)
        except docker.errors.APIError as exc:
            error = f"Login at container registry {registry} failed: {exc}"
            print(error)
            exit(error)

        print(f"Push of new created images of clone detector tools to container registry {registry} is enabled.")
        redis.set("container_registry.upload_new_images", "enabled")
    else:
        print(f"Environment variable 'PUSH_CREATED_IMAGES_TO_CONTAINER_REGISTRY' is not set to 'True'. Push for new created images of clone detector tools to a container registry will not be available.")
        redis.set("container_registry.upload_new_images", "disabled")


def check_images() -> None:
    """
    Validates the local availability of Docker images required for clone detector tools and benchmarks, as specified in configuration templates.

    This function:
    - Extracts Docker image names/tags from configuration templates.
    - Checks for the existence of these images locally.
    - Attempts to update or download missing images. (if 'UPDATE_IMAGES_ON_STARTUP' environment variable is not set or set to a truthy value)
    
    If any images are missing and cannot be downloaded 
    (e.g., due to the 'UPDATE_IMAGES_ON_STARTUP' option being disabled, 
        missing Images in the remote repository or network failures), 
    it prints an error message detailing the missing images and raises a exception.
    """
    updateImages = environ.get('UPDATE_IMAGES_ON_STARTUP', default="True").lower() in ('true', '1', 't', 'yes')

    images = []
    templateDir = settings.directories["confTemplates"]
    detectorTools = utils.read_template_files(templateDir)
    images.extend([tool["container"]["image"] for tool in detectorTools])

    benchmarks = utils.read_benchmark_files()
    images.extend([benchmark["container"]["image"] for benchmark in benchmarks])

    missingImages = check_images_exist_local(images)

    if updateImages:
        missingImages = update_all_images(images, missingImages)
    else:
        print(f"Skipping image updates: Environment variable 'UPDATE_IMAGES_ON_STARTUP' is set to a falsy value.")

    if missingImages:
        if updateImages:
            print("Error: Failed to locate or download the following images:")
            print(f"{', '.join(missingImages)}")
            print("To resolve this, ensure the 'image' value ist correct, build the images locally or/and upload it to its image registry.")
        else:
            print("Error: Failed to locate the following images locally:")
            print(f"{', '.join(missingImages)}")
            print("""To resolve this, ensure the 'image' value ist correct, 
build the images locally or set the 'UPDATE_IMAGES_ON_STARTUP' 
environment variable to 'true' to attempt automatic download.""")            
        raise docker.errors.ImageNotFound(f"{', '.join(missingImages)} images could not be found")


def check_images_exist_local(images: list[str]) -> list[str]:
    """
    Check whether images are available locally on this machine.

    Returns:
        a list of images, which could not be found
    """
    dockerClient = docker.from_env()
    missingImages = []

    for image in images:
        try:
            # Attempt to get the image
            image = dockerClient.images.get(image)
        except (docker.errors.ImageNotFound, docker.errors.NotFound) as exc:
            print(f"Image '{image}' not found locally.")
            missingImages.append(image)
        except docker.errors.NullResource as exc:
            print("image name is empty")
            raise exc

    return missingImages


def update_all_images(images: list[str], missingImages: list[str]) -> list[str]: 
    """
    Updates/pulls the current versions of all images for clone detector tools.

    This function checks if the 'UPDATE_IMAGES_ON_STARTUP' environment variable is set to a falsy value (false, 0, f, no, disabled, disable). 
    If set, it proceeds to update all images specified in the configuration templates for the clone detector tools and benchmark files.

    The function reads image names from the configuration files and pulls the latest versions of these images from the specified container registry.
    """
    if environ.get('UPDATE_IMAGES_ON_STARTUP', default="true").lower() in ('false', '0', 'f', 'no', 'disabled', 'disable'):
        print("Environment variable 'UPDATE_IMAGES_ON_STARTUP' is not set to 'True'. Update/Pull of all images for clone detector tools will be skipped.")
        return missingImages
    
    redis = configure_redis()

    dockerClient = docker.from_env()
    dockerClient.login(
        username=redis.get("container_registry.username"),
        password=redis.get("container_registry.password"),
        registry=redis.get("container_registry.URL")
    )

    updatedImages = []

    for image in images:
        print(f"Update/Pull of image {image}")
        try:
            dockerClient.images.pull(image)
            updatedImages.append(image)
            try: missingImages.remove(image)
            except ValueError: pass
        except (docker.errors.ImageNotFound, docker.errors.NotFound) as exc:
            print(f"Error: Image '{image}' not found in remote image repository.")
            #raise exc
        except docker.errors.APIError as exc:
            print("Error: Failed to check image due to an API error: ")
            raise exc
        
    print(f"Updated images: {', '.join(updatedImages)}")
    return missingImages
    
