# Render in Google Colaboratory

pyvista-wasm renders interactive 3D scenes inline in [Google Colaboratory](https://colab.research.google.com/) notebook cells, with no local setup required.

## How it works

Colab sets `IPYTHON_AVAILABLE = True`, but it strips inline `<script>` tags from cell output. To work around this, pyvista-wasm detects the Colab environment and uses `ColabRenderer`, which embeds the standalone HTML inside a sandboxed `<iframe srcdoc="..." sandbox="allow-scripts">`. Colab renders `<iframe>` elements in cell output, and `allow-scripts` permits JavaScript execution inside the iframe regardless of Colab's output sanitization.

Environment detection checks `google.colab` in `sys.modules` or the `COLAB_RELEASE_TAG` environment variable **before** the generic IPython branch, so the sandboxed iframe is used instead of the stripped `<script>` injection.

## Quick start

Open a Colab notebook and run:

```python
import pyvista_wasm as pv

plotter = pv.Plotter()
plotter.add_mesh(pv.Sphere(), color="red")
plotter.show()
```

The interactive VTK.wasm canvas renders inline in the cell output area. The 3D scene is mouse-rotatable once the "Initializing WASM Environment..." overlay dismisses.

## Notes

- `Plotter.show()` returns an `IPython.display.HTML` object so Colab captures it in the cell output area.
- The other backends (`VTKWasmRenderer` for JupyterLite, `MarimoRenderer`, `BrowserRenderer`, and `MockRenderer`) are unaffected.
