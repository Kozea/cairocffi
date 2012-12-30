from __future__ import print_function

import cairocffi
import cairo as pycairo

# We want the real pycairo
assert pycairo is not cairocffi


for name in dir(pycairo):
    pycairo_obj = getattr(pycairo, name)
    cairocffi_obj = getattr(cairocffi, name, None)
    if not isinstance(pycairo_obj, type):
        continue
    if cairocffi_obj is None:
        print('Missing class:', name)
        continue
    for method_name in dir(pycairo_obj):
        if method_name.startswith('__'):
            continue
        pycairo_method = getattr(pycairo_obj, method_name)
        cairocffi_method = getattr(cairocffi_obj, method_name, None)
        if cairocffi_method is None:
            print('Missing method:', name, method_name)
            continue
