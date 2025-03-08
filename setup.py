############################################################
# -*- coding: utf-8 -*-
#
#  Astroimaging catalogue software
#
# Ferrante Enriques
# (c) 2021-2025
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
    include_package_data=True,
    package_data={
        'astrodom.rsc': ['gui/*', 'icons/*'],
    },
    python_requires=">=3.12",
    install_requires=[
        "astropy",
        "ephem",
        "matplotlib",
        "numpy",
        "pandas",
        "PyQt6",
        "photutils",
        "pyqtgraph",
        "importlib_resources",
    ],
    url="https://github.com/fenriques/AstroDom",
    license="MIT",
    author="Ferrante Enriques",
    author_email="ferrante.enriques@gmail.com",
    description="Astroimaging Catalogue Software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Other Environment",
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
