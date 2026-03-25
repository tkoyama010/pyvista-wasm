# pyvista-wasm

[PyVista](https://github.com/pyvista/pyvista)-like API for [VTK.wasm](https://kitware.github.io/vtk-wasm/) — bring intuitive 3D visualization to the browser using WebAssembly.

## Install

```bash
pip install pyvista-wasm
```

For Pyodide/stlite:

```python
import micropip

await micropip.install("pyvista-wasm")
```

## Usage

```python
import pyvista_wasm as pv

plotter = pv.Plotter()
plotter.add_mesh(pv.Sphere())
plotter.show()
```

## API Reference

- `Plotter` — main entry point for building and displaying scenes
- `examples` — sample datasets (sphere, bunny, etc.)

## Links

- [Source code](https://github.com/tkoyama010/pyvista-wasm)
- [Issue tracker](https://github.com/tkoyama010/pyvista-wasm/issues)
- [Changelog](../CHANGELOG.md)
