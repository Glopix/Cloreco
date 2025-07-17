# BigCloneEval base image
# docker build . -t ghcr.io/glopix/cloreco-images/big-clone-eval-base

ARG DISTRO=ubuntu:22.04

##############################################################
# first stage
FROM ${DISTRO} AS build
# install build dependencies
RUN apt-get update    && \
    apt-get install make openjdk-8-jdk git --no-install-recommends --yes

WORKDIR /cloneDetection/

RUN git clone https://github.com/jeffsvajlenko/BigCloneEval

# if these links are expired, you need to update them based on these https://github.com/jeffsvajlenko/BigCloneEval#step-2-get-the-latest-version-of-bigclonebench
# download bigclonebenchdb
ADD https://my.microsoftpersonalcontent.com/personal/8bfcb70aa333db15/_layouts/15/download.aspx?UniqueId=a333db15-b70a-20fc-808b-f0f903000000&Translate=false&tempauth=v1e.eyJzaXRlaWQiOiJkYzVkMGMxNy01MjQ1LTQ0YTEtODUzNS1iOTlkZTk4NGFhYzciLCJhdWQiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAvbXkubWljcm9zb2Z0cGVyc29uYWxjb250ZW50LmNvbUA5MTg4MDQwZC02YzY3LTRjNWItYjExMi0zNmEzMDRiNjZkYWQiLCJleHAiOiIxNzUyMTY4MzE5In0.F2A_yaeAkOqXHSRGnkgYIi_bzkvFkacAtvbglQjgeltOCQDNWBPGWzGuMhRfLdXGIWKEmAxlyXTZblTPhF5BK903VFEowhB39NBvWgEjQHOLeVY2536Jtw1ao5C00GFmggzPjwe_sB-wkRnjfCAIwu4_bPQBvk3cmvfhcW-rDH-gZyocB1yRrQHyW4q9lpDwB4f4V-wFA9SNWZmnJEdxJiZmB_8HMBxE-9jTGP2N7vFXx0WcbXghGzk3H8xfnRVD20M-Q5zUPnPqX5OgAZ1PaNSZjsW6YhqoX3SDLEEBiGTOfoY4uVEsp_T_-fN2RQGzfTZdjGNyBwRtRT_TXiKAMnzUOYT4NtS2oMxa1YzHcbREpZkYtiQWWqQucuEubcb9SkJxs_2xAadi-dt9pZuIiNXESAlAif4fN2abz5VNiUySBSJsSKPIwgE-CkSgMCwZ1pNOVWOhS6Mr32s-mAXXKNUEC5jMGawagqWd8zEH0yg44TZxw6IXxA0YuEe_7L2lk1moZarHkpZP5SBXWOZJhA.0Qe2F3wngdyKnJdKjQmufttjyejjOA6Ing3oT-Bs2Es&ApiVersion=2.0 BigCloneBench_BCEvalVersion.tar.gz
#COPY BigCloneBench_BCEvalVersion.tar.gz ./
RUN tar -xf BigCloneBench_BCEvalVersion.tar.gz -C /cloneDetection/BigCloneEval/bigclonebenchdb    && \
    rm BigCloneBench_BCEvalVersion.tar.gz

# download ijadataset
ADD https://my.microsoftpersonalcontent.com/personal/8bfcb70aa333db15/_layouts/15/download.aspx?UniqueId=a333db15-b70a-20fc-808b-f5f903000000&Translate=false&tempauth=v1e.eyJzaXRlaWQiOiJkYzVkMGMxNy01MjQ1LTQ0YTEtODUzNS1iOTlkZTk4NGFhYzciLCJhdWQiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAvbXkubWljcm9zb2Z0cGVyc29uYWxjb250ZW50LmNvbUA5MTg4MDQwZC02YzY3LTRjNWItYjExMi0zNmEzMDRiNjZkYWQiLCJleHAiOiIxNzUyMTY4MzQ4In0.0Q0NdLDfWQHXbokF3TkSNUeoaI2ZMLEC6sUv3KuTbcZDrlhuXFsdmqaYpFb57URaAeCutv1y54QVweHSBn56_5IhoIuEyRmIALxEPF838WmbfkY8Tguktf7HDOu1xteeeR6FV2dCnRnjK6bS1hy3pATEeJM58Y6NskHlF6rkJ_nLPe8CaDM9kL5jTTvPsCxacd42uujVp0jQU_SQKfgCenPYD7lGOFAH5lv1ODwW7oHW6MCrFOnIhnQL0030It-XKYcYeSOoS5-zAV49SnJpBhzGfAo-WmbJPApjNiJLJM0wOaay5RVRUqpWbrkM-gij9ylPfXhWpP_tMLOIcqWIIxdQC7WsHieNSArY8aevyD4nCn4H-HhWxX_ZtVMzelpPJIn1dw3BmhWRM7MLH9udO0yJUWuqkbwY-H8BduwJslh1O4_zrH-58rrGTI5ULI9odQT1MKA06jUx2gQJoc0OJJDGCgUZmY8I-lPn9Me3LZAhIJhKF0txpUsznNEixgCXzGHRjH2jrYsRhk7jCUzdwQ.UIdX9peZeDn4FPfb77YKT29UVPfO_6hRsn2ELSnslq0&ApiVersion=2.0 IJaDataset_BCEvalVersion.tar.gz
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

