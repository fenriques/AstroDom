echo Activating virtual environment
call venv\Scripts\activate.bat

SET QT_SCALE_FACTOR=1 && SET QT_FONT_DPI=96

cd venv\Lib\site-packages && 
python -m astrodom 
deactivate
