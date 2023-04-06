#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='fabelcommon',
    version='15.0.2',
    description='Common API and functions',
    packages=find_packages(),
    package_data={'': ['py.typed']},
    install_requires=['djangorestframework', 'pytz', 'requests', 'xmltodict', 'lxml'],
)
