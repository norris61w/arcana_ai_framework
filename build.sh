#!/usr/bin/env bash

##
# This script builds a Docker container image.
# The tag can be passed as an argument, defaulting to "latest" if not provided.
##

set -e  # Exit immediately if any command exits with a non-zero status

# Variables
IMAGE="033969152235.dkr.ecr.us-east-1.amazonaws.com/astragateway:${1:-latest}"

# Log the image being built
echo "Building container... $IMAGE"

# Build the Docker image
docker build ../ -f Dockerfile --rm=false -t "$IMAGE"
