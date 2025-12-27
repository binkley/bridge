#!/usr/bin/env bash
# Exit immediately if any command fails
set -e

# Assumes Python 3.13 because of C++ depencencies

python3 -m coverage erase
python3 -m coverage run -a --source=. generate-hands.py --test
python3 -m coverage run -a --source=. evaluate-hands.py --test

echo
echo ">>> Coverage Report"
echo "--------------------------------------"
# This will exit with a non-zero status if coverage is < 90%
python3 -m coverage report --show-missing --fail-under=90
