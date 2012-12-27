"""
    cairocffi
    ~~~~~~~~~

    cffi-based cairo bindings for Python. See README for details.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from cffi import FFI
from .constants import _CAIRO_HEADERS
from .constants import *


VERSION = '0.1'


ffi = FFI()
ffi.cdef(_CAIRO_HEADERS)
cairo_c = ffi.dlopen('cairo')


def cairo_version():
    """Return the cairo version number a single integer."""
    return cairo_c.cairo_version()


def cairo_version_string():
    """Return the cairo version number a string."""
    return ffi.string(cairo_c.cairo_version_string()).decode('ascii')
