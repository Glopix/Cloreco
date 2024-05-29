#!/usr/bin/env bash

# download and setup the benchmark dataset files outside of the docker build process,
# so a minimal base image (busybox) can be used to store them in a docker image

# dir of the script
MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

# download/add as many google code jam versions as desired
wget -N https://zibada.guru/gcj/gcj-archive-2022.zip
#wget https://zibada.guru/gcj/gcj-archive-2021.zip
#wget https://zibada.guru/gcj/gcj-archive-2020.zip

mkdir -p ./input/
unzip '*.zip' -d ./input/

# Execute rm commands only if "nocleanup" argument is specified
if [[ "$1" != "nocleanup" ]]; then
    rm -f ./gcj-archive-*.zip
fi

./prepare/prepare-files.sh

IMAGE_NAME="ghcr.io/glopix/cloreco-images/google-code-jam-benchmark:latest"

docker build . -t "$IMAGE_NAME"
docker push "$IMAGE_NAME"

if [[ "$1" != "nocleanup" ]]; then
    rm -rf ./input
fi

