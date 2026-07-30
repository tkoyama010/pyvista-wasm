# PyCon JP 2026 Talk — PyVista on WebAssembly

## Overview

Tetsuo Koyama presented pyvista-wasm at [PyCon JP 2026](https://2026.pycon.jp/)
on August 21, 2026 in Phoenix Hall.

- **Title**: PyVista on WebAssembly: サーバーレス3D可視化の実現
- **Speaker**: Tetsuo Koyama (小山 哲央)
- **Duration**: 30 minutes
- **Language**: Japanese
- **Proposal**: [pretalx session page](https://pretalx.com/pyconjp2026/talk/review/VVJZFPCFCJCRGGKWEWKPYC3QXF8YE3A9)

## Talk Materials

| Material | Link |
| :------- | :--- |
| Slide deck (Slidev) | <https://tkoyama010.github.io/pyvista-wasm/slides/> |
| Live demo — JupyterLite | <https://pyvista-js.readthedocs.io/en/latest/lite/lab/index.html?path=intro.ipynb> |
| Live demo — marimo | <https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HhCkrLqRGr4mzgwIpn-VwiQTeLSnJW1uZC8AA9EcAs8G1iA+sbmuCubsDubbs3t-uMhlY0KMPHJ3rd7j8ttM4p8IDAyFBxFsOAAFCzwxFeHYIe4MZjgz73DjkCBUAgYxCUABGGgIBDs2NhGIRxA4VMoahsdDaeNqAThrKgHG5ZOxGGAY0wBBueGwTGYLGwSEy2BYvjiAKgdOxQA> |
| Live demo — stlite | <https://edit.share.stlite.net/#%21CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt> |
| Talk proposal | <https://pretalx.com/pyconjp2026/talk/review/VVJZFPCFCJCRGGKWEWKPYC3QXF8YE3A9> |

## Talk Summary

The talk introduced pyvista-wasm — a PyVista-like API running entirely in the
browser via WebAssembly — and demonstrated that server-less 3D visualization is
practical today.

### 1. PyVista and WASM overview

PyVista wraps VTK, the 30-year C++ visualization toolkit, in a Pythonic API.
Traditionally, sharing 3D results on the web required a server-side rendering
backend, which adds cost and security concerns. WebAssembly removes those
barriers: the entire visualization pipeline runs client-side, so data never
leaves the machine and no infrastructure is needed.

### 2. Technical stack and implementation

- **VTK Emscripten build**: VTK's C++ codebase is compiled to WebAssembly once;
  consumers simply `npm install @kitware/vtk-wasm`.
- **Pyodide + PyVista**: CPython compiled to Wasm runs the real interpreter in
  the browser, and pyvista-wasm bridges the PyVista API to the vtk-wasm
  TypeScript bindings.
- **WebGL / WebGPU**: The runtime selects between WebGL (universally supported)
  and WebGPU (higher performance, GPU compute) with automatic fallback.
- **Development challenges**: async/await everywhere (createNamespace returns a
  Promise), SharedArrayBuffer requiring COOP/COEP headers, and CDN CORS
  configuration for the WASM tarball.

### 3. Live demos

Three browser-only environments were demonstrated:

- **JupyterLite** — a browser-only Jupyter environment for notebook-style
  visualization.
- **marimo** — a reactive notebook where slider changes trigger instant mesh
  redraws.
- **stlite** — Streamlit in the browser with declarative widgets driving 3D
  mesh rendering.

### 4. Performance and limitations

- Initial load takes several seconds (10–15 MB gzip download).
- Once loaded, ~100K-element meshes run at practical interactive speed.
- Key constraints: module size, COOP/COEP headers, WebGPU flags, and initial
  load time — each with a proven workaround.

### 5. Future roadmap

WebGPU stabilization and Pyodide + PyVista maturity will widen the practical
application range, with browser-native GPU compute as the next milestone.

## Community Feedback

_This section will be updated after the talk with audience questions,
discussion highlights, and community feedback._

## Recording

_If PyCon JP publishes a recording, the link will be added here._
