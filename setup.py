import sys

from setuptools import setup

if sys.version_info.major < 3:
    raise RuntimeError(
        "cairocffi does not support Python 2.x anymore. "
        "Please use Python 3 or install an older version of cairocffi."
    )

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            python, abi = 'py3', 'none'
            return python, abi, plat
except ImportError:
    bdist_wheel = None

setup(
    cffi_modules=[
         "cairocffi/ffi_build.py:ffi",
         "cairocffi/ffi_build.py:ffi_pixbuf"
         ],
    cmdclass={'bdist_wheel': bdist_wheel},
)
