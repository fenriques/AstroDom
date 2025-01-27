#!/bin/bash
cd $(dirname "$0")

# Check for Python 3.12
PYTHON_VERSION=$(python3 --version 2>&1)
if [[ $PYTHON_VERSION != "Python 3.12"* ]]; then
  echo "Python 3.12 is required. Current version: $PYTHON_VERSION"
  exit 1
fi

export QT_SCALE_FACTOR=1
python3 -m astrodom
deactivate