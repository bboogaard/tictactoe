# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /apps/
WORKDIR /apps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /apps/