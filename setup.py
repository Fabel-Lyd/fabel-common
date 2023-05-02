#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages
from version import PACKAGE_VERSION


setup(
    name='fabelcommon',
    version=PACKAGE_VERSION,
    description='Common API and functions',
    packages=find_packages(),
    package_data={'': ['py.typed']},
    install_requires=['djangorestframework', 'pytz', 'requests', 'xmltodict', 'lxml'],
)
