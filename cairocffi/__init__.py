"""
    cairocffi
    ~~~~~~~~~

    cffi-based cairo bindings for Python. See README for details.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from cffi import FFI


VERSION = '0.1'


ffi = FFI()
ffi.cdef("""
    const char* cairo_version_string (void);
""")
cairo_c = ffi.dlopen('cairo')

print(ffi.string(cairo_c.cairo_version_string()))
