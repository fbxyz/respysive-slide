import os
import sys

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("_ext"))

from respysive import __version__ as _respysive_version
from respysive_demo import gallery_scraper

project = "respysive-slide"
author = "fbxyz"
release = _respysive_version
version = ".".join(_respysive_version.split(".")[:2])
copyright = "2026, fbxyz"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
    "respysive_demo",
]

sphinx_gallery_conf = {
    "examples_dirs": "examples",
    "gallery_dirs": "gallery",
    "filename_pattern": r"plot_",
    # the showcase opens the home page, it is not a gallery example
    "ignore_pattern": r"__init__\.py|showcase\.py",
    "image_scrapers": (gallery_scraper,),
    "image_srcset": [],
    "remove_config_comments": True,
    "download_all_examples": False,
    "within_subsection_order": "FileNameSortKey",
    "matplotlib_animations": False,
    "reset_modules": (),
}

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_rtype = False
napoleon_use_ivar = True  # dataclass fields would otherwise be documented twice

# The gallery scraper is a function, so the gallery config cannot be
# pickled for the build cache. The warning is harmless.
suppress_warnings = ["config.cache"]

html_theme = "furo"
html_title = f"respysive-slide {release}"
html_static_path = ["_static"]
html_css_files = ["demo.css"]

exclude_patterns = ["_build", "_old", "Thumbs.db", ".DS_Store"]
