#!/usr/bin/env bash
# runner script for DrDup2 (https://github.com/tronicek/DrDup2)

CLONES_INPUT_PATH="$1"

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

CONFIG_FILE_ORIG="${MAIN_DIR}/drdup2-mounted.config"
CONFIG_FILE="${MAIN_DIR}/drdup2.config"
KEY="sourceDir"

# since the config file is mounted, it can't be changed in place
# which is why we copy it
cp "$CONFIG_FILE_ORIG" "$CONFIG_FILE"

# Check if the 'sourceDir' key exists and set it to the clones path, or append if it doesn't
if grep -q "^${KEY}[[:space:]]*="   "$CONFIG_FILE"; then
    sed -i "s|^${KEY}[[:space:]]*=.*|${KEY}=${CLONES_INPUT_PATH}|" "$CONFIG_FILE"
else
    echo "${KEY}=${CLONES_INPUT_PATH}" >> "$CONFIG_FILE"
fi

# execute DrDup2-1.0-jar with drdup2.config configuration file,
# redirect and append both stdout and stderr to $OUTPUT_TARGET
java -jar target/DrDup2-1.0-jar-with-dependencies.jar "$CONFIG_FILE"  &>> $OUTPUT_TARGET    || exit 1

python3 transform-output-xml-to-csv.py drdup-output.xml drdup-output.csv

# print results to stdout
cat drdup-output.csv

rm drdup-output.xml drdup-output.csv
