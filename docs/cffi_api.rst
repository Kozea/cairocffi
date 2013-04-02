CFFI API
========

.. currentmodule:: cairocffi

cairocffi’s :doc:`API <api>` is made of a number of
:ref:`wrapper <wrappers>` classes
that provide a more Pythonic interface for various cairo objects.
Functions that take a pointer as their first argument become methods,
error statuses become exceptions,
and :ref:`reference counting <refcounting>` is hidden away.

In order to use other C libraries that use integrate with cairo,
or if cairocffi’s API is not sufficient
(Consider making a `pull request`_!)
you can access cairo’s lower level C pointers and API through CFFI_.

.. _pull request: https://github.com/SimonSapin/cairocffi
.. _CFFI: https://cffi.readthedocs.org/


Module-level objects
--------------------

.. data:: ffi

    A :class:`cffi.FFI` instance with all of the cairo C API declared.

.. data:: cairo

    The libcairo library, pre-loaded with :meth:`ffi.dlopen`.
    All cairo functions are accessible as attributes of this object::

        from cairocffi import cairo as cairo_c

        if cairo_c.cairo_surface_get_type(surface._pointer) == 'XLIB':
            ...

    See the `cairo manual`_ for details.

    .. _cairo manual: http://cairographics.org/manual/


.. _refcounting:

Reference counting in cairo
---------------------------

Most cairo objects are reference-counted,
and freed when the count reaches zero.
cairocffi’s Python wrapper will automatically decrease the reference count
when they are garbage-collected.
Therefore, care must be taken when creating a wrapper
as to the reference count should be increased (for existing cairo objects)
or not (for cairo objects that were just created with a refcount of 1.)


.. _wrappers:

Wrappers
--------

.. automethod:: Surface._from_pointer
.. automethod:: Pattern._from_pointer
.. automethod:: FontFace._from_pointer
.. automethod:: ScaledFont._from_pointer
.. automethod:: Context._from_pointer

.. attribute:: Surface._pointer

    The underlying :c:type:`cairo_surface_t *` cdata pointer.

.. attribute:: Pattern._pointer

    The underlying :c:type:`cairo_pattern_t *` cdata pointer.

.. attribute:: FontFace._pointer

    The underlying :c:type:`cairo_font_face_t *` cdata pointer.

.. attribute:: ScaledFont._pointer

    The underlying :c:type:`cairo_scaled_font_t *` cdata pointer.

.. attribute:: FontOptions._pointer

    The underlying :c:type:`cairo_scaled_font_t *` cdata pointer.

.. attribute:: Matrix._pointer

    The underlying :c:type:`cairo_matrix_t *` cdata pointer.

.. attribute:: Context._pointer

    The underlying :c:type:`cairo_t *` cdata pointer.


.. _converting_pycairo:

Converting pycairo wrappers
---------------------------

Some libraries such as PyGTK or PyGObject
provide a pycairo :class:`~cairo.Context` object for you to draw on.
It is possible to extract the underlying :c:type:`cairo_t *` pointer
and create a cairocffi wrapper for the same cairo context.

The follwing function does that with unsafe pointer manipulation.
It only works on CPython.

.. code-block:: python

    import cairo  # pycairo
    import cairocffi

    def _UNSAFE_cairocffi_context_from_pycairo_context(pycairo_context):
        # Sanity check. Continuing with another type would probably segfault.
        if not isinstance(context, cairo.Context):
            raise TypeError('Expected a cairo.Context, got %r' % pycairo_context)

        # On CPython, id() gives the memory address of a Python object.
        # pycairo implements Context as a C struct:
        #   typedef struct {
        #     PyObject_HEAD
        #     cairo_t *ctx;
        #     PyObject *base;
        #   } PycairoContext;
        pycairo_context_address = id(pycairo_context)

        # Still on CPython, object.__basicsize__ is the size of PyObject_HEAD.
        ctx_field_address = pycairo_context_address + object.__basicsize__

        # Wrap the address of the 'ctx' field in a CFFI cdata (pointer) object.
        ctx_field_pointer = cairocffi.ffi.cast('cairo_t **', ctx_field_address)

        # Dereference that pointer, ie. read the ctx field.
        # The result is the pointer to the underlying cairo_t C struct.
        cairo_t_pointer = ctx_field_pointer[0]

        # Finally we can create a cairocffi context!
        return cairocffi.Context._from_pointer(cairo_t_pointer, incref=True)

If you’re willing to compile C code against pycairo,
using :c:func:`PycairoContext_GET` from pycairo’s C API might be more robust.
Untested C code:

.. code-block:: c

    PycairoContext *pycairo_context = ...;
    PyObject *cairo_t_address = PyLong_FromLong(
        (uintptr_t) PycairoContext_GET(pycairo_context));

In Python:

.. code-block:: python

    cairo_t_pointer = cairocffi.ffi.cast('cairo_t *', cairo_t_address)
    context = cairocffi.Context._from_pointer(cairo_t_pointer, incref=True)


.. _using_pango:

Example: using Pango through CFFI with cairocffi
------------------------------------------------

The program below shows a fairly standard usage of CFFI
to access Pango’s C API.
The :attr:`Context._pointer` pointer needs to be cast
in order to be recognized by the new :obj:`~pango_example.ffi` object.
The C definitions are copied from `Pango’s`_ and `GLib’s`_ documentation.

.. _Pango’s: http://developer.gnome.org/pango/stable/
.. _GLib’s: http://developer.gnome.org/glib/stable/


Using CFFI for accessing Pango
(rather than the traditional bindings in PyGTK or PyGObject with introspection)
is not only easiest for using together with cairocffi,
but also means that all of Pango’s API is within reach,
whereas bindings often only expose the high level API.

.. literalinclude:: ../utils/pango_example.py
