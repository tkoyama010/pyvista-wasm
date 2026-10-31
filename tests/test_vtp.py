"""Tests for .vtp XML read/save (issue #784)."""

import numpy as np
import pytest

import pyvista_wasm as pv


class TestSaveVtp:
    """Tests for PolyData.save on .vtp files."""

    def test_roundtrip(self, tmp_path) -> None:
        """Test save + read returns the same geometry."""
        points = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])
        faces = np.array([3, 0, 1, 2, 3, 0, 2, 3])
        mesh = pv.PolyData(points=points, faces=faces)
        path = tmp_path / "mesh.vtp"
        mesh.save(path)

        reader = pv.XMLPolyDataReader(path)
        loaded = reader.read()
        np.testing.assert_allclose(loaded.points, points)
        np.testing.assert_allclose(loaded.faces, faces)

    def test_two_dimensional_faces(self, tmp_path) -> None:
        """Test saving meshes built with 2D face arrays."""
        points = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
        mesh = pv.PolyData(points=points, faces=np.array([[0, 1, 2]]))
        path = tmp_path / "mesh.vtp"
        mesh.save(path)
        loaded = pv.XMLPolyDataReader(path).read()
        np.testing.assert_allclose(loaded.points, points)
        assert loaded.faces is not None

    def test_point_cloud(self, tmp_path) -> None:
        """Test saving a mesh without faces."""
        points = np.array([[0.0, 0, 0], [1, 1, 1]])
        mesh = pv.PolyData(points=points)
        path = tmp_path / "cloud.vtp"
        mesh.save(path)
        loaded = pv.XMLPolyDataReader(path).read()
        np.testing.assert_allclose(loaded.points, points)
        assert loaded.faces is None

    def test_wrong_extension_raises(self, tmp_path) -> None:
        """Test the reader rejects non-.vtp files."""
        path = tmp_path / "mesh.vtk"
        path.write_text("junk")
        with pytest.raises(ValueError, match="\\.vtp"):
            pv.XMLPolyDataReader(path)

    def test_missing_file_raises(self, tmp_path) -> None:
        """Test the reader rejects missing files."""
        with pytest.raises(FileNotFoundError):
            pv.XMLPolyDataReader(tmp_path / "nope.vtp")
