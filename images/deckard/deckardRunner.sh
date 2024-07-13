#!/bin/bash

ulimit -s hard

MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

inputfolder="$1"
foldername="${1##*/}"

# Check if LOGGING_VERBOSE env var is set and not empty
if [[ -n "$LOGGING_VERBOSE" ]]; then
  OUTPUT_TARGET="$LOGGING_VERBOSE"
else
  # if it is not set, redirects both stdout and stderr of all commands to /dev/null
  OUTPUT_TARGET="/dev/null"
fi

export LC_NUMERIC="en_US.UTF-8"

# clean up
rm -rf clusters/          &>> $OUTPUT_TARGET
rm -rf times/             &>> $OUTPUT_TARGET
rm -rf vectors/           &>> $OUTPUT_TARGET

cp -r "${inputfolder}" "src/examples/${foldername}"

./scripts/clonedetect/deckard.sh    &>> $OUTPUT_TARGET    || exit 1

cd bcboutput
python3 main.py     2>> $OUTPUT_TARGET    || exit 1

# clean up
cd ..
rm -rf clusters/                      &>> $OUTPUT_TARGET
rm -rf "src/examples/${foldername}"   &>> $OUTPUT_TARGET
rm -rf times/                         &>> $OUTPUT_TARGET
rm -rf vectors/                       &>> $OUTPUT_TARGET
