from flask import Blueprint, render_template, redirect, request

import project.utils.utils as Utils
import project.utils.pages.downloads as Downloads
import project.utils.pages.run as Run
import project.utils.pages.logs as Logs
import project.forms as Forms
import project.utils.pages.addDetectorTool as AddDetectorTool

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    #return redirect("/run")
    return render_template('home.html')

############
# "Run" page
############
@main.route('/run', methods=['GET', 'POST'])
def run():

    detectorTemplates = Utils.read_template_files()
    benchmarks = Utils.read_benchmark_files()

    if request.method == 'GET':
        return render_template('run_form.html', detectorsTemplates=detectorTemplates, benchmarks=benchmarks)

    # on form submit
    if request.method == 'POST':
        msgToClient = Run.start_run(formData=request.form)
        return render_template('run_form.html', detectorsTemplates=detectorTemplates, benchmarks=benchmarks, messageFromServer=msgToClient)
    

# abort the current run
@main.route('/run_abort', methods=['GET'])
def run_abort():
    msg = Run.abort_run()
    return msg


# copy/duplicate a clone detector tool's config file
@main.route('/run/copy_detector_tool_config', methods=['PUT'])
def copy_detector_tool_config():
    if request.headers['Content-Type'] != 'application/json':
        return "error: Invalid content type. Expected application/json", 400

    requestData = request.get_json()
    if ('toolName' not in requestData) or ('newName' not in requestData):
        return "error: Invalid json data. Expected 'toolName' and 'newName' in json data", 400
    
    toolName = requestData['toolName']
    newName = requestData['newName']
    ret = Run.duplicate_tool_config(toolName, newName)
    return ret


# remove all duplicated tools and reset all tools to default
@main.route('/run/reset_workbench', methods=['GET'])
def reset_workbench():
    Run.reset_workbench_configs()
    return redirect("/run")


############
# "add tool" pages:
# add a new clone detector tool to the webinterface
# either based on a git repo or a (docker) image
############

# user can choose between the two methods 
@main.route('/run/add_detector_tool', methods=['GET'])
def add_detector_tool():
    return render_template('add_tool_step1_choice.html')


# based on a git repo or an image
# Process:
#   add via git repo:   User enters git URL, name etc. -> build image from repo via ImageBuilder.py with output to the "logs" page; on success: -> add via image
#   add via image:      add BigCloneEval arguments (max_files etc.) to the form -> User enters image URL, name etc.  -> image/tool will be added to config templates
@main.route('/run/add_detector_tool/<via>', methods=['GET', 'POST'])
def add_detector_tool_via(via: str):
    match via:
        case "repo":
            form = Forms.GitRepoForm()
        case "image":
            form = Forms.ImageForm()
        case _:
            raise ValueError("via not in {'repo', 'image'}")

    # dynamically add BigCloneEval arguments (max_files etc.) to the form 
    if request.method == 'GET' and via=="image":
        form = AddDetectorTool.append_bce_arguments_to_form(form)

    msgToClient = {}
    if form.validate_on_submit():
        # Process the data
        msgToClient = AddDetectorTool.add_detector_tool(form, via=via)
        return render_template('add_tool_step2_form.html', form=form, via=via, messageFromServer=msgToClient)

    # Pre-fill form ('toolName', 'imageURL') if query parameters exist ( = if this image was build via ImageBuilder.py based on a git repo)
    for field in ['toolName', 'imageURL']:
        if field in request.args:
            getattr(form.tool, field).data = request.args.get(field, '')
            

    return render_template('add_tool_step2_form.html', form=form, via=via)

############
# "Logs" page
############
@main.route('/logs/<logCategory>', methods=['GET'])
def show_logs(logCategory: str ="run"):

    if logCategory not in { 'run', 'imageBuild' }:
        return "Error: invalid /logs/<logCategory>"

    logHistory = Logs.get_log_history(logCategory)
    containerProgress = Logs.get_container_progress(logCategory)

    logsChannel, progressChannel, heartbeatsChannel = Logs.get_SSE_channels(logCategory)
        
    return render_template("show_logs.html", logHistory=logHistory, containerProgress=containerProgress, 
                           logsChannel=logsChannel, progressChannel=progressChannel, heartbeatsChannel=heartbeatsChannel)


############
# "Downloads" Page
############
@main.route('/downloads')
def downloads():
    #file_list = list_downloads()
    return redirect("/downloads/ ")


# List all files and directories in a directory
@main.route('/downloads/')
@main.route('/downloads/<path:path>/', strict_slashes=False)
def show_directory(path: str = None):  
    # Check if there is a trailing slash in the request URL
    if str(request.url).endswith('/'):
        files, diagrams, summaryData = Downloads.list_directory_content(path)
        return render_template('downloads.html', files=files, diagrams=diagrams, summaryData=summaryData)
    else:
        return Downloads.serve_file(path)


# delete a file or directory
@main.route('/downloads/<path:directory>', methods=['DELETE'])
def delete(directory: str):
    ret = Downloads.path_delete(directory)
    return ret


# download a file or directory (as zip file)
@main.route('/downloads/<path:directory>/download', methods=['POST'])
def download(directory: str):
    ret = Downloads.path_download(directory)
    return ret

############
# "Imprint" Page
############

@main.route('/imprint', methods=['GET', 'POST'])
def imprint():
    return render_template('imprint.html')

