# NIL
# https://github.com/kusumotolab/NIL
# docker build . -t ghcr.io/glopix/cloreco-images/nil:latest
FROM ghcr.io/glopix/cloreco-images/detector-tool-base:ubuntu22.04-jdk21

ARG app=/cloneDetection/Applications/nil/

WORKDIR ${app}

RUN git clone https://github.com/kusumotolab/NIL .
RUN ./gradlew ShadowJar

# remove unnecessary files
RUN rm -rf ./*.md ./*.pdf

# add runer script
ADD runner.sh ${app}
RUN chmod +x ${app}/runner.sh

# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/runner.sh

LABEL org.opencontainers.image.source=https://github.com/Glopix/Cloreco-images
