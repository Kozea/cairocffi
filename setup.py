import sys

from setuptools import setup

if sys.version_info.major < 3:
    raise RuntimeError(
        'cairocffi does not support Python 2.x anymore. '
        'Please use Python 3 or install an older version of cairocffi.')

setup(
    cffi_modules=[
        'cairocffi/ffi_build.py:ffi',
        'cairocffi/ffi_build.py:ffi_pixbuf']
)
