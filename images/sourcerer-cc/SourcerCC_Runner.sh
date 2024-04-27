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
outputfolder="tokenizers/block-level/"${foldername} 

python3 adjustInput/main.py ${inputfolder} ${outputfolder}  || exit 1
echo "${foldername}"        > "tokenizers/block-level/list.txt"

cd "${MAIN_DIR}/tokenizers/block-level/"
rm -r "logs"                        &>> $OUTPUT_TARGET
rm -r "blocks_tokens"               &>> $OUTPUT_TARGET
rm -r "bookkeeping_projs"           &>> $OUTPUT_TARGET
rm -r "file_block_stats"            &>> $OUTPUT_TARGET
python3 tokenizer.py folderblocks   &>> $OUTPUT_TARGET    || exit 1

cat blocks_tokens/* > blocks.file
cp blocks.file "${MAIN_DIR}/clone-detector/input/dataset/"

cd "${MAIN_DIR}/clone-detector/"
./cleanup.sh 1                      &>> $OUTPUT_TARGET
python3 controller.py 1             &>> $OUTPUT_TARGET    || exit 1

# output clone pairs to detectClones 
cd "${MAIN_DIR}/bcboutput/"
python3 main.py                     2> $OUTPUT_TARGET     || exit 1

cd "${MAIN_DIR}"
rm -r "tokenizers/block-level/logs"                 &>> $OUTPUT_TARGET
rm -r "tokenizers/block-level/blocks_tokens"        &>> $OUTPUT_TARGET
rm -r "tokenizers/block-level/bookkeeping_projs"    &>> $OUTPUT_TARGET
rm -r "tokenizers/block-level/file_block_stats"     &>> $OUTPUT_TARGET
rm -r "tokenizers/block-level/${foldername}/"       &>> $OUTPUT_TARGET

