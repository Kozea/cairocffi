"""
    cairocffi.surface
    ~~~~~~~~~~~~~~~~~

    Bindings for the various types of surface objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

import sys
import ctypes

from . import ffi, cairo, _check_status


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
        _check_status(cairo.cairo_surface_status(handle))
        self._handle = ffi.gc(handle, cairo.cairo_surface_destroy)

    def copy_page(self):
        raise NotImplementedError

    def show_page(self):
        raise NotImplementedError

    def create_similar(self, content, width, height):
        raise NotImplementedError

    def finish(self):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def get_content(self):
        raise NotImplementedError

    def get_device_offset(self):
        raise NotImplementedError

    def set_device_offset(self, x_offset, y_offset):
        raise NotImplementedError

    def get_fallback_resolution(self):
        raise NotImplementedError

    def set_fallback_resolution(self, x_pixels_per_inch, y_pixels_per_inch):
        raise NotImplementedError

    def get_font_options(self):
        raise NotImplementedError

    def get_mime_data(self, mime_type):
        raise NotImplementedError

    def set_mime_data(self, mime_type, data):
        raise NotImplementedError

    def set_supports_mime_type(self, mime_type):
        raise NotImplementedError

    def mark_dirty(self):
        raise NotImplementedError

    def mark_dirty_rectangle(self, x, y, width, height):
        raise NotImplementedError

    def write_to_png(self, target):
        if hasattr(target, 'write'):
            write_func = _make_write_func(target)
            _check_status(cairo.cairo_surface_write_to_png_stream(
                self._handle, write_func, ffi.NULL))
        else:
            _check_status(cairo.cairo_surface_write_to_png(
                self._handle, _encode_filename(target)))


class ImageSurface(Surface):
    def __init__(self, format, width, height, data=None, stride=None):
        if data is None:
            handle = cairo.cairo_image_surface_create(format, width, height)
        else:
            if stride is None:
                stride = self.format_stride_for_width(format, width)
            self._data = data  # keep it alive
            data = ffi.cast(
                'char *', ctypes.addressof(ctypes.c_char.from_buffer(data)))
            handle = cairo.cairo_image_surface_create_for_data(
                data, format, width, height, stride)
        Surface.__init__(self, handle)

    @staticmethod
    def format_stride_for_width(format, width):
        return cairo.cairo_format_stride_for_width(format, width)

    @classmethod
    def create_for_data(cls, data, format, width, height, stride=None):
        return cls(format, width, height, data, stride)

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
        # XXX is there a cleaner way to bypass ImageSurface.__init__?
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
