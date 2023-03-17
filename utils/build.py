import importlib.util
import sys
from pathlib import Path

from setuptools import build_meta as _orig

prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
get_requires_for_build_wheel = _orig.get_requires_for_build_wheel
get_requires_for_build_sdist = _orig.get_requires_for_build_sdist

folder = Path(__file__).parent.parent / 'cairocffi'


def build_sdist(*args, **kwargs):
    (folder / '_generated' / 'ffi.py').unlink(missing_ok=True)
    (folder / '_generated' / 'ffi_pixbuf.py').unlink(missing_ok=True)
    return _orig.build_sdist(*args, **kwargs)


def build_wheel(*args, **kwargs):
    spec = importlib.util.spec_from_file_location(
        'ffi_build', folder / 'ffi_build.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules['ffi_build'] = module
    spec.loader.exec_module(module)
    module.compile()
    return _orig.build_wheel(*args, **kwargs)
