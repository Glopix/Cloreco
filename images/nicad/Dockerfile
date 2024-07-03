# NiCad
# docker build . -t ghcr.io/glopix/cloreco-images/ni-cad:latest

FROM ghcr.io/glopix/cloreco-images/detector-tool-base:latest

ARG app=/cloneDetection/Applications/NiCad/

# install dependencies
RUN apt-get update    && \
    apt-get install make gcc glibc-source gcc-multilib --no-install-recommends --yes

# download Txl compiler / interpreter
ADD https://www.txl.ca/download/5150-txl10.8b.linux64.tar.gz /tmp/
RUN mkdir -p /tmp/txl    && \
    tar -xf /tmp/5150-txl10.8b.linux64.tar.gz -C /tmp/txl/ --strip-components 1    && \
    rm /tmp/5150-txl10.8b.linux64.tar.gz    && \
    cd /tmp/txl/    && \
# install Txl compiler / interpreter    
    ./InstallTxl    && \
    rm -rf /tmp/txl/

# install NiCad
WORKDIR ${app}
ADD https://www.txl.ca/download/323-NiCad-6.2.tar.gz ${app}
RUN tar -xf 323-NiCad-6.2.tar.gz --strip-components 1    && \
    rm 323-NiCad-6.2.tar.gz    && \
    make

# copy runner script
ADD ./nicadRunner.sh ${app}/nicadRunner.sh
RUN chmod +x ${app}/nicadRunner.sh
# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/nicadRunner.sh

LABEL org.opencontainers.image.source=https://github.com/Glopix/Cloreco-images
