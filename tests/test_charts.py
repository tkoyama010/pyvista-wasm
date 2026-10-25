"""Tests for Chart2D (issue #777, VTK::ChartsCore parity)."""

import numpy as np
import pytest

import pyvista_wasm as pv
from pyvista_wasm.rendering import _BaseHTMLRenderer


class TestChart2DConstruction:
    """Tests for Chart2D construction."""

    def test_defaults(self) -> None:
        """Test defaults."""
        chart = pv.Chart2D()
        assert chart.width == 640
        assert chart.height == 480
        assert chart.title == ""

    def test_axes_labels(self) -> None:
        """Test axes labels."""
        chart = pv.Chart2D()
        chart.x_axis.label = "time"
        chart.y_axis.label = "value"
        assert chart.x_axis.label == "time"
        assert chart.y_axis.label == "value"


class TestChart2DSeries:
    """Tests for chart series."""

    def test_line(self) -> None:
        """Test line."""
        chart = pv.Chart2D()
        entry = chart.line([0, 1], [0, 1], color="red", label="x")
        assert entry["kind"] == "line"
        assert entry["x"] == [0, 1]
        assert entry["label"] == "x"
        assert chart._series[0]["color"] == [1.0, 0.0, 0.0]

    def test_line_default_color(self) -> None:
        """Test line default color."""
        chart = pv.Chart2D()
        chart.line([0], [0])
        chart.line([0], [0])
        assert chart._series[0]["color"] != chart._series[1]["color"]

    def test_scatter(self) -> None:
        """Test scatter."""
        chart = pv.Chart2D()
        entry = chart.scatter([0], [1], size=4)
        assert entry["kind"] == "scatter"
        assert entry["size"] == 4

    def test_bar(self) -> None:
        """Test bar."""
        chart = pv.Chart2D()
        entry = chart.bar([0, 1], [2, 3])
        assert entry["kind"] == "bar"

    def test_mismatched_lengths(self) -> None:
        """Test mismatched lengths."""
        chart = pv.Chart2D()
        with pytest.raises(ValueError, match="matching 1D"):
            chart.line([0, 1, 2], [0, 1])


class TestChart2DSceneData:
    """Tests for chart scene serialization."""

    def test_scene_data(self) -> None:
        """Test scene data."""
        chart = pv.Chart2D(width=200, height=100, title="t")
        chart.x_axis.label = "x"
        chart.y_axis.label = "y"
        chart.line([0, 1], [0, 2], color=(0.1, 0.2, 0.3))
        data = chart.to_scene_data()
        assert data["type"] == "chart"
        assert data["width"] == 200
        assert data["height"] == 100
        assert data["title"] == "t"
        assert data["xLabel"] == "x"
        assert data["yLabel"] == "y"
        series = data["series"]
        assert series[0]["kind"] == "line"  # type: ignore[index]
        assert series[0]["color"] == [0.1, 0.2, 0.3]  # type: ignore[index]


class TestAddChart:
    """Tests for Plotter.add_chart."""

    def test_add_chart(self) -> None:
        """Test add chart."""
        plotter = pv.Plotter()
        chart = pv.Chart2D()
        _ = chart.line([0, 1], [1, 0])
        plotter.add_chart(chart)
        assert plotter._renderer.charts == [chart]

    def test_scene_data_contains_chart(self) -> None:
        """Test scene data contains chart."""
        renderer = _BaseHTMLRenderer()
        chart = pv.Chart2D(title="c")
        _ = chart.line(np.arange(3), np.arange(3) * 2.0)
        renderer.add_chart_actor(chart)
        scene = renderer._build_scene_data()
        charts = scene["charts"]
        assert charts[0]["title"] == "c"  # type: ignore[index]
        assert charts[0]["series"][0]["y"] == [0, 2, 4]  # type: ignore[index]


class TestExport:
    """Tests for exports."""

    def test_exported(self) -> None:
        """Test exported."""
        assert hasattr(pv, "Chart2D")
