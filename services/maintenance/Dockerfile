FROM nginx:1.29.5-alpine3.23

LABEL maintainer "bioinformatics@age.mpg.de"

ARG EMAIL
ENV EMAIL ${EMAIL}

COPY index.html /usr/share/nginx/html/index.html
COPY maintenance.conf /etc/nginx/conf.d/default.conf

RUN sed -i "s/mail@address.com/${EMAIL}/g" /usr/share/nginx/html/index.html

## docker buildx create --use
## docker buildx build --platform linux/amd64,linux/arm64 --build-arg EMAIL="flaski@age.mpg.de" -t mpgagebioinformatics/flaski:maintenance --push .