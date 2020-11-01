FROM python:3.8-alpine
MAINTAINER Walter Capa

ENV PYTHONUNBUFFERED 1

COPY ./requeriments.txt /requeriments.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requeriments.txt
RUN apk del .tmp-build-deps

RUN mkdir /src
WORKDIR /src
COPY ./src /src

RUN adduser -D user
USER user
