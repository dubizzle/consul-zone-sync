FROM python:3.5-alpine

ENV APP_NAME consul-zone-sync



ADD docker/archive.tar.gz /opt


ADD requirements/requirements.txt /tmp/requirements.txt
RUN set -e; \
    pip install -r /tmp/requirements.txt;


