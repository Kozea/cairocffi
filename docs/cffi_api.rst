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


.. _using_pango:

Example: using Pango with CFFI
------------------------------

The program below shows a fairly standard usage of CFFI
to access Pango’ C API.
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
