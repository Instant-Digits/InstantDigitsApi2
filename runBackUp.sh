#!/bin/bash

# Determine the directory of the current script
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the Python script
python "$SCRIPT_DIR/mangoBackUp.py"
