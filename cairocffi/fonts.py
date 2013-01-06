# coding: utf8
"""
    cairocffi.fonts
    ~~~~~~~~~~~~~~~

    Bindings for font-related objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status, Matrix
from .compat import xrange


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

    @staticmethod
    def _from_pointer(pointer, incref):
        """Wrap an existing :c:type:`cairo_font_face_t *` cdata pointer.

        :type incref: bool
        :param incref:
            Whether increase the :ref:`reference count <refcounting>` now.
        :return:
            A new instance of :class:`FontFace` or one of its sub-classes,
            depending on the face’s type.

        """
        if pointer == ffi.NULL:
            raise ValueError('Null pointer')
        if incref:
            cairo.cairo_font_face_reference(pointer)
        self = object.__new__(FONT_TYPE_TO_CLASS.get(
            cairo.cairo_font_face_get_type(pointer), FontFace))
        FontFace.__init__(self, pointer)  # Skip the subclass’s __init__
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


class ScaledFont(object):
    def __init__(self, font_face, font_matrix=None, ctm=None, options=None):
        if font_matrix is None:
            font_matrix = Matrix()
            font_matrix.scale(10)  # Default font size
        if ctm is None:
            ctm = Matrix()
        if options is None:
            options = FontOptions()
        self._init_pointer(cairo.cairo_scaled_font_create(
            font_face._pointer, font_matrix._pointer,
            ctm._pointer, options._pointer))

    def _init_pointer(self, pointer):
        self._pointer = ffi.gc(pointer, cairo.cairo_scaled_font_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_scaled_font_status(self._pointer))

    @staticmethod
    def _from_pointer(pointer, incref):
        """Wrap an existing :c:type:`cairo_scaled_font_t *` cdata pointer.

        :type incref: bool
        :param incref:
            Whether increase the :ref:`reference count <refcounting>` now.
        :return: A new :class:`ScaledFont` instance.

        """
        if pointer == ffi.NULL:
            raise ValueError('Null pointer')
        if incref:
            cairo.cairo_scaled_font_reference(pointer)
        self = object.__new__(ScaledFont)
        ScaledFont._init_pointer(self, pointer)
        return self

    def get_font_face(self):
        return FontFace._from_pointer(
            cairo.cairo_scaled_font_get_font_face(self._pointer), incref=True)

    def get_font_options(self):
        font_options = FontOptions()
        cairo.cairo_scaled_font_get_font_options(
            self._pointer, font_options._pointer)
        return font_options

    def get_font_matrix(self):
        matrix = Matrix()
        cairo.cairo_scaled_font_get_font_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def get_ctm(self):
        matrix = Matrix()
        cairo.cairo_scaled_font_get_ctm(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def get_scale_matrix(self):
        matrix = Matrix()
        cairo.cairo_scaled_font_get_scale_matrix(
            self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def extents(self):
        extents = ffi.new('cairo_font_extents_t *')
        cairo.cairo_scaled_font_extents(self._pointer, extents)
        self._check_status()
        return (
            extents.ascent, extents.descent, extents.height,
            extents.max_x_advance, extents.max_y_advance)

    def text_extents(self, text):
        extents = ffi.new('cairo_text_extents_t *')
        cairo.cairo_scaled_font_text_extents(
            self._pointer, _encode_string(text), extents)
        self._check_status()
        return (
            extents.x_bearing, extents.y_bearing,
            extents.width, extents.height,
            extents.x_advance, extents.y_advance)

    def glyph_extents(self, glyphs):
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        extents = ffi.new('cairo_text_extents_t *')
        cairo.cairo_scaled_font_glyph_extents(
            self._pointer, glyphs, len(glyphs), extents)
        self._check_status()
        return (
            extents.x_bearing, extents.y_bearing,
            extents.width, extents.height,
            extents.x_advance, extents.y_advance)

    def text_to_glyphs(self, x, y, text):
        glyphs = ffi.new('cairo_glyph_t **', ffi.NULL)
        clusters = ffi.new('cairo_text_cluster_t **', ffi.NULL)
        num_glyphs = ffi.new('int *')
        num_clusters = ffi.new('int *')
        cluster_flags = ffi.new('cairo_text_cluster_flags_t *')
        # TODO: Pass len_utf8 explicitly to support NULL bytes?
        status = cairo.cairo_scaled_font_text_to_glyphs(
            self._pointer, x, y, _encode_string(text), -1,
            glyphs, num_glyphs, clusters, num_clusters, cluster_flags)
        glyphs = ffi.gc(glyphs[0], cairo.cairo_glyph_free)
        clusters = ffi.gc(clusters[0], cairo.cairo_text_cluster_free)
        _check_status(status)
        glyphs = [
            (glyph.index, glyph.x, glyph.y)
            for i in xrange(num_glyphs[0])
            for glyph in [glyphs[i]]]
        clusters = [
            (cluster.num_bytes, cluster.num_glyphs)
            for i in xrange(num_clusters[0])
            for cluster in [clusters[i]]]
        # Intentionally trigger a KeyError on unknown flags
        is_backwards = {'BACKWARDS': True, '#0': False}[cluster_flags[0]]
        return glyphs, clusters, is_backwards


class FontOptions(object):
    def __init__(self, **values):
        self._init_pointer(cairo.cairo_font_options_create())
        for name, value in values.items():
            getattr(self, 'set_' + name)(value)

    def _init_pointer(self, pointer):
        self._pointer = ffi.gc(pointer, cairo.cairo_font_options_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_font_options_status(self._pointer))

    def copy(self):
        cls = type(self)
        other = object.__new__(cls)
        cls._init_pointer(other, cairo.cairo_font_options_copy(self._pointer))
        return other

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
