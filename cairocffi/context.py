"""
    cairocffi.context
    ~~~~~~~~~~~~~~~~~

    Bindings for Context objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status


class Context(object):
    def __init__(self, surface):
        handle = cairo.cairo_create(surface._handle)
        _check_status(cairo.cairo_status(handle))
        self._handle = ffi.gc(handle, cairo.cairo_destroy)

    def paint(self):
        cairo.cairo_paint(self._handle)
