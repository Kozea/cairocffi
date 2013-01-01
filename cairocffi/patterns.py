# coding: utf8
"""
    cairocffi.patterns
    ~~~~~~~~~~~~~~~~~~

    Bindings for the various types of pattern objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status, Matrix
from .surfaces import Surface
from .compat import xrange


class Pattern(object):
    def __init__(self, pointer):
        self._pointer = ffi.gc(pointer, cairo.cairo_pattern_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_pattern_status(self._pointer))

    @classmethod
    def _from_pointer(cls, pointer):
        self = object.__new__(PATTERN_TYPE_TO_CLASS.get(
            cairo.cairo_pattern_get_type(pointer), cls))
        cls.__init__(self, pointer)  # Skip the subclass’s __init__
        return self

    def set_extend(self, extend):
        cairo.cairo_pattern_set_extend(self._pointer, extend)
        self._check_status()

    def get_extend(self):
        return cairo.cairo_pattern_get_extend(self._pointer)

    # pycairo only has filters on SurfacePattern,
    # but cairo seems to accept it on any pattern.
    def set_filter(self, filter):
        cairo.cairo_pattern_set_filter(self._pointer, filter)
        self._check_status()

    def get_filter(self):
        return cairo.cairo_pattern_get_filter(self._pointer)

    def get_matrix(self):
        matrix = Matrix()
        cairo.cairo_pattern_get_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def set_matrix(self, matrix):
        cairo.cairo_pattern_set_matrix(self._pointer, matrix._pointer)
        self._check_status()


class SolidPattern(Pattern):
    def __init__(self, red, green, blue, alpha=1):
        Pattern.__init__(
            self, cairo.cairo_pattern_create_rgba(red, green, blue, alpha))

    def get_rgba(self):
        rgba = ffi.new('double[4]')
        _check_status(cairo.cairo_pattern_get_rgba(
            self._pointer, rgba + 0, rgba + 1, rgba + 2, rgba + 3))
        return tuple(rgba)


class SurfacePattern(Pattern):
    def __init__(self, surface):
        Pattern.__init__(
            self, cairo.cairo_pattern_create_for_surface(surface._pointer))

    def get_surface(self):
        surface_p = ffi.new('cairo_surface_t **')
        _check_status(cairo.cairo_pattern_get_surface(
            self._pointer, surface_p))
        surface = Surface._from_pointer(surface_p[0])
        cairo.cairo_surface_reference(surface_p[0])
        return surface


class Gradient(Pattern):
    def add_color_stop_rgb(self, offset, red, green, blue):
        cairo.cairo_pattern_add_color_stop_rgb(
            self._pointer, offset, red, green, blue)
        self._check_status()

    def add_color_stop_rgba(self, offset, red, green, blue, alpha):
        cairo.cairo_pattern_add_color_stop_rgba(
            self._pointer, offset, red, green, blue, alpha)
        self._check_status()

    def get_color_stops(self):
        count = ffi.new('int *')
        _check_status(cairo.cairo_pattern_get_color_stop_count(
            self._pointer, count))
        stops = []
        stop = ffi.new('double[5]')
        for i in xrange(count[0]):
            _check_status(cairo.cairo_pattern_get_color_stop_rgba(
                self._pointer, i,
                stop + 0, stop + 1, stop + 2, stop + 3, stop + 4))
            stops.append(tuple(stop))
        return stops


class LinearGradient(Gradient):
    def __init__(self, x0, y0, x1, y1):
        Pattern.__init__(
            self, cairo.cairo_pattern_create_linear(x0, y0, x1, y1))

    def get_linear_points(self):
        points = ffi.new('double[4]')
        _check_status(cairo.cairo_pattern_get_linear_points(
            self._pointer, points + 0, points + 1, points + 2, points + 3))
        return tuple(points)


class RadialGradient(Gradient):
    def __init__(self, cx0, cy0, radius0, cx1, cy1, radius1):
        Pattern.__init__(self, cairo.cairo_pattern_create_radial(
            cx0, cy0, radius0, cx1, cy1, radius1))

    def get_radial_circles(self):
        circles = ffi.new('double[6]')
        _check_status(cairo.cairo_pattern_get_radial_circles(
            self._pointer,  circles + 0, circles + 1, circles + 2,
            circles + 3, circles + 4, circles + 5))
        return tuple(circles)


PATTERN_TYPE_TO_CLASS = {
    'SOLID': SolidPattern,
    'SURFACE': SurfacePattern,
    'LINEAR': LinearGradient,
    'RADIAL': RadialGradient,
}
