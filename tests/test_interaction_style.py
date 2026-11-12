"""Tests for interaction style selection (issue #782)."""

import pytest

import pyvista_wasm as pv


class TestEnableStyle:
    """Tests for the enable_*_style family."""

    def test_trackball_default(self) -> None:
        """Test the default style is trackball."""
        renderer = pv.Plotter()._renderer
        assert renderer._interaction_style == "trackball"

    @pytest.mark.parametrize(
        "method",
        [
            "enable_trackball_style",
            "enable_trackball_actor_style",
            "enable_joystick_style",
            "enable_joystick_actor_style",
            "enable_2d_style",
            "enable_zoom_style",
        ],
    )
    def test_enable_methods_set_style(self, method: str) -> None:
        """Test each enable method selects its style."""
        plotter = pv.Plotter()
        getattr(plotter, method)()
        expected = method.removeprefix("enable_").removesuffix("_style")
        assert plotter._renderer._interaction_style == expected.replace("2d", "2d")

    def test_unknown_style_raises(self) -> None:
        """Test an unknown style raises ValueError."""
        with pytest.raises(ValueError, match="style"):
            pv.Plotter()._renderer.set_interaction_style("nope")

    def test_scene_data_carries_style(self) -> None:
        """Test the scene data includes the interaction style."""
        plotter = pv.Plotter()
        plotter.enable_2d_style()
        scene = plotter._renderer._build_scene_data()
        assert scene["interactionStyle"] == "2d"
