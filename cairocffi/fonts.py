"""
    cairocffi.fonts
    ~~~~~~~~~~~~~~~

    Bindings for font-related objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status


def _encode_string(string):
    if not isinstance(string, bytes):
        string = string.encode('utf8')
    return ffi.new('char[]', string)


class FontFace(object):
    def __init__(self, pointer):
        self._pointer = ffi.gc(pointer, cairo.cairo_font_face_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_font_face_status(self._pointer))

    @classmethod
    def _from_pointer(cls, pointer):
        self = object.__new__(FONT_TYPE_TO_CLASS.get(
            cairo.cairo_font_face_get_type(pointer), cls))
        cls.__init__(self, pointer)  # Skip the subclass’s __init__
        return self


class ToyFontFace(FontFace):
    def __init__(self, family='', slant='NORMAL', weight='NORMAL'):
        FontFace.__init__(self, cairo.cairo_toy_font_face_create(
            _encode_string(family), slant, weight))

    def get_family(self):
        return ffi.string(cairo.cairo_toy_font_face_get_family(
            self._pointer)).decode('utf8', 'replace')

    def get_slant(self):
        return cairo.cairo_toy_font_face_get_slant(self._pointer)

    def get_weight(self):
        return cairo.cairo_toy_font_face_get_weight(self._pointer)


FONT_TYPE_TO_CLASS = {
    'TOY': ToyFontFace,
}




class FontOptions(object):
    def __init__(self, _pointer=None, **values):
        if _pointer is None:
            _pointer = cairo.cairo_font_options_create()
        self._pointer = ffi.gc(_pointer, cairo.cairo_font_options_destroy)
        self._check_status()
        for name, value in values.items():
            getattr(self, 'set_' + name)(value)

    def _check_status(self):
        _check_status(cairo.cairo_font_options_status(self._pointer))

    def copy(self):
        return type(self)(cairo.cairo_font_options_copy(self._pointer))

    def merge(self, other):
        cairo.cairo_font_options_merge(self._pointer, other._pointer)
        _check_status(cairo.cairo_font_options_status(self._pointer))

    def __hash__(self):
        return cairo.cairo_font_options_hash(self._pointer)

    def __eq__(self, other):
        return cairo.cairo_font_options_equal(self._pointer, other._pointer)

    def __ne__(self, other):
        return not self == other

    equal = __eq__
    hash = __hash__

    def set_antialias(self, antialias):
        cairo.cairo_font_options_set_antialias(self._pointer, antialias)
        self._check_status()

    def get_antialias(self):
        return cairo.cairo_font_options_get_antialias(self._pointer)

    def set_subpixel_order(self, subpixel_order):
        cairo.cairo_font_options_set_subpixel_order(
            self._pointer, subpixel_order)
        self._check_status()

    def get_subpixel_order(self):
        return cairo.cairo_font_options_get_subpixel_order(self._pointer)

    def set_hint_style(self, hint_style):
        cairo.cairo_font_options_set_hint_style(self._pointer, hint_style)
        self._check_status()

    def get_hint_style(self):
        return cairo.cairo_font_options_get_hint_style(self._pointer)

    def set_hint_metrics(self, hint_metrics):
        cairo.cairo_font_options_set_hint_metrics(self._pointer, hint_metrics)
        self._check_status()

    def get_hint_metrics(self):
        return cairo.cairo_font_options_get_hint_metrics(self._pointer)
