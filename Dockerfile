# Define arguments for Python version and base image
ARG PYTHON_VERSION=3.8.3-alpine3.11
ARG BASE=033969152235.dkr.ecr.us-east-1.amazonaws.com/astrabase:latest

# Base image for building the application
FROM ${BASE} as builder

# Install necessary build tools and update pip
RUN apk update \
 && apk add --no-cache linux-headers gcc libtool openssl-dev libffi \
 && apk add --no-cache --virtual .build_deps build-base libffi-dev \
 && pip install --upgrade pip

# Set up a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements files
COPY astragateway/requirements.txt ./astragateway_requirements.txt
COPY astracommon/requirements.txt ./astracommon_requirements.txt

# Fix compatibility issues with manylinux wheels and Alpine Linux
RUN echo 'manylinux2014_compatible = True' > /usr/local/lib/python3.8/_manylinux.py
RUN pip install -U pip==20.2.2
RUN pip install orjson==3.4.6

# Install application dependencies
RUN pip install -U pip wheel \
 && pip install -r ./astragateway_requirements.txt \
                -r ./astracommon_requirements.txt

# Main image to run the application
FROM python:${PYTHON_VERSION}

# Create a user and group for the application
RUN addgroup -g 502 -S astragateway \
 && adduser -u 502 -S -G astragateway astragateway \
 && mkdir -p /app/astragateway/src \
 && mkdir -p /app/astracommon/src \
 && mkdir -p /app/astracommon-internal/src \
 && mkdir -p /app/astraextensions \
 && chown -R astragateway:astragateway /app/astragateway /app/astracommon /app/astraextensions

# Install runtime dependencies
RUN apk update \
 && apk add --no-cache \
        'su-exec>=0.2' \
        tini \
        bash \
        gcc \
        openssl-dev \
        gcompat \
 && pip install --upgrade pip

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application entry point script
COPY astragateway/docker-entrypoint.sh /usr/local/bin/

# Copy application source code with correct ownership
COPY --chown=astragateway:astragateway astragateway/src /app/astragateway/src
COPY --chown=astragateway:astragateway astracommon/src /app/astracommon/src
COPY --chown=astragateway:astragateway astracommon-internal/src /app/astracommon-internal/src
COPY --chown=astragateway:astragateway astraextensions/release/alpine-3.11 /app/astraextensions

# Allow non-root users to use `ping`
RUN chmod u+s /bin/ping

# Add CLI utility script
COPY astragateway/docker-scripts/astra-cli /bin/astra-cli
RUN chmod u+x /bin/astra-cli

# Set the working directory
WORKDIR /app/astragateway

# Expose necessary ports
EXPOSE 28332 9001 1801

# Configure environment variables
ENV PYTHONPATH=/app/astracommon/src/:/app/astracommon-internal/src/:/app/astragateway/src/:/app/astraextensions/ \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/app/astraextensions" \
    PATH="/opt/venv/bin:$PATH"

# Define the entry point
ENTRYPOINT ["/sbin/tini", "--", "/bin/sh", "/usr/local/bin/docker-entrypoint.sh"]
