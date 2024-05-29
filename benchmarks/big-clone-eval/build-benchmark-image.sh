#!/usr/bin/env bash

# dir of the script
MAIN_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd "${MAIN_DIR}"

IMAGE_NAME="ghcr.io/glopix/cloreco-images/big-clone-eval-benchmark:latest"

docker build . -t "$IMAGE_NAME"
docker push "$IMAGE_NAME"


