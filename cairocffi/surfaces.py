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
from .fonts import FontOptions, _encode_string


SURFACE_TARGET_KEY = ffi.new('cairo_user_data_key_t *')


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
    if file_obj is None:
        return ffi.NULL

    @ffi.callback("cairo_write_func_t", error='WRITE_ERROR')
    def read_func(_closure, data, length):
        file_obj.write(ffi.buffer(data, length))
        return 'SUCCESS'
    return read_func


def _encode_filename(filename):
    if not isinstance(filename, bytes):
        filename = filename.encode(sys.getfilesystemencoding())
    return ffi.new('char[]', filename)


def from_buffer(data):
    return ffi.cast(
        'char *', ctypes.addressof(ctypes.c_char.from_buffer(data)))


class KeepAlive(object):
    """
    Keep some objects alive until a callback is called.
    :attr:`closure` is a tuple of cairo_destroy_func_t and void* cdata objects,
    as expected by cairo_surface_set_mime_data().

    """
    instances = set()

    def __init__(self, *objects):
        self.objects = objects
        callback = ffi.callback(
            'cairo_destroy_func_t', lambda _: self.instances.remove(self))
        # cairo wants a non-NULL closure pointer.
        self.closure = (callback, callback)

    def save(self):
        self.instances.add(self)


class Surface(object):
    def __init__(self, pointer, target_keep_alive=None):
        self._pointer = ffi.gc(pointer, cairo.cairo_surface_destroy)
        self._check_status()
        if target_keep_alive not in (None, ffi.NULL):
            keep_alive = KeepAlive(target_keep_alive)
            _check_status(cairo.cairo_surface_set_user_data(
                self._pointer, SURFACE_TARGET_KEY, *keep_alive.closure))
            keep_alive.save()

    def _check_status(self):
        _check_status(cairo.cairo_surface_status(self._pointer))

    @staticmethod
    def _from_pointer(pointer):
        self = object.__new__(SURFACE_TYPE_TO_CLASS.get(
            cairo.cairo_surface_get_type(pointer), Surface))
        Surface.__init__(self, pointer)  # Skip the subclass’s __init__
        return self

    def copy_page(self):
        cairo.cairo_surface_copy_page(self._pointer)
        self._check_status()

    def show_page(self):
        cairo.cairo_surface_show_page(self._pointer)
        self._check_status()

    def create_similar(self, content, width, height):
        return Surface._from_pointer(cairo.cairo_surface_create_similar(
            self._pointer, content, width, height))

    def create_similar_image(self, content, width, height):
        return Surface._from_pointer(cairo.cairo_surface_create_similar_image(
            self._pointer, content, width, height))

    def create_for_rectangle(self, x, y, width, height):
        return Surface._from_pointer(cairo.cairo_surface_create_for_rectangle(
            self._pointer, x, y, width, height))

    def finish(self):
        cairo.cairo_surface_finish(self._pointer)
        self._check_status()

    def flush(self):
        cairo.cairo_surface_flush(self._pointer)
        self._check_status()

    def get_content(self):
        return cairo.cairo_surface_get_content(self._pointer)

    def get_device_offset(self):
        offsets = ffi.new('double[2]')
        cairo.cairo_surface_get_device_offset(
            self._pointer, offsets + 0, offsets + 1)
        return tuple(offsets)

    def set_device_offset(self, x_offset, y_offset):
        cairo.cairo_surface_set_device_offset(
            self._pointer, x_offset, y_offset)
        self._check_status()

    def get_fallback_resolution(self):
        ppi = ffi.new('double[2]')
        cairo.cairo_surface_get_fallback_resolution(
            self._pointer, ppi + 0, ppi + 1)
        return tuple(ppi)

    def set_fallback_resolution(self, x_pixels_per_inch, y_pixels_per_inch):
        cairo.cairo_surface_set_fallback_resolution(
            self._pointer, x_pixels_per_inch, y_pixels_per_inch)
        self._check_status()

    def get_font_options(self):
        font_options = FontOptions()
        cairo.cairo_surface_get_font_options(
            self._pointer, font_options._pointer)
        return font_options

    def get_mime_data(self, mime_type):
        buffer_address = ffi.new('unsigned char **')
        buffer_length = ffi.new('unsigned long *')
        mime_type = ffi.new('char[]', mime_type.encode('utf8'))
        cairo.cairo_surface_get_mime_data(
            self._pointer, mime_type, buffer_address, buffer_length)
        return (ffi.buffer(buffer_address[0], buffer_length[0])
                if buffer_address[0] != ffi.NULL else None)

    def set_mime_data(self, mime_type, data):
        mime_type = ffi.new('char[]', mime_type.encode('utf8'))
        if data is None:
            _check_status(cairo.cairo_surface_set_mime_data(
                self._pointer, mime_type, ffi.NULL, 0, ffi.NULL, ffi.NULL))
        else:
            keep_alive = KeepAlive(data, mime_type)
            _check_status(cairo.cairo_surface_set_mime_data(
                self._pointer, mime_type, from_buffer(data), len(data),
                *keep_alive.closure))
            keep_alive.save()  # Only on success

    def supports_mime_type(self, mime_type):
        mime_type = ffi.new('char[]', mime_type.encode('utf8'))
        return bool(cairo.cairo_surface_supports_mime_type(
            self._pointer, mime_type))

    def mark_dirty(self):
        cairo.cairo_surface_mark_dirty(self._pointer)
        self._check_status()

    def mark_dirty_rectangle(self, x, y, width, height):
        cairo.cairo_surface_mark_dirty_rectangle(
            self._pointer, x, y, width, height)
        self._check_status()

    def write_to_png(self, target):
        if hasattr(target, 'write'):
            write_func = _make_write_func(target)
            _check_status(cairo.cairo_surface_write_to_png_stream(
                self._pointer, write_func, ffi.NULL))
        else:
            _check_status(cairo.cairo_surface_write_to_png(
                self._pointer, _encode_filename(target)))


class ImageSurface(Surface):
    def __init__(self, format, width, height, data=None, stride=None):
        if data is None:
            pointer = cairo.cairo_image_surface_create(format, width, height)
        else:
            if stride is None:
                stride = self.format_stride_for_width(format, width)
            if len(data) < stride * height:
                raise ValueError('Got a %d bytes buffer, needs at least %d.'
                                 % (len(data), stride * height))
            self._data = data  # keep it alive
            data = from_buffer(data)
            pointer = cairo.cairo_image_surface_create_for_data(
                data, format, width, height, stride)
        Surface.__init__(self, pointer)

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
            pointer = cairo.cairo_image_surface_create_from_png_stream(
                read_func, ffi.NULL)
        else:
            pointer = cairo.cairo_image_surface_create_from_png(
                _encode_filename(source))
        self = object.__new__(ImageSurface)
        Surface.__init__(self, pointer)  # Skip ImageSurface.__init__
        return self

    def get_data(self):
        return ffi.buffer(
            cairo.cairo_image_surface_get_data(self._pointer),
            size=self.get_stride() * self.get_height())

    def get_format(self):
        return cairo.cairo_image_surface_get_format(self._pointer)

    def get_width(self):
        return cairo.cairo_image_surface_get_width(self._pointer)

    def get_height(self):
        return cairo.cairo_image_surface_get_height(self._pointer)

    def get_stride(self):
        return cairo.cairo_image_surface_get_stride(self._pointer)


class PDFSurface(Surface):
    def __init__(self, target, width_in_points, height_in_points):
        if hasattr(target, 'write') or target is None:
            write_func = _make_write_func(target)
            pointer = cairo.cairo_pdf_surface_create_for_stream(
                write_func, ffi.NULL, width_in_points, height_in_points)
        else:
            write_func = None
            pointer = cairo.cairo_pdf_surface_create(
                _encode_filename(target), width_in_points, height_in_points)
        Surface.__init__(self, pointer, target_keep_alive=write_func)

    def set_size(self, width_in_points, height_in_points):
        cairo.cairo_pdf_surface_set_size(
            self._pointer, width_in_points, height_in_points)
        self._check_status()

    def restrict_to_version(self, version):
        cairo.cairo_pdf_surface_restrict_to_version(self._pointer, version)
        self._check_status()

    @staticmethod
    def get_versions():
        versions = ffi.new('cairo_pdf_version_t const **')
        num_versions = ffi.new('int *')
        cairo.cairo_pdf_get_versions(versions, num_versions)
        versions = versions[0]
        return [versions[i] for i in range(num_versions[0])]

    @staticmethod
    def version_to_string(version):
        return ffi.string(
            cairo.cairo_pdf_version_to_string(version)).decode('ascii')


class PSSurface(Surface):
    def __init__(self, target, width_in_points, height_in_points):
        if hasattr(target, 'write') or target is None:
            write_func = _make_write_func(target)
            pointer = cairo.cairo_ps_surface_create_for_stream(
                write_func, ffi.NULL, width_in_points, height_in_points)
        else:
            write_func = None
            pointer = cairo.cairo_ps_surface_create(
                _encode_filename(target), width_in_points, height_in_points)
        Surface.__init__(self, pointer, target_keep_alive=write_func)

    def dsc_comment(self, comment):
        cairo.cairo_ps_surface_dsc_comment(
            self._pointer, _encode_string(comment))
        self._check_status()

    def dsc_begin_setup(self):
        cairo.cairo_ps_surface_dsc_begin_setup(self._pointer)
        self._check_status()

    def dsc_begin_page_setup(self):
        cairo.cairo_ps_surface_dsc_begin_page_setup(self._pointer)
        self._check_status()

    def get_eps(self):
        return bool(cairo.cairo_ps_surface_get_eps(self._pointer))

    def set_eps(self, eps):
        cairo.cairo_ps_surface_set_eps(self._pointer, bool(eps))
        self._check_status()

    def set_size(self, width_in_points, height_in_points):
        cairo.cairo_ps_surface_set_size(
            self._pointer, width_in_points, height_in_points)
        self._check_status()

    def restrict_to_level(self, level):
        cairo.cairo_ps_surface_restrict_to_level(self._pointer, level)
        self._check_status()

    @staticmethod
    def get_levels():
        levels = ffi.new('cairo_ps_level_t const **')
        num_levels = ffi.new('int *')
        cairo.cairo_ps_get_levels(levels, num_levels)
        levels = levels[0]
        return [levels[i] for i in range(num_levels[0])]

    @staticmethod
    def ps_level_to_string(level):
        return ffi.string(
            cairo.cairo_ps_level_to_string(level)).decode('ascii')


class SVGSurface(Surface):
    def __init__(self, target, width_in_points, height_in_points):
        if hasattr(target, 'write') or target is None:
            write_func = _make_write_func(target)
            pointer = cairo.cairo_svg_surface_create_for_stream(
                write_func, ffi.NULL, width_in_points, height_in_points)
        else:
            write_func = None
            pointer = cairo.cairo_svg_surface_create(
                _encode_filename(target), width_in_points, height_in_points)
        Surface.__init__(self, pointer, target_keep_alive=write_func)

    def restrict_to_version(self, version):
        cairo.cairo_svg_surface_restrict_to_version(self._pointer, version)
        self._check_status()

    @staticmethod
    def get_versions():
        versions = ffi.new('cairo_svg_version_t const **')
        num_versions = ffi.new('int *')
        cairo.cairo_svg_get_versions(versions, num_versions)
        versions = versions[0]
        return [versions[i] for i in range(num_versions[0])]

    @staticmethod
    def version_to_string(version):
        return ffi.string(
            cairo.cairo_svg_version_to_string(version)).decode('ascii')


SURFACE_TYPE_TO_CLASS = {
    'IMAGE': ImageSurface,
    'PDF': PDFSurface,
    'SVG': SVGSurface,
}
