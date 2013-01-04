CFFI API
========

If the cairocffi API is not sufficient,
you can access cairo’s lower level C API through CFFI_.
See the `cairo manual`_ for details.
If however some functionnality could be added to cairocffi itself,
please consider making a `pull request
<https://github.com/SimonSapin/cairocffi>`_!

.. _CFFI: https://cffi.readthedocs.org/
.. _cairo manual: http://cairographics.org/manual/


.. currentmodule:: cairocffi
.. data:: ffi

    A :class:`cffi.FFI` instance with all of the cairo C API declared.

.. data:: cairo

    The libcairo library, pre-loaded with :meth:`ffi.dlopen`.
    All cairo functions are accessible as attributes of this object::

        from cairocffi import cairo as cairo_c

        if cairo_c.cairo_surface_get_type(surface._pointer) == 'XLIB':
            ...


.. attribute:: Surface._pointer

    The :c:type:`cairo_surface_t*` cdata object for this surface.
    Automatically calls :c:func:`cairo_surface_destroy()` on itself
    when garbage-collected.
