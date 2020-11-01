FROM python:3.8-alpine
MAINTAINER Walter Capa

ENV PYTHONUNBUFFERED 1

COPY ./requeriments.txt /requeriments.txt
RUN pip install -r /requeriments.txt

RUN mkdir /src
WORKDIR /scr
COPY ./src /src

RUN adduser -D user
USER user
