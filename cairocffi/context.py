# coding: utf8
"""
    cairocffi.context
    ~~~~~~~~~~~~~~~~~

    Bindings for Context objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status, Matrix
from .patterns import Pattern
from .surfaces import Surface
from .fonts import FontFace, ScaledFont, FontOptions, _encode_string
from .compat import xrange


PATH_POINTS_PER_TYPE = {
    'MOVE_TO': 1,
    'LINE_TO': 1,
    'CURVE_TO': 3,
    'CLOSE_PATH': 0}


def _encode_path(path_items):
    """Take an iterable of ``(path_type, points)`` tuples
    and return a ``(path, data)`` tuple of cdata object.

    :obj:`path` points to a cairo_path_t struct that can be used
    as long as the two cdata objects live.

    See :meth:`Context.copy_path` for the data structure.

    """
    points_per_type = PATH_POINTS_PER_TYPE
    path_items = list(path_items)
    length = 0
    for path_type, coordinates in path_items:
        num_points = points_per_type[path_type]
        length += 1 + num_points  # 1 header + N points
        if len(coordinates) != 2 * num_points:
            raise ValueError('Expected %d coordinates, got %d.' % (
                2 * num_points, len(coordinates)))

    data = ffi.new('cairo_path_data_t[]', length)
    position = 0
    for path_type, coordinates in path_items:
        header = data[position].header
        header.type = path_type
        header.length = 1 + len(coordinates) // 2
        position += 1
        for i in xrange(0, len(coordinates), 2):
            point = data[position].point
            point.x = coordinates[i]
            point.y = coordinates[i + 1]
            position += 1
    path = ffi.new('cairo_path_t *', ('SUCCESS', data, length))
    return path, data


def _iter_path(pointer):
    """Take a cairo_path_t * pointer and yield ``(path_type, points)`` tuples.

    See :meth:`Context.copy_path` for the data structure.

    """
    _check_status(pointer.status)
    data = pointer.data
    num_data = pointer.num_data
    points_per_type = PATH_POINTS_PER_TYPE
    position = 0
    while position < num_data:
        path_data = data[position]
        path_type = path_data.header.type
        points = ()
        for i in xrange(points_per_type[path_type]):
            point = data[position + i + 1].point
            points += (point.x, point.y)
        yield (path_type, points)
        position += path_data.header.length


class Context(object):
    """A :class:`Context` contains the current state of the rendering device,
    including coordinates of yet to be drawn shapes.

    Cairo contexts are central to cairo
    and all drawing with cairo is always done to a :class:`Context` object.

    :param target: The target :class:`Surface` object.

    Cairo contexts can be used as Python :ref:`context managers <with>`.
    See :meth:`save`.

    """
    def __init__(self, target):
        self._init_pointer(cairo.cairo_create(target._pointer))

    def _init_pointer(self, pointer):
        self._pointer = ffi.gc(pointer, cairo.cairo_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_status(self._pointer))

    @classmethod
    def _from_pointer(cls, pointer, incref):
        """Wrap an existing :c:type:`cairo_t *` cdata pointer.

        :type incref: bool
        :param incref:
            Whether increase the :ref:`reference count <refcounting>` now.
        :return:
            A new :class:`Context` instance.

        """
        if pointer == ffi.NULL:
            raise ValueError('Null pointer')
        if incref:
            cairo.cairo_reference(pointer)
        self = object.__new__(cls)
        cls._init_pointer(self, pointer)
        return self

    def get_target(self):
        """Return this context’s target surface.

        :returns:
            An instance of :class:`Surface` or one of its sub-classes,
            a new Python object referencing the existing cairo surface.

        """
        return Surface._from_pointer(
            cairo.cairo_get_target(self._pointer), incref=True)

    ##
    ##  Save / restore
    ##

    def save(self):
        """Makes a copy of the current state of this context
        and saves it on an internal stack of saved states.
        When :meth:`restore` is called,
        the context will be restored to the saved state.
        Multiple calls to :meth:`save` and :meth:`restore` can be nested;
        each call to :meth:`restore` restores the state
        from the matching paired :meth:`save`.

        Instead of using :meth:`save` and :meth:`restore` directly,
        it is recommended to use a :ref:`with statement <with>`::

            with context:
                do_something(context)

        … which is equivalent to::

            context.save()
            try:
                do_something(context)
            finally:
                context.restore()

        """
        cairo.cairo_save(self._pointer)
        self._check_status()

    def restore(self):
        """Restores the context to the state saved
        by a preceding call to :meth:`save`
        and removes that state from the stack of saved states.

        """
        cairo.cairo_restore(self._pointer)
        self._check_status()

    def __enter__(self):
        self.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore()

    ##
    ##  Groups
    ##

    def push_group(self):
        """Temporarily redirects drawing to an intermediate surface
        known as a group.
        The redirection lasts until the group is completed
        by a call to :meth:`pop_group` or :meth:`pop_group_to_source`.
        These calls provide the result of any drawing
        to the group as a pattern,
        (either as an explicit object, or set as the source pattern).

        This group functionality can be convenient
        for performing intermediate compositing.
        One common use of a group is to render objects
        as opaque within the group,  (so that they occlude each other),
        and then blend the result with translucence onto the destination.

        Groups can be nested arbitrarily deep
        by making balanced calls to :meth:`push_group` / :meth:`pop_group`.
        Each call pushes / pops the new target group onto / from a stack.

        The :meth:`group` method calls :meth:`save`
        so that any changes to the graphics state
        will not be visible outside the group,
        (the pop_group methods call :meth:`restore`).

        By default the intermediate group will have
        a content type of :obj:`COLOR_ALPHA <CONTENT_COLOR_ALPHA>`.
        Other content types can be chosen for the group
        by using :meth:`push_group_with_content` instead.

        As an example,
        here is how one might fill and stroke a path with translucence,
        but without any portion of the fill being visible under the stroke::

            context.push_group()
            context.set_source(fill_pattern)
            context.fill_preserve()
            context.set_source(stroke_pattern)
            context.stroke()
            context.pop_group_to_source()
            context.paint_with_alpha(alpha)

        """
        cairo.cairo_push_group(self._pointer)
        self._check_status()

    def push_group_with_content(self, content):
        """Temporarily redirects drawing to an intermediate surface
        known as a group.
        The redirection lasts until the group is completed
        by a call to :meth:`pop_group` or :meth:`pop_group_to_source`.
        These calls provide the result of any drawing
        to the group as a pattern,
        (either as an explicit object, or set as the source pattern).

        The group will have a content type of :obj:`content`.
        The ability to control this content  type
        is the only distinction between this method and :meth:`push_group`
        which you should see for a more detailed description
        of group rendering.

        :param content: A :ref:`CONTENT` string.

        """
        cairo.cairo_push_group_with_content(self._pointer, content)
        self._check_status()

    def pop_group(self):
        """Terminates the redirection begun by a call to :meth:`push_group`
        or :meth:`push_group_with_content`
        and returns a new pattern containing the results
        of all drawing operations performed to the group.

        The :meth:`pop_group` method calls :meth:`restore`,
        (balancing a call to :meth:`save` by the push_group method),
        so that any changes to the graphics state
        will not be visible outside the group.

        :returns:
            A newly created :class:`SurfacePattern`
            containing the results of all drawing operations
            performed to the group.

        """
        return Pattern._from_pointer(
            cairo.cairo_pop_group(self._pointer), incref=False)

    def pop_group_to_source(self):
        """Terminates the redirection begun by a call to :meth:`push_group`
        or :meth:`push_group_with_content`
        and installs the resulting pattern
        as the source pattern in the given cairo context.

        The behavior of this method is equivalent to::

            context.set_source(context.pop_group())

        """
        cairo.cairo_pop_group_to_source(self._pointer)
        self._check_status()

    def get_group_target(self):
        """Returns the current destination surface for the context.
        This is either the original target surface
        as passed to :class:`Context`
        or the target surface for the current group as started
        by the most recent call to :meth:`push_group`
        or :meth:`push_group_with_content`.

        """
        return Surface._from_pointer(
            cairo.cairo_get_group_target(self._pointer), incref=True)

    ##
    ##  Sources
    ##

    def set_source_rgba(self, red, green, blue, alpha=1):
        """Sets the source pattern within this context to a solid color.
        This color will then be used for any subsequent drawing operation
        until a new source pattern is set.

        The color and alpha components are
        floating point numbers  in the range 0 to 1.
        If the values passed in are outside that range, they will be clamped.

        The default source pattern is opaque black,
        (that is, it is equivalent to ``context.set_source_rgba(0, 0, 0)``).

        :param red: Red component of the color.
        :param green: Green component of the color.
        :param blue: Blue component of the color.
        :param alpha:
            Alpha component of the color.
            1 (the default) is opaque, 0 fully transparent.
        :type red: float
        :type green: float
        :type blue: float
        :type alpha: float

        """
        cairo.cairo_set_source_rgba(self._pointer, red, green, blue, alpha)
        self._check_status()

    def set_source_rgb(self, red, green, blue):
        """Same as :meth:`set_source_rgba` with alpha always 1.
        Exists for compatibility with pycairo.

        """
        cairo.cairo_set_source_rgb(self._pointer, red, green, blue)
        self._check_status()

    def set_source_surface(self, surface, x=0, y=0):
        """This is a convenience method for creating a pattern from surface
        and setting it as the source in this context with :meth:`set_source`.

        The :obj:`x` and :obj:`y` parameters give the user-space coordinate
        at which the surface origin should appear.
        (The surface origin is its upper-left corner
        before any transformation has been applied.)
        The :obj:`x` and :obj:`y` parameters are negated
        and then set as translation values in the pattern matrix.

        Other than the initial translation pattern matrix, as described above,
        all other pattern attributes, (such as its extend mode),
        are set to the default values as in :class:`SurfacePattern`.
        The resulting pattern can be queried with :meth:`get_source`
        so that these attributes can be modified if desired,
        (eg. to create a repeating pattern with :meth:`Pattern.set_extend`).

        :param surface:
            A :class:`Surface` to be used to set the source pattern.
        :param x: User-space X coordinate for surface origin.
        :param y: User-space Y coordinate for surface origin.
        :type x: float
        :type y: float

        """
        cairo.cairo_set_source_surface(self._pointer, surface._pointer, x, y)
        self._check_status()

    def set_source(self, source):
        """Sets the source pattern within this context to :obj:`source`.
        This pattern will then be used for any subsequent drawing operation
        until a new source pattern is set.

        .. note::

            The pattern's transformation matrix will be locked
            to the user space in effect at the time of :meth:`set_source`.
            This means that further modifications
            of the current transformation matrix
            will not affect the source pattern.
            See :meth:`Pattern.set_matrix`.

        The default source pattern is opaque black,
        (that is, it is equivalent to ``context.set_source_rgba(0, 0, 0)``).

        :param source:
            A :class:`Pattern` to be used
            as the source for subsequent drawing operations.

        """
        cairo.cairo_set_source(self._pointer, source._pointer)
        self._check_status()

    def get_source(self):
        """Return this context’s source.

        :returns:
            An instance of :class:`Pattern` or one of its sub-classes,
            a new Python object referencing the existing cairo pattern.

        """
        return Pattern._from_pointer(
            cairo.cairo_get_source(self._pointer), incref=True)

    ##
    ##  Context parameters
    ##

    def set_antialias(self, antialias):
        """Set the :ref:`ANTIALIAS` of the rasterizer used for drawing shapes.
        This value is a hint,
        and a particular backend may or may not support a particular value.
        At the current time,
        no backend supports :obj:`SUBPIXEL <ANTIALIAS_SUBPIXEL>`
        when drawing shapes.

        Note that this option does not affect text rendering,
        instead see :meth:`FontOptions.set_antialias`.

        :param antialias: An :ref:`ANTIALIAS` string.

        """
        cairo.cairo_set_antialias(self._pointer, antialias)
        self._check_status()

    def get_antialias(self):
        """Return the :ref:`ANTIALIAS` string."""
        return cairo.cairo_get_antialias(self._pointer)

    def set_dash(self, dashes, offset=0):
        """Sets the dash pattern to be used by :meth:`stroke`.
        A dash pattern is specified by dashes, a list of positive values.
        Each value provides the length of alternate "on" and "off"
        portions of the stroke.
        :obj:`offset` specifies an offset into the pattern
        at which the stroke begins.

        Each "on" segment will have caps applied
        as if the segment were a separate sub-path.
        In particular, it is valid to use an "on" length of 0
        with :obj:`LINE_CAP_ROUND` or :obj:`LINE_CAP_SQUARE`
        in order to distributed dots or squares along a path.

        Note: The length values are in user-space units
        as evaluated at the time of stroking.
        This is not necessarily the same as the user space
        at the time of :meth:`set_dash`.

        If :obj:`dashes` is empty dashing is disabled.
        If it is of length 1 a symmetric pattern is assumed
        with alternating on and off portions of the size specified
        by the single value.

        :param dashes:
            A list of floats specifying alternate lengths
            of on and off stroke portions.
        :type offset: float
        :param offset:
            An offset into the dash pattern at which the stroke should start.
        :raises:
            :exc:`CairoError`
            if any value in dashes is negative,
            or if all values are 0.
            The context  will be put into an error state.

        """
        cairo.cairo_set_dash(
            self._pointer, ffi.new('double[]', dashes), len(dashes), offset)
        self._check_status()

    def get_dash(self):
        """Return the current dash pattern.

        :returns:
            A ``(dashes, offset)`` tuple of a list and a float.
            :obj:`dashes` is a list of floats,
            empty if no dashing is in effect.

        """
        dashes = ffi.new('double[]', cairo.cairo_get_dash_count(self._pointer))
        offset = ffi.new('double *')
        cairo.cairo_get_dash(self._pointer, dashes, offset)
        self._check_status()
        return list(dashes), offset[0]

    def get_dash_count(self):
        """Same as ``len(context.get_dash()[0])``."""
        # Not really useful with get_dash() returning a list,
        # but retained for compatibility with pycairo.
        return cairo.cairo_get_dash_count(self._pointer)

    def set_fill_rule(self, fill_rule):
        """Set the current :ref:`FILL_RULE` within the cairo context.
        The fill rule is used to determine which regions are inside
        or outside a complex (potentially self-intersecting) path.
        The current fill rule affects both :meth:`fill` and :meth:`clip`.

        The default fill rule is :obj:`WINDING <FILL_RULE_WINDING>`.

        :param fill_rule: A :ref:`FILL_RULE` string.

        """
        cairo.cairo_set_fill_rule(self._pointer, fill_rule)
        self._check_status()

    def get_fill_rule(self):
        """Return the current :ref:`FILL_RULE` string."""
        return cairo.cairo_get_fill_rule(self._pointer)

    def set_line_cap(self, line_cap):
        """Set the current :ref:`LINE_CAP` within the cairo context.
        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default line cap is :obj:`BUTT <LINE_CAP_BUTT>`.

        :param line_cap: A :ref:`LINE_CAP` string.

        """
        cairo.cairo_set_line_cap(self._pointer, line_cap)
        self._check_status()

    def get_line_cap(self):
        """Return the current :ref:`LINE_CAP` string."""
        return cairo.cairo_get_line_cap(self._pointer)

    def set_line_join(self, line_join):
        """Set the current :ref:`LINE_JOIN` within the cairo context.
        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default line cap is :obj:`MITER <LINE_JOIN_MITER>`.

        :param line_join: A :ref:`LINE_JOIN` string.

        """
        cairo.cairo_set_line_join(self._pointer, line_join)
        self._check_status()

    def get_line_join(self):
        """Return the current :ref:`LINE_JOIN` string."""
        return cairo.cairo_get_line_join(self._pointer)

    def set_line_width(self, width):
        """Sets the current line width within the cairo context.
        The line width value specifies the diameter of a pen
        that is circular in user space,
        (though device-space pen may be an ellipse in general
        due to scaling / shear / rotation of the CTM).

        .. note::
            When the description above refers to user space and CTM
            it refers to the user space and CTM in effect
            at the time of the stroking operation,
            not the user space and CTM in effect
            at the time of the call to :meth:`set_line_width`.
            The simplest usage makes both of these spaces identical.
            That is, if there is no change to the CTM
            between a call to :meth:`set_line_width`
            and the stroking operation,
            then one can just pass user-space values to :meth:`set_line_width`
            and ignore this note.

        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default line width value is 2.0.

        :type width: float
        :param width: The new line width.

        """
        cairo.cairo_set_line_width(self._pointer, width)
        self._check_status()

    def get_line_width(self):
        """Return the current line width as a float."""
        return cairo.cairo_get_line_width(self._pointer)

    def set_miter_limit(self, limit):
        """Sets the current miter limit within the cairo context.

        If the current line join style is set to :obj:`MITER <LINE_JOIN_MITER>`
        (see :meth:`set_line_join`),
        the miter limit is used to determine
        whether the lines should be joined with a bevel instead of a miter.
        Cairo divides the length of the miter by the line width.
        If the result is greater than the miter limit,
        the style is converted to a bevel.

        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default miter limit value is 10.0,
        which will convert joins with interior angles less than 11 degrees
        to bevels instead of miters.
        For reference,
        a miter limit of 2.0 makes the miter cutoff at 60 degrees,
        and a miter limit of 1.414 makes the cutoff at 90 degrees.

        A miter limit for a desired angle can be computed as:
        ``miter_limit = 1. / sin(angle / 2.)``

        :param limit: The miter limit to set.
        :type limit: float

        """
        cairo.cairo_set_miter_limit(self._pointer, limit)
        self._check_status()

    def get_miter_limit(self):
        """Return the current miter limit as a float."""
        return cairo.cairo_get_miter_limit(self._pointer)

    def set_operator(self, operator):
        """Set the current :ref:`OPERATOR`
        to be used for all drawing operations.

        The default operator is :obj:`OVER <OPERATOR_OVER>`.

        :param operator: A :ref:`OPERATOR` string.

        """
        cairo.cairo_set_operator(self._pointer, operator)
        self._check_status()

    def get_operator(self):
        """Return the current :ref:`OPERATOR` string."""
        return cairo.cairo_get_operator(self._pointer)

    def set_tolerance(self, tolerance):
        """Sets the tolerance used when converting paths into trapezoids.
        Curved segments of the path will be subdivided
        until the maximum deviation between the original path
        and the polygonal approximation is less than tolerance.
        The default value is 0.1.
        A larger value will give better performance,
        a smaller value, better appearance.
        (Reducing the value from the default value of 0.1
        is unlikely to improve appearance significantly.)
        The accuracy of paths within Cairo is limited
        by the precision of its internal arithmetic,
        and the prescribed tolerance is restricted
        to the smallest representable internal value.

        :type tolerance: float
        :param tolerance : The tolerance, in device units (typically pixels)

        """
        cairo.cairo_set_tolerance(self._pointer, tolerance)
        self._check_status()

    def get_tolerance(self):
        """Return the current tolerance as a float."""
        return cairo.cairo_get_tolerance(self._pointer)

    ##
    ##  CTM: Current transformation matrix
    ##

    def translate(self, tx, ty):
        cairo.cairo_translate(self._pointer, tx, ty)
        self._check_status()

    def scale(self, sx, sy=None):
        if sy is None:
            sy = sx
        cairo.cairo_scale(self._pointer, sx, sy)
        self._check_status()

    def rotate(self, radians):
        cairo.cairo_rotate(self._pointer, radians)
        self._check_status()

    def transform(self, matrix):
        cairo.cairo_transform(self._pointer, matrix._pointer)
        self._check_status()

    def get_matrix(self):
        matrix = Matrix()
        cairo.cairo_get_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def set_matrix(self, matrix):
        cairo.cairo_set_matrix(self._pointer, matrix._pointer)
        self._check_status()

    def identity_matrix(self):
        cairo.cairo_identity_matrix(self._pointer)
        self._check_status()

    def user_to_device(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_user_to_device(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def user_to_device_distance(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_user_to_device_distance(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def device_to_user(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_device_to_user(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def device_to_user_distance(self, x, y):
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_device_to_user_distance(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    ##
    ##  Path
    ##

    def arc(self, xc, yc, radius, angle1, angle2):
        cairo.cairo_arc(self._pointer, xc, yc, radius, angle1, angle2)
        self._check_status()

    def arc_negative(self, xc, yc, radius, angle1, angle2):
        cairo.cairo_arc_negative(self._pointer, xc, yc, radius, angle1, angle2)
        self._check_status()

    def rectangle(self, x, y, width, height):
        cairo.cairo_rectangle(self._pointer, x, y, width, height)
        self._check_status()

    def move_to(self, x, y):
        cairo.cairo_move_to(self._pointer, x, y)
        self._check_status()

    def rel_move_to(self, dx, dy):
        cairo.cairo_rel_move_to(self._pointer, dx, dy)
        self._check_status()

    def line_to(self, x, y):
        cairo.cairo_line_to(self._pointer, x, y)
        self._check_status()

    def rel_line_to(self, dx, dy):
        cairo.cairo_rel_line_to(self._pointer, dx, dy)
        self._check_status()

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        cairo.cairo_curve_to(self._pointer, x1, y1, x2, y2, x3, y3)
        self._check_status()

    def rel_curve_to(self, dx1, dy1, dx2, dy2, dx3, dy3):
        cairo.cairo_rel_curve_to(self._pointer, dx1, dy1, dx2, dy2, dx3, dy3)
        self._check_status()

    def close_path(self):
        cairo.cairo_close_path(self._pointer)
        self._check_status()

    def copy_path(self):
        path = cairo.cairo_copy_path(self._pointer)
        result = list(_iter_path(path))
        cairo.cairo_path_destroy(path)
        return result

    def copy_path_flat(self):
        path = cairo.cairo_copy_path_flat(self._pointer)
        result = list(_iter_path(path))
        cairo.cairo_path_destroy(path)
        return result

    def append_path(self, path):
        # Both objects need to stay alive
        # until after cairo.cairo_append_path() is finished, but not after.
        path, _ = _encode_path(path)
        cairo.cairo_append_path(self._pointer, path)
        self._check_status()

    def path_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_path_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def new_path(self):
        cairo.cairo_new_path(self._pointer)
        self._check_status()

    def new_sub_path(self):
        cairo.cairo_new_sub_path(self._pointer)
        self._check_status()

    def get_current_point(self):
        """Return the (x, y) coordinates of the current point,
        or (0., 0.) if there is no current point.

        """
        # I’d prefer returning None if self.has_current_point() is False
        # But keep (0, 0) for compat with pycairo.
        xy = ffi.new('double[2]')
        cairo.cairo_get_current_point(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def has_current_point(self):
        return bool(cairo.cairo_has_current_point(self._pointer))

    ##
    ##  Drawing operators
    ##

    def paint(self):
        cairo.cairo_paint(self._pointer)
        self._check_status()

    def paint_with_alpha(self, alpha):
        cairo.cairo_paint_with_alpha(self._pointer, alpha)
        self._check_status()

    def fill(self):
        cairo.cairo_fill(self._pointer)
        self._check_status()

    def fill_preserve(self):
        cairo.cairo_fill_preserve(self._pointer)
        self._check_status()

    def fill_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_fill_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def in_fill(self, x, y):
        return bool(cairo.cairo_in_fill(self._pointer, x, y))

    def stroke(self):
        cairo.cairo_stroke(self._pointer)
        self._check_status()

    def stroke_preserve(self):
        cairo.cairo_stroke_preserve(self._pointer)
        self._check_status()

    def stroke_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_stroke_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def in_stroke(self, x, y):
        return bool(cairo.cairo_in_stroke(self._pointer, x, y))

    def clip(self):
        cairo.cairo_clip(self._pointer)
        self._check_status()

    def clip_preserve(self):
        cairo.cairo_clip_preserve(self._pointer)
        self._check_status()

    def clip_extents(self):
        extents = ffi.new('double[4]')
        cairo.cairo_clip_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def copy_clip_rectangle_list(self):
        rectangle_list = cairo.cairo_copy_clip_rectangle_list(self._pointer)
        _check_status(rectangle_list.status)
        rectangles = rectangle_list.rectangles
        result = []
        for i in xrange(rectangle_list.num_rectangles):
            rect = rectangles[i]
            result.append((rect.x, rect.y, rect.width, rect.height))
        cairo.cairo_rectangle_list_destroy(rectangle_list)
        return result

    def in_clip(self, x, y):
        return bool(cairo.cairo_in_clip(self._pointer, x, y))

    def reset_clip(self):
        cairo.cairo_reset_clip(self._pointer)
        self._check_status()

    def mask(self, pattern):
        cairo.cairo_mask(self._pointer, pattern._pointer)
        self._check_status()

    def mask_surface(self, surface, surface_x=0, surface_y=0):
        cairo.cairo_mask_surface(
            self._pointer, surface._pointer, surface_x, surface_y)
        self._check_status()

    ##
    ##  Fonts
    ##

    def select_font_face(self, family='', slant='NORMAL', weight='NORMAL'):
        cairo.cairo_select_font_face(
            self._pointer, _encode_string(family), slant, weight)
        self._check_status()

    def get_font_face(self):
        return FontFace._from_pointer(
            cairo.cairo_get_font_face(self._pointer), incref=True)

    def set_font_face(self, font_face):
        cairo.cairo_set_font_face(self._pointer, font_face._pointer)
        self._check_status()

    def get_scaled_font(self):
        return ScaledFont._from_pointer(
            cairo.cairo_get_scaled_font(self._pointer), incref=True)

    def set_scaled_font(self, scaled_font):
        cairo.cairo_set_scaled_font(self._pointer, scaled_font._pointer)
        self._check_status()

    def get_font_options(self):
        font_options = FontOptions()
        cairo.cairo_get_font_options(self._pointer, font_options._pointer)
        return font_options

    def set_font_options(self, font_options):
        cairo.cairo_set_font_options(self._pointer, font_options._pointer)
        self._check_status()

    def get_font_matrix(self):
        matrix = Matrix()
        cairo.cairo_get_font_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def set_font_matrix(self, matrix):
        cairo.cairo_set_font_matrix(self._pointer, matrix._pointer)
        self._check_status()

    def set_font_size(self, size):
        cairo.cairo_set_font_size(self._pointer, size)
        self._check_status()

    def font_extents(self):
        """Return the extents of the currently selected font.

        Values are given in the current user-space coordinate system.

        Because font metrics are in user-space coordinates, they are mostly,
        but not entirely, independent of the current transformation matrix.
        If you call :meth:`context.scale(2) <scale>`,
        text will be drawn twice as big,
        but the reported text extents will not be doubled.
        They will change slightly due to hinting
        (so you can't assume that metrics are independent
        of the transformation matrix),
        but otherwise will remain unchanged.

        :returns:
            A ``(ascent, descent, height, max_x_advance, max_y_advance)``
            tuple of floats.

        :obj:`ascent`
            The distance that the font extends above the baseline.
            Note that this is not always exactly equal to
            the maximum of the extents of all the glyphs in the font,
            but rather is picked to express the font designer's intent
            as to how the font should align with elements above it.
        :obj:`descent`
            The distance that the font extends below the baseline.
            This value is positive for typical fonts
            that include portions below the baseline.
            Note that this is not always exactly equal
            to the maximum of the extents of all the glyphs in the font,
            but rather is picked to express the font designer's intent
            as to how the font should align with elements below it.
        :obj:`height`
            The recommended vertical distance between baselines
            when setting consecutive lines of text with the font.
            This is greater than ``ascent + descent``
            by a quantity known as the line spacing or external leading.
            When space is at a premium, most fonts can be set
            with only a distance of ``ascent + descent`` between lines.
        :obj:`max_x_advance`
            The maximum distance in the X direction
            that the origin is advanced for any glyph in the font.
        :obj:`max_y_advance`
            The maximum distance in the Y direction
            that the origin is advanced for any glyph in the font.
            This will be zero for normal fonts used for horizontal writing.
            (The scripts of East Asia are sometimes written vertically.)

        """
        extents = ffi.new('cairo_font_extents_t *')
        cairo.cairo_font_extents(self._pointer, extents)
        self._check_status()
        # returning extents as is would be a nice API,
        # but return a tuple for compat with pycairo.
        return (
            extents.ascent, extents.descent, extents.height,
            extents.max_x_advance, extents.max_y_advance)

    ##
    ##  Text
    ##

    def text_extents(self, text):
        """Returns the extents for a string of text.

        The extents describe a user-space rectangle
        that encloses the "inked" portion of the text,
        (as it would be drawn by :meth:`show_text`).
        Additionally, the :obj:`x_advance` and :obj:`y_advance` values
        indicate the amount by which the current point would be advanced
        by :meth:`show_text`.

        Note that whitespace characters do not directly contribute
        to the size of the rectangle (:obj:`width` and :obj:`height`).
        They do contribute indirectly by changing the position
        of non-whitespace characters.
        In particular, trailing whitespace characters are likely
        to not affect the size of the rectangle,
        though they will affect the x_advance and y_advance values.

        Because text extents are in user-space coordinates,
        they are mostly, but not entirely,
        independent of the current transformation matrix.
        If you call :meth:`context.scale(2) <scale>`,
        text will be drawn twice as big,
        but the reported text extents will not be doubled.
        They will change slightly due to hinting
        (so you can't assume that metrics are independent
        of the transformation matrix),
        but otherwise will remain unchanged.

        :param text: The text to measure, as an Unicode or UTF-8 string.
        :returns:
            A ``(x_bearing, y_bearing, width, height, x_advance, y_advance)``
            tuple of floats.

        :obj:`x_bearing`
            The horizontal distance
            from the origin to the leftmost part of the glyphs as drawn.
            Positive if the glyphs lie entirely to the right of the origin.

        :obj:`y_bearing`
            The vertical distance
            from the origin to the topmost part of the glyphs as drawn.
            Positive only if the glyphs lie completely below the origin;
            will usually be negative.

        :obj:`width`
            Width of the glyphs as drawn.

        :obj:`height`
            Height of the glyphs as drawn.

        :obj:`x_advance`
            Distance to advance in the X direction
            after drawing these glyphs.

        :obj:`y_advance`
            Distance to advance in the Y direction
            after drawing these glyphs.
            Will typically be zero except for vertical text layout
            as found in East-Asian languages.

        """
        extents = ffi.new('cairo_text_extents_t *')
        cairo.cairo_text_extents(self._pointer, _encode_string(text), extents)
        self._check_status()
        # returning extents as is would be a nice API,
        # but return a tuple for compat with pycairo.
        return (
            extents.x_bearing, extents.y_bearing,
            extents.width, extents.height,
            extents.x_advance, extents.y_advance)

    def glyph_extents(self, glyphs):
        """Returns the extents for a list of glyphs.

        The extents describe a user-space rectangle
        that encloses the "inked" portion of the glyphs,
        (as it would be drawn by :meth:`show_glyphs`).
        Additionally, the :obj:`x_advance` and :obj:`y_advance` values
        indicate the amount by which the current point would be advanced
        by :meth:`show_glyphs`.

        :param glyphs:
            A list of glyphs.
            See :meth:`show_text_glyphs` for the data structure.
        :returns:
            A ``(x_bearing, y_bearing, width, height, x_advance, y_advance)``
            tuple of floats.
            See :meth:`text_extents` for details.

        """
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        extents = ffi.new('cairo_text_extents_t *')
        cairo.cairo_glyph_extents(
            self._pointer, glyphs, len(glyphs), extents)
        self._check_status()
        return (
            extents.x_bearing, extents.y_bearing,
            extents.width, extents.height,
            extents.x_advance, extents.y_advance)

    def show_text(self, text):
        """A drawing operator that generates the shape from a string text,
        rendered according to the current
        font :meth:`face <set_font_face>`,
        font :meth:`size <set_font_size>`
        (font :meth:`matrix <set_font_matrix>`),
        and font :meth:`options <set_font_options>`.

        This method first computes a set of glyphs for the string of text.
        The first glyph is placed so that its origin is at the current point.
        The origin of each subsequent glyph
        is offset from that of the previous glyph
        by the advance values of the previous glyph.

        After this call the current point is moved
        to the origin of where the next glyph would be placed
        in this same progression.
        That is, the current point will be at
        the origin of the final glyph offset by its advance values.
        This allows for easy display of a single logical string
        with multiple calls to :meth:`show_text`.

        :param text: The text to show, as an Unicode or UTF-8 string.

        .. note::

            This method is part of
            what the cairo designers call the "toy" text API.
            It is convenient for short demos and simple programs,
            but it is not expected to be adequate
            for serious text-using applications.
            See :ref:`fonts` for details
            and :meth:`show_glyphs` for the "real" text display API in cairo.

        """
        cairo.cairo_show_text(self._pointer, _encode_string(text))
        self._check_status()

    def show_glyphs(self, glyphs):
        """A drawing operator that generates the shape from a list of glyphs,
        rendered according to the current
        font :meth:`face <set_font_face>`,
        font :meth:`size <set_font_size>`
        (font :meth:`matrix <set_font_matrix>`),
        and font :meth:`options <set_font_options>`.

        :param glyphs:
            The glyphs to show.
            See :meth:`show_text_glyphs` for the data structure.

        """
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        cairo.cairo_show_glyphs(self._pointer, glyphs, len(glyphs))
        self._check_status()

    def show_text_glyphs(self, text, glyphs, clusters, clusters_backwards):
        """This operation has rendering effects similar to :meth:`show_glyphs`
        but, if the target surface supports it
        (see :meth:`Surface.has_show_text_glyphs`),
        uses the provided text and cluster mapping
        to embed the text for the glyphs shown in the output.
        If the target does not support the extended attributes,
        this method acts like the basic :meth:`show_glyphs`
        as if it had been passed :obj:`glyphs`.

        The mapping between :obj:`text` and :obj:`glyphs`
        is provided by an list of clusters.
        Each cluster covers a number of UTF-8 text bytes and glyphs,
        and neighboring clusters cover neighboring areas
        of :obj:`text` and :obj:`glyphs`.
        The clusters should collectively cover :obj:`text` and :obj:`glyphs`
        in entirety.

        :param text:
            The text to show, as an Unicode or UTF-8 string.
            Because of how :obj:`clusters` work,
            using UTF-8 bytes might be more convenient.
        :param glyphs:
            A list of glyphs.
            Each glyph is a ``(glyph_id, x, y)`` tuple.
            :obj:`glyph_id` is an opaque integer.
            Its exact interpretation depends on the font technology being used.
            :obj:`x` and :obj:`y` are the float offsets
            in the X and Y direction
            between the origin used for drawing or measuring the string
            and the origin of this glyph.
            Note that the offsets are not cumulative.
            When drawing or measuring text,
            each glyph is individually positioned
            with respect to the overall origin.
        :param clusters:
            A list of clusters.
            A text cluster is a minimal mapping of some glyphs
            corresponding to some UTF-8 text,
            represented as a ``(num_bytes, num_glyphs)`` tuple of integers,
            the number of UTF-8 bytes and glyphs covered by the cluster.
            For a cluster to be valid,
            both :obj:`num_bytes` and :obj:`num_glyphs` should be non-negative,
            and at least one should be non-zero.
            Note that clusters with zero glyphs
            are not as well supported as normal clusters.
            For example, PDF rendering applications
            typically ignore those clusters when PDF text is being selected.
        :type clusters_backwards: bool
        :param clusters_backwards:
            The first cluster always covers bytes
            from the beginning of :obj:`text`.
            If :obj:`clusters_backwards` is false,
            the first cluster also covers the beginning of :obj:`glyphs`,
            otherwise it covers the end of the :obj:`glyphs` list
            and following clusters move backward.

        """
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        clusters = ffi.new('cairo_text_cluster_t[]', clusters)
        flags = 'BACKWARDS' if clusters_backwards else 0
        cairo.cairo_show_text_glyphs(
            self._pointer, _encode_string(text), -1,
            glyphs, len(glyphs), clusters, len(clusters), flags)
        self._check_status()

    def text_path(self, text):
        cairo.cairo_text_path(self._pointer, _encode_string(text))
        self._check_status()

    def glyph_path(self, glyphs):
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        cairo.cairo_glyph_path(self._pointer, glyphs, len(glyphs))
        self._check_status()

    ##
    ##  Pages
    ##

    def show_page(self):
        cairo.cairo_show_page(self._pointer)
        self._check_status()

    def copy_page(self):
        cairo.cairo_copy_page(self._pointer)
        self._check_status()
