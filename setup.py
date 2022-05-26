#!/usr/bin/env python

from distutils.core import setup

setup(
    name='fabelcommon',
    version='1.1.0',
    description='Common API and functions',
    packages=['fabelcommon', 'fabelcommon/bokbasen', 'fabelcommon/feed', 'fabelcommon/beat', 'fabelcommon/datetime'],
    install_requires=['djangorestframework', 'pytz', 'requests', 'xmltodict'],
)
