from setuptools import setup, find_packages
from os import path
import re
import io
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

if '_cffi_backend' in sys.builtin_module_names:
    import _cffi_backend
    requires_cffi = "cffi==" + _cffi_backend.__version__
else:
    requires_cffi = "cffi>=1.1.0"

# PyPy < 2.6 compatibility
if requires_cffi.startswith("cffi==0."):
    cffi_args = dict()
else:
    cffi_args = dict(cffi_modules=[
        'cairocffi/ffi_build.py:ffi',
        'cairocffi/ffi_build.py:ffi_pixbuf'
    ])

try:
    import cffi
    if cffi.__version__.startswith('0.'):
        # https://github.com/SimonSapin/cairocffi/issues/64
        cffi_args = dict()
except ImportError:
    pass

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
    install_requires=[requires_cffi],
    setup_requires=[requires_cffi],
    extras_require={'xcb': ['xcffib>=0.3.2']},
    **cffi_args
)
