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

# if these links are invalid, you need to update them based on these https://github.com/jeffsvajlenko/BigCloneEval#step-2-get-the-latest-version-of-bigclonebench
# download bigclonebenchdb
ADD https://my.microsoftpersonalcontent.com/personal/8bfcb70aa333db15/_layouts/15/download.aspx?UniqueId=a333db15-b70a-20fc-808b-f0f903000000&Translate=false&tempauth=v1e.eyJzaXRlaWQiOiJkYzVkMGMxNy01MjQ1LTQ0YTEtODUzNS1iOTlkZTk4NGFhYzciLCJhdWQiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAvbXkubWljcm9zb2Z0cGVyc29uYWxjb250ZW50LmNvbUA5MTg4MDQwZC02YzY3LTRjNWItYjExMi0zNmEzMDRiNjZkYWQiLCJleHAiOiIxNzUyMTYzMjY3In0.NTj46n2oxFgejnG-4qPSKDAc6qU-bZcYti4RO9ESjnf8tGVCK7IAl9kd0GsT215wcj7JnsFxYJM4aSa5Oela7ClEi_6mjmPcOBfXpc92qj8o0armA8IJwtgt-PIJKA-D6EKHqKduL31REsEFtiqpo_eRxbMQNlZ-O1zrDtCM7EwCNlx0VmNdOQP6aoBeHqIyA6rjLBngne5sPbHmZTwr5_XhVsjyI7g44IpwXKp3edqUBZLfgHB9XBWKs-e--NjIwBEUcrv-oV0va7sa4KGlkkeAqswGy2Z2xCTYmuq1BLh9VvjN9Z7BELk85qx4Yfgm5HsuTDdXehn6ulWYP7QdN0sO4FTLOmc3iNeIojRSyBp1l8kgzx0pZ0qX5baW9EJZ9WkRBEKku1EuXCBvmLdCLrh1ObHIZM1wBZSTvPR3D9lkuE3ZOez05Oda9jIH8ZenkyLrjia7A46bzu6Zf8AqvZdrH2Qlj4QQ0mDNT1QTGFSEME3gzYksPPwKKlVaOsLM_uNBayZoWcNYbfLVTZeHWA.ESvhK_EGAIx-t9cSGwq3QIDCwHpS-kDbfxGPkBbz93M&ApiVersion=2.0 BigCloneBench_BCEvalVersion.tar.gz
#COPY BigCloneBench_BCEvalVersion.tar.gz ./
RUN tar -xf BigCloneBench_BCEvalVersion.tar.gz -C /cloneDetection/BigCloneEval/bigclonebenchdb    && \
    rm BigCloneBench_BCEvalVersion.tar.gz

# download ijadataset
ADD https://my.microsoftpersonalcontent.com/personal/8bfcb70aa333db15/_layouts/15/download.aspx?UniqueId=a333db15-b70a-20fc-808b-f5f903000000&Translate=false&tempauth=v1e.eyJzaXRlaWQiOiJkYzVkMGMxNy01MjQ1LTQ0YTEtODUzNS1iOTlkZTk4NGFhYzciLCJhdWQiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAvbXkubWljcm9zb2Z0cGVyc29uYWxjb250ZW50LmNvbUA5MTg4MDQwZC02YzY3LTRjNWItYjExMi0zNmEzMDRiNjZkYWQiLCJleHAiOiIxNzUyMTYzMzY3In0.WL8GjKwCLmMLA_5duL0lRDAgtsuGmyVsARC9yCarw9i7fLbQt5OA3Kgsxr_rRgJv3BIS1JE_58Z_5GsIXh_RgRC7GBtkz2BE-GX1yxlk37tk6biAd695WIvgTwLMXF1k-7EiQrFOIQgC3lzjDolxJXqgnX9um4a5WozWKNd6DcQqop4AtkRNCA9Ej4TS93_rAhxjHghUfIw1CfYyU78kKrdIHO48_g8IddhNG0DkRg0lAXWapb6ORE-LF4RbxZjk_uxduLfUfaEIwC7CxNival1NcK6ujDmnAMNdYt37hIgci8A1wXbsES1tWKYC1D3aVAqkX0utadau40LQcJMvO1cXr4JO3KS-d3UJQODgSU4D0P9hPT3f8Tl8lKFAIX7xXcp1Nb_drrqPf1G_w6ild97L81OhZJHuSM5DSEap2e1GnrFVb4NcL0EzpQ6oF9q4SeCRLBv-DdGHzasyjsplwY1fIzg8OjJ88_2W4Lha0PH2eInUPdsFqHNQl6MMmFJQ0Fmop4s2Jza12SQ8oyFwIg.do1fV9wgyoBcc26nofsGVsNCWBQdS4fjXnHPWIWTqtA&ApiVersion=2.0 IJaDataset_BCEvalVersion.tar.gz
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

