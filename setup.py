import os
import sys
from os import path

from setuptools import setup

if sys.version_info.major < 3:
    raise RuntimeError(
        "cairocffi does not support Python 2.x anymore. "
        "Please use Python 3 or install an older version of cairocffi."
    )
has_cairo =os.path.isfile(os.path.join("cairocffi", "cairo.dll"))
is_build_wheel = ("bdist_wheel" in sys.argv)

if is_build_wheel:
    if has_cairo:
        pos_bdist_wheel = sys.argv.index("bdist_wheel")
        # we also need to make sure that this version of bdist_wheel supports
        # the --plat-name argument
        try:
            import wheel
            from distutils.version import StrictVersion
            if not StrictVersion(wheel.__version__) >= StrictVersion("0.27"):
                msg = "Including pandoc in wheel needs wheel >=0.27 but found %s.\nPlease update wheel!"
                raise RuntimeError(msg % wheel.__version__)
        except ImportError:
            print("No wheel installed, please install 'wheel'...")
        from distutils.util import get_platform
        sys.argv.insert(pos_bdist_wheel + 1, '--plat-name')
        sys.argv.insert(pos_bdist_wheel + 2, get_platform())
    else:
        print("no cairo found, building platform unspecific wheel...")

setup(
    cffi_modules=[
         "cairocffi/ffi_build.py:ffi",
         "cairocffi/ffi_build.py:ffi_pixbuf"
         ],
)
