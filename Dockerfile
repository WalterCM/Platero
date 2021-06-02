FROM python:3.8-alpine
MAINTAINER Walter Capa

ENV PYTHONUNBUFFERED 1

COPY ./requeriments.txt /requeriments.txt
RUN apk add --update --no-cache jpeg-dev zlib-dev
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .build-deps \
        build-base linux-headers gcc libc-dev postgresql-dev



RUN pip install virtualenv && virtualenv -p python /.env
RUN /.env/bin/pip install -r /requeriments.txt
RUN apk del .build-deps

RUN mkdir /src
WORKDIR /src
COPY ./src /src

RUN adduser -D user
USER user
