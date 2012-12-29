# coding: utf8
"""
    cairocffi
    ~~~~~~~~~

    cffi-based cairo bindings for Python. See README for details.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

import sys
from cffi import FFI

from .constants import _CAIRO_HEADERS
from .compat import FileNotFoundError


VERSION = '0.1'


ffi = FFI()
ffi.cdef(_CAIRO_HEADERS)
cairo = ffi.dlopen('cairo')


STATUS_TO_EXCEPTION = dict(
    NO_MEMORY=MemoryError,
    READ_ERROR=IOError,
    WRITE_ERRORS=IOError,
    TEMP_FILE_ERROR=IOError,
    FILE_NOT_FOUND=FileNotFoundError,
)


class CairoError(Exception):
    """Cairo returned an error status."""


def _check_status(status):
    if status != 'SUCCESS':
        exception = STATUS_TO_EXCEPTION.get(status, CairoError)
        raise exception('cairo returned %s: %s' % (
            status, ffi.string(cairo.cairo_status_to_string(status))))


def cairo_version():
    """Return the cairo version number a single integer."""
    return cairo.cairo_version()


def cairo_version_string():
    """Return the cairo version number a string."""
    return ffi.string(cairo.cairo_version_string()).decode('ascii')


def install_as_pycairo():
    """Install cairocffi so that ``import cairo`` imports it.

    cairoffi’s API is compatible with pycairo as much as possible.

    """
    sys.modules['cairo'] = sys.modules[__name__]


class Matrix(object):
    def __init__(self, xx=1, yx=0, xy=0, yy=1, x0=0, y0=0):
        self._struct = ffi.new('cairo_matrix_t *')
        cairo.cairo_matrix_init(self._struct, xx, yx, xy, yy, x0, y0)

    @classmethod
    def init_rotate(cls, radians):
        result = cls()
        cairo.cairo_matrix_init_rotate(result._struct, radians)
        return result

    def __getattr__(self, name):
        if name in ('xx', 'yx', 'xy', 'yy', 'x0', 'y0'):
            return getattr(self._struct, name)
        else:
            return object.__getattr__(self, name)

    def __setattr__(self, name, value):
        if name in ('xx', 'yx', 'xy', 'yy', 'x0', 'y0'):
            return setattr(self._struct, name, value)
        else:
            return object.__setattr__(self, name, value)

    def multiply(self, other):
        res = Matrix()
        cairo.cairo_matrix_multiply(res._struct, self._struct, other._struct)
        return res

    __mul__ = multiply

    def translate(self, tx, ty):
        cairo.cairo_matrix_translate(self._struct, tx, ty)

    def scale(self, sx, sy):
        cairo.cairo_matrix_scale(self._struct, sx, sy)

    def rotate(self, radians):
        cairo.cairo_matrix_rotate(self._struct, radians)

    def invert(self):
        _check_status(cairo.cairo_matrix_invert(self._struct))

    def transform_point(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_matrix_transform_point(self._struct, xy + 0, xy + 1)
        return tuple(xy)

    def transform_distance(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_matrix_transform_distance(self._struct, xy + 0, xy + 1)
        return tuple(xy)


from .surfaces import Surface, ImageSurface, PDFSurface, PSSurface, SVGSurface
from .patterns import Pattern, SurfacePattern
from .context import Context

# For compatibility with pycairo. In cairocffi users can just use strings.
from .constants import *
