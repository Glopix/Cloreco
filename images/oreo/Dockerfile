# Oreo
# https://github.com/Mondego/oreo
# https://github.com/Mondego/oreo-artifact/blob/master/INSTALL.md
# docker build . -t ghcr.io/glopix/cloreco-images/oreo:latest

# use Ubuntu 18.04 as base, since it provides python3.6 for Oreo
FROM ghcr.io/glopix/cloreco-images/detector-tool-base:ubuntu18.04-jdk8

ARG app=/cloneDetection/Applications/Oreo/
WORKDIR ${app}

# install dependencies
RUN apt-get update    && \
    apt-get install python3.6 python3.6-distutils python3-pip python3-setuptools python3-wheel ant gcc --no-install-recommends --yes

# set /usr/bin/python3.6 as alias for python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10

# download Oreo repo and use only the oreo folder
RUN git clone https://github.com/Mondego/oreo-artifact /tmp/Oreo-tmp    && \
    mv /tmp/Oreo-tmp/oreo/*     ${app}    && \
    rm -rf /tmp/Oreo-tmp

# install Python dependencies
RUN pip3 install -r ${app}/python_scripts/dependencies/dependencies.txt

WORKDIR ${app}/java-parser/
RUN ant metric

WORKDIR ${app}

# fix error in old pandas import
RUN sed -i "1s/^/import os\nos.environ.setdefault('PATH', '')\n/" ${app}/python_scripts/Predictor.py

# copy customized runnodes.sh script
ADD ./clone-detector/runnodes.sh ./clone-detector/runnodes.sh

# copy runner script
ADD ./oreoRunner.sh ${app}/oreoRunner.sh
RUN chmod +x ${app}/oreoRunner.sh
# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/oreoRunner.sh

LABEL org.opencontainers.image.source=https://github.com/Glopix/Cloreco-images
