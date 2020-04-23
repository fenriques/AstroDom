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

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()
setup(
    name='astrodom',
    version='0.1.6',
    packages=find_packages(),
    python_requires='~=3.6',
    install_requires=[
        'astropy==4.0',
        'matplotlib==3.1.3',
        'PyQt5==5.13.2',
        'pyqtgraph==0.10.0',
        'numpy==1.18.2',
    ],
    include_package_data=True,
    url='https://github.com/fenriques/AstroDom',
    license='MIT',
    author='Ferrante Enriques',
    author_email='ferrante.enriques@gmail.com',
    description='Astroimaging Catalogue Software',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Other Environment',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
    ]
)