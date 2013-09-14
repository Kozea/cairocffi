"""
GTK+ 3 example using a drawing area to draw with cairocffi.

Drawing code taken from:
http://cairographics.org/pycairo/tutorial/
"""

import sys
import math

import cairocffi as cairo
cairo.enable_capi()

from gi.repository import Gtk
from gi.repository import Gdk


class Viewport(Gtk.ScrolledWindow):
    def __init__(self):
        super(Viewport, self).__init__()

        self.drawingArea = Gtk.DrawingArea()
        self.drawingArea.set_app_paintable(True)
        self.drawingArea.add_events(Gdk.EventMask.EXPOSURE_MASK |
                                    Gdk.EventMask.SCROLL_MASK)
        self.drawingArea.connect('draw', self.on_draw)
        self.add_with_viewport(self.drawingArea)

    def on_draw(self, widget, ctx):
        extents = ctx.clip_extents()
        ctx.scale (extents[2], extents[3]) # Normalizing the canvas

        pat = cairo.LinearGradient (0.0, 0.0, 0.0, 1.0)
        pat.add_color_stop_rgba (1, 0.7, 0, 0, 0.5) # First stop, 50% opacity
        pat.add_color_stop_rgba (0, 0.9, 0.7, 0.2, 1) # Last stop, 100% opacity

        ctx.rectangle (0, 0, 1, 1) # Rectangle(x0, y0, x1, y1)
        ctx.set_source (pat)
        ctx.fill ()

        ctx.translate (0.1, 0.1) # Changing the current transformation matrix

        ctx.move_to (0, 0)
        ctx.arc (0.2, 0.1, 0.1, -math.pi/2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
        ctx.line_to (0.5, 0.1) # Line to (x,y)
        ctx.curve_to (0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
        ctx.close_path ()

        ctx.set_source_rgb (0.3, 0.2, 0.5) # Solid color
        ctx.set_line_width (0.02)
        ctx.stroke ()

        return False


def main(argv):
    window = Gtk.Window()
    window.connect('destroy', Gtk.main_quit)
    vpt = Viewport()
    window.add(vpt)
    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main(sys.argv)
