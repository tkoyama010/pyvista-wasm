"""Camera class for pyvista-wasm.

Provides a PyVista-like camera interface for controlling the viewpoint
in VTK.wasm scenes.
"""

from __future__ import annotations

import math

import numpy as np

_NORM_TOL = 1e-12


def _to_float3(arr: np.ndarray) -> tuple[float, float, float]:
    """Convert a 3-element array to a typed 3-tuple of floats."""
    return (float(arr[0]), float(arr[1]), float(arr[2]))


def _rodrigues_rotate(
    vec: np.ndarray,
    axis: np.ndarray,
    angle_deg: float,
) -> np.ndarray:
    """Rotate *vec* around *axis* by *angle_deg* degrees (Rodrigues' formula).

    Parameters
    ----------
    vec : numpy.ndarray
        Vector to rotate.
    axis : numpy.ndarray
        Unit axis of rotation.
    angle_deg : float
        Rotation angle in degrees.

    Returns
    -------
    numpy.ndarray
        Rotated vector.

    """
    angle = math.radians(angle_deg)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return vec * cos_a + np.cross(axis, vec) * sin_a + axis * np.dot(axis, vec) * (1 - cos_a)


class Camera:
    """Represents a virtual camera in a 3D scene.

    Provides a PyVista-like API for controlling camera position, orientation,
    and projection settings in VTK.wasm scenes.

    Parameters
    ----------
    position : tuple of float, optional
        Camera position as (x, y, z). Default is (0, 0, 1).
    focal_point : tuple of float, optional
        Point the camera looks at as (x, y, z). Default is (0, 0, 0).
    view_up : tuple of float, optional
        View-up vector as (x, y, z). Default is (0, 1, 0).
    view_angle : float, optional
        Camera view angle (field of view) in degrees. Default is 30.0.
    clipping_range : tuple of float, optional
        Near and far clipping plane distances as (near, far).
        Default is (0.01, 1000.01).
    parallel_projection : bool, optional
        Enable parallel (orthographic) projection instead of perspective
        projection. Default is False.
    elevation : float, optional
        Camera elevation angle in degrees. Default is 0.0.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> camera = pv.Camera()
    >>> camera.position = (5, 5, 5)
    >>> camera.focal_point = (0, 0, 0)
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(pv.Sphere())
    >>> plotter.camera = camera
    >>> plotter.show()  # doctest: +SKIP

    """

    def __init__(  # noqa: PLR0913
        self,
        position: tuple[float, float, float] = (0.0, 0.0, 1.0),
        focal_point: tuple[float, float, float] = (0.0, 0.0, 0.0),
        view_up: tuple[float, float, float] = (0.0, 1.0, 0.0),
        view_angle: float = 30.0,
        clipping_range: tuple[float, float] = (0.01, 1000.01),
        parallel_projection: bool = False,  # noqa: FBT001 FBT002
        elevation: float = 0.0,
    ) -> None:
        """Initialize a Camera instance."""
        self.position = position
        self.focal_point = focal_point
        self.view_up = view_up
        self.view_angle = view_angle
        self.clipping_range = clipping_range
        self.parallel_projection = parallel_projection
        self.elevation = elevation

    @property
    def position(self) -> tuple[float, float, float]:
        """Get or set the camera position.

        Parameters
        ----------
        value : tuple of float
            Camera position as (x, y, z).

        Returns
        -------
        tuple of float
            Camera position as (x, y, z).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.position = (5, 0, 0)
        >>> camera.position
        (5.0, 0.0, 0.0)

        """
        return self._position

    @position.setter
    def position(self, value: tuple[float, float, float]) -> None:
        """Set the camera position."""
        self._position = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def focal_point(self) -> tuple[float, float, float]:
        """Get or set the camera focal point.

        Parameters
        ----------
        value : tuple of float
            Focal point as (x, y, z).

        Returns
        -------
        tuple of float
            Focal point as (x, y, z).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.focal_point = (1, 2, 3)
        >>> camera.focal_point
        (1.0, 2.0, 3.0)

        """
        return self._focal_point

    @focal_point.setter
    def focal_point(self, value: tuple[float, float, float]) -> None:
        """Set the camera focal point."""
        self._focal_point = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def view_up(self) -> tuple[float, float, float]:
        """Get or set the view-up vector.

        Parameters
        ----------
        value : tuple of float
            View-up vector as (x, y, z).

        Returns
        -------
        tuple of float
            View-up vector as (x, y, z).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.view_up = (0, 0, 1)
        >>> camera.view_up
        (0.0, 0.0, 1.0)

        """
        return self._view_up

    @view_up.setter
    def view_up(self, value: tuple[float, float, float]) -> None:
        """Set the view-up vector."""
        self._view_up = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def view_angle(self) -> float:
        """Get or set the camera view angle in degrees.

        Parameters
        ----------
        value : float
            View angle in degrees (field of view).

        Returns
        -------
        float
            View angle in degrees.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.view_angle = 45.0
        >>> camera.view_angle
        45.0

        """
        return self._view_angle

    @view_angle.setter
    def view_angle(self, value: float) -> None:
        """Set the camera view angle."""
        self._view_angle = float(value)

    @property
    def clipping_range(self) -> tuple[float, float]:
        """Get or set the clipping range (near, far).

        Parameters
        ----------
        value : tuple of float
            Near and far clipping plane distances as (near, far).

        Returns
        -------
        tuple of float
            Clipping range as (near, far).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.clipping_range = (0.1, 100.0)
        >>> camera.clipping_range
        (0.1, 100.0)

        """
        return self._clipping_range

    @clipping_range.setter
    def clipping_range(self, value: tuple[float, float]) -> None:
        """Set the clipping range."""
        self._clipping_range = (float(value[0]), float(value[1]))

    @property
    def parallel_projection(self) -> bool:
        """Get or set parallel projection mode.

        When True, uses parallel (orthographic) projection instead of
        perspective projection. Parallel projection is useful for viewing
        2D datasets, CAD-like orthographic views, and scientific visualization
        where perspective distortion is undesirable.

        Parameters
        ----------
        value : bool
            Enable (True) or disable (False) parallel projection.

        Returns
        -------
        bool
            Whether parallel projection is enabled.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.parallel_projection = True
        >>> camera.parallel_projection
        True

        """
        return self._parallel_projection

    @parallel_projection.setter
    def parallel_projection(self, value: bool) -> None:
        """Set parallel projection mode."""
        self._parallel_projection = bool(value)

    def enable_parallel_projection(self) -> None:
        """Enable parallel (orthographic) projection.

        Switches the camera from perspective projection to parallel projection.
        This is equivalent to setting ``parallel_projection = True``.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.enable_parallel_projection()
        >>> camera.parallel_projection
        True

        """
        self.parallel_projection = True

    def disable_parallel_projection(self) -> None:
        """Disable parallel projection (use perspective projection).

        Switches the camera from parallel projection to perspective projection.
        This is equivalent to setting ``parallel_projection = False``.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.enable_parallel_projection()
        >>> camera.disable_parallel_projection()
        >>> camera.parallel_projection
        False

        """
        self.parallel_projection = False

    @property
    def elevation(self) -> float:
        """Get or set the camera elevation angle in degrees.

        The elevation angle controls the vertical rotation of the camera.
        It rotates the camera about the cross product of the negative of
        the direction of projection and the view up vector, using the
        focal point as the center of rotation.

        Parameters
        ----------
        value : float
            Elevation angle in degrees.

        Returns
        -------
        float
            Elevation angle in degrees.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera()
        >>> camera.elevation
        0.0
        >>> camera.elevation = 45.0
        >>> camera.elevation
        45.0

        """
        return self._elevation

    @elevation.setter
    def elevation(self, value: float) -> None:
        """Set the camera elevation angle."""
        self._elevation = float(value)

    def _orthonormal_frame(
        self,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None:
        """Build an orthonormal camera frame from current state.

        Returns
        -------
        tuple or None
            ``(pos, fp, forward, right, up_ortho)`` as numpy arrays, or
            ``None`` when the frame is degenerate (position == focal_point
            or forward is parallel to view-up).

        """
        pos = np.array(self._position, dtype=np.float64)
        fp = np.array(self._focal_point, dtype=np.float64)
        up = np.array(self._view_up, dtype=np.float64)

        direction = fp - pos
        dist = np.linalg.norm(direction)
        if dist < _NORM_TOL:
            return None

        forward = direction / dist

        right = np.cross(forward, up)
        right_norm = np.linalg.norm(right)
        if right_norm < _NORM_TOL:
            return None
        right = right / right_norm

        up_ortho = np.cross(right, forward)
        return pos, fp, forward, right, up_ortho

    def azimuth(self, angle: float) -> None:
        """Rotate the camera position horizontally around the focal point.

        Parameters
        ----------
        angle : float
            Rotation angle in degrees.  Positive values rotate
            counter-clockwise when viewed from above the up vector.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera(position=(0, 0, 5), focal_point=(0, 0, 0))
        >>> camera.azimuth(90)
        >>> import numpy as np
        >>> np.allclose(camera.position, (5, 0, 0), atol=1e-10)
        True

        """
        frame = self._orthonormal_frame()
        if frame is None:
            return
        pos, fp, _forward, _right, up_ortho = frame

        offset = _rodrigues_rotate(pos - fp, up_ortho, angle)
        self.position = _to_float3(fp + offset)

    def orbit_elevation(self, angle: float) -> None:
        """Rotate the camera position vertically around the focal point.

        This method is named ``orbit_elevation`` to avoid conflict with
        the :attr:`elevation` property, which stores a static angle value.

        Parameters
        ----------
        angle : float
            Rotation angle in degrees.  Positive values tilt the camera
            upward.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera(position=(0, 0, 5), focal_point=(0, 0, 0))
        >>> camera.orbit_elevation(90)
        >>> import numpy as np
        >>> np.allclose(camera.position, (0, -5, 0), atol=1e-10)
        True

        """
        frame = self._orthonormal_frame()
        if frame is None:
            return
        pos, fp, _forward, right, up_ortho = frame

        offset = _rodrigues_rotate(pos - fp, right, angle)
        new_up = _rodrigues_rotate(up_ortho, right, angle)
        self.position = _to_float3(fp + offset)
        self.view_up = _to_float3(new_up)

    def zoom(self, factor: float) -> None:
        """Move the camera closer to or farther from the focal point.

        Parameters
        ----------
        factor : float
            Zoom factor.  Values greater than 1 move the camera closer
            (zoom in); values between 0 and 1 move it farther away
            (zoom out).

        Raises
        ------
        ValueError
            If *factor* is not positive.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera(position=(0, 0, 10), focal_point=(0, 0, 0))
        >>> camera.zoom(2.0)
        >>> import numpy as np
        >>> np.allclose(camera.position, (0, 0, 5), atol=1e-10)
        True

        """
        if factor <= 0:
            msg = f"zoom factor must be positive, got {factor}"
            raise ValueError(msg)

        pos = np.array(self._position, dtype=np.float64)
        fp = np.array(self._focal_point, dtype=np.float64)
        direction = fp - pos
        dist = np.linalg.norm(direction)
        if dist < _NORM_TOL:
            return

        forward = direction / dist
        new_pos = fp - forward * (dist / factor)
        self.position = _to_float3(new_pos)

    def roll(self, angle: float) -> None:
        """Roll the camera around the view direction axis.

        Parameters
        ----------
        angle : float
            Roll angle in degrees.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> camera = pv.Camera(position=(0, 0, 5), focal_point=(0, 0, 0))
        >>> camera.roll(90)
        >>> import numpy as np
        >>> np.allclose(camera.view_up, (1, 0, 0), atol=1e-10)
        True

        """
        frame = self._orthonormal_frame()
        if frame is None:
            return
        _pos, _fp, forward, _right, up_ortho = frame

        new_up = _rodrigues_rotate(up_ortho, forward, angle)
        self.view_up = _to_float3(new_up)

    def __repr__(self) -> str:
        """Return string representation of the camera."""
        return (
            f"Camera("
            f"position={self._position}, "
            f"focal_point={self._focal_point}, "
            f"view_up={self._view_up}, "
            f"view_angle={self._view_angle}, "
            f"clipping_range={self._clipping_range}, "
            f"parallel_projection={self._parallel_projection}, "
            f"elevation={self._elevation})"
        )
