Python API reference
####################

.. module:: cairocffi

Meta
====

.. autofunction:: install_as_pycairo
.. autofunction:: cairo_version
.. autofunction:: cairo_version_string
.. autoexception:: CairoError
.. data:: Error

    An alias for :exc:`CairoError`, for compatibility with pycairo.


Surfaces
========

.. autoclass:: Surface()

ImageSurface
------------
.. autoclass:: ImageSurface

PDFSurface
----------
.. autoclass:: PDFSurface

PSSurface
---------
.. autoclass:: PSSurface

SVGSurface
----------
.. autoclass:: SVGSurface

RecordingSurface
----------------
.. autoclass:: RecordingSurface

Win32PrintingSurface
--------------------
.. autoclass:: Win32PrintingSurface


Context
=======

.. autoclass:: Context


Matrix
======

.. autoclass:: Matrix


Patterns
========

.. autoclass:: Pattern()

SolidPattern
------------
.. autoclass:: SolidPattern

SurfacePattern
--------------
.. autoclass:: SurfacePattern

Gradient
--------
.. autoclass:: Gradient()

LinearGradient
..............
.. autoclass:: LinearGradient

RadialGradient
..............
.. autoclass:: RadialGradient


.. _fonts:

Fonts & text
============

A font is (in simple terms) a collection of shapes used to draw text.
A *glyph* is one of these shapes.
There can be multiple glyphs for the same character
(alternates to be used in different contexts, for example),
or a glyph can be a ligature of multiple characters.
Converting text to positioned glyphs is *shaping*.

Cairo itself provides a "toy" text API that only does simple shaping:
no ligature or kerning;
one glyph per character,
positioned by moving the cursor by the X and Y *advance* of each glyph.

It is expected that most applications will need to
:ref:`use Pango <using_pango>` or a similar library in conjunction with cairo
for more comprehensive font handling and text layout.


Font faces
----------

.. note::

    At the moment cairocffi only supports cairo’s "toy" font selection API.
    :class:`FontFace` objects of other types could be obtained
    eg. from :meth:`Context.get_font_face`,
    but they can not be instantiated directly.

.. autoclass:: FontFace()

ToyFontFace
...........
.. autoclass:: ToyFontFace


ScaledFont
----------
.. autoclass:: ScaledFont

FontOptions
-----------
.. autoclass:: FontOptions(**values)


.. _enumerated values:

Enumerated values
=================

Some parameters or return values in the cairo API
only have a fixed, finite set of valid values.
These are represented as *enumerated types* in C, and as integers in CFFI.
Users are encouraged to use the constants defined here
in the :mod:`cairocffi` module
rather than literal integers.
For example::

    surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, 300, 400)


.. _CONTENT:

Content
-------

Used to describe the content that a :class:`Surface` will contain,
whether color information, alpha information (translucence vs. opacity),
or both.


.. data:: CONTENT_COLOR

    The surface will hold color content only.


.. data:: CONTENT_ALPHA

    The surface will hold alpha content only.


.. data:: CONTENT_COLOR_ALPHA

    The surface will hold color and alpha content.


.. _FORMAT:

Pixel format
------------

Used to identify the memory format of image data.

.. data:: FORMAT_ARGB32

    Each pixel is a 32-bit quantity,
    with alpha in the upper 8 bits, then red, then green, then blue.
    The 32-bit quantities are stored native-endian.
    Pre-multiplied alpha is used.
    (That is, 50% transparent red is 0x80800000, not 0x80ff0000.)

.. data:: FORMAT_RGB24

    Each pixel is a 32-bit quantity, with the upper 8 bits unused.
    Red, Green, and Blue are stored in the remaining 24 bits in that order.

.. data:: FORMAT_A8

    Each pixel is a 8-bit quantity holding an alpha value.

.. data:: FORMAT_A1

    Each pixel is a 1-bit quantity holding an alpha value.
    Pixels are packed together into 32-bit quantities.
    The ordering of the bits matches the endianess of the platform.
    On a big-endian machine, the first pixel is in the uppermost bit,
    on a little-endian machine the first pixel is in the least-significant bit.

.. data:: FORMAT_RGB16_565

    Each pixel is a 16-bit quantity
    with red in the upper 5 bits,
    then green in the middle 6 bits,
    and blue in the lower 5 bits.

.. data:: FORMAT_RGB30

    Like :obj:`FORMAT_RGB24`,
    but with the upper 2 bits unused and 10 bits per components.


.. _OPERATOR:

Compositiong operator
---------------------

Used to set the compositing operator for all cairo drawing operations.

The default operator is :obj:`OPERATOR_OVER`.

The operators marked as **unbounded** modify their destination
even outside of the mask layer
(that is, their effect is not bound by the mask layer).
However, their effect can still be limited by way of clipping.

To keep things simple, the operator descriptions here
document the behavior for when both source and destination are either
fully transparent or fully opaque.
The actual implementation works for translucent layers too.
For a more detailed explanation of the effects of each operator,
including the mathematical definitions,
see `http://cairographics.org/operators/ <http://cairographics.org/operators/>`_.



.. data:: OPERATOR_CLEAR

    Clear destination layer. (bounded)

.. data:: OPERATOR_SOURCE

    Replace destination layer. (bounded)

.. data:: OPERATOR_OVER

    Draw source layer on top of destination layer. (bounded)

.. data:: OPERATOR_IN

    Draw source where there was destination content. (unbounded)

.. data:: OPERATOR_OUT

    Draw source where there was no destination content. (unbounded)

.. data:: OPERATOR_ATOP

    Draw source on top of destination content and only there.

.. data:: OPERATOR_DEST

    Ignore the source.

.. data:: OPERATOR_DEST_OVER

    Draw destination on top of source.

.. data:: OPERATOR_DEST_IN

    Leave destination only where there was source content. (unbounded)

.. data:: OPERATOR_DEST_OUT

    Leave destination only where there was no source content.

.. data:: OPERATOR_DEST_ATOP

    Leave destination on top of source content and only there. (unbounded)

.. data:: OPERATOR_XOR

    Source and destination are shown where there is only one of them.

.. data:: OPERATOR_ADD

    Source and destination layers are accumulated.

.. data:: OPERATOR_SATURATE

    Like :obj:`OPERATOR_OVER`,
    but assuming source and destination are disjoint geometries.

.. data:: OPERATOR_MULTIPLY

    Source and destination layers are multiplied.
    This causes the result to be at least as dark as the darker inputs.
    (Since 1.10)


.. data:: OPERATOR_SCREEN

    Source and destination are complemented and multiplied.
    This causes the result to be at least as light as the lighter inputs.
    (Since cairo 1.10)


.. data:: OPERATOR_OVERLAY

    Multiplies or screens, depending on the lightness of the destination color.
    (Since cairo 1.10)

.. data:: OPERATOR_DARKEN

    Replaces the destination with the source if it is darker,
    otherwise keeps the source. (Since cairo 1.10)


.. data:: OPERATOR_LIGHTEN

    Replaces the destination with the source if it is lighter,
    otherwise keeps the source. (Since cairo 1.10)


.. data:: OPERATOR_COLOR_DODGE

    Brightens the destination color to reflect the source color.
    (Since cairo 1.10)


.. data:: OPERATOR_COLOR_BURN

    Darkens the destination color to reflect the source color.
    (Since cairo 1.10)


.. data:: OPERATOR_HARD_LIGHT

    Multiplies or screens, dependent on source color. (Since cairo 1.10)


.. data:: OPERATOR_SOFT_LIGHT

    Darkens or lightens, dependent on source color. (Since cairo 1.10)


.. data:: OPERATOR_DIFFERENCE

    Takes the difference of the source and destination color.
    (Since cairo 1.10)


.. data:: OPERATOR_EXCLUSION

    Produces an effect similar to difference, but with lower contrast.
    (Since cairo 1.10)

.. data:: OPERATOR_HSL_HUE

    Creates a color with the hue of the source
    and the saturation and luminosity of the target. (Since cairo 1.10)

.. data:: OPERATOR_HSL_SATURATION

    Creates a color with the saturation of the source
    and the hue and luminosity of the target.
    Painting with this mode onto a gray area produces no change.
    (Since cairo 1.10)

.. data:: OPERATOR_HSL_COLOR

    Creates a color with the hue and saturation of the source
    and the luminosity of the target.
    This preserves the gray levels of the target
    and is useful for coloring monochrome images or tinting color images.
    (Since cairo 1.10)

.. data:: OPERATOR_HSL_LUMINOSITY

    Creates a color with the luminosity of the source
    and the hue and saturation of the target.
    This produces an inverse effect to :obj:`OPERATOR_HSL_COLOR`.
    (Since cairo 1.10)


.. _ANTIALIAS:

Antialiasing mode
-----------------

Specifies the type of antialiasing to do when rendering text or shapes.

.. data:: ANTIALIAS_DEFAULT

    Use the default antialiasing for  the subsystem and target device.

.. data:: ANTIALIAS_NONE

    Use a bilevel alpha mask.

.. data:: ANTIALIAS_GRAY

    Perform single-color antialiasing.

.. data:: ANTIALIAS_SUBPIXEL

    Perform antialiasing by taking advantage of the order
    of subpixel elements on devices such as LCD panels.

As it is not necessarily clear from the above what advantages
a particular antialias method provides,
since cairo 1.12, there is also a set of hints:

.. data:: ANTIALIAS_FAST

    Allow the backend to degrade raster quality for speed.

.. data:: ANTIALIAS_GOOD

    A balance between speed and quality.

.. data:: ANTIALIAS_BEST

    A high-fidelity, but potentially slow, raster mode.

These make no guarantee on how the backend will perform its rasterisation
(if it even rasterises!),
nor that they have any differing effect other than to enable
some form of antialiasing.
In the case of glyph rendering,
:obj:`ANTIALIAS_FAST` and :obj:`ANTIALIAS_GOOD`
will be mapped to :obj:`ANTIALIAS_GRAY`,
with :obj:`ANTIALIAS_BEST` being equivalent to :obj:`ANTIALIAS_SUBPIXEL`.

The interpretation of :obj:`ANTIALIAS_DEFAULT` is left entirely up to
the backend, typically this will be similar to :obj:`ANTIALIAS_GOOD`.


.. _FILL_RULE:

Fill rule
---------

Used to select how paths are filled.
For both fill rules, whether or not a point is included in the fill
is determined by taking a ray from that point to infinity
and looking at intersections with the path.
The ray can be in any direction,
as long as it doesn't pass through the end point of a segment
or have a tricky intersection such as intersecting tangent to the path.
(Note that filling is not actually implemented in this way.
This is just a description of the rule that is applied.)

The default fill rule is :obj:`FILL_RULE_WINDING`.

New entries may be added in future versions.


.. data:: FILL_RULE_WINDING

    If the path crosses the ray fromleft-to-right, counts +1.
    If the path crosses the rayfrom right to left, counts -1.
    (Left and right are determined from the perspective
    of looking along the ray from the starting point.)
    If the total count is non-zero, the point will be filled.

.. data:: FILL_RULE_EVEN_ODD

     Counts the total number of intersections,
     without regard to the orientation of the contour.
     If the total number of intersections is odd, the point will be filled.


.. _LINE_CAP:

Line cap style
--------------

Specifies how to render the endpoints of the path when stroking.

The default line cap style is :obj:`LINE_CAP_BUTT`.

.. data:: LINE_CAP_BUTT

    Start (stop) the line exactly at the start (end) point.

.. data:: LINE_CAP_ROUND

    Use a round ending, the center of the circle is the end point.

.. data:: LINE_CAP_SQUARE

    Use squared ending, the center of the square is the end point.


.. _LINE_JOIN:

Line join style
---------------

Specifies how to render the junction of two lines when stroking.

The default line join style is :obj:`LINE_JOIN_MITER`.


.. data:: LINE_JOIN_MITER

    Use a sharp (angled) corner, see :meth:`Context.set_miter_limit`.

.. data:: LINE_JOIN_ROUND

    Use a rounded join, the center of the circle is the joint point.

.. data:: LINE_JOIN_BEVEL

    Use a cut-off join, the join is cut off at half the line width
    from the joint point.


.. _FONT_SLANT:

Font slant
----------

Specifies variants of a font face based on their slant.

.. data:: FONT_SLANT_NORMAL

    Upright font style.

.. data:: FONT_SLANT_ITALIC

    Italic font style.

.. data:: FONT_SLANT_OBLIQUE

    Oblique font style.


.. _FONT_WEIGHT:

Font weight
-----------

Specifies variants of a font face based on their weight.

.. data:: FONT_WEIGHT_NORMAL

    Normal font weight.

.. data:: FONT_WEIGHT_BOLD

    Bold font weight.


.. _SUBPIXEL_ORDER:

Subpixel order
--------------

The subpixel order specifies the order of color elements within each pixel
on the display device when rendering with an antialiasing mode of
:obj:`ANTIALIAS_SUBPIXEL`.


.. data:: SUBPIXEL_ORDER_DEFAULT

    Use the default subpixel order for for the target device.

.. data:: SUBPIXEL_ORDER_RGB

    Subpixel elements are arranged horizontally with red at the left.

.. data:: SUBPIXEL_ORDER_BGR

    Subpixel elements are arranged horizontally with blue at the left.

.. data:: SUBPIXEL_ORDER_VRGB

    Subpixel elements are arranged vertically with red at the top.

.. data:: SUBPIXEL_ORDER_VBGR

    Subpixel elements are arranged vertically with blue at the top.


.. _HINT_STYLE:

Hint style
----------

Specifies the type of hinting to do on font outlines.
Hinting is the process of fitting outlines to the pixel grid
in order to improve the appearance of the result.
Since hinting outlines involves distorting them,
it also reduces the faithfulness to the original outline shapes.
Not all of the outline hinting styles are supported by all font backends.

New entries may be added in future versions.


.. data:: HINT_STYLE_DEFAULT

    Use the default hint style for font backend and target device.

.. data:: HINT_STYLE_NONE

    Do not hint outlines.

.. data:: HINT_STYLE_SLIGHT

     Hint outlines slightly to improve contrast
     while retaining good fidelity to the original shapes.

.. data:: HINT_STYLE_MEDIUM

    Hint outlines with medium strength
    giving a compromise between fidelity to the original shapes and contrast.

.. data:: HINT_STYLE_FULL

    Hint outlines to maximize contrast.


.. _HINT_METRICS:

Metrics hinting mode
--------------------

Specifies whether to hint font metrics;
hinting font metrics means quantizing them
so that they are integer values in device space.
Doing this improves the consistency of letter and line spacing,
however it also means that text will be laid out differently
at different zoom factors.


.. data:: HINT_METRICS_DEFAULT

    Hint metrics in the default manner for the font backend and target device.

.. data:: HINT_METRICS_OFF

    Do not hint font metrics.

.. data:: HINT_METRICS_ON

    Hint font metrics.

..
    .. _FONT_TYPE:

    Font type
    ---------

    Used to describe the type of a given font face or scaled font.
    The font types are also known as "font backends" within cairo.

    The type of a font face is determined by the function used to create it.

    The type of a scaled font is determined by the type of the font face
    passed to :class:`ScaledFont`.

    New entries may be added in future versions.


    .. data:: FONT_TYPE_TOY

        The font was created using cairo's toy font api.

    .. data:: FONT_TYPE_FT

        The font is of type FreeType.

    .. data:: FONT_TYPE_WIN32

        The font is of type Win32.

    .. data:: FONT_TYPE_QUARTZ

        The font is of type Quartz.

    .. data:: FONT_TYPE_USER

        The font was create using cairo's user font api. (Since cairo 1.8)


.. _PATH_OPERATION:

Path operation
--------------

Used to describe the type of one portion of a path when represented as a list.
See :meth:`Context.copy_path` for details.


.. data:: PATH_MOVE_TO

.. data:: PATH_LINE_TO

.. data:: PATH_CURVE_TO

.. data:: PATH_CLOSE_PATH


.. _EXTEND:

Pattern extend
--------------

Used to describe how pattern color/alpha will be determined
for areas "outside" the pattern's natural area,
(for example, outside the surface bounds or outside the gradient geometry).

Mesh patterns are not affected by the extend mode.

The default extend mode is
:obj:`EXTEND_NONE` for :class:`SurfacePattern`
and :obj:`EXTEND_PAD` for :class:`Gradient` patterns.

New entries may be added in future versions.


.. data:: EXTEND_NONE

    Pixels outside of the source pattern are fully transparent.

.. data:: EXTEND_REPEAT

    The pattern is tiled by repeating.

.. data:: EXTEND_REFLECT

    The pattern is tiled by reflecting at the edges.

.. data:: EXTEND_PAD

    Pixels outside of the pattern copy the closest pixel from the source.


.. _FILTER:

Pixel filter
------------

Used to indicate what filtering should be applied
when reading pixel values from patterns.
See :meth:`Pattern.set_filter` for indicating the desired filter
to be used with a particular pattern.


.. data:: FILTER_FAST

    A high-performance filter,
    with quality similar to :obj:`FILTER_NEAREST`.

.. data:: FILTER_GOOD

    A reasonable-performance filter,
    with quality similar to :obj:`FILTER_BILINEAR`.

.. data:: FILTER_BEST

    The highest-quality available,
    performance may not be suitable for interactive use.

.. data:: FILTER_NEAREST

    Nearest-neighbor filtering.

.. data:: FILTER_BILINEAR

    Linear interpolation in two dimensions.

.. data:: FILTER_GAUSSIAN

    This filter value is currently unimplemented,
    and should not be used in current code.


.. _PDF_VERSION:

PDF version
-----------

Used to describe the version number of the PDF specification
that a generated PDF file will conform to.

.. data:: PDF_VERSION_1_4

    The version 1.4 of the PDF specification.

.. data:: PDF_VERSION_1_5

    The version 1.5 of the PDF specification.


.. _PS_LEVEL:

PostScript level
----------------

Used to describe the language level of the PostScript Language Reference
that a generated PostScript file will conform to.

.. data:: PS_LEVEL_2

    The language level 2 of the PostScript specification.

.. data:: PS_LEVEL_3

    The language level 3 of the PostScript specification.


.. _SVG_VERSION:

SVG version
-----------

Used to describe the version number of the SVG specification
that a generated SVG file will conform to.

.. data:: SVG_VERSION_1_1

    The version 1.1 of the SVG specification.

.. data:: SVG_VERSION_1_2

    The version 1.2 of the SVG specification.


.. _cluster-flags:

Cluster flags
-------------

Specifies properties of a text cluster mapping.
Flags are integer values representing a bit field.

.. data:: TEXT_CLUSTER_FLAG_BACKWARD
    :annotation: = 0x00000001

    The clusters in the cluster array
    map to glyphs in the glyph array from end to start. (Since 1.8) 
