# DrDup2
# https://github.com/tronicek/DrDup2
# docker build . -t ghcr.io/glopix/cloreco-images/dr-dup2:latest
FROM ghcr.io/glopix/cloreco-images/detector-tool-base:ubuntu22.04-jdk8

ARG app=/cloneDetection/Applications/drDup2/

WORKDIR ${app}

RUN git clone https://github.com/tronicek/DrDup2 . && \
# remove unnecessary files
    rm -rf ./*.md ./*.pdf .git* bigclonebench* evaluation config verification-* input

RUN apt-get update    && \
    apt-get install maven \
        --no-install-recommends --yes && \
    rm -rf /var/lib/apt/lists/*
RUN mvn clean compile assembly:single

# add runer script
ADD runner.sh ${app}
RUN chmod +x ${app}/runner.sh

ADD transform-output-xml-to-csv.py ${app}
RUN chmod +x ${app}/transform-output-xml-to-csv.py

# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/runner.sh

LABEL org.opencontainers.image.source=https://github.com/Glopix/Cloreco-images
