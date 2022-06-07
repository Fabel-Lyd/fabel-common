#!/usr/bin/env python

from distutils.core import setup

setup(
    name='fabelcommon',
    version='1.2.0',
    description='Common API and functions',
    packages=[
        'fabelcommon',
        'fabelcommon/bokbasen',
        'fabelcommon/feed',
        'fabelcommon/beat',
        'fabelcommon/datetime',
        'fabelcommon/json',
        'fabelcommon/beat/releases',
        'fabelcommon/bokbasen/export',
        'fabelcommon/feed/export'
    ],
    install_requires=['djangorestframework', 'pytz', 'requests', 'xmltodict'],
)
