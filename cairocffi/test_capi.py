# coding: utf8
#
# cairocffi.test_capi
# ~~~~~~~~~~~~~~~~~
# 
# Tests for Pycairo C API compat
# 
# :copyright: Copyright 2013 by Simon Feltman
# :license: BSD, see LICENSE for details.

import gc
import sys
import unittest
import ctypes

import cairocffi as cairo
from cairocffi import ffi
from ctypes import pythonapi


@unittest.skipUnless(sys.implementation.name == 'cpython',
                     'Test can only run under cpython')
class Test(unittest.TestCase):
    def test_capsule(self):
        # Pull the data back out of the capsule and test it.
        from cairocffi import capi
        data = pythonapi.PyCapsule_GetPointer(capi.CAPI, capi._capsule_name)
        data_ptr = ffi.cast('void*', data)
        self.assertEqual(data_ptr, capi._pycairo_api)

    def test_class_ptr_stored_in_capi(self):
        # Use ctypes to test the CAPI exposed by cffi
        from cairocffi import capi
        data = pythonapi.PyCapsule_GetPointer(capi.CAPI, capi._capsule_name)
        data = ctypes.cast(data, ctypes.POINTER(ctypes.c_void_p))

        self.assertEqual(data[0], id(cairo.Context))
        self.assertEqual(data[2], id(cairo.FontFace))
        self.assertEqual(data[3], id(cairo.ToyFontFace))
        self.assertEqual(data[5], id(cairo.FontOptions))
        self.assertEqual(data[7], id(cairo.Matrix))
        self.assertEqual(data[11], id(cairo.Pattern))
        self.assertEqual(data[12], id(cairo.SolidPattern))
        self.assertEqual(data[13], id(cairo.SurfacePattern))
        self.assertEqual(data[14], id(cairo.Gradient))
        self.assertEqual(data[15], id(cairo.LinearGradient))
        self.assertEqual(data[16], id(cairo.RadialGradient))
        self.assertEqual(data[18], id(cairo.ScaledFont))
        self.assertEqual(data[20], id(cairo.Surface))
        self.assertEqual(data[21], id(cairo.ImageSurface))
        self.assertEqual(data[22], id(cairo.PDFSurface))
        self.assertEqual(data[23], id(cairo.PSSurface))
        self.assertEqual(data[24], id(cairo.RecordingSurface))
        self.assertEqual(data[25], id(cairo.SVGSurface))

    def test_context_round_trip(self):
        from cairocffi import capi
        data = pythonapi.PyCapsule_GetPointer(capi.CAPI, capi._capsule_name)
        data = ctypes.cast(data, ctypes.POINTER(ctypes.c_void_p))

        Context_FromContext = ctypes.CFUNCTYPE(ctypes.py_object,
                                               ctypes.c_void_p,
                                               ctypes.c_void_p,
                                               ctypes.c_void_p)(data[1])

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 32, 32)
        cffi_ctx = cairo.Context(surface)
        self.assertEqual(sys.getrefcount(cffi_ctx), 2)
        self.assertEqual(cairo.cairo.cairo_get_reference_count(cffi_ctx._pointer), 1)

        # call the C API through ctypes to get a new wrapper of the cairo context
        ctx_addr = int(ffi.cast('uintptr_t', cffi_ctx._pointer))
        ctypes_ctx = Context_FromContext(ctx_addr, None, None)
        self.assertEqual(sys.getrefcount(cffi_ctx), 2)
        self.assertEqual(sys.getrefcount(ctypes_ctx), 2)
        self.assertEqual(cairo.cairo.cairo_get_reference_count(cffi_ctx._pointer), 2)
        self.assertEqual(cairo.cairo.cairo_get_reference_count(ctypes_ctx._pointer), 2)
        self.assertEqual(cffi_ctx._pointer, ctypes_ctx._pointer)

        # verify context refcount decreases as things are deleted
        del ctypes_ctx
        gc.collect()
        self.assertEqual(cairo.cairo.cairo_get_reference_count(cffi_ctx._pointer), 1)


if __name__ == '__main__':
    unittest.main()

