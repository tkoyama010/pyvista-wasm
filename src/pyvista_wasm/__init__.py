"""pyvista-wasm: PyVista-like API for VTK.wasm.

This package provides a familiar PyVista interface for 3D visualization
in browser environments using VTK.wasm as the rendering backend.

This package uses lazy loading (SPEC 0001) to improve import performance.
"""

import sys

__version__ = "0.1.0"
__author__ = "Tetsuo Koyama"
__license__ = "BSD-3-Clause"

if sys.platform == "emscripten":
    try:
        import numpy as np  # noqa: F401
    except ImportError:
        import asyncio

        import micropip  # type: ignore[import-not-found]

        asyncio.get_event_loop().run_until_complete(micropip.install("numpy"))

# SPEC 0001 — Lazy Loading of Submodules and Functions
# https://scientific-python.org/specs/spec-0001/
import lazy_loader as _lazy

__getattr__, __dir__, _all = _lazy.attach_stub(__name__, __file__)

# Ensure module-level attributes are included in __all__
__all__ = [*_all, "__version__"]  # noqa: PLE0604
