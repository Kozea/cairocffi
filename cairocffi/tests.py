"""
    cairocffi.tests
    ~~~~~~~~~~~~~~~

    Test suite for cairocffi.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import cairo_version, cairo_version_string


def test_cairo_version():
    major, minor, micro = map(int, cairo_version_string().split('.'))
    assert cairo_version() == major * 10000 + minor * 100 + micro
