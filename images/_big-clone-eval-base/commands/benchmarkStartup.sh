#!/usr/bin/env bash

# execute registerTool command with ENV var CLONE_DETECTOR_TOOL_NAME as tool name

MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

# check if the CLONE_DETECTOR_TOOL_NAME environment variable is not set or is empty
if [ -z "$CLONE_DETECTOR_TOOL_NAME" ]; then
    # If not set or empty
    CLONE_DETECTOR_TOOL_NAME="clone detector tool"
fi

./registerTool --name="${CLONE_DETECTOR_TOOL_NAME}" --description="${CLONE_DETECTOR_TOOL_NAME}"
