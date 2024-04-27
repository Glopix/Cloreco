#!/bin/bash
# based on runner (https://github.com/PCWcn/CCAligner/blob/master/runner)
# This script executes CCAligner with preparation steps

ulimit -s hard

# dir of the tool
MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

inputfolder="$1"

# Check if LOGGING_VERBOSE env var is set and not empty
if [[ -n "$LOGGING_VERBOSE" ]]; then
  OUTPUT_TARGET="$LOGGING_VERBOSE"
else
  # if it is not set, redirects both stdout and stderr of all commands to /dev/null
  OUTPUT_TARGET="/dev/null"
fi

# get arguments/settings for 'detect' and 'tokenize' commands from config file
source config.cfg

# ensure inputfolder has (only) one trailing Slash
inputfolder="$(readlink -m ${inputfolder})/"

rm -rf input/*
rm -rf output/*
# due to large num of files, 'rm -rf token/*' doesn't work
cd token
find ./ -type f -delete     &>> $OUTPUT_TARGET
cd ..
rm function.file            &>> $OUTPUT_TARGET
rm tokenline_num            &>> $OUTPUT_TARGET
rm clones                   &>> $OUTPUT_TARGET
# compile
cd txl
chmod +x *.x

cd ..
cd lexical
make clean                  &>> $OUTPUT_TARGET
make                        &>> $OUTPUT_TARGET
cd ..


# start timing
#date

####################
#! parser functions:
####################
#./extract 'txl' 'language' 'functions' 'source code'       'output' 'thread num'
./extract ./txl     java    functions   "${inputfolder}"    ./input   "${thread_num}"     &>> $OUTPUT_TARGET      || exit 1
#if c: ./extract ./txl c .. ; if c#:./extract ./txl cs ..

./parser ./input ./ 5                       &>> $OUTPUT_TARGET        || exit 1

####################
# tokenize: 
####################
# ./tokenize    'function.file' 'token' 'output' 'thread num'
./tokenize      ./function.file ./token  ./      "${thread_num}"                          &>> $OUTPUT_TARGET      || exit 1

####################
# detect
####################
#./detect 'token files' 'Output' 'function_frag.file' 'window size of token'    'edit-dist'     'similarity'
./detect ./token        ./output ./function.file      "${window_size_of_token}" "${edit_dist}" "${similarity}"  &>> $OUTPUT_TARGET    || exit 1
# or using filter-version by following (more faster):
#./detect2 ./token      ./output ./function.file      "${window_size_of_token}" "${edit_dist}" "${similarity}"  &>> $OUTPUT_TARGET

./co1       ./output    ./                                &>> $OUTPUT_TARGET      || exit 1

####################
# print output files and format output to fit BigCloneEval
####################
cat ./output/*    | \
    # remove 'inputfolder' string
    # e.g. /tmp/DetectClones988752979529351364/9_partition/0-9/selected/2331912.java -> /selected/2331912.java
    sed "s#${inputfolder}##g"   | \
    # remove leading Slash at the beginning/from left file path
    sed "s#^/##"   | \
    # remove leading Slash from second/right file path
    # e.g. selected,1475438.java,409,424,/selected/2647699.java,366,380 -> selected,1475438.java,409,424,selected/2647699.java,366,380
    sed "s#,/#,#"   | \
    # replace remaining Slashes with comma
    sed "s#/#,#g"

# end timing
#date
