for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
if not "%PYTHON_VERSION:~0,6%"=="3.12.0" (
  echo Python 3.12 is required. Current version: %PYTHON_VERSION%
  exit /b 1
)
echo Activating virtual environment
call venv\Scripts\activate.bat

SET QT_SCALE_FACTOR=1
SET QT_FONT_DPI=96

cd venv\Lib\site-packages
python -m astrodom 
deactivate
