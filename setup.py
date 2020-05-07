############################################################
# -*- coding: utf-8 -*-
#
#  Astroimaging catalogue software
#
# Ferrante Enriques
# (c) 2020
#
# License MIT
#
###########################################################
from setuptools import setup, find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="astrodom",
    version="0.2.0",
    packages=find_packages(),
    python_requires=">=3.6, <3.9",
    install_requires=[
        "astropy==4.0",
        "matplotlib==3.1.3",
        "PyQt5==5.13.2",
        "pyqtgraph==0.10.0",
        "numpy==1.18.2",
    ],
    include_package_data=True,
    url="https://github.com/fenriques/AstroDom",
    license="MIT",
    author="Ferrante Enriques",
    author_email="ferrante.enriques@gmail.com",
    description="Astroimaging Catalogue Software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Other Environment",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
    ],
)
