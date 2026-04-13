# pyvista-wasm

[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://pyvista-js.readthedocs.io/en/latest/lite/lab/index.html?path=intro.ipynb)
[![Stlite](https://img.shields.io/badge/stlite-Streamlit%20in%20Browser-FF4B4B?logo=streamlit)](https://edit.share.stlite.net/#!CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt)
[![marimo](https://marimo.io/shield.svg)](https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HgkFBAIeJsEdDi5kMKSsupEatW4MCLYgPrG5vXu49P+4yGrNFGPNogbk+m41wiQOAArNZbeDkCCmLSEGA3GgEUFUGb+H4QP6FCDkYAuDiuVzAQLgeZwcJ4Uh4TBgCIADzsZ38YAsEBgZCg4hOHAACvTGcQvAjjpymRxEORKGobHQ5KyAMpgOjEPBeG6mCD0qAqerkXS8ugwEAWTBKghkQ0s-nEDj4IgkMiYMqw3IQIiYbW6nm8g05TLETAY8QsIowADWlQOIHK7qSlqEvJemX+eFMMEw-oDXl8cTi4c9zOYoPBakN5oaAFELHh8zAAEJ2ACS5Dkmct3vItXT-mA7gbxECawAcg68GnW+mLk0CLzNj9EGpxLmIQWiSSS2XIfl2yQ1Jqh4FJ2oODYoKZc+JnXr3ZDx7Md3g9zA7KWzDYbAAVPAU+DMOQX1ssRT0bz8Ng2DACkAG5ZWAHBtW8AAWQDgJAoQtziVRMnKcDIJgGC4NAgAjaAXCgbwACZgLgGxlR9ABiHgaIQr84BbVs1yna8bEQWE8IpX1cnpKhyhscJohgGxEKHTsoAyAhLQACSfABZAAZX1RNbcTBVEQhyAAYToYALDrZi1D6OJyQgKlxAXa1TKpORY3jRNk0YuAYThPcGifUA8AgDQYAlSk7BuABWQDjPOBpR3WDhpJ1CxPy3VwAHIAB50SKQJyBUABvcSmwAXxYOAEvohLsjvPAVF-Oh-2wsC8AgqDYKA3DEFMAMcAiDRYW8SjXDYXrepAoqtwS9EbDpRA7G8VxS1A3IIIIcpaDLGxvHMQ1iBA-4NGyds7DDB0jUwtamQQgA+IahxYJKwFOhSICFTIcDgAA1J8AGkOCqEAOB+pKAHobpU9Mrr+1LTqBvo0HbDxMAIFjsCYZgWGwJBMmwFhB38B4oE6nkgA)

[PyVista](https://github.com/pyvista/pyvista)-like API for [VTK.wasm](https://kitware.github.io/vtk-wasm/) — bring intuitive 3D visualization to the browser using WebAssembly.

| [Try it with JupyterLite] | [Try it with Stlite] | [Try it with marimo] |
| :-----------------------: | :------------------: | :------------------: |
| ![jupyterlite-preview] | ![stlite-preview] | ![marimo-preview] |

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

[jupyterlite-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/preview.gif
[marimo-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/marimo-preview.gif
[stlite-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/stlite-preview.gif
[try it with jupyterlite]: https://pyvista-js.readthedocs.io/en/latest/lite/lab/index.html?path=intro.ipynb
[try it with marimo]: https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HgkFBAIeJsEdDi5kMKSsupEatW4MCLYgPrG5vXu49P+4yGrNFGPNogbk+m41wiQOAArNZbeDkCCmLSEGA3GgEUFUGb+H4QP6FCDkYAuDiuVzAQLgeZwcJ4Uh4TBgCIADzsZ38YAsEBgZCg4hOHAACvTGcQvAjjpymRxEORKGobHQ5KyAMpgOjEPBeG6mCD0qAqerkXS8ugwEAWTBKghkQ0s-nEDj4IgkMiYMqw3IQIiYbW6nm8g05TLETAY8QsIowADWlQOIHK7qSlqEvJemX+eFMMEw-oDXl8cTi4c9zOYoPBakN5oaAFELHh8zAAEJ2ACS5Dkmct3vItXT-mA7gbxECawAcg68GnW+mLk0CLzNj9EGpxLmIQWiSSS2XIfl2yQ1Jqh4FJ2oODYoKZc+JnXr3ZDx7Md3g9zA7KWzDYbAAVPAU+DMOQX1ssRT0bz8Ng2DACkAG5ZWAHBtW8AAWQDgJAoQtziVRMnKcDIJgGC4NAgAjaAXCgbwACZgLgGxlR9ABiHgaIQr84BbVs1yna8bEQWE8IpX1cnpKhyhscJohgGxEKHTsoAyAhLQACSfABZAAZX1RNbcTBVEQhyAAYToYALDrZi1D6OJyQgKlxAXa1TKpORY3jRNk0YuAYThPcGifUA8AgDQYAlSk7BuABWQDjPOBpR3WDhpJ1CxPy3VwAHIAB50SKQJyBUABvcSmwAXxYOAEvohLsjvPAVF-Oh-2wsC8AgqDYKA3DEFMAMcAiDRYW8SjXDYXrepAoqtwS9EbDpRA7G8VxS1A3IIIIcpaDLGxvHMQ1iBA-4NGyds7DDB0jUwtamQQgA+IahxYJKwFOhSICFTIcDgAA1J8AGkOCqEAOB+pKAHobpU9Mrr+1LTqBvo0HbDxMAIFjsCYZgWGwJBMmwFhB38B4oE6nkgA
[try it with stlite]: https://edit.share.stlite.net/#!CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt
