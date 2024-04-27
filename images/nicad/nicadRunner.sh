#!/bin/bash

# This tool runner works with the myconfig.cfg nicad configuration file included
# You will need to modify the hard-coded installation below before running
# Test this out on one of the IJaDataset directories (such as 11/) to test and 
# see that clones are detected and output in the correct format for BigCloneEval
# as specified in the readme.

ulimit -s hard

root=`dirname $1`
dir=`basename $1`
path="${root}"/"${dir}"

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


# Execute NiCad, Suppress Output
./nicad6 functions java "${path}" myconfig  &>> $OUTPUT_TARGET    || exit 1

# Convert Detected Clones Into BigCloneEval Format
#java -jar Convert.jar ${path}_functions-blind-abstract-clones/${dir}_functions-blind-abstract-clones-0.30.xml 2> $OUTPUT_TARGET

cat "${path}"_*-clones/"${dir}"_*-clones-0.30.xml | \
    sed 's$<source file="$$g' | sed 's$" startline="$,$g' | sed 's$" endline="$,$g' | sed 's$" pcid=.*"></source>$$g' | \
    sed 's$<clone nlines=.*$$g' | sed 's$</clone>.*$$g' | sed 's$</clones>$$g' |sed 's$<clones>$$g' | \
    sed 's$<cloneinfo.*$$g' | sed 's$<systeminfo.*$$g' | sed 's$<runinfo.*$$g' | sed '/^$/d' | paste -d ',' - - | \
    sed "s#${path}/##g" | sed 's#/#,#g'

# Cleanup
rm -rf "${path}"_functions-blind-abstract-clones  &>> $OUTPUT_TARGET
rm "${path}"_functions-blind-abstract.xml         &>> $OUTPUT_TARGET
rm "${path}"_functions-clones*.log                &>> $OUTPUT_TARGET
rm "${path}"_functions-blind.xml                  &>> $OUTPUT_TARGET
rm "${path}"_functions.xml                        &>> $OUTPUT_TARGET
