from flask import url_for
from pathlib import Path
from shutil import copy2
import project.forms as forms
import project.utils.configFilesParser.configParserFiles as cp
import project.utils.configFilesParser.shellConfigFiles as sc
import project.settings as settings
from project.utils.utils import copy_config_files_from_template_dir_to_workbench
from project.tasks import build_image_task


def append_bce_arguments_to_form(form: forms.GitRepoForm|forms.ImageForm) -> forms.GitRepoForm|forms.ImageForm:
    """
    dynamicly appends BigCloneEval (BCE) arguments as fiels to an existing form, which is used for configuring a new clone detector tool.
    These fields correspond to the BCE arguments that are read from a template file specified in the application settings.

    The added fields allow a website user to specify default values for BCE commands (e.g. max_files value recommended for execution)

    Args:
        form (forms.GitRepoForm | forms.ImageForm): The form to which BCE arguments are to be appended.

    Returns:
        forms.GitRepoForm | forms.ImageForm: The modified form with appended BCE arguments.

    Note:
        The function expects a template file defined in 'settings.templateFiles['newToolTemplate']', which contains 
        the descriptions of the BCE arguments. These descriptions are used to populate the labels and descriptions 
        of the form fields.
    """
    # read [benchmark-argument-descriptions] from the template file for new tools and append a field entry for each of these arguments
    templateFile = cp.read_cp_config_file(settings.templateFiles['newToolTemplate'])

    for argName, argValue in templateFile.items(settings.templateFiles['benchmarkDescriptionSection']):
        # Create a new entry for the FieldList for each BigCloneEval argument
        form.bceArgs.append_entry()

        # Access the last entry (just new created entry) in the FieldList and set its data
        #form.bceArgs.entries[-1].argument.name = argName
        form.bceArgs.entries[-1].argument.label.text = argName
        form.bceArgs.entries[-1].argument.description = argValue

    return form

def add_detector_tool(formData: forms.GitRepoForm|forms.ImageForm, via: str) -> dict:
    """
    Process:
    via="repo":   build image from repo via ImageBuilder.py with output to the "logs" page; on success: -> add_detector_tool(via="image")
    via="image":  User enters image URL, name etc.  -> image/tool will be added to config templates
    Args: 
        formData: form data after submit
    via:
        "image" or "repo"
    Returns:
        dict: message to be displayed on the web client
    """
    kwargs = {field.short_name: field.data.strip() for field in formData.tool}
    toolName = kwargs.get('toolName')

    match via:
        case "repo":
            build_image_task.apply_async(kwargs=kwargs)
            return {
                'type': "success", 
                'message': f"""The image build of your submitted clone detector tool will now start. <br>
                            Please visit the <a href="{url_for("main.show_logs", logCategory="imageBuild")}">image Build Logs</a>
                            to monitor the current progress and wait for the process to finish, 
                            in order to go to the next step. """
                        }
        case "image":
            return add_arguments_to_template(toolName, formData)
        case _:
            raise ValueError("via not in {'repo', 'image'}")   
    

def add_arguments_to_template(toolName: str, formData) -> dict:
    """
    Add arguments for the new clone detector tool config and Big Clone Eval arguments 
    to the new template config file. 
    This file is a copy of the template for new tools at project/utils/ImageBuilder/newTool.cfg.template
    and will be modified based on form data from the website.
    """

    # 1) arguments of the tool
    toolFile = Path(settings.directories['confTemplates']) / f"{toolName}{settings.templateFiles['fileExtensionWebEdit']}"
    copy2(settings.templateFiles['newToolTemplate'], toolFile)
    _update_config_with_form_data(toolFile, formData)

    # 2) # arguments of BCE
    toolFile = Path(settings.directories['confTemplates']).joinpath(
        f"{toolName}{settings.templateFiles['fileExtensionBase']}"
    )
    # if a config file was uploaded, save it and override values in it, based on the DefaultValue form inputs
    if config_file_was_uploaded(formData):
        if save_uploaded_file(formData, toolFile) == "error":
            return {
                'type': "error", 
                'message': f"""Error: All arguments entered in this form should be included in your uploaded configuration file, but not more than in this file.""" 
                    }
    # if no config file was uploaded, create a new file and insert values based on the DefaultValue form inputs
    else:
        sc.create_shell_config_file(toolFile, _extract_arguments(formData, 'DefaultValue'))

    copy_config_files_from_template_dir_to_workbench()

    return {
            'type': "success", 
            'message': f"""Your image was added to this web platform. <br>
                        You can now start your clone detection benchmarking with your new tool 
                        at '<a href="{url_for("main.run")}">Run</a>' """ 
                }


def save_uploaded_file(formData, toolFile: Path) -> str:
    """
    save the uploaded file in the template directory, if it is valid
    and update values in it based on the submitted form data
    """
    tmpStorage = Path("temp.cfg")
    uploadedFile = formData.toolArgsFile.data
    uploadedFile.save(tmpStorage)
    if not validate_file(formData, tmpStorage):
        tmpStorage.unlink()
        return "error"
    
    copy2(tmpStorage, toolFile)
    sc.update_shell_config_file(toolFile, _extract_arguments(formData, 'DefaultValue'))
    tmpStorage.unlink()
    return "success"


def config_file_was_uploaded(formData) -> bool:
    uploadedFile = formData.toolArgsFile.data
    return True if uploadedFile.filename else False 


def validate_file(formData, file: str) -> bool:
    """
    check if the uploaded file is valid = arguments entered in the form are a subset of the arguments in this file
    """
    formArguments = [argument['Name'] for argument in formData.toolArgs.data]

    fileArguments = sc.read_shell_config_file(file)
    fileArguments = [arg.split("=",1)[0] for arg in fileArguments]

    if set(formArguments).issubset(fileArguments):
        return True
    else:
        return False
    
def _extract_template_container_data(formData) -> dict:
    """
    extract information for the [container] section of the new detector tool template file

    """
    toolInformation = {key: value for key, value in formData.tool.data.items()}
    toolInformation['image'] = toolInformation.pop('imageURL')
    toolInformation['mountpoint_detector_config'] = toolInformation.pop('toolConfigFilePath')
    toolInformation.pop('toolName')
    return toolInformation


def _update_config_with_form_data(toolFile: Path, formData) -> None:
    """
    Update the tool configuration template file with form data for the container, descriptions and default values sections.
    """
    # [container]
    toolInformation = _extract_template_container_data(formData)
    cp.update_config(toolFile, settings.templateFiles['containerSection'], toolInformation)

    # [detector-argument-descriptions]
    descriptionArguments = {d['Name']: d['Description'] for d in formData.toolArgs.data}
    descriptionArguments = {key: value.replace("\r\n", "<br>").replace("\n", "<br>") for key, value in descriptionArguments.items()}
    cp.update_config(toolFile, settings.templateFiles['descriptionSection'], descriptionArguments)
    
    # [detector-argument-defaults]
    defaultArguments = {d['Name']: d['DefaultValue'] for d in formData.toolArgs.data}
    cp.update_config(toolFile, settings.templateFiles['defaultValueSection'], defaultArguments)

    _add_BigCloneEval_arguments(formData, toolFile)


def _extract_arguments(formData, argType: str) -> dict:
    """
    Extract values of a specified key ('Description' or 'DefaultValue') from form data and return them in one single dict.

    Args: 
        formData: form data after submit, array of dicts
            e.g.: 
            [{'Name': 'arg1', 'Description': 'description of arg1', 'DefaultValue': ''}, 
            {'Name': 'arg2', 'Description': '123', 'DefaultValue': ''}, 
            {'Name': 'arg3', 'Description': 'abc', 'DefaultValue': ''}]
        argType: dict key, 'Description' or 'DefaultValue'

    Returns:
        one dict, containing values of 'Name' key and argType key from all dicts
        e.g.:  {'arg1': 'description of arg1', 'arg2': '123', 'arg3': 'abc'}
    """
    return {d['Name']: d[argType] for d in formData.toolArgs.data}


def _add_BigCloneEval_arguments(formData, toolFile)-> None:
    """
    adds values for the [benchmark-argument-descriptions] and [benchmark-argument-defaults] sections to the new template file

    """
    arguments = {}
    section = settings.templateFiles['benchmarkDefaultValueSection']
    options = cp.read_cp_config_file(toolFile).options(section)
    for i, option in enumerate(options):
        arg = str(formData.bceArgs.data[i]['argument']).strip()
        if arg:
            arguments[option] = formData.bceArgs.data[i]['argument']

    cp.update_config(toolFile, section, arguments)
    
"""
def check_image(image) -> bool:
    client = docker.from_env()

    def image_exists_local(image) -> bool:
        try:
            client.images.inspect_image(image)
            return True
        except docker.errors.ImageNotFound:
            return False

    def image_exists_remote(image) -> bool:
        try:
            client.images.pull(image)
            return True
        except docker.errors.ImageNotFound:
            return False
        except docker.errors.APIError as e:
            print(f"An API error occurred: {e}")
            return False
        
    if not image_exists_remote(image) and not image_exists_local(image):
        print(f"ERROR: Image '{image}' not found!")
        return False
    else:
        return True
    
"""

