@echo off
cd %~dp0

for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
if not "%PYTHON_VERSION:~0,6%"=="3.12.0" (
  echo Python 3.12 is required. Current version: %PYTHON_VERSION%
  exit /b 1
)
echo Creating virtual environment
python -m venv venv

echo Activating virtual environment
call venv\Scripts\activate.bat

echo Installing astrodom and collecting packages, it may take a while
python -m pip install astrodom --upgrade --no-cache-dir

echo Setup complete!
deactivate




