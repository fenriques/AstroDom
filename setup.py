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
import codecs
import os


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


long_description = read("README.md")

setup(
    name="astrodom",
    version=get_version("astrodom/__init__.py"),
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
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
    ],
)
