from flask import url_for
from project.tasks import start_container_runner
from project.utils.configure import configure_redis, get_run_directory
import project.settings as settings
from project.utils.utils import read_template_files, read_benchmark_files
import project.utils.configFilesParser.shellConfigFiles as sc
from shutil import copy2
import project.utils.configFilesParser.configParserFiles as cp
from pathlib import Path
from re import fullmatch
import shutil

class SetupRun():

    def __init__(self, formData, cliMode:bool = False, importDir:str = None) -> None:
        self.formData           = formData
        self.templateDir        = Path(settings.directories["confWorkbench"])
        self.runDir             = get_run_directory(runName=self.formData.get("runName"))
        self.runID              = self.runDir.name
        self.benchmarks         = read_benchmark_files()
        self.detectorTemplates  = read_template_files()
        self.redis              = configure_redis()

        self.cliMode            = cliMode
        if cliMode:
            if importDir:
                self.importDir      = Path(importDir)  # only used for CLI Mode
            else:
                raise ValueError("value of paramter importDir missing")
            

    def get_selected(self, templates: list[dict]) -> list[dict]:
        """
        selects all elements of the specified templates list 
        (self.detectorTemplates for clone detector tools or self.benchmarks for benchmarks) 
        that were selected in the web form.
        This means that only the detector tools whose checkbox was clicked in the web form remain.

        Returns:
            Array of selected dicts (detector tools whose checkbox was clicked), 
            containing the filename and config content of each file ( similar format as read_template_files() )
        """

        def is_selected(detector):
            filename = detector['filename']
            formValueName = f"{filename}--selected"

            return self.formData.get(formValueName)
        
        selectedDetectors = [detector for detector in templates if is_selected(detector)]

        return selectedDetectors

    def start_run(self) -> dict:

        # only used for debugging, to allow mutliple runs at the same time
        #self.redis.set("run.status", "finished")

        # prevent whitespaces, since this could lead to error in docker
        if not fullmatch(pattern=r"^[\w\d\_\-\.]*", string=self.runID):
            return {'type': "error", 
                    'message': "Run name: only [a-z A-Z 0-9 _ . -] allowed, no whitespaces" }

        # check if a run is executed at the moment
        if self.redis.hget('run.progress', 'isExecuted') == "True":
            return {'type': "error", 
                    'message': "Another run is being executed at the moment. Please wait and try again" }
        
        self.redis.set("run.status", "starting")
        
        # update detectors list
        # only those detector tools whose checkbox was clicked in the web form remain
        self.detectorTemplates = self.get_selected(self.detectorTemplates)
        # update benchmarks list
        self.benchmarks = self.get_selected(self.benchmarks)

        if len(self.detectorTemplates) == 0:
            self.redis.set("run.status", "aborted")
            return {'type': "error", 
                    'message': "no detector tool selected" }
        
        if len(self.benchmarks) == 0:
            self.redis.set("run.status", "aborted")
            return {'type': "error", 
                    'message': "no benchmark selected" }

        if self.cliMode:
            if not self.importDir.is_dir():
                raise NotADirectoryError(f"{self.importDir} is not a directory")
            
            # Copies the entire directory recursively from self.importDir (given as CLI option) to the new run directory. 
            # If the destination directory already exist, it will be overwritten (dirs_exist_ok=True).
            # Files matching the patterns '*.csv', '*.report', and '*.log' will be ignored during the copy process.
            csvSuffix = settings.benchmarks['detectedClonesFileExtension']
            ReportSuffix = settings.benchmarks['reportFileExtension']

            shutil.copytree(self.importDir, self.runDir, dirs_exist_ok=True, 
                            ignore=shutil.ignore_patterns(csvSuffix, ReportSuffix,'*.log'))

        else:
            # get website form data and save to config files in run dir
            self.form_data_to_files()

        # extract container config from config templates
        containerConfigs = self.assamble_container_configs()

        # extract benchmark directories and names
        benchmarks = self.assamble_benchmarks()

        # run container of each detector tool 
        # in celery task queue, executed by worker services in the background
        start_container_runner.apply_async(args=(containerConfigs, str(self.runDir), benchmarks))

        if self.cliMode: 
            return {'type': "success", 'message': f"""Run started."""}
        else:
            return {'type': "success", 
                    'message': f"""Run started. <br>
                            The current progress can be monitored via the 
                            '<a href="{url_for("main.show_logs", logCategory="run")}">Logs (Run)</a>' 
                            menu item."""}
    

    def assamble_benchmarks(self) -> list[dict]:
        """
        Extract names, pretty names and container configuration of each benchmark, which will be used for this run.

        Returns:
            list of dicts,
            containing the names, pretty names and container configuration of each benchmark
            e.g:
            [
                {
                    "name":"BigCloneEval",
                    "general":{
                        "pretty_name":"Big Clone Eval",
                        "description": 'Repo: <a href="https://github.com/jeffsvajlenko/BigCloneEval">https://github.com/jeffsvajlenko/BigCloneEval</a>'
                    },
                    "container":{
                        "image":"ghcr.io/glopix/cloreco-images/big-clone-eval",
                        "benchmark_path":"/cloneDetection/benchmark/"
                    }
                },
                {
                    "name":"GoogleCodeJam",
                    "general":{
                        "pretty_name":"Google Code Jam",
                        "description": ''
                    },
                    "container":{
                        "image":"ghcr.io/glopix/cloreco-images/google-code-jam",
                        "benchmark_path":"/cloneDetection/benchmark/"
                    }
                }
            ]
        """
        benchmarks = []
        for benchmark in self.benchmarks:
            benchmarks.append( 
                {
                'name'      : benchmark['name'],
                'general'   : benchmark['general'],
                'container' : benchmark['container'],
                }
            )

        return benchmarks

    def assamble_container_configs(self) -> list[dict]:
        """
        Extract container config from clone detector tool config templates.

        Returns:
            list of dictionaries, 
            containing the configuration of the to be executed containers of each clone detector tool
            e.g.:
                [
                    {
                        "detector_config_filename":"Sourcer-CC.cfg.web.template",
                        "entrypoint_config_filename":"entrypoint.cfg",
                        "container":{
                            "image":"ghcr.io/glopix/cloreco-images/sourcer-cc",
                            "mountpoint_base":"/cloneDetection/",
                            "mountpoint_detector_config":"/cloneDetection/Applications/SourcerCC/clone-detector/sourcerer-cc.properties",
                            "mountpoint_entrypoint_config":"/cloneDetection/entrypoint.cfg"
                        }
                    },
                    {
                        "detector_config_filename":"StoneDetector.cfg.web.template",
                        "entrypoint_config_filename":"entrypoint.cfg",
                        "container":{
                            "image":"ghcr.io/glopix/cloreco-images/stone-detector",
                            "mountpoint_base":"/cloneDetection/",
                            "mountpoint_detector_config":"/cloneDetection/Applications/StoneDetector/config/default.properties",
                            "mountpoint_entrypoint_config":"/cloneDetection/entrypoint.cfg"
                        }
                    }
                ]
        """
        containerConfigs = []
        for template in self.detectorTemplates:
            containerConfigs.append( 
                {
                'detector_config_filename'  : template['filename'],
                'entrypoint_config_filename': template['benchmarkCfgFilename'],
                'container'                 : template['container'],
                }
            )
        
        return containerConfigs

    def form_data_to_files(self) -> None:
        """
        execute form_data_to_file() for each clone detector tool
        and create subdirectory
        """
        # create a new directory, if it doesn't exist
        self.runDir.mkdir(exist_ok=True)

        self.benchmarks_form_data_to_files()

        for benchmark in self.benchmarks:
            benchmark = benchmark['name']
            for detector in self.detectorTemplates:

                detectorName = detector['detectorName']
                detectorFolder = self.runDir / benchmark / detectorName

                # create a new directory for this detector tool, if it doesn't exist
                detectorFolder.mkdir(exist_ok=True)

                self.form_data_to_file(detector, detectorFolder)


    def get_form_data(self, filename: str, arguments: dict, detectorBenchmarkSettings=False) -> dict:
        """
        Retrieve detector tool config data from the website form and return this data as a dict.
        If the detector tool specific BigCloneEval (detectTools) config (set on the website per detector tool) should be retrieved,
        a different prefix with the Benchmark Framework config file name (in the containers) will be used to get the values.

        Returns:
            {
            'argument1': '16200',
            'argument2': 'true',
            'argument3': 'NTG',
            }
        """
        if detectorBenchmarkSettings:
            formValuePrefix = f"{filename}__{settings.benchmarks['configFileName']}"
        else:
            formValuePrefix = f"{filename}"

        config = {}
        for argument in arguments:
            # Get value of variable from website form
            formValueName = f"{formValuePrefix}__{argument['name']}"
            config[argument['name']] = self.formData.get(formValueName)

        return config


    def form_data_to_file(self, detector: dict, directory: Path) -> None:
        """
        Retrieve data from website form 
        and create two config files for each clone detector tool
        based on the variable names from the template file 
        with the values from the website form.
        config file 1: arguments for detector tool
        config file 2: benchmark arguments for entrypoint.py script (entrypoint.cfg)

        Step 1:
            copy template config files, so all arguments will be initialized with default values
        Step 2:
            get data from website form and override arguments in the previously copied files
        """
        detectorName = detector['detectorName']
        filename = detector['filename']

        # copy base config file of detector tool to detector dir
        srcFile = self.templateDir / f"{detectorName}{settings.templateFiles['fileExtensionBase']}"
        dstFile = directory / f"{detectorName}{settings.templateFiles['fileExtensionFinal']}"
        copy2(srcFile, dstFile)

        # copy benchmakr config file (entrypoint.cfg) from <run>/<benchmark>/ dir to detector dir
        srcFile = directory.parent / settings.benchmarks['configFileName']
        dstFile = directory / settings.benchmarks['configFileName']
        copy2(srcFile, dstFile)

        ####### Step 2: get data from website form and override arguments in the previously copied files
        # get config for detector tool
        config = self.get_form_data(filename, arguments=detector['arguments'])
        # write detector tool config to detector config file
        sc.update_shell_config_file(file=f"{directory}/{detectorName}{settings.templateFiles['fileExtensionFinal']}", config=config)

        # get detector tool specific benchmark config (entrypoint.cfg)
        config = self.get_form_data(filename, arguments=detector['benchmarkArguments'], detectorBenchmarkSettings=True)
        # write detector tool specific benchmark config to benchmark config file (default: entrypoint.cfg)
        cp.update_config(dstFile, section=settings.benchmarks['detectClonesSection'], config=config)

    
    def benchmarks_form_data_to_files(self) -> None:
        evaluateToolDefaults = settings.benchmarks["evaluateToolDefaults"]
        evaluateToolSection = settings.benchmarks["evaluateToolSection"]

        detectClonesDefaults = settings.benchmarks["detectClonesDefaults"]
        detectClonesSection = settings.benchmarks["detectClonesSection"]

        for benchmark in self.benchmarks:
            runBenchmarkDir = self.runDir / benchmark["name"]
            runBenchmarkDir.mkdir(exist_ok=True)

            filename = benchmark["filename"]
            templateFile = benchmark["filepath"]
            dstFile = runBenchmarkDir / settings.benchmarks["configFileName"]

            # copy default values from benchmark template file into new entrypoint.cfg config file (evaluateTool arguments) in the run dir 
            cp.copy_config_section(templateFile, dstFile, srcSection=evaluateToolDefaults, dstSection=evaluateToolSection)

            # config for detector tool
            config = self.get_form_data(filename, arguments=benchmark['evaluateToolArguments'])
            cp.update_config(dstFile, evaluateToolSection, config)

            # copy default values from benchmark template file into new entrypoint.cfg config file (detectTools arguments) in the run dir 
            cp.copy_config_section(templateFile, dstFile, srcSection=detectClonesDefaults, dstSection=detectClonesSection)

            # config for detector tool
            config = self.get_form_data(filename, arguments=benchmark['detectClonesArguments'])
            cp.update_config(dstFile, detectClonesSection, config)

