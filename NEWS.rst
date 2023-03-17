cairocffi changelog
-------------------


Version 1.5.0
.............

Released on 2023-03-17

* `#106 <https://github.com/Kozea/cairocffi/issues/106>`,
  `#200 <https://github.com/Kozea/cairocffi/issues/200>`:
  Fallback to manual PNG file creation on hardened systems
* `#210 <https://github.com/Kozea/cairocffi/pull/210>`:
  Use pyproject.toml for packaging and remove other useless files


Version 1.4.0
.............

Released on 2022-09-23

* `#205 <https://github.com/Kozea/cairocffi/pull/205>`_:
  Use pikepdf to parse generated PDF
* `#171 <https://github.com/Kozea/cairocffi/pull/171>`_:
  Don’t use deprecated pytest-runner anymore


Version 1.3.0
.............

Released on 2021-10-04

* `2cd512d <https://github.com/Kozea/cairocffi/commit/2cd512d>`_:
  Drop Python 3.6 support
* `#196 <https://github.com/Kozea/cairocffi/pull/196>`_:
  Fix import `constants.py` import
* `#169 <https://github.com/Kozea/cairocffi/pull/169>`_:
  Add extra library name "cairo-2.dll"
* `#178 <https://github.com/Kozea/cairocffi/pull/178>`_:
  Workaround for testing date string with cairo 1.17.4
* `#186 <https://github.com/Kozea/cairocffi/pull/186>`_:
  Fix link in documentation
* `#195 <https://github.com/Kozea/cairocffi/pull/195>`_:
  Fix typo in documentation
* `#184 <https://github.com/Kozea/cairocffi/pull/184>`_,
  `a4fc2a7 <https://github.com/Kozea/cairocffi/commit/a4fc2a7>`_:
  Clean .gitignore


Version 1.2.0
.............

Released on 2020-10-29

* `#152 <https://github.com/Kozea/cairocffi/pull/152>`_:
  Add NumPy support
* `#143 <https://github.com/Kozea/cairocffi/issues/143>`_:
  Make write_to_png function work on hardened systems
* `#156 <https://github.com/Kozea/cairocffi/pull/156>`_:
  Use major version name to open shared libraries
* `#165 <https://github.com/Kozea/cairocffi/pull/165>`_:
  Don’t list setuptools as required for installation


Version 1.1.0
.............

Released on 2019-09-05

* `#135 <https://github.com/Kozea/cairocffi/pull/135>`_,
  `#127 <https://github.com/Kozea/cairocffi/pull/127>`_,
  `#119 <https://github.com/Kozea/cairocffi/pull/119>`_:
  Clean the way external libraries are found
* `#126 <https://github.com/Kozea/cairocffi/pull/126>`_:
  Remove const char* elements from cdef
* Support Cairo features up to 1.17.2
* Fix documentation generation


Version 1.0.2
.............

Released on 2019-02-15

* `#123 <https://github.com/Kozea/cairocffi/issues/123>`_:
  Rely on a recent version of setuptools to handle VERSION


Version 1.0.1
.............

Released on 2019-02-12

* `#120 <https://github.com/Kozea/cairocffi/issues/120>`_:
  Don't delete _generated modules on ffi_build import


Version 1.0.0
.............

Released on 2019-02-08

6 years after its first release, cairocffi can now be considered as stable.

* Drop Python 2.6, 2.7 and 3.4 support
* Test with Python 3.7
* Clean code, tests and packaging


Version 0.9.0
.............

Released on 2018-08-06

* Drop Python 3.2 and 3.3 support
* Test with PyPy and PyPy3
* `#114 <https://github.com/Kozea/cairocffi/pull/114>`_:
  Fix test compatibility with Cairo 1.15.12
* `#112 <https://github.com/Kozea/cairocffi/pull/112>`_:
  Add cairo library name from PyGObject for Windows
* Fix ``pango_example.py``
* `#85 <https://github.com/Kozea/cairocffi/issues/85>`_:
  Fix crash with xbc tests
* Clean documentation
* Support Cairo features up to 1.15.12


Version 0.8.1
.............

Released on 2018-05-30

* `#98 <https://github.com/Kozea/cairocffi/pull/98>`_:
  Add width and height options to pixbuf.decode_to_image_surface
* `#112 <https://github.com/Kozea/cairocffi/pull/112>`_:
  Add cairo library name from PyGObject for Windows


Version 0.8.0
.............

Released on 2017-02-03

* Follow semver
* `#76 <https://github.com/Kozea/cairocffi/issues/76>`_:
  Avoid implicit relative import
* `#74 <https://github.com/Kozea/cairocffi/pull/74>`_:
  Use utf-8 instead of utf8 in headers
* `#73 <https://github.com/Kozea/cairocffi/issues/73>`_:
  Keep cairo library loaded until all relevant objects are freed
* `#86 <https://github.com/Kozea/cairocffi/pull/86>`_:
  Add cairo_quartz_* functions for MacOS
* Use the default ReadTheDocs theme
* Fix implicit casts


Version 0.7.2
.............

Released on 2015-08-04

* Use ctypes.util.find_library with dlopen.


Version 0.7.1
.............

Released on 2015-06-22

* Allow installing cairocffi when cffi<1.0 is installed.


Version 0.7
...........

Released on 2015-06-05

* `#47 <https://github.com/SimonSapin/cairocffi/pull/47>`_:
  Fix PyPy support.
* `#60 <https://github.com/SimonSapin/cairocffi/pull/60>`_:
  Use CFFI-1.0 methods.
* `#61 <https://github.com/SimonSapin/cairocffi/pull/61>`_:
  Allow ffi import when package is pip installed.


Version 0.6
...........

Released on 2014-09-23.

* `#39 <https://github.com/SimonSapin/cairocffi/pull/39>`_:
  Add :class:`xcb.XCBSurface`.
* `#42 <https://github.com/SimonSapin/cairocffi/pull/42>`_:
  Add :class:`Win32PrintingSurface`.


Version 0.5.4
.............

Released on 2014-05-23.

* Stop testing with tox on Python 3.1, start on 3.4
* Start testing pushes and pull requests
  `on Travis-CI <https://travis-ci.org/SimonSapin/cairocffi>`_
* Add more variants of the library names to try with `dlopen()`.
  This seems to be necessary on OpenBSD.


Version 0.5.3
.............

Released on 2014-03-11.

Fix `#28 <https://github.com/SimonSapin/cairocffi/pull/28>`_:
Add another dynamic library name to try to load, for OS X.


Version 0.5.2
.............

Released on 2014-02-27.

Fix `#21 <https://github.com/SimonSapin/cairocffi/pull/21>`_:
``UnicodeDecodeError`` when installing with a non-UTF-8 locale.


Version 0.5.1
.............

Released on 2013-07-16.

Fix `#15 <https://github.com/SimonSapin/cairocffi/pull/15>`_:
Work around `CFFI bug #92 <https://bitbucket.org/cffi/cffi/issue/92/>`_
that caused memory leaks when file-like :obj:`target` objects
are passed to :meth:`Surface.write_to_png`, :class:`PDFSurface`,
:class:`PSSurface` and :class:`SVGSurface`.


Version 0.5
...........

Released on 2013-06-20.

Change :func:`~cairocffi.pixbuf.decode_to_image_surface`
to raise a specific :exc:`~cairocffi.pixbuf.ImageLoadingError` exception
instead of a generic :exc:`~exceptions.ValueError`.
This new exception type inherits from :exc:`~exceptions.ValueError`.


Version 0.4.3
.............

Released on 2013-05-27.

* Fix `#10 <https://github.com/SimonSapin/cairocffi/issues/10>`_:
  Pretend to be pycairo 1.10.0, for compatibility with matplotlib
  which does version detection.
* Fix `WeasyPrint#94 <https://github.com/Kozea/WeasyPrint/issues/94>`_:
  Make (again??) GTK acutally optional for PixBuf support.


Version 0.4.2
.............

Released on 2013-05-03.

* Fix `#9 <https://github.com/SimonSapin/cairocffi/issues/9>`_:
  Make GTK acutally optional for PixBuf support.


Version 0.4.1
.............

Released on 2013-04-30.

* Various documentation improvements
* Bug fixes:

  * Fix error handling in :meth:`ImageSurface.create_from_png`.
  * Fix :meth:`ScaledFont.text_to_glyphs` and :meth:`Context.show_text_glyphs`
    with new-style enums.


Version 0.4
...........

Released on 2013-04-06.

No change since 0.3.1, but depend on CFFI < 0.6
because of backward-incompatible changes.
cairocffi 0.4 will require CFFI 0.6 or more.


  .. code-block:: python

      # Before cairocffi 0.4:
      surface = cairocffi.ImageSurface('ARGB32', 300, 400)

      # All cairocffi versions:
      surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, 300, 400)

* Compatibility with CFFI 0.6


Version 0.3.2
.............

Released on 2013-03-29.

No change since 0.3.1, but depend on CFFI < 0.6
because of backward-incompatible changes.
cairocffi 0.4 will require CFFI 0.6 or more.


Version 0.3.1
.............

Released on 2013-03-18.

Fix handling of GDK-PixBuf errors.


Version 0.3
...........

Released on 2013-02-26.

* Add :mod:`cairocffi.pixbuf`, for loading images with GDK-PixBuf.
* Add iteration and item access on :class:`Matrix`.
* Better `Windows support`_ by trying to load ``libcairo-2.dll``

.. _Windows support: http://packages.python.org/cairocffi/overview.html#installing-cairo-on-windows


Version 0.2
...........

Released on 2013-01-08.

Added :class:`RecordingSurface`.


Version 0.1
...........

Released on  2013-01-07.

First PyPI release.
