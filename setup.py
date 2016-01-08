try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
from codecs import open
import mrtparse

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

try:
    os.symlink('../examples', 'mrtparse/examples')
    os.symlink('../samples', 'mrtparse/samples')
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
            'Operating System :: OS Independent',
            'Topic :: System :: Networking',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Internet',
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
        include_package_data=True,
        use_2to3=True,
        zip_safe=False,
    )
finally:
    os.unlink('mrtparse/examples')
    os.unlink('mrtparse/samples')
