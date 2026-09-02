# pyvista-wasm

[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://pyvista-wasm.readthedocs.io/en/latest/lite/lab/index.html?path=intro.ipynb)
[![Stlite](https://img.shields.io/badge/stlite-Streamlit%20in%20Browser-FF4B4B?logo=streamlit)](https://edit.share.stlite.net/#!CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt)
[![marimo](https://marimo.io/shield.svg)](https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HhCkrLqRGr4mzgwIpn-VwiQTeLSnJW1uZC8AA9EcAs8G1iA+sbmuCubsDubbs3t-uMhlY0KMPHJ3rd7j8ttM4p8IDAyFBxFsOAAFCzwxFeHYIe4MZjgz73DjkCBUAgYxCUABGGgIBDs2NhGIRxA4VMoahsdDaeNqAThrKgHG5ZOxGGAY0wBBueGwTGYLGwSEy2BYvjiAKgdOxQA)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tkoyama010/pyvista-wasm/blob/main/notebooks/intro.ipynb)
[![Slidev](https://img.shields.io/badge/Slides-PyCon%20JP%202026-639BFF?logo=slides)](https://tkoyama010.github.io/pyvista-wasm/slides/)

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh-TW.md">繁體中文</a>
</p>

提供類似 [PyVista](https://github.com/pyvista/pyvista) 的 API 給 [VTK.wasm](https://kitware.github.io/vtk-wasm/) — 透過 WebAssembly 在瀏覽器中實現直覺式的 3D 視覺化。

| [用 JupyterLite 試用] | [用 Stlite 試用] | [用 marimo 試用] |
| :-------------------: | :--------------: | :--------------: |
| ![jupyterlite-preview] | ![stlite-preview] | ![marimo-preview] |

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Install](#install)
- [Usage](#usage)
- [Presentation](#presentation)
- [Differences from pyvista-js](#differences-from-pyvista-js)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)

## Install

[![PyPI](https://img.shields.io/pypi/v/pyvista-wasm)](https://pypi.org/project/pyvista-wasm/)

```bash
pip install pyvista-wasm
```

Pyodide/stlite 環境:

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

## Presentation

PyCon JP 2026 的議程介紹了 pyvista-wasm，包含即時示範與 WASM 渲染架構的深入探討：

[**檢視簡報**](https://tkoyama010.github.io/pyvista-wasm/slides/)

[**pretalx 上的議程詳情**](https://pretalx.com/pyconjp2026/talk/review/VVJZFPCFCJCRGGKWEWKPYC3QXF8YE3A9)

## Differences from pyvista-js

本專案將 [pyvista-js](https://github.com/tkoyama010/pyvista-js) 中使用的 [vtk.js](https://github.com/Kitware/vtk-js) 渲染後端替換為 [VTK.wasm](https://kitware.github.io/vtk-wasm/)（`@kitware/vtk-wasm` npm 套件）。

主要差異：

- **渲染後端**：VTK.wasm（VTK C++ 的 WebAssembly 移植版本），而非 vtk.js（純 JavaScript 重寫版本）
- **API 風格**：VTK.wasm 使用命名空間物件上的 `vtk.vtkRenderer()` 工廠函式，而非 vtk.js 的 `vtk.Rendering.Core.vtkRenderer.newInstance()` 階層結構
- **初始化**：VTK.wasm 需要透過 `vtkWASM.createNamespace()` 進行非同步初始化以載入 WASM 二進位檔
- **功能完整性**：VTK.wasm 提供完整的 VTK C++ API 存取，支援 vtk.js 無法實現的功能

## Citation

若在學術研究或專案中使用 pyvista-wasm，歡迎引用。完整的引用中繼資料請參閱 [`CITATION.cff`](CITATION.cff)，或使用下方的 BibTeX 條目：

```bibtex
@software{Koyama2026pyvista-wasm,
  author       = {Tetsuo Koyama},
  title        = {{pyvista-wasm: PyVista-like API for VTK.wasm}},
  year         = {2026},
  version      = {0.9.0},
  license      = {Apache-2.0},
  url          = {https://github.com/tkoyama010/pyvista-wasm}
}
```

## Contributing

歡迎貢獻！請在 [GitHub](https://github.com/tkoyama010/pyvista-wasm/issues) 上建立 issue 或 pull request。貢獻者名單請參閱 [`CONTRIBUTORS.md`](CONTRIBUTORS.md)。

## License

[Apache License 2.0](LICENSE) © Tetsuo Koyama

[jupyterlite-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/preview.gif
[marimo-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/marimo-preview.gif
[stlite-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/stlite-preview.gif
[用 jupyterlite 試用]: https://pyvista-wasm.readthedocs.io/en/latest/lite/lab/index.html?path=intro.ipynb
[用 marimo 試用]: https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HhCkrLqRGr4mzgwIpn-VwiQTeLSnJW1uZC8AA9EcAs8G1iA+sbmuCubsDubbs3t-uMhlY0KMPHJ3rd7j8ttM4p8IDAyFBxFsOAAFCzwxFeHYIe4MZjgz73DjkCBUAgYxCUABGGgIBDs2NhGIRxA4VMoahsdDaeNqAThrKgHG5ZOxGGAY0wBBueGwTGYLGwSEy2BYvjiAKgdOxQA
[用 stlite 試用]: https://edit.share.stlite.net/#!CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt
