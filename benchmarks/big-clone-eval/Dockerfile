# base image for detector tools
# docker build . -t ghcr.io/glopix/cloreco-images/big-clone-eval-benchmark --build-arg DISTRO=<distro> 
# e.g. docker build . -t ghcr.io/glopix/cloreco-images/big-clone-eval-benchmark --build-arg DISTRO=ubuntu:latest

ARG DISTRO=ubuntu:latest

##############################################################
# second stage
FROM ${DISTRO}

ENV LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /cloneDetection/
COPY --from=ghcr.io/glopix/cloreco-images/big-clone-eval-base /cloneDetection /cloneDetection

ENTRYPOINT ["/usr/bin/sleep", "1"]

LABEL org.opencontainers.image.source=https://github.com/Glopix/Cloreco-images
