"""Test Texture class and texture mapping functionality."""

import webbrowser

import numpy as np
import pytest

import pyvista_wasm as pv
from pyvista_wasm import PolyData, Sphere, Texture, examples


def test_texture_creation() -> None:
    """Test that Texture stores the URL."""
    tex = examples.download_masonry_texture()
    assert tex.url == "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/masonry.bmp"


def test_texture_repr() -> None:
    """Test Texture __repr__."""
    tex = examples.download_masonry_texture()
    assert "masonry.bmp" in repr(tex)


def test_texture_map_to_plane_returns_polydata() -> None:
    """Test that texture_map_to_plane returns a PolyData."""
    sphere = Sphere()
    mapped = sphere.texture_map_to_plane()
    assert isinstance(mapped, PolyData)


def test_texture_map_to_plane_sets_t_coords() -> None:
    """Test that texture_map_to_plane sets t_coords."""
    sphere = Sphere()
    mapped = sphere.texture_map_to_plane()
    assert mapped.t_coords is not None
    assert mapped.t_coords.shape == (sphere.n_points, 2)


def test_texture_map_to_plane_uv_range() -> None:
    """Test that UV coordinates are in [0, 1] range."""
    sphere = Sphere()
    mapped = sphere.texture_map_to_plane()
    assert mapped.t_coords is not None
    assert float(mapped.t_coords[:, 0].min()) >= 0.0
    assert float(mapped.t_coords[:, 0].max()) <= 1.0
    assert float(mapped.t_coords[:, 1].min()) >= 0.0
    assert float(mapped.t_coords[:, 1].max()) <= 1.0


def test_texture_map_to_plane_preserves_points() -> None:
    """Test that texture_map_to_plane preserves points and faces."""
    sphere = Sphere()
    mapped = sphere.texture_map_to_plane()
    assert np.array_equal(mapped.points, sphere.points)


def test_texture_map_to_plane_generic_polydata() -> None:
    """Test texture_map_to_plane on custom PolyData."""
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
    )
    faces = np.array([[0, 1, 2, 3]])
    mesh = PolyData(points, faces)
    mapped = mesh.texture_map_to_plane()
    assert mapped.t_coords is not None
    assert mapped.t_coords.shape == (4, 2)
    # Corner at (0,0) should map to U=0, V=0
    assert np.isclose(mapped.t_coords[0, 0], 0.0)
    assert np.isclose(mapped.t_coords[0, 1], 0.0)
    # Corner at (1,1) should map to U=1, V=1
    assert np.isclose(mapped.t_coords[2, 0], 1.0)
    assert np.isclose(mapped.t_coords[2, 1], 1.0)


def test_scene_data_injects_tcoords() -> None:
    """Test that t_coords are injected into scene data."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    mesh = PolyData(points)
    mapped = mesh.texture_map_to_plane()
    scene = mapped.to_scene_data()
    assert "tCoords" in scene
    assert len(scene["tCoords"]) == 3 * 2  # 3 points x 2 UV components


def test_scene_data_no_tcoords_by_default() -> None:
    """Test that t_coords are NOT included in scene data when not set."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    mesh = PolyData(points)
    scene = mesh.to_scene_data()
    assert "tCoords" not in scene


def test_add_mesh_with_texture(monkeypatch) -> None:
    """Test that add_mesh accepts texture parameter."""
    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", opened.append)

    plotter = pv.Plotter()
    sphere = pv.Sphere()
    texture = examples.download_masonry_texture()
    actor = plotter.add_mesh(sphere, texture=texture)
    assert actor["texture"] is texture


def test_generated_html_contains_texture_code(monkeypatch) -> None:
    """Test that HTML output contains texture data when texture is set."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(webbrowser, "open", lambda _: None)

    plotter = pv.Plotter()
    sphere = pv.Sphere()
    texture = examples.download_masonry_texture()
    plotter.add_mesh(sphere, texture=texture)

    html = plotter._renderer._generate_html()
    assert "masonry.bmp" in html
    scene = extract_scene_data(html)
    assert scene["actors"][0]["texture"] is not None
    assert "masonry.bmp" in scene["actors"][0]["texture"]["url"]


def test_generated_html_no_texture_code_without_texture(monkeypatch) -> None:
    """Test that scene data has no texture when no texture is set."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(webbrowser, "open", lambda _: None)

    plotter = pv.Plotter()
    sphere = pv.Sphere()
    plotter.add_mesh(sphere)

    html = plotter._renderer._generate_html()
    scene = extract_scene_data(html)
    assert scene["actors"][0]["texture"] is None


def test_texture_with_primitive_sphere(monkeypatch) -> None:
    """Test texture applied to a Sphere (primitive with auto UV coords)."""
    monkeypatch.setattr(webbrowser, "open", lambda _: None)

    plotter = pv.Plotter()
    sphere = pv.Sphere()
    texture = Texture("https://example.com/earth.jpg")
    plotter.add_mesh(sphere, texture=texture)
    plotter.show()


def test_texture_with_custom_polydata_and_tcoords(monkeypatch) -> None:
    """Test texture on custom PolyData with explicit texture coordinates."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(webbrowser, "open", lambda _: None)

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
    )
    faces = np.array([[0, 1, 2, 3]])
    mesh = PolyData(points, faces)
    mapped = mesh.texture_map_to_plane()

    plotter = pv.Plotter()
    texture = examples.download_masonry_texture()
    plotter.add_mesh(mapped, texture=texture)

    html = plotter._renderer._generate_html()
    scene = extract_scene_data(html)
    assert scene["actors"][0]["texture"] is not None
    assert scene["actors"][0]["source"]["tCoords"] is not None


def test_polydata_t_coords_none_by_default() -> None:
    """Test that PolyData has t_coords=None by default."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    mesh = PolyData(points)
    assert mesh.t_coords is None


@pytest.mark.parametrize("primitive_factory", [pv.Sphere, pv.Cube, pv.Cylinder])
def test_primitives_t_coords_none_by_default(primitive_factory) -> None:
    """Test that primitive meshes have t_coords=None by default."""
    mesh = primitive_factory()
    assert mesh.t_coords is None


def test_texture_in_public_api() -> None:
    """Test that Texture is accessible from the top-level pyvista_wasm module."""
    assert hasattr(pv, "Texture")
    assert pv.Texture is Texture
