#!/bin/bash
# Set the local Python version
pyenv local

# Activate the virtual environment
source venv/bin/activate

# Run main script and capture any errors
python main.py || echo "main.py encountered an error."

# Run the sync script regardless of the main script's success
python sync.py