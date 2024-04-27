# generic Dockerfile
# used to build images from a script (from a git repository)

ARG BASE_IMAGE=git.uni-jena.de:5050/pi65gop/klondetektoren-automatisierung/detector-tool-base
ARG DISTRO
ARG JDK_VERSION

FROM ${BASE_IMAGE}:${DISTRO}-${JDK_VERSION}

ARG INSTALL_DIR
ARG GIT_REPO
ARG TOOL_NAME
ARG RUNNER_SCRIPT_PATH
# print arguments for debugging purposes
RUN echo -e "\nINSTALL_DIR=${INSTALL_DIR} \nGIT_REPO=${GIT_REPO} \nTOOL_NAME=${TOOL_NAME} \nRUNNER_SCRIPT_PATH=${RUNNER_SCRIPT_PATH}"

WORKDIR ${INSTALL_DIR}

# download git repo into this image
RUN git clone ${GIT_REPO} .

# install dependencies and the tool
RUN bash -c '(set -e; source ./install.sh)'

# set execution bit for all .sh scripts
RUN chmod +x ./*.sh

# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${RUNNER_SCRIPT_PATH}

