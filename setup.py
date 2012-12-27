from setuptools import setup, find_packages
from os import path
import re


VERSION = re.search("VERSION = '([^']+)'", open(
    path.join(path.dirname(__file__), 'cairocffi', '__init__.py')
).read().strip()).group(1)

LONG_DESCRIPTION = open(path.join(path.dirname(__file__), 'README.rst')).read()


setup(
    name='cairocffi',
    version=VERSION,
    url='https://github.com/SimonSapin/cairocffi',
    license='BSD',
    author='Simon Sapin',
    author_email='simon.sapin@exyr.org',
    description='cffi-based cairo bindings for Python',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics',
    ],
    packages=find_packages(),
    install_requires=['cffi'],
)
