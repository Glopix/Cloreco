#!/usr/bin/env bash
# runner script for NIL (https://github.com/kusumotolab/NIL)


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
    echo "Error: No value provided for the input directory argument (\$1)." >> $OUTPUT_TARGET
    exit 1
fi

CONF_FILE="NIL.config"
# Read config values  from the config file
if [[ -f "$CONF_FILE" ]]; then
    source "${MAIN_DIR}/$CONF_FILE"
else
    echo "config file not found."
    echo "config file not found." >> $OUTPUT_TARGET
    exit 1
fi

ARGUMENTS=("--output" "result.csv")
ARGUMENTS+=("--src" "$1")
ARGUMENTS+=("--bigcloneeval")
ARGUMENTS+=("--language" "java")

# Check if the variables are defined and not empty
# append arguments
if [[ -n "$min_line" ]]; then
    ARGUMENTS+=("--min-line" "$min_line")
fi

if [[ -n "$min_token" ]]; then
    ARGUMENTS+=("--min-token" "$min_token")
fi

if [[ -n "$n_gram" ]]; then
    ARGUMENTS+=("--n-gram" "$n_gram")
fi

if [[ -n "$partition_number" ]]; then
    ARGUMENTS+=("--partition-number" "$partition_number")
fi

if [[ -n "$filtration_threshold" ]]; then
    ARGUMENTS+=("--filtration-threshold" "$filtration_threshold")
fi

if [[ -n "$verification_threshold" ]]; then
    ARGUMENTS+=("--verification-threshold" "$verification_threshold")
fi

# execute NIL-all.jar with arguments 
# and redirect and append both stdout and stderr to $OUTPUT_TARGET
java -XX:MaxRAMPercentage=80 -jar ./build/libs/NIL-all.jar "${ARGUMENTS[@]}"  &>> $OUTPUT_TARGET    || exit 1

# print results to stdout
cat result.csv

rm result.csv
