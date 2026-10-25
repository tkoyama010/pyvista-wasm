"""Tests for the dataset family added for issue #774 (VTK::CommonDataModel parity)."""

import numpy as np
import pytest

import pyvista_wasm as pv


class TestCellData:
    """Tests for CellData."""

    def test_set_and_get(self) -> None:
        """Test set_and_get."""
        mesh = pv.Sphere()
        mesh.cell_data["area"] = np.arange(mesh.n_faces)
        assert "area" in mesh.cell_data
        np.testing.assert_array_equal(mesh.cell_data["area"], np.arange(mesh.n_faces))

    def test_independent_from_point_data(self) -> None:
        """Test independent_from_point_data."""
        mesh = pv.Sphere()
        mesh.point_data["a"] = [1]
        mesh.cell_data["b"] = [2]
        assert list(mesh.point_data.keys()) == ["a"]
        assert list(mesh.cell_data.keys()) == ["b"]


class TestFieldData:
    """Tests for FieldData."""

    def test_set_and_get(self) -> None:
        """Test set_and_get."""
        mesh = pv.Sphere()
        mesh.field_data["meta"] = [42]
        assert mesh.field_data["meta"] == [42]


class TestPolyDataGeometryProperties:
    """Tests for PolyData bounds/center."""

    def test_bounds(self) -> None:
        """Test bounds."""
        points = np.array([[0.0, 0, 0], [1.0, 2, 3]])
        mesh = pv.PolyData(points)
        assert mesh.bounds == (0.0, 1.0, 0.0, 2.0, 0.0, 3.0)

    def test_center(self) -> None:
        """Test center."""
        points = np.array([[0.0, 0, 0], [1.0, 2, 3]])
        mesh = pv.PolyData(points)
        assert mesh.center == (0.5, 1.0, 1.5)

    def test_bounds_empty(self) -> None:
        """Test bounds_empty."""
        mesh = pv.PolyData(np.zeros((0, 3)))
        assert all(np.isnan(b) for b in mesh.bounds)

    def test_n_cells(self) -> None:
        """Test n_cells."""
        mesh = pv.Sphere()
        assert mesh.n_cells == mesh.n_faces


class TestPointSet:
    """Tests for PointSet."""

    def test_creation(self) -> None:
        """Test creation."""
        rng = np.random.default_rng()
        points = rng.random((10, 3))
        ps = pv.PointSet(points)
        assert ps.n_points == 10
        assert ps.n_cells == 10

    def test_scene_data(self) -> None:
        """Test scene_data."""
        ps = pv.PointSet(np.array([[0.0, 0, 0], [1, 1, 1]]))
        data = ps.to_scene_data()
        assert data["type"] == "points"
        assert data["points"] == [0.0, 0, 0, 1, 1, 1]

    def test_scene_data_with_scalars(self) -> None:
        """Test scene_data_with_scalars."""
        ps = pv.PointSet(np.array([[0.0, 0, 0], [1, 1, 1]]))
        ps["temp"] = [10.0, 20.0]
        data = ps.to_scene_data()
        assert data["pointData"][0]["name"] == "temp"
        assert data["pointData"][0]["values"] == [10.0, 20.0]


class TestImageData:
    """Tests for ImageData."""

    def test_default_counts(self) -> None:
        """Test default_counts."""
        grid = pv.ImageData()
        assert grid.n_points == 1000
        assert grid.n_cells == 729

    def test_counts(self) -> None:
        """Test counts."""
        grid = pv.ImageData(dimensions=(2, 3, 4))
        assert grid.n_points == 24
        assert grid.n_cells == 6

    def test_points(self) -> None:
        """Test points."""
        grid = pv.ImageData(dimensions=(2, 2, 2), spacing=(1, 2, 3), origin=(5, 5, 5))
        expected = np.array(
            [
                [5, 5, 5],
                [6, 5, 5],
                [5, 7, 5],
                [6, 7, 5],
                [5, 5, 8],
                [6, 5, 8],
                [5, 7, 8],
                [6, 7, 8],
            ],
            dtype=float,
        )
        np.testing.assert_array_equal(grid.points, expected)

    def test_bounds(self) -> None:
        """Test bounds."""
        grid = pv.ImageData(dimensions=(3, 3, 3), spacing=(0.5, 1, 2), origin=(1, 2, 3))
        assert grid.bounds == (1.0, 2.0, 2.0, 4.0, 3.0, 7.0)

    def test_center(self) -> None:
        """Test center."""
        grid = pv.ImageData(dimensions=(2, 3, 4), spacing=(1, 1, 1))
        assert grid.center == (0.5, 1.0, 1.5)


class TestRectilinearGrid:
    """Tests for RectilinearGrid."""

    def test_counts(self) -> None:
        """Test counts."""
        grid = pv.RectilinearGrid(np.arange(3), np.arange(4), np.arange(5))
        assert grid.n_points == 60
        assert grid.n_cells == 24

    def test_dimensions(self) -> None:
        """Test dimensions."""
        grid = pv.RectilinearGrid(np.arange(3), np.arange(4), np.arange(5))
        assert grid.dimensions == (3, 4, 5)

    def test_points_ordering(self) -> None:
        """Test points_ordering."""
        grid = pv.RectilinearGrid([0, 1], [0, 1], [0, 1])
        # x varies fastest
        assert grid.points[0, 0] == 0
        assert grid.points[1, 0] == 1
        assert grid.points.shape == (8, 3)

    def test_bounds(self) -> None:
        """Test bounds."""
        grid = pv.RectilinearGrid([0, 1, 5], [0, 2], [0, 3])
        assert grid.bounds == (0.0, 5.0, 0.0, 2.0, 0.0, 3.0)


class TestStructuredGrid:
    """Tests for StructuredGrid."""

    def test_default_dimensions(self) -> None:
        """Test default_dimensions."""
        rng = np.random.default_rng()
        points = rng.random((12, 3))
        grid = pv.StructuredGrid(points)
        assert grid.dimensions == (12, 1, 1)

    def test_explicit_dimensions(self) -> None:
        """Test explicit_dimensions."""
        rng = np.random.default_rng()
        points = rng.random((24, 3))
        grid = pv.StructuredGrid(points, dimensions=(4, 3, 2))
        assert grid.dimensions == (4, 3, 2)
        assert grid.n_points == 24
        assert grid.n_cells == 6


class TestUnstructuredGrid:
    """Tests for UnstructuredGrid."""

    def test_single_triangle(self) -> None:
        """Test single_triangle."""
        points = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
        grid = pv.UnstructuredGrid(points, [3, 0, 1, 2])
        assert grid.n_points == 3
        assert grid.n_cells == 1

    def test_multiple_cells(self) -> None:
        """Test multiple_cells."""
        points = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])
        cells = [3, 0, 1, 2, 3, 1, 3, 2]
        grid = pv.UnstructuredGrid(points, cells)
        assert grid.n_cells == 2

    def test_explicit_celltypes(self) -> None:
        """Test explicit_celltypes."""
        points = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
        grid = pv.UnstructuredGrid(points, [3, 0, 1, 2], celltypes=[5])
        assert grid.n_cells == 1

    def test_bounds(self) -> None:
        """Test bounds."""
        points = np.array([[0.0, 0, 0], [1, 2, 3]])
        grid = pv.UnstructuredGrid(points, [2, 0, 1])
        assert grid.bounds == (0.0, 1.0, 0.0, 2.0, 0.0, 3.0)


class TestMultiBlock:
    """Tests for MultiBlock."""

    def test_dict_init(self) -> None:
        """Test dict_init."""
        block = pv.MultiBlock({"sphere": pv.Sphere(), "cube": pv.Cube()})
        assert block.n_blocks == 2
        assert block.keys() == ["sphere", "cube"]

    def test_list_init(self) -> None:
        """Test list_init."""
        block = pv.MultiBlock([pv.Sphere(), pv.Cube()])
        assert block.n_blocks == 2
        assert isinstance(block[0], pv.PolyData)

    def test_setitem_getitem(self) -> None:
        """Test setitem_getitem."""
        block = pv.MultiBlock()
        block["a"] = pv.Sphere()
        block[1] = pv.Cube()
        assert block["a"] is block[0]
        assert block[1] is block["1"]

    def test_combined_bounds(self) -> None:
        """Test combined_bounds."""
        block = pv.MultiBlock(
            {
                "a": pv.PolyData(np.array([[0.0, 0, 0], [1, 1, 1]])),
                "b": pv.PolyData(np.array([[5.0, 5, 5], [6, 6, 6]])),
            },
        )
        assert block.bounds == (0.0, 6.0, 0.0, 6.0, 0.0, 6.0)
        assert block.center == (3.0, 3.0, 3.0)

    def test_empty_bounds(self) -> None:
        """Test empty_bounds."""
        block = pv.MultiBlock()
        assert all(np.isnan(b) for b in block.bounds)


class TestDataSetAttributes:
    """Tests for data attribute containers."""

    def test_len_and_items(self) -> None:
        """Test len_and_items."""
        mesh = pv.Sphere()
        mesh.point_data["a"] = [1]
        mesh.point_data["b"] = [2]
        assert len(mesh.point_data) == 2
        assert dict(mesh.point_data.items()) == {"a": [1], "b": [2]}

    def test_values(self) -> None:
        """Test values."""
        mesh = pv.Sphere()
        mesh.point_data["a"] = [1]
        assert list(mesh.point_data.values()) == [[1]]


class TestExports:
    """Tests for public exports."""

    @pytest.mark.parametrize(
        "name",
        [
            "CellData",
            "FieldData",
            "PointSet",
            "ImageData",
            "RectilinearGrid",
            "StructuredGrid",
            "UnstructuredGrid",
            "MultiBlock",
        ],
    )
    def test_exported(self, name: str) -> None:
        """Test exported."""
        assert hasattr(pv, name)
