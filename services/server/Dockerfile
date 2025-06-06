# Copyright (c) Bioinformatics Core Facility of the Max Planck Institute for Biology of Ageing.
# Distributed under the terms of the Modified BSD License.

# Debian buster-slim (10.1)
FROM python:3.10-slim-bullseye

LABEL maintainer "bioinformatics@age.mpg.de"

USER root

ENV DEBIAN_FRONTEND noninteractive

RUN echo "deb http://ftp.debian.org/debian bullseye main non-free contrib" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian bullseye main non-free contrib" >> /etc/apt/sources.list && \
echo "deb http://ftp.debian.org/debian bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian bullseye-updates main contrib non-free" >> /etc/apt/sources.list 

# apt-get -o Acquire::Check-Valid-Until=false update
RUN apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq --no-install-recommends locales && \
apt-get clean && rm -rf /var/lib/apt/lists/* && \
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

ENV TZ="Europe/Berlin"

ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# -o Acquire::Check-Valid-Until=false 
RUN apt-get update && \
apt-get install -yq build-essential libcairo2-dev pkg-config mariadb-client cron rsync && \
apt-get clean && rm -rf /var/lib/apt/lists/*

ARG BUILD_NAME
ENV BUILD_NAME ${BUILD_NAME}

# Add myapp user for running the service
RUN groupadd ${BUILD_NAME} --gid=17600 && useradd -m ${BUILD_NAME} --uid=60564 --gid=17600 && echo "${BUILD_NAME}:4.iMkMm4zFoNViof" | \
    chpasswd && passwd -d ${BUILD_NAME}

# flaski2 compatible
# RUN useradd -m flaski --uid=1001 --gid=1000 && echo "flaski:4.iMkMm4zFoNViof" | \
#     chpasswd

# data folders and access rights
RUN mkdir -p /var/log/${BUILD_NAME} /${BUILD_NAME}/.git /${BUILD_NAME}/data /${BUILD_NAME}/${BUILD_NAME} /${BUILD_NAME}/migrations /${BUILD_NAME}/utils /${BUILD_NAME}/services /${BUILD_NAME}_data/users /backup/users_data /backup/mariadb
RUN touch /mysql_backup.log && touch /rsync.log /owncloud.log

# comment during development
COPY requirements.txt /${BUILD_NAME}/requirements.txt
COPY utils/requirements.min.txt utils/getenv.sh /${BUILD_NAME}/utils/

ARG MYAPP_VERSION
ARG UPGRADE_REQS

ENV MYAPP_VERSION ${MYAPP_VERSION}
# ENV UPGRADE_REQS ${UPGRADE_REQS}

RUN pip install --upgrade pip 
RUN if test "${UPGRADE_REQS}" = "yes" ; then echo "${MYAPP_VERSION}  : requirements.min.txt" ; pip3 install -r /${BUILD_NAME}/utils/requirements.min.txt ; /${BUILD_NAME}/utils/getenv.sh ; fi
# RUN if test "${UPGRADE_REQS}" != "yes" ; then echo "${MYAPP_VERSION}  : requirements.txt" ; pip3 install --ignore-installed pyxdg==0.26 ; pip3 install -r /${BUILD_NAME}/requirements.txt ; fi
RUN if test "${UPGRADE_REQS}" != "yes" ; then echo "${MYAPP_VERSION}  : requirements.txt" ; pip3 install -r /${BUILD_NAME}/requirements.txt ; fi


COPY LICENSE.md README.md config.py myapp.py requirements.txt setup.py .flaskenv /${BUILD_NAME}/
COPY services /${BUILD_NAME}/services
COPY utils /${BUILD_NAME}/utils
COPY myapp /${BUILD_NAME}/myapp
COPY .git /${BUILD_NAME}/.git

RUN rm -rf /${BUILD_NAME}/migrations

RUN touch /${BUILD_NAME}/utils/.requirements.all.txt.tmp 
RUN touch /${BUILD_NAME}/utils/.requirements.all.txt
RUN chown -R ${BUILD_NAME}:${BUILD_NAME} /${BUILD_NAME}_data /${BUILD_NAME}_data/users /${BUILD_NAME} /var/log/${BUILD_NAME} /mysql_backup.log /rsync.log /owncloud.log
# RUN chmod o+w /mysql_backup.log /rsync.log /owncloud.log && chmod g+w /mysql_backup.log /rsync.log /owncloud.log

## TEMPORARY FLASKI2 compatible init and backup containers
RUN mkdir -p /submissions /flaski_private /mpcdf /backup/oc_data/ /oc_data/ /submissions_ftp
#/utils/requirements.all.txt /${BUILD_NAME}/utils/requirements.min.txt /${BUILD_NAME}/utils/.requirements.all.txt.tmp /${BUILD_NAME}/utils/requirements.all.txt
RUN chown -R ${BUILD_NAME}:${BUILD_NAME} /submissions /flaski_private /mpcdf /backup/oc_data/ /oc_data/ /submissions_ftp 
# /flaski_data /flaski_data/users 
# RUN chmod -R g+w /submissions /flaski_private /mpcdf /flaski_data /flaski_data/users /backup

# Setup default user, when enter docker container
USER ${BUILD_NAME}:${BUILD_NAME}
WORKDIR /${BUILD_NAME}


ENTRYPOINT /${BUILD_NAME}/services/server/entrypoint.sh
