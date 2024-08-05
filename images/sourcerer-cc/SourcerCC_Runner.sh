#!/bin/bash

ulimit -s hard

# directory of SourcerCC (where this script is located )
MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

# Check if LOGGING_VERBOSE env var is set and not empty
if [[ -n "$LOGGING_VERBOSE" ]]; then
  OUTPUT_TARGET="$LOGGING_VERBOSE"
else
  # if it is not set, redirects both stdout and stderr of all commands to /dev/null
  OUTPUT_TARGET="/dev/null"
fi

inputfolder="$1"
foldername="${1##*/}"
sourcererCC_Input="${MAIN_DIR}/tokenizers/block-level/"${foldername}

function cleanup {
  rm -r "${MAIN_DIR}/tokenizers/block-level/logs"                 &>> $OUTPUT_TARGET
  rm -r "${MAIN_DIR}/tokenizers/block-level/blocks_tokens"        &>> $OUTPUT_TARGET
  rm -r "${MAIN_DIR}/tokenizers/block-level/bookkeeping_projs"    &>> $OUTPUT_TARGET
  rm -r "${MAIN_DIR}/tokenizers/block-level/file_block_stats"     &>> $OUTPUT_TARGET
  rm -r "${MAIN_DIR}/tokenizers/block-level/list.txt"             &>> $OUTPUT_TARGET
}

cleanup

# link the benchmark dataset input to the sourcererCC input directory
ln -s $inputfolder $sourcererCC_Input

cd "${MAIN_DIR}/tokenizers/block-level/"
find "$foldername/" -type d    > "${MAIN_DIR}/tokenizers/block-level/list.txt"

python3 tokenizer.py folderblocks   &>> $OUTPUT_TARGET    || exit 1

cat blocks_tokens/* > blocks.file
cp blocks.file "${MAIN_DIR}/clone-detector/input/dataset/"

cd "${MAIN_DIR}/clone-detector/"
./cleanup.sh 1                      &>> $OUTPUT_TARGET
python3 controller.py 1             &>> $OUTPUT_TARGET    || exit 1

# output clone pairs to detectClones 
python3 "${MAIN_DIR}/bcboutput/main.py"   2> $OUTPUT_TARGET     || exit 1

cleanup
rm    "${MAIN_DIR}/tokenizers/block-level/${foldername}"       &>> $OUTPUT_TARGET

