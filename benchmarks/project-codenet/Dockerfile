FROM busybox

WORKDIR /cloneDetection/benchmark/

ADD input/ ./input/
ADD commands/ ./commands/

RUN chmod +x ./commands/*

# short sleep, so all benchmark files can be copied to the volume and the container exits shortly after
ENTRYPOINT [ "/bin/sleep", "1" ]

LABEL org.opencontainers.image.source https://github.com/Glopix/Cloreco-images
