# CairoCFFI documentation build configuration file.

import cairocffi

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'CairoCFFI'
copyright = 'Simon Sapin and contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = cairocffi.__version__

# The short X.Y version.
version = release

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'monokai'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'collapse_navigation': False,
}

# Favicon URL
html_favicon = 'https://www.courtbouillon.org/static/images/favicon.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'https://www.courtbouillon.org/static/docs.css',
]

# Output file base name for HTML help builder.
htmlhelp_basename = 'cairocffidoc'

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('manpage', 'cairocffi', 'CFFI-based cairo bindings for Python',
     ['Simon Sapin and contributors'], 1)
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [(
    'index', 'CairoCFFI', 'CairoCFFI Documentation',
    'Simon Sapin and contributors', 'CairoCFFI',
    'CFFI-based cairo bindings for Python', 'Miscellaneous'),
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'pycairo': ('https://cairographics.org/documentation/pycairo/2/', None),
    'cffi': ('https://cffi.readthedocs.io/en/latest/', None),
}
