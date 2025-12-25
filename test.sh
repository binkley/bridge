#!/usr/bin/env bash
# Exit immediately if any command fails
set -e

# Ensure we are in the virtual environment
source .venv/bin/activate

# 1. Clean up previous coverage data
python3 -m coverage erase

echo ">>> Running generate-hands.py tests..."
python3 -m coverage run -a --source=. generate-hands.py --test

echo ">>> Running evaluate-hands.py tests..."
# We use -a (append) to combine coverage with generate-hands
python3 -m coverage run -a --source=. evaluate-hands.py --test

echo ""
echo ">>> Coverage Report"
echo "--------------------------------------"
# This will exit with a non-zero status if coverage is < 90%
python3 -m coverage report --show-missing --fail-under=90