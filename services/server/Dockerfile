# Copyright (c) Bioinformatics Core Facility of the Max Planck Institute for Biology of Ageing.
# Distributed under the terms of the Modified BSD License.

# Debian buster-slim (10.1)
# FROM debian@sha256:11253793361a12861562d1d7b15b8b7e25ac30dd631e3d206ed1ca969bf97b7d
FROM debian:buster-slim

LABEL maintainer "bioinformatics@age.mpg.de"

# ARG TARGETPLATFORM

USER root

ENV DEBIAN_FRONTEND noninteractive

RUN echo "deb http://ftp.debian.org/debian buster main non-free contrib" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian buster main non-free contrib" >> /etc/apt/sources.list && \
echo "deb http://ftp.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list 

RUN apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq --no-install-recommends locales && \
apt-get clean && rm -rf /var/lib/apt/lists/* && \
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq python3 python3-pip libcairo2-dev pkg-config python3-dev mariadb-client cron rsync sudo && \
apt-get clean && rm -rf /var/lib/apt/lists/*

# plotly saving of images to file
RUN apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq wget libgtk-3-0 libxtst-dev libxss-dev libgconf2-dev libnss3 libasound2-dev xvfb && \
apt-get clean && rm -rf /var/lib/apt/lists/*

# # plotly saving of images to file
# RUN apt-get update && apt-get -yq dist-upgrade && \
# apt-get install -yq wget libgtk-3-0 libxtst-dev libxss-dev libgconf2-dev libnss3 libasound2-dev xvfb && \
# wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh  -b -p /miniconda && \
# /miniconda/bin/conda install -c plotly plotly-orca psutil requests && \
# apt-get clean && rm -rf /var/lib/apt/lists/*

ARG BUILD_NAME
ENV BUILD_NAME ${BUILD_NAME}

# Add cycshare user for running the service
RUN groupadd ${BUILD_NAME} --gid=1000 && useradd -m ${BUILD_NAME} --uid=1000 --gid=1000 && echo "${BUILD_NAME}:4.iMkMm4zFoNViof" | \
    chpasswd

# data folders and access rights
RUN mkdir -p /var/log/${BUILD_NAME} /${BUILD_NAME}/.git /${BUILD_NAME}/data /${BUILD_NAME}/${BUILD_NAME} /${BUILD_NAME}/migrations /${BUILD_NAME}/utils /${BUILD_NAME}/services /${BUILD_NAME}_data/users /backup/users_data /backup/mariadb
RUN touch /mysql_backup.log && touch /rsync.log
RUN chown -R ${BUILD_NAME}:${BUILD_NAME} /${BUILD_NAME}_data /${BUILD_NAME}_data/users /${BUILD_NAME}/migrations /var/log/${BUILD_NAME} /mysql_backup.log /rsync.log

# comment during development
COPY requirements.txt /${BUILD_NAME}/requirements.txt

RUN pip3 install Cython
RUN pip3 install -r /${BUILD_NAME}/requirements.txt

COPY LICENSE.md README.md config.py ${BUILD_NAME}.py requirements.txt setup.py .flaskenv /${BUILD_NAME}/
COPY services /${BUILD_NAME}/services
COPY ${BUILD_NAME} /${BUILD_NAME}/${BUILD_NAME}
COPY .git /${BUILD_NAME}/.git

# Setup default user, when enter docker container
USER ${BUILD_NAME}:${BUILD_NAME}
WORKDIR /${BUILD_NAME}

ENTRYPOINT /${BUILD_NAME}/services/server/docker-entrypoint.sh