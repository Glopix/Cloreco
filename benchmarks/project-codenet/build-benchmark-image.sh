#!/usr/bin/env bash

# download and setup the benchmark dataset files outside of the docker build process,
# so a minimal base image (busybox) can be used to store them in a docker image

# dir of the script
MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

# download dataset
wget -N https://dax-cdn.cdn.appdomain.cloud/dax-project-codenet/1.0.0/Project_CodeNet_Java250.tar.gz

rm -rf ./input/

mkdir -p ./input/
tar -C ./input/ --strip-components 1 -xf Project_CodeNet_Java250.tar.gz Project_CodeNet_Java250

# Execute rm commands only if "nocleanup" argument is specified
if [[ "$1" != "nocleanup" ]]; then
    rm -f ./*.tar.gz
fi

echo "adjusting files"
find ./input/ -type f -exec chmod 664 {} \;
./prepare/adjust_files.py ./input/

echo "sorting directories"
./prepare/sort_directories.py --input-directory ./input/

IMAGE_NAME="ghcr.io/glopix/cloreco-images/project-codenet-benchmark:latest"

docker build . -t "$IMAGE_NAME"
docker push "$IMAGE_NAME"

if [[ "$1" != "nocleanup" ]]; then
    rm -rf ./input
fi

