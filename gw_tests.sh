TAG=${1:-latest}
IMAGE=033969152235.dkr.ecr.us-east-1.amazonaws.com/astragateway:$TAG
BASE_PATH=$PWD/../
docker run --rm -it \
  -e PYTHONPATH=/app/astracommon/src/:/app/astracommon-internal/src:/app/astragateway/src/:/app/astragateway-internal/src/:/app/astraextensions/ \
  -v $BASE_PATH/astragateway/test:/app/astragateway/test \
  -v $BASE_PATH/astracommon/src:/app/astracommon/src \
  -v $BASE_PATH/astracommon-internal/src:/app/astracommon-internal/src \
  -v $BASE_PATH/astragateway/src:/app/astragateway/src \
  -v $BASE_PATH/astragateway-internal/src:/app/astragateway-internal/src \
  -v $BASE_PATH/ssl_certificates/dev:/app/ssl_certificates \
  --entrypoint "" \
  $IMAGE /bin/sh -c "pip install mock websockets && python -m unittest discover"
