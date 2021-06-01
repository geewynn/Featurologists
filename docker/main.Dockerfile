FROM python:3.8.3

COPY . /opt/workdir
RUN cd /opt/workdir && pip install .
