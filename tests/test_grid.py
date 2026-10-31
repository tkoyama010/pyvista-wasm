"""Tests for add_bounding_box and show_grid (issue #788)."""

import numpy as np
import pytest

import pyvista_wasm as pv


class TestAddBoundingBox:
    """Tests for add_bounding_box."""

    def test_outline_lines(self) -> None:
        """Test the outline is a lines-only mesh around the bounds."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(radius=0.5))
        actor = plotter.add_bounding_box()
        assert actor
        outline = plotter.actors[-1]["mesh"]
        assert outline.lines is not None
        assert len(outline.lines) == 36  # 12 edges x (2 + 2 ids)
        corners = outline.points
        assert corners.shape == (8, 3)
        assert np.isclose(np.abs(corners).max(), 0.5, atol=1e-6)

    def test_requires_actor(self) -> None:
        """Test an empty plotter raises ValueError."""
        with pytest.raises(ValueError, match="actor"):
            pv.Plotter().add_bounding_box()


class TestShowGrid:
    """Tests for show_grid."""

    def test_grid_in_scene(self) -> None:
        """Test the grid config reaches the scene data."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere())
        plotter.show_grid(color="gray")
        scene = plotter._renderer._build_scene_data()
        grid = scene["grid"]
        assert grid["color"] == "gray"
        assert len(grid["bounds"]) == 6
        assert grid["bounds"][1] >= grid["bounds"][0]

    def test_requires_actor(self) -> None:
        """Test an empty plotter raises ValueError."""
        with pytest.raises(ValueError, match="actor"):
            pv.Plotter().show_grid()
