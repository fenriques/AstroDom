
echo checking python version
python --version

echo Creating virtual environment
python -m virtualenv venv

echo Collecting packages, it takes a while
venv\Scripts\activate && python -m pip install astrodom --upgrade --no-cache-dir

