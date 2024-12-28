# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# para ler a versão do projeto
import os
from pathlib import Path
this_directory = Path(__file__).parent

about = dict()
with open(os.path.join(this_directory, '..', 'db2', '__version__.py'), 'r', encoding='utf-8') as read_file:
    exec(read_file.read(), about)

project = about['__title__']
copyright = about['__copyright__']
author = about['__author__']
release = about['__version__']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']

exclude_patterns = ['setup.py', 'tests.py']

language = 'pt_BR'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'press'
html_static_path = ['_static']
