# BigCloneEval base image
# docker build . -t ghcr.io/glopix/cloreco-images/big-clone-eval-base

ARG DISTRO=ubuntu:22.04

##############################################################
# first stage
FROM ${DISTRO} as build
# install build dependencies
RUN apt-get update    && \
    apt-get install make openjdk-8-jdk git --no-install-recommends --yes

WORKDIR /cloneDetection/

RUN git clone https://github.com/jeffsvajlenko/BigCloneEval

# download bigclonebenchdb
ADD https://r5je2q.dm.files.1drv.com/y4mmgbYfYvpEq1KxOZvhR7Si4bXocKSse0d5iuMf-02tnGD34il8-Fx9KCHPWnRRIWOoYW5-qj8J3ou86ZUgMH_J2a5AYMYX9JrLPOFrW8BCZw5fPQGxq8xnEhHn2dvwWd2ndIhhenhWZCt4ewNkDMzZfhVxVYHLF9yPWmP-t9umjrzty9rcoIQ2NvfCZ1dFCSAVsCSB9CYTEnqZUTe0VoxAw BigCloneBench_BCEvalVersion.tar.gz
#COPY BigCloneBench_BCEvalVersion.tar.gz ./
RUN tar -xf BigCloneBench_BCEvalVersion.tar.gz -C /cloneDetection/BigCloneEval/bigclonebenchdb    && \
    rm BigCloneBench_BCEvalVersion.tar.gz

# download ijadataset
ADD https://qffqra.dm.files.1drv.com/y4mzcsXh-6hPIevr3IXNuSGhO2_ADTD9j0eRdlDbiJrcDI_2WjR6DvphGJyNecskWdbToMwEq4Pgic6I49VBdidExbqVkhE6kjvej378YOUvxJLDx5fJVHYOl34ZZHV4clx9nOSNu-XYp_Rgk__oxHRZU8lUaTaaFNEqYI7miBymv51JsS4PtcGKhtKB84ujC26filEDJ5Vm4MyUDfS-9rv2Q IJaDataset_BCEvalVersion.tar.gz
#COPY IJaDataset_BCEvalVersion.tar.gz    ./
RUN tar -xf IJaDataset_BCEvalVersion.tar.gz -C /cloneDetection/BigCloneEval/ijadataset    && \
    rm IJaDataset_BCEvalVersion.tar.gz

# install BigCloneEval
WORKDIR /cloneDetection/BigCloneEval/
RUN make

# initialize BigCloneEval
WORKDIR /cloneDetection/BigCloneEval/commands/
RUN ./init

# rename original detectClones
RUN mv /cloneDetection/BigCloneEval/commands/detectClones /cloneDetection/BigCloneEval/commands/detectClones_bce
# add custom detectClones wrapper script and placed it in the same location as the original script
ADD ./commands/detectClonesWrapper.py /cloneDetection/BigCloneEval/commands/detectClones

ADD ./commands/benchmarkStartup.sh /cloneDetection/BigCloneEval/commands/benchmarkStartup.sh

RUN chmod +x /cloneDetection/BigCloneEval/commands/*

##############################################################
# second stage
FROM ${DISTRO}
WORKDIR /cloneDetection/BigCloneEval/

COPY --from=build /cloneDetection/BigCloneEval/commands/         /cloneDetection/BigCloneEval/commands/
COPY --from=build /cloneDetection/BigCloneEval/bigclonebenchdb/  /cloneDetection/BigCloneEval/bigclonebenchdb//
COPY --from=build /cloneDetection/BigCloneEval/bin/              /cloneDetection/BigCloneEval/bin/
COPY --from=build /cloneDetection/BigCloneEval/ijadataset/       /cloneDetection/BigCloneEval/ijadataset/
COPY --from=build /cloneDetection/BigCloneEval/libs/             /cloneDetection/BigCloneEval/libs/
COPY --from=build /cloneDetection/BigCloneEval/toolsdb/          /cloneDetection/BigCloneEval/toolsdb/

