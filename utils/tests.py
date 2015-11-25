# coding: utf-8

import io
import cairo  # pycairo
import cairocffi

from pycairo_to_cairocffi import _UNSAFE_pycairo_context_to_cairocffi
from cairocffi_to_pycairo import _UNSAFE_cairocffi_context_to_pycairo
import pango_example


def test():
    cairocffi_context = cairocffi.Context(cairocffi.PDFSurface(None, 10, 20))
    cairocffi_context.scale(2, 3)
    pycairo_context = _UNSAFE_cairocffi_context_to_pycairo(cairocffi_context)
    cairocffi_context2 = _UNSAFE_pycairo_context_to_cairocffi(pycairo_context)
    assert tuple(cairocffi_context.get_matrix()) == (2, 0, 0, 3, 0, 0)
    assert tuple(cairocffi_context2.get_matrix()) == (2, 0, 0, 3, 0, 0)
    assert tuple(pycairo_context.get_matrix()) == (2, 0, 0, 3, 0, 0)
    assert cairocffi_context2._pointer == cairocffi_context._pointer

    file_obj = io.BytesIO()
    # Mostly test that this runs without raising.
    pango_example.write_example_pdf(file_obj)
    assert file_obj.getvalue().startswith(b'%PDF')


if __name__ == '__main__':
    test()
