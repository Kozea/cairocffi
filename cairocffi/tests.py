# coding: utf8
"""
    cairocffi.tests
    ~~~~~~~~~~~~~~~

    Test suite for cairocffi.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

import io
import os
import sys
import base64
import shutil
import tempfile

import cairocffi
import pytest

from . import cairo_version, cairo_version_string, ImageSurface, Context
from .compat import u


def test_cairo_version():
    major, minor, micro = map(int, cairo_version_string().split('.'))
    assert cairo_version() == major * 10000 + minor * 100 + micro


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
    data = bytearray(b'\x00' * 800)
    with pytest.raises(ValueError):
        # buffer too small
        ImageSurface.create_for_data(data, 'ARGB32', 10, 21)
    surface = ImageSurface.create_for_data(data, 'ARGB32', 10, 20)
    context = Context(surface)
    context.paint()  # The default source is opaque black.
    assert data == b'\x00\x00\x00\xFF' * 200


def test_png():
    png_bytes = base64.b64decode(
        b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQI12O'
        b'w69x7BgAE3gJRgNit0AAAAABJRU5ErkJggg==')
    png_magic_number = png_bytes[:8]

    tempdir = tempfile.mkdtemp(u('é'))
    try:
        filename = os.path.join(tempdir, 'foo.png')
        filename_bytes = filename.encode(sys.getfilesystemencoding())
        assert u('é') in filename

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

        for surface in [
                ImageSurface.create_from_png(io.BytesIO(png_bytes)),
                ImageSurface.create_from_png(filename),
                ImageSurface.create_from_png(filename_bytes)]:
            assert surface.get_format() == 'ARGB32'
            assert surface.get_width() == 1
            assert surface.get_height() == 1
            assert surface.get_stride() == 4
            data = surface.get_data()[:]
            if sys.byteorder == 'little':
                data = data[::-1]
            assert data == b'\xcc\x32\x6e\x97'
    finally:
        shutil.rmtree(tempdir)

    file_obj = io.BytesIO()
    surface.write_to_png(file_obj)
    assert file_obj.getvalue().startswith(png_magic_number)
