# base image for detector tools
# docker build . -t git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/big-clone-eval-benchmark --build-arg DISTRO=<distro> 
# e.g. docker build . -t git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/big-clone-eval-benchmark --build-arg DISTRO=ubuntu:latest

ARG DISTRO=ubuntu:latest

##############################################################
# second stage
FROM ${DISTRO}

ENV LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /cloneDetection/
COPY --from=ghcr.io/glopix/abcd-images/big-clone-eval-base /cloneDetection /cloneDetection

ENTRYPOINT ["/usr/bin/sleep", "1"]
