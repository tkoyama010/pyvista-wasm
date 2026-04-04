# Configuration file for the Sphinx documentation builder.  # noqa: INP001, D100
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import shutil
from pathlib import Path

import pyvista_wasm

# Copy source code to JupyterLite content directory
docs_dir = Path(__file__).parent
project_root = docs_dir.parent
src_dir = project_root / "src" / "pyvista_wasm"
content_dir = docs_dir / "content" / "src"

# Create content directory and copy source
content_dir.mkdir(parents=True, exist_ok=True)
dest_dir = content_dir / "pyvista_wasm"
if dest_dir.exists():
    shutil.rmtree(dest_dir)
shutil.copytree(src_dir, dest_dir)

# Configure JupyterLite to pre-load jinja2 and set up sys.path
# so that examples work without explicit micropip or sys.path calls.
_jupyterlite_config = docs_dir / "content" / "jupyter-lite.json"
_jupyterlite_config.write_text(
    json.dumps(
        {
            "jupyter-lite-schema-version": 0,
            "jupyter-config-data": {
                "litePluginSettings": {
                    "@jupyterlite/pyodide-kernel-extension:kernel": {
                        "loadPyodideOptions": {"packages": ["Jinja2"]},
                        "pipliteUrls": [],
                    },
                },
            },
        },
        indent=2,
    )
    + "\n",
)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pyvista-wasm"
copyright = "2026, Tetsuo Koyama"  # noqa: A001
author = "Tetsuo Koyama"
release = pyvista_wasm.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "jupyterlite_sphinx",
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_design",
]

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for internationalization ----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-internationalization

language = "en"
locale_dirs = ["locale/"]
gettext_compact = False

# Suppress warnings for missing cross-references in included README
suppress_warnings = [
    "myst.xref_missing",
    "py.duplicate_object",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -- Options for MyST parser -------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# -- Options for jupyterlite-sphinx ------------------------------------------
jupyterlite_dir = ".jupyterlite"
jupyterlite_contents = ["content"]
global_enable_try_examples = True
try_examples_global_warning_text = (
    "pyvista-wasm's interactive examples are experimental and may not always work as expected."
)
try_examples_preamble = (
    "import micropip\n"
    "await micropip.install('jinja2')\n"
    "await micropip.install('lazy-loader')\n"
    "import sys\n"
    "sys.path.insert(0, '/drive/src')\n"
    "import pyvista_wasm as pv\n"
)
