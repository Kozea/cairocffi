import os
import sys

from setuptools import setup


VERSION_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cairocffi", "VERSION")
with open(VERSION_FILE, "r") as fd:
    version = fd.read().strip()


if sys.version_info.major < 3:
    raise RuntimeError(
        'cairocffi does not support Python 2.x anymore. '
        'Please use Python 3 or install an older version of cairocffi.')

setup(
    version=version,
    cffi_modules=[
        'cairocffi/ffi_build.py:ffi',
        'cairocffi/ffi_build.py:ffi_pixbuf']
)
