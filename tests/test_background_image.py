"""Tests for add_background_image (issue #789)."""

import pyvista_wasm as pv


class TestAddBackgroundImage:
    """Tests for add_background_image."""

    def test_url_reaches_scene(self) -> None:
        """Test the image URL reaches the scene data."""
        plotter = pv.Plotter()
        plotter.add_background_image("sky.png")
        scene = plotter._renderer._build_scene_data()
        assert scene["backgroundImage"] == "sky.png"

    def test_default_none(self) -> None:
        """Test no background image by default."""
        scene = pv.Plotter()._renderer._build_scene_data()
        assert scene["backgroundImage"] is None
