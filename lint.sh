#!/usr/bin/env bash

mkdir -p .venv
virtualenv .venv -p python3
. .venv/bin/activate
pip install -r ../astracommon/requirements.txt
pip install -r ../astracommon/requirements-dev.txt
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo ""
echo ""
echo ""
echo "**********PYLINT***********"
PYTHONPATH=../astracommon/src/ pylint src/astragateway --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --rcfile=../astracommon/pylintrc
deactivate