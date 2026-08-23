(howtos-creating-planet)=

# Creating a Planet

Render a textured planet sphere in the browser, mirroring PyVista's
`create-planet` example. pyvista-wasm ships the Mars surface texture via
{func}`pyvista_wasm.examples.download_mars_surface`.

## Steps

Build a UV-mapped sphere and wrap the Mars surface image around it:

```python
import pyvista_wasm as pv
from pyvista_wasm import examples

texture = examples.download_mars_surface()

sphere = pv.Sphere(theta_resolution=120, phi_resolution=120)
planet = sphere.texture_map_to_plane()

plotter = pv.Plotter()
_ = plotter.add_mesh(planet, texture=texture)
plotter.show()
```

## How it works

- {func}`~pyvista_wasm.examples.download_mars_surface` returns a
  {class}`~pyvista_wasm.Texture` wrapping the remote Mars surface image URL
  from the PyVista `solar_textures` dataset. pyvista-wasm textures are
  URL-based, so no file is downloaded on the Python side.
- {meth}`~pyvista_wasm.PolyData.texture_map_to_plane` generates texture
  coordinates (UVs) on the sphere so the image wraps around the surface.
- {meth}`~pyvista_wasm.Plotter.add_mesh` accepts the texture via the
  `texture` argument; VTK.wasm samples it in the browser via WebGL.

## PyVista comparison

This mirrors
[`pyvista.examples.planets.download_mars_surface(texture=True)`](https://docs.pyvista.org/examples/99-advanced/planets.html)
combined with a textured sphere, adapted to pyvista-wasm's URL-based
`Texture`.
