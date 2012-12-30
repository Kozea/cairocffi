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
               ImageSurface, PDFSurface, PSSurface, SVGSurface,
               SolidPattern, SurfacePattern, LinearGradient, RadialGradient)
from .compat import u


@contextlib.contextmanager
def temp_directory():
    tempdir = tempfile.mkdtemp(u('é'))
    assert u('é') in tempdir  # Test non-ASCII filenames
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)


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
        ImageSurface.create_for_data(bytearray(b'\x00' * 799), 'ARGB32', 10, 20)
    data = bytearray(b'\x00' * 800)
    surface = ImageSurface.create_for_data(data, 'ARGB32', 10, 20)
    context = Context(surface)
    context.paint()  # The default source is opaque black.
    assert data == b'\x00\x00\x00\xFF' * 200


def test_surface():
    surface = ImageSurface('ARGB32', 20, 30)
    for similar in [
            surface.create_similar('ALPHA', 4, 100),
            surface.create_similar_image('A8', 4, 100)]:
        assert isinstance(similar, ImageSurface)
        assert similar.get_content() == 'ALPHA'
        assert similar.get_format() == 'A8'
        assert similar.get_width() == 4
        assert similar.get_height() == 100

    surface = ImageSurface('A8', 4, 4)
    data = surface.get_data()
    assert data[:] == b'\x00' * 16
    Context(surface.create_for_rectangle(1, 1, 2, 2)).paint()
    assert data[:] == (
        b'\x00\x00\x00\x00'
        b'\x00\xFF\xFF\x00'
        b'\x00\xFF\xFF\x00'
        b'\x00\x00\x00\x00'
    )
    surface.copy_page()
    surface.show_page()
    surface.mark_dirty()
    surface.mark_dirty_rectangle(1, 2, 300, 12000)
    surface.flush()

    surface.set_device_offset(14, 3)
    assert surface.get_device_offset() == (14, 3)

    surface.set_fallback_resolution(15, 6)
    assert surface.get_fallback_resolution() == (15, 6)


    def assert_raise_finished(func, *args, **kwargs):
        with pytest.raises(cairocffi.CairoError) as exc:
            func(*args, **kwargs)
        assert 'SURFACE_FINISHED' in str(exc)

    surface.finish()
    assert_raise_finished(surface.copy_page)
    assert_raise_finished(surface.show_page)
    assert_raise_finished(surface.set_device_offset, 1, 2)
    assert_raise_finished(surface.set_fallback_resolution, 3, 4)
    assert_raise_finished(surface.set_mime_data, 'image/jpeg', None)


def test_mime_data():
    if '__pypy__' in sys.modules:
        # See https://bitbucket.org/cffi/cffi/issue/47
        # and https://bugs.pypy.org/issue1354
        pytest.xfail()
    assert PDFSurface(None, 1, 1).supports_mime_type('image/jpeg') is True
    surface = ImageSurface('A8', 1, 1)
    assert surface.supports_mime_type('image/jpeg') is False
    assert surface.get_mime_data('image/jpeg') is None
    assert len(cairocffi.surfaces.KeepAlive.instances) == 0
    surface.set_mime_data('image/jpeg', bytearray(b'lol'))
    assert len(cairocffi.surfaces.KeepAlive.instances) == 1
    assert surface.get_mime_data('image/jpeg')[:] == b'lol'

    surface.set_mime_data('image/jpeg', None)
    assert len(cairocffi.surfaces.KeepAlive.instances) == 0
    assert surface.get_mime_data('image/jpeg') is None


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
            fd.read().startswith(png_magic_number)

        with open(filename, 'wb') as fd:
            fd.write(png_bytes)

        for source in [io.BytesIO(png_bytes), filename, filename_bytes]:
            surface = ImageSurface.create_from_png(source)
            assert surface.get_format() == 'ARGB32'
            assert surface.get_width() == 1
            assert surface.get_height() == 1
            assert surface.get_stride() == 4
            data = surface.get_data()[:]
            if sys.byteorder == 'little':
                data = data[::-1]
            assert data == b'\xcc\x32\x6e\x97'

    file_obj = io.BytesIO()
    surface.write_to_png(file_obj)
    assert file_obj.getvalue().startswith(png_magic_number)

    with pytest.raises(IOError):
        # Truncated input
        surface = ImageSurface.create_from_png(io.BytesIO(png_bytes[:30]))

def test_pdf_surface():
    assert set(PDFSurface.get_versions()) >= set([
        'PDF_VERSION_1_4', 'PDF_VERSION_1_5'])
    assert PDFSurface.version_to_string('PDF_VERSION_1_4') == 'PDF 1.4'

    with temp_directory() as tempdir:
        filename = os.path.join(tempdir, 'foo.pdf')
        filename_bytes = filename.encode(sys.getfilesystemencoding())
        file_obj = io.BytesIO()
        for target in [filename, filename_bytes, file_obj, None]:
            PDFSurface(target, 123, 432).finish()
        with open(filename, 'rb') as fd:
            assert fd.read().startswith(b'%PDF-1.5')
        with open(filename_bytes, 'rb') as fd:
            assert fd.read().startswith(b'%PDF-1.5')
        pdf_bytes = file_obj.getvalue()
        assert pdf_bytes.startswith(b'%PDF-1.5')
        assert b'/MediaBox [ 0 0 123 432 ]' in pdf_bytes
        assert pdf_bytes.count(b'/Type /Page\n') == 1

    file_obj = io.BytesIO()
    surface = PDFSurface(file_obj, 1, 1)
    surface.restrict_to_version('PDF_VERSION_1_4')
    surface.finish()
    assert file_obj.getvalue().startswith(b'%PDF-1.4')

    file_obj = io.BytesIO()
    surface = PDFSurface(file_obj, 1, 1)
    surface.set_size(12, 100)
    surface.show_page()
    surface.set_size(42, 700)
    surface.show_page()
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
    def round_all(m):
        for name in ('xx', 'yx', 'xy', 'yy', 'x0', 'y0'):
            setattr(m, name, round(getattr(m, name), 3))

    m = Matrix()
    with pytest.raises(AttributeError):
        m.some_inexistent_attribute
    assert m.as_tuple() == (1, 0,  0, 1,  0, 0)
    m.translate(12, 4)
    assert m.as_tuple() == (1, 0,  0, 1,  12, 4)
    m.scale(2, 3)
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
    round_all(m)
    assert m.as_tuple() == (0, 3,  -2, 0,  12, 4)
    m *= Matrix.init_rotate(math.pi)
    round_all(m)
    assert m.as_tuple() == (0, -3,  2, 0,  -12, -4)


def test_surface_pattern():
    surface = ImageSurface('A1', 1, 1)
    pattern = SurfacePattern(surface)

    surface_again = pattern.get_surface()
    assert surface_again is not surface
    assert surface_again._handle == surface._handle

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
