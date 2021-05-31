FROM python:3.8.3

RUN pip install -U --no-cache-dir pip \
    && pip install -U --no-cache-dir jupyter==1.0.0
