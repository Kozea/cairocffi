cairocffi
=========

cairocffi is a `CFFI`_-based drop-in replacement for Pycairo_,
a set of Python bindings and object-oriented API for cairo_.
Cairo is a 2D vector graphics library with support for multiple backends
including image buffers, PNG, PostScript, PDF, and SVG file output.

Additionally, the ``cairocffi.pixbuf`` module uses GDK-PixBuf_
to decode various image formats for use in cairo.

.. _CFFI: https://cffi.readthedocs.org/
.. _Pycairo: https://pycairo.readthedocs.io/
.. _cairo: http://cairographics.org/
.. _GDK-PixBuf: https://gitlab.gnome.org/GNOME/gdk-pixbuf

* `Latest documentation <http://cairocffi.readthedocs.io/en/latest/>`_
* `Source code and issue tracker <https://github.com/Kozea/cairocffi>`_
  on GitHub.
* Install with ``pip install cairocffi``
* Python 3.5+. `Tested with CPython and PyPy3
  <https://travis-ci.org/Kozea/cairocffi>`_.
* API partially compatible with Pycairo.
* Works with any version of cairo.
