from configparser import ConfigParser
from glob import glob
import project.settings as settings
import project.utils.configFilesParser.configParserFiles as cp
from pathlib import Path
from shutil import copy2


def read_benchmark_files(fromDir:str = None) -> list[dict]:
    """
    Reads all benchmark files (<Name>.benchmark in data/cloneDetection/benchmarks/ or in fromDir)
    and extracts the following informations for each benchmark:
        - name of the benchmark     (e.g. GoogleCodeJam)
        - filename of the benachmark (e.g. GoogleCodeJam.benchmark)
        - pretty name of the benchmark, as set in the benchmark file (e.g. Google Code Jam)
        - path to this benchmark file (e.g. .../benchmarks/GoogleCodeJam.benchmark)
        - descriptions and default values of the arguments of the 'detectClones' command
        - descriptions and default values of the arguments of the 'evaluateTool' command
        - container configuration

    Returns:
        a list of dicts, containing these informations
        e.g.:
            [
                {
                    "name":"BigCloneEval",
                    "filename":"BigCloneEval.benchmark",
                    "prettyName":"Big Clone Eval",
                    "filepath":"/app/data/cloneDetection/benchmarks/BigCloneEval.benchmark",
                    "detectClonesArguments":[
                        {
                            "name":"bcb_parts",
                            "description":"Which parts of the BigCloneBench (IJaDataset) clone database will be used <br> Valid values: 1-45, \"all\" (default);   seperate multiple values by \\',\\',   ranges by \\'-\\' <br> e.g.:  1, 2, 6-11",
                            "default":"all"
                        }
                    ],
                    "evaluateToolArguments":[
                        {
                            "name":"minimum-judges",
                            "description":"Minimum number of judges.",
                            "default":""
                        },
                        {
                            "name":"matcher",
                            "description":"Specify the clone matcher. See documentation for configuration strings. Default is coverage-matcher with 70% coverage threshold.",
                            "default":"CoverageMatcher 0.7"
                        },
                        ...
                    ],
                    "container":{
                        "image":"ghcr.io/glopix/cloreco-images/big-clone-eval",
                        "benchmark_path":"/cloneDetection/benchmark/"
                    }
                },
                {
                    "name":"GoogleCodeJam",
                    "filename":"GoogleCodeJam.benchmark",
                    "prettyName":"Google Code Jam",
                    "filepath":"/app/data/cloneDetection/benchmarks/GoogleCodeJam.benchmark",
                    "detectClonesArguments":[
                        ...
                    ],
                    "evaluateToolArguments":[
                        ...
                    ],
                    "container":{
                        "image":"ghcr.io/glopix/cloreco-images/google-code-jam",
                        "benchmark_path":"/cloneDetection/benchmark/"
                    }
                }
            ]
    """
    if fromDir:
        dir = Path(fromDir)
    else:
        dir = Path(settings.directories["benchmarks"])

    fileExtension = settings.benchmarks["fileExtension"]
    containerSection = settings.benchmarks["containerSection"]

    benchmarks = []
    
    # loop over every benchmark file (<name>.benchmark)
    for benchmarkFile in dir.glob(f"*{fileExtension}"):
        if benchmarkFile.is_dir(): continue

        detectClonesArguments = read_description_and_defaults(benchmarkFile, settings.benchmarks['detectClonesDescriptions'], settings.benchmarks['detectClonesDefaults'])
        evaluateToolArguments = read_description_and_defaults(benchmarkFile, settings.benchmarks['evaluateToolDescriptions'], settings.benchmarks['evaluateToolDefaults'])
        
        configFile = cp.read_cp_config_file(benchmarkFile)
        container  = dict(configFile[containerSection])

        # remove all whitespaces in file name, without suffix
        # e.g. 'big cloneEval.benchmark' -> bigcloneEval
        name = benchmarkFile.stem.strip(" ").strip()

        prettyName = configFile.get(settings.benchmarks["generalSection"], "pretty_name", fallback=name)

        templateConfig = {
            'name'          : name,
            'filename'      : benchmarkFile.name,
            'prettyName'    : prettyName,
            'filepath'      : str(benchmarkFile.resolve()),
            'detectClonesArguments' : detectClonesArguments,
            'evaluateToolArguments' : evaluateToolArguments,
            'container'     : container,
        }
        benchmarks.append(templateConfig)
    
    # sort the list of dictionaries by the 'name' key
    return sorted(benchmarks, key=lambda x: x['name'])

def read_template_files(fromDir:str = None) -> list[dict]:
    """
    reads configuration from all files in the workbench directory or the specified directory

    Returns:
    Array of dicts, containing the filenames and (template)config content of each file
    e.g.:
    [
        {
            "filename": "NiCad.cfg.web.template",
            "baseFilename": "NiCad.cfg.template",
            "detectorName": "NiCad",
            "container": {
                "image": "NiCad",
                "mountpoint_base": "/cloneDetection/",
                "mountpoint_detector_config": "/cloneDetection/Applications/NiCad/config/myconfig.cfg",
                "mountpoint_entrypoint_config": "/cloneDetection/entrypoint.cfg",
            },
            "arguments": 
            [
                {
                    "name": "var1",
                    "description": "Description of variable1",
                    "default": "True",
                },
                {
                    "name": "var2",
                    "description": "Description of variable2",
                    "default": "dfs",
                },
                {
                    "name": "var3",
                    "description": "Description of variable3",
                    "default": "2342",
                },
            ],
            "benchmarkCfgFilename" : "entrypoint.cfg",
            "benchmarkArguments": 
            [
                {
                    "name": "max_files",
                    "description": "Maximum amount of files",
                    "default": "100000",
                }
            ],
        },
        {
            "filename": "Tool2.cfg.web.template",
            "baseFilename": "Tool2.cfg.template",
            "detectorName": "Tool2",
            "container": {
                "image": "Tool2",
                "mountpoint_detector_config": "/cloneDetection/Applications/Tool2/confdir/default.cfg",
                "mountpoint_entrypoint_config": "/cloneDetection/entrypoint.cfg",
            },
            "arguments": 
            [
                {"name": "var14", "description": "Description of variable1", "default": "False"},
                {"name": "var12", "description": "Description of variable2", "default": "420"},
                {"name": "var33", "description": "Description of variable3", "default": ""},
            ],
            "benchmarkCfgFilename" : "entrypoint.cfg",
            "benchmarkArguments": 
            [
                {
                    "name": "max_files",
                    "description": "Maximum amount of files",
                    "default": "20000",
                }
            ],
        },
    ]
    """
    if fromDir: 
        dir = Path(fromDir)
    else:
        dir = Path(settings.directories["confWorkbench"])

    configFiles = []
    fileExtensionWebCfg = settings.templateFiles['fileExtensionWebEdit']

    for file in dir.glob(f"*{fileExtensionWebCfg}"):
        file = Path(file)
        config = read_template_file(file)
        detectorName = file.name.split(fileExtensionWebCfg, 1)[0]
        baseFile = Path(f"{detectorName}{settings.templateFiles['fileExtensionBase']}")

        configFiles.append(
            {
                'filename'             : file.name,
                'baseFilename'         : baseFile.name,
                'detectorName'         : detectorName,
                'container'            : config['container'],
                'arguments'            : config['arguments'],
                'benchmarkCfgFilename' : settings.benchmarks['configFileName'],
                'benchmarkArguments'   : config['benchmarkArguments']
            }
        )
    
    return configFiles

def read_description_and_defaults(file: str|ConfigParser, descriptionSection: str, defaultValueSection:str=None) -> list[dict]:
    """
    Reads the configuration from the specified ConfigParser object.
    This includes:  
        arguments, description and default values(optional)
    
    Returns:
        A list of dicts, containing the arguments, description and default values(optional)
    e.g.:
    [
        {"name": "var1", "description": "Description of variable1", "default": "True"},
        {"name": "var2", "description": "Description of variable2", "default": "dfs"},
        {"name": "var3", "description": "Description of variable3", "default": "2342"},
    ]

    """
    if isinstance(file, ConfigParser):
        parsedConfigFile = file
    else:
        parsedConfigFile = cp.read_cp_config_file(file)


    # Read arguments and descriptions of the detector software from the config file
    arguments = dict(parsedConfigFile[descriptionSection])

    # Read Benchmark specific argument defaults for this detector software from the config file, if present
    defaults = {}
    if defaultValueSection:
        if defaultValueSection in parsedConfigFile:
            defaults = dict(parsedConfigFile[defaultValueSection])

    config = []

    for argument in arguments:
        argumentDict = {
            "name": argument,
            "description": arguments[argument]
        }
        if defaultValueSection:
            argumentDict["default"] = defaults.get(argument, "")

        config.append(argumentDict)

    return config

def read_template_file(file: str) -> dict[dict]:
    """
    Reads the configuration from the specified file.
    This includes:  
        container configuration;  
        arguments, description and default values of detector tool software
        Benchmark specific arguments, description and default values for this detector tool software

    Returns:
        a nested dict
    e.g:
    {
        "container": {
            "image": "NiCad",
            "mountpoint_base": "/cloneDetection/",
            "mountpoint_detector_config": "/cloneDetection/Applications/NiCad/config/myconfig.cfg",
            "mountpoint_entrypoint_config": "/cloneDetection/entrypoint.cfg",
        },
        "arguments": [
            {"name": "var1", "description": "Description of variable1", "default": "True"},
            {"name": "var2", "description": "Description of variable2", "default": "dfs"},
            {"name": "var3", "description": "Description of variable3", "default": "2342"},
        ],
        "benchmarkArguments": [
            {
                "name": "max_files",
                "description": "Maximum amount of files",
                "default": "100000",
            }
        ],
    }
    """
    configFile = cp.read_cp_config_file(file)

    containerSection        = settings.templateFiles['containerSection']
    descriptionSection      = settings.templateFiles['descriptionSection']
    defaultValueSection     = settings.templateFiles['defaultValueSection']
    benchmarkDescriptionSection   = settings.templateFiles['benchmarkDescriptionSection']
    benchmarkDefaultValueSection  = settings.templateFiles['benchmarkDefaultValueSection']
    
    container        = dict(configFile[containerSection])
    arguments        = read_description_and_defaults(configFile, descriptionSection, defaultValueSection)
    benchmarkConfig  = read_description_and_defaults(configFile, benchmarkDescriptionSection, benchmarkDefaultValueSection)

    # ensure no value is empty in the container section
    if any(not str(value).strip() for value in container.values()):
        raise ValueError(f"Error in {file}: At least one required value in the [{containerSection}] section is empty or contains only whitespaces.")

    config = {
        'container' : container,
        'arguments' : arguments,
        'benchmarkArguments': benchmarkConfig
    }
    
    return config

def copy_config_files_from_template_dir_to_workbench() -> None: 
    """
    copy all clone detector tool config files from the template directory to the workbench directory
    """
    templDir = Path(settings.directories["confTemplates"])
    confDir = settings.directories["confWorkbench"]

    webTemplateFiles = glob(f"{templDir}/*{settings.templateFiles['fileExtensionWebEdit']}")
    templateBaseFile = glob(f"{templDir}/*{settings.templateFiles['fileExtensionBase']}")

    srcFiles = webTemplateFiles + templateBaseFile

    for file in srcFiles:
        copy2(templDir / file, confDir)

