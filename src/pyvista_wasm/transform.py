"""Transform class for pyvista-wasm.

Mirrors the PyVista ``Transform`` API (pyvista.Transform) for composing
affine transformations. Backed by a 4x4 homogeneous matrix, compatible
with the VTK::CommonMath / VTK::CommonTransforms mapping.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

_VECTOR_COMPONENTS = 3  # Number of components in a 3D vector (x, y, z)


def _rotation_matrix(angle: float, axis: str) -> np.ndarray:
    """Return a 4x4 rotation matrix for a rotation (degrees) about an axis."""
    theta = np.deg2rad(angle)
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.eye(4)
    if axis == "x":
        matrix[1, 1], matrix[1, 2] = c, -s
        matrix[2, 1], matrix[2, 2] = s, c
    elif axis == "y":
        matrix[0, 0], matrix[0, 2] = c, s
        matrix[2, 0], matrix[2, 2] = -s, c
    elif axis == "z":
        matrix[0, 0], matrix[0, 1] = c, -s
        matrix[1, 0], matrix[1, 1] = s, c
    else:
        msg = f"Invalid axis {axis!r}; expected 'x', 'y', or 'z'"
        raise ValueError(msg)
    return matrix


class Transform:
    """Composable affine transformation (4x4 homogeneous matrix).

    Mirrors ``pyvista.Transform``. Operations are applied in the order they
    are called, matching PyVista's default ``multiply_mode='post'``.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> transform = pv.Transform().translate((1, 2, 3))
    >>> float(transform.matrix[0, 3])
    1.0

    """

    def __init__(self, matrix: ArrayLike | None = None) -> None:
        """Initialize a Transform, optionally from a 4x4 matrix."""
        if matrix is None:
            self.matrix = np.eye(4)
        else:
            self.matrix = np.asarray(matrix, dtype=float)
            if self.matrix.shape != (4, 4):
                msg = f"matrix must have shape (4, 4), got {self.matrix.shape}"
                raise ValueError(msg)

    def _compose(self, operation: np.ndarray) -> Transform:
        """Compose an operation so it applies after the current transform."""
        self.matrix = operation @ self.matrix
        return self

    def translate(self, vector: ArrayLike) -> Transform:
        """Translate by a ``(tx, ty, tz)`` vector."""
        t = np.asarray(vector, dtype=float)
        if t.shape != (3,):
            msg = f"vector must have shape (3,), got {t.shape}"
            raise ValueError(msg)
        operation = np.eye(4)
        operation[:3, 3] = t
        return self._compose(operation)

    def rotate_x(self, angle: float) -> Transform:
        """Rotate ``angle`` degrees about the x axis."""
        return self._compose(_rotation_matrix(angle, "x"))

    def rotate_y(self, angle: float) -> Transform:
        """Rotate ``angle`` degrees about the y axis."""
        return self._compose(_rotation_matrix(angle, "y"))

    def rotate_z(self, angle: float) -> Transform:
        """Rotate ``angle`` degrees about the z axis."""
        return self._compose(_rotation_matrix(angle, "z"))

    def rotate(self, vector: ArrayLike, angle: float) -> Transform:
        """Rotate ``angle`` degrees about ``vector`` (Rodrigues' formula).

        Mirrors ``pyvista.Transform.rotate(vector, angle)``. The axis
        vector does not need to be normalized.
        """
        axis = np.asarray(vector, dtype=float)
        if axis.shape != (3,):
            msg = f"vector must have shape (3,), got {axis.shape}"
            raise ValueError(msg)
        norm = np.linalg.norm(axis)
        if norm == 0:
            msg = "vector must be non-zero"
            raise ValueError(msg)
        axis = axis / norm
        theta = np.deg2rad(angle)
        c, s = np.cos(theta), np.sin(theta)
        x, y, z = axis
        cross = np.array(
            [
                [0.0, -z, y],
                [z, 0.0, -x],
                [-y, x, 0.0],
            ],
        )
        operation = np.eye(4)
        operation[:3, :3] = c * np.eye(3) + s * cross + (1 - c) * np.outer(axis, axis)
        return self._compose(operation)

    def scale(self, factors: ArrayLike) -> Transform:
        """Scale by ``(sx, sy, sz)`` factors."""
        s = np.asarray(factors, dtype=float)
        if s.shape != (3,):
            msg = f"factors must have shape (3,), got {s.shape}"
            raise ValueError(msg)
        operation = np.diag(np.concatenate((s, [1.0])))
        return self._compose(operation)

    def apply(self, vectors: ArrayLike) -> np.ndarray:
        """Apply the transform to (n, 3) vectors or points."""
        points = np.asarray(vectors, dtype=float)
        if points.ndim != 2 or points.shape[1] != _VECTOR_COMPONENTS:  # noqa: PLR2004
            msg = f"expected an (n, 3) array, got shape {points.shape}"
            raise ValueError(msg)
        homogeneous = np.hstack((points, np.ones((len(points), 1))))
        transformed = homogeneous @ self.matrix.T
        return transformed[:, :3]

    def transform_vector(self, vector: ArrayLike) -> np.ndarray:
        """Apply the linear part of the transform to a single 3D vector."""
        v = np.asarray(vector, dtype=float)
        if v.shape != (3,):
            msg = f"vector must have shape (3,), got {v.shape}"
            raise ValueError(msg)
        return self.matrix[:3, :3] @ v

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"Transform(\n{self.matrix!r}\n)"
