# coding: utf8
#
# cairocffi.capi
# ~~~~~~~~~~~~~~~~~
#
# :copyright: Copyright 2013 by Simon Feltman
# :license: BSD, see LICENSE for details.

"""
Mostly ABI compatible Pycairo C API

This modules exposes a PyCapsule as "CAPI" which can be installed using
cairocffi.enable_capi().

The Pycairo C API looks for the capsule in a module named "cairo",
so cairocffi.enable_capi() installs cairocffi into sys.modules
as "cairo". The capsule holds a table of pointers to functions and
Python types which is mostly ABI compatible with what Pycairo supplies.
The exception being attempts to access returned wrapper struct members
of the PyObjects supplied by this API, e.g:

    PyObject *pyctx = Context_FromContext (ctx);
    ((PycairoContext*)pyctx)->ctx

Extensions which do this will crash due to the actual PyObjects returned
from Pycairo and cairocffi not being binary compatible.

This only works with cpython and will raise an import error otherwise.
"""

import sys
if sys.implementation.name != 'cpython':
    raise ImportError('Cannot use cairo C API with implementations other than cpython')

from . import ffi, cairo, _check_status, dlopen

from .surfaces import (Surface, ImageSurface, PDFSurface, PSSurface,
                       SVGSurface, RecordingSurface)
from .patterns import (Pattern, SolidPattern, SurfacePattern,
                       Gradient, LinearGradient, RadialGradient)
from .fonts import FontFace, ToyFontFace, ScaledFont, FontOptions
from .context import Context
from .matrix import Matrix


# cffi python api
Python_CAPI = """
typedef struct PyObject PyObject;
typedef struct PyTypeObject PyTypeObject;
PyObject* PyCapsule_New(void *pointer, const char *name, void*);
void* PyCapsule_GetPointer(PyObject *capsule, const char *name);
void Py_IncRef(PyObject *o);
void Py_DecRef(PyObject *o);
"""
ffi.cdef(Python_CAPI)
_dlname = 'libpython%i.%i%s.so' % (sys.version_info[:2] + (sys.abiflags,))
pythoncffi = dlopen(ffi, _dlname)


def CPyObjectWrapper_ForCairoPtr(tp, cairo_ptr):
    # We must add an additional ref to the newly created PyObject which
    # is handed back to the calling C API. This needs to return
    # a "New value reference". Otherwise the refcount of "wrapper"
    # will go to zero at the end of this function.
    wrapper = tp._from_pointer(cairo_ptr, True)
    wrapperptr = ffi.cast('PyObject*', id(wrapper))
    pythoncffi.Py_IncRef(wrapperptr)
    return wrapperptr


@ffi.callback("PyObject*(*)(cairo_t*, PyTypeObject*, PyObject*)")
def Context_FromContext(ctx, tp, base):
    return CPyObjectWrapper_ForCairoPtr(Context, ctx)


@ffi.callback("PyObject*(*)(cairo_font_face_t*)")
def FontFace_FromFontFace(font_face):
    return CPyObjectWrapper_ForCairoPtr(FontFace, font_face)


@ffi.callback("PyObject*(*)(cairo_font_options_t*)")
def FontOptions_FromFontOptions(font_options):
    return CPyObjectWrapper_ForCairoPtr(FontOptions, font_options)


@ffi.callback("PyObject*(*)(const cairo_matrix_t*)")
def Matrix_FromMatrix(matrix):
    return CPyObjectWrapper_ForCairoPtr(Matrix, matrix)


@ffi.callback("PyObject*(*)(cairo_path_t*)")
def Path_FromPath(path):
    return CPyObjectWrapper_ForCairoPtr(Path, path)


@ffi.callback("PyObject*(*)(cairo_pattern_t*, PyObject*)")
def Pattern_FromPattern(pattern, base):
    return CPyObjectWrapper_ForCairoPtr(Pattern, pattern)


@ffi.callback("PyObject*(*)(cairo_scaled_font_t*)")
def ScaledFont_FromScaledFont(scaled_font):
    return CPyObjectWrapper_ForCairoPtr(ScaledFont, scaled_font)


@ffi.callback("PyObject*(*)(cairo_surface_t*, PyObject*)")
def Surface_FromSurface(surface):
    return CPyObjectWrapper_ForCairoPtr(Surface, surface)


@ffi.callback("PyObject*(*)(cairo_rectangle_int_t*)")
def RectangleInt_FromRectangleInt(rectangle_int):
    return CPyObjectWrapper_ForCairoPtr(RectangleInt, rectangle_int)


@ffi.callback("PyObject*(*)(cairo_region_t*)")
def Region_FromRegion(region):
    return CPyObjectWrapper_ForCairoPtr(Region, region)


@ffi.callback("int(*)(cairo_status_t)")
def Check_Status(status):
    return _check_status(status)


# Note: this must match the layout of the Pycairo_CAPI_t
# found in pycairo.h and py3cairo.h
# Todo: perhaps this should parse a copy of the Pycairo_CAPI_t and
# use ffi.verify with pycairo.h
_pointers = [ffi.cast('PyTypeObject*', id(Context)),
             Context_FromContext,
             ffi.cast('PyTypeObject*', id(FontFace)),
             ffi.cast('PyTypeObject*', id(ToyFontFace)),
             FontFace_FromFontFace,
             ffi.cast('PyTypeObject*', id(FontOptions)),
             FontOptions_FromFontOptions,
             ffi.cast('PyTypeObject*', id(Matrix)),
             Matrix_FromMatrix,
             ffi.NULL,  # ffi.cast('PyTypeObject*', id(Path)),
             ffi.NULL,  # Path_FromPath,
             ffi.cast('PyTypeObject*', id(Pattern)),
             ffi.cast('PyTypeObject*', id(SolidPattern)),
             ffi.cast('PyTypeObject*', id(SurfacePattern)),
             ffi.cast('PyTypeObject*', id(Gradient)),
             ffi.cast('PyTypeObject*', id(LinearGradient)),
             ffi.cast('PyTypeObject*', id(RadialGradient)),
             Pattern_FromPattern,
             ffi.cast('PyTypeObject*', id(ScaledFont)),
             ScaledFont_FromScaledFont,
             ffi.cast('PyTypeObject*', id(Surface)),
             ffi.cast('PyTypeObject*', id(ImageSurface)),
             ffi.cast('PyTypeObject*', id(PDFSurface)),
             ffi.cast('PyTypeObject*', id(PSSurface)),
             ffi.cast('PyTypeObject*', id(RecordingSurface)),
             ffi.cast('PyTypeObject*', id(SVGSurface)),
             ffi.NULL,  # ffi.cast('PyTypeObject*', id(Win32Surface)),
             ffi.NULL,  # ffi.cast('PyTypeObject*', id(Win32PrintingSurface)),
             ffi.NULL,  # ffi.cast('PyTypeObject*', id(XCBSurface)),
             ffi.NULL,  # ffi.cast('PyTypeObject*', id(XlibSurface)),
             Surface_FromSurface,
             Check_Status,
             ffi.NULL,  # ffi.cast('PyTypeObject*', id(RectangleInt)),
             ffi.NULL,  # RectangleInt_FromRectangleInt,
             ffi.NULL,  # ffi.cast('PyTypeObject*', id(Region)),
             Region_FromRegion,
            ]


# We must use ctypes to create a valid PyCapsule
import ctypes

ctypes.pythonapi.PyCapsule_New.restype = ctypes.py_object
ctypes.pythonapi.PyCapsule_New.argtypes = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p)
ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
ctypes.pythonapi.PyCapsule_GetPointer.argtypes = (ctypes.py_object, ctypes.c_char_p)


# Stash these at the module level to ensure they are kept alive
_pycairo_api = ffi.new("void*[%i]" % len(_pointers), _pointers)
_capsule_name = b'cairo.CAPI'
_pycairo_api_addr = int(ffi.cast('uintptr_t', _pycairo_api))
CAPI = ctypes.pythonapi.PyCapsule_New(_pycairo_api_addr, _capsule_name, None)

# Failed attempt at using cffi to create the PyCapsule
# (ffi.from_handle did not do what I expected)
"""
_capsule_name = ffi.NULL  # b'cairo.CAPI'
_capsule = pythoncffi.PyCapsule_New(_pycairo_api, _capsule_name, ffi.NULL)
_capsule_addr = int(ffi.cast('uintptr_t', _capsule))
CAPI = ffi.from_handle(ffi.cast('void*', _capsule_addr))
"""
