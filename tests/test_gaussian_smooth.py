"""Tests for ImageData.gaussian_smooth (issue #793)."""

import numpy as np
import pytest

import pyvista_wasm as pv


class TestGaussianSmooth:
    """Tests for gaussian_smooth."""

    def test_reduces_variance(self) -> None:
        """Test smoothing reduces the variance of random data."""
        rng = np.random.default_rng()
        grid = pv.ImageData(dimensions=(10, 10, 10))
        grid.point_data["values"] = rng.random(grid.n_points)
        smoothed = grid.gaussian_smooth(std_dev=1.0)
        before = float(grid.point_data["values"].std())
        after = float(smoothed.point_data["values"].std())
        assert after < before

    def test_preserves_dimensions(self) -> None:
        """Test output has the same geometry."""
        grid = pv.ImageData(dimensions=(5, 6, 7), spacing=(2, 2, 2))
        grid.point_data["values"] = np.arange(grid.n_points, dtype=float)
        smoothed = grid.gaussian_smooth()
        assert smoothed.dimensions == grid.dimensions
        assert smoothed.spacing == grid.spacing
        assert smoothed.n_points == grid.n_points

    def test_named_scalars(self) -> None:
        """Test smoothing a named array."""
        grid = pv.ImageData(dimensions=(6, 6, 6))
        grid.point_data["a"] = np.ones(grid.n_points)
        grid.point_data["b"] = np.zeros(grid.n_points)
        smoothed = grid.gaussian_smooth(scalars="b")
        np.testing.assert_allclose(
            smoothed.point_data["a"],
            grid.point_data["a"],
        )

    def test_no_data_raises(self) -> None:
        """Test smoothing without point data raises ValueError."""
        with pytest.raises(ValueError, match="point data"):
            pv.ImageData(dimensions=(4, 4, 4)).gaussian_smooth()
