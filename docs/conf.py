import cairocffi

extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.coverage']
master_doc = 'index'
project = 'cairocffi'
copyright = 'Simon Sapin and contributors'
release = cairocffi.version
version = release
exclude_patterns = ['_build']
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members']
intersphinx_mapping = {
    'http://docs.python.org/3/': None,
    'http://cairographics.org/documentation/pycairo/2/': None}
