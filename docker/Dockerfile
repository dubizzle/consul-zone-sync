FROM python:3.5-alpine

ENV APP_NAME consul-zone-sync

ADD requirements/requirements.txt /tmp/requirements.txt
RUN set -e; \
    pip install -r /tmp/requirements.txt;

ADD docker/archive.tar.gz /opt

CMD ["python", "-u",  "/opt/main.py"]

HEALTHCHECK --interval=5s --timeout=3s \
CMD if pgrep -f  'python -u /opt/main.py'; then exit 0; else exit 1; fi
