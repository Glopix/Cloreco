# StoneDetector
# https://github.com/StoneDetector/StoneDetector
# based on https://github.com/StoneDetector/StoneDetector/blob/main/Dockerfile
# docker build . -t ghcr.io/glopix/cloreco-images/stone-detector:latest

FROM gradle:6.3.0-jdk11 AS build

WORKDIR /home/gradle/src
RUN git clone https://github.com/StoneDetector/StoneDetector.git .

#COPY --chown=gradle:gradle . /home/gradle/src
RUN chown -R gradle:gradle ./

#WORKDIR /home/gradle/src
RUN rm -rf build
RUN gradle jar --no-daemon

#RUN git clone https://github.com/jeffsvajlenko/BigCloneEval
#RUN wget https://gitlab.com/t.heinze/bigcloneevaldata/-/raw/main/BigCloneBench_BCEvalVersion.tar.gz
#RUN wget https://gitlab.com/t.heinze/bigcloneevaldata/-/raw/main/IJaDataset_BCEvalVersion.tar.gz

#WORKDIR /home/gradle/src/BigCloneEval
#RUN cp src/util/Version.java.template src/util/Version.java
#RUN mkdir -p bin/
#RUN javac -d bin/ -cp src/:libs/* src/**/*.java


#FROM openjdk:11-jre-slim
FROM ghcr.io/glopix/cloreco-images/detector-tool-base:ubuntu22.04-jdk11

ARG app=/cloneDetection/Applications/StoneDetector/

WORKDIR ${app}
#COPY --from=build /home/gradle/src/BigCloneEval                                 ${app}/BigCloneEval
COPY --from=build /home/gradle/src/build/libs/*.jar                             ${app}/build/libs/StoneDetector.jar
COPY --from=build /home/gradle/src/test/Example.java                            ${app}/test/Example.java
COPY --from=build /home/gradle/src/test/Example.class                           ${app}/test/Example.class
COPY --from=build /home/gradle/src/config/default.properties                    ${app}/config/default.properties
COPY --from=build /home/gradle/src/config/Patterns/ConfigByteCodePatterns       ${app}/config/Patterns/ConfigByteCodePatterns
COPY --from=build /home/gradle/src/config/Patterns/ConfigRegisterCodePatterns   ${app}/config/Patterns/ConfigRegisterCodePatterns
COPY --from=build /home/gradle/src/config/Patterns/ConfigSourceCodePatterns     ${app}/config/Patterns/ConfigSourceCodePatterns
COPY --from=build /home/gradle/src/errors.txt                                   ${app}/errors.txt
COPY --from=build /home/gradle/src/README.md                                    ${app}/README.md
COPY --from=build /home/gradle/src/BCE_runner                                   ${app}/BCE_runner
COPY --from=build /home/gradle/src/run_benchmark.sh                             ${app}/run_benchmark.sh
COPY --from=build /home/gradle/src/run.sh                                       ${app}/run.sh
#COPY --from=build /home/gradle/src/BigCloneBench_BCEvalVersion.tar.gz           ${app}/BigCloneEval/bigclonebenchdb/BigCloneBench_BCEvalVersion.tar.gz
#COPY --from=build /home/gradle/src/IJaDataset_BCEvalVersion.tar.gz              ${app}/BigCloneEval/ijadataset/IJaDataset_BCEvalVersion.tar.gz

# override runner script from repo with custom runner script
ADD BCE_runner.sh ${app}/BCE_runner
RUN chmod +x ${app}/BCE_runner
# set environmental variable: path of runner script (used by entrypoint.py)
ENV RUNNER_SCRIPT_PATH=${app}/BCE_runner

LABEL org.opencontainers.image.source=https://github.com/Glopix/Cloreco-images
