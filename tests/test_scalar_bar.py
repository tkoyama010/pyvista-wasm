"""Tests for the scalar bar scene data (issue #785)."""

import pyvista_wasm as pv


class TestScalarBarData:
    """Tests for scalar bar scene data."""

    def _plotter_with_scalars(self) -> pv.Plotter:
        """Build a plotter with a scalar-colored mesh and a scalar bar."""
        plotter = pv.Plotter()
        mesh = pv.Sphere()
        mesh.point_data["height"] = mesh.points[:, 2]
        plotter.add_mesh(mesh, scalars="height", cmap="viridis")
        plotter.add_scalar_bar(title="Height", vertical=False, n_labels=7)
        return plotter

    def test_config_in_scene(self) -> None:
        """Test title/orientation/labels reach the scene data."""
        scene = self._plotter_with_scalars()._renderer._build_scene_data()
        bar = scene["scalarBar"]
        assert bar["title"] == "Height"
        assert bar["vertical"] is False
        assert bar["n_labels"] == 7

    def test_gradient_included(self) -> None:
        """Test the gradient stops and range are included."""
        scene = self._plotter_with_scalars()._renderer._build_scene_data()
        bar = scene["scalarBar"]
        assert len(bar["gradient"]) == 32
        assert bar["range"] == [-1.0, 1.0]

    def test_none_without_scalar_bar(self) -> None:
        """Test the scene has no scalar bar unless requested."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere())
        scene = plotter._renderer._build_scene_data()
        assert scene["scalarBar"] is None
