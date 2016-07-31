# coding: utf-8

import cairo  # pycairo
import cairocffi


def _UNSAFE_pycairo_context_to_cairocffi(pycairo_context):
    # Sanity check. Continuing with another type would probably segfault.
    if not isinstance(pycairo_context, cairo.Context):
        raise TypeError('Expected a cairo.Context, got %r' % pycairo_context)

    # On CPython, id() gives the memory address of a Python object.
    # pycairo implements Context as a C struct:
    #     typedef struct {
    #         PyObject_HEAD
    #         cairo_t *ctx;
    #         PyObject *base;
    #     } PycairoContext;
    # Still on CPython, object.__basicsize__ is the size of PyObject_HEAD,
    # ie. the offset to the ctx field.
    # ffi.cast() converts the integer address to a cairo_t** pointer.
    # [0] dereferences that pointer, ie. read the ctx field.
    # The result is a cairo_t* pointer that cairocffi can use.
    return cairocffi.Context._from_pointer(
        cairocffi.ffi.cast('cairo_t **',
                           id(pycairo_context) + object.__basicsize__)[0],
        incref=True)
