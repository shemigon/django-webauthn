#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import codecs
import os

from setuptools import find_packages, setup

PACKAGE = 'webauthn'

def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


setup(
    name='django-webauthn',
    version='0.0.1',
    description="Django support for Web Authn.",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    keywords='django environment variables 12factor',
    author='Boris Shemigon',
    author_email='i@boris.co',
    url='https://github.com/shemigon/django-webauthn',
    license='MIT',
    packages=find_packages(),
    platforms=["any"],
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        'pywarp'
    ],
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django'
    ]
)
