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

        import cairocffi
        from cairocffi import cairo as cairo_c, SURFACE_TYPE_XLIB

        if cairo_c.cairo_surface_get_type(surface._pointer) == SURFACE_TYPE_XLIB:
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

Converting pycairo wrappers to cairocffi
----------------------------------------

Some libraries such as PyGTK or PyGObject
provide a pycairo :class:`~cairo.Context` object for you to draw on.
It is possible to extract the underlying :c:type:`cairo_t *` pointer
and create a cairocffi wrapper for the same cairo context.

The follwing function does that with unsafe pointer manipulation.
It only works on CPython.

.. literalinclude:: ../utils/pycairo_to_cairocffi.py

Converting other types of objects like surfaces is very similar,
but left as an exercise to the reader.


Converting cairocffi wrappers to pycairo
----------------------------------------

The reverse conversion is also possible.
Here we use ctypes rather than CFFI
because Python’s C API is sensitive to the GIL.

.. literalinclude:: ../utils/cairocffi_to_pycairo.py


.. _using_pango:

Example: using Pango through CFFI with cairocffi
------------------------------------------------

The program below shows a fairly standard usage of CFFI
to access Pango’s C API.
The :attr:`Context._pointer` pointer can be used directly as an argument
to CFFI functions that expect ``cairo_t *``.
The C definitions are copied from `Pango’s`_ and `GLib’s`_ documentation.

.. _Pango’s: http://developer.gnome.org/pango/stable/
.. _GLib’s: http://developer.gnome.org/glib/stable/


Using CFFI for accessing Pango
(rather than the traditional bindings in PyGTK or PyGObject with introspection)
is not only easiest for using together with cairocffi,
but also means that all of Pango’s API is within reach,
whereas bindings often only expose the high level API.

.. literalinclude:: ../utils/pango_example.py
