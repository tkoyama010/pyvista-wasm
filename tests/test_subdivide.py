"""Tests for PolyData.subdivide (issue #779)."""

import numpy as np
import pytest

import pyvista_wasm as pv


class TestSubdivide:
    """Tests for subdivide."""

    def test_triangle_becomes_four(self) -> None:
        """Test a single triangle splits into four."""
        tri = pv.PolyData(
            np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            faces=np.array([3, 0, 1, 2]),
        )
        sub = tri.subdivide(nsub=1)
        assert sub.n_points == 6
        assert len(sub.faces) == 16  # 4 triangles

    def test_subdivide_twice(self) -> None:
        """Test two levels of subdivision."""
        tri = pv.PolyData(
            np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            faces=np.array([3, 0, 1, 2]),
        )
        sub = tri.subdivide(nsub=2)
        assert sub.n_points == 15  # 3 + 3 + 9

    def test_quad_becomes_four_quads(self) -> None:
        """Test a quad splits into four quads."""
        quad = pv.PolyData(
            np.array([[0.0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]),
            faces=np.array([4, 0, 1, 2, 3]),
        )
        sub = quad.subdivide(nsub=1)
        assert sub.n_points == 9  # 4 corners + 4 edge midpoints + center
        assert len(sub.faces) == 20  # 4 quads

    def test_invalid_nsub_raises(self) -> None:
        """Test nsub below 1 raises ValueError."""
        with pytest.raises(ValueError, match="nsub"):
            pv.Sphere().subdivide(nsub=0)

    def test_unknown_filter_raises(self) -> None:
        """Test an unsupported subfilter raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="linear"):
            pv.Sphere().subdivide(subfilter="butterfly")
