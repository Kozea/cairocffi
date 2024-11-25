import os
import sys

from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build


api_mode = False
if ('CAIROCFFI_API_MODE' in os.environ and
        int(os.environ['CAIROCFFI_API_MODE']) == 1):
    api_mode = True

setup(
    name='cairocffi',
    #use_scm_version=True,
    version='1.7.2',
    install_requires=['cffi >= 1.1.0', 'xcffib >= 1.5.1'],
    setup_requires=['setuptools_scm', 'cffi >= 1.1.0', 'xcffib >= 1.5.1'],
    packages=['cairocffi'] if api_mode else [],
    cffi_modules=['cairocffi/ffi_build.py:ffi']
)
