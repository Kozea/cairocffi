# coding: utf8
import cairocffi as cairo
import cffi


ffi = cffi.FFI()
ffi.cdef('''
    typedef ... cairo_t;

    /* GLib */
    typedef void* gpointer;
    void g_object_unref (gpointer object);

    /* Pango and PangoCairo */
    typedef ... PangoLayout;
    typedef enum {
        PANGO_ALIGN_LEFT,
        PANGO_ALIGN_CENTER,
        PANGO_ALIGN_RIGHT
    } PangoAlignment;
    int pango_units_from_double (double d);
    PangoLayout * pango_cairo_create_layout (cairo_t *cr);
    void pango_cairo_show_layout (cairo_t *cr, PangoLayout *layout);
    void pango_layout_set_width (PangoLayout *layout, int width);
    void pango_layout_set_alignment (PangoLayout *layout, PangoAlignment alignment);
    void pango_layout_set_markup (PangoLayout *layout, const char *text, int length);
''')
gobject = ffi.dlopen('gobject-2.0')
pango = ffi.dlopen('pango-1.0')
pangocairo = ffi.dlopen('pangocairo-1.0')

gobject_ref = lambda pointer: ffi.gc(pointer, gobject.g_object_unref)
units_from_double = pango.pango_units_from_double


def write_example_pdf(filename):
    pt_per_mm = 72 / 25.4
    width, height = 210 * pt_per_mm, 297 * pt_per_mm  # A4 portrait
    surface = cairo.PDFSurface(filename, width, height)
    context = cairo.Context(surface)
    context.move_to(0, 200)
    # 'cairo_t *' in both FFI objects is not considered the same type:
    context_p = ffi.cast('cairo_t *', context._pointer)

    layout = gobject_ref(pangocairo.pango_cairo_create_layout(context_p))
    pango.pango_layout_set_width(layout, units_from_double(width))
    pango.pango_layout_set_alignment(layout, pango.PANGO_ALIGN_CENTER)
    markup = u'<span font="italic 30">Hi from Παν語!</span>'
    markup = ffi.new('char[]', markup.encode('utf8'))
    pango.pango_layout_set_markup(layout, markup, -1)
    pangocairo.pango_cairo_show_layout(context_p, layout)


if __name__ == '__main__':
    write_example_pdf(filename='pango_example.pdf')
