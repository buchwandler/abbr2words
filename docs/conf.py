from __future__ import annotations

from abbr2words import __version__

project = "abbr2words"
author = "Holger Nahrstaedt"
release = __version__
version = __version__

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
autodoc_typehints = "description"
nitpicky = True
