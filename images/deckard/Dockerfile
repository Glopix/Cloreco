# Deckard
# https://github.com/skyhover/Deckard
# docker build . -t git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/deckard:latest

FROM git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/detector-tool-base:ubuntu18.04-jdk8

ARG app=/cloneDetection/Applications/Deckard/

# install dependencies
RUN apt-get update    && \
    apt-get install make python2.7 bison flex g++ language-pack-en --no-install-recommends --yes

# set /usr/bin/python2.7 as alias for python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python2.7 20

# download Deckard repo and build Deckard
WORKDIR ${app}
RUN git clone https://github.com/skyhover/Deckard .    && \
    cd ${app}/src/main/    && \
    ./build.sh             && \
    \
    cd ${app}              && \
    rm -rf ./.git*

# copy helper scripts
ADD ./bcboutput ${app}/bcboutput/

# copy runner script
ADD ./deckardRunner.sh ${app}/deckardRunner.sh
RUN chmod +x ${app}/deckardRunner.sh
# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/deckardRunner.sh

LABEL org.opencontainers.image.source https://github.com/Glopix/Cloreco-images
