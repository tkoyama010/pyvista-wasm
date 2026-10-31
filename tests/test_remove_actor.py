"""Tests for Plotter.remove_actor (issue #787)."""

import numpy as np

import pyvista_wasm as pv

rng = np.random.default_rng()


class TestRemoveActor:
    """Tests for remove_actor."""

    def test_removes_mesh_actor(self) -> None:
        """Test removing a mesh actor leaves the others intact."""
        plotter = pv.Plotter()
        first = plotter.add_mesh(pv.Sphere())
        _ = plotter.add_mesh(pv.Cube())
        assert len(plotter.actors) == 2
        plotter.remove_actor(first)
        assert len(plotter.actors) == 1
        assert len(plotter._renderer.actors) == 1

    def test_removes_points_actor(self) -> None:
        """Test removing a point actor rebuilds remaining mesh actors."""
        plotter = pv.Plotter()
        _ = plotter.add_mesh(pv.Sphere())
        points = plotter.add_points(rng.random((10, 3)))
        assert len(plotter.actors) == 2
        plotter.remove_actor(points)
        assert len(plotter.actors) == 1
        assert len(plotter._renderer.actors) == 1

    def test_unknown_actor_is_ignored(self) -> None:
        """Test removing an actor that is not in the plotter is a no-op."""
        plotter = pv.Plotter()
        _ = plotter.add_mesh(pv.Sphere())
        assert len(plotter.actors) == 1
        plotter.remove_actor({"actor": object()})
        assert len(plotter.actors) == 1

    def test_keeps_lights(self) -> None:
        """Test removing an actor does not clear configured lights."""
        plotter = pv.Plotter()
        _ = plotter.add_mesh(pv.Sphere())
        plotter.add_light(pv.Light(position=(1, 1, 1), intensity=2.0))
        actor = plotter.add_mesh(pv.Cube())
        assert len(plotter.actors) == 2
        plotter.remove_actor(actor)
        assert len(plotter.actors) == 1
        assert len(plotter._renderer.lights) == 1

    def test_empty_plotter_is_noop(self) -> None:
        """Test removing from a plotter with no actors is a no-op."""
        plotter = pv.Plotter()
        assert len(plotter.actors) == 0
        plotter.remove_actor({"actor": object()})
        assert len(plotter.actors) == 0
