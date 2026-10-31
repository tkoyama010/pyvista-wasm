"""Tests for Chart2D.area (issue #795)."""

import pyvista_wasm as pv


class TestChartArea:
    """Tests for the area series type."""

    def test_series_entry(self) -> None:
        """Test the area series entry shape."""
        chart = pv.Chart2D(width=400, height=300)
        entry = chart.area([1, 2, 3], [1, 4, 2], color="blue", label="a")
        assert entry["kind"] == "area"
        assert entry["opacity"] == 0.35
        assert len(chart._series) == 1

    def test_scene_data(self) -> None:
        """Test the area series reaches the scene data."""
        chart = pv.Chart2D(width=400, height=300)
        chart.area([1, 2, 3], [3, 1, 2])
        scene = chart.to_scene_data()
        assert scene["series"][0]["kind"] == "area"
