#!/bin/bash
cd $(dirname "$0")
python3 -m venv venv
source ./venv/bin/activate
pip3 install astrodom --upgrade --no-cache-dir
deactivate
