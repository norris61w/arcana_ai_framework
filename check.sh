#!/usr/bin/env bash

##
# This script sets up a Python virtual environment and runs type checking using `pyre`.
##

set -e  # Exit immediately if any command exits with a non-zero status

# Create and activate virtual environment
mkdir -p .venv
python3 -m venv .venv  # Use the built-in `venv` module for creating the virtual environment
source .venv/bin/activate

# Install required dependencies
pip install -r ../astracommon/requirements.txt
pip install -r ../astracommon/requirements-dev.txt
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Add spacing for better output readability
echo ""
echo ""
echo ""

# Run type checking with pyre
echo "********** TYPE CHECKING ***********"
pyre check  # Perform full type checking
