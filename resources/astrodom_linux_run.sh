#!/bin/bash
cd $(dirname "$0")
source ./venv/bin/activate
if [ -d "./venv/lib/python3.12" ]
then
  cd ./venv/lib/python3.12/site-packages/
else
  echo "python not found"
  exit 0
fi
export QT_SCALE_FACTOR=1
python3 -m astrodom
deactivate