from os import path
from setuptools import setup, find_packages
import io
import re
import sys


VERSION = re.search(
    "VERSION = '([^']+)'",
    io.open(
        path.join(path.dirname(__file__), 'cairocffi', '__init__.py'),
        encoding='utf-8',
    ).read().strip()
).group(1)

LONG_DESCRIPTION = io.open(
    path.join(path.dirname(__file__), 'README.rst'),
    encoding='utf-8',
).read()

needs_pytest = set(('pytest', 'test', 'ptr')).intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name='cairocffi',
    version=VERSION,
    url='https://github.com/SimonSapin/cairocffi',
    license='BSD',
    author='Simon Sapin',
    author_email='simon.sapin@exyr.org',
    description='cffi-based cairo bindings for Python',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics',
    ],
    packages=find_packages(),
    install_requires=['cffi>=1.1.0'],
    setup_requires=['cffi>=1.1.0'] + pytest_runner,
    cffi_modules=[
        'cairocffi/ffi_build.py:ffi',
        'cairocffi/ffi_build.py:ffi_pixbuf'
    ],
    tests_require=['pytest-runner', 'pytest-cov'],
    extras_require={
        'xcb': ['xcffib>=0.3.2'],
        'test': ['pytest-runner', 'pytest-cov'],
    },
)
