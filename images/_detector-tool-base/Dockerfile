# base image for detector tools
# docker build . -t ghcr.io/glopix/cloreco-images/big-clone-eval:<version> --build-arg DISTRO=<distro> --build-arg JDK_VERSION=<JDK version>
# e.g. docker build . -t ghcr.io/glopix/cloreco-images/big-clone-eval:ubuntu22.04-jdk8 --build-arg DISTRO=ubuntu:latest --build-arg JDK_VERSION=openjdk-8-jdk

ARG DISTRO=ubuntu:latest

FROM ${DISTRO}
ARG JDK_VERSION=openjdk-11-jdk

ENV LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /cloneDetection/

# for test and debugging purposes, could be removed to reduce image size
#COPY --from=ghcr.io/glopix/cloreco-images/big-clone-eval-base /cloneDetection /cloneDetection

# install dependencies
RUN apt-get update    && \
    apt-get install ${JDK_VERSION} git python3 --no-install-recommends --yes && \
    rm -rf /var/lib/apt/lists/*

# prepare report directory
RUN mkdir -p /cloneDetection/reports/

ADD ./entrypoint.py /cloneDetection/entrypoint.py
RUN chmod +x /cloneDetection/entrypoint.py

ENTRYPOINT ["/usr/bin/python3", "/cloneDetection/entrypoint.py"]
