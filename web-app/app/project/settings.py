from os import path
from pathlib import Path

def thisDir():
    # /app/project/
    return Path(__file__).resolve().parent

def appRootDir():
    # /app/
    return thisDir().parent

templateFiles = dict(
    # subset of config files, includes only config arguments which will appear in web form, splitted in descriptions and defaults
    fileExtensionWebEdit = ".cfg.web.template",
    # whole (original) config files, including parts/arguments which won't appear in the web form
    fileExtensionBase = ".cfg.template",
    # file extension in execution stage
    fileExtensionFinal = ".cfg",
    # Section in config files, where the discription of each config argument is set
    descriptionSection  = 'detector-argument-descriptions',
    # Section in config files, where the default value of each config argument is set
    defaultValueSection = 'detector-argument-defaults',
    # Section in config files, where the Container config is set
    containerSection    = 'container',
    # Section in config files, where the description or defaults of the global(same for all tools) Benchmark settings are stored
    benchmarkDescriptionSection  = 'benchmark-argument-descriptions',
    benchmarkDefaultValueSection = 'benchmark-argument-defaults',
    # template for new created tools
    newToolTemplate = f"{thisDir()}/utils/ImageBuilder/newTool.cfg.template"
)

directories = dict(
    benchmarks      = f"{appRootDir()}/data/cloneDetection/benchmarks/",
    confTemplates   = f"{appRootDir()}/data/cloneDetection/cloneDetectorTools/templates/",
    confWorkbench   = f"{appRootDir()}/data/cloneDetection/cloneDetectorTools/workbench/",
    runs            = f"{appRootDir()}/data/cloneDetection/runs/",
    downloads       = f"{appRootDir()}/data/cloneDetection/archivedRuns/"
)

benchmarks = dict(
    # files in directories["benchmarks"] with this suffix will be used
    fileExtension            = ".benchmark",
    startCommand             = "python3 /cloneDetection/entrypoint.py",
    configFileName           = "entrypoint.cfg",
    templateFileName         = "BigCloneEval",
    # Section in config files, where some general settings are set
    generalSection           = 'general',
    # Section in config files, where the Container config is set
    containerSection         = 'container',
    # Section in config files, where the default value of each 'detectClones' command argument is set
    detectClonesDefaults     = "detectClones-defaults", 
    detectClonesDescriptions = "detectClones-descriptions",
    # Section in config files, where the default value of each 'evaluateTool' command argument is set
    evaluateToolDefaults     = "evaluateTool-defaults",
    evaluateToolDescriptions = "evaluateTool-descriptions",
    # must match the detectClonesSection and evaluateToolSection in entrypoint.py in containers:
    detectClonesSection      = "detectClones",
    evaluateToolSection      = "evaluateTool",
    detectedClonesFileExtension = ".csv",
    reportFileExtension      = ".report",
)

ImageBuilder = dict(
    availableJDKs       = ["jdk8", "jdk11", "jdk17"],
    availableDistros    = ["ubuntu22.04", "ubuntu18.04"],
    baseImage           = "ghcr.io/glopix/abcd-images/detector-tool-base"
)