import numpy
# import cairo
import cairocffi as cairo
import math

data = numpy.zeros((200, 200, 4), dtype=numpy.uint8)
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200, data=data)
cr = cairo.Context(surface)

# fill with solid white
cr.set_source_rgb(1.0, 1.0, 1.0)
cr.paint()

# draw red circle
cr.arc(100, 100, 80, 0, 2*math.pi)
cr.set_line_width(3)
cr.set_source_rgb(1.0, 0.0, 0.0)
cr.stroke()

# write output
surface.write_to_png("circle.png")
