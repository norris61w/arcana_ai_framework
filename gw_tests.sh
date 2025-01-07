#!/usr/bin/env bash

##
# This script runs a Docker container for testing, mounting the necessary volumes and setting up the environment.
# It installs test dependencies (`mock` and `websockets`) and runs unit tests using `unittest`.
##

set -e  # Exit immediately if any command exits with a non-zero status

# Variables
TAG=${1:-latest}  # Use the provided tag or default to "latest"
IMAGE="033969152235.dkr.ecr.us-east-1.amazonaws.com/astragateway:$TAG"
BASE_PATH="$PWD/../"  # Base path for mounting volumes

# Log the image and paths being used
echo "Running container with image: $IMAGE"
echo "Base path: $BASE_PATH"

# Run the Docker container
docker run --rm -it \
  -e PYTHONPATH="/app/astracommon/src/:/app/astracommon-internal/src:/app/astragateway/src/:/app/astragateway-internal/src/:/app/astraextensions/" \
  -v "$BASE_PATH/astragateway/test:/app/astragateway/test" \
  -v "$BASE_PATH/astracommon/src:/app/astracommon/src" \
  -v "$BASE_PATH/astracommon-internal/src:/app/astracommon-internal/src" \
  -v "$BASE_PATH/astragateway/src:/app/astragateway/src" \
  -v "$BASE_PATH/astragateway-internal/src:/app/astragateway-internal/src" \
  -v "$BASE_PATH/ssl_certificates/dev:/app/ssl_certificates" \
  --entrypoint "" \
  "$IMAGE" /bin/sh -c "pip install mock websockets && python -m unittest discover"

# Completion message
echo "Tests completed successfully."
