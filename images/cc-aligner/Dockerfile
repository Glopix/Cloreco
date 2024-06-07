# CCAligner
# docker build . -t ghcr.io/glopix/cloreco-images/cc-aligner:latest

FROM ghcr.io/glopix/cloreco-images/detector-tool-base:ubuntu22.04-jdk17

ARG app=/cloneDetection/Applications/CCAligner/

# install dependencies
RUN apt-get update    && \
    apt-get install make g++ flex libboost-all-dev --no-install-recommends --yes


WORKDIR ${app}
# download CCAligner repo
RUN git clone https://github.com/PCWcn/CCAligner.git .

# install CCAligner
#cd txl    && \
#    make    && \
RUN cd lexical    && \
    make

RUN chmod +x detect detect2 extract parser tokenize co1

# copy runner script
ADD ./CCAlignerRunner.sh ${app}/CCAlignerRunner.sh
RUN chmod +x ${app}/CCAlignerRunner.sh
# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/CCAlignerRunner.sh

LABEL org.opencontainers.image.source https://github.com/Glopix/Cloreco-images
