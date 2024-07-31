#!/bin/bash

CONF_FILE="../iclones.config"

# dir of the tool
MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

# Check if LOGGING_VERBOSE env var is set and not empty
if [[ -n "$LOGGING_VERBOSE" ]]; then
  OUTPUT_TARGET="$LOGGING_VERBOSE"
else
  # if it is not set, redirects both stdout and stderr of all commands to /dev/null
  OUTPUT_TARGET="/dev/null"
fi

# Check if input dir is provided
if [[ -z "$1" ]]; then
    echo "Error: No value provided for the input directory argument (\$1)."
    exit 1
fi

# Read config values (minclone and minblock) from the config file in the parent directory
if [[ -f "$CONF_FILE" ]]; then
    source "${MAIN_DIR}/$CONF_FILE"
else
    echo "iClones config file not found."
    exit 1
fi

ICLONE_ARGUMENTS=("-output" "output/test")
ICLONE_ARGUMENTS+=("-input" "$1")
ICLONE_ARGUMENTS+=("-informat" "single")
ICLONE_ARGUMENTS+=("-language" "java")

# Check if the variables are defined and not empty
if [[ -n "$minblock" ]]; then
    ICLONE_ARGUMENTS+=("-minblock" "$minblock")
fi

if [[ -n "$minclone" ]]; then
    ICLONE_ARGUMENTS+=("-minclone" "$minclone")
fi

cd "$(dirname $0)"
java -XX:InitialRAMPercentage=50 -XX:MaxRAMPercentage=80 -jar target/iclones.jar "${ICLONE_ARGUMENTS[@]}"   &>> $OUTPUT_TARGET    || exit 1

python3 parseOutputSource.py   2>> $OUTPUT_TARGET  || exit 1
