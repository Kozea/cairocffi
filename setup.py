import os
import sys
from os import path

from setuptools import setup

if sys.version_info.major < 3:
    raise RuntimeError(
        "cairocffi does not support Python 2.x anymore. "
        "Please use Python 3 or install an older version of cairocffi."
    )
if os.environ.get("BUILD_WHEEL_WINDOWS"):
    from setuptools import Extension
    from setuptools.command.build_ext import build_ext
    from wheel.bdist_wheel import bdist_wheel

    class BdistWheel(bdist_wheel):
        def get_tag(self):
            return ("py3", "none") + bdist_wheel.get_tag(self)[2:]

    class SharedLibrary(Extension):
        """Object that describes the library (filename) and how to
        make it."""

        if sys.platform == "darwin":
            suffix = ".dylib"
        elif sys.platform == "win32":
            suffix = ".dll"
        else:
            suffix = ".so"

        def __init__(self, name, cmd, cwd=".", output_dir=".", env=None):
            Extension.__init__(self, name, sources=[])
            self.cmd = cmd
            self.cwd = path.normpath(cwd)
            self.output_dir = path.normpath(output_dir)
            self.env = env or dict(os.environ)

    class SharedLibBuildExt(build_ext):
        """Object representing command to produce and install a shared
        library."""

        # Needed to make setuptools and wheel believe they're looking at an
        # extension instead of a shared library.
        def get_ext_filename(self, ext_name):
            for ext in self.extensions:
                if isinstance(ext, SharedLibrary):
                    return os.path.join(*ext_name.split(".")) + ext.suffix
            return build_ext.get_ext_filename(self, ext_name)

        def build_extension(self, ext):
            # there should a command to build cairo here. Currently
            # there is no meson for now. Inn next release meson can
            # be used.
            return

    ext_modules = [
        SharedLibrary("cairocffi.cairo", cmd="", output_dir="build")
        ]
    cmdclass = {"bdist_wheel": BdistWheel, "build_ext": SharedLibBuildExt}
else:
    ext_modules = {}
    cmdclass = {}
setup(
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    cffi_modules=[
         "cairocffi/ffi_build.py:ffi",
         "cairocffi/ffi_build.py:ffi_pixbuf"
         ],
)
