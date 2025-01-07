#!/usr/bin/env bash

set -e


VENV_DIR=".venv"
COMMON_REQUIREMENTS="../astracommon/requirements.txt"
COMMON_DEV_REQUIREMENTS="../astracommon/requirements-dev.txt"
PROJECT_REQUIREMENTS="requirements.txt"
PROJECT_DEV_REQUIREMENTS="requirements-dev.txt"
UNIT_TEST_DIR="test/unit"
INTEGRATION_TEST_DIR="test/integration"
ASTRACOMMON_SRC="../../../astracommon/src"
PROJECT_SRC="../../src"
ASTRAEXTENSIONS_SRC="../../../astraextensions"


mkdir -p "$VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"


echo "Installing dependencies..."
pip install -r "$COMMON_REQUIREMENTS"
pip install -r "$COMMON_DEV_REQUIREMENTS"
pip install -r "$PROJECT_REQUIREMENTS"
pip install -r "$PROJECT_DEV_REQUIREMENTS"

# Unit tests
echo "********** UNIT TEST ***********"
cd "$UNIT_TEST_DIR"
PYTHONPATH="$ASTRACOMMON_SRC:$PROJECT_SRC:$ASTRAEXTENSIONS_SRC" python -m unittest discover --verbose

# Integration tests
echo "********** INTEGRATION TEST ***********"
cd "../integration"
PYTHONPATH="$ASTRACOMMON_SRC:$PROJECT_SRC:$ASTRAEXTENSIONS_SRC" python -m unittest discover --verbose


deactivate
#!/usr/bin/env bash

set -e


VENV_DIR=".venv"
COMMON_REQUIREMENTS="../astracommon/requirements.txt"
COMMON_DEV_REQUIREMENTS="../astracommon/requirements-dev.txt"
PROJECT_REQUIREMENTS="requirements.txt"
PROJECT_DEV_REQUIREMENTS="requirements-dev.txt"
UNIT_TEST_DIR="test/unit"
INTEGRATION_TEST_DIR="test/integration"
ASTRACOMMON_SRC="../../../astracommon/src"
PROJECT_SRC="../../src"
ASTRAEXTENSIONS_SRC="../../../astraextensions"


mkdir -p "$VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"


echo "Installing dependencies..."
pip install -r "$COMMON_REQUIREMENTS"
pip install -r "$COMMON_DEV_REQUIREMENTS"
pip install -r "$PROJECT_REQUIREMENTS"
pip install -r "$PROJECT_DEV_REQUIREMENTS"

# Unit tests
echo "********** UNIT TEST ***********"
cd "$UNIT_TEST_DIR"
PYTHONPATH="$ASTRACOMMON_SRC:$PROJECT_SRC:$ASTRAEXTENSIONS_SRC" python -m unittest discover --verbose

# Integration tests
echo "********** INTEGRATION TEST ***********"
cd "../integration"
PYTHONPATH="$ASTRACOMMON_SRC:$PROJECT_SRC:$ASTRAEXTENSIONS_SRC" python -m unittest discover --verbose

deactivate
