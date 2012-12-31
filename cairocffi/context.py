"""
    cairocffi.context
    ~~~~~~~~~~~~~~~~~

    Bindings for Context objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status, Matrix, Path
from .patterns import Pattern
from .surfaces import Surface, _encode_string
from .fonts import FontOptions
from .compat import xrange


class Context(object):
    def __init__(self, surface):
        self._pointer = ffi.gc(
            cairo.cairo_create(surface._pointer), cairo.cairo_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_status(self._pointer))

    def get_target(self):
        return Surface._from_pointer(cairo.cairo_surface_reference(
            cairo.cairo_get_target(self._pointer)))

    def save(self):
        cairo.cairo_save(self._pointer)
        self._check_status()

    def restore(self):
        cairo.cairo_restore(self._pointer)
        self._check_status()

    def __enter__(self):
        self.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore()

    def push_group(self):
        cairo.cairo_push_group(self._pointer)
        self._check_status()

    def push_group_with_content(self, content):
        cairo.cairo_push_group_with_content(self._pointer, content)
        self._check_status()

    def pop_group(self):
        return Pattern._from_pointer(cairo.cairo_pop_group(self._pointer))

    def pop_group_to_source(self):
        cairo.cairo_pop_group_to_source(self._pointer)
        self._check_status()

    def get_group_target(self):
        return Surface._from_pointer(cairo.cairo_surface_reference(
            cairo.cairo_get_group_target(self._pointer)))

    def translate(self, tx, ty):
        cairo.cairo_translate(self._pointer, tx, ty)
        self._check_status()

    def scale(self, sx, sy):
        cairo.cairo_scale(self._pointer, sx, sy)
        self._check_status()

    def rotate(self, radians):
        cairo.cairo_rotate(self._pointer, radians)
        self._check_status()

    def transform(self, matrix):
        cairo.cairo_transform(self._pointer, matrix._pointer)
        self._check_status()

    def get_matrix(self):
        matrix = Matrix()
        cairo.cairo_get_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def set_matrix(self, matrix):
        cairo.cairo_set_matrix(self._pointer, matrix._pointer)
        self._check_status()

    def identity_matrix(self):
        cairo.cairo_identity_matrix(self._pointer)
        self._check_status()

    def arc(self, xc, yc, radius, angle1, angle2):
        cairo.cairo_arc(self._pointer, xc, yc, radius, angle1, angle2)
        self._check_status()

    def arc_negative(self, xc, yc, radius, angle1, angle2):
        cairo.cairo_arc_negative(self._pointer, xc, yc, radius, angle1, angle2)
        self._check_status()

    def rectangle(self, x, y, width, height):
        cairo.cairo_rectangle(self._pointer, x, y, width, height)
        self._check_status()

    def move_to(self, x, y):
        cairo.cairo_move_to(self._pointer, x, y)
        self._check_status()

    def rel_move_to(self, dx, dy):
        cairo.cairo_rel_move_to(self._pointer, dx, dy)
        self._check_status()

    def line_to(self, x, y):
        cairo.cairo_line_to(self._pointer, x, y)
        self._check_status()

    def rel_line_to(self, dx, dy):
        cairo.cairo_rel_line_to(self._pointer, dx, dy)
        self._check_status()

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        cairo.cairo_curve_to(self._pointer, x1, y1, x2, y2, x3, y3)
        self._check_status()

    def rel_curve_to(self, dx1, dy1, dx2, dy2, dx3, dy3):
        cairo.cairo_rel_curve_to(self._pointer, dx1, dy1, dx2, dy2, dx3, dy3)
        self._check_status()

    def close_path(self):
        cairo.cairo_close_path(self._pointer)
        self._check_status()

    def copy_path(self):
        return Path(cairo.cairo_copy_path(self._pointer))

    def copy_path_flat(self):
        return Path(cairo.cairo_copy_path_flat(self._pointer))

    def append_path(self, path):
        cairo.cairo_append_path(self._pointer, path._pointer)
        self._check_status()

    def path_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_path_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def new_path(self):
        cairo.cairo_new_path(self._pointer)
        self._check_status()

    def new_sub_path(self):
        cairo.cairo_new_sub_path(self._pointer)
        self._check_status()

    def get_current_point(self):
        if self.has_current_point():
            xy = ffi.new('double[2]')
            cairo.cairo_get_current_point(self._pointer, xy + 0, xy + 1)
            self._check_status()
            return tuple(xy)

    def has_current_point(self):
        return bool(cairo.cairo_has_current_point(self._pointer))

    def set_dash(self, dashes, offset=0):
        cairo.cairo_set_dash(
            self._pointer, ffi.new('double[]', dashes), len(dashes), offset)
        self._check_status()

    def set_antialias(self, antialias):
        cairo.cairo_set_antialias(self._pointer, antialias)
        self._check_status()

    def get_antialias(self):
        return cairo.cairo_get_antialias(self._pointer)

    def get_dash(self):
        dashes = ffi.new('double[]', cairo.cairo_get_dash_count(self._pointer))
        offset = ffi.new('double *')
        cairo.cairo_get_dash(self._pointer, dashes, offset)
        self._check_status()
        return list(dashes), offset[0]

    def get_dash_count(self):
        # Not really useful with get_dash() returning a list,
        # but retained for compatibility with pycairo.
        return cairo.cairo_get_dash_count(self._pointer)

    def set_fill_rule(self, fill_rule):
        cairo.cairo_set_fill_rule(self._pointer, fill_rule)
        self._check_status()

    def get_fill_rule(self):
        return cairo.cairo_get_fill_rule(self._pointer)

    def set_line_cap(self, line_cap):
        cairo.cairo_set_line_cap(self._pointer, line_cap)
        self._check_status()

    def get_line_cap(self):
        return cairo.cairo_get_line_cap(self._pointer)

    def set_line_join(self, line_join):
        cairo.cairo_set_line_join(self._pointer, line_join)
        self._check_status()

    def get_line_join(self):
        return cairo.cairo_get_line_join(self._pointer)

    def set_line_width(self, width):
        cairo.cairo_set_line_width(self._pointer, width)
        self._check_status()

    def get_line_width(self):
        return cairo.cairo_get_line_width(self._pointer)

    def set_miter_limit(self, miter_limit):
        cairo.cairo_set_miter_limit(self._pointer, miter_limit)
        self._check_status()

    def get_miter_limit(self):
        return cairo.cairo_get_miter_limit(self._pointer)

    def set_operator(self, operator):
        cairo.cairo_set_operator(self._pointer, operator)
        self._check_status()

    def get_operator(self):
        return cairo.cairo_get_operator(self._pointer)

    def set_tolerance(self, tolerance):
        cairo.cairo_set_tolerance(self._pointer, tolerance)
        self._check_status()

    def get_tolerance(self):
        return cairo.cairo_get_tolerance(self._pointer)

    def paint(self):
        cairo.cairo_paint(self._pointer)
        self._check_status()

    def paint_with_alpha(self, alpha):
        cairo.cairo_paint_with_alpha(self._pointer, alpha)
        self._check_status()

    def fill(self):
        cairo.cairo_fill(self._pointer)
        self._check_status()

    def fill_preserve(self):
        cairo.cairo_fill_preserve(self._pointer)
        self._check_status()

    def fill_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_fill_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def in_fill(self, x, y):
        return bool(cairo.cairo_in_fill(self._pointer, x, y))

    def stroke(self):
        cairo.cairo_stroke(self._pointer)
        self._check_status()

    def stroke_preserve(self):
        cairo.cairo_stroke_preserve(self._pointer)
        self._check_status()

    def stroke_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_stroke_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def in_stroke(self, x, y):
        return bool(cairo.cairo_in_stroke(self._pointer, x, y))

    def clip(self):
        cairo.cairo_clip(self._pointer)
        self._check_status()

    def clip_preserve(self):
        cairo.cairo_clip_preserve(self._pointer)
        self._check_status()

    def clip_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_clip_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def copy_clip_rectangle_list(self):
        rectangle_list = cairo.cairo_copy_clip_rectangle_list(self._pointer)
        _check_status(rectangle_list.status)
        rectangles = rectangle_list.rectangles
        result = []
        for i in xrange(rectangle_list.num_rectangles):
            rect = rectangles[i]
            result.append((rect.x, rect.y, rect.width, rect.height))
        cairo.cairo_rectangle_list_destroy(rectangle_list)
        return result

    def in_clip(self, x, y):
        return bool(cairo.cairo_in_clip(self._pointer, x, y))

    def reset_clip(self):
        cairo.cairo_reset_clip(self._pointer)
        self._check_status()

    def mask(self, pattern):
        cairo.cairo_mask(self._pointer, pattern._pointer)
        self._check_status()

    def mask_surface(self, surface, surface_x=0, surface_y=0):
        cairo.cairo_mask_surface(
            self._pointer, surface._pointer, surface_x, surface_y)
        self._check_status()

    def set_source_rgb(self, r, g, b):
        cairo.cairo_set_source_rgb(self._pointer, r, g, b)
        self._check_status()

    def set_source_rgba(self, r, g, b, a=1):
        cairo.cairo_set_source_rgba(self._pointer, r, g, b, a)
        self._check_status()

    def set_source_surface(self, surface, x=0, y=0):
        cairo.cairo_set_source_surface(self._pointer, surface._pointer, x, y)
        self._check_status()

    def set_source(self, source):
        cairo.cairo_set_source(self._pointer, source._pointer)
        self._check_status()

    def get_source(self):
        return Pattern._from_pointer(cairo.cairo_pattern_reference(
            cairo.cairo_get_source(self._pointer)))

    def user_to_device(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_user_to_device(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def user_to_device_distance(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_user_to_device_distance(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def device_to_user(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_device_to_user(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def device_to_user_distance(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_device_to_user_distance(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def select_font_face(self, family, slant='NORMAL', weight='NORMAL'):
        cairo.cairo_select_font_face(
            self._pointer, _encode_string(family), slant, weight)
        self._check_status()

    def get_font_options(self):
        font_options = FontOptions()
        cairo.cairo_get_font_options(self._pointer, font_options._pointer)
        return font_options

    def set_font_options(self, font_options):
        cairo.cairo_set_font_options(self._pointer, font_options._pointer)
        self._check_status()

    def get_font_matrix(self):
        matrix = Matrix()
        cairo.cairo_get_font_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def set_font_matrix(self, matrix):
        cairo.cairo_set_font_matrix(self._pointer, matrix._pointer)
        self._check_status()

    def set_font_size(self, size):
        cairo.cairo_set_font_size(self._pointer, size)
        self._check_status()

    def font_extents(self):
        extents = ffi.new('cairo_font_extents_t *')
        cairo.cairo_font_extents(self._pointer, extents)
        self._check_status()
        # returning extents as is would be a nice API,
        # but return a tuple for compat with pycairo.
        return (
            extents.ascent, extents.descent, extents.height,
            extents.max_x_advance, extents.max_y_advance)

    def text_extents(self, text):
        extents = ffi.new('cairo_text_extents_t *')
        cairo.cairo_text_extents(self._pointer, _encode_string(text), extents)
        self._check_status()
        # returning extents as is would be a nice API,
        # but return a tuple for compat with pycairo.
        return (
            extents.x_bearing, extents.y_bearing,
            extents.width, extents.height,
            extents.x_advance, extents.y_advance)

    def text_path(self, text):
        cairo.cairo_text_path(self._pointer, _encode_string(text))
        self._check_status()

    def show_text(self, text):
        cairo.cairo_show_text(self._pointer, _encode_string(text))
        self._check_status()

    def show_page(self):
        cairo.cairo_show_page(self._pointer)
        self._check_status()

    def copy_page(self):
        cairo.cairo_copy_page(self._pointer)
        self._check_status()
