FROM python:3.13-slim

LABEL maintainer="naeimiarian82@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./core .