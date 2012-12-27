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
        exception = STATUS_TO_EXCEPTION.get(status, Exception)
        raise exception('cairo returned %s: %s' % (
            status, ffi.string(cairo.cairo_status_to_string(status))))


def cairo_version():
    """Return the cairo version number a single integer."""
    return cairo.cairo_version()


def cairo_version_string():
    """Return the cairo version number a string."""
    return ffi.string(cairo.cairo_version_string()).decode('ascii')


def _make_read_func(file_obj):
    @ffi.callback("cairo_read_func_t", error='READ_ERROR')
    def read_func(closure, data, length):
        string = file_obj.read(length)
        if len(string) < length:  # EOF too early
            return 'READ_ERROR'
        ffi.buffer(data, length)[:len(string)] = string
        return 'SUCCESS'
    return read_func


def _make_write_func(file_obj):
    @ffi.callback("cairo_write_func_t", error='WRITE_ERROR')
    def read_func(_closure, data, length):
        file_obj.write(ffi.buffer(data, length))
        return 'SUCCESS'
    return read_func


def _encode_filename(filename):
    if not isinstance(filename, bytes):
        filename = filename.encode(sys.getfilesystemencoding())
    return ffi.new('char[]', filename)


class Surface(object):
    def __init__(self, handle):
        self._handle = handle
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_surface_status(self._handle))

    def write_to_png(self, target):
        if hasattr(target, 'write'):
            write_func = _make_write_func(target)
            _check_status(cairo.cairo_surface_write_to_png_stream(
                self._handle, write_func, ffi.NULL))
        else:
            _check_status(cairo.cairo_surface_write_to_png(
                self._handle, _encode_filename(target)))


class ImageSurface(Surface):
    def __init__(self, format, width, height):
        Surface.__init__(
            self, cairo.cairo_image_surface_create(format, width, height))

    @staticmethod
    def format_stride_for_width(format, width):
        return cairo.cairo_format_stride_for_width(format, width)

    @classmethod
    def create_from_png(cls, source):
        if hasattr(source, 'read'):
            read_func = _make_read_func(source)
            handle = cairo.cairo_image_surface_create_from_png_stream(
                read_func, ffi.NULL)
        else:
            handle = cairo.cairo_image_surface_create_from_png(
                _encode_filename(source))
        surface = Surface(handle)
        surface.__class__ = cls
        return surface

    def get_data(self):
        return ffi.buffer(
            cairo.cairo_image_surface_get_data(self._handle),
            size=self.get_stride() * self.get_height())

    def get_format(self):
        return cairo.cairo_image_surface_get_format(self._handle)

    def get_width(self):
        return cairo.cairo_image_surface_get_width(self._handle)

    def get_height(self):
        return cairo.cairo_image_surface_get_height(self._handle)

    def get_stride(self):
        return cairo.cairo_image_surface_get_stride(self._handle)


# For compatibility with pycairo. In cairocffi users can just use strings.
from .constants import *
