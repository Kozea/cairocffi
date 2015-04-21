# coding: utf8

import ctypes
import cairo  # pycairo
import cairocffi

pycairo = ctypes.PyDLL(cairo._cairo.__file__)
pycairo.PycairoContext_FromContext.restype = ctypes.c_void_p
pycairo.PycairoContext_FromContext.argtypes = 3 * [ctypes.c_void_p]
ctypes.pythonapi.PyList_Append.argtypes = 2 * [ctypes.c_void_p]


def _UNSAFE_cairocffi_context_to_pycairo(cairocffi_context):
    # Sanity check. Continuing with another type would probably segfault.
    if not isinstance(cairocffi_context, cairocffi.Context):
        raise TypeError('Expected a cairocffi.Context, got %r'
                        % cairocffi_context)

    # Create a reference for PycairoContext_FromContext to take ownership of.
    cairocffi.cairo.cairo_reference(cairocffi_context._pointer)
    # Casting the pointer to uintptr_t (the integer type as wide as a pointer)
    # gets the context’s integer address.
    # On CPython id(cairo.Context) gives the address to the Context type,
    # as expected by PycairoContext_FromContext.
    address = pycairo.PycairoContext_FromContext(
        int(cairocffi.ffi.cast('uintptr_t', cairocffi_context._pointer)),
        id(cairo.Context),
        None)
    assert address
    # This trick uses Python’s C API
    # to get a reference to a Python object from its address.
    temp_list = []
    assert ctypes.pythonapi.PyList_Append(id(temp_list), address) == 0
    return temp_list[0]
