#!/usr/bin/env python
'''
setup.py - setuptools installation configuration for urlcanon

Copyright (C) 2016-2018 Internet Archive

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import setuptools

dependencies = ['idna>=2.5,<=2.8']
try:
    import ipaddress
except ImportError:
    dependencies.append('py2-ipaddress>=3.4.1,<=3.4.1')

setuptools.setup(
        name='urlcanon',
        description='url canonicalization library for python and java',
        version='0.2.1',
        packages=['urlcanon'],
        url='https://github.com/iipc/urlcanon',
        install_requires=dependencies,
        tests_require=['pytest'],
        long_description=open('README.rst', mode='rb').read().decode('UTF-8'),
        classifiers=[
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Java',
            'Topic :: Internet :: WWW/HTTP',],)

