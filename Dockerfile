FROM python:3.7
COPY . /app
WORKDIR /app
RUN make install
