from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build


setup(
    name='cairocffi',
    use_scm_version=True,
    version='1.7.1',
    # when xcffib is updated, bump to include API mode
    install_requires=['cffi >= 1.1.0', 'xcffib >= 1.5.0'],
    setup_requires=['setuptools_scm', 'cffi >= 1.1.0', 'xcffib >= 1.5.0'],
    packages=['cairocffi'],
    cffi_modules=['cairocffi/ffi_build.py:build_ffi',
                  'cairocffi/ffi_build.py:build_pixbuf_ffi',
                  'cairocffi/ffi_build.py:build_xcb_ffi']
)
