#!/usr/bin/env bash

##
# This script sets up a Python virtual environment and performs type checking using `pyre`.
# It leverages `watchman` for faster incremental filesystem change detection.
# Prerequisite: `brew install watchman`

set -e  # Exit on any error

# Create and activate virtual environment
mkdir -p .venv
python3 -m venv .venv
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

# Perform type checking with pyre
echo "********** TYPE CHECKING ***********"
watchman watch .  # Initialize watchman to monitor file changes
pyre incremental   # Perform incremental type checking
