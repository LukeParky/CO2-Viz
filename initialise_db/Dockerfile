FROM continuumio/miniconda3 as base
#FROM ubuntu:jammy

WORKDIR app/

## Install Miniconda
#ENV PATH="/root/miniconda3/bin:${PATH}"
#ARG PATH="/root/miniconda3/bin:${PATH}"
#
#RUN apt-get update \
#    && apt install -y wget \
#    && rm -rf /var/lib/apt/lists/*
#
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#    && mkdir /root/.conda \
#    && bash Miniconda3-latest-Linux-x86_64.sh -b \
#    && rm -f Miniconda3-latest-Linux-x86_64.sh
#RUN conda --version

COPY environment.yml .
RUN conda env create -f environment.yml

COPY . .

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "co2sa1", "python", "organise_data.py"]
