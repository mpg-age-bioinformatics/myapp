# Copyright (c) Bioinformatics Core Facility of the Max Planck Institute for Biology of Ageing.
# Distributed under the terms of the Modified BSD License.

# Debian buster-slim (10.1)
FROM debian@sha256:11253793361a12861562d1d7b15b8b7e25ac30dd631e3d206ed1ca969bf97b7d

LABEL maintainer "bioinformatics@age.mpg.de"

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
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh  -b -p /miniconda && \
/miniconda/bin/conda install -c plotly plotly-orca psutil requests && \
apt-get clean && rm -rf /var/lib/apt/lists/*

# Add cycshare user for running the service
RUN groupadd cycshare --gid=1000 && useradd -m cycshare --uid=1000 --gid=1000 && echo "cycshare:4.iMkMm4zFoNViof" | \
    chpasswd

RUN mkdir /submissions
RUN chown -R cycshare:cycshare /submissions

# remove old cycshare files
RUN rm -rf /cycshare

# data folders and access rights
RUN mkdir -p /var/log/cycshare /cycshare/.git /cycshare/data /cycshare/cycshare /cycshare/migrations /cycshare/utils /cycshare/services /cycshare/pycycshare /cycshare_data/users /backup/users_data /backup/mariadb
RUN touch /mysql_backup.log && touch /rsync.log
RUN chown -R cycshare:cycshare /cycshare_data /cycshare_data/users /cycshare/migrations /var/log/cycshare /mysql_backup.log /rsync.log

# comment during development
COPY requirements.txt /cycshare/
RUN pip3 install -r /cycshare/requirements.txt

COPY LICENSE.md README.md config.py cycshare.py MANIFEST.in requirements.txt setup.py .flaskenv /cycshare/
COPY services /cycshare/services
COPY cycshare /cycshare/cycshare
COPY .git /cycshare/.git

# Setup default user, when enter docker container
USER cycshare:cycshare
WORKDIR /cycshare

ENTRYPOINT /cycshare/services/server/docker-entrypoint.sh