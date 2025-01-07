ARG PYTHON_VERSION=3.8.3-alpine3.11
ARG BASE=033969152235.dkr.ecr.us-east-1.amazonaws.com/astrabase:latest

FROM ${BASE} as builder
# Assumes this repo and astracommon repo are at equal roots

RUN apk update \
 && apk add --no-cache linux-headers gcc libtool openssl-dev libffi \
 && apk add --no-cache --virtual .build_deps build-base libffi-dev \
 && pip install --upgrade pip

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY astragateway/requirements.txt ./astragateway_requirements.txt
COPY astracommon/requirements.txt ./astracommon_requirements.txt

# most recent version of pip doesn't seem to detect manylinux wheel correctly
# orjson cannot be installed normally due to alpine linux using musl-dev
RUN echo 'manylinux2014_compatible = True' > /usr/local/lib/python3.8/_manylinux.py
RUN pip install -U pip==20.2.2
RUN pip install orjson==3.4.6

RUN pip install -U pip wheel \
 && pip install -r ./astragateway_requirements.txt \
                -r ./astracommon_requirements.txt

FROM python:${PYTHON_VERSION}

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN addgroup -g 502 -S astragateway \
 && adduser -u 502 -S -G astragateway astragateway \
 && mkdir -p /app/astragateway/src \
 && mkdir -p /app/astracommon/src \
 && mkdir -p /app/astracommon-internal/src \
 && mkdir -p /app/astraextensions \
 && chown -R astragateway:astragateway /app/astragateway /app/astracommon /app/astraextensions

RUN apk update \
 && apk add --no-cache \
        'su-exec>=0.2' \
        tini \
        bash \
        gcc \
        openssl-dev \
        gcompat \
 && pip install --upgrade pip

COPY --from=builder /opt/venv /opt/venv

COPY astragateway/docker-entrypoint.sh /usr/local/bin/

COPY --chown=astragateway:astragateway astragateway/src /app/astragateway/src
COPY --chown=astragateway:astragateway astracommon/src /app/astracommon/src
COPY --chown=astragateway:astragateway astracommon-internal/src /app/astracommon-internal/src
COPY --chown=astragateway:astragateway astraextensions/release/alpine-3.11 /app/astraextensions

RUN chmod u+s /bin/ping

COPY astragateway/docker-scripts/astra-cli /bin/astra-cli
RUN chmod u+x /bin/astra-cli

WORKDIR /app/astragateway
EXPOSE 28332 9001 1801
ENV PYTHONPATH=/app/astracommon/src/:/app/astracommon-internal/src/:/app/astragateway/src/:/app/astraextensions/ \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/app/astraextensions" \
    PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["/sbin/tini", "--", "/bin/sh", "/usr/local/bin/docker-entrypoint.sh"]
