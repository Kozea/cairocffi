import re
import os

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinx.ext.coverage']
source_suffix = '.rst'
master_doc = 'index'
project = 'cairocffi'
copyright = '2013, Simon Sapin'
release = re.search(
    "VERSION = '([^']+)'",
    open(os.path.join(os.path.dirname(__file__), os.pardir,
         'cairocffi', '__init__.py')).read().strip()
).group(1)
version = '.'.join(release.split('.')[:2])
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'haiku'
intersphinx_mapping = {
    'http://docs.python.org/': None,
    'http://cairographics.org/documentation/pycairo/2/': None}
