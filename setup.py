import os
import sys

from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build

setup(
    name='cairocffi',
    use_scm_version=True,
    install_requires=['cffi >= 1.1.0'],
    setup_requires=['setuptools_scm', 'cffi >= 1.1.0'],
    cffi_modules=['cairocffi/ffi.py:ffi'],
)
