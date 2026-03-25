# pyvista-wasm

[PyVista](https://github.com/pyvista/pyvista)-like API for [VTK.wasm](https://kitware.github.io/vtk-wasm/) — bring intuitive 3D visualization to the browser using WebAssembly.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Install](#install)
- [Usage](#usage)
- [Differences from pyvista-js](#differences-from-pyvista-js)
- [Contributing](#contributing)
- [License](#license)

## Install

[![PyPI](https://img.shields.io/pypi/v/pyvista-wasm)](https://pypi.org/project/pyvista-wasm/)

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
plotter.add_mesh(pv.Sphere(), color="red")
plotter.show()
```

## Differences from pyvista-js

This project replaces the [vtk.js](https://github.com/Kitware/vtk-js) rendering backend used in [pyvista-js](https://github.com/tkoyama010/pyvista-js) with [VTK.wasm](https://kitware.github.io/vtk-wasm/) (`@kitware/vtk-wasm` npm package).

Key differences:

- **Rendering backend**: VTK.wasm (WebAssembly port of VTK C++) instead of vtk.js (pure JavaScript reimplementation)
- **API style**: VTK.wasm uses `vtk.vtkRenderer()` factory functions on a namespace object, vs vtk.js's `vtk.Rendering.Core.vtkRenderer.newInstance()` hierarchy
- **Initialization**: VTK.wasm requires async initialization via `vtkWASM.createNamespace()` to load the WASM binary
- **Feature parity**: VTK.wasm provides access to the full VTK C++ API, enabling features not available in vtk.js

## Contributing

Contributions are welcome! Please open an issue or pull request on [GitHub](https://github.com/tkoyama010/pyvista-wasm/issues).

## License

[Apache License 2.0](LICENSE) © Tetsuo Koyama
