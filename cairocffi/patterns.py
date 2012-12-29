"""
    cairocffi.patterns
    ~~~~~~~~~~~~~~~~~~

    Bindings for the various types of pattern objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status
from .surfaces import Surface


class Pattern(object):
    def __init__(self, handle):
        self._handle = ffi.gc(handle, cairo.cairo_pattern_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_pattern_status(self._handle))

    @staticmethod
    def _from_handle(handle):
        pattern = Pattern(handle)
        pattern_type = cairo.cairo_pattern_get_type(handle)
        if pattern_type in PATTERN_TYPE_TO_CLASS:
            pattern.__class__ = PATTERN_TYPE_TO_CLASS[pattern_type]
        return pattern

    def set_extend(self, extend):
        cairo.cairo_pattern_set_extend(self._handle, extend)
        self._check_status()

    def get_extend(self):
        return cairo.cairo_pattern_get_extend(self._handle)

    # pycairo only has filters on SurfacePattern,
    # but cairo seems to accept it on any pattern.
    def set_filter(self, filter):
        cairo.cairo_pattern_set_filter(self._handle, filter)
        self._check_status()

    def get_filter(self):
        return cairo.cairo_pattern_get_filter(self._handle)


class SurfacePattern(Pattern):
    def __init__(self, surface):
        Pattern.__init__(
            self, cairo.cairo_pattern_create_for_surface(surface._handle))

    def get_surface(self):
        surface_p = ffi.new('cairo_surface_t **')
        _check_status(cairo.cairo_pattern_get_surface(self._handle, surface_p))
        surface = Surface._from_handle(surface_p[0])
        cairo.cairo_surface_reference(surface_p[0])
        return surface


PATTERN_TYPE_TO_CLASS = dict(
    SURFACE=SurfacePattern,
)
