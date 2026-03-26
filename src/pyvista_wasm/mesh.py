"""Mesh classes for pyvista-wasm.

Provides geometric primitives and mesh handling compatible with PyVista API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

    from numpy.typing import ArrayLike


class PointData:
    """Dict-like container for point data arrays.

    This class provides a dictionary interface for storing named scalar arrays
    associated with mesh points, mimicking PyVista's point_data API.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> import numpy as np
    >>> mesh = pv.Sphere()
    >>> mesh.point_data['elevation'] = mesh.points[:, 2]
    >>> 'elevation' in mesh.point_data
    True

    Render with scalar coloring:

    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
    >>> plotter.show()  # doctest: +SKIP

    """

    def __init__(self) -> None:
        """Initialize an empty PointData container."""
        self._arrays: dict[str, np.ndarray] = {}

    def __setitem__(self, name: str, array: ArrayLike) -> None:
        """Set a named array.

        Parameters
        ----------
        name : str
            Name of the array.
        array : array-like
            Data array to store.

        """
        self._arrays[name] = np.asarray(array)

    def __getitem__(self, name: str) -> np.ndarray:
        """Get a named array.

        Parameters
        ----------
        name : str
            Name of the array.

        Returns
        -------
        np.ndarray
            The requested array.

        """
        return self._arrays[name]

    def __contains__(self, name: str) -> bool:
        """Check if an array with the given name exists.

        Parameters
        ----------
        name : str
            Name to check.

        Returns
        -------
        bool
            True if the array exists.

        """
        return name in self._arrays

    def __len__(self) -> int:
        """Return the number of arrays."""
        return len(self._arrays)

    def keys(self) -> list[str]:
        """Return the names of all arrays.

        Returns
        -------
        list
            List of array names.

        """
        return list(self._arrays.keys())

    def items(self) -> list[tuple[str, np.ndarray]]:
        """Return (name, array) pairs.

        Returns
        -------
        list
            List of (name, array) tuples.

        """
        return list(self._arrays.items())

    def values(self) -> list[np.ndarray]:
        """Return all arrays.

        Returns
        -------
        list
            List of arrays.

        """
        return list(self._arrays.values())


_CIRCLE_MIN_RESOLUTION = 3
_VECTOR_COMPONENTS = 3  # Number of components in a 3D vector (x, y, z)
_TUBE_MIN_SIDES = 3


class PolyData:
    """Base polygonal mesh class.

    Parameters
    ----------
    points : array-like
        Vertex coordinates as an (n, 3) array.
    faces : array-like, optional
        Cell connectivity information.

    """

    def __init__(
        self,
        points: ArrayLike,
        faces: ArrayLike | None = None,
        *,
        t_coords: ArrayLike | None = None,
        scalars: ArrayLike | None = None,
        scalar_name: str = "scalars",
        _scene_data: dict[str, object] | None = None,
    ) -> None:
        """Initialize a PolyData mesh."""
        self.points = np.asarray(points)
        self.faces = np.asarray(faces) if faces is not None else None
        self.t_coords = np.asarray(t_coords) if t_coords is not None else None
        self.scalars = np.asarray(scalars) if scalars is not None else None
        self.scalar_name = scalar_name
        self._scene_data = _scene_data
        self._point_data = PointData()

    @property
    def point_data(self) -> PointData:
        """Access point data arrays.

        Returns
        -------
        PointData
            Dict-like container for point data arrays.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> import numpy as np
        >>> mesh = pv.Sphere()
        >>> mesh.point_data['elevation'] = mesh.points[:, 2]
        >>> 'elevation' in mesh.point_data
        True

        Render with scalar coloring:

        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()  # doctest: +SKIP

        """
        return self._point_data

    def __setitem__(self, name: str, array: ArrayLike) -> None:
        """Set a point data array using dictionary-style access.

        Parameters
        ----------
        name : str
            Name of the array.
        array : array-like
            Data array to store.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> import numpy as np
        >>> mesh = pv.Sphere()
        >>> mesh['elevation'] = mesh.points[:, 2]
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()  # doctest: +SKIP

        """
        self._point_data[name] = array

    def __getitem__(self, name: str) -> np.ndarray:
        """Get a point data array using dictionary-style access.

        Parameters
        ----------
        name : str
            Name of the array.

        Returns
        -------
        np.ndarray
            The requested array.

        """
        return self._point_data[name]

    @property
    def n_points(self) -> int:
        """Return the number of points."""
        return len(self.points)

    @property
    def bounding_sphere(self) -> tuple[float, tuple[float, float, float]]:
        """Compute the radius and center of a bounding sphere.

        Uses Ritter's algorithm to approximate the minimum bounding sphere.
        Returns NaN values if there are no points.

        Returns
        -------
        float, tuple
            Sphere radius as a float and center as a tuple of floats ``(x, y, z)``.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> mesh = pv.Sphere(radius=1.5, center=(1, 2, 3))
        >>> radius, center = mesh.bounding_sphere
        >>> round(radius, 5)
        1.5
        >>> [round(c, 5) for c in center]
        [1.0, 2.0, 3.0]

        """
        if self.n_points == 0:
            nan = float("nan")
            return nan, (nan, nan, nan)

        pts = self.points.astype(float)

        # Ritter's algorithm
        p = pts[0]
        dists = np.linalg.norm(pts - p, axis=1)
        q = pts[np.argmax(dists)]
        dists = np.linalg.norm(pts - q, axis=1)
        r = pts[np.argmax(dists)]

        center = (q + r) / 2.0
        radius = float(np.linalg.norm(r - q) / 2.0)

        for pt in pts:
            d = float(np.linalg.norm(pt - center))
            if d > radius:
                radius = (radius + d) / 2.0
                center = center + (d - radius) / d * (pt - center)

        return radius, (float(center[0]), float(center[1]), float(center[2]))

    @property
    def n_faces(self) -> int:
        """Return the number of faces."""
        return len(self.faces) if self.faces is not None else 0

    def plot(
        self,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
    ) -> None:
        """Plot this mesh.

        This is a convenience method that creates a :class:`~pyvista_wasm.Plotter`,
        adds this mesh, and calls :func:`~pyvista_wasm.Plotter.show`.

        Parameters
        ----------
        color : str or tuple, optional
            Color of the mesh. Can be a color name or RGB tuple.
        opacity : float, optional
            Opacity of the mesh, between 0 (transparent) and 1 (opaque).
        pbr : bool, optional
            Enable physically based rendering (PBR). Default is False.
        metallic : float, optional
            Metallic factor for PBR, between 0 and 1. Default is 0.0.
        roughness : float, optional
            Roughness factor for PBR, between 0 and 1. Default is 0.5.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> sphere.plot(color='red')  # doctest: +SKIP

        """
        from .plotter import Plotter  # noqa: PLC0415

        plotter = Plotter()
        plotter.add_mesh(
            self,
            color=color,
            opacity=opacity,
            pbr=pbr,
            metallic=metallic,
            roughness=roughness,
        )
        plotter.show()

    def save(self, filename: str | Path) -> None:
        """Write this mesh to disk using meshio.

        The file format is inferred from the extension of ``filename``.
        Any format supported by `meshio <https://github.com/nschloe/meshio>`_
        can be used (e.g. ``'.obj'``, ``'.vtk'``, ``'.ply'``, ``'.stl'``).

        .. note::

            Requires ``meshio`` to be installed::

                pip install "pyvista-wasm[io]"

            In Pyodide / JupyterLite, install it with micropip before calling
            this method::

                import micropip
                await micropip.install("meshio")

        Parameters
        ----------
        filename : str or Path
            Output path. The extension determines the file format.

        Returns
        -------
        None

        Raises
        ------
        ImportError
            If ``meshio`` is not installed.

        Examples
        --------
        >>> from pyvista_wasm import examples
        >>> mesh = examples.download_trumpet()  # doctest: +SKIP
        >>> mesh.save('trumpet.obj')  # doctest: +SKIP

        """
        try:
            import meshio  # noqa: PLC0415
        except ImportError:
            msg = (
                "meshio is required for save(). "
                "Install it with: pip install 'pyvista-wasm[io]'\n"
                "In Pyodide: await micropip.install('meshio')"
            )
            raise ImportError(msg) from None

        cells = self._meshio_cells()
        mesh = meshio.Mesh(points=self.points, cells=cells)
        mesh.write(str(filename))

    def _meshio_cells(self) -> list:
        """Build a meshio-compatible cell list from ``self.faces``."""
        if self.faces is None or len(self.faces) == 0:
            return []

        from collections import defaultdict  # noqa: PLC0415

        groups: dict = defaultdict(list)
        for face in self.faces:
            groups[len(face)].append(face)

        _CELL_TYPES = {3: "triangle", 4: "quad"}  # noqa: N806
        return [(_CELL_TYPES.get(n, "polygon"), np.array(faces)) for n, faces in groups.items()]

    def shrink(self, shrink_factor: float = 0.8) -> PolyData:
        """Shrink the cells of a mesh towards their centroid.

        This filter shrinks the individual cells of a mesh towards their
        centroids, producing visual separation between adjacent cells.
        It mirrors the PyVista ``shrink`` filter API.

        .. note::

            The shrink is computed in JavaScript at render time by
            iterating over the cell array from the VTK.wasm source,
            moving each vertex toward its cell's centroid.
            ``VTK.wasm`` does not include ``vtkShrinkFilter``, so this
            filter is implemented as a custom JavaScript pass.

        Parameters
        ----------
        shrink_factor : float, optional
            The factor to shrink each cell by, between 0 and 1.
            A value of 1.0 produces no change; lower values produce
            more shrinkage. Default is 0.8.

        Returns
        -------
        PolyData
            A new mesh with shrunk cells.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> shrunk = sphere.shrink(shrink_factor=0.8)
        >>> isinstance(shrunk, pv.PolyData)
        True

        Render the shrunk mesh:

        >>> shrunk.plot()  # doctest: +SKIP

        """
        if not (0.0 <= shrink_factor <= 1.0):
            msg = f"shrink_factor must be between 0 and 1, got {shrink_factor}"
            raise ValueError(msg)

        base_scene = (
            dict(self._scene_data)
            if self._scene_data
            else {
                "type": "mesh",
                "points": self.points.flatten().tolist(),
            }
        )
        base_scene.setdefault("filters", [])
        filters_list: list[object] = base_scene["filters"]  # type: ignore[assignment]
        filters_list.append(
            {
                "type": "shrink",
                "shrinkFactor": shrink_factor,
            },
        )

        return PolyData(
            points=self.points,
            faces=self.faces,
            _scene_data=base_scene,
        )

    def clip(
        self,
        normal: str | tuple[float, float, float] = "x",
        origin: tuple[float, float, float] | None = None,
        *,
        invert: bool = False,
    ) -> PolyData:
        """Clip the mesh with a plane.

        This filter clips the mesh with a plane defined by a normal vector
        and an origin point. Points on one side of the plane are removed.
        It mirrors the PyVista ``clip`` filter API.

        .. note::

            The clipping is performed at render time using VTK.wasm's
            built-in ``vtkClipPolyData`` filter with a ``vtkPlane``
            clip function.

        Parameters
        ----------
        normal : str or tuple of float, optional
            The normal vector of the clipping plane. Can be a string
            specifying a cardinal direction ('x', 'y', 'z', '-x', '-y', '-z')
            or a 3-tuple of floats (nx, ny, nz). Default is 'x'.
        origin : tuple of float, optional
            The origin point of the clipping plane as (x, y, z).
            If not provided, defaults to the center of the mesh's bounding box.
        invert : bool, optional
            If True, flip the clipping direction to keep the part that would
            normally be removed. Default is False.

        Returns
        -------
        PolyData
            A new mesh with clipped cells removed.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> clipped = sphere.clip(normal='x', origin=(0, 0, 0))
        >>> isinstance(clipped, pv.PolyData)
        True

        Clip along the negative Y axis:

        >>> clipped = sphere.clip(normal='-y')
        >>> isinstance(clipped, pv.PolyData)
        True

        Clip with a custom normal vector:

        >>> clipped = sphere.clip(normal=(1, 1, 0), origin=(0, 0, 0))
        >>> isinstance(clipped, pv.PolyData)
        True

        Render the clipped mesh:

        >>> clipped.plot()  # doctest: +SKIP

        """
        # Parse normal vector
        if isinstance(normal, str):
            normal_map = {
                "x": (1.0, 0.0, 0.0),
                "+x": (1.0, 0.0, 0.0),
                "-x": (-1.0, 0.0, 0.0),
                "y": (0.0, 1.0, 0.0),
                "+y": (0.0, 1.0, 0.0),
                "-y": (0.0, -1.0, 0.0),
                "z": (0.0, 0.0, 1.0),
                "+z": (0.0, 0.0, 1.0),
                "-z": (0.0, 0.0, -1.0),
            }
            if normal not in normal_map:
                msg = f"Invalid normal string '{normal}'. Must be one of {list(normal_map.keys())}"
                raise ValueError(msg)
            normal_vec = normal_map[normal]
        else:
            if len(normal) != _VECTOR_COMPONENTS:  # type: ignore[arg-type]
                msg = f"Normal vector must have {_VECTOR_COMPONENTS} components, got {len(normal)}"  # type: ignore[arg-type]
                raise ValueError(msg)
            n = [float(x) for x in normal]  # type: ignore[arg-type]
            normal_vec = (n[0], n[1], n[2])

        # Compute origin if not provided (use center of bounding box)
        if origin is None:
            pts = self.points
            origin = (
                float((pts[:, 0].min() + pts[:, 0].max()) / 2),
                float((pts[:, 1].min() + pts[:, 1].max()) / 2),
                float((pts[:, 2].min() + pts[:, 2].max()) / 2),
            )
        else:
            if len(origin) != _VECTOR_COMPONENTS:
                msg = f"Origin must have {_VECTOR_COMPONENTS} components, got {len(origin)}"
                raise ValueError(msg)
            o = [float(x) for x in origin]
            origin = (o[0], o[1], o[2])

        base_scene = (
            dict(self._scene_data)
            if self._scene_data
            else {
                "type": "mesh",
                "points": self.points.flatten().tolist(),
            }
        )
        base_scene.setdefault("filters", [])
        filters_list: list[object] = base_scene["filters"]  # type: ignore[assignment]
        filters_list.append(
            {
                "type": "clip",
                "normal": list(normal_vec),
                "origin": list(origin),
                "invert": invert,
            },
        )

        return PolyData(
            points=self.points,
            faces=self.faces,
            _scene_data=base_scene,
        )

    def tube(
        self,
        *,
        radius: float = 0.5,
        n_sides: int = 20,
        capping: bool = True,  # noqa: ARG002
    ) -> PolyData:
        """Generate a tube around a line polydata.

        This filter creates a tube representation around lines in the mesh
        by sweeping a polygonal cross-section along each line. It mirrors
        the PyVista ``tube`` filter API and is backed by VTK.wasm's
        ``vtkTubeFilter``.

        .. note::

            This filter is intended for use with line-based polydata (such as
            the output of :class:`Line`). It uses VTK.wasm's ``vtkTubeFilter``,
            which generates a tube by sweeping a circle with ``n_sides`` sides
            along the line segments.

        Parameters
        ----------
        radius : float, optional
            The radius of the tube. Default is 0.5.
        n_sides : int, optional
            The number of sides for the tube cross-section.
            Higher values produce smoother tubes. Default is 20.
        capping : bool, optional
            Whether to cap the ends of the tube. Default is True.

        Returns
        -------
        PolyData
            A new mesh representing the tube.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> line = pv.Line()
        >>> tube = line.tube(radius=0.05, n_sides=20)
        >>> isinstance(tube, pv.PolyData)
        True

        Render the tube:

        >>> tube.plot()  # doctest: +SKIP

        """
        if radius <= 0:
            msg = f"radius must be positive, got {radius}"
            raise ValueError(msg)
        if n_sides < _TUBE_MIN_SIDES:
            msg = f"n_sides must be at least {_TUBE_MIN_SIDES}, got {n_sides}"
            raise ValueError(msg)

        base_scene = (
            dict(self._scene_data)
            if self._scene_data
            else {
                "type": "mesh",
                "points": self.points.flatten().tolist(),
            }
        )
        base_scene.setdefault("filters", [])
        filters_list: list[object] = base_scene["filters"]  # type: ignore[assignment]
        filters_list.append(
            {
                "type": "tube",
                "radius": radius,
                "numberOfSides": n_sides,
            },
        )

        return PolyData(
            points=self.points,
            faces=self.faces,
            _scene_data=base_scene,
        )

    def contour(
        self,
        isosurfaces: int | list[float] = 10,
        scalars: ArrayLike | None = None,
        scalar_name: str | None = None,
    ) -> PolyData:
        """Generate contour lines at constant scalar values.

        This filter extracts isolines from the mesh at specified scalar values
        using a marching triangles algorithm implemented in JavaScript.
        It mirrors the PyVista ``contour`` filter API.

        .. note::

            The contour is computed in JavaScript at render time by applying
            the marching triangles algorithm to each triangle of the mesh,
            interpolating edge crossings at the specified iso-values.
            ``VTK.wasm`` does not support ``vtkPolyData`` input for
            ``vtkContourFilter``, so this filter is implemented as a custom
            JavaScript pass.

        Parameters
        ----------
        isosurfaces : int or list of float, optional
            Number of evenly spaced contours to generate, or a list of explicit
            scalar values at which to generate contours. Default is 10.
        scalars : array-like, optional
            Scalar values per point to use for contouring. If not provided,
            uses the mesh's existing ``scalars`` attribute. Must have length
            equal to ``n_points``.
        scalar_name : str, optional
            Name for the scalar array in VTK.wasm. If not provided, uses the
            mesh's existing ``scalar_name`` attribute or defaults to "scalars".

        Returns
        -------
        PolyData
            A new mesh containing the contour lines.

        Raises
        ------
        ValueError
            If no scalars are provided and the mesh has no scalar data, or if
            isosurfaces parameter is invalid.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> sphere = pv.Sphere()
        >>> sphere_scalars = sphere.points[:, 2]
        >>> contours = sphere.contour(isosurfaces=5, scalars=sphere_scalars)
        >>> isinstance(contours, pv.PolyData)
        True

        Generate contours at specific values:

        >>> contours = sphere.contour(isosurfaces=[-0.5, 0.0, 0.5], scalars=sphere_scalars)

        Render the contours:

        >>> contours.plot()

        """
        # Determine scalar data to use
        scalar_data = self._get_contour_scalars(scalars)

        # Determine scalar name
        scalar_name_final = scalar_name or self.scalar_name

        # Generate contour values
        contour_values = self._get_contour_values(isosurfaces, scalar_data)

        base_scene = (
            dict(self._scene_data)
            if self._scene_data
            else {
                "type": "mesh",
                "points": self.points.flatten().tolist(),
            }
        )
        base_scene.setdefault("filters", [])
        filters_list: list[object] = base_scene["filters"]  # type: ignore[assignment]
        filters_list.append(
            {
                "type": "contour",
                "values": contour_values,
                "scalarName": scalar_name_final,
                "scalarData": scalar_data.flatten().tolist(),
            },
        )

        # Return new PolyData with contour filter applied
        return PolyData(
            points=self.points,
            faces=self.faces,
            scalars=scalar_data,
            scalar_name=scalar_name_final,
            _scene_data=base_scene,
        )

    def _get_contour_scalars(self, scalars: ArrayLike | None) -> np.ndarray:
        """Get scalar data for contouring, validating length."""
        if scalars is not None:
            scalar_data = np.asarray(scalars)
        elif self.scalars is not None:
            scalar_data = self.scalars
        else:
            msg = "No scalar data provided. Pass scalars parameter or set mesh.scalars"
            raise ValueError(msg)

        if len(scalar_data) != self.n_points:
            msg = f"scalars must have length {self.n_points}, got {len(scalar_data)}"
            raise ValueError(msg)

        return scalar_data

    def _get_contour_values(
        self,
        isosurfaces: int | list[float],
        scalar_data: np.ndarray,
    ) -> list[float]:
        """Generate contour values from isosurfaces parameter."""
        if isinstance(isosurfaces, int):
            if isosurfaces < 1:
                msg = f"isosurfaces must be >= 1 when int, got {isosurfaces}"
                raise ValueError(msg)
            scalar_min, scalar_max = float(scalar_data.min()), float(scalar_data.max())
            return np.linspace(scalar_min, scalar_max, isosurfaces).tolist()

        contour_values = [float(v) for v in isosurfaces]
        if len(contour_values) < 1:
            msg = "isosurfaces list must contain at least one value"
            raise ValueError(msg)
        return contour_values

    def texture_map_to_plane(self) -> PolyData:
        """Generate texture coordinates by projecting points onto the XY plane.

        Maps the mesh's X and Y extents to UV coordinates in the [0, 1] range.
        This mirrors the PyVista :meth:`pyvista.DataSet.texture_map_to_plane` API.

        Returns
        -------
        PolyData
            A new mesh with texture coordinates (``t_coords``) set.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> mesh = pv.Sphere()
        >>> mapped = mesh.texture_map_to_plane()
        >>> mapped.t_coords is not None
        True
        >>> mapped.t_coords.shape == (mesh.n_points, 2)
        True

        """
        pts = self.points.astype(float)
        x_min, x_max = float(pts[:, 0].min()), float(pts[:, 0].max())
        y_min, y_max = float(pts[:, 1].min()), float(pts[:, 1].max())
        x_range = x_max - x_min or 1.0
        y_range = y_max - y_min or 1.0

        u = (pts[:, 0] - x_min) / x_range
        v = (pts[:, 1] - y_min) / y_range
        t_coords = np.column_stack([u, v])

        return PolyData(
            points=self.points,
            faces=self.faces,
            t_coords=t_coords,
            scalars=self.scalars,
            scalar_name=self.scalar_name,
            _scene_data=self._scene_data,
        )

    def to_scene_data(self) -> dict[str, object]:
        """Return a JSON-serializable dict describing this mesh source.

        Returns
        -------
        dict
            Source configuration with ``"type"`` key and type-specific parameters.

        """
        if self._scene_data is not None:
            data: dict[str, object] = dict(self._scene_data)
        else:
            data = {
                "type": "mesh",
                "points": self.points.flatten().tolist(),
            }
            if self.faces is not None:
                data["polys"] = self.faces.tolist()

        # Inject texture coordinates
        if self.t_coords is not None:
            data["tCoords"] = self.t_coords.flatten().tolist()

        # Inject point data arrays
        if len(self._point_data) > 0:
            point_data_arrays: list[dict[str, object]] = []
            for name, array in self._point_data.items():
                n_components = 1 if array.ndim == 1 else array.shape[1]
                point_data_arrays.append(
                    {
                        "name": name,
                        "numberOfComponents": n_components,
                        "values": array.flatten().tolist(),
                    },
                )
            data["pointData"] = point_data_arrays

        return data

    def __getstate__(self) -> dict[str, object]:
        """Return state for pickling.

        Returns
        -------
        dict
            State dictionary containing points, faces, texture coordinates,
            point data, and scene data.

        """
        return {
            "points": self.points,
            "faces": self.faces,
            "t_coords": self.t_coords,
            "_point_data": self._point_data,
            "_scene_data": self._scene_data,
        }

    def __setstate__(self, state: dict[str, object]) -> None:
        """Restore state from pickle.

        Parameters
        ----------
        state : dict
            State dictionary from __getstate__.

        """
        self.points = state["points"]  # type: ignore[assignment]
        self.faces = state["faces"]  # type: ignore[assignment]
        self.t_coords = state["t_coords"]  # type: ignore[assignment]
        self._point_data = state["_point_data"]  # type: ignore[assignment]
        self._scene_data = state.get("_scene_data")  # type: ignore[assignment]


def Sphere(  # noqa: N802
    radius: float = 1.0,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    theta_resolution: int = 30,
    phi_resolution: int = 30,
) -> PolyData:
    """Create a sphere mesh.

    Parameters
    ----------
    radius : float, optional
        Sphere radius. Default is 1.0.
    center : tuple, optional
        Center of the sphere (x, y, z). Default is (0, 0, 0).
    theta_resolution : int, optional
        Number of points in the azimuthal direction. Default is 30.
    phi_resolution : int, optional
        Number of points in the polar direction. Default is 30.

    Returns
    -------
    PolyData
        A sphere mesh.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> sphere = pv.Sphere(radius=1.0)
    >>> sphere.n_points
    842

    """
    # Generate points matching VTK.wasm vtkSphereSource ordering exactly:
    #   index 0: north pole
    #   index 1: south pole
    #   then theta (outer) x phi (inner) for intermediate rows
    # phi[j] = j * pi / (phi_resolution - 1)  for j = 1 .. phi_resolution-2
    # theta[i] = i * 2*pi / theta_resolution   for i = 0 .. theta_resolution-1
    delta_phi = np.pi / (phi_resolution - 1)
    delta_theta = 2.0 * np.pi / theta_resolution

    points = []
    # North pole (index 0)
    points.append([center[0], center[1], center[2] + radius])
    # South pole (index 1)
    points.append([center[0], center[1], center[2] - radius])
    # Intermediate points: theta outer loop, phi inner loop
    for i in range(theta_resolution):
        theta = i * delta_theta
        for j in range(1, phi_resolution - 1):
            phi = j * delta_phi
            x = radius * np.sin(phi) * np.cos(theta) + center[0]
            y = radius * np.sin(phi) * np.sin(theta) + center[1]
            z = radius * np.cos(phi) + center[2]
            points.append([x, y, z])

    return PolyData(
        points=np.array(points),
        _scene_data={
            "type": "sphere",
            "center": list(center),
            "radius": radius,
            "thetaResolution": theta_resolution,
            "phiResolution": phi_resolution,
        },
    )


def Cube(  # noqa: N802
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    x_length: float = 1.0,
    y_length: float = 1.0,
    z_length: float = 1.0,
) -> PolyData:
    """Create a cube mesh.

    Parameters
    ----------
    center : tuple, optional
        Center of the cube (x, y, z). Default is (0, 0, 0).
    x_length : float, optional
        Length in x direction. Default is 1.0.
    y_length : float, optional
        Length in y direction. Default is 1.0.
    z_length : float, optional
        Length in z direction. Default is 1.0.

    Returns
    -------
    PolyData
        A cube mesh.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> cube = pv.Cube()
    >>> cube.n_points
    24

    """
    x, y, z = center
    dx, dy, dz = x_length / 2, y_length / 2, z_length / 2

    # Generate 24 points matching VTK.wasm vtkCubeSource ordering:
    # 4 points per face, 6 faces (3 axis pairs), each corner duplicated 3x with face normal.
    # Block 1 - X-facing faces (i=0: -hx face, i=1: +hx face), inner order: j(y), k(z)
    # Block 2 - Y-facing faces (i=0: -hy face, i=1: +hy face), inner order: j(x), k(z)
    # Block 3 - Z-facing faces (i=0: -hz face, i=1: +hz face), inner order: j(y), k(x)
    px = [x - dx, x + dx]
    py = [y - dy, y + dy]
    pz = [z - dz, z + dz]
    points = np.array(
        [
            # Block 1: X-facing faces
            [px[0], py[0], pz[0]],
            [px[0], py[0], pz[1]],
            [px[0], py[1], pz[0]],
            [px[0], py[1], pz[1]],
            [px[1], py[0], pz[0]],
            [px[1], py[0], pz[1]],
            [px[1], py[1], pz[0]],
            [px[1], py[1], pz[1]],
            # Block 2: Y-facing faces
            [px[0], py[0], pz[0]],
            [px[0], py[0], pz[1]],
            [px[1], py[0], pz[0]],
            [px[1], py[0], pz[1]],
            [px[0], py[1], pz[0]],
            [px[0], py[1], pz[1]],
            [px[1], py[1], pz[0]],
            [px[1], py[1], pz[1]],
            # Block 3: Z-facing faces
            [px[0], py[0], pz[0]],
            [px[1], py[0], pz[0]],
            [px[0], py[1], pz[0]],
            [px[1], py[1], pz[0]],
            [px[0], py[0], pz[1]],
            [px[1], py[0], pz[1]],
            [px[0], py[1], pz[1]],
            [px[1], py[1], pz[1]],
        ],
    )

    faces = np.array(
        [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Front
            [2, 3, 7, 6],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5],  # Right
        ],
    )

    return PolyData(
        points=points,
        faces=faces,
        _scene_data={
            "type": "cube",
            "xLength": x_length,
            "yLength": y_length,
            "zLength": z_length,
        },
    )


def Cylinder(  # noqa: N802
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),  # noqa: ARG001
    radius: float = 0.5,
    height: float = 1.0,
    resolution: int = 100,
) -> PolyData:
    """Create a cylinder mesh.

    Parameters
    ----------
    center : tuple, optional
        Center of the cylinder (x, y, z). Default is (0, 0, 0).
    direction : tuple, optional
        Direction vector of the cylinder axis. Default is (1, 0, 0).
    radius : float, optional
        Radius of the cylinder. Default is 0.5.
    height : float, optional
        Height of the cylinder. Default is 1.0.
    resolution : int, optional
        Number of points around the cylinder. Default is 100.

    Returns
    -------
    PolyData
        A cylinder mesh.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> cylinder = pv.Cylinder(radius=1.0, height=2.0)

    """
    # Generate points matching VTK.wasm vtkCylinderSource ordering (capping=true default):
    # Cylinder axis is Y. Total = 4 * resolution points:
    #   indices 0..2R-1:   side wall, interleaved pairs [y=+h/2, y=-h/2] per angle step
    #   indices 2R..3R-1:  top cap ring at y=+h/2, forward angular order
    #   indices 3R..4R-1:  bottom cap ring at y=-h/2, REVERSED angular order
    # x = radius*cos(i*angle), z = -radius*sin(i*angle) (VTK.wasm uses -sin for z)
    angle = 2.0 * np.pi / resolution
    cx, cy, cz = center
    points_list = []
    # Side wall
    for i in range(resolution):
        px = radius * np.cos(i * angle) + cx
        pz = -radius * np.sin(i * angle) + cz
        points_list.append([px, cy + height / 2, pz])  # y = +h/2
        points_list.append([px, cy - height / 2, pz])  # y = -h/2
    # Top cap (forward order, y = +h/2)
    points_list.extend(
        [radius * np.cos(i * angle) + cx, cy + height / 2, -radius * np.sin(i * angle) + cz]
        for i in range(resolution)
    )
    # Bottom cap (reversed order, y = -h/2)
    points_list.extend(
        [
            radius * np.cos((resolution - 1 - k) * angle) + cx,
            cy - height / 2,
            -radius * np.sin((resolution - 1 - k) * angle) + cz,
        ]
        for k in range(resolution)
    )
    points = np.array(points_list)

    return PolyData(
        points=points,
        _scene_data={
            "type": "cylinder",
            "height": height,
            "radius": radius,
            "resolution": resolution,
        },
    )


def Disc(  # noqa: N802, PLR0913
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    inner: float = 0.25,
    outer: float = 0.5,
    normal: tuple[float, float, float] = (0.0, 0.0, 1.0),
    r_res: int = 1,
    c_res: int = 6,
) -> PolyData:
    """Create a disc (annular ring) geometric primitive.

    This mirrors the :func:`pyvista.Disc` API.  The geometry is built
    directly from ``(r_res + 1)`` rings of ``c_res`` points each, connected
    as triangles, so it renders correctly in VTK.wasm without depending on any
    specific VTK.wasm source filter.

    Parameters
    ----------
    center : tuple, optional
        Center of the disc (x, y, z). Default is (0, 0, 0).
    inner : float, optional
        Inner radius of the disc. Default is 0.25.
    outer : float, optional
        Outer radius of the disc. Default is 0.5.
    normal : tuple, optional
        Normal vector of the disc. Default is (0, 0, 1).
    r_res : int, optional
        Number of radial subdivisions. Default is 1.
    c_res : int, optional
        Number of circumferential subdivisions. Default is 6.

    Returns
    -------
    PolyData
        A disc (annular ring) mesh.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> disc = pv.Disc(center=(0, 0, 0), inner=0.25, outer=0.5)
    >>> disc.n_points
    12

    >>> disc.plot()  # doctest: +SKIP

    """
    # Generate points matching VTK.wasm vtkDiskSource ordering:
    # outer loop circumferential (i), inner loop radial (j)
    # point index = i * (r_res + 1) + j
    theta_step = 2.0 * np.pi / c_res
    delta_r = (outer - inner) / r_res
    pts_list = []
    for i in range(c_res):
        theta = i * theta_step
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        for j in range(r_res + 1):
            r = inner + j * delta_r
            pts_list.append([r * cos_t, r * sin_t, 0.0])
    pts = np.array(pts_list)

    # Build triangular faces: two triangles per quad between adjacent rings
    faces = []
    for i in range(c_res):
        next_i = (i + 1) % c_res
        for j in range(r_res):
            p0 = i * (r_res + 1) + j
            p1 = p0 + 1
            p2 = next_i * (r_res + 1) + j + 1
            p3 = p2 - 1
            faces.append([p0, p1, p2])
            faces.append([p0, p2, p3])

    # Rotate from default normal (0,0,1) to requested normal
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    z = np.array([0.0, 0.0, 1.0])
    if not np.allclose(n, z):
        if np.allclose(n, -z):
            pts[:, 2] = -pts[:, 2]
        else:
            axis = np.cross(z, n)
            axis = axis / np.linalg.norm(axis)
            angle = np.arccos(np.clip(np.dot(z, n), -1.0, 1.0))
            c, s = np.cos(angle), np.sin(angle)
            t_val = 1.0 - c
            ax, ay, az = axis
            rot = np.array(
                [
                    [t_val * ax * ax + c, t_val * ax * ay - s * az, t_val * ax * az + s * ay],
                    [t_val * ax * ay + s * az, t_val * ay * ay + c, t_val * ay * az - s * ax],
                    [t_val * ax * az - s * ay, t_val * ay * az + s * ax, t_val * az * az + c],
                ],
            )
            pts = pts @ rot.T

    pts += np.asarray(center, dtype=float)

    return PolyData(
        points=pts,
        faces=np.array(faces) if faces else None,
        _scene_data={
            "type": "disk",
            "innerRadius": inner,
            "outerRadius": outer,
            "resolution": c_res,
        },
    )


def Circle(  # noqa: N802
    radius: float = 0.5,
    resolution: int = 100,
) -> PolyData:
    """Create a circle defined by a set of points in the XY plane.

    This mirrors the :func:`pyvista.Circle` API, producing a closed polygon
    outline of ``resolution`` points lying in the XY plane.

    Parameters
    ----------
    radius : float, optional
        Radius of the circle. Default is 0.5.
    resolution : int, optional
        Number of points on the circle. Default is 100.

    Returns
    -------
    PolyData
        A circle mesh (closed polyline in the XY plane).

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> circle = pv.Circle(radius=1.0)
    >>> circle.n_points
    101

    >>> circle.plot(color="black")  # doctest: +SKIP

    """
    if resolution < _CIRCLE_MIN_RESOLUTION:
        msg = f"resolution must be >= {_CIRCLE_MIN_RESOLUTION}, got {resolution}"
        raise ValueError(msg)

    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    points = np.column_stack([radius * np.cos(theta), radius * np.sin(theta), np.zeros(resolution)])
    # Close the loop by appending the first point
    points = np.vstack([points, points[0]])

    return PolyData(
        points=points,
        _scene_data={
            "type": "circle",
            "radius": radius,
            "resolution": resolution,
        },
    )


def Arrow(  # noqa: N802, PLR0913
    start: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),
    tip_length: float = 0.25,
    tip_radius: float = 0.1,
    tip_resolution: int = 20,  # noqa: ARG001
    shaft_radius: float = 0.05,
    shaft_resolution: int = 20,  # noqa: ARG001
    scale: float | None = None,
) -> PolyData:
    """Create an arrow mesh.

    Returns a :class:`PolyData` representing an arrow starting at ``start``
    and pointing in ``direction``, backed by VTK.wasm ``vtkArrowSource``.

    Parameters
    ----------
    start : tuple, optional
        Starting point of the arrow ``(x, y, z)``. Default is ``(0, 0, 0)``.
    direction : tuple, optional
        Direction vector of the arrow. Default is ``(1, 0, 0)``.
    tip_length : float, optional
        Length of the conical tip as a fraction of the total arrow length.
        Default is 0.25.
    tip_radius : float, optional
        Radius of the base of the tip. Default is 0.1.
    tip_resolution : int, optional
        Number of faces around the tip cone. Default is 20.
    shaft_radius : float, optional
        Radius of the cylindrical shaft. Default is 0.05.
    shaft_resolution : int, optional
        Number of faces around the shaft cylinder. Default is 20.
    scale : float, optional
        Scaling factor applied to the entire arrow. When ``None`` the arrow
        is not scaled.

    Returns
    -------
    PolyData
        An arrow mesh.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> arrow = pv.Arrow()
    >>> isinstance(arrow, pv.PolyData)
    True

    Create an arrow with a custom start point and direction:

    >>> arrow = pv.Arrow(start=(1, 0, 0), direction=(0, 1, 0))
    >>> isinstance(arrow, pv.PolyData)
    True

    Plot the arrow:

    >>> arrow.plot()  # doctest: +SKIP

    """
    direction_arr = np.asarray(direction, dtype=float)
    norm = float(np.linalg.norm(direction_arr))
    if norm == 0.0:
        msg = "direction must be a non-zero vector"
        raise ValueError(msg)
    unit_dir = direction_arr / norm

    length = 1.0 if scale is None else float(scale)

    # Build a simple representative point set: shaft start + tip end
    start_arr = np.asarray(start, dtype=float)
    end = start_arr + unit_dir * length
    points = np.array([start_arr, end])

    return PolyData(
        points=points,
        _scene_data={
            "type": "arrow",
            "tipLength": tip_length,
            "tipRadius": tip_radius,
            "shaftRadius": shaft_radius,
        },
    )


def Cone(  # noqa: N802 PLR0913
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),
    height: float = 1.0,
    radius: float = 0.5,
    resolution: int = 6,
    capping: bool = True,  # noqa: FBT001 FBT002
) -> PolyData:
    """Create a cone mesh.

    Parameters
    ----------
    center : tuple, optional
        Center of the cone (x, y, z). Default is (0, 0, 0).
    direction : tuple, optional
        Direction vector of the cone axis. Default is (1, 0, 0).
    height : float, optional
        Height of the cone. Default is 1.0.
    radius : float, optional
        Base radius of the cone. Default is 0.5.
    resolution : int, optional
        Number of facets around the cone. Default is 6.
    capping : bool, optional
        Whether to cap the base of the cone. Default is True.

    Returns
    -------
    PolyData
        A cone mesh.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> cone = pv.Cone(center=(0, 0, 0), direction=(1, 0, 0), height=1.0, radius=0.5, resolution=6)
    >>> cone.plot()  # doctest: +SKIP

    """
    # Generate approximate points for the cone
    norm = np.linalg.norm(direction)
    d = np.asarray(direction, dtype=float) / (norm if norm > 0 else 1.0)

    # Build two perpendicular vectors to d
    perp1 = np.cross(d, [1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.cross(d, [0.0, 1.0, 0.0])  # noqa: PLR2004
    perp1 /= np.linalg.norm(perp1)
    perp2 = np.cross(d, perp1)

    apex = np.asarray(center, dtype=float) + d * (height / 2.0)
    base_center = np.asarray(center, dtype=float) - d * (height / 2.0)

    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    base_points = np.array(
        [base_center + radius * (np.cos(t) * perp1 + np.sin(t) * perp2) for t in theta],
    )

    points = np.vstack([apex[np.newaxis, :], base_points])
    if capping:
        points = np.vstack([points, base_center[np.newaxis, :]])

    return PolyData(
        points=points,
        _scene_data={
            "type": "cone",
            "height": height,
            "radius": radius,
            "resolution": resolution,
        },
    )


def Line(  # noqa: N802
    pointa: tuple[float, float, float] = (0.0, 0.0, 0.0),
    pointb: tuple[float, float, float] = (1.0, 0.0, 0.0),
    resolution: int = 1,
) -> PolyData:
    """Create a line segment between two points.

    This mirrors the :func:`pyvista.Line` API, producing a polyline of
    ``resolution + 1`` evenly spaced points from ``pointa`` to ``pointb``.

    Parameters
    ----------
    pointa : tuple, optional
        Start point of the line (x, y, z). Default is (0, 0, 0).
    pointb : tuple, optional
        End point of the line (x, y, z). Default is (1, 0, 0).
    resolution : int, optional
        Number of line segments (i.e. ``resolution + 1`` points). Default is 1.

    Returns
    -------
    PolyData
        A line mesh.

    Raises
    ------
    ValueError
        If ``resolution`` is less than 1.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> line = pv.Line(pointa=(0, 0, 0), pointb=(1, 0, 0), resolution=1)
    >>> line.n_points
    2

    >>> line.plot(color="black")  # doctest: +SKIP

    """
    if resolution < 1:
        msg = f"resolution must be >= 1, got {resolution}"
        raise ValueError(msg)

    points = np.linspace(pointa, pointb, resolution + 1)

    return PolyData(
        points=points,
        _scene_data={
            "type": "line",
            "point1": list(pointa),
            "point2": list(pointb),
        },
    )


def Plane(  # noqa: N802 PLR0913
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
    i_size: float = 1.0,
    j_size: float = 1.0,
    i_resolution: int = 10,
    j_resolution: int = 10,
) -> PolyData:
    """Create a plane mesh.

    This mirrors the :func:`pyvista.Plane` API, producing a flat rectangular
    mesh oriented according to the given normal ``direction``.

    Parameters
    ----------
    center : tuple, optional
        Center of the plane (x, y, z). Default is (0, 0, 0).
    direction : tuple, optional
        Normal direction of the plane (x, y, z). Default is (0, 0, 1).
    i_size : float, optional
        Size in the i (first) direction. Default is 1.0.
    j_size : float, optional
        Size in the j (second) direction. Default is 1.0.
    i_resolution : int, optional
        Number of subdivisions in the i direction. Default is 10.
    j_resolution : int, optional
        Number of subdivisions in the j direction. Default is 10.

    Returns
    -------
    PolyData
        A plane mesh.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> plane = pv.Plane()
    >>> plane.n_points
    121

    >>> plane.plot()  # doctest: +SKIP

    """
    n = np.array(direction, dtype=float)
    n = n / np.linalg.norm(n)

    # Find two orthogonal vectors in the plane
    if not np.allclose(np.abs(n), [0.0, 1.0, 0.0]):
        ref = np.array([0.0, 1.0, 0.0])
    else:
        ref = np.array([1.0, 0.0, 0.0])
    i_hat = np.cross(ref, n)
    i_hat = i_hat / np.linalg.norm(i_hat)
    j_hat = np.cross(n, i_hat)
    j_hat = j_hat / np.linalg.norm(j_hat)

    c = np.array(center, dtype=float)
    origin = c - (i_size / 2) * i_hat - (j_size / 2) * j_hat

    # Build Python points grid for PolyData
    points = []
    for j in range(j_resolution + 1):
        for i in range(i_resolution + 1):
            p = origin + (i / i_resolution) * i_size * i_hat + (j / j_resolution) * j_size * j_hat
            points.append(p)

    # Build quad faces
    faces = []
    for j in range(j_resolution):
        for i in range(i_resolution):
            idx0 = j * (i_resolution + 1) + i
            idx1 = idx0 + 1
            idx2 = idx0 + i_resolution + 2
            idx3 = idx0 + i_resolution + 1
            faces.append([idx0, idx1, idx2, idx3])

    return PolyData(
        points=np.array(points),
        faces=np.array(faces),
        _scene_data={
            "type": "plane",
            "origin": [float(origin[0]), float(origin[1]), float(origin[2])],
            "normal": [float(n[0]), float(n[1]), float(n[2])],
        },
    )
