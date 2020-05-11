# Installation
## Requirements
AstroDom is developed using Python's QT bindings (PyQT) and thus can be installed on Linux, Windows and MacOS platforms.
AstrDom is all about presenting data, so it needs high definition displays (1920x1080). 
FITS header data are read from astro imaging software like Astro Photography Tool, Sequence Generator Pro, BackyardEOS, MaximDL, Nebulosity, N.I.N.A., CCDCiel and INDI/Ekos. All these softwares are supported even though it has been tested extensively on INDI/Ekos and MaximDL only.

## Install Python and Venv
Setting up a Python Virtual Environment is recommended not to mess up your other Python apps.  
Installation of Python and venv is not the main purpose of this document; you can search for many resource that have step by step instruction for your platform.
On a terminal window check  which Python and Virtualenv are installed.

    python --version
    virtualenv --version
  
  AstroDom requires Python version 3.6 or 3.7. It is not (yet) tested on 3.8 or above.

## Install AstroDom
To install AstroDom, create a directory on your system where you will store AstroDom's file. 
Any name is ok, but let's say '**astrodom**'. 
Download one of the following script to 'astrodom':

Linux: https://github.com/fenriques/AstroDom/blob/master/resources/astrodom_linux_install.sh

Windows: https://github.com/fenriques/AstroDom/blob/master/resources/astrodom_windows_install.bat

Run the script from the terminal. The script is automating the following steps that you can enter manually if you prefer:
On Linux:

	cd astrodom
    python3 -m venv venv
    source ./venv/bin/activate
    pip3 install astrodom --upgrade --no-cache-dir
  
  On Windows:
 

     cd astrodom
     venv\Scripts\activate
     python -m pip install astrodom --upgrade --no-cache-dir
     
## Run AstroDom
 Download one of the following script to 'astrodom':

Linux: https://github.com/fenriques/AstroDom/blob/master/resources/astrodom_linux_run.sh

Windows: https://github.com/fenriques/AstroDom/blob/master/resources/astrodom_windows_run.bat

Run the script from the terminal. Else follow these steps:
On Linux:

    cd astrodom
    source ./venv/bin/activate
    cd ./venv/lib/python3.7/site-packages
    python -m astrodom

On Windows:

    cd astrodom
    venv\Scripts\activate 
    cd venv\Lib\site-packages
    python -m astrodom







