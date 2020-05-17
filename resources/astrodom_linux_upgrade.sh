#!/bin/bash
cd $(dirname "$0")
source ./venv/bin/activate
pip3 install astrodom --upgrade --no-cache-dir
deactivate
