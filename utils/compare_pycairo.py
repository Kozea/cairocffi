# coding: utf-8

import cairo as pycairo
import cairocffi

# We want the real pycairo
assert pycairo is not cairocffi


print('Missing pycairo API:\n')

for name in dir(pycairo):
    pycairo_obj = getattr(pycairo, name)
    cairocffi_obj = getattr(cairocffi, name, None)
    if name.startswith(('_', 'version', 'CAPI')):
        continue
    if cairocffi_obj is None:
        print(name)
    elif isinstance(pycairo_obj, type):
        for method_name in dir(pycairo_obj):
            if method_name.startswith('__'):
                continue
            pycairo_method = getattr(pycairo_obj, method_name)
            cairocffi_method = getattr(cairocffi_obj, method_name, None)
            if cairocffi_method is None:
                print('%s.%s' % (name, method_name))
