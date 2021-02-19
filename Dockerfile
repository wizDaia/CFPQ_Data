FROM ubuntu:latest

RUN apt-get -y update && \
    apt-get install -y \
    python3-pip \
    git \
    openjdk-11-jre-headless

COPY . /CFPQ_Data

WORKDIR /CFPQ_Data
RUN pip3 install -r requirements.txt
