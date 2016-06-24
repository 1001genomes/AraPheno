FROM python:2.7
MAINTAINER Ümit Seren

ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code

VOLUME /code

ADD requirements.txt /code/

RUN pip install -r requirements.txt && pip install gunicorn

ADD . /code/