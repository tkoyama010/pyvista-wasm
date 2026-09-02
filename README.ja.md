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

[PyVista](https://github.com/pyvista/pyvista) のような API を [VTK.wasm](https://kitware.github.io/vtk-wasm/) に提供し、WebAssembly を使ってブラウザで直感的な 3D 可視化を実現します。

| [JupyterLite で試す] | [Stlite で試す] | [marimo で試す] |
| :-------------------: | :-------------: | :-------------: |
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

Pyodid/stlite の場合:

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

PyCon JP 2026 のトークでは、pyvista-wasm をライブデモと WASM レンダリングアーキテクチャの詳細解説とともに紹介します:

[**スライドを見る**](https://tkoyama010.github.io/pyvista-wasm/slides/)

[**pretalx でトーク詳細を見る**](https://pretalx.com/pyconjp2026/talk/review/VVJZFPCFCJCRGGKWEWKPYC3QXF8YE3A9)

## Differences from pyvista-js

このプロジェクトは [pyvista-js](https://github.com/tkoyama010/pyvista-js) で使用されている [vtk.js](https://github.com/Kitware/vtk-js) レンダリングバックエンドを [VTK.wasm](https://kitware.github.io/vtk-wasm/) (`@kitware/vtk-wasm` npm パッケージ) に置き換えます。

主な違い:

- **レンダリングバックエンド**: vtk.js (JavaScript の再実装) ではなく VTK.wasm (VTK C++ の WebAssembly ポート) を使用
- **API スタイル**: VTK.wasm は名前空間オブジェクト上で `vtk.vtkRenderer()` ファクトリ関数を使用。vtk.js の `vtk.Rendering.Core.vtkRenderer.newInstance()` 階層とは異なる
- **初期化**: VTK.wasm は WASM バイナリを読み込むために `vtkWASM.createNamespace()` による非同期初期化が必要
- **機能の網羅性**: VTK.wasm は VTK C++ API 全体へのアクセスを提供し、vtk.js では利用できない機能を利用可能

## Citation

学術研究やプロジェクトで pyvista-wasm を使用する場合は、引用をご検討ください。完全な引用メタデータは [`CITATION.cff`](CITATION.cff) を参照するか、以下の BibTeX エントリを使用してください:

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

貢献を歓迎します！[GitHub](https://github.com/tkoyama010/pyvista-wasm/issues) で issue またはプルリクエストを開いてください。貢献者の一覧は [`CONTRIBUTORS.md`](CONTRIBUTORS.md) を参照してください。

## License

[Apache License 2.0](LICENSE) © Tetsuo Koyama

[jupyterlite で試す]: https://pyvista-wasm.readthedocs.io/en/latest/lite/lab/index.html?path=intro.ipynb
[jupyterlite-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/preview.gif
[marimo で試す]: https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HhCkrLqRGr4mzgwIpn-VwiQTeLSnJW1uZC8AA9EcAs8G1iA+sbmuCubsDubbs3t-uMhlY0KMPHJ3rd7j8ttM4p8IDAyFBxFsOAAFCzwxFeHYIe4MZjgz73DjkCBUAgYxCUABGGgIBDs2NhGIRxA4VMoahsdDaeNqAThrKgHG5ZOxGGAY0wBBueGwTGYLGwSEy2BYvjiAKgdOxQA
[marimo-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/marimo-preview.gif
[stlite で試す]: https://edit.share.stlite.net/#!CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt
[stlite-preview]: https://github.com/tkoyama010/pyvista-wasm/releases/latest/download/stlite-preview.gif
