"""Tests for add_point_labels (issue #790)."""

import numpy as np
import pytest

import pyvista_wasm as pv


class TestAddPointLabels:
    """Tests for add_point_labels."""

    def test_labels_in_scene(self) -> None:
        """Test labels reach the scene data."""
        plotter = pv.Plotter()
        plotter.add_point_labels(
            np.array([[0.0, 0, 1], [1, 0, 0]]),
            ["north", "east"],
        )
        scene = plotter._renderer._build_scene_data()
        labels = scene["pointLabels"]
        assert labels[0]["text"] == "north"
        assert labels[1]["position"] == [1.0, 0.0, 0.0]

    def test_shape_mismatch_raises(self) -> None:
        """Test label/point count mismatch raises ValueError."""
        with pytest.raises(ValueError, match="labels"):
            pv.Plotter().add_point_labels(np.zeros((2, 3)), ["one"])

    def test_bad_shape_raises(self) -> None:
        """Test non-(n, 3) points raise ValueError."""
        with pytest.raises(ValueError, match=r"\(n, 3\)"):
            pv.Plotter().add_point_labels(np.zeros((2, 2)), ["a", "b"])
