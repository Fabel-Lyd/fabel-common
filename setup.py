#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='fabelcommon',
    version='4.0.1',
    description='Common API and functions',
    packages=find_packages(),
    install_requires=['djangorestframework', 'pytz', 'requests', 'xmltodict'],
)
