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
from .compat import FileNotFoundError, xrange


VERSION = '0.1'


ffi = FFI()
ffi.cdef(_CAIRO_HEADERS)
cairo = ffi.dlopen('cairo')


class CairoError(Exception):
    """Cairo returned an error status."""


Error = CairoError  # pycairo compat

STATUS_TO_EXCEPTION = dict(
    NO_MEMORY=MemoryError,
    READ_ERROR=IOError,
    WRITE_ERRORS=IOError,
    TEMP_FILE_ERROR=IOError,
    FILE_NOT_FOUND=FileNotFoundError,
)


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
        self._pointer = ffi.new('cairo_matrix_t *')
        cairo.cairo_matrix_init(self._pointer, xx, yx, xy, yy, x0, y0)

    @classmethod
    def init_rotate(cls, radians):
        result = cls()
        cairo.cairo_matrix_init_rotate(result._pointer, radians)
        return result

    def __getattr__(self, name):
        if name in ('xx', 'yx', 'xy', 'yy', 'x0', 'y0'):
            return getattr(self._pointer, name)
        else:
            return object.__getattr__(self, name)

    def __setattr__(self, name, value):
        if name in ('xx', 'yx', 'xy', 'yy', 'x0', 'y0'):
            return setattr(self._pointer, name, value)
        else:
            return object.__setattr__(self, name, value)

    def as_tuple(self):
        return (self.xx, self.yx,  self.xy, self.yy,  self.x0, self.y0)

    def copy(self):
        return type(self)(*self.as_tuple())

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __ne__(self, other):
        return self.as_tuple() != other.as_tuple()

    def multiply(self, other):
        res = Matrix()
        cairo.cairo_matrix_multiply(res._pointer, self._pointer, other._pointer)
        return res

    __mul__ = multiply

    def translate(self, tx, ty):
        cairo.cairo_matrix_translate(self._pointer, tx, ty)

    def scale(self, sx, sy):
        cairo.cairo_matrix_scale(self._pointer, sx, sy)

    def rotate(self, radians):
        cairo.cairo_matrix_rotate(self._pointer, radians)

    def invert(self):
        _check_status(cairo.cairo_matrix_invert(self._pointer))

    def inverted(self):
        matrix = self.copy()
        matrix.invert()
        return matrix

    def transform_point(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_matrix_transform_point(self._pointer, xy + 0, xy + 1)
        return tuple(xy)

    def transform_distance(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_matrix_transform_distance(self._pointer, xy + 0, xy + 1)
        return tuple(xy)


class Path(object):
    def __init__(self, handle):
        self._pointer = ffi.gc(handle, cairo.cairo_path_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(self._pointer.status)

    def __iter__(self):
        data = self._pointer.data
        num_data = self._pointer.num_data
        position = 0
        length_per_type = {
            'MOVE_TO': 1,
            'LINE_TO': 1,
            'CURVE_TO': 3,
            'CLOSE_PATH': 0}
        while position < num_data:
            path_data = data[position]
            path_type = path_data.header.type
            points = ()
            for i in xrange(length_per_type[path_type]):
                point = data[position + i + 1].point
                points += (point.x, point.y)
            yield (path_type, points)
            position += path_data.header.length


from .surfaces import Surface, ImageSurface, PDFSurface, PSSurface, SVGSurface
from .patterns import (Pattern, SolidPattern, SurfacePattern,
                       Gradient, LinearGradient, RadialGradient)
from .context import Context

# For compatibility with pycairo. In cairocffi users can just use strings.
from .constants import *
