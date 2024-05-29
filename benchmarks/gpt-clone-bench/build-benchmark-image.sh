#!/usr/bin/env bash

# download and setup the benchmark dataset files outside of the docker build process,
# so a minimal base image (busybox) can be used to store them in a docker image

# dir of the script
MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

# download GPTCloneBench_semantic_standalone_clones.zip
wget -N https://raw.githubusercontent.com/srlabUsask/GPTCloneBench/main/GPTCloneBench_semantic_standalone_clones.zip

rm -rf ./input/*
mkdir -p ./input/
#unzip '*.zip' -d ./input/
#unzip 'gpt_cb.zip' -d ./input/
#mv ./input/standalone/* ./input/
#rm -rf ./input/standalone/

rm -rf standalone
mkdir -p ./input/fsc/  ./input/tsc_p1_MT3/  ./input/tsc_p1_T4/  ./input/tsc_p2_MT3/  ./input/tsc_p2_T4/
unzip GPTCloneBench_semantic_standalone_clones.zip

# flatten directory hierarchy
mv standalone/false_semantic_clones/java/*.java               input/fsc/
mv standalone/true_semantic_clones/java/prompt_1/MT3/*.java   input/tsc_p1_MT3/
mv standalone/true_semantic_clones/java/prompt_1/T4/*.java    input/tsc_p1_T4/
mv standalone/true_semantic_clones/java/prompt_2/MT3/*.java   input/tsc_p2_MT3/
mv standalone/true_semantic_clones/java/prompt_2/T4/*.java    input/tsc_p2_T4/

rm -rf standalone

# Execute rm commands only if "nocleanup" argument is specified
if [[ "$1" != "nocleanup" ]]; then
    rm -f ./GPTCloneBench_semantic_standalone_clones.zip.zip
fi

echo "add classes to files"
./prepare/addClasses.py --input ./input

echo "remove files with errors"
./prepare/remove_noncompilable.py --input ./input

echo "splitting input directories"
./prepare/split_directories.py --input ./input --divide-number 10

# delete all empty directories in the input directory
find ./input/ -type d -empty -delete

rm -f ./input/*.md ./input/*.txt

IMAGE_NAME="ghcr.io/glopix/cloreco-images/gpt-clone-bench-benchmark:latest"

docker build . -t "$IMAGE_NAME"
docker push "$IMAGE_NAME"

if [[ "$1" != "nocleanup" ]]; then
    rm -rf ./input
fi

