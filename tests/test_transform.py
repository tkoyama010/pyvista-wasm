"""Tests for Transform (issue #775, VTK::CommonMath parity)."""

import numpy as np
from numpy.testing import assert_allclose

import pyvista_wasm as pv
from pyvista_wasm import Plotter
from pyvista_wasm.rendering import _BaseHTMLRenderer


class TestTranslate:
    """Tests for translate."""

    def test_matrix(self) -> None:
        """Test matrix."""
        transform = pv.Transform().translate((1, 2, 3))
        assert_allclose(transform.matrix[:3, 3], [1, 2, 3])

    def test_apply(self) -> None:
        """Test apply."""
        transform = pv.Transform().translate((1, 2, 3))
        result = transform.apply([[0, 0, 0]])
        assert_allclose(result, [[1, 2, 3]])

    def test_invalid_shape(self) -> None:
        """Test invalid shape."""
        try:
            pv.Transform().translate((1, 2))
        except ValueError:
            pass
        else:
            msg = "expected ValueError"
            raise AssertionError(msg)


class TestRotate:
    """Tests for rotation methods."""

    def test_rotate_z_90(self) -> None:
        """Test rotate z 90."""
        transform = pv.Transform().rotate_z(90)
        result = transform.apply([[1, 0, 0]])
        assert_allclose(result[0], [0, 1, 0], atol=1e-12)

    def test_rotate_x_90(self) -> None:
        """Test rotate x 90."""
        transform = pv.Transform().rotate_x(90)
        result = transform.apply([[0, 1, 0]])
        assert_allclose(result[0], [0, 0, 1], atol=1e-12)

    def test_rotate_y_90(self) -> None:
        """Test rotate y 90."""
        transform = pv.Transform().rotate_y(90)
        result = transform.apply([[0, 0, 1]])
        assert_allclose(result[0], [1, 0, 0], atol=1e-12)


class TestScale:
    """Tests for scale."""

    def test_scale(self) -> None:
        """Test scale."""
        transform = pv.Transform().scale((2, 3, 4))
        result = transform.apply([[1, 1, 1]])
        assert_allclose(result[0], [2, 3, 4])


class TestComposition:
    """Tests for operation composition order."""

    def test_post_multiply_order(self) -> None:
        """Test post multiply order."""
        # translate then rotate: rotation applies after translation
        transform = pv.Transform().translate((1, 0, 0)).rotate_z(90)
        result = transform.apply([[0, 0, 0]])
        # translation happens first: point (1,0,0), then rotated to (0,1,0)
        assert_allclose(result[0], [0, 1, 0], atol=1e-12)

    def test_from_matrix(self) -> None:
        """Test from matrix."""
        matrix = np.diag([2.0, 2, 2, 1])
        transform = pv.Transform(matrix)
        assert_allclose(transform.matrix, matrix)

    def test_from_invalid_matrix(self) -> None:
        """Test from invalid matrix."""
        try:
            pv.Transform(np.eye(3))
        except ValueError:
            pass
        else:
            msg = "expected ValueError"
            raise AssertionError(msg)


class TestMeshTransform:
    """Tests for PolyData.transform."""

    def test_translate_mesh(self) -> None:
        """Test translate mesh."""
        mesh = pv.Sphere()
        original_center = mesh.center
        moved = mesh.transform(pv.Transform().translate((1, 2, 3)))
        assert moved.n_points == mesh.n_points
        assert moved.n_faces == mesh.n_faces
        expected_center = tuple(c + d for c, d in zip(original_center, (1, 2, 3), strict=False))
        assert all(abs(a - b) < 1e-12 for a, b in zip(moved.center, expected_center, strict=False))

    def test_inplace(self) -> None:
        """Test inplace."""
        mesh = pv.Sphere()
        result = mesh.transform(pv.Transform().translate((1, 0, 0)), inplace=True)
        assert result is mesh
        assert mesh.center[0] != 0

    def test_accepts_matrix(self) -> None:
        """Test accepts matrix."""
        mesh = pv.Sphere()
        moved = mesh.transform(np.diag([2.0, 2, 2, 1]))
        assert moved.n_points == mesh.n_points


class TestActorTransform:
    """Tests for add_mesh(transform=...) (issue #776)."""

    def test_actor_stores_transform(self) -> None:
        """Test actor stores transform."""
        plotter = Plotter()
        plotter.add_mesh(pv.Sphere(), transform=pv.Transform().translate((1, 2, 3)))
        renderer_actor = plotter._renderer.actors[0]
        assert isinstance(renderer_actor["transform"], pv.Transform)

    def test_accepts_matrix(self) -> None:
        """Test accepts matrix."""
        plotter = Plotter()
        plotter.add_mesh(pv.Sphere(), transform=np.eye(4))
        renderer_actor = plotter._renderer.actors[0]
        assert isinstance(renderer_actor["transform"], pv.Transform)

    def test_build_actor_data_bakes_transform(self) -> None:
        """Test build actor data bakes transform."""
        renderer = _BaseHTMLRenderer()
        mesh = pv.PolyData(np.array([[0.0, 0, 0], [1, 1, 1]]))
        transform = pv.Transform().translate((10, 0, 0))
        actor_info = renderer.add_mesh_actor(mesh, transform=transform)
        data = renderer._build_actor_data(actor_info)
        assert data["source"]["points"][0] == 10.0
