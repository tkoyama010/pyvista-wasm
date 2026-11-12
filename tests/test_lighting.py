"""Tests for add_mesh material coefficients (issue #791)."""

import pyvista_wasm as pv


class TestAddMeshLighting:
    """Tests for ambient/diffuse/specular pass-through."""

    def test_defaults(self) -> None:
        """Test the default coefficients match VTK defaults."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere())
        info = plotter.actors[0]
        assert info["ambient"] == 0.0
        assert info["diffuse"] == 1.0
        assert info["specular"] == 0.0

    def test_custom_coefficients(self) -> None:
        """Test custom coefficients reach the actor info."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), ambient=0.2, diffuse=0.8, specular=0.5)
        info = plotter.actors[0]
        assert info["ambient"] == 0.2
        assert info["diffuse"] == 0.8
        assert info["specular"] == 0.5

    def test_scene_data_carries_lighting(self) -> None:
        """Test the scene data includes the lighting block."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), specular=0.3, specular_power=20)
        data = plotter._renderer._build_actor_data(plotter.actors[0])
        assert data["lighting"]["specular"] == 0.3
        assert data["lighting"]["specularPower"] == 20
