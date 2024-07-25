#!/bin/bash

# Check if LOGGING_VERBOSE env var is set and not empty
if [[ -n "$LOGGING_VERBOSE" ]]; then
  OUTPUT_TARGET="$LOGGING_VERBOSE"
else
  # if it is not set, redirects both stdout and stderr of all commands to /dev/null
  OUTPUT_TARGET="/dev/null"
fi


cd "$(dirname $0)"
java -Xms8G -XX:MaxRAMPercentage=80 -jar build/libs/StoneDetector.jar -x --directory="$1" --error-file=$OUTPUT_TARGET    2>> $OUTPUT_TARGET
