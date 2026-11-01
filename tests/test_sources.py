"""Tests for new source factories (issue #780)."""

import pytest

import pyvista_wasm as pv


class TestPolygon:
    """Tests for Polygon."""

    def test_hexagon(self) -> None:
        """Test a hexagon has six points and one face."""
        poly = pv.Polygon(n_sides=6, radius=2.0)
        assert poly.n_points == 6
        assert len(poly.faces) == 7

    def test_invalid_sides_raises(self) -> None:
        """Test fewer than 3 sides raises ValueError."""
        with pytest.raises(ValueError, match="n_sides"):
            pv.Polygon(n_sides=2)


class TestTriangle:
    """Tests for Triangle."""

    def test_three_points(self) -> None:
        """Test a triangle has three points."""
        assert pv.Triangle().n_points == 3


class TestTetrahedron:
    """Tests for Tetrahedron."""

    def test_four_faces(self) -> None:
        """Test a tetrahedron has four points and four faces."""
        tet = pv.Tetrahedron(radius=2.0, center=(1, 2, 3))
        assert tet.n_points == 4
        assert len(tet.faces) == 16  # 4 triangles
        assert tet.points[:, 0].max() > 1  # offset by center
