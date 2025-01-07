#!/usr/bin/env bash

set -e  # Stop execution on error

# Variables
TAG=${1:-latest}  # Use provided tag or default to 'latest'
IMAGE="033969152235.dkr.ecr.us-east-1.amazonaws.com/astragateway:$TAG"
BASE_PATH="$PWD/../"
PYTHONPATH="/app/astracommon/src/:/app/astracommon-internal/src:/app/astragateway/src/:/app/astragateway-internal/src/:/app/astraextensions/"
TEST_DIR="$BASE_PATH/astragateway/test"
ASTRACOMMON_SRC="$BASE_PATH/astracommon/src"
ASTRACOMMON_INTERNAL_SRC="$BASE_PATH/astracommon-internal/src"
ASTRAGATEWAY_SRC="$BASE_PATH/astragateway/src"
ASTRAGATEWAY_INTERNAL_SRC="$BASE_PATH/astragateway-internal/src"
SSL_CERTS="$BASE_PATH/ssl_certificates/dev"

# Log image and base path
echo "Using image: $IMAGE"
echo "Base path: $BASE_PATH"
echo "Running tests in Docker container..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
  echo "Error: Docker is not installed or not available in PATH."
  exit 1
fi

# Run Docker container with the necessary configurations
docker run --rm -it \
  -e PYTHONPATH="$PYTHONPATH" \
  -v "$TEST_DIR:/app/astragateway/test" \
  -v "$ASTRACOMMON_SRC:/app/astracommon/src" \
  -v "$ASTRACOMMON_INTERNAL_SRC:/app/astracommon-internal/src" \
  -v "$ASTRAGATEWAY_SRC:/app/astragateway/src" \
  -v "$ASTRAGATEWAY_INTERNAL_SRC:/app/astragateway-internal/src" \
  -v "$SSL_CERTS:/app/ssl_certificates" \
  --entrypoint "" \
  "$IMAGE" /bin/sh -c "pip install mock websockets && python -m unittest discover"

echo "Docker container tests completed successfully."
