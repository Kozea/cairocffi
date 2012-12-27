# coding: utf8
"""
    cairocffi.compat
    ~~~~~~~~~~~~~~~~

    Compatibility module for various Python versions.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

import sys


try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError

try:
    callable = callable
except:
    from collections import Callable
    from cffi import api
    api.callable = callable = lambda x: isinstance(x, Callable)


if sys.version_info >= (3,):
    u = lambda x: x
else:
    u = lambda x: x.decode('utf8')
