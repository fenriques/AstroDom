#!/bin/bash
cd $(dirname "$0")
source ./venv/bin/activate
cd ./venv/lib/python3.7/site-packages/
export QT_SCALE_FACTOR=1
python -m astrodom
deactivate
