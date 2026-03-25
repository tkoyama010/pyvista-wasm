"""Test scalar array support in PolyData and rendering."""

import webbrowser

import numpy as np
import pytest

from pyvista_wasm import Plotter, PolyData, Sphere


def test_point_data_creation() -> None:
    """Test that PointData container is created."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    assert hasattr(mesh, "point_data")
    assert len(mesh.point_data) == 0


def test_point_data_setitem() -> None:
    """Test adding scalar arrays via point_data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    scalars = np.array([1.0, 2.0, 3.0])
    mesh.point_data["test"] = scalars

    assert "test" in mesh.point_data
    assert len(mesh.point_data) == 1
    assert np.array_equal(mesh.point_data["test"], scalars)


def test_point_data_getitem() -> None:
    """Test retrieving scalar arrays via point_data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    scalars = np.array([1.0, 2.0, 3.0])
    mesh.point_data["test"] = scalars

    retrieved = mesh.point_data["test"]
    assert np.array_equal(retrieved, scalars)


def test_mesh_dict_style_access() -> None:
    """Test dictionary-style access on mesh directly."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    scalars = np.array([1.0, 2.0, 3.0])

    mesh["elevation"] = scalars
    assert np.array_equal(mesh["elevation"], scalars)


def test_sphere_with_elevation() -> None:
    """Test adding elevation scalars to a sphere."""
    sphere = Sphere(radius=1.0)
    sphere["elevation"] = sphere.points[:, 2]

    assert "elevation" in sphere.point_data
    assert len(sphere["elevation"]) == sphere.n_points


def test_point_data_keys() -> None:
    """Test retrieving array names from point_data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    mesh.point_data["a"] = np.array([1.0, 2.0, 3.0])
    mesh.point_data["b"] = np.array([4.0, 5.0, 6.0])

    keys = mesh.point_data.keys()
    assert "a" in keys
    assert "b" in keys
    assert len(keys) == 2


def test_point_data_items() -> None:
    """Test retrieving (name, array) pairs from point_data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    mesh.point_data["test"] = np.array([1.0, 2.0, 3.0])

    items = mesh.point_data.items()
    assert len(items) == 1
    assert items[0][0] == "test"
    assert np.array_equal(items[0][1], np.array([1.0, 2.0, 3.0]))


def test_point_data_values() -> None:
    """Test retrieving all arrays from point_data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    mesh.point_data["test"] = np.array([1.0, 2.0, 3.0])

    values = mesh.point_data.values()
    assert len(values) == 1
    assert np.array_equal(values[0], np.array([1.0, 2.0, 3.0]))


def test_scene_data_with_scalars() -> None:
    """Test that scalar arrays are included in scene data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    mesh["elevation"] = np.array([0.0, 0.5, 1.0])

    scene = mesh.to_scene_data()

    assert "pointData" in scene
    assert len(scene["pointData"]) == 1
    assert scene["pointData"][0]["name"] == "elevation"


def test_scene_data_with_multiple_scalars() -> None:
    """Test that multiple scalar arrays are included in scene data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    mesh["elevation"] = np.array([0.0, 0.5, 1.0])
    mesh["temperature"] = np.array([100.0, 200.0, 300.0])

    scene = mesh.to_scene_data()

    assert "pointData" in scene
    assert len(scene["pointData"]) == 2
    names = [arr["name"] for arr in scene["pointData"]]
    assert "elevation" in names
    assert "temperature" in names


def test_plotter_add_mesh_with_scalars(monkeypatch) -> None:
    """Test adding a mesh with scalar coloring to plotter."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    plotter = Plotter()
    mesh = Sphere()
    mesh["elevation"] = mesh.points[:, 2]

    plotter.add_mesh(mesh, scalars="elevation", cmap="viridis")

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["scalars"] == "elevation"
    assert plotter.actors[0]["cmap"] == "viridis"


def test_plotter_add_mesh_scalars_default_cmap(monkeypatch) -> None:
    """Test that default colormap is viridis."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    plotter = Plotter()
    mesh = Sphere()
    mesh["elevation"] = mesh.points[:, 2]

    plotter.add_mesh(mesh, scalars="elevation")

    assert plotter.actors[0]["cmap"] == "viridis"


@pytest.mark.parametrize(
    "cmap",
    [
        "viridis",
        "plasma",
        "jet",
        "coolwarm",
    ],
)
def test_plotter_add_mesh_different_colormaps(monkeypatch, cmap: str) -> None:
    """Test adding mesh with different colormaps."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    plotter = Plotter()
    mesh = Sphere()
    mesh["elevation"] = mesh.points[:, 2]

    plotter.add_mesh(mesh, scalars="elevation", cmap=cmap)

    assert plotter.actors[0]["cmap"] == cmap


def test_plotter_show_with_scalars(monkeypatch) -> None:
    """Test that show() works with scalar coloring."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    plotter = Plotter()
    mesh = Sphere()
    mesh["elevation"] = mesh.points[:, 2]

    plotter.add_mesh(mesh, scalars="elevation", cmap="viridis")
    plotter.show()

    assert len(opened) == 1
    assert opened[0].startswith("file://")


def test_scalar_array_2d() -> None:
    """Test that 2D scalar arrays are supported."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    # 2D array with 2 components per point
    mesh["vectors"] = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

    scene = mesh.to_scene_data()

    assert "pointData" in scene
    vec_array = scene["pointData"][0]
    assert vec_array["name"] == "vectors"
    assert vec_array["numberOfComponents"] == 2


def test_scalar_array_3d_still_serializes() -> None:
    """Test that 3D arrays are flattened and serialized in scene data."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    mesh["data3d"] = np.array([[[1.0]], [[2.0]], [[3.0]]])

    scene = mesh.to_scene_data()
    assert "pointData" in scene
    assert scene["pointData"][0]["name"] == "data3d"


def test_point_data_convert_list_to_array() -> None:
    """Test that lists are converted to numpy arrays."""
    mesh = PolyData(points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    mesh.point_data["test"] = [1.0, 2.0, 3.0]

    assert isinstance(mesh.point_data["test"], np.ndarray)
    assert np.array_equal(mesh.point_data["test"], np.array([1.0, 2.0, 3.0]))
