"""
    cairocffi.ffi
    ~~~~~~~~~~~~~

    Build the cffi bindings

    :copyright: Copyright 2013-2019 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

import importlib.util
import platform
import sys
from pathlib import Path
from warnings import warn

from setuptools.errors import CCompilerError, ExecError, PlatformError

from cffi import FFI
from cffi.error import VerificationError


# import constants
# without loading the module via import which would invoke __init__.py
sys.path.append(str(Path(__file__).parent))
spec = importlib.util.spec_from_file_location(
    'constants',
    str(Path(__file__).parent / 'constants.py')
)
constants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(constants)


xcffib_available = False
try:
    from xcffib import cffi_mode as xcb_cffi_mode
    from xcffib.ffi_build import ffi_for_mode as _xcb_ffi_for_mode
except ImportError:
    warn("xcfiib not available")
else:
    xcffib_available = True


c_source_cairo_compat = r"""
    /* Deal with some newer definitions for compatibility */
    #if CAIRO_VERSION < 11702
    #define CAIRO_FORMAT_RGBA128F 7
    #define CAIRO_FORMAT_RGB96F 6
    #endif
    #if CAIRO_VERSION < 11800
    #include <stdio.h>
    #include <stdbool.h>
    void cairo_set_hairline(cairo_t*, cairo_bool_t);
    cairo_bool_t cairo_get_hairline(cairo_t*);
    void cairo_set_hairline(cairo_t*, cairo_bool_t) {
        fprintf(stderr, "Unimplemented!!\n");
    }
    cairo_bool_t cairo_get_hairline(cairo_t*) {
        fprintf(stderr, "Unimplemented!!\n");
        return false;
    }
    #endif
"""

c_source_cairo = (
    r"""
    #include "cairo.h"
    #include "cairo-pdf.h"
    #include "cairo-svg.h"
    #include "cairo-ps.h"
    #if defined(__APPLE__)
    #include "cairo-quartz.h"
    #endif
    #if defined(_WIN64) || defined(_WIN32)
    #include "cairo-win32.h"
    #endif
    #include "cairo-ft.h"
    """ +
    c_source_cairo_compat)

c_source_cairo_pixbuf = (
    c_source_cairo +
    r"""
        #include "gdk-pixbuf/gdk-pixbuf.h"
        #include "gdk/gdk.h"
    """ +
    c_source_cairo_compat)

c_source_cairo_xcb = (
    c_source_cairo +
    (r"""
        #include "xcb/xcb.h"
        #include "xcb/xproto.h"
        #include "xcb/xcbext.h"
        #include "xcb/render.h"
        #include "cairo-xcb.h"
     """ if xcffib_available else "") +
    c_source_cairo_compat)


# Primary cffi definitions
def ffi_for_mode(mode):
    ffi = FFI()
    ffi.cdef(constants._CAIRO_HEADERS)
    if platform.system() == 'Windows':
        ffi.cdef(constants._CAIRO_WIN32_HEADERS)
    if platform.system() == 'Darwin':
        ffi.cdef(constants._CAIRO_QUARTZ_HEADERS)

    if mode == "api":
        ffi.set_source_pkgconfig(
            '_cairocffi',
            ['cairo'],
            c_source_cairo,
            sources=[]
        )
    else:
        ffi.set_source(
            '_cairocffi', None)

    return ffi


# gdk pixbuf cffi definitions
def pixbuf_ffi_for_mode(mode):
    ffi_pixbuf = FFI()
    ffi_cairo = ffi_for_mode(mode)
    ffi_pixbuf.include(ffi_cairo)
    ffi_pixbuf.cdef('''
        typedef unsigned long   gsize;
        typedef unsigned int    guint32;
        typedef unsigned int    guint;
        typedef unsigned char   guchar;
        typedef char            gchar;
        typedef int             gint;
        typedef gint            gboolean;
        typedef guint32         GQuark;
        typedef void*           gpointer;
        typedef ...             GdkPixbufLoader;
        typedef ...             GdkPixbufFormat;
        typedef ...             GdkPixbuf;
        typedef struct {
            GQuark              domain;
            gint                code;
            gchar              *message;
        } GError;
        typedef enum {
            GDK_COLORSPACE_RGB
        } GdkColorspace;


        GdkPixbufLoader * gdk_pixbuf_loader_new          (void);
        GdkPixbufFormat * gdk_pixbuf_loader_get_format   (GdkPixbufLoader *loader);
        GdkPixbuf *       gdk_pixbuf_loader_get_pixbuf   (GdkPixbufLoader *loader);
        gboolean          gdk_pixbuf_loader_write        (
            GdkPixbufLoader *loader, const guchar *buf, gsize count,
            GError **error);
        void              gdk_pixbuf_loader_set_size (
            GdkPixbufLoader *loader, int width, int height);
        gboolean          gdk_pixbuf_loader_close        (
            GdkPixbufLoader *loader, GError **error);

        gchar *           gdk_pixbuf_format_get_name     (GdkPixbufFormat *format);

        GdkColorspace     gdk_pixbuf_get_colorspace      (const GdkPixbuf *pixbuf);
        int               gdk_pixbuf_get_n_channels      (const GdkPixbuf *pixbuf);
        gboolean          gdk_pixbuf_get_has_alpha       (const GdkPixbuf *pixbuf);
        int               gdk_pixbuf_get_bits_per_sample (const GdkPixbuf *pixbuf);
        int               gdk_pixbuf_get_width           (const GdkPixbuf *pixbuf);
        int               gdk_pixbuf_get_height          (const GdkPixbuf *pixbuf);
        int               gdk_pixbuf_get_rowstride       (const GdkPixbuf *pixbuf);
        guchar *          gdk_pixbuf_get_pixels          (const GdkPixbuf *pixbuf);
        gsize             gdk_pixbuf_get_byte_length     (const GdkPixbuf *pixbuf);
        gboolean          gdk_pixbuf_save_to_buffer      (
            GdkPixbuf *pixbuf, gchar **buffer, gsize *buffer_size,
            const char *type, GError **error, ...);

        void              gdk_cairo_set_source_pixbuf    (
            cairo_t *cr, const GdkPixbuf *pixbuf,
            double pixbuf_x, double pixbuf_y);


        void              g_object_ref                   (gpointer object);
        void              g_object_unref                 (gpointer object);
        void              g_error_free                   (GError *error);
        void              g_type_init                    (void);
    ''')

    if mode == "api":
        ffi_pixbuf.set_source_pkgconfig(
            '_cairocffi_pixbuf',
            ['cairo', 'glib-2.0', 'gdk-pixbuf-2.0', 'gobject-2.0', 'gdk-3.0'],
            c_source_cairo_pixbuf,
            sources=[]
        )
    else:
        ffi_pixbuf.set_source(
            '_cairocffi_pixbuf', None)

    return ffi_pixbuf


def xcb_ffi_for_mode(mode):
    ffi_xcb = FFI()
    ffi_cairo = ffi_for_mode(mode)
    ffi_xcb.include(ffi_cairo)

    # include xcffib cffi definitions for cairo xcb support
    if xcffib_available:
        ffi_xcb.include(_xcb_ffi_for_mode(mode))
        ffi_xcb.cdef(constants._CAIRO_XCB_HEADERS)

    if mode == "api":
        ffi_xcb.set_source_pkgconfig(
            '_cairocffi_xcb',
            ['cairo', 'xcb'],
            c_source_cairo_xcb,
            sources=[]
        )
    else:
        ffi_xcb.set_source(
            '_cairocffi_xcb', None)

    return ffi_xcb


def _build_ffi(ffi_gen_for_mode):
    """
    This will be called from setup() to return an FFI
    which it will compile - work out here which type is
    possible and return it.
    """
    try:
        ffi_api = ffi_gen_for_mode("api")
        ffi_api.compile(verbose=True)
        return ffi_api
    except (CCompilerError, ExecError, PlatformError,
            VerificationError) as e:
        warn("Falling back to precompiled python mode: {}".format(str(e)))

        ffi_abi = ffi_gen_for_mode("abi")
        ffi_abi.compile(verbose=True)
        return ffi_abi


def build_ffi():
    return _build_ffi(ffi_for_mode)


def build_pixbuf_ffi():
    return _build_ffi(pixbuf_ffi_for_mode)


def build_xcb_ffi():
    return _build_ffi(xcb_ffi_for_mode)


if __name__ == "__main__":
    build_ffi()
    build_pixbuf_ffi()
    if xcffib_available:
        build_xcb_ffi()
