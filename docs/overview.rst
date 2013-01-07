Overview
========

.. currentmodule:: cairocffi

Installing cairocffi
--------------------

Install with pip_::

    pip install cairocffi

This will automatically install CFFI,
which on CPython requires ``python-dev`` and ``libffi-dev``.
See the `CFFI documentation`_ for details.


Importing
---------

The module to import is named ``cairocffi``
in order to co-exist peacefully with Pycairo_ which uses ``cairo``,
but ``cairo`` is shorter and nicer to use::

    import cairocffi as cairo

cairocffi will dynamically load cairo as a shared library at this point.
If it fails to find it, you will see an exception like this::

    OSError: library not found: 'cairo'

Make sure cairo is correctly installed and available through your system’s
usual mechanisms.
On Linux, the ``LD_LIBRARY_PATH`` environment variable can be used to indicate
where to find shared libraries.

.. _pip: http://pip-installer.org/
.. _CFFI documentation: http://cffi.readthedocs.org/
.. _Pycairo: http://cairographics.org/pycairo/


Compatibility with Pycairo
--------------------------

cairocffi’s Python API is compatible with Pycairo.
Please `file a bug <https://github.com/SimonSapin/cairocffi/issues>`_
if you find incompatibilities.

In your own code that uses Pycairo, you should be able to just change
the imports from ``import cairo`` to ``import cairocffi as cairo`` as above.
If it’s not your own code that imports Pycairo,
the :func:`install_as_pycairo` function can help::

    import cairocffi
    cairocffi.install_as_pycairo()
    import cairo
    assert cairo is cairocffi


Basic usage
-----------

For doing something useful with cairo,
you need at least a surface and a context::

    surface = cairo.ImageSurface('RGB24', 300, 200)
    context = cairo.Context(surface)
    with context:
        context.set_source_rgb(1, 1, 1)  # White
        context.paint()
    # Restore the default source which is black.
    context.move_to(90, 140)
    context.rotate(-0.5)
    context.set_font_size(20)
    context.show_text(u'Hi from cairo!')
    surface.write_to_png('example.png')

The :class:`Surface` represents the target.
There are various types of surface for various output backends.
The :class:`Context` holds internal state and is use for drawing.
We’re only using solid colors here,
but more complex :class:`Pattern` types are also available.

All the details are in :doc:`api`.
