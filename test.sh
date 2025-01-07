#!/usr/bin/env bash

mkdir -p .venv
virtualenv -p python3 .venv
. .venv/bin/activate
pip install -r ../astracommon/requirements.txt
pip install -r ../astracommon/requirements-dev.txt
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo ""
echo ""
echo ""
echo "**********UNIT TEST***********"
cd test/unit
PYTHONPATH=../../../astracommon/src:../../src:../../../astraextensions python -m unittest discover --verbose

echo ""
echo ""
echo ""
echo "**********INTEGRATION TEST***********"
cd ../integration
PYTHONPATH=../../../astracommon/src:../../src:../../../astraextensions python -m unittest discover --verbose

deactivate
