Overview
========

.. currentmodule:: cairocffi

Installing CFFI
---------------

cairocffi requires CFFI,
which can be installed with pip_ but has its own dependencies
that can be tricky to install.

* On Linux, install ``python-dev`` and ``libffi-dev`` from your system’s package manager.
* On OS X, install ``pkg-config`` and ``libffi``, for example with `Homebrew`_.
  You may need to `set the PKG_CONFIG_PATH environment variable`_.
* On Windows, consider using `Christoph Gohlke’s unofficial binary builds`_.

See `CFFI’s own documentation`_ for details.

.. _Homebrew: http://brew.sh/
.. _set the PKG_CONFIG_PATH environment variable: http://cffi.readthedocs.org/#macos-x
.. _Christoph Gohlke’s unofficial binary builds: http://www.lfd.uci.edu/~gohlke/pythonlibs/#cffi
.. _CFFI’s own documentation: http://cffi.readthedocs.org/


Installing cairocffi
--------------------

Install with pip_::

    pip install cairocffi

This will automatically install CFFI.

cairocffi can also be setup to utilize XCB support via xcffib_, that has to be
installed before cairocffi::

    pip install xcffib
    pip install cairocffi

In addition to other dependencies, this will install xcffib.

.. _pip: http://pip-installer.org/
.. _xcffib: https://github.com/tych0/xcffib/


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

.. _Pycairo: http://cairographics.org/pycairo/


Installing cairo on Windows
...........................

cairocffi needs a ``libcairo-2.dll`` file
in a directory that is listed in the ``PATH`` environment variable.

`Alexander Shaduri’s GTK+ installer
<http://gtk-win.sourceforge.net/home/index.php/Main/Downloads>`_ works.
(Make sure to leave the *Set up PATH environment variable* checkbox checked.)
Pycairo on Windows is sometimes compiled statically against cairo
and may not provide a ``.dll`` file that cairocffi can use.


cairo versions
--------------

Cairo, pycairo, and cairocffi each have version numbers. The same cairocffi
version can be used with a variety of cairo versions. For example, the
:meth:`Surface.set_mime_data` method is based on the
``cairo_surface_set_mime_data`` C function, which is only available since
cairo 1.10. You will get a runtime exception if you try to use it with an older
cairo. You can however still use the rest of the API. There is no need for
cairocffi’s versions to be tied to cairo’s versions.

Use :func:`cairo_version` to test the version number for cairo::

    if cairocffi.cairo_version() > 11000:
        surface.set_mime_data('image/jpeg', jpeg_bytes)

Here are all the version numbers::

      >>> print("The cairo version is %s, meaning %s."
      ...       % (cairocffi.cairo_version(), cairocffi.cairo_version_string())
      The cairo version is 11402, meaning 1.14.02.
      >>> print("The latest pycairo version this cairocffi version is compatible with is %s."
      ...       % cairo.version)
      The latest pycairo version this cairocffi version is compatible with is 1.10.0.
      >>> print("The cairocffi version is %s." % cairo.VERSION)
      The cairocffi version is 0.7.2

cairocffi is automatically tested with both cairo 1.13.0 (Ubuntu Trusty's
default version) and manually tested with the latest (1.15.12 as of this
writing.)


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

Alternatively, add a ``cairo.py`` file somewhere in your ``sys.path``,
so that it’s imported instead of pycairo::

    from cairocffi import *

It is also possible to :ref:`convert pycairo contexts to cairocffi
<converting_pycairo>`.


Basic usage
-----------

For doing something useful with cairo,
you need at least a surface and a context::

    import cairocffi as cairo

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 200)
    context = cairo.Context(surface)
    with context:
        context.set_source_rgb(1, 1, 1)  # White
        context.paint()
    # Restore the default source which is black.
    context.move_to(90, 140)
    context.rotate(-0.5)
    context.set_font_size(20)
    context.show_text('Hi from cairo!')
    surface.write_to_png('example.png')

The :class:`Surface` represents the target.
There are various types of surface for various output backends.
The :class:`Context` holds internal state and is use for drawing.
We’re only using solid colors here,
but more complex :class:`Pattern` types are also available.

All the details are in :doc:`api`.
