"""Tests for TextProperty.background_color (issue #786)."""

import pyvista_wasm as pv


class TestTextBackgroundColor:
    """Tests for the text background (2D context actor)."""

    def test_default_none(self) -> None:
        """Test no background is drawn by default."""
        prop = pv.TextProperty()
        assert prop.background_color is None

    def test_rgb_tuple(self) -> None:
        """Test an RGB tuple background."""
        prop = pv.TextProperty(background_color=(0.1, 0.2, 0.3))
        assert prop.background_color == (0.1, 0.2, 0.3)

    def test_named_color(self) -> None:
        """Test a named background color is converted to RGB."""
        prop = pv.TextProperty(background_color="white")
        assert prop.background_color == (1.0, 1.0, 1.0)

    def test_scene_data_carries_background(self) -> None:
        """Test the scene data includes the background color."""
        plotter = pv.Plotter()
        text = pv.Text("hello")
        text.prop = pv.TextProperty(background_color="black")
        plotter.add_text(text)
        scene = plotter._renderer._build_scene_data()
        assert scene["textActors"][0]["backgroundColor"] == [0.0, 0.0, 0.0]
