set PYTHON_VERSION=3.12

echo Checking for Python version
for /f "tokens=2 delims==" %%i in ('python --version 2^>^&1 ^| findstr /c:"Python"') do set VERSION=%%i
if not "%VERSION:~7,4%" == "%PYTHON_VERSION%" (
    echo Python %PYTHON_VERSION% is not installed.
    exit /b 1
)

echo Creating virtual environment
python -m venv venv

echo Activating virtual environment
call venv\Scripts\activate.bat

echo Installing astrodom and collecting packages, it may take a while
python -m pip install astrodom --upgrade --no-cache-dir

echo Setup complete!
pause
