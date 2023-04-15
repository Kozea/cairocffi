import importlib.util
import subprocess
import sys
from pathlib import Path

from setuptools import build_meta
from setuptools.build_meta import *  # noqa

folder = Path(__file__).parent.parent / 'cairocffi'


def build_sdist(*args, **kwargs):
    (folder / '_generated' / 'ffi.py').unlink(missing_ok=True)
    (folder / '_generated' / 'ffi_pixbuf.py').unlink(missing_ok=True)
    return build_meta.build_sdist(*args, **kwargs)


def build_wheel(*args, **kwargs):
    # Try to install xcffib for XCB support
    try:
        pip = Path(sys.executable).parent / 'pip'
        subprocess.run([str(pip), 'install', 'xcffib'])
    except Exception:
        pass

    spec = importlib.util.spec_from_file_location(
        'ffi_build', folder / 'ffi_build.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules['ffi_build'] = module
    spec.loader.exec_module(module)
    module.compile()
    return build_meta.build_wheel(*args, **kwargs)
