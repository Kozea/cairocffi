CFFI API
========

.. currentmodule:: cairocffi

If the cairocffi API is not sufficient,
you can access cairo’s lower level C API through CFFI_.
See the `cairo manual`_ for details.
If however some functionnality could be added to cairocffi itself,
please consider making a `pull request
<https://github.com/SimonSapin/cairocffi>`_!

.. _CFFI: https://cffi.readthedocs.org/
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

Wrappers
--------

.. automethod:: Surface._from_pointer
.. automethod:: Pattern._from_pointer
.. automethod:: FontFace._from_pointer
.. automethod:: ScaledFont._from_pointer

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

    This is what you would typically pass to other C libraries
    that work together with cairo::

        pangocairo = ffi.dlopen('pangocairo-1.0')
        layout = pangocairo.pango_cairo_create_layout(context._pointer)
        # ...
