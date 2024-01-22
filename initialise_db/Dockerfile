FROM continuumio/miniconda3 as build

WORKDIR app/

COPY environment.yml .
RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "co2sa1", "/bin/bash", "-c"]
RUN conda-pack --ignore-missing-files -n co2sa1 -o /tmp/env.tar \
  && mkdir /venv \
  && cd /venv \
  && tar xf /tmp/env.tar \
  && rm /tmp/env.tar
RUN /venv/bin/conda-unpack


FROM ubuntu:jammy as runtime

COPY --from=build /venv /venv

COPY . .

SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && \
           python organise_data.py
