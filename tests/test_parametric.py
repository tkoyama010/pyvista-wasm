"""Tests for parametric surface factories (issue #781)."""

import numpy as np

import pyvista_wasm as pv


class TestParametricKlein:
    """Tests for ParametricKlein."""

    def test_resolution(self) -> None:
        """Test the default resolution is respected."""
        klein = pv.ParametricKlein()
        assert klein.n_points == 1600

    def test_center_offset(self) -> None:
        """Test the center offset is applied."""
        klein = pv.ParametricKlein(center=(1, 2, 3))
        assert klein.points[:, 0].min() < 1 < klein.points[:, 0].max()
        assert klein.points[:, 1].min() < 2 < klein.points[:, 1].max()
        assert klein.points[:, 2].min() < 3 < klein.points[:, 2].max()


class TestParametricTorus:
    """Tests for ParametricTorus."""

    def test_resolution(self) -> None:
        """Test the default resolution is respected."""
        torus = pv.ParametricTorus()
        assert torus.n_points == 1600

    def test_major_radius(self) -> None:
        """Test all points lie on the torus surface."""
        radius = 2.0
        torus = pv.ParametricTorus(radius=radius)
        r_xy = np.hypot(torus.points[:, 0], torus.points[:, 1])
        dist_from_ring = np.abs(np.hypot(r_xy - radius, torus.points[:, 2]))
        np.testing.assert_allclose(dist_from_ring, radius / 2, atol=1e-9)
