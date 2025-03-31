#!/bin/bash

set -e

# Go to the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it first."
    exit 1
fi

# Remove existing virtual environment
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create a new virtual environment
echo "Creating a new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

# Run tests with coverage
echo "Running tests with coverage..."
PYTHONPATH=./src pytest --cov=src --cov-report=term-missing tests/

# Run main script if present
if [ -f "run.py" ]; then
    echo "Running run.py..."
    python run.py
else
    echo "run.py not found. Skipping execution."
fi

echo "Script completed successfully."
