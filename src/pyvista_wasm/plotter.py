"""Plotter class for pyvista-wasm.

The Plotter provides the main interface for creating 3D visualizations
using VTK.wasm in browser environments.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, ClassVar

from .rendering import get_renderer

if TYPE_CHECKING:
    from pathlib import Path

    import numpy as np

    from .camera import Camera
    from .examples import CubeMap
    from .light import Light
    from .mesh import PolyData
    from .text import Text
    from .texture import Texture


class Plotter:
    """Main plotting interface for pyvista-wasm.

    This class provides a PyVista-like API for creating 3D visualizations
    in the browser using VTK.wasm as the rendering backend.

    Parameters
    ----------
    lighting : str or None, optional
        Lighting mode for the plotter. Options are:
        - ``"default"`` (default): Creates a default directional light
        - ``None``: No default lights are created, giving full control over lighting
    wasm_rendering : str, optional
        WebAssembly rendering backend. One of ``"webgl"`` or ``"webgpu"``.
        Default is ``"webgl"``.
    wasm_mode : str, optional
        Execution mode for VTK.wasm method calls. One of ``"sync"`` or
        ``"async"``. ``"async"`` requires WebAssembly JavaScript Promise
        Integration (JSPI) browser support. ``"webgpu"`` rendering always
        uses ``"async"`` regardless of this setting. Default is ``"sync"``.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> plotter = pv.Plotter()
    >>> mesh = pv.Sphere()
    >>> _ = plotter.add_mesh(mesh, color='red')
    >>> plotter.show()  # doctest: +SKIP

    Create a plotter with no default lights:

    >>> plotter = pv.Plotter(lighting=None)
    >>> light = pv.Light(position=(1, 1, 1), intensity=2.0)
    >>> plotter.add_light(light)
    >>> mesh = pv.Sphere()
    >>> _ = plotter.add_mesh(mesh, color='white')
    >>> plotter.show()  # doctest: +SKIP

    Create a plotter using WebGPU rendering:

    >>> plotter = pv.Plotter(wasm_rendering='webgpu')  # doctest: +SKIP

    """

    def __init__(
        self,
        lighting: str | None = "default",
        wasm_rendering: str = "webgl",
        wasm_mode: str = "sync",
    ) -> None:
        """Initialize a new Plotter instance.

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

        """
        self._actors: list[dict[str, object]] = []
        self._renderer = get_renderer(
            lighting=lighting,
            wasm_rendering=wasm_rendering,
            wasm_mode=wasm_mode,
        )
        self._background_color = (1.0, 1.0, 1.0)  # Default background color
        self._container_id = f"pyvista-container-{uuid.uuid4().hex[:8]}"
        self._camera: Camera | None = None
        self._scalar_bar: dict[str, Any] | None = None

    def add_mesh(  # noqa: PLR0913
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
        **kwargs: object,
    ) -> dict[str, object]:
        """Add a mesh to the plotter.

        Parameters
        ----------
        mesh : Mesh
            The mesh object to add to the scene.
        color : str or tuple, optional
            Color of the mesh. Can be a color name or RGB tuple.
        opacity : float, optional
            Opacity of the mesh, between 0 (transparent) and 1 (opaque).
        pbr : bool, optional
            Enable physically based rendering (PBR). Default is False.
        metallic : float, optional
            Metallic factor for PBR, between 0 (non-metallic) and 1 (fully
            metallic). Only used when ``pbr=True``. Default is 0.0.
        roughness : float, optional
            Roughness factor for PBR, between 0 (mirror-like) and 1 (fully
            rough). Only used when ``pbr=True``. Default is 0.5.
        smooth_shading : bool, optional
            Enable smooth shading (Gouraud interpolation). When True, the mesh
            surface appears smooth by interpolating normals across polygons.
            When False, flat shading is used where each polygon face has a
            uniform color. Default is True.
        texture : Texture, optional
            Surface texture to apply to the mesh. Create one with
            :class:`~pyvista_wasm.Texture`. The mesh should have texture
            coordinates set (e.g., via
            :meth:`~pyvista_wasm.PolyData.texture_map_to_plane`) or use a
            primitive (Sphere, Cube, Cylinder) that generates them automatically.
        show_edges : bool, optional
            Show the edges of the mesh. Default is False.
        edge_color : str or tuple, optional
            Color of the edges when ``show_edges=True``. Can be a color name
            or RGB tuple. If not specified, defaults to black.
        style : str, optional
            Visualization style of the mesh. One of ``'surface'`` (default),
            ``'wireframe'``, or ``'points'``.
        scalars : str, optional
            Name of the scalar array to use for coloring. The array must exist
            in ``mesh.point_data``.
        cmap : str, optional
            Name of the colormap to use when rendering scalars. Default is 'viridis'.
            Supported colormaps: 'viridis', 'plasma', 'inferno', 'magma', 'jet',
            'rainbow', 'turbo', 'coolwarm'.
        **kwargs
            Additional rendering options.

        Returns
        -------
        actor
            The VTK.wasm actor representing the mesh.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> mesh = pv.Sphere()
        >>> _ = plotter.add_mesh(mesh, color='red', opacity=0.8)

        PBR example:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> mesh = pv.Sphere()
        >>> _ = plotter.add_mesh(mesh, color='white', pbr=True, metallic=0.8, roughness=0.1)

        Texture example:

        >>> import pyvista_wasm as pv
        >>> from pyvista_wasm import examples
        >>> plotter = pv.Plotter()
        >>> sphere = pv.Sphere()
        >>> texture = examples.download_masonry_texture()  # doctest: +SKIP
        >>> _ = plotter.add_mesh(sphere, texture=texture)  # doctest: +SKIP
        >>> plotter.show()  # doctest: +SKIP

        Show edges:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> mesh = pv.Sphere()
        >>> _ = plotter.add_mesh(mesh, show_edges=True, edge_color='black')
        >>> plotter.show()  # doctest: +SKIP

        Wireframe rendering:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> mesh = pv.Cube()
        >>> _ = plotter.add_mesh(mesh, style='wireframe')
        >>> plotter.show()  # doctest: +SKIP

        Surface with edges:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> mesh = pv.Cube()
        >>> _ = plotter.add_mesh(mesh, style='surface', show_edges=True)
        >>> plotter.show()  # doctest: +SKIP

        Scalar coloring:

        >>> import pyvista_wasm as pv
        >>> mesh = pv.Sphere()
        >>> mesh['elevation'] = mesh.points[:, 2]
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()  # doctest: +SKIP

        Compare smooth shading (left) and flat shading (right) side by side:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> color = (0.8, 0.6, 0.2)
        >>> smooth = pv.Sphere(center=(-1.5, 0, 0), theta_resolution=8, phi_resolution=8)
        >>> _ = plotter.add_mesh(smooth, color=color, smooth_shading=True)
        >>> flat = pv.Sphere(center=(1.5, 0, 0), theta_resolution=8, phi_resolution=8)
        >>> _ = plotter.add_mesh(flat, color=color, smooth_shading=False)
        >>> plotter.show()  # doctest: +SKIP

        """
        # Add mesh to VTK.wasm renderer
        actor = self._renderer.add_mesh_actor(
            mesh,
            color=color,
            opacity=opacity,
            pbr=pbr,
            metallic=metallic,
            roughness=roughness,
            smooth_shading=smooth_shading,
            texture=texture,
            show_edges=show_edges,
            edge_color=edge_color,
            style=style,
            scalars=scalars,
            cmap=cmap,
        )

        # Store reference
        self._actors.append(
            {
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
                "actor": actor,
                "kwargs": kwargs,
            },
        )

        return actor

    def add_points(
        self,
        points: object,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        point_size: float = 5.0,
        render_points_as_spheres: bool = False,  # noqa: FBT001 FBT002
        **kwargs: object,
    ) -> dict[str, object]:
        """Add a point cloud to the plotter.

        Parameters
        ----------
        points : array-like or PolyData
            Point coordinates as an (n, 3) numpy array or PolyData object.
        color : str or tuple, optional
            Color of the points. Can be a color name or RGB tuple.
        opacity : float, optional
            Opacity of the points, between 0 (transparent) and 1 (opaque).
        point_size : float, optional
            Size of the points in pixels. Default is 5.0.
        render_points_as_spheres : bool, optional
            Render points as spheres instead of screen-space squares.
            Default is False.
        **kwargs
            Additional rendering options.

        Returns
        -------
        actor
            The VTK.wasm actor representing the point cloud.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> import numpy as np
        >>> points = np.random.rand(100, 3)
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_points(points, color='red', point_size=10)
        >>> plotter.show()  # doctest: +SKIP

        With spheres:

        >>> plotter = pv.Plotter()
        >>> points = np.random.rand(50, 3)
        >>> _ = plotter.add_points(
        ...     points, color='blue', point_size=8, render_points_as_spheres=True
        ... )
        >>> plotter.show()  # doctest: +SKIP

        """
        # Add points to VTK.wasm renderer
        actor = self._renderer.add_points_actor(
            points,
            color=color,
            opacity=opacity,
            point_size=point_size,
            render_points_as_spheres=render_points_as_spheres,
        )

        # Store reference
        self._actors.append(
            {
                "type": "points",
                "points": points,
                "color": color,
                "opacity": opacity,
                "point_size": point_size,
                "render_points_as_spheres": render_points_as_spheres,
                "actor": actor,
                "kwargs": kwargs,
            },
        )

        return actor

    def show(
        self,
        container_id: str | None = None,
        cpos: str
        | tuple[float, float, float]
        | tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ]
        | list[float]
        | list[tuple[float, float, float]]
        | list[list[float]]
        | None = None,
    ) -> None:
        """Display the visualization.

        In browser environments, this will render the scene using VTK.wasm.

        Parameters
        ----------
        container_id : str, optional
            HTML element ID for the visualization container.
            Defaults to a unique ID generated per Plotter instance to avoid
            conflicts when calling show() multiple times in the same session.
        cpos : str, tuple, or list, optional
            Camera position specification. Can be:

            - String shortcut: 'xy', 'xz', 'yz', 'yx', 'zx', 'zy', or 'iso'
            - Direction vector: 3-element tuple/list (x, y, z)
            - Full camera spec: 3-tuple/list of 3-tuples/lists:
              [(position), (focal_point), (view_up)]

        Examples
        --------
        Basic usage:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.show()  # doctest: +SKIP

        With camera position string shortcut:

        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.show(cpos='xy')

        With direction vector:

        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.show(cpos=(1, 0, 0))

        With full camera specification:

        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.show(cpos=[(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)])

        """
        # Set camera position if provided
        if cpos is not None:
            self.camera_position = cpos

        # Create container if needed
        self._renderer.create_container(container_id or self._container_id)

        # Render the scene
        self._renderer.render()

    def generate_standalone_html(self) -> str:
        """Generate a complete standalone HTML page with the current scene.

        Returns
        -------
        str
            A full HTML document string containing the visualization.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> html = plotter.generate_standalone_html()
        >>> '<!DOCTYPE html>' in html
        True

        """
        return self._renderer.generate_standalone_html()

    def view_vector(
        self,
        vector: tuple[float, float, float],
        viewup: tuple[float, float, float] | None = None,
    ) -> None:
        """Point the camera in the direction of the given vector.

        Parameters
        ----------
        vector : tuple of float
            Direction to point the camera in, given as (vx, vy, vz).
        viewup : tuple of float, optional
            View-up vector. Defaults to (0, 1, 0).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.view_vector((1, 0, 0))
        >>> plotter.show()  # doctest: +SKIP

        View from an isometric angle:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Cube())
        >>> plotter.view_vector((1, 1, 1))
        >>> plotter.show()  # doctest: +SKIP

        """
        self._renderer.view_vector(vector, viewup=viewup)

    def view_xy(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the XY plane.

        Look down the Z-axis, with the positive Z-axis pointing toward
        the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Z direction (down the +Z axis). Default is
            False (look down the -Z axis).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.view_xy()
        >>> plotter.show()  # doctest: +SKIP

        View from the negative Z direction:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Cube())
        >>> plotter.view_xy(negative=True)
        >>> plotter.show()  # doctest: +SKIP

        """
        vector = (0.0, 0.0, -1.0) if negative else (0.0, 0.0, 1.0)
        self.view_vector(vector)

    def view_xz(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the XZ plane.

        Look down the Y-axis, with the positive Y-axis pointing toward
        the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Y direction (down the +Y axis). Default is
            False (look down the -Y axis).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.view_xz()
        >>> plotter.show()  # doctest: +SKIP

        View from the negative Y direction:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Cube())
        >>> plotter.view_xz(negative=True)
        >>> plotter.show()  # doctest: +SKIP

        """
        vector = (0.0, -1.0, 0.0) if negative else (0.0, 1.0, 0.0)
        self.view_vector(vector, viewup=(0.0, 0.0, 1.0))

    def view_yz(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the YZ plane.

        Look down the X-axis, with the positive X-axis pointing toward
        the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative X direction (down the +X axis). Default is
            False (look down the -X axis).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.view_yz()
        >>> plotter.show()  # doctest: +SKIP

        View from the negative X direction:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Cube())
        >>> plotter.view_yz(negative=True)
        >>> plotter.show()  # doctest: +SKIP

        """
        vector = (-1.0, 0.0, 0.0) if negative else (1.0, 0.0, 0.0)
        self.view_vector(vector)

    def view_yx(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the YX plane (inverse of XY).

        Look down the Z-axis from below, with the negative Z-axis pointing
        toward the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Z direction (down the +Z axis). Default is
            False (look down the -Z axis).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.view_yx()
        >>> plotter.show()

        """
        vector = (0.0, 0.0, 1.0) if negative else (0.0, 0.0, -1.0)
        self.view_vector(vector)

    def view_zx(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the ZX plane (inverse of XZ).

        Look down the Y-axis from below, with the negative Y-axis pointing
        toward the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Y direction (down the +Y axis). Default is
            False (look down the -Y axis).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.view_zx()
        >>> plotter.show()

        """
        vector = (0.0, 1.0, 0.0) if negative else (0.0, -1.0, 0.0)
        self.view_vector(vector, viewup=(0.0, 0.0, 1.0))

    def view_zy(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the ZY plane (inverse of YZ).

        Look down the X-axis from the left, with the negative X-axis pointing
        toward the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative X direction (down the +X axis). Default is
            False (look down the -X axis).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.view_zy()
        >>> plotter.show()

        """
        vector = (1.0, 0.0, 0.0) if negative else (-1.0, 0.0, 0.0)
        self.view_vector(vector)

    def view_isometric(self) -> None:
        """View the scene from an isometric angle.

        The isometric view shows all three axes equally, looking from the
        (1, 1, 1) direction.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Cube())
        >>> plotter.view_isometric()
        >>> plotter.show()  # doctest: +SKIP

        """
        self.view_vector((1.0, 1.0, 1.0))

    def set_environment_texture(self, texture: str | CubeMap) -> None:
        """Set the environment texture for image-based lighting (IBL).

        Used with PBR materials to provide realistic reflections and lighting.

        Parameters
        ----------
        texture : str or CubeMap
            Either a URL string pointing to an equirectangular image, or a
            :class:`~pyvista_wasm.examples.CubeMap` returned by
            :func:`~pyvista_wasm.examples.download_sky_box_cube_map`.

        Examples
        --------
        URL string:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere(), color='white', pbr=True, metallic=1.0, roughness=0.1)
        >>> plotter.set_environment_texture('https://example.com/env.jpg')  # doctest: +SKIP
        >>> plotter.show()  # doctest: +SKIP

        CubeMap:

        >>> import pyvista_wasm as pv
        >>> from pyvista_wasm import examples
        >>> cubemap = examples.download_sky_box_cube_map()  # doctest: +SKIP
        >>> plotter = pv.Plotter()  # doctest: +SKIP
        >>> _ = plotter.add_mesh(  # doctest: +SKIP
        ...     pv.Sphere(), color='white', pbr=True, metallic=1.0, roughness=0.1)
        >>> plotter.set_environment_texture(cubemap)  # doctest: +SKIP
        >>> plotter.show()  # doctest: +SKIP

        """
        self._renderer.set_environment_texture(texture)

    def add_light(self, light: Light) -> None:
        """Add a light source to the scene.

        Parameters
        ----------
        light : Light
            The :class:`~pyvista_wasm.light.Light` to add.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere(), color='white')
        >>> light = pv.Light(position=(5, 5, 5), color='white', intensity=2.0)
        >>> plotter.add_light(light)
        >>> plotter.show()  # doctest: +SKIP

        """
        self._renderer.add_light(light)

    def add_text(self, text: Text) -> None:
        """Add a text annotation to the scene.

        Parameters
        ----------
        text : Text
            The :class:`~pyvista_wasm.text.Text` to add.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere(), color='white')
        >>> text = pv.Text("Hello World", position=(0.5, 0.9))
        >>> plotter.add_text(text)
        >>> plotter.show()

        """
        self._renderer.add_text_actor(text)

    def add_axes(self, **kwargs: object) -> None:
        """Add an orientation marker (axes indicator) to the viewport.

        Displays XYZ axes in the corner of the viewport to help orient
        the viewer. Backed by VTK.wasm ``vtkOrientationMarkerWidget``.

        Parameters
        ----------
        **kwargs
            Reserved for future implementation. Currently accepts no parameters.

        Examples
        --------
        Basic usage:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.add_axes()
        >>> plotter.show()  # doctest: +SKIP

        With multiple meshes:

        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere(), color='red')
        >>> _ = plotter.add_mesh(pv.Cube(center=(2, 0, 0)), color='blue')
        >>> plotter.add_axes()
        >>> plotter.show()  # doctest: +SKIP

        """
        self._renderer.add_axes(**kwargs)

    def add_scalar_bar(
        self,
        title: str = "",
        vertical: bool = True,  # noqa: FBT001, FBT002
        n_labels: int = 5,
    ) -> None:
        """Add a scalar bar to display the color legend.

        This method adds a scalar bar (color legend) that shows the mapping
        between scalar values and colors. The scalar bar is linked to the
        active scalar colormap from the most recently added mesh.

        Parameters
        ----------
        title : str, optional
            Title text to display on the scalar bar. Default is an empty string.
        vertical : bool, optional
            Whether to orient the scalar bar vertically (True) or horizontally
            (False). Default is True.
        n_labels : int, optional
            Number of labels to display on the scalar bar. Default is 5.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> import numpy as np
        >>> mesh = pv.Sphere()
        >>> mesh['height'] = mesh.points[:, 2]  # doctest: +SKIP
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(mesh, scalars='height', cmap='viridis')  # doctest: +SKIP
        >>> plotter.add_scalar_bar(title='Height', vertical=True)
        >>> plotter.show()  # doctest: +SKIP

        Horizontal scalar bar:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(mesh, scalars='height', cmap='viridis')  # doctest: +SKIP
        >>> plotter.add_scalar_bar(title='Height', vertical=False, n_labels=7)
        >>> plotter.show()  # doctest: +SKIP

        """
        self._scalar_bar = {
            "title": title,
            "vertical": vertical,
            "n_labels": n_labels,
        }
        self._renderer.add_scalar_bar(title=title, vertical=vertical, n_labels=n_labels)

    def clear(self) -> None:
        """Clear all actors from the plotter.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.clear()

        """
        self._actors = []
        self._scalar_bar = None
        self._renderer.clear()

    @property
    def actors(self) -> list[dict[str, Any]]:
        """Return the list of actors in the plotter."""
        return self._actors

    @property
    def camera(self) -> Camera | None:
        """Get or set the camera for the plotter.

        Parameters
        ----------
        cam : Camera
            The camera object to use for rendering.

        Returns
        -------
        Camera or None
            The current camera, or None if not set.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> camera = pv.Camera()
        >>> camera.position = (5, 5, 5)
        >>> camera.focal_point = (0, 0, 0)
        >>> plotter.camera = camera
        >>> plotter.show()  # doctest: +SKIP

        """
        return self._camera

    @camera.setter
    def camera(self, cam: Camera) -> None:
        """Set the camera."""
        self._camera = cam
        self._renderer.camera = cam

    @property
    def camera_position(
        self,
    ) -> (
        tuple[float, float, float]
        | tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ]
        | None
    ):
        """Get the camera position.

        Returns
        -------
        tuple or None
            If a camera is set, returns a 3-tuple of 3-tuples:
            (position, focal_point, view_up).
            Otherwise returns None.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = [(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        >>> plotter.camera_position
        ((2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))

        """
        if self._camera is not None:
            return (
                self._camera.position,
                self._camera.focal_point,
                self._camera.view_up,
            )
        return None

    @camera_position.setter
    def camera_position(
        self,
        cpos: str
        | tuple[float, float, float]
        | tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ]
        | list[float]
        | list[tuple[float, float, float]]
        | list[list[float]],
    ) -> None:
        """Set the camera position.

        Parameters
        ----------
        cpos : str, tuple, or list
            Camera position specification. Can be:

            - String shortcut: 'xy', 'xz', 'yz', 'yx', 'zx', 'zy', or 'iso'
            - Direction vector: 3-element tuple/list (x, y, z)
            - Full camera spec: 3-tuple/list of 3-tuples/lists:
              [(position), (focal_point), (view_up)]

        Examples
        --------
        Using string shortcuts:

        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = 'xy'
        >>> plotter.camera_position = 'iso'

        Using direction vector:

        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = (1, 0, 0)

        Using full camera specification:

        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = [(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

        """
        if isinstance(cpos, str):
            self._set_camera_position_from_str(cpos)
        elif isinstance(cpos, (tuple, list)):
            self._set_camera_position_from_sequence(cpos)
        else:
            msg = f"Invalid camera position type: {type(cpos)}. Expected string, tuple, or list"  # type: ignore[unreachable]
            raise TypeError(msg)

    #: Maps camera position string shortcuts to the corresponding view method name.
    _CAMERA_POSITION_SHORTCUTS: ClassVar[dict[str, str]] = {
        "xy": "view_xy",
        "xz": "view_xz",
        "yz": "view_yz",
        "yx": "view_yx",
        "zx": "view_zx",
        "zy": "view_zy",
        "iso": "view_isometric",
    }

    def _set_camera_position_from_str(self, cpos: str) -> None:
        """Set camera position from a string shortcut."""
        key = cpos.lower()
        method = self._CAMERA_POSITION_SHORTCUTS.get(key)
        if method is None:
            msg = (
                f"Unknown camera position string: '{cpos}'. "
                "Supported: 'xy', 'xz', 'yz', 'yx', 'zx', 'zy', 'iso'"
            )
            raise ValueError(msg)
        getattr(self, method)()

    def _set_camera_position_from_sequence(
        self,
        cpos: tuple[float, float, float]
        | tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ]
        | list[float]
        | list[tuple[float, float, float]]
        | list[list[float]],
    ) -> None:
        """Set camera position from a tuple or list."""
        vector_length = 3
        if len(cpos) == vector_length and all(isinstance(x, (int, float)) for x in cpos):
            self.view_vector((float(cpos[0]), float(cpos[1]), float(cpos[2])))  # type: ignore[arg-type]
            return

        if len(cpos) == vector_length and all(
            isinstance(item, (tuple, list))
            and len(item) == vector_length
            and all(isinstance(x, (int, float)) for x in item)
            for item in cpos
        ):
            from .camera import Camera  # noqa: PLC0415

            self.camera = Camera(
                position=(float(cpos[0][0]), float(cpos[0][1]), float(cpos[0][2])),  # type: ignore[index]
                focal_point=(float(cpos[1][0]), float(cpos[1][1]), float(cpos[1][2])),  # type: ignore[index]
                view_up=(float(cpos[2][0]), float(cpos[2][1]), float(cpos[2][2])),  # type: ignore[index]
            )
            return

        msg = (
            "Invalid camera position format. Expected: "
            "3-element direction vector or 3x3 camera specification"
        )
        raise ValueError(msg)

    @property
    def background_color(self) -> tuple[float, float, float]:
        """Get or set the background color.

        Parameters
        ----------
        color : str or tuple
            Color name (e.g., 'white', 'black', 'red') or RGB tuple
            with values between 0 and 1 (e.g., (1.0, 1.0, 1.0) for white).

        Returns
        -------
        tuple
            RGB color tuple with values between 0 and 1.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> plotter.background_color = 'white'
        >>> plotter.background_color
        (1.0, 1.0, 1.0)
        >>> plotter.background_color = (0.5, 0.5, 0.5)

        """
        return self._background_color

    @background_color.setter
    def background_color(self, color: str | tuple[float, float, float]) -> None:
        """Set the background color."""
        self._background_color = self._parse_color(color)
        # Update renderer's background color
        self._renderer.set_background(self._background_color)

    def _parse_color(
        self,
        color: str | tuple[float, float, float] | list[float],
    ) -> tuple[float, float, float]:
        """Parse color input to RGB tuple.

        Parameters
        ----------
        color : str or tuple
            Color as string name or RGB tuple.

        Returns
        -------
        tuple
            RGB color tuple with values between 0 and 1.

        """
        # Common color names
        color_map = {
            "white": (1.0, 1.0, 1.0),
            "black": (0.0, 0.0, 0.0),
            "red": (1.0, 0.0, 0.0),
            "green": (0.0, 1.0, 0.0),
            "blue": (0.0, 0.0, 1.0),
            "yellow": (1.0, 1.0, 0.0),
            "cyan": (0.0, 1.0, 1.0),
            "magenta": (1.0, 0.0, 1.0),
            "gray": (0.5, 0.5, 0.5),
            "grey": (0.5, 0.5, 0.5),
            "orange": (1.0, 0.647, 0.0),
            "purple": (0.5, 0.0, 0.5),
            "pink": (1.0, 0.753, 0.796),
            "brown": (0.647, 0.165, 0.165),
        }

        if isinstance(color, str):
            color_lower = color.lower()
            if color_lower in color_map:
                return color_map[color_lower]
            msg = f"Unknown color name: '{color}'. Supported colors: {', '.join(color_map.keys())}"
            raise ValueError(
                msg,
            )
        if isinstance(color, (tuple, list)):
            rgb_size = 3
            if len(color) != rgb_size:
                msg = f"RGB color must have 3 values, got {len(color)}"
                raise ValueError(msg)
            # Validate values are between 0 and 1
            for val in color:
                if not 0 <= val <= 1:
                    msg = f"RGB values must be between 0 and 1, got {val}"
                    raise ValueError(msg)
            return (color[0], color[1], color[2])
        msg = f"Color must be a string or RGB tuple, got {type(color)}"  # type: ignore[unreachable]
        raise TypeError(msg)

    def enable_parallel_projection(self) -> None:
        """Enable parallel (orthographic) projection.

        Switches the camera from perspective projection to parallel projection.
        This is useful for viewing 2D datasets, CAD-like orthographic views,
        and scientific visualization where perspective distortion is undesirable.

        If no camera is set, creates a default camera with parallel projection enabled.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Cube())
        >>> plotter.enable_parallel_projection()
        >>> plotter.view_isometric()
        >>> plotter.show()  # doctest: +SKIP

        """
        if self._camera is None:
            from .camera import Camera  # noqa: PLC0415

            self._camera = Camera()
            self._renderer.camera = self._camera

        self._camera.enable_parallel_projection()

    def disable_parallel_projection(self) -> None:
        """Disable parallel projection (use perspective projection).

        Switches the camera from parallel projection to perspective projection.

        If no camera is set, creates a default camera with perspective projection.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(pv.Sphere())
        >>> plotter.enable_parallel_projection()
        >>> plotter.disable_parallel_projection()
        >>> plotter.show()  # doctest: +SKIP

        """
        if self._camera is None:
            from .camera import Camera  # noqa: PLC0415

            self._camera = Camera()
            self._renderer.camera = self._camera

        self._camera.disable_parallel_projection()

    def screenshot(
        self,
        filename: str | Path | None = None,
        transparent_background: bool | None = None,  # noqa: FBT001
        return_img: bool = True,  # noqa: FBT001, FBT002
        window_size: tuple[int, int] | list[int] | None = None,
        scale: int | None = None,
    ) -> np.ndarray | None:
        """Take a screenshot of the current scene.

        Parameters
        ----------
        filename : str, Path, or None, optional
            File path to save the image. If ``None``, no file is written.
            Supported formats: PNG, JPEG. Default is ``None``.
        transparent_background : bool or None, optional
            Whether to make the background transparent. If ``None``, uses the
            current background setting. Default is ``None``.
        return_img : bool, optional
            If ``True``, return a numpy array of the image. Default is ``True``.
        window_size : tuple or list of int, optional
            Temporarily resize the window to ``(width, height)`` before capturing.
            If ``None``, uses the current window size. Default is ``None``.
        scale : int or None, optional
            Scale factor for the window size to produce a higher-resolution image.
            For example, ``scale=2`` will double the resolution. Default is ``None``.

        Returns
        -------
        numpy.ndarray or None
            If ``return_img`` is ``True``, returns a numpy array with shape
            ``(height, width, 3)`` for RGB or ``(height, width, 4)`` for RGBA
            (when ``transparent_background=True``). Otherwise returns ``None``.

        Examples
        --------
        Save a screenshot to a file:

        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> pl = pv.Plotter()
        >>> _ = pl.add_mesh(sphere)
        >>> pl.screenshot("screenshot.png")  # doctest: +SKIP

        Get image data as numpy array:

        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> pl = pv.Plotter()
        >>> _ = pl.add_mesh(sphere)
        >>> img = pl.screenshot(return_img=True)  # doctest: +SKIP
        >>> img.shape  # doctest: +SKIP
        (400, 600, 3)

        High-resolution screenshot with scaling:

        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> pl = pv.Plotter()
        >>> _ = pl.add_mesh(sphere)
        >>> pl.screenshot("high_res.png", scale=2)  # doctest: +SKIP

        Screenshot with transparent background:

        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> pl = pv.Plotter()
        >>> _ = pl.add_mesh(sphere)
        >>> pl.screenshot("transparent.png", transparent_background=True)  # doctest: +SKIP

        """
        return self._renderer.screenshot(
            filename=filename,
            transparent_background=transparent_background,
            return_img=return_img,
            window_size=window_size,
            scale=scale,
        )

    def __getstate__(self) -> dict[str, object]:
        """Return state for pickling.

        Excludes the renderer (browser-specific) and actor references,
        keeping only the serializable mesh data and rendering parameters.

        Returns
        -------
        dict
            State dictionary containing actors list, background color,
            container ID, and camera.

        """
        # Create a picklable copy of actors without the actor objects
        picklable_actors = []
        for actor_info in self._actors:
            # Copy actor info but exclude the unpicklable 'actor' object
            actor_copy = {key: value for key, value in actor_info.items() if key != "actor"}
            picklable_actors.append(actor_copy)

        return {
            "_actors": picklable_actors,
            "_background_color": self._background_color,
            "_container_id": self._container_id,
            "_camera": self._camera,
        }

    def __setstate__(self, state: dict[str, object]) -> None:
        """Restore state from pickle.

        Reconstructs the plotter from pickled state by recreating the
        renderer and restoring all actors.

        Parameters
        ----------
        state : dict
            State dictionary from __getstate__.

        """
        # Restore basic attributes
        self._actors = state["_actors"]  # type: ignore[assignment]
        self._background_color = state["_background_color"]  # type: ignore[assignment]
        self._container_id = state["_container_id"]  # type: ignore[assignment]
        self._camera = state["_camera"]  # type: ignore[assignment]

        # Recreate the renderer
        self._renderer = get_renderer()
        self._renderer.set_background(self._background_color)
