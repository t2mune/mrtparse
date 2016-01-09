'''
setup.py - a setup script

Copyright (C) 2016 greenHippo, LLC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Authors:
    Tetsumune KISO <t2mune@gmail.com>
    Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>
    Nobuhiro ITOU <js333123@gmail.com>
'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys
from codecs import open
import mrtparse

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

examples = 'mrtparse/examples'
samples = 'mrtparse/samples'

try:
    if 'install' in sys.argv:
        os.symlink('../examples', examples)
        os.symlink('../samples', samples)
    setup(
        name=mrtparse.__name__,
        version=mrtparse.__version__,
        description='MRT format data parser',
        long_description=long_descr,
        url='https://github.com/YoshiyukiYamauchi/mrtparse',
        author='Tetsumune KISO, Yoshiyuki YAMAUCHI, Nobuhiro ITOU',
        author_email='t2mune@gmail.com, info@greenhippo.co.jp, js333123@gmail.com',
        license='Apache License 2.0',
        platforms='any',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Telecommunications Industry',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Internet',
            'Topic :: System :: Networking',
        ],
        keywords='mrt bgp',
        packages = ['mrtparse'],
        package_data={
            'mrtparse': [
                'examples/*.py',
                'samples/bird*',
                'samples/openbgpd*',
                'samples/quagga*'
            ]
        },
        zip_safe=False,
    )
finally:
    if 'install' in sys.argv:
        os.unlink(examples)
        os.unlink(samples)
