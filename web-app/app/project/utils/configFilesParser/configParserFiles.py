from configparser import ConfigParser


def update_config(file: str, section: str, config: dict, override: bool =True):
    """
    create a new config file or modify a existing file in ConfigParser config style, with sections
    for later use in container

    optional: don't override existing values, only append new options ( default: override)

    
    e.g. resulting file:

    [SECTION1]  
    var1 = 432  
    var2 = abc
    """

    configFile = read_cp_config_file(file)

    if not configFile.has_section(section):
        configFile.add_section(section)

    # populate the ConfigParser instance with the dictionary data
    for option, value in config.items():
        # if values should not be overridden: check if the option doesn't already exist in the new config
        if not override and configFile.has_option(section, option):
            continue
        else:
            configFile.set(section, option, value)

    # Write the configuration to a file
    with open(file, 'w') as updatedFile:
        configFile.write(updatedFile)

    return

def copy_config_section(src: str, dst: str, srcSection: str, dstSection: str =None, override: bool =True):
    """
    copy one section of a source file into another destination file
    
    optional: specify a different destination section (default: same as source section)
    optional: don't override existing values, only append new options (default: override)
    """
    srcConfig = read_cp_config_file(src)

    if not dstSection:
        dstSection = srcSection

    newConfig = {}

    for option in srcConfig.options(srcSection):
        newConfig[option] = srcConfig.get(srcSection, option)

    update_config(dst, dstSection, newConfig, override)


def read_cp_config_file(file: str):
    config = ConfigParser(interpolation=None)
    # preserve formatting of argument names (don't change "MAX_FILES" to "max_files")
    config.optionxform = str
    config.read(file)

    return config
