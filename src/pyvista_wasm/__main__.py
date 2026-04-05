"""Entry point for running pyvista-wasm as a module.

Allows the package to be executed via ``python -m pyvista_wasm``.
"""

from __future__ import annotations

from pyvista_wasm._cli import cli_main

if __name__ == "__main__":
    cli_main()
