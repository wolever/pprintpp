#!/usr/bin/env python

import os
import sys

from setuptools import setup

os.chdir(os.path.dirname(sys.argv[0]) or ".")

try:
    long_description = open("README.rst", "U").read()
except IOError:
    long_description = "See https://github.com/wolever/pprintpp"

setup(
    name="pp-ez",
    version="0.2.0",
    url="https://github.com/wolever/pprintpp",
    author="David Wolever",
    author_email="david@wolever.net",
    description="A short alias for the pprintpp or pprint module",
    long_description=long_description,
    py_modules=["pp"],
    install_requires=[],
    license="BSD",
    classifiers=[ x.strip() for x in """
        Development Status :: 3 - Alpha
        Environment :: Console
        Intended Audience :: Developers
        License :: OSI Approved :: BSD License
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python
        Programming Language :: Python :: 2
        Programming Language :: Python :: 3
        Topic :: Software Development
        Topic :: Utilities
    """.split("\n") if x.strip() ],
)
