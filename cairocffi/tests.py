# coding: utf8
"""
    cairocffi.tests
    ~~~~~~~~~~~~~~~

    Test suite for cairocffi.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

import io
import re
import os
import sys
import math
import base64
import shutil
import tempfile
import contextlib

import pytest

import cairocffi
from . import (cairo_version, cairo_version_string, Context, Matrix,
               Surface, ImageSurface, PDFSurface, PSSurface, SVGSurface,
               Pattern, SolidPattern, SurfacePattern,
               LinearGradient, RadialGradient,
               FontFace, ToyFontFace, ScaledFont, FontOptions)
from .compat import u, pixel


@contextlib.contextmanager
def temp_directory():
    tempdir = tempfile.mkdtemp(u('é'))
    assert u('é') in tempdir  # Test non-ASCII filenames
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)


def round_tuple(values):
    return tuple(round(v, 6) for v in values)


def assert_raise_finished(func, *args, **kwargs):
    with pytest.raises(cairocffi.CairoError) as exc:
        func(*args, **kwargs)
    assert 'SURFACE_FINISHED' in str(exc)


def test_cairo_version():
    major, minor, micro = map(int, cairo_version_string().split('.'))
    assert cairo_version() == major * 10000 + minor * 100 + micro


def test_install_as_pycairo():
    cairocffi.install_as_pycairo()
    import cairo
    assert cairo is cairocffi


def test_image_surface():
    assert ImageSurface.format_stride_for_width('ARGB32', 100) == 400
    assert ImageSurface.format_stride_for_width('A8', 100) == 100

    assert cairocffi.FORMAT_ARGB32 == 'ARGB32'
    surface = ImageSurface('ARGB32', 20, 30)
    assert surface.get_format() == 'ARGB32'
    assert surface.get_width() == 20
    assert surface.get_height() == 30
    assert surface.get_stride() == 20 * 4


def test_image_surface_from_buffer():
    if '__pypy__' in sys.modules:
        # See https://bitbucket.org/cffi/cffi/issue/47
        # and https://bugs.pypy.org/issue1354
        pytest.xfail()
    with pytest.raises(ValueError):
        # buffer too small
        data = bytearray(b'\x00' * 799)
        ImageSurface.create_for_data(data, 'ARGB32', 10, 20)
    data = bytearray(b'\x00' * 800)
    surface = ImageSurface.create_for_data(data, 'ARGB32', 10, 20, stride=40)
    context = Context(surface)
    # The default source is opaque black:
    assert context.get_source().get_rgba() == (0, 0, 0, 1)
    context.paint_with_alpha(0.5)
    assert data == pixel(b'\x80\x00\x00\x00') * 200


def test_surface_create_similar_image():
    if cairo_version() < 11200:
        pytest.xfail()
    surface = ImageSurface('ARGB32', 20, 30)
    similar = surface.create_similar_image('A8', 4, 100)
    assert isinstance(similar, ImageSurface)
    assert similar.get_content() == 'ALPHA'
    assert similar.get_format() == 'A8'
    assert similar.get_width() == 4
    assert similar.get_height() == 100


def test_surface_create_for_rectangle():
    if cairo_version() < 11000:
        pytest.xfail()
    surface = ImageSurface('A8', 4, 4)
    data = surface.get_data()
    assert data[:] == b'\x00' * 16
    Context(surface.create_for_rectangle(1, 1, 2, 2)).paint()
    assert data[:] == (
        b'\x00\x00\x00\x00'
        b'\x00\xFF\xFF\x00'
        b'\x00\xFF\xFF\x00'
        b'\x00\x00\x00\x00')


def test_surface():
    surface = ImageSurface('ARGB32', 20, 30)
    similar = surface.create_similar('ALPHA', 4, 100)
    assert isinstance(similar, ImageSurface)
    assert similar.get_content() == 'ALPHA'
    assert similar.get_format() == 'A8'
    assert similar.get_width() == 4
    assert similar.get_height() == 100
    surface.copy_page()
    surface.show_page()
    surface.mark_dirty()
    surface.mark_dirty_rectangle(1, 2, 300, 12000)
    surface.flush()

    surface.set_device_offset(14, 3)
    assert surface.get_device_offset() == (14, 3)

    surface.set_fallback_resolution(15, 6)
    assert surface.get_fallback_resolution() == (15, 6)

    context = Context(surface)
    assert isinstance(context.get_target(), ImageSurface)
    try:
        del cairocffi.surfaces.SURFACE_TYPE_TO_CLASS['IMAGE']
        target = context.get_target()
        assert target._pointer == surface._pointer
        assert isinstance(target, Surface)
        assert not isinstance(target, ImageSurface)
    finally:
        cairocffi.surfaces.SURFACE_TYPE_TO_CLASS['IMAGE'] = ImageSurface

    surface.finish()
    assert_raise_finished(surface.copy_page)
    assert_raise_finished(surface.show_page)
    assert_raise_finished(surface.set_device_offset, 1, 2)
    assert_raise_finished(surface.set_fallback_resolution, 3, 4)


def test_mime_data():
    if cairo_version() < 11000:
        pytest.xfail()
    # Also test we get actually booleans:
    assert PDFSurface(None, 1, 1).supports_mime_type('image/jpeg') is True
    surface = ImageSurface('A8', 1, 1)
    assert surface.supports_mime_type('image/jpeg') is False
    assert surface.get_mime_data('image/jpeg') is None
    assert len(cairocffi.surfaces.KeepAlive.instances) == 0
    surface.set_mime_data('image/jpeg', b'lol')
    assert len(cairocffi.surfaces.KeepAlive.instances) == 1
    assert surface.get_mime_data('image/jpeg')[:] == b'lol'

    surface.set_mime_data('image/jpeg', None)
    assert len(cairocffi.surfaces.KeepAlive.instances) == 0
    assert surface.get_mime_data('image/jpeg') is None
    surface.finish()
    assert_raise_finished(surface.set_mime_data, 'image/jpeg', None)


def test_png():
    png_bytes = base64.b64decode(
        b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQI12O'
        b'w69x7BgAE3gJRgNit0AAAAABJRU5ErkJggg==')
    png_magic_number = png_bytes[:8]

    with temp_directory() as tempdir:
        filename = os.path.join(tempdir, 'foo.png')
        filename_bytes = filename.encode(sys.getfilesystemencoding())

        surface = ImageSurface('ARGB32', 1, 1)
        surface.write_to_png(filename)
        with open(filename, 'rb') as fd:
            assert fd.read().startswith(png_magic_number)
        open(filename, 'wb').close()
        with open(filename, 'rb') as fd:
            assert fd.read() == b''
        surface.write_to_png(filename_bytes)
        with open(filename, 'rb') as fd:
            assert fd.read().startswith(png_magic_number)

        with open(filename, 'wb') as fd:
            fd.write(png_bytes)

        for source in [io.BytesIO(png_bytes), filename, filename_bytes]:
            surface = ImageSurface.create_from_png(source)
            assert surface.get_format() == 'ARGB32'
            assert surface.get_width() == 1
            assert surface.get_height() == 1
            assert surface.get_stride() == 4
            data = surface.get_data()[:] == pixel(b'\xcc\x32\x6e\x97')

    file_obj = io.BytesIO()
    surface.write_to_png(file_obj)
    assert file_obj.getvalue().startswith(png_magic_number)

    with pytest.raises(IOError):
        # Truncated input
        surface = ImageSurface.create_from_png(io.BytesIO(png_bytes[:30]))


def test_pdf_versions():
    if cairo_version() < 11000:
        pytest.xfail()
    assert set(PDFSurface.get_versions()) >= set([
        'PDF_VERSION_1_4', 'PDF_VERSION_1_5'])
    assert PDFSurface.version_to_string('PDF_VERSION_1_4') == 'PDF 1.4'

    file_obj = io.BytesIO()
    PDFSurface(file_obj, 1, 1).finish()
    assert file_obj.getvalue().startswith(b'%PDF-1.5')

    file_obj = io.BytesIO()
    surface = PDFSurface(file_obj, 1, 1)
    surface.restrict_to_version('PDF_VERSION_1_4')
    surface.finish()
    assert file_obj.getvalue().startswith(b'%PDF-1.4')


def test_pdf_surface():
    with temp_directory() as tempdir:
        filename = os.path.join(tempdir, 'foo.pdf')
        filename_bytes = filename.encode(sys.getfilesystemencoding())
        file_obj = io.BytesIO()
        for target in [filename, filename_bytes, file_obj, None]:
            surface = PDFSurface(target, 123, 432)
            surface.finish()
        with open(filename, 'rb') as fd:
            assert fd.read().startswith(b'%PDF')
        with open(filename_bytes, 'rb') as fd:
            assert fd.read().startswith(b'%PDF')
        pdf_bytes = file_obj.getvalue()
        assert pdf_bytes.startswith(b'%PDF')
        assert b'/MediaBox [ 0 0 123 432 ]' in pdf_bytes
        assert pdf_bytes.count(b'/Type /Page\n') == 1

    file_obj = io.BytesIO()
    surface = PDFSurface(file_obj, 1, 1)
    context = Context(surface)
    surface.set_size(12, 100)
    context.show_page()
    surface.set_size(42, 700)
    context.copy_page()
    surface.finish()
    pdf_bytes = file_obj.getvalue()
    assert b'/MediaBox [ 0 0 1 1 ]' not in pdf_bytes
    assert b'/MediaBox [ 0 0 12 100 ]' in pdf_bytes
    assert b'/MediaBox [ 0 0 42 700 ]' in pdf_bytes
    assert pdf_bytes.count(b'/Type /Page\n') == 2


def test_svg_surface():
    assert set(SVGSurface.get_versions()) >= set([
        'SVG_VERSION_1_1', 'SVG_VERSION_1_2'])
    assert SVGSurface.version_to_string('SVG_VERSION_1_1') == 'SVG 1.1'

    with temp_directory() as tempdir:
        filename = os.path.join(tempdir, 'foo.svg')
        filename_bytes = filename.encode(sys.getfilesystemencoding())
        file_obj = io.BytesIO()
        for target in [filename, filename_bytes, file_obj, None]:
            SVGSurface(target, 123, 432).finish()
        with open(filename, 'rb') as fd:
            assert fd.read().startswith(b'<?xml')
        with open(filename_bytes, 'rb') as fd:
            assert fd.read().startswith(b'<?xml')
        svg_bytes = file_obj.getvalue()
        assert svg_bytes.startswith(b'<?xml')
        assert b'viewBox="0 0 123 432"' in svg_bytes

    surface = SVGSurface(None, 1, 1)
    surface.restrict_to_version('SVG_VERSION_1_1')  # Not obvious to test


def test_ps_surface():
    assert set(PSSurface.get_levels()) >= set([
        'PS_LEVEL_2', 'PS_LEVEL_3'])
    assert PSSurface.ps_level_to_string('PS_LEVEL_3') == 'PS Level 3'

    with temp_directory() as tempdir:
        filename = os.path.join(tempdir, 'foo.ps')
        filename_bytes = filename.encode(sys.getfilesystemencoding())
        file_obj = io.BytesIO()
        for target in [filename, filename_bytes, file_obj, None]:
            PSSurface(target, 123, 432).finish()
        with open(filename, 'rb') as fd:
            assert fd.read().startswith(b'%!PS')
        with open(filename_bytes, 'rb') as fd:
            assert fd.read().startswith(b'%!PS')
        assert file_obj.getvalue().startswith(b'%!PS')

    file_obj = io.BytesIO()
    surface = PSSurface(file_obj, 1, 1)
    surface.restrict_to_level('PS_LEVEL_2')  # Not obvious to test
    assert surface.get_eps() is False
    surface.set_eps('lol')
    assert surface.get_eps() is True
    surface.set_eps('')
    assert surface.get_eps() is False
    surface.set_size(10, 12)
    surface.dsc_comment(u('%%Lorem'))
    surface.dsc_begin_setup()
    surface.dsc_comment('%%ipsum')
    surface.dsc_begin_page_setup()
    surface.dsc_comment('%%dolor')
    surface.finish()
    ps_bytes = file_obj.getvalue()
    assert b'%%Lorem' in ps_bytes
    assert b'%%ipsum' in ps_bytes
    assert b'%%dolor' in ps_bytes


def test_matrix():
    m = Matrix()
    with pytest.raises(AttributeError):
        m.some_inexistent_attribute
    assert m.as_tuple() == (1, 0,  0, 1,  0, 0)
    m.translate(12, 4)
    assert m.as_tuple() == (1, 0,  0, 1,  12, 4)
    m.scale(2, 7)
    assert m.as_tuple() == (2, 0,  0, 7,  12, 4)
    assert m.yy == 7
    m.yy = 3
    assert m.as_tuple() == (2, 0,  0, 3,  12, 4)

    assert m.transform_distance(1, 2) == (2, 6)
    assert m.transform_point(1, 2) == (14, 10)

    m2 = m.copy()
    assert m2 == m
    m2.invert()
    assert m2.as_tuple() == (0.5, 0,  0, 1./3,  -12 / 2, -4. / 3)
    assert m.inverted() == m2
    assert m.as_tuple() == (2, 0,  0, 3,  12, 4)  # Unchanged

    m.rotate(math.pi / 2)
    assert round_tuple(m.as_tuple()) == (0, 3,  -2, 0,  12, 4)
    m *= Matrix.init_rotate(math.pi)
    assert round_tuple(m.as_tuple()) == (0, -3,  2, 0,  -12, -4)


def test_surface_pattern():
    surface = ImageSurface('A1', 1, 1)
    pattern = SurfacePattern(surface)

    surface_again = pattern.get_surface()
    assert surface_again is not surface
    assert surface_again._pointer == surface._pointer

    assert pattern.get_extend() == 'NONE'
    pattern.set_extend('REPEAT')
    assert pattern.get_extend() == 'REPEAT'

    assert pattern.get_filter() == 'GOOD'
    pattern.set_filter('BEST')
    assert pattern.get_filter() == 'BEST'

    assert pattern.get_matrix() == Matrix()  # identity
    matrix = Matrix.init_rotate(0.5)
    pattern.set_matrix(matrix)
    assert pattern.get_matrix() == matrix
    assert pattern.get_matrix() != Matrix()


def test_solid_pattern():
    assert SolidPattern(1, .5, .25).get_rgba() == (1, .5, .25, 1)
    assert SolidPattern(1, .5, .25, .75).get_rgba() == (1, .5, .25, .75)

    surface = PDFSurface(None, 1, 1)
    context = Context(surface)
    pattern = SolidPattern(1, .5, .25)
    context.set_source(pattern)
    assert isinstance(context.get_source(), SolidPattern)
    try:
        del cairocffi.patterns.PATTERN_TYPE_TO_CLASS['SOLID']
        re_pattern = context.get_source()
        assert re_pattern._pointer == pattern._pointer
        assert isinstance(re_pattern, Pattern)
        assert not isinstance(re_pattern, SolidPattern)
    finally:
        cairocffi.patterns.PATTERN_TYPE_TO_CLASS['SOLID'] = SolidPattern


def test_linear_gradient():
    gradient = LinearGradient(1, 2, 10, 20)
    assert gradient.get_linear_points() == (1, 2, 10, 20)
    gradient.add_color_stop_rgb(1, 1, .5, .25)
    gradient.add_color_stop_rgb(offset=.5, red=1, green=.5, blue=.25)
    gradient.add_color_stop_rgba(.5, 1, .5, .75, .25)
    assert gradient.get_color_stops() == [
        (.5, 1, .5, .25, 1),
        (.5, 1, .5, .75, .25),
        (1, 1, .5, .25, 1)]

    surface = ImageSurface('A8', 4, 4)
    assert surface.get_data()[:] == b'\x00' * 16
    gradient = LinearGradient(1, 0, 3, 0)
    gradient.add_color_stop_rgba(0, 0, 0, 0, 0)
    gradient.add_color_stop_rgba(1, 0, 0, 0, 1)
    context = Context(surface)
    context.set_source(gradient)
    context.paint()
    assert surface.get_data()[:] == b'\x00\x3f\xbf\xff' * 4


def test_radial_gradient():
    gradient = RadialGradient(42, 420, 10, 43, 430, 20)
    assert gradient.get_radial_circles() == (42, 420, 10, 43, 430, 20)
    gradient.add_color_stop_rgb(1, 1, .5, .25)
    gradient.add_color_stop_rgb(offset=.5, red=1, green=.5, blue=.25)
    gradient.add_color_stop_rgba(.5, 1, .5, .75, .25)
    assert gradient.get_color_stops() == [
        (.5, 1, .5, .25, 1),
        (.5, 1, .5, .75, .25),
        (1, 1, .5, .25, 1)]


def test_context_as_context_manager():
    surface = ImageSurface('ARGB32', 1, 1)
    context = Context(surface)
    # The default source is opaque black:
    assert context.get_source().get_rgba() == (0, 0, 0, 1)
    with context:
        context.set_source_rgb(1, .25, .5)
        assert context.get_source().get_rgba() == (1, .25, .5, 1)
    # Context restored at the end of with statement.
    assert context.get_source().get_rgba() == (0, 0, 0, 1)
    try:
        with context:
            context.set_source_rgba(1, .25, .75, .5)
            assert context.get_source().get_rgba() == (1, .25, .75, .5)
            raise ValueError
    except ValueError:
        pass
    # Context also restored on exceptions.
    assert context.get_source().get_rgba() == (0, 0, 0, 1)


def test_context_groups():
    surface = ImageSurface('ARGB32', 1, 1)
    context = Context(surface)
    assert isinstance(context.get_target(), ImageSurface)
    assert context.get_target()._pointer == surface._pointer
    assert context.get_group_target()._pointer == surface._pointer
    assert context.get_group_target().get_content() == 'COLOR_ALPHA'
    assert surface.get_data()[:] == pixel(b'\x00\x00\x00\x00')

    with context:
        context.push_group_with_content('ALPHA')
        assert context.get_group_target().get_content() == 'ALPHA'
        context.set_source_rgba(1, .2, .4, .8)  # Only A is actually used
        assert isinstance(context.get_source(), SolidPattern)
        context.paint()
        context.pop_group_to_source()
        assert isinstance(context.get_source(), SurfacePattern)
        # Still nothing on the original surface
        assert surface.get_data()[:] == pixel(b'\x00\x00\x00\x00')
        context.paint()
        assert surface.get_data()[:] == pixel(b'\xCC\x00\x00\x00')

    with context:
        context.push_group()
        context.set_source_rgba(1, .2, .4)
        context.paint()
        group = context.pop_group()
        assert isinstance(context.get_source(), SolidPattern)
        assert isinstance(group, SurfacePattern)
        context.set_source_surface(group.get_surface())
        assert surface.get_data()[:] == pixel(b'\xCC\x00\x00\x00')
        context.paint()
        assert surface.get_data()[:] == pixel(b'\xFF\xFF\x33\x66')


def test_context_current_transform_matrix():
    surface = ImageSurface('ARGB32', 1, 1)
    context = Context(surface)
    assert isinstance(context.get_matrix(), Matrix)
    assert context.get_matrix().as_tuple() == (1, 0, 0, 1, 0, 0)
    context.translate(6, 5)
    assert context.get_matrix().as_tuple() == (1, 0, 0, 1, 6, 5)
    context.scale(.5, 3)
    assert context.get_matrix().as_tuple() == (.5, 0, 0, 3, 6, 5)
    context.rotate(math.pi / 2)
    assert round_tuple(context.get_matrix().as_tuple()) == (0, 3, -.5, 0, 6, 5)

    context.identity_matrix()
    assert context.get_matrix().as_tuple() == (1, 0, 0, 1, 0, 0)
    context.set_matrix(Matrix(2, 1, 3, 7, 8, 2))
    assert context.get_matrix().as_tuple() == (2, 1, 3, 7, 8, 2)
    context.transform(Matrix(2, 0, 0, .5, 0, 0))
    assert context.get_matrix().as_tuple() == (4, 2, 1.5, 3.5, 8, 2)

    context.set_matrix(Matrix(2, 0,  0, 3,  12, 4))
    assert context.user_to_device_distance(1, 2) == (2, 6)
    assert context.user_to_device(1, 2) == (14, 10)
    assert context.device_to_user_distance(2, 6) == (1, 2)
    assert round_tuple(context.device_to_user(14, 10)) == (1, 2)


def test_context_path():
    surface = ImageSurface('ARGB32', 1, 1)
    context = Context(surface)

    assert list(context.copy_path()) == []
    assert context.get_current_point() is None
    context.arc(100, 200, 20, math.pi/2, 0)
    path_1 = list(context.copy_path())
    assert path_1[0] == ('MOVE_TO', (100, 220))
    assert len(path_1) > 1
    assert all(part[0] == 'CURVE_TO' for part in path_1[1:])
    assert context.get_current_point() == (120, 200)

    context.new_sub_path()
    assert list(context.copy_path()) == path_1
    assert context.get_current_point() is None
    context.new_path()
    assert list(context.copy_path()) == []
    assert context.get_current_point() is None

    assert context.get_current_point() is None
    context.arc_negative(100, 200, 20, math.pi/2, 0)
    path_2 = list(context.copy_path())
    assert path_2[0] == ('MOVE_TO', (100, 220))
    assert len(path_2) > 1
    assert all(part[0] == 'CURVE_TO' for part in path_2[1:])
    assert path_2 != path_1

    context.new_path()
    context.rectangle(10, 20, 100, 200)
    path = list(context.copy_path())
    # Some cairo versions add a MOVE_TO after a CLOSE_PATH
    if path[-1] == ('MOVE_TO', (10, 20)):
        path = path[:-1]
    assert path == [
        ('MOVE_TO', (10, 20)),
        ('LINE_TO', (110, 20)),
        ('LINE_TO', (110, 220)),
        ('LINE_TO', (10, 220)),
        ('CLOSE_PATH', ())]
    assert context.path_extents() == (10, 20, 110, 220)

    context.new_path()
    context.move_to(10, 20)
    context.line_to(10, 30)
    context.rel_move_to(2, 5)
    context.rel_line_to(2, 5)
    context.curve_to(20, 30, 70, 50, 100, 120)
    context.rel_curve_to(20, 30, 70, 50, 100, 120)
    context.close_path()
    path_obj = context.copy_path()
    path = list(path_obj)
    if path[-1] == ('MOVE_TO', (12, 35)):
        path = path[:-1]
    assert path == [
        ('MOVE_TO', (10, 20)),
        ('LINE_TO', (10, 30)),
        ('MOVE_TO', (12, 35)),
        ('LINE_TO', (14, 40)),
        ('CURVE_TO', (20, 30, 70, 50, 100, 120)),
        ('CURVE_TO', (120, 150, 170, 170, 200, 240)),
        ('CLOSE_PATH', ())]
    context.append_path(path_obj)
    assert list(context.copy_path()) == path + list(path_obj)

    context.new_path()
    context.curve_to(20, 30, 70, 50, 100, 120)
    path = list(context.copy_path_flat())
    assert len(path) > 2
    assert path[0] == ('MOVE_TO', (20, 30))
    assert all(part[0] == 'LINE_TO' for part in path[1:])
    assert path[-1] == ('LINE_TO', (100, 120))


def test_context_properties():
    surface = ImageSurface('ARGB32', 1, 1)
    context = Context(surface)

    assert context.get_antialias() == 'DEFAULT'
    context.set_antialias('BEST')
    assert context.get_antialias() == 'BEST'

    assert context.get_dash() == ([], 0)
    context.set_dash([4, 1, 3, 2], 1.5)
    assert context.get_dash() == ([4, 1, 3, 2], 1.5)
    assert context.get_dash_count() == 4

    assert context.get_fill_rule() == 'WINDING'
    context.set_fill_rule('EVEN_ODD')
    assert context.get_fill_rule() == 'EVEN_ODD'

    assert context.get_line_cap() == 'BUTT'
    context.set_line_cap('SQUARE')
    assert context.get_line_cap() == 'SQUARE'

    assert context.get_line_join() == 'MITER'
    context.set_line_join('ROUND')
    assert context.get_line_join() == 'ROUND'

    assert context.get_line_width() == 2
    context.set_line_width(13)
    assert context.get_line_width() == 13

    assert context.get_miter_limit() == 10
    context.set_miter_limit(4)
    assert context.get_miter_limit() == 4

    assert context.get_operator() == 'OVER'
    context.set_operator('XOR')
    assert context.get_operator() == 'XOR'

    assert context.get_tolerance() == 0.1
    context.set_tolerance(0.25)
    assert context.get_tolerance() == 0.25


def test_context_fill():
    surface = ImageSurface('A8', 4, 4)
    assert surface.get_data()[:] == b'\x00' * 16
    context = Context(surface)
    context.set_source_rgba(0, 0, 0, .5)
    context.set_line_width(.5)
    context.rectangle(1, 1, 2, 2)
    assert context.fill_extents() == (1, 1, 3, 3)
    assert context.stroke_extents() == (.75, .75, 3.25, 3.25)
    assert context.in_fill(2, 2) is True
    assert context.in_fill(.8, 2) is False
    assert context.in_stroke(2, 2) is False
    assert context.in_stroke(.8, 2) is True
    path = list(context.copy_path())
    assert path
    context.fill_preserve()
    assert list(context.copy_path()) == path
    assert surface.get_data()[:] == (
        b'\x00\x00\x00\x00'
        b'\x00\x80\x80\x00'
        b'\x00\x80\x80\x00'
        b'\x00\x00\x00\x00'
    )
    context.fill()
    assert list(context.copy_path()) == []
    assert surface.get_data()[:] == (
        b'\x00\x00\x00\x00'
        b'\x00\xC0\xC0\x00'
        b'\x00\xC0\xC0\x00'
        b'\x00\x00\x00\x00'
    )


def test_context_stroke():
    for preserve in [True, False]:
        surface = ImageSurface('A8', 4, 4)
        assert surface.get_data()[:] == b'\x00' * 16
        context = Context(surface)
        context.set_source_rgba(0, 0, 0, 1)
        context.set_line_width(1)
        context.rectangle(.5, .5, 2, 2)
        path = list(context.copy_path())
        assert path
        context.stroke_preserve() if preserve else context.stroke()
        assert list(context.copy_path()) == (path if preserve else [])
        assert surface.get_data()[:] == (
            b'\xFF\xFF\xFF\x00'
            b'\xFF\x00\xFF\x00'
            b'\xFF\xFF\xFF\x00'
            b'\x00\x00\x00\x00')


def test_context_clip():
    surface = ImageSurface('A8', 4, 4)
    assert surface.get_data()[:] == b'\x00' * 16
    context = Context(surface)
    context.rectangle(1, 1, 2, 2)
    assert context.clip_extents() == (0, 0, 4, 4)
    path = list(context.copy_path())
    assert path
    context.clip_preserve()
    assert list(context.copy_path()) == path
    assert context.clip_extents() == (1, 1, 3, 3)
    context.clip()
    assert list(context.copy_path()) == []
    assert context.clip_extents() == (1, 1, 3, 3)
    context.reset_clip()
    assert context.clip_extents() == (0, 0, 4, 4)

    context.rectangle(1, 1, 2, 2)
    context.rectangle(1, 2, 1, 2)
    context.clip()
    assert context.copy_clip_rectangle_list() == [(1, 1, 2, 2), (1, 3, 1, 1)]
    assert context.clip_extents() == (1, 1, 3, 4)


def test_context_in_clip():
    if cairo_version() < 11000:
        pytest.xfail()
    surface = ImageSurface('A8', 4, 4)
    context = Context(surface)
    context.rectangle(1, 1, 2, 2)
    assert context.in_clip(.5, 2) is True
    assert context.in_clip(1.5, 2) is True
    context.clip()
    assert context.in_clip(.5, 2) is False
    assert context.in_clip(1.5, 2) is True


def test_context_mask():
    mask_surface = ImageSurface('ARGB32', 2, 2)
    context = Context(mask_surface)
    context.set_source_rgba(1, 0, .5, 1)
    context.rectangle(0, 0, 1, 1)
    context.fill()
    context.set_source_rgba(1, .5, 1, .5)
    context.rectangle(1, 1, 1, 1)
    context.fill()

    surface = ImageSurface('ARGB32', 4, 4)
    context = Context(surface)
    context.mask(SurfacePattern(mask_surface))
    o = pixel(b'\x00\x00\x00\x00')
    b = pixel(b'\x80\x00\x00\x00')
    B = pixel(b'\xFF\x00\x00\x00')
    assert surface.get_data()[:] == (
        B + o + o + o +
        o + b + o + o +
        o + o + o + o +
        o + o + o + o
    )

    surface = ImageSurface('ARGB32', 4, 4)
    context = Context(surface)
    context.mask_surface(mask_surface, surface_x=1, surface_y=2)
    o = pixel(b'\x00\x00\x00\x00')
    b = pixel(b'\x80\x00\x00\x00')
    B = pixel(b'\xFF\x00\x00\x00')
    assert surface.get_data()[:] == (
        o + o + o + o +
        o + o + o + o +
        o + B + o + o +
        o + o + b + o
    )


def test_context_font():
    surface = ImageSurface('ARGB32', 10, 10)
    context = Context(surface)
    assert context.get_font_matrix().as_tuple() == (10, 0, 0, 10, 0, 0)
    context.set_font_matrix(Matrix(2, 0,  0, 3,  12, 4))
    assert context.get_font_matrix().as_tuple() == (2, 0,  0, 3,  12, 4)
    context.set_font_size(14)
    assert context.get_font_matrix().as_tuple() == (14, 0, 0, 14, 0, 0)

    context.set_font_size(10)
    context.select_font_face(b'serif', 'ITALIC')
    font_face = context.get_font_face()
    assert isinstance(font_face, ToyFontFace)
    assert font_face.get_family() == 'serif'
    assert font_face.get_slant() == 'ITALIC'
    assert font_face.get_weight() == 'NORMAL'

    try:
        del cairocffi.fonts.FONT_TYPE_TO_CLASS['TOY']
        re_font_face = context.get_font_face()
        assert re_font_face._pointer == font_face._pointer
        assert isinstance(re_font_face, FontFace)
        assert not isinstance(re_font_face, ToyFontFace)
    finally:
        cairocffi.fonts.FONT_TYPE_TO_CLASS['TOY'] = ToyFontFace

    ascent, descent, height, max_x_advance, max_y_advance = (
        context.font_extents())
    # That’s about all we can assume for a default font.
    assert height > ascent + descent
    assert max_x_advance > 0
    assert max_y_advance == 0
    _, _, _, _, x_advance, y_advance = context.text_extents('i' * 10)
    assert x_advance > 0
    assert y_advance == 0
    context.set_font_face(ToyFontFace(u('monospace'), weight='BOLD'))
    _, _, _, _, x_advance_mono, y_advance = context.text_extents('i' * 10)
    assert x_advance_mono > x_advance
    assert y_advance == 0
    assert list(context.copy_path()) == []
    context.text_path('a')
    assert list(context.copy_path())
    assert surface.get_data()[:] == b'\x00' * 400
    context.move_to(1, 9)
    context.show_text('a')
    assert surface.get_data()[:] != b'\x00' * 400

    assert context.get_font_options().get_hint_metrics() == 'DEFAULT'
    context.set_font_options(FontOptions(hint_metrics='ON'))
    assert context.get_font_options().get_hint_metrics() == 'ON'
    assert surface.get_font_options().get_hint_metrics() == 'ON'

    context.set_font_matrix(Matrix(2, 0,  0, 3,  12, 4))
    assert context.get_scaled_font().get_font_matrix().as_tuple() == (
        2, 0,  0, 3,  12, 4)
    context.set_scaled_font(ScaledFont(ToyFontFace(), font_matrix=Matrix(
        0, 1,  4, 0,  12, 4)))
    assert context.get_font_matrix().as_tuple() == (0, 1,  4, 0,  12, 4)


def test_scaled_font():
    font = ScaledFont(ToyFontFace())
    font_extents = font.extents()
    ascent, descent, height, max_x_advance, max_y_advance = font_extents
    assert height > ascent + descent
    assert max_x_advance > 0
    assert max_y_advance == 0
    _, _, _, _, x_advance, y_advance = font.text_extents('i' * 10)
    assert x_advance > 0
    assert y_advance == 0

    font = ScaledFont(ToyFontFace('monospace'))
    _, _, _, _, x_advance_mono, y_advance = font.text_extents('i' * 10)
    assert x_advance_mono > x_advance
    assert y_advance == 0
    # Not much we can test:
    # Che toy font face was "materialized" into a specific backend.
    assert isinstance(font.get_font_face(), FontFace)

    font = ScaledFont(
        ToyFontFace('monospace'), Matrix(xx=20, yy=20), Matrix(xx=3, yy=.5),
        FontOptions(antialias='BEST'))
    assert font.get_font_options().get_antialias() == 'BEST'
    assert font.get_font_matrix().as_tuple() == (20, 0, 0, 20, 0, 0)
    assert font.get_ctm().as_tuple() == (3, 0, 0, .5, 0, 0)
    assert font.get_scale_matrix().as_tuple() == (60, 0, 0, 10, 0, 0)
    _, _, _, _, x_advance_mono_2, y_advance_2 = font.text_extents('i' * 10)
    # Same yy as before:
    assert y_advance == y_advance_2
    # Bigger xx:
    assert x_advance_mono_2 > x_advance_mono


def test_font_options():
    options = FontOptions()

    assert options.get_antialias() == 'DEFAULT'
    options.set_antialias('FAST')
    assert options.get_antialias() == 'FAST'

    assert options.get_subpixel_order() == 'DEFAULT'
    options.set_subpixel_order('BGR')
    assert options.get_subpixel_order() == 'BGR'

    assert options.get_hint_style() == 'DEFAULT'
    options.set_hint_style('SLIGHT')
    assert options.get_hint_style() == 'SLIGHT'

    assert options.get_hint_metrics() == 'DEFAULT'
    options.set_hint_metrics('OFF')
    assert options.get_hint_metrics() == 'OFF'


    options_1 = FontOptions(hint_metrics='ON')
    assert options_1.get_hint_metrics() == 'ON'
    assert options_1.get_antialias() == 'DEFAULT'
    options_2 = options_1.copy()
    assert options_2 == options_1
    assert len(set([options_1, options_2])) == 1  # test __hash__
    options_2.set_antialias('BEST')
    assert options_2 != options_1
    assert len(set([options_1, options_2])) == 2
    options_1.merge(options_2)
    assert options_2 == options_1
