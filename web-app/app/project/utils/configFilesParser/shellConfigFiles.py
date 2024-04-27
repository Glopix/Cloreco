

def read_shell_config_file(file: str) -> list:
    """
    read values from a existing config file in shell config style (without sections)

    e.g. imput file:
    var1=432
    var2=abc
    """

    with open(file, 'r') as f:
        lines = f.readlines()

    retLines = []
    for line in lines:
        if line.startswith(("#", "//")):
            continue
        line = line.strip()
        if line:
            retLines.append(line)

    return retLines

def update_shell_config_file(file: str, config: dict) -> None:
    """
    update values in a existing config file in shell config style (without sections)

    Resulting file e.g.:
    var1=432
    var2=abc
    """
    lines = read_shell_config_file(file)

    updatedLines = []
    for line in lines:
        for arg, value in config.items():
            if line.startswith(f"{arg}="):
                updatedLines.append(f"{arg}={value}\n")
                break
        else:
            updatedLines.append(line)

    # append newline to every line, if not present
    updatedLines = [f"{line}\n" if not line.endswith("\n") else line for line in updatedLines ]

    with open(file, 'w') as f:
        f.writelines(updatedLines)


def create_shell_config_file(file: str, config: dict) -> None:
    """
    create a new config file in shell config style (without sections)

    Resulting file e.g.:
    var1=432
    var2=abc
    """
    lines = []

    for arg, value in config.items():
        lines.append(f"{arg}={value}\n")

    # append newline to every line, if not present
    lines = [f"{line}\n" if not line.endswith("\n") else line for line in lines ]

    with open(file, 'w') as f:
        f.writelines(lines)
