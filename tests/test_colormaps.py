"""Tests for the colormap utilities (issue #794)."""

import numpy as np
import pytest

from pyvista_wasm.colormaps import available_colormaps, map_to_rgb


class TestMapToRgb:
    """Tests for map_to_rgb."""

    def test_extremes_match_stops(self) -> None:
        """Test 0 maps to the first and 1 to the last stop."""
        stops = np.array(
            [(0, 0, 0), (255, 255, 255)],
            dtype=float,
        )
        rgb = map_to_rgb(
            np.array([0.0, 1.0]),
            cmap="viridis",
        )
        assert rgb.shape == (2, 3)
        # viridis endpoints: dark purple and yellow
        assert rgb[0].tolist() == [68, 1, 84]
        assert rgb[1].tolist() == [253, 231, 37]
        del stops

    def test_clim(self) -> None:
        """Test a custom normalization range."""
        rgb = map_to_rgb(np.array([5.0]), cmap="viridis", clim=(0.0, 10.0))
        expected = map_to_rgb(np.array([0.5]), cmap="viridis", clim=(0.0, 1.0))
        np.testing.assert_allclose(rgb, expected)

    def test_unknown_cmap_raises(self) -> None:
        """Test an unknown colormap raises ValueError."""
        with pytest.raises(ValueError, match="cmap"):
            map_to_rgb(np.array([1.0]), cmap="not-a-cmap")


class TestAvailableColormaps:
    """Tests for available_colormaps."""

    def test_contains_defaults(self) -> None:
        """Test the documented colormaps are available."""
        names = available_colormaps()
        for name in ("viridis", "plasma", "inferno", "magma", "jet"):
            assert name in names
