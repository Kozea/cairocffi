from pathlib import Path

extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.coverage']
master_doc = 'index'
project = 'cairocffi'
copyright = '2013-2019, Simon Sapin'
release = (
    Path(__file__).parent.parent / 'cairocffi' / 'VERSION').read_text().strip()
version = '.'.join(release.split('.')[:2])
exclude_patterns = ['_build']
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members']
intersphinx_mapping = {
    'http://docs.python.org/': None,
    'http://cairographics.org/documentation/pycairo/2/': None}
