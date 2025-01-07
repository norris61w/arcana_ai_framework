#!/usr/bin/env bash

##
# This is a version that relies on `watchman` and is much faster for repeated usage, since it queries
# incremental changes in the filesystem.
# Make sure you have run `brew install watchman` beforehand.

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
echo "**********TYPE CHECKING***********"
watchman watch .
pyre incremental
