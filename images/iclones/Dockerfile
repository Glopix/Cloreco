# iClones
# docker build . -t ghcr.io/glopix/cloreco-images/iclones:latest

# Important:
# The domain on which iClones was provided (www.softwareclones.org) is no longer available.
# This means that the docker build process for iClones also fails, as an attempt is made to download packages from www.softwareclones.org before/during compilation. This fails and so does the build process.
# A Docker image with fully compiled iClones is still available.(ghcr.io/glopix/cloreco-images/iClones:last-successfull-build) 
# However, changes to the base image (essentially entrypoint.py) must be made via this Dockerfile.

FROM ghcr.io/glopix/cloreco-images/iclones:last-successfull-build

ARG app=/cloneDetection/Applications/iClones/

ENV LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8

ADD ./entrypoint.py /cloneDetection/entrypoint.py
# copy runner script
ADD ./iclones_Source_Runner.sh ${app}/iclones/iclones_Source_Runner.sh
RUN chmod +x ${app}/iclones/iclones_Source_Runner.sh

WORKDIR /cloneDetection/BigCloneEval/commands/

# (re)initialize BigCloneEval
RUN ./init

# run detectClones and evaluateTool in script
ENTRYPOINT ["/usr/bin/python3", "/cloneDetection/entrypoint.py"]

LABEL org.opencontainers.image.source=https://github.com/Glopix/Cloreco-images
