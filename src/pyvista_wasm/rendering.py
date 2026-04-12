"""VTK.wasm rendering backend for pyvista-wasm.

This module provides the JavaScript bridge to VTK.wasm for rendering
in Pyodide/browser environments.

Architecture
------------
pyvista-wasm uses a backend abstraction to support multiple environments:

1. **VTKWasmRenderer**: Used in Pyodide/browser with VTK.wasm for WebGL rendering
2. **BrowserRenderer**: Used in standard Python; opens the plot in the default browser
3. **MockRenderer**: Used in standard Python for development/testing

Environment Detection
---------------------
The library automatically detects the runtime:

>>> import sys
>>> PYODIDE_ENV = sys.platform == "emscripten"  # True in Pyodide

If running in Pyodide and VTK.wasm is available, VTKWasmRenderer is used.
If running in standard Python, BrowserRenderer opens the plot in the default browser.
MockRenderer provides a fallback for testing.

Data Conversion
---------------
NumPy arrays are converted to JavaScript for VTK.wasm.

Python NumPy array (n, 3)::

    points = mesh.points

    # Convert to JavaScript flat array
    points_js = points.flatten().tolist()
    polydata.getPoints().setData(points_js, 3)

Loading VTK.wasm
----------------
VTK.wasm is automatically loaded when VTKWasmRenderer is initialized in
IPython/Jupyter environments. No manual script loading required.

For manual loading or custom versions:

.. code-block:: html

    <script
      src="https://unpkg.com/@kitware/vtk-wasm/vtk-umd.js"
      id="vtk-wasm"
      data-url="https://gitlab.kitware.com/api/v4/projects/13/packages/generic/vtk-wasm32-emscripten/9.6.20260228/vtk-9.6.20260228-wasm32-emscripten.tar.gz"
    ></script>

Examples
--------
Using the renderer (automatically selected)::

    from pyvista_wasm.rendering import get_renderer
    from pyvista_wasm import Sphere

    renderer = get_renderer()
    mesh = Sphere()
    renderer.add_mesh_actor(mesh, color='red', opacity=0.8)
    renderer.create_container('viz-container')
    renderer.render()

In Pyodide environment, this uses VTK.wasm. In standard Python,
it opens the visualization in the default web browser.

"""

from __future__ import annotations

import logging
import os
import pathlib
import sys
import tempfile
import time
import webbrowser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Self

    import numpy as np

    from .camera import Camera
    from .light import Light
    from .mesh import PolyData
    from .text import Text
    from .texture import Texture


from jinja2 import Environment, StrictUndefined

from .examples import CubeMap

# Load JavaScript templates
_TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
_RENDERING_TEMPLATE = (_TEMPLATES_DIR / "standalone.html").read_text()
_RENDERER_JS = (_TEMPLATES_DIR / "renderer.js").read_text()

_jinja_env = Environment(undefined=StrictUndefined, autoescape=False)  # noqa: S701


# VTK.wasm CDN URLs used across renderers
_VTKWASM_UMD = "https://unpkg.com/@kitware/vtk-wasm@1.7.4/vtk-umd.js"
_VTKWASM_DATA_URL = (
    "https://gitlab.kitware.com/api/v4/projects/13/packages/generic/"
    "vtk-wasm32-emscripten/9.6.20260228/vtk-9.6.20260228-wasm32-emscripten.tar.gz"
)

# Check if running in Pyodide environment
PYODIDE_ENV = sys.platform == "emscripten"

if PYODIDE_ENV:
    try:
        from js import document  # type: ignore[import-not-found]

        VTK_AVAILABLE = True
    except ImportError:
        VTK_AVAILABLE = False
        document = None  # type: ignore[assignment]
else:
    VTK_AVAILABLE = False
    document = None  # type: ignore[assignment]

# Check if IPython is available
try:
    from IPython.display import HTML, Javascript, display

    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False
    HTML = None  # type: ignore[assignment]
    Javascript = None  # type: ignore[assignment]
    display = None  # type: ignore[assignment]


class _VTKWasmLoader:
    """Singleton class to manage VTK.wasm library loading."""

    _instance: _VTKWasmLoader | None = None
    _loaded: bool = False

    def __new__(cls) -> Self:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance  # type: ignore[return-value]

    def load(self) -> None:
        """Load VTK.wasm library in IPython/Jupyter/Pyodide environment.

        This function automatically loads the VTK.wasm library from unpkg CDN
        when working in Jupyter notebooks or JupyterLite. It only loads the
        library once per session and waits for it to be available.
        """
        if self._loaded:
            return

        if IPYTHON_AVAILABLE:
            try:
                display(
                    HTML(f"""
<script src="{_VTKWASM_UMD}" id="vtk-wasm" data-url="{_VTKWASM_DATA_URL}"></script>
"""),
                )
                # Wait for VTK.wasm to load from CDN
                time.sleep(2)
                self._loaded = True
            except (NameError, TypeError):
                # display/HTML not available (e.g., in tests)
                pass
        elif PYODIDE_ENV and document is not None:
            # In pure Pyodide environment without IPython
            script = document.createElement("script")
            script.src = _VTKWASM_UMD
            script.id = "vtk-wasm"
            script.dataset.url = _VTKWASM_DATA_URL
            document.head.appendChild(script)
            # Wait for VTK.wasm to load from CDN
            time.sleep(2)
            self._loaded = True


logger = logging.getLogger(__name__)


def _color_name_to_rgb(color_name: str) -> tuple[float, float, float]:
    """Convert color name to RGB tuple.

    Parameters
    ----------
    color_name : str
        Color name (e.g., 'red', 'blue').

    Returns
    -------
    tuple of float
        RGB values (0-1). Returns gray (0.5, 0.5, 0.5) for unknown colors.

    """
    colors = {
        "red": (1.0, 0.0, 0.0),
        "green": (0.0, 1.0, 0.0),
        "blue": (0.0, 0.0, 1.0),
        "yellow": (1.0, 1.0, 0.0),
        "cyan": (0.0, 1.0, 1.0),
        "magenta": (1.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0),
        "black": (0.0, 0.0, 0.0),
    }
    return colors.get(color_name.lower(), (0.5, 0.5, 0.5))


class _BaseHTMLRenderer:
    """Base class providing shared state and HTML generation for VTK.wasm renderers.

    Subclasses implement :meth:`render` to display the generated HTML in their
    respective environments (Jupyter notebook, standalone browser, etc.).
    """

    def __init__(
        self,
        lighting: str | None = "default",
        wasm_rendering: str = "webgl",
        wasm_mode: str = "sync",
    ) -> None:
        """Initialize shared renderer state.

        Parameters
        ----------
        lighting : str or None, optional
            Lighting mode. ``"default"`` creates a default directional light,
            ``None`` creates no default lights. Default is ``"default"``.
        wasm_rendering : str, optional
            WebAssembly rendering backend. One of ``"webgl"`` or ``"webgpu"``.
            Default is ``"webgl"``.
        wasm_mode : str, optional
            Execution mode for VTK.wasm method calls. One of ``"sync"`` or
            ``"async"``. ``"async"`` requires WebAssembly JavaScript Promise
            Integration (JSPI) browser support. ``"webgpu"`` rendering always
            uses ``"async"`` regardless of this setting. Default is ``"sync"``.

        Raises
        ------
        ValueError
            If ``wasm_rendering`` is not ``"webgl"`` or ``"webgpu"``, or
            ``wasm_mode`` is not ``"sync"`` or ``"async"``.

        """
        valid_rendering = {"webgl", "webgpu"}
        if wasm_rendering not in valid_rendering:
            msg = f"wasm_rendering must be one of {valid_rendering!r}, got {wasm_rendering!r}"
            raise ValueError(msg)
        valid_mode = {"sync", "async"}
        if wasm_mode not in valid_mode:
            msg = f"wasm_mode must be one of {valid_mode!r}, got {wasm_mode!r}"
            raise ValueError(msg)

        self.actors: list[dict[str, object]] = []
        self.lights: list[Light] = []
        self.lighting: str | None = lighting
        self.text_actors: list[Text] = []
        self.background: tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.container_id: str = "pyvista-container"
        self._environment_texture_url: str | None = None
        self._environment_texture_cubemap: CubeMap | None = None
        self._view_vector: tuple[float, float, float] | None = None
        self._view_up: tuple[float, float, float] = (0.0, 1.0, 0.0)
        self._camera: Camera | None = None
        self._axes_enabled: bool = False
        self._scalar_bar: dict[str, object] | None = None
        self._wasm_rendering: str = wasm_rendering
        self._wasm_mode: str = wasm_mode

    def create_container(self, element_id: str = "pyvista-container") -> object | None:
        """Store the container ID for later HTML generation.

        Parameters
        ----------
        element_id : str, default="pyvista-container"
            HTML element ID for the container.

        Returns
        -------
        object or None
            Subclasses may return a DOM element or None.

        """
        self.container_id = element_id
        return None

    def add_mesh_actor(  # noqa: PLR0913
        self,
        mesh: PolyData,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
        smooth_shading: bool = True,  # noqa: FBT001 FBT002
        texture: Texture | None = None,
        show_edges: bool = False,  # noqa: FBT001 FBT002
        edge_color: str | tuple[float, float, float] | None = None,
        style: str = "surface",
        scalars: str | None = None,
        cmap: str = "viridis",
    ) -> dict[str, object]:
        """Add a mesh to the renderer.

        Parameters
        ----------
        mesh : PolyData
            The mesh object to render.
        color : tuple or str, optional
            RGB color tuple (0-1) or color name ('red', 'blue', etc.).
        opacity : float, default=1.0
            Opacity value between 0 and 1.
        pbr : bool, default=False
            Enable physically based rendering.
        metallic : float, default=0.0
            Metallic factor for PBR.
        roughness : float, default=0.5
            Roughness factor for PBR.
        smooth_shading : bool, default=True
            Enable smooth shading (Gouraud interpolation). When True, normals
            are interpolated across polygons for a smooth appearance. When
            False, flat shading is used.
        texture : Texture, optional
            Surface texture to apply. The texture image is loaded from the
            URL stored in the :class:`~pyvista_wasm.Texture` object.
        show_edges : bool, default=False
            Show the edges of the mesh.
        edge_color : tuple or str, optional
            RGB color tuple (0-1) or color name for edges when ``show_edges=True``.
            If not specified, defaults to black.
        style : str, default='surface'
            Visualization style. One of 'surface', 'wireframe', or 'points'.
        scalars : str, optional
            Name of the scalar array to use for coloring. The array must exist
            in ``mesh.point_data``.
        cmap : str, default='viridis'
            Name of the colormap to use when rendering scalars.

        Returns
        -------
        dict
            Actor information dictionary.

        Examples
        --------
        Compare smooth shading (left) and flat shading (right) side by side:

        >>> from pyvista_wasm import Sphere
        >>> from pyvista_wasm.rendering import get_renderer
        >>> renderer = get_renderer()
        >>> color = (0.8, 0.6, 0.2)
        >>> smooth = Sphere(center=(-1.5, 0, 0), theta_resolution=8, phi_resolution=8)
        >>> _ = renderer.add_mesh_actor(smooth, color=color, smooth_shading=True)
        >>> flat = Sphere(center=(1.5, 0, 0), theta_resolution=8, phi_resolution=8)
        >>> _ = renderer.add_mesh_actor(flat, color=color, smooth_shading=False)
        >>> renderer.render()  # doctest: +SKIP

        """
        if isinstance(color, str):
            color = _color_name_to_rgb(color)

        # Convert edge_color if it's a string
        if isinstance(edge_color, str):
            edge_color = _color_name_to_rgb(edge_color)

        actor_info: dict[str, object] = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
            "pbr": pbr,
            "metallic": metallic,
            "roughness": roughness,
            "smooth_shading": smooth_shading,
            "texture": texture,
            "show_edges": show_edges,
            "edge_color": edge_color,
            "style": style,
            "scalars": scalars,
            "cmap": cmap,
        }
        self.actors.append(actor_info)
        return actor_info

    def add_points_actor(
        self,
        points: object,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        point_size: float = 5.0,
        render_points_as_spheres: bool = False,  # noqa: FBT001 FBT002
    ) -> dict[str, object]:
        """Add a point cloud to the renderer.

        Parameters
        ----------
        points : array-like or PolyData
            Point coordinates as an (n, 3) array or PolyData object.
        color : tuple or str, optional
            RGB color tuple (0-1) or color name ('red', 'blue', etc.).
        opacity : float, default=1.0
            Opacity value between 0 and 1.
        point_size : float, default=5.0
            Size of points in pixels.
        render_points_as_spheres : bool, default=False
            Render points as spheres instead of screen-space squares.

        Returns
        -------
        dict
            Actor information dictionary.

        """
        import numpy as np  # noqa: PLC0415

        from .mesh import PolyData  # noqa: PLC0415

        if isinstance(color, str):
            color = _color_name_to_rgb(color)

        # Convert to PolyData if needed
        if not isinstance(points, PolyData):
            points_array = np.asarray(points)
            if points_array.ndim != 2 or points_array.shape[1] != 3:  # noqa: PLR2004
                msg = f"Points must be an (n, 3) array, got shape {points_array.shape}"
                raise ValueError(msg)
            points = PolyData(points_array)

        actor_info: dict[str, object] = {
            "type": "points",
            "mesh": points,
            "color": color,
            "opacity": opacity,
            "point_size": point_size,
            "render_points_as_spheres": render_points_as_spheres,
        }
        self.actors.append(actor_info)
        return actor_info

    def add_light(self, light: Light) -> None:
        """Add a light source to the scene.

        Parameters
        ----------
        light : Light
            The :class:`~pyvista_wasm.light.Light` instance to add.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> renderer = get_renderer()
        >>> renderer.add_light(pv.Light(position=(1, 1, 1), intensity=2.0))

        """
        self.lights.append(light)

    def add_text_actor(self, text: Text) -> None:
        """Add a text actor to the scene.

        Parameters
        ----------
        text : Text
            The :class:`~pyvista_wasm.text.Text` instance to add.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> renderer = get_renderer()
        >>> renderer.add_text_actor(pv.Text("Hello", position=(0.5, 0.9)))

        """
        self.text_actors.append(text)

    def add_axes(self, **kwargs: object) -> None:  # noqa: ARG002
        """Add an orientation marker (axes indicator) to the viewport.

        Displays XYZ axes in the corner of the viewport to help orient
        the viewer. Backed by VTK.wasm ``vtkOrientationMarkerWidget``.

        Parameters
        ----------
        **kwargs
            Reserved for future implementation. Currently accepts no parameters.

        """
        self._axes_enabled = True

    def add_scalar_bar(
        self,
        title: str = "",
        vertical: bool = True,  # noqa: FBT001, FBT002
        n_labels: int = 5,
    ) -> None:
        """Add a scalar bar to the scene.

        The scalar bar displays a color legend mapping scalar values to
        colors using ``vtkScalarBarActor``.

        Parameters
        ----------
        title : str, optional
            Title text displayed on the scalar bar. Default is ``""``.
        vertical : bool, optional
            Whether to orient the scalar bar vertically (``True``) or
            horizontally (``False``). Default is ``True``.
        n_labels : int, optional
            Number of labels to display on the scalar bar. Default is ``5``.

        Examples
        --------
        >>> from pyvista_wasm.rendering import get_renderer
        >>> renderer = get_renderer()
        >>> renderer.add_scalar_bar(title="Height", vertical=True, n_labels=5)

        """
        self._scalar_bar = {
            "title": title,
            "vertical": vertical,
            "n_labels": n_labels,
        }

    def set_environment_texture(self, texture: str | CubeMap) -> None:
        """Set the environment texture for image-based lighting.

        Parameters
        ----------
        texture : str or CubeMap
            Either a URL string pointing to an equirectangular image, or a
            :class:`~pyvista_wasm.examples.CubeMap` with six face image URLs.

        """
        if isinstance(texture, CubeMap):
            self._environment_texture_cubemap = texture
            self._environment_texture_url = None
        else:
            self._environment_texture_url = texture
            self._environment_texture_cubemap = None

    def set_background(self, color: tuple[float, float, float]) -> None:
        """Set the background color of the renderer.

        Parameters
        ----------
        color : tuple
            RGB color tuple with values between 0 and 1.

        """
        self.background = color

    def view_vector(
        self,
        vector: tuple[float, float, float],
        viewup: tuple[float, float, float] | None = None,
    ) -> None:
        """Point the camera in the direction of the given vector.

        Parameters
        ----------
        vector : tuple of float
            Direction vector (vx, vy, vz) to point the camera.
        viewup : tuple of float, optional
            View-up vector. Defaults to (0, 1, 0).

        """
        self._view_vector = (float(vector[0]), float(vector[1]), float(vector[2]))
        if viewup is not None:
            self._view_up = (float(viewup[0]), float(viewup[1]), float(viewup[2]))

    @property
    def camera(self) -> Camera | None:
        """Get or set the camera for the renderer.

        Parameters
        ----------
        camera : Camera
            The camera object to use for rendering.

        Returns
        -------
        Camera or None
            The current camera, or None if not set.

        """
        return self._camera

    @camera.setter
    def camera(self, camera: Camera) -> None:
        """Set the camera."""
        self._camera = camera

    def clear(self) -> None:
        """Remove all actors, lights, and text actors from the renderer."""
        self.actors = []
        self.lights = []
        self._scalar_bar = None
        self.text_actors = []

    def _build_lights_data(self) -> list[dict[str, object]]:
        """Build JSON-serializable light configurations."""
        if not self.lights:
            if self.lighting is None:
                return []
            return [
                {
                    "type": "scene",
                    "positional": False,
                    "intensity": 1.0,
                    "position": [1, 1, 1],
                    "focalPoint": [0, 0, 0],
                    "color": [1, 1, 1],
                    "coneAngle": 30,
                    "coneFalloff": 0,
                    "attenuationValues": [1, 0, 0],
                },
            ]
        lights_data: list[dict[str, object]] = []
        for light in self.lights:
            light_type = light.light_type.lower().replace("light", "")
            lights_data.append(
                {
                    "type": light_type,
                    "positional": light.positional,
                    "intensity": light.intensity,
                    "position": list(light.position),
                    "focalPoint": list(light.focal_point),
                    "color": list(light.color),
                    "coneAngle": light.cone_angle,
                    "coneFalloff": light.cone_falloff,
                    "attenuationValues": list(light.attenuation_values),
                },
            )
        return lights_data

    def _build_actor_data(self, actor_info: dict[str, object]) -> dict[str, object]:
        """Build JSON-serializable actor configuration."""
        mesh = actor_info["mesh"]
        color: tuple[float, ...] = actor_info.get("color") or (0.5, 0.5, 0.5)  # type: ignore[assignment]
        opacity = float(actor_info.get("opacity", 1.0))  # type: ignore[arg-type]
        smooth_shading = bool(actor_info.get("smooth_shading", True))
        style = str(actor_info.get("style", "surface"))

        source_data = mesh.to_scene_data()  # type: ignore[attr-defined]

        # Normals configuration
        normals_data = None
        if smooth_shading or source_data.get("type") == "sphere":
            normals_data = {
                "computePointNormals": bool(smooth_shading),
                "computeCellNormals": not bool(smooth_shading),
            }

        # Texture
        texture_data = None
        texture: object = actor_info.get("texture")
        if texture is not None:
            texture_data = {"url": getattr(texture, "url", "")}

        # Scalars
        scalars_data = None
        scalars_name = actor_info.get("scalars")
        if scalars_name is not None:
            cmap = actor_info.get("cmap", "viridis")
            scalars_array = mesh.point_data[str(scalars_name)]  # type: ignore[attr-defined]
            scalars_data = {
                "arrayName": scalars_name,
                "cmap": cmap,
                "range": [float(scalars_array.min()), float(scalars_array.max())],
            }

        # PBR
        pbr_data = None
        if actor_info.get("pbr"):
            pbr_data = {
                "metallic": actor_info.get("metallic", 0.0),
                "roughness": actor_info.get("roughness", 0.5),
            }

        # Edge
        edge_data = None
        if actor_info.get("show_edges"):
            edge_color = actor_info.get("edge_color")
            if isinstance(edge_color, str):
                from pyvista_wasm.light import _color_name_to_rgb  # noqa: PLC0415

                edge_color = list(_color_name_to_rgb(edge_color))
            elif edge_color is not None:
                edge_color = list(edge_color)  # type: ignore[call-overload]
            else:
                edge_color = [0, 0, 0]
            edge_data = {"color": edge_color}

        actor_type = actor_info.get("type", "mesh")

        result: dict[str, object] = {
            "source": source_data,
            "normals": normals_data,
            "mapper": {"class": "vtkMapper"},
            "color": list(color),
            "opacity": float(opacity),
            "style": style,
            "shading": "gouraud" if smooth_shading else "flat",
            "edges": edge_data,
            "pbr": pbr_data,
            "texture": texture_data,
            "scalars": scalars_data,
            "actorType": actor_type,
        }

        if actor_type == "points":
            point_size = float(actor_info.get("point_size", 5.0))  # type: ignore[arg-type]
            as_spheres = bool(
                actor_info.get("render_points_as_spheres", False),
            )
            result["pointSize"] = point_size
            result["renderPointsAsSpheres"] = as_spheres
            if as_spheres:
                result["mapper"] = {"class": "vtkSphereMapper"}
            else:
                result["mapper"] = {"class": "vtkMapper"}

        return result

    def _build_camera_data(self) -> dict[str, object] | None:
        """Build JSON-serializable camera configuration."""
        if self._camera is not None:
            cam = self._camera
            data: dict[str, object] = {
                "position": list(cam.position),
                "focalPoint": list(cam.focal_point),
                "viewUp": list(cam.view_up),
            }
            if cam.view_angle is not None:
                data["viewAngle"] = cam.view_angle
            if cam.clipping_range is not None:
                data["clippingRange"] = list(cam.clipping_range)
            if cam.parallel_projection:
                data["parallelProjection"] = True
            return data
        if self._view_vector is not None:
            return {
                "viewVector": list(self._view_vector),
                "viewUp": list(self._view_up),
            }
        return None

    def _build_text_actors_data(self) -> list[dict[str, object]]:
        """Build JSON-serializable text actor configurations."""
        return [
            {
                "text": ta.input,
                "position": list(ta.position),
                "fontSize": ta.prop.font_size,
                "color": list(ta.prop.color),
                "opacity": ta.prop.opacity,
                "bold": ta.prop.bold,
                "italic": ta.prop.italic,
            }
            for ta in self.text_actors
        ]

    def _build_scene_data(self) -> dict[str, object]:
        """Build a complete JSON-serializable scene description.

        Returns
        -------
        dict
            Scene configuration including container, background, lights,
            actors, camera, etc.

        """
        import json as _json  # noqa: PLC0415

        actors_data = [self._build_actor_data(info) for info in self.actors]

        text_actors_data = self._build_text_actors_data()

        scene: dict[str, object] = {
            "containerId": self.container_id,
            "background": list(self.background),
            "lights": self._build_lights_data(),
            "actors": actors_data,
            "textActors": text_actors_data,
            "axes": self._axes_enabled,
            "camera": self._build_camera_data(),
            "lightingMode": self.lighting,
            "wasmConfig": {
                "rendering": self._wasm_rendering,
                "mode": self._wasm_mode,
            },
        }

        # Validate JSON serializable
        _json.dumps(scene)

        return scene

    def _generate_html(self) -> str:
        """Generate HTML fragment with embedded VTK.wasm JavaScript."""
        import json as _json  # noqa: PLC0415

        scene_data = self._build_scene_data()
        scene_json = _json.dumps(scene_data)
        wasm_config_json = _json.dumps(
            {"rendering": self._wasm_rendering, "mode": self._wasm_mode},
        )

        return _jinja_env.from_string(_RENDERING_TEMPLATE).render(
            VTKWASM_UMD=_VTKWASM_UMD,
            VTKWASM_DATA_URL=_VTKWASM_DATA_URL,
            WASM_CONFIG=wasm_config_json,
            CONTAINER_ID=self.container_id,
            SCENE_JSON=scene_json,
            RENDERER_JS=_RENDERER_JS,
        )

    def generate_standalone_html(self) -> str:
        """Generate a complete standalone HTML page with vtk.js.

        Wraps the HTML fragment from _generate_html() in a full HTML document.
        """
        fragment = self._generate_html()
        return (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head><meta charset='utf-8'></head>\n"
            "<body>\n" + fragment + "\n</body>\n"
            "</html>\n"
        )

    def _generate_render_js(self) -> str:
        """Generate pure JavaScript for display(Javascript(...)) in JupyterLite.

        Embeds scene data as a JS variable and creates the container and
        scene-data elements inside the cell output area. Each invocation
        uses a unique scene-data ID to avoid collisions between cells.
        """
        import json as _json  # noqa: PLC0415

        scene_data = self._build_scene_data()
        scene_json = _json.dumps(scene_data)
        wasm_config_json = _json.dumps(
            {"rendering": self._wasm_rendering, "mode": self._wasm_mode},
        )

        # For JupyterLite: pass scene data and container via JS variables
        # so renderer.js can use them directly without DOM lookups.
        return (
            "(function() {\n"
            "  var container = document.createElement('div');\n"
            f"  container.id = {_json.dumps(self.container_id)};\n"
            "  container.style.cssText = "
            "'width:600px;height:400px;min-height:400px;border:2px solid #333;position:relative';\n"
            "  var parent = (typeof element !== 'undefined' && element)"
            " ? element : document.body;\n"
            "  parent.appendChild(container);\n"
            f"  var __pvwasmSceneData = {scene_json};\n"
            "  var __pvwasmContainer = container;\n"
            "  function doRender() {\n"
            f"    {_RENDERER_JS}\n"
            "  }\n"
            "  if (typeof vtkWASM !== 'undefined') {\n"
            "    doRender();\n"
            "  } else {\n"
            "    var script = document.createElement('script');\n"
            f"    script.src = {_json.dumps(_VTKWASM_UMD)};\n"
            "    script.id = 'vtk-wasm';\n"
            f"    script.dataset.url = {_json.dumps(_VTKWASM_DATA_URL)};\n"
            f"    script.dataset.config = {_json.dumps(wasm_config_json)};\n"
            "    script.onload = doRender;\n"
            "    document.head.appendChild(script);\n"
            "  }\n"
            "})();\n"
        )

    def _repr_html_(self) -> str:
        """IPython representation as HTML for Jupyter notebooks."""
        return self._generate_html()

    @staticmethod
    def _color_name_to_rgb(color_name: str) -> tuple[float, float, float]:
        """Convert color name to RGB tuple.

        Parameters
        ----------
        color_name : str
            Color name (e.g., 'red', 'blue').

        Returns
        -------
        tuple of float
            RGB values (0-1). Returns gray (0.5, 0.5, 0.5) for unknown colors.

        """
        colors = {
            "red": (1.0, 0.0, 0.0),
            "green": (0.0, 1.0, 0.0),
            "blue": (0.0, 0.0, 1.0),
            "yellow": (1.0, 1.0, 0.0),
            "cyan": (0.0, 1.0, 1.0),
            "magenta": (1.0, 0.0, 1.0),
            "white": (1.0, 1.0, 1.0),
            "black": (0.0, 0.0, 0.0),
        }
        return colors.get(color_name.lower(), (0.5, 0.5, 0.5))

    def screenshot(
        self,
        filename: str | Path | None = None,
        transparent_background: bool | None = None,  # noqa: FBT001
        return_img: bool = True,  # noqa: FBT001, FBT002
        window_size: tuple[int, int] | list[int] | None = None,
        scale: int | None = None,
    ) -> np.ndarray | None:
        """Take a screenshot of the rendered scene.

        This is a base implementation that raises NotImplementedError.
        Subclasses should override this method to provide actual screenshot functionality.

        Parameters
        ----------
        filename : str, Path, or None, optional
            File path to save the image.
        transparent_background : bool or None, optional
            Whether to make the background transparent.
        return_img : bool, optional
            If True, return a numpy array of the image.
        window_size : tuple or list of int, optional
            Temporarily resize the window to (width, height).
        scale : int or None, optional
            Scale factor for higher resolution.

        Returns
        -------
        numpy.ndarray or None
            Image data as numpy array if return_img is True, otherwise None.

        Raises
        ------
        NotImplementedError
            This base implementation always raises NotImplementedError.

        """
        msg = "screenshot() must be implemented by renderer subclass"
        raise NotImplementedError(msg)


class VTKWasmRenderer(_BaseHTMLRenderer):
    """Renderer using VTK.wasm for browser visualization.

    This class wraps VTK.wasm rendering components and provides
    a bridge between Python mesh data and JavaScript WebGL rendering.

    Notes
    -----
    This renderer can only be instantiated in a Pyodide environment
    with VTK.wasm loaded in the page. Use `get_renderer()` to automatically
    get the appropriate renderer for the current environment.

    The renderer creates standard VTK.wasm objects:
    - vtkRenderer: Scene renderer
    - vtkRenderWindow: Rendering window
    - vtkRenderWindowInteractor: User interaction handler

    Examples
    --------
    >>> # In Pyodide/browser environment
    >>> renderer = VTKWasmRenderer()  # doctest: +SKIP
    >>> renderer.create_container('my-viz')  # doctest: +SKIP
    >>> # Add a mesh
    >>> from pyvista_wasm import Sphere  # doctest: +SKIP
    >>> mesh = Sphere()  # doctest: +SKIP
    >>> actor = renderer.add_mesh_actor(mesh, color='blue')  # doctest: +SKIP
    >>> # Render the scene
    >>> renderer.render()  # doctest: +SKIP

    """

    def __init__(
        self,
        lighting: str | None = "default",
        wasm_rendering: str = "webgl",
        wasm_mode: str = "sync",
    ) -> None:
        """Initialize the VTK.wasm renderer.

        Automatically loads VTK.wasm library if in IPython/Jupyter environment.

        Parameters
        ----------
        lighting : str or None, optional
            Lighting mode. ``"default"`` creates a default directional light,
            ``None`` creates no default lights. Default is ``"default"``.
        wasm_rendering : str, optional
            WebAssembly rendering backend. One of ``"webgl"`` or ``"webgpu"``.
            Default is ``"webgl"``.
        wasm_mode : str, optional
            Execution mode for VTK.wasm method calls. One of ``"sync"`` or
            ``"async"``. Default is ``"sync"``.

        Raises
        ------
        RuntimeError
            If not running in Pyodide environment.
        ImportError
            If vtk.js is not available in the page.

        """
        if not PYODIDE_ENV and not IPYTHON_AVAILABLE:
            msg = "VTKWasmRenderer requires either Pyodide environment or IPython"
            raise RuntimeError(msg)

        super().__init__(
            lighting=lighting,
            wasm_rendering=wasm_rendering,
            wasm_mode=wasm_mode,
        )

        # Automatically load VTK.wasm in IPython/Jupyter (including Pyodide)
        if IPYTHON_AVAILABLE or PYODIDE_ENV:
            _VTKWasmLoader().load()

        self.container = None
        self.use_ipython = IPYTHON_AVAILABLE

    def create_container(self, element_id: str = "pyvista-container") -> object | None:
        """Create a DOM container for rendering.

        Creates a <div> element in the document and configures it for
        VTK.wasm rendering with mouse/touch interaction support.

        Parameters
        ----------
        element_id : str, default="pyvista-container"
            HTML element ID for the container.

        Returns
        -------
        container
            The created DOM element (if using direct DOM) or None (if using IPython).

        Examples
        --------
        >>> renderer = VTKWasmRenderer()  # doctest: +SKIP
        >>> container = renderer.create_container('my-visualization')  # doctest: +SKIP

        """
        if self.use_ipython:
            super().create_container(element_id)
            return None
        # Create container div directly
        self.container = document.createElement("div")  # type: ignore[attr-defined]
        self.container.setAttribute("id", element_id)  # type: ignore[attr-defined]
        self.container.style.width = "100%"  # type: ignore[attr-defined]
        self.container.style.height = "600px"  # type: ignore[attr-defined]

        # Append to body
        document.body.appendChild(self.container)  # type: ignore[union-attr]

        return self.container

    def render(self) -> None:
        """Render the scene.

        Resets the camera to show all actors and triggers rendering.
        In IPython/Jupyter, generates and displays HTML with VTK.wasm code.

        Examples
        --------
        >>> renderer.render()  # Display the visualization  # doctest: +SKIP

        """
        if self.use_ipython:
            js_code = self._generate_render_js()
            display(Javascript(js_code))
        else:
            # Direct rendering
            self.renderer.resetCamera()  # type: ignore[attr-defined]
            self.render_window.render()  # type: ignore[attr-defined]

    def clear(self) -> None:
        """Remove all actors from the renderer.

        Examples
        --------
        >>> renderer.clear()  # Remove all visualizations  # doctest: +SKIP

        """
        super().clear()
        if not self.use_ipython and hasattr(self, "renderer"):
            self.renderer.removeAllActors()


def _playwright_capture(html_path: str, w: int, h: int, omit_bg: bool) -> bytes:  # noqa: FBT001
    """Capture a screenshot of an HTML file using Playwright in a thread.

    Parameters
    ----------
    html_path : str
        Path to the HTML file to capture.
    w : int
        Viewport width in pixels.
    h : int
        Viewport height in pixels.
    omit_bg : bool
        Whether to omit the background (transparent PNG).

    Returns
    -------
    bytes
        PNG image data.

    """
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        pg = browser.new_page(viewport={"width": w, "height": h})
        pg.goto(f"file://{html_path}")
        pg.wait_for_timeout(2000)
        data = pg.screenshot(type="png", omit_background=omit_bg)
        browser.close()
    return data


class BrowserRenderer(_BaseHTMLRenderer):
    """Renderer that opens the visualization in the default web browser.

    Used automatically in standard Python environments (outside of
    Jupyter/Pyodide). Generates a standalone HTML file and opens it
    with :func:`webbrowser.open`.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(pv.Sphere(), color='red')
    >>> plotter.show()  # doctest: +SKIP

    """

    def render(self) -> None:
        """Write the visualization to a temp HTML file and open it in the browser."""
        html = self.generate_standalone_html()
        with tempfile.NamedTemporaryFile(
            suffix=".html",
            delete=False,
            mode="w",
            encoding="utf-8",
        ) as f:
            f.write(html)
            tmp_path = f.name

        url = pathlib.Path(tmp_path).as_uri()
        webbrowser.open(url)
        logger.info("Opened visualization in browser: %s", url)

    def generate_standalone_html(self) -> str:
        """Wrap the HTML fragment in a complete standalone HTML page."""
        fragment = self._generate_html()
        container_id = self.container_id
        container_rule = (
            f"    #{container_id} "
            "{ width: 100vw !important; height: 100vh !important; border: none !important; }\n"
        )
        style = (
            "  <style>\n"
            "    html, body { margin: 0; padding: 0; width: 100%; height: 100%;"
            " overflow: hidden; }\n" + container_rule + "  </style>\n"
        )
        return (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "  <meta charset='utf-8'>\n"
            "  <title>pyvista-wasm</title>\n" + style + "</head>\n"
            "<body>\n" + fragment + "</body>\n"
            "</html>\n"
        )

    def screenshot(
        self,
        filename: str | Path | None = None,
        transparent_background: bool | None = None,  # noqa: FBT001
        return_img: bool = True,  # noqa: FBT001, FBT002
        window_size: tuple[int, int] | list[int] | None = None,
        scale: int | None = None,
    ) -> np.ndarray | None:
        """Take a screenshot using Playwright browser automation.

        Parameters
        ----------
        filename : str, Path, or None, optional
            File path to save the image. If None, no file is written.
        transparent_background : bool or None, optional
            Whether to make the background transparent. If None, uses current setting.
        return_img : bool, optional
            If True, return a numpy array of the image.
        window_size : tuple or list of int, optional
            Window size as (width, height). Default is (600, 400).
        scale : int or None, optional
            Scale factor for higher resolution.

        Returns
        -------
        numpy.ndarray or None
            Image data as numpy array if return_img is True, otherwise None.

        """
        import numpy as np  # noqa: PLC0415

        # Set default window size
        width, height = (600, 400) if window_size is None else window_size
        if scale is not None:
            width *= scale
            height *= scale

        # Temporarily change background if transparent requested
        original_background = self.background
        if transparent_background:
            self.background = (0.0, 0.0, 0.0)  # Will be made transparent

        try:
            # Generate HTML
            html = self.generate_standalone_html()

            # Create temp HTML file
            with tempfile.NamedTemporaryFile(
                suffix=".html",
                delete=False,
                mode="w",
                encoding="utf-8",
            ) as f:
                f.write(html)
                tmp_html_path = f.name

            try:
                # Run Playwright in a thread to avoid conflicts when called
                # inside an existing asyncio event loop (e.g. pytest-playwright).
                import concurrent.futures  # noqa: PLC0415

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        _playwright_capture,
                        tmp_html_path,
                        width,
                        height,
                        transparent_background or False,
                    )
                    screenshot_bytes = future.result()

                # Save to file if requested
                if filename is not None:
                    pathlib.Path(filename).write_bytes(screenshot_bytes)

                # Convert to numpy array if requested
                if return_img:
                    try:
                        from PIL import Image  # noqa: PLC0415
                    except ImportError as e:  # pragma: no cover
                        msg = (
                            "Pillow is required to return image as numpy array. "
                            "Install it with: pip install pillow"
                        )
                        raise ImportError(msg) from e

                    from io import BytesIO  # noqa: PLC0415

                    img = Image.open(BytesIO(screenshot_bytes))
                    if transparent_background:
                        img = img.convert("RGBA")
                    return np.array(img)
                return None

            finally:
                # Clean up temp file
                pathlib.Path(tmp_html_path).unlink()

        finally:
            # Restore original background
            if transparent_background:
                self.background = original_background


class MockRenderer:
    """Mock renderer for non-Pyodide environments.

    Provides a drop-in replacement for VTKWasmRenderer that can be used
    in standard Python environments for development and testing.

    Why MockRenderer is Needed
    ---------------------------
    1. **Local Development**: Develop and test code on your PC without browser
    2. **CI/CD Testing**: Run pytest in GitHub Actions and other CI systems
    3. **Documentation**: Generate docs with sphinx-build without Pyodide
    4. **API Validation**: Verify API design before VTK.wasm integration
    5. **Cross-platform**: Same code works in Pyodide and standard Python

    The MockRenderer prints debug information instead of rendering,
    allowing you to verify that your visualization code is correct.

    Examples
    --------
    >>> # Works in standard Python
    >>> from pyvista_wasm.rendering import MockRenderer
    >>> from pyvista_wasm import Sphere
    >>>
    >>> renderer = MockRenderer()
    >>> mesh = Sphere()
    >>> _ = renderer.add_mesh_actor(mesh, color='red')
    >>>
    >>> renderer.render()  # doctest: +SKIP
    Mock: Rendering 1 actors

    Notes
    -----
    The mock renderer is automatically used when calling `get_renderer()`
    outside of a Pyodide environment. You typically don't need to instantiate
    it directly.

    """

    def __init__(
        self,
        lighting: str | None = "default",
        wasm_rendering: str = "webgl",
        wasm_mode: str = "sync",
    ) -> None:
        """Initialize mock renderer.

        Parameters
        ----------
        lighting : str or None, optional
            Lighting mode. ``"default"`` creates a default directional light,
            ``None`` creates no default lights. Default is ``"default"``.
        wasm_rendering : str, optional
            WebAssembly rendering backend (stored but not used). Default is ``"webgl"``.
        wasm_mode : str, optional
            Execution mode (stored but not used). Default is ``"sync"``.

        """
        self.actors: list[dict[str, object]] = []
        self.lights: list[Light] = []
        self.lighting: str | None = lighting
        self.text_actors: list[Text] = []
        self.background = (1.0, 1.0, 1.0)  # Default background color
        self._view_vector: tuple[float, float, float] | None = None
        self._view_up: tuple[float, float, float] = (0.0, 1.0, 0.0)
        self._camera: Camera | None = None
        self._scalar_bar: dict[str, object] | None = None
        self._wasm_rendering: str = wasm_rendering
        self._wasm_mode: str = wasm_mode

    def create_container(self, element_id: str = "pyvista-container") -> None:
        """Mock container creation.

        Parameters
        ----------
        element_id : str
            Container ID (for API compatibility).

        Returns
        -------
        None
            Mock renderers don't create actual containers.

        """
        logger.info("Created container '%s'", element_id)

    def add_mesh_actor(  # noqa: PLR0913
        self,
        mesh: PolyData,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
        smooth_shading: bool = True,  # noqa: FBT001 FBT002
        texture: Texture | None = None,
        show_edges: bool = False,  # noqa: FBT001 FBT002
        edge_color: str | tuple[float, float, float] | None = None,
        style: str = "surface",
        scalars: str | None = None,
        cmap: str = "viridis",
    ) -> dict[str, object]:
        """Mock mesh addition.

        Parameters
        ----------
        mesh : PolyData
            The mesh to add.
        color : str or tuple, optional
            Color (stored but not rendered).
        opacity : float
            Opacity (stored but not rendered).
        pbr : bool
            PBR flag (stored but not rendered).
        metallic : float
            Metallic factor (stored but not rendered).
        roughness : float
            Roughness factor (stored but not rendered).
        smooth_shading : bool
            Smooth shading flag (stored but not rendered).
        texture : Texture, optional
            Surface texture (stored but not rendered).
        show_edges : bool
            Edge visibility (stored but not rendered).
        edge_color : str or tuple, optional
            Edge color (stored but not rendered).
        style : str
            Rendering style (stored but not rendered).
        scalars : str, optional
            Scalar array name (stored but not rendered).
        cmap : str
            Colormap name (stored but not rendered).

        Returns
        -------
        dict
            Mock actor dictionary with mesh data.

        """
        actor: dict[str, object] = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
            "pbr": pbr,
            "metallic": metallic,
            "roughness": roughness,
            "smooth_shading": smooth_shading,
            "texture": texture,
            "show_edges": show_edges,
            "edge_color": edge_color,
            "style": style,
            "scalars": scalars,
            "cmap": cmap,
        }
        self.actors.append(actor)
        logger.info("Added mesh with %d points", mesh.n_points)
        return actor

    def add_points_actor(
        self,
        points: object,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        point_size: float = 5.0,
        render_points_as_spheres: bool = False,  # noqa: FBT001 FBT002
    ) -> dict[str, object]:
        """Mock point cloud addition.

        Parameters
        ----------
        points : array-like or PolyData
            Point coordinates (stored but not rendered).
        color : str or tuple, optional
            Color (stored but not rendered).
        opacity : float
            Opacity (stored but not rendered).
        point_size : float
            Point size (stored but not rendered).
        render_points_as_spheres : bool
            Sphere rendering flag (stored but not rendered).

        Returns
        -------
        dict
            Mock actor dictionary with point data.

        """
        import numpy as np  # noqa: PLC0415

        from .mesh import PolyData  # noqa: PLC0415

        if isinstance(color, str):
            color = _color_name_to_rgb(color)

        if not isinstance(points, PolyData):
            points_array = np.asarray(points)
            if points_array.ndim != 2 or points_array.shape[1] != 3:  # noqa: PLR2004
                msg = f"Points must be an (n, 3) array, got shape {points_array.shape}"
                raise ValueError(msg)
            points = PolyData(points_array)

        actor: dict[str, object] = {
            "type": "points",
            "mesh": points,
            "color": color,
            "opacity": opacity,
            "point_size": point_size,
            "render_points_as_spheres": render_points_as_spheres,
        }
        self.actors.append(actor)
        logger.info("Added point cloud with %d points", points.n_points)
        return actor

    def render(self) -> None:
        """Mock rendering.

        Logs the number of actors that would be rendered.
        """
        logger.info("Rendering %d actors", len(self.actors))

    def generate_standalone_html(self) -> str:
        """Return a minimal HTML string for mock rendering.

        Returns
        -------
        str
            A placeholder HTML document.

        """
        return (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head><meta charset='utf-8'></head>\n"
            "<body><!-- mock renderer --></body>\n"
            "</html>\n"
        )

    def add_light(self, light: Light) -> None:
        """Mock add_light.

        Parameters
        ----------
        light : Light
            The light to add (stored but not rendered).

        """
        self.lights.append(light)
        logger.info("Added light type=%s intensity=%s", light.light_type, light.intensity)

    def add_scalar_bar(
        self,
        title: str = "",
        vertical: bool = True,  # noqa: FBT001, FBT002
        n_labels: int = 5,
    ) -> None:
        """Mock add_scalar_bar.

        Parameters
        ----------
        title : str, optional
            Title text for the scalar bar. Default is ``""``.
        vertical : bool, optional
            Whether to orient vertically. Default is ``True``.
        n_labels : int, optional
            Number of labels. Default is ``5``.

        """
        self._scalar_bar = {
            "title": title,
            "vertical": vertical,
            "n_labels": n_labels,
        }
        logger.info("Added scalar bar title=%s vertical=%s n_labels=%d", title, vertical, n_labels)

    def add_text_actor(self, text: Text) -> None:
        """Mock add_text_actor.

        Parameters
        ----------
        text : Text
            The text actor to add (stored but not rendered).

        """
        self.text_actors.append(text)
        logger.info("Added text actor: %s", text.input)

    def clear(self) -> None:
        """Mock clear.

        Removes all actors, lights, and text actors from the mock renderer.
        """
        self.actors = []
        self.lights = []
        self._scalar_bar = None
        self.text_actors = []
        logger.info("Cleared all actors")

    def set_background(self, color: tuple[float, float, float]) -> None:
        """Set the background color.

        Parameters
        ----------
        color : tuple
            RGB color tuple with values between 0 and 1.

        """
        self.background = color

    def view_vector(
        self,
        vector: tuple[float, float, float],
        viewup: tuple[float, float, float] | None = None,
    ) -> None:
        """Mock view_vector.

        Parameters
        ----------
        vector : tuple of float
            Direction vector (stored but not rendered).
        viewup : tuple of float, optional
            View-up vector (stored but not rendered).

        """
        self._view_vector = (float(vector[0]), float(vector[1]), float(vector[2]))
        if viewup is not None:
            self._view_up = (float(viewup[0]), float(viewup[1]), float(viewup[2]))
        logger.info("Set view vector: %s (viewup=%s)", vector, viewup)

    @property
    def camera(self) -> Camera | None:
        """Get or set the camera (mock).

        Parameters
        ----------
        camera : Camera
            Camera object (stored but not rendered).

        Returns
        -------
        Camera or None
            The current camera, or None if not set.

        """
        return self._camera

    @camera.setter
    def camera(self, camera: Camera) -> None:
        """Set the camera."""
        self._camera = camera
        logger.info("Set camera: %s", camera)

    def add_axes(self, **kwargs: object) -> None:  # noqa: ARG002
        """Mock add_axes.

        Parameters
        ----------
        **kwargs
            Reserved for future implementation.

        """
        logger.info("add_axes called (mock)")

    def set_environment_texture(self, texture: object) -> None:
        """Mock environment texture.

        Parameters
        ----------
        texture : str or CubeMap
            Environment texture (stored but not rendered).

        """
        logger.info("Set environment texture: %s", texture)

    def screenshot(
        self,
        filename: str | Path | None = None,
        transparent_background: bool | None = None,  # noqa: FBT001
        return_img: bool = True,  # noqa: FBT001, FBT002
        window_size: tuple[int, int] | list[int] | None = None,
        scale: int | None = None,
    ) -> np.ndarray | None:
        """Mock screenshot that returns a dummy numpy array.

        Parameters
        ----------
        filename : str, Path, or None, optional
            File path to save the image. If None, no file is written.
        transparent_background : bool or None, optional
            Whether to make the background transparent.
        return_img : bool, optional
            If True, return a numpy array of the image.
        window_size : tuple or list of int, optional
            Window size as (width, height). Default is (600, 400).
        scale : int or None, optional
            Scale factor for higher resolution.

        Returns
        -------
        numpy.ndarray or None
            Dummy image data as numpy array if return_img is True, otherwise None.

        """
        import numpy as np  # noqa: PLC0415

        width, height = (600, 400) if window_size is None else window_size
        if scale is not None:
            width *= scale
            height *= scale

        logger.info(
            "Mock screenshot: filename=%s size=(%d, %d) transparent=%s",
            filename,
            width,
            height,
            transparent_background,
        )

        if filename is not None:
            # Create a dummy PNG file
            try:
                from PIL import Image  # noqa: PLC0415
            except ImportError as e:  # pragma: no cover
                msg = "Pillow is required to save screenshot. Install it with: pip install pillow"
                raise ImportError(msg) from e

            channels = 4 if transparent_background else 3
            img = Image.new("RGBA" if transparent_background else "RGB", (width, height))
            img.save(filename)

        if return_img:
            # Return a dummy numpy array
            channels = 4 if transparent_background else 3
            return np.zeros((height, width, channels), dtype=np.uint8)
        return None


def get_renderer(
    lighting: str | None = "default",
    wasm_rendering: str = "webgl",
    wasm_mode: str = "sync",
) -> VTKWasmRenderer | BrowserRenderer | MockRenderer:
    """Get appropriate renderer for current environment.

    Automatically detects whether running in Pyodide/browser and
    returns the appropriate renderer implementation.

    Parameters
    ----------
    lighting : str or None, optional
        Lighting mode. ``"default"`` creates a default directional light,
        ``None`` creates no default lights. Default is ``"default"``.
    wasm_rendering : str, optional
        WebAssembly rendering backend. One of ``"webgl"`` or ``"webgpu"``.
        Default is ``"webgl"``.
    wasm_mode : str, optional
        Execution mode for VTK.wasm method calls. One of ``"sync"`` or
        ``"async"``. Default is ``"sync"``.

    Returns
    -------
    VTKWasmRenderer or BrowserRenderer or MockRenderer
        - VTKWasmRenderer if in Pyodide or IPython environment
        - BrowserRenderer in standard Python (opens the default browser)
        - MockRenderer if ``PYVISTA_JS_NO_BROWSER=1`` is set (for testing/CI)

    Examples
    --------
    >>> # Automatically gets the right renderer
    >>> renderer = get_renderer()  # doctest: +SKIP
    >>> # In Pyodide or Jupyter: returns VTKWasmRenderer
    >>> # In standard Python: returns BrowserRenderer (opens browser)
    >>> # Same code works in both environments
    >>> from pyvista_wasm import Sphere  # doctest: +SKIP
    >>> mesh = Sphere()  # doctest: +SKIP
    >>> renderer.add_mesh_actor(mesh, color='blue')  # doctest: +SKIP
    >>> renderer.create_container()  # doctest: +SKIP
    >>> renderer.render()  # doctest: +SKIP

    Notes
    -----
    This function is used internally by the Plotter class. You typically
    don't need to call it directly unless implementing custom rendering logic.

    Set the environment variable ``PYVISTA_JS_NO_BROWSER=1`` to suppress
    browser opening (useful for CI/CD and automated testing).

    """
    # Use VTKWasmRenderer if in Pyodide with VTK.wasm OR if IPython is available
    if (PYODIDE_ENV and VTK_AVAILABLE) or IPYTHON_AVAILABLE:
        return VTKWasmRenderer(
            lighting=lighting,
            wasm_rendering=wasm_rendering,
            wasm_mode=wasm_mode,
        )
    # Respect opt-out env var for CI/testing
    if os.environ.get("PYVISTA_JS_NO_BROWSER"):
        return MockRenderer(
            lighting=lighting,
            wasm_rendering=wasm_rendering,
            wasm_mode=wasm_mode,
        )
    return BrowserRenderer(
        lighting=lighting,
        wasm_rendering=wasm_rendering,
        wasm_mode=wasm_mode,
    )
