#!/usr/bin/env python

from distutils.core import setup
import mrtparse

setup(
    name=mrtparse.__pyname__,
    version=mrtparse.__version__,
    description=mrtparse.__descr__,
    url=mrtparse.__url__,
    author=mrtparse.__author__,
    author_email=mrtparse.__email__,
    license=mrtparse.__license__,
    py_modules=[mrtparse.__pyname__],
)
