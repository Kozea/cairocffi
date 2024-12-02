import os
import sys

from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build


api_mode = False
if ('CAIROCFFI_API_MODE' in os.environ and
        int(os.environ['CAIROCFFI_API_MODE']) == 2):
    api_mode = True

setup(
    name='cairocffi',
    use_scm_version=True,
    version='1.7.2',
    # when xcffib is updated, bump to include API mode
    install_requires=['cffi >= 1.1.0', 'xcffib >= 1.5.0'],
    setup_requires=['setuptools_scm', 'cffi >= 1.1.0', 'xcffib >= 1.5.0'],
    packages=['cairocffi'],
    cffi_modules=['cairocffi/ffi_build.py:ffi'] if api_mode else []
)
