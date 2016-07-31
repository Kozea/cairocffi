import re
import os

html_theme = 'classic'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinx.ext.coverage']
master_doc = 'index'
project = 'cairocffi'
copyright = '2013, Simon Sapin'
release = re.search(
    "VERSION = '([^']+)'",
    open(os.path.join(os.path.dirname(__file__), os.pardir,
         'cairocffi', '__init__.py')).read().strip()).group(1)
version = '.'.join(release.split('.')[:2])
exclude_patterns = ['_build']
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members']
intersphinx_mapping = {
    'http://docs.python.org/': None,
    'http://cairographics.org/documentation/pycairo/2/': None}
