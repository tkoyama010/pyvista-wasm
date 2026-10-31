"""Tests for Plotter.add_volume (issue #743)."""

import numpy as np
import pytest

import pyvista_wasm as pv


def _volume(dims: int = 16) -> pv.ImageData:
    """Build a small test volume with a Gaussian scalar field."""
    grid = pv.ImageData(dimensions=(dims, dims, dims))
    x, y, z = np.meshgrid(*(np.linspace(-1, 1, dims),) * 3, indexing="ij")
    grid.point_data["values"] = np.exp(-(x**2 + y**2 + z**2) * 4).ravel(order="F")
    return grid


class TestAddVolume:
    """Tests for add_volume."""

    def test_returns_actor_and_adds_scalar_bar(self) -> None:
        """Test the actor is stored and the scalar bar configured."""
        plotter = pv.Plotter()
        actor = plotter.add_volume(_volume(), scalars="values")
        assert actor
        assert len(plotter.actors) == 1
        assert plotter._scalar_bar is not None

    def test_no_scalar_bar(self) -> None:
        """Test show_scalar_bar=False skips the scalar bar."""
        plotter = pv.Plotter()
        plotter.add_volume(_volume(), show_scalar_bar=False)
        assert plotter._scalar_bar is None

    def test_opacity_presets(self) -> None:
        """Test each opacity preset is accepted."""
        for preset in ("linear", "sigmoid", "geom"):
            plotter = pv.Plotter()
            plotter.add_volume(_volume(), opacity=preset, show_scalar_bar=False)

    def test_constant_opacity(self) -> None:
        """Test a numeric opacity is accepted."""
        plotter = pv.Plotter()
        plotter.add_volume(_volume(), opacity=0.5, show_scalar_bar=False)

    def test_unknown_preset_raises(self) -> None:
        """Test an unknown opacity preset raises ValueError."""
        with pytest.raises(ValueError, match="opacity preset"):
            pv.Plotter().add_volume(_volume(), opacity="nope")

    def test_bad_clim_raises(self) -> None:
        """Test a non-increasing clim raises ValueError."""
        with pytest.raises(ValueError, match="clim"):
            pv.Plotter().add_volume(_volume(), clim=(1.0, 0.0))

    def test_empty_volume_raises(self) -> None:
        """Test a volume without point data raises ValueError."""
        with pytest.raises(ValueError, match="point data"):
            pv.Plotter().add_volume(pv.ImageData(dimensions=(4, 4, 4)))

    def test_decimation(self) -> None:
        """Test the point count respects max_points."""
        plotter = pv.Plotter()
        plotter.add_volume(_volume(64), max_points=1000, show_scalar_bar=False)
        actor_info = plotter.actors[0]
        mesh = actor_info["mesh"]
        assert mesh.n_points <= 1000
