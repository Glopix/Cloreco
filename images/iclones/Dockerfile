# iClones
# docker build . -t git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/iclones:latest --build-arg GITLAB_ACCESS_TOKEN=XXXXX

# Important:
# The domain on which iClones was provided (www.softwareclones.org) is no longer available.
# This means that the docker build process for iClones also fails, as an attempt is made to download packages from www.softwareclones.org before/during compilation. This fails and so does the build process.
# A Docker image with fully compiled iClones is still available.(git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/iClones:last-successfull-build) 
# However, changes to the base image (essentially entrypoint.py) must be made via this Dockerfile.

FROM git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/iclones:last-successfull-build

ENV LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8

ADD ./entrypoint.py /cloneDetection/entrypoint.py

WORKDIR /cloneDetection/BigCloneEval/commands/

# (re)initialize BigCloneEval
RUN ./init

# run detectClones and evaluateTool in script
ENTRYPOINT ["/usr/bin/python3", "/cloneDetection/entrypoint.py"]
