#!/bin/bash

# dir of the tool
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

cleanup () {
    echo "start cleanup" &>> $OUTPUT_TARGET
    cd "${MAIN_DIR}"
    rm -f ./clone-detector/input/dataset/blocks.file
    rm -rf ./results/
    rm -rf ./clone-detector/input/
    rm -rf ./clone-detector/backup_output/
    rm -rf ./clone-detector/NODE_1/
    rm -rf ./python_scripts/*_metric_output/
    rm -rf ./python_scripts/out*
    rm -f ./python_scripts/metric.out  ./python_scripts/metric.err

    cd "${MAIN_DIR}/clone-detector/"
    ./cleanup.sh        &>> $OUTPUT_TARGET
    echo "finished cleanup" &>> $OUTPUT_TARGET
}

cleanup

cd "${MAIN_DIR}/python_scripts/"

# reduce processors parameter to 1, since otherwise the result (.csv) file grows to over 1GB
#NUM_PROCESSORS=$(getconf _NPROCESSORS_ONLN)
NUM_PROCESSORS=1

#2. Generate Input for Oreo
# Metrics calculator calculates metrics for the methods found in these Java files
#python3 metricCalculationWorkManager.py 1 d <absolute path to input dataset>
python3 metricCalculationWorkManager.py "$NUM_PROCESSORS" d "$inputfolder"      &>> $OUTPUT_TARGET      || exit 1

# check if error file is empty
if [ -s metric.err ]; then
    echo "ERROR: python_scripts/metric.err file is non empty"
    echo "python_scripts/metric.err:"
    cat ./python_scripts/metric.err >> $OUTPUT_TARGET
    exit 1
fi

# wait until "done!" line appears in metric.out file ( = metricCalculationWorkManager.py has finished)
tail -f metric.out | grep -q "done!"

#3. Setting Up Oreo
# In order to proceed to clone detection step, we need to place metrics file in the appropriate place for Oreo to use it
mkdir -p "${MAIN_DIR}/clone-detector/input/dataset/"
cat ./*_metric_output/mlcc_input.file >> "${MAIN_DIR}/clone-detector/input/dataset/blocks.file"  

#4. Running Oreo
cd "${MAIN_DIR}/clone-detector"

# run controller.py in background
python3 controller.py 1     &>> $OUTPUT_TARGET   &
PID_CONTROLLER=$!

cd "${MAIN_DIR}/python_scripts"
./runPredictor.sh           &>> $OUTPUT_TARGET     || exit 1

# wait until the prediction is finished and the files are available
until [ -d "${MAIN_DIR}/results/predictions/" ]; do 
    sleep 1
done

# wait for controller.py background to finish
wait $PID_CONTROLLER
CONTROLLER_STATUS=$?
# check the exit status of controller.py
if [ $CONTROLLER_STATUS -ne 0 ]; then
    echo "controller.py background process failed with status $STATUS."
    exit 1
fi

# print all found clones
cat "${MAIN_DIR}/results/predictions/"*

cleanup

