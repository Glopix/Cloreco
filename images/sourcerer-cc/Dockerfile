# SourcerCC
# https://github.com/Mondego/SourcererCC
# docker build . -t git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/sourcer-cc:latest

FROM git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/detector-tool-base:latest

ARG app=/cloneDetection/Applications/SourcerCC/

# install dependencies
RUN apt-get update    && \
    apt-get install python3-pip python-is-python3 ant --no-install-recommends --yes
RUN pip3 install javalang

# download SourcererCC repo
WORKDIR ${app}
RUN git clone https://github.com/Mondego/SourcererCC .    && \
    rm -rf ./WebApp/

# install SourcerCC
WORKDIR ${app}/clone-detector/
RUN ant cdi    && \
    ant cdmerge    && \ 
    java -Dproperties.location="sourcerer-cc.properties" -Xms4g -Xmx4g  -jar dist/indexbased.IndexMerger.jar merge

WORKDIR ${app}
# copy helper scripts
ADD ./adjustInput ./adjustInput/
ADD ./bcboutput ./bcboutput/

# copy tokenizers/block-level/config.ini
ADD ./tokenizers ./tokenizers

# copy runner script
ADD ./SourcerCC_Runner.sh ${app}/SourcerCC_Runner.sh
RUN chmod +x ${app}/SourcerCC_Runner.sh
# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/SourcerCC_Runner.sh

LABEL org.opencontainers.image.source https://github.com/Glopix/Cloreco-images
