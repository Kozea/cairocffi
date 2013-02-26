.. module:: cairocffi.pixbuf

Decoding images with GDK-PixBuf
===============================

The
:meth:`ImageSurface.create_from_png() <cairocffi.ImageSurface.create_from_png>`
method can decode PNG images and provide a cairo surface,
but what about other image formats?

The :mod:`cairocffi.pixbuf` module uses GDK-PixBuf_
to decode JPEG, GIF, and various other formats (depending on what is installed.)
If you don’t import this module,
it is possible to use the rest of cairocffi without having GDK-PixBuf installed.
GDK-PixBuf is an independent package since version 2.22,
but before that was part of GTK_.

.. _GDK-PixBuf: https://live.gnome.org/GdkPixbuf
.. _GTK: http://www.gtk.org/

This module also converts pixel data
since the internal format in GDK-PixBuf (big-endian RGBA)
is not the same as in cairo (native-endian ARGB).
For this reason, although it is a "toy" API,
:meth:`ImageSurface.create_from_png() <cairocffi.ImageSurface.create_from_png>`
can be faster than :func:`decode_to_image_surface`
if the format is known to be PNG.
The pixel conversion is done by GTK if available,
but a (slower) fallback method is used otherwise.

.. autofunction:: decode_to_image_surface
