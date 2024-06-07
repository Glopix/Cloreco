Files in this folder were made to create a docker image of iClones.
However, the domain on which iClones was provided (www.softwareclones.org) is no longer available.
This means that the docker build process for iClones also fails, as an attempt is made to download packages from www.softwareclones.org before/during compilation. This fails and so does the build process.
A Docker image with fully compiled iClones is still available. (ghcr.io/glopix/cloreco-images/iClones:last-successfull-build)
However, changes to the base image (essentially entrypoint.py) must be made manually with a different Dockerfile.
