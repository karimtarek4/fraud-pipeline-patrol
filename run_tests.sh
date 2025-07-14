#!/bin/bash

# Simple shell script to run all tests in the fraud pipeline project
# This is a wrapper around the Python test runner for convenience

echo "🧪 Running all tests for Fraud Pipeline Patrol..."
echo "================================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python to run tests."
    exit 1
fi

# Check if pytest is available
if ! python -c "import pytest" &> /dev/null; then
    echo "❌ pytest not found. Installing pytest..."
    pip install pytest pytest-cov pytest-xdist
fi

# Run the Python test runner with all arguments passed through
python run_all_tests.py "$@"
