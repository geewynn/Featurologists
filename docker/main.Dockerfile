FROM python:3.8.3

COPY featurologists /opt/featurologists
RUN cd /opt/featurologists && make setup
