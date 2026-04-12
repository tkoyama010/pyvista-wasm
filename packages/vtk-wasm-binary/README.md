# @pyvista-wasm/vtk-wasm-binary

Mirrored VTK.wasm binary for pyvista-wasm, served via [jsDelivr](https://www.jsdelivr.com/) CDN.

## Usage

The binary is available at:

```
https://cdn.jsdelivr.net/npm/@pyvista-wasm/vtk-wasm-binary@<version>/vtk-wasm32-emscripten.tar.gz
```

## Updating

1. Update the `version` in `package.json` to match the upstream VTK.wasm version.
2. Run `npm run download` to fetch the binary from upstream.
3. Publish with `npm publish`.

The [mirror-vtk-wasm](.github/workflows/mirror-vtk-wasm.yml) workflow automates
steps 2 and 3.
