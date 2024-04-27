# iClones
# docker build . -t git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/iclones:latest --build-arg GITLAB_ACCESS_TOKEN=XXXXX

FROM git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/big-clone-eval:ubuntu22.04-jdk11

ARG app=/cloneDetection/Applications/iClones/
ARG GITLAB_ACCESS_TOKEN

# install dependencies
RUN apt-get update    && \
    apt-get install ruby maven --no-install-recommends --yes

# set /usr/bin/python3 as alias for python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

# download iClones repo
WORKDIR ${app}
RUN git clone https://oauth2:${GITLAB_ACCESS_TOKEN}@gitlab.com/andre.schaefer.jena/iclones_local.git .

# install iClones
RUN mvn install

# copy runner script
ADD ./iclones_Source_Runner.sh ${app}/iclones/iclones_Source_Runner.sh
RUN chmod +x ${app}/iclones/iclones_Source_Runner.sh
# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/iclones/iclones_Source_Runner.sh

WORKDIR /cloneDetection/BigCloneEval/commands/

# initialize BigCloneEval
RUN ./init

# register NiCad
RUN ./registerTool -d iClones -n iClones

# run detectClones and evaluateTool in script
ENTRYPOINT ["/cloneDetection/entrypoint.py"]