import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'NetGuardian'
copyright = '2024, forekz'
author = 'forekz'
release = '1.0.0'

language = 'ru'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx_autodoc_typehints'
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
    'display_version': True,
    'logo_only': False,
    'style_nav_header_background': '#2b3d50'
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None)
}

locale_dirs = ['locale/']
gettext_compact = False
gettext_uuid = True
gettext_location = True

todo_include_todos = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True
html_copy_source = True
html_use_index = True
html_split_index = False
html_show_search_summary = True