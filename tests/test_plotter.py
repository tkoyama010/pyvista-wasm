"""Test basic plotter functionality."""

import pathlib
import tempfile
import webbrowser

import numpy as np
import pytest

from pyvista_wasm import Camera, Cube, Cylinder, Plotter, PolyData, Sphere


def test_plotter_creation() -> None:
    """Test that a plotter can be created."""
    plotter = Plotter()
    assert plotter is not None
    assert len(plotter.actors) == 0


def test_add_mesh() -> None:
    """Test adding a mesh to the plotter."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh, color="red", opacity=0.8)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[0]["opacity"] == 0.8


def test_clear() -> None:
    """Test clearing the plotter."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_mesh(Sphere())

    assert len(plotter.actors) == 2

    plotter.clear()
    assert len(plotter.actors) == 0


def test_multiple_meshes() -> None:
    """Test adding multiple meshes."""
    plotter = Plotter()

    plotter.add_mesh(Sphere(radius=1.0), color="red")
    plotter.add_mesh(Sphere(radius=0.5, center=(2, 0, 0)), color="blue")

    assert len(plotter.actors) == 2


def test_show(monkeypatch) -> None:
    """Test show method opens browser with a file:// URL."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.show()

    assert len(opened) == 1
    assert opened[0].startswith("file://")


@pytest.mark.parametrize(
    ("mesh_factory", "expected_n_points"),
    [
        (lambda: Sphere(radius=2.0, center=(1, 2, 3), theta_resolution=50), 2 + 50 * (30 - 2)),
        (lambda: Cube(center=(0, 0, 0), x_length=3.0, y_length=2.0, z_length=1.0), 24),
        (lambda: Cylinder(radius=1.5, height=4.0, resolution=80), 4 * 80),
    ],
)
def test_plotter_mesh_with_parameters(mesh_factory, expected_n_points) -> None:
    """Test plotter correctly handles different mesh types with parameters."""
    plotter = Plotter()
    mesh = mesh_factory()

    plotter.add_mesh(mesh, color="green", opacity=0.6)

    assert len(plotter.actors) == 1
    actor = plotter.actors[0]
    assert isinstance(actor["mesh"], PolyData)
    assert actor["mesh"].n_points == expected_n_points


def test_plotter_all_mesh_types() -> None:
    """Test plotter with all mesh types in one scene."""
    plotter = Plotter()

    sphere = Sphere(radius=1.0)
    cube = Cube(center=(3, 0, 0))
    cylinder = Cylinder(center=(-3, 0, 0), radius=0.5)

    plotter.add_mesh(sphere, color="red")
    plotter.add_mesh(cube, color="green")
    plotter.add_mesh(cylinder, color="blue")

    assert len(plotter.actors) == 3
    assert all(isinstance(actor["mesh"], PolyData) for actor in plotter.actors)


def test_background_color_default() -> None:
    """Test default background color."""
    plotter = Plotter()
    assert plotter.background_color == (1.0, 1.0, 1.0)


def test_background_color_set_rgb() -> None:
    """Test setting background color with RGB tuple."""
    plotter = Plotter()
    plotter.background_color = (1.0, 1.0, 1.0)
    assert plotter.background_color == (1.0, 1.0, 1.0)
    assert plotter._renderer.background == (1.0, 1.0, 1.0)


def test_background_color_set_string() -> None:
    """Test setting background color with color name."""
    plotter = Plotter()
    plotter.background_color = "white"
    assert plotter.background_color == (1.0, 1.0, 1.0)
    assert plotter._renderer.background == (1.0, 1.0, 1.0)

    plotter.background_color = "black"
    assert plotter.background_color == (0.0, 0.0, 0.0)
    assert plotter._renderer.background == (0.0, 0.0, 0.0)

    plotter.background_color = "red"
    assert plotter.background_color == (1.0, 0.0, 0.0)
    assert plotter._renderer.background == (1.0, 0.0, 0.0)


@pytest.mark.parametrize(
    ("color_name", "expected_rgb"),
    [
        ("white", (1.0, 1.0, 1.0)),
        ("black", (0.0, 0.0, 0.0)),
        ("red", (1.0, 0.0, 0.0)),
        ("green", (0.0, 1.0, 0.0)),
        ("blue", (0.0, 0.0, 1.0)),
        ("yellow", (1.0, 1.0, 0.0)),
        ("cyan", (0.0, 1.0, 1.0)),
        ("magenta", (1.0, 0.0, 1.0)),
        ("gray", (0.5, 0.5, 0.5)),
        ("grey", (0.5, 0.5, 0.5)),
        ("orange", (1.0, 0.647, 0.0)),
        ("purple", (0.5, 0.0, 0.5)),
        ("pink", (1.0, 0.753, 0.796)),
        ("brown", (0.647, 0.165, 0.165)),
    ],
)
def test_background_color_names(color_name, expected_rgb) -> None:
    """Test all supported color names."""
    plotter = Plotter()
    plotter.background_color = color_name
    assert plotter.background_color == expected_rgb
    assert plotter._renderer.background == expected_rgb


def test_background_color_invalid_name() -> None:
    """Test setting background color with invalid color name."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="Unknown color name"):
        plotter.background_color = "invalid_color"


def test_background_color_invalid_rgb_length() -> None:
    """Test setting background color with wrong RGB tuple length."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="RGB color must have 3 values"):
        plotter.background_color = (1.0, 1.0)


def test_background_color_invalid_rgb_range() -> None:
    """Test setting background color with RGB values out of range."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="RGB values must be between 0 and 1"):
        plotter.background_color = (1.5, 0.5, 0.5)

    with pytest.raises(ValueError, match="RGB values must be between 0 and 1"):
        plotter.background_color = (-0.1, 0.5, 0.5)


def test_background_color_invalid_type() -> None:
    """Test setting background color with invalid type."""
    plotter = Plotter()
    with pytest.raises(TypeError, match="Color must be a string or RGB tuple"):
        plotter.background_color = 123


def test_background_color_updates_renderer() -> None:
    """Test that background color updates the renderer."""
    plotter = Plotter()
    plotter.background_color = "white"

    # Check that renderer was updated
    assert plotter._renderer.background == (1.0, 1.0, 1.0)


def test_multiple_plotters_have_unique_container_ids() -> None:
    """Test that each Plotter instance gets a unique container ID.

    Regression test for: second plotter.show() renders no output because
    both plotters share the same container ID, causing the second vtk.js
    renderer to attach to the first container instead of its own.
    """
    plotter1 = Plotter()
    plotter2 = Plotter()

    assert plotter1._container_id != plotter2._container_id


def test_show_twice_uses_same_container_id() -> None:
    """Test that calling show() twice on the same plotter reuses its container ID."""
    plotter = Plotter()
    container_id = plotter._container_id

    plotter.add_mesh(Sphere())
    plotter.show()
    plotter.show()

    assert plotter._container_id == container_id


def test_show_custom_container_id() -> None:
    """Test that show() respects an explicitly provided container ID."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.show(container_id="my-custom-container")

    # The instance container_id should be unchanged
    assert plotter._container_id != "my-custom-container"


def test_view_vector_sets_renderer_state() -> None:
    """Test that view_vector stores the vector in the renderer."""
    plotter = Plotter()
    plotter.view_vector((1.0, 0.0, 0.0))

    assert plotter._renderer._view_vector == (1.0, 0.0, 0.0)


def test_view_vector_default_viewup() -> None:
    """Test that default viewup is (0, 1, 0) when not specified."""
    plotter = Plotter()
    plotter.view_vector((0.0, 0.0, 1.0))

    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_vector_custom_viewup() -> None:
    """Test that a custom viewup is stored correctly."""
    plotter = Plotter()
    plotter.view_vector((1.0, 1.0, 0.0), viewup=(0.0, 0.0, 1.0))

    assert plotter._renderer._view_vector == (1.0, 1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


@pytest.mark.parametrize(
    "vector",
    [
        (1.0, 0.0, 0.0),  # +X (view from right)
        (-1.0, 0.0, 0.0),  # -X (view from left)
        (0.0, 1.0, 0.0),  # +Y (view from top)
        (0.0, 0.0, 1.0),  # +Z (view from front)
        (1.0, 1.0, 1.0),  # isometric
    ],
)
def test_view_vector_common_directions(vector) -> None:
    """Test view_vector with common viewing directions."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_vector(vector)

    assert plotter._renderer._view_vector == tuple(float(v) for v in vector)


def test_add_points_numpy_array() -> None:
    """Test adding points from a numpy array."""
    plotter = Plotter()
    points = np.random.rand(100, 3)  # noqa: NPY002

    plotter.add_points(points, color="red", point_size=10)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["type"] == "points"
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[0]["point_size"] == 10


def test_add_points_default_params() -> None:
    """Test adding points with default parameters."""
    plotter = Plotter()
    points = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])

    plotter.add_points(points)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["type"] == "points"
    assert plotter.actors[0]["opacity"] == 1.0
    assert plotter.actors[0]["point_size"] == 5.0
    assert plotter.actors[0]["render_points_as_spheres"] is False


def test_add_points_with_opacity() -> None:
    """Test adding points with custom opacity."""
    plotter = Plotter()
    points = np.random.rand(50, 3)  # noqa: NPY002

    plotter.add_points(points, color="blue", opacity=0.5, point_size=8)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == "blue"
    assert plotter.actors[0]["opacity"] == 0.5
    assert plotter.actors[0]["point_size"] == 8


def test_add_points_with_spheres() -> None:
    """Test adding points rendered as spheres."""
    plotter = Plotter()
    points = np.random.rand(30, 3)  # noqa: NPY002

    plotter.add_points(
        points,
        color="green",
        point_size=12,
        render_points_as_spheres=True,
    )

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["render_points_as_spheres"] is True
    assert plotter.actors[0]["point_size"] == 12


def test_add_points_rgb_color() -> None:
    """Test adding points with RGB color tuple."""
    plotter = Plotter()
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])

    plotter.add_points(points, color=(0.8, 0.2, 0.5))

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == (0.8, 0.2, 0.5)


def test_add_points_polydata() -> None:
    """Test adding points from a PolyData object."""
    plotter = Plotter()
    points_array = np.random.rand(20, 3)  # noqa: NPY002
    polydata = PolyData(points_array)

    plotter.add_points(polydata, color="yellow", point_size=6)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["type"] == "points"


def test_add_multiple_point_clouds() -> None:
    """Test adding multiple point clouds."""
    plotter = Plotter()

    points1 = np.random.rand(50, 3)  # noqa: NPY002
    points2 = np.random.rand(30, 3) + [2, 0, 0]  # noqa: NPY002, RUF005

    plotter.add_points(points1, color="red", point_size=5)
    plotter.add_points(points2, color="blue", point_size=8)

    assert len(plotter.actors) == 2
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[1]["color"] == "blue"


def test_add_points_and_mesh() -> None:
    """Test adding both points and meshes to the same plotter."""
    plotter = Plotter()
    mesh = Sphere()
    points = np.random.rand(40, 3)  # noqa: NPY002

    plotter.add_mesh(mesh, color="white", opacity=0.5)
    plotter.add_points(points, color="red", point_size=10)

    assert len(plotter.actors) == 2
    assert plotter.actors[0].get("type", "mesh") == "mesh"
    assert plotter.actors[1]["type"] == "points"


def test_add_points_invalid_shape() -> None:
    """Test that invalid point array shape raises an error."""
    plotter = Plotter()
    # Wrong shape - should be (n, 3)
    points = np.random.rand(10, 2)  # noqa: NPY002

    with pytest.raises(ValueError, match="Points must be an \\(n, 3\\) array"):
        plotter.add_points(points)


def test_add_points_1d_array() -> None:
    """Test that 1D array raises an error."""
    plotter = Plotter()
    points = np.random.rand(10)  # noqa: NPY002

    with pytest.raises(ValueError, match="Points must be an \\(n, 3\\) array"):
        plotter.add_points(points)


@pytest.mark.parametrize(
    ("color_name", "expected_rgb"),
    [
        ("red", (1.0, 0.0, 0.0)),
        ("green", (0.0, 1.0, 0.0)),
        ("blue", (0.0, 0.0, 1.0)),
        ("yellow", (1.0, 1.0, 0.0)),
        ("cyan", (0.0, 1.0, 1.0)),
        ("magenta", (1.0, 0.0, 1.0)),
    ],
)
def test_add_points_color_names(color_name, expected_rgb) -> None:
    """Test adding points with different color names."""
    plotter = Plotter()
    points = np.random.rand(10, 3)  # noqa: NPY002

    plotter.add_points(points, color=color_name)

    # Check that the renderer converted the color
    actor = plotter.actors[0]["actor"]
    assert actor["color"] == expected_rgb


@pytest.mark.parametrize(
    "point_size",
    [1.0, 5.0, 10.0, 20.0, 50.0],
)
def test_add_points_various_sizes(point_size) -> None:
    """Test adding points with various sizes."""
    plotter = Plotter()
    points = np.random.rand(10, 3)  # noqa: NPY002

    plotter.add_points(points, point_size=point_size)

    assert plotter.actors[0]["point_size"] == point_size


def test_view_xy() -> None:
    """Test view_xy() sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_xy()

    assert plotter._renderer._view_vector == (0.0, 0.0, 1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_xy_negative() -> None:
    """Test view_xy(negative=True) sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_xy(negative=True)

    assert plotter._renderer._view_vector == (0.0, 0.0, -1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_xz() -> None:
    """Test view_xz() sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_xz()

    assert plotter._renderer._view_vector == (0.0, 1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


def test_view_xz_negative() -> None:
    """Test view_xz(negative=True) sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_xz(negative=True)

    assert plotter._renderer._view_vector == (0.0, -1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


def test_view_yz() -> None:
    """Test view_yz() sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_yz()

    assert plotter._renderer._view_vector == (1.0, 0.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_yz_negative() -> None:
    """Test view_yz(negative=True) sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_yz(negative=True)

    assert plotter._renderer._view_vector == (-1.0, 0.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_isometric() -> None:
    """Test view_isometric() sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Cube())
    plotter.view_isometric()

    assert plotter._renderer._view_vector == (1.0, 1.0, 1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_yx() -> None:
    """Test view_yx() sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_yx()

    assert plotter._renderer._view_vector == (0.0, 0.0, -1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_yx_negative() -> None:
    """Test view_yx(negative=True) sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_yx(negative=True)

    assert plotter._renderer._view_vector == (0.0, 0.0, 1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_zx() -> None:
    """Test view_zx() sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_zx()

    assert plotter._renderer._view_vector == (0.0, -1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


def test_view_zx_negative() -> None:
    """Test view_zx(negative=True) sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_zx(negative=True)

    assert plotter._renderer._view_vector == (0.0, 1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


def test_view_zy() -> None:
    """Test view_zy() sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_zy()

    assert plotter._renderer._view_vector == (-1.0, 0.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_zy_negative() -> None:
    """Test view_zy(negative=True) sets correct camera vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_zy(negative=True)

    assert plotter._renderer._view_vector == (1.0, 0.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_add_mesh_with_show_edges() -> None:
    """Test adding a mesh with edge visibility enabled."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh, show_edges=True)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["show_edges"] is True


def test_add_mesh_with_edge_color() -> None:
    """Test adding a mesh with custom edge color."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh, show_edges=True, edge_color="red")

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["show_edges"] is True
    assert plotter.actors[0]["edge_color"] == "red"


def test_add_mesh_with_edge_color_rgb() -> None:
    """Test adding a mesh with RGB edge color."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh, show_edges=True, edge_color=(1.0, 0.0, 0.0))

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["show_edges"] is True
    assert plotter.actors[0]["edge_color"] == (1.0, 0.0, 0.0)


def test_add_mesh_with_wireframe_style() -> None:
    """Test adding a mesh with wireframe style."""
    plotter = Plotter()
    mesh = Cube()

    plotter.add_mesh(mesh, style="wireframe")

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["style"] == "wireframe"


def test_add_mesh_with_points_style() -> None:
    """Test adding a mesh with points style."""
    plotter = Plotter()
    mesh = Cube()

    plotter.add_mesh(mesh, style="points")

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["style"] == "points"


def test_add_mesh_with_surface_style() -> None:
    """Test adding a mesh with surface style (default)."""
    plotter = Plotter()
    mesh = Cube()

    plotter.add_mesh(mesh, style="surface")

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["style"] == "surface"


def test_add_mesh_surface_with_edges() -> None:
    """Test adding a mesh with surface style and edges."""
    plotter = Plotter()
    mesh = Cube()

    plotter.add_mesh(mesh, style="surface", show_edges=True, edge_color="black")

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["style"] == "surface"
    assert plotter.actors[0]["show_edges"] is True
    assert plotter.actors[0]["edge_color"] == "black"


@pytest.mark.parametrize(
    "style",
    ["surface", "wireframe", "points"],
)
def test_add_mesh_all_styles(style) -> None:
    """Test all supported rendering styles."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh, style=style)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["style"] == style


def test_add_mesh_default_style() -> None:
    """Test that default style is 'surface'."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["style"] == "surface"


def test_add_mesh_default_show_edges() -> None:
    """Test that default show_edges is False."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["show_edges"] is False


def test_add_mesh_default_edge_color() -> None:
    """Test that default edge_color is None."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["edge_color"] is None


def test_camera_position_string_xy() -> None:
    """Test camera_position property with 'xy' string."""
    plotter = Plotter()
    plotter.camera_position = "xy"

    assert plotter._renderer._view_vector == (0.0, 0.0, 1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_camera_position_string_xz() -> None:
    """Test camera_position property with 'xz' string."""
    plotter = Plotter()
    plotter.camera_position = "xz"

    assert plotter._renderer._view_vector == (0.0, 1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


def test_camera_position_string_yz() -> None:
    """Test camera_position property with 'yz' string."""
    plotter = Plotter()
    plotter.camera_position = "yz"

    assert plotter._renderer._view_vector == (1.0, 0.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_camera_position_string_yx() -> None:
    """Test camera_position property with 'yx' string."""
    plotter = Plotter()
    plotter.camera_position = "yx"

    assert plotter._renderer._view_vector == (0.0, 0.0, -1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_camera_position_string_zx() -> None:
    """Test camera_position property with 'zx' string."""
    plotter = Plotter()
    plotter.camera_position = "zx"

    assert plotter._renderer._view_vector == (0.0, -1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


def test_camera_position_string_zy() -> None:
    """Test camera_position property with 'zy' string."""
    plotter = Plotter()
    plotter.camera_position = "zy"

    assert plotter._renderer._view_vector == (-1.0, 0.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_camera_position_string_iso() -> None:
    """Test camera_position property with 'iso' string."""
    plotter = Plotter()
    plotter.camera_position = "iso"

    assert plotter._renderer._view_vector == (1.0, 1.0, 1.0)
    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_camera_position_string_invalid() -> None:
    """Test camera_position property with invalid string."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="Unknown camera position string"):
        plotter.camera_position = "invalid"


def test_camera_position_direction_vector_tuple() -> None:
    """Test camera_position property with direction vector as tuple."""
    plotter = Plotter()
    plotter.camera_position = (1.0, 0.0, 0.0)

    assert plotter._renderer._view_vector == (1.0, 0.0, 0.0)


def test_camera_position_direction_vector_list() -> None:
    """Test camera_position property with direction vector as list."""
    plotter = Plotter()
    plotter.camera_position = [0.0, 1.0, 0.0]

    assert plotter._renderer._view_vector == (0.0, 1.0, 0.0)


def test_camera_position_full_camera_spec_tuple() -> None:
    """Test camera_position property with full camera spec as tuple."""
    plotter = Plotter()
    plotter.camera_position = ((2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))

    assert plotter._camera is not None
    assert isinstance(plotter._camera, Camera)
    assert plotter._camera.position == (2.0, 5.0, 13.0)
    assert plotter._camera.focal_point == (0.0, 0.0, 0.0)
    assert plotter._camera.view_up == (0.0, 1.0, 0.0)


def test_camera_position_full_camera_spec_list() -> None:
    """Test camera_position property with full camera spec as list."""
    plotter = Plotter()
    plotter.camera_position = [[2.0, 5.0, 13.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]

    assert plotter._camera is not None
    assert isinstance(plotter._camera, Camera)
    assert plotter._camera.position == (2.0, 5.0, 13.0)
    assert plotter._camera.focal_point == (0.0, 0.0, 0.0)
    assert plotter._camera.view_up == (0.0, 1.0, 0.0)


def test_camera_position_getter() -> None:
    """Test camera_position getter returns None when no camera is set."""
    plotter = Plotter()
    assert plotter.camera_position is None


def test_camera_position_getter_with_camera() -> None:
    """Test camera_position getter returns camera spec when camera is set."""
    plotter = Plotter()
    plotter.camera_position = [(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

    cpos = plotter.camera_position
    assert cpos is not None
    assert cpos == ((2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))


def test_camera_position_invalid_format() -> None:
    """Test camera_position property with invalid format."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="Invalid camera position format"):
        plotter.camera_position = (1.0, 2.0)  # Wrong length


def test_camera_position_invalid_type() -> None:
    """Test camera_position property with invalid type."""
    plotter = Plotter()
    with pytest.raises(TypeError, match="Invalid camera position type"):
        plotter.camera_position = 123


def test_show_with_cpos_string() -> None:
    """Test show() with cpos parameter as string."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.show(cpos="xy")

    assert plotter._renderer._view_vector == (0.0, 0.0, 1.0)


def test_show_with_cpos_direction_vector() -> None:
    """Test show() with cpos parameter as direction vector."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.show(cpos=(1.0, 0.0, 0.0))

    assert plotter._renderer._view_vector == (1.0, 0.0, 0.0)


def test_show_with_cpos_full_camera_spec() -> None:
    """Test show() with cpos parameter as full camera spec."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.show(cpos=[(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)])

    assert plotter._camera is not None
    assert isinstance(plotter._camera, Camera)
    assert plotter._camera.position == (2.0, 5.0, 13.0)


def test_show_without_cpos() -> None:
    """Test show() without cpos parameter doesn't change camera."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_xy()

    # Call show without cpos
    plotter.show()

    # Camera should remain as set by view_xy()
    assert plotter._renderer._view_vector == (0.0, 0.0, 1.0)


def test_add_axes() -> None:
    """Test add_axes() method enables axes widget."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    # Initially axes should not be enabled
    assert plotter._renderer._axes_enabled is False

    # Add axes
    plotter.add_axes()

    # Axes should now be enabled
    assert plotter._renderer._axes_enabled is True


def test_add_axes_generates_code() -> None:
    """Test that add_axes() generates scene data with axes enabled."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_axes()

    # Check that axes flag is set in scene data
    scene_data = plotter._renderer._build_scene_data()
    assert scene_data["axes"] is True


def test_add_axes_without_meshes() -> None:
    """Test add_axes() can be called without any meshes."""
    plotter = Plotter()
    plotter.add_axes()

    assert plotter._renderer._axes_enabled is True


def test_multiple_axes_calls() -> None:
    """Test calling add_axes() multiple times doesn't cause issues."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    # Call add_axes multiple times
    plotter.add_axes()
    plotter.add_axes()
    plotter.add_axes()

    # Should still be enabled
    assert plotter._renderer._axes_enabled is True


def test_plotter_enable_parallel_projection() -> None:
    """Test Plotter.enable_parallel_projection() method."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    # Enable parallel projection
    plotter.enable_parallel_projection()

    # Camera should be created automatically if not set
    assert plotter.camera is not None
    assert plotter.camera.parallel_projection is True


def test_plotter_disable_parallel_projection() -> None:
    """Test Plotter.disable_parallel_projection() method."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    # Enable then disable
    plotter.enable_parallel_projection()
    plotter.disable_parallel_projection()

    assert plotter.camera is not None
    assert plotter.camera.parallel_projection is False


def test_plotter_enable_parallel_projection_with_existing_camera() -> None:
    """Test enable_parallel_projection works with an existing camera."""
    plotter = Plotter()
    camera = Camera(position=(10, 10, 10))
    plotter.camera = camera

    # Enable parallel projection
    plotter.enable_parallel_projection()

    # Should use the same camera
    assert plotter.camera is camera
    assert plotter.camera.parallel_projection is True


def test_plotter_parallel_projection_generates_code() -> None:
    """Test that plotter generates scene data for parallel projection."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.enable_parallel_projection()

    html = plotter._renderer._generate_html()
    scene = extract_scene_data(html)
    assert scene["camera"]["parallelProjection"] is True


def test_plotter_perspective_projection_generates_code() -> None:
    """Test that plotter generates scene data for perspective projection."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.enable_parallel_projection()
    plotter.disable_parallel_projection()

    # Generate HTML
    html = plotter._renderer._generate_html()
    scene = extract_scene_data(html)

    # After disabling parallel projection, it should not be set to True
    camera = scene["camera"]
    assert camera is not None
    assert camera.get("parallelProjection") is not True


def test_plotter_pickle() -> None:
    """Test that a plotter can be pickled and unpickled."""
    import pickle  # noqa: PLC0415

    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="red", opacity=0.8)
    plotter.background_color = "white"

    # Pickle the plotter
    pickled = pickle.dumps(plotter)

    # Unpickle the plotter
    loaded_plotter = pickle.loads(pickled)  # noqa: S301

    # Verify the loaded plotter
    assert len(loaded_plotter.actors) == 1
    assert loaded_plotter.actors[0]["color"] == "red"
    assert loaded_plotter.actors[0]["opacity"] == 0.8
    assert loaded_plotter.background_color == (1.0, 1.0, 1.0)


def test_plotter_pickle_multiple_meshes() -> None:
    """Test pickling a plotter with multiple meshes."""
    import pickle  # noqa: PLC0415

    plotter = Plotter()
    plotter.add_mesh(Sphere(radius=1.0), color="red")
    plotter.add_mesh(Cube(center=(2, 0, 0)), color="blue", opacity=0.5)
    plotter.background_color = "black"

    # Pickle and unpickle
    pickled = pickle.dumps(plotter)
    loaded_plotter = pickle.loads(pickled)  # noqa: S301

    # Verify the loaded plotter
    assert len(loaded_plotter.actors) == 2
    assert loaded_plotter.actors[0]["color"] == "red"
    assert loaded_plotter.actors[1]["color"] == "blue"
    assert loaded_plotter.actors[1]["opacity"] == 0.5
    assert loaded_plotter.background_color == (0.0, 0.0, 0.0)


def test_plotter_pickle_with_camera() -> None:
    """Test pickling a plotter with camera settings."""
    import pickle  # noqa: PLC0415

    plotter = Plotter()
    plotter.add_mesh(Sphere())
    camera = Camera(
        position=(2.0, 5.0, 13.0),
        focal_point=(0.0, 0.0, 0.0),
        view_up=(0.0, 1.0, 0.0),
    )
    plotter.camera = camera

    # Pickle and unpickle
    pickled = pickle.dumps(plotter)
    loaded_plotter = pickle.loads(pickled)  # noqa: S301

    # Verify camera was preserved
    assert loaded_plotter.camera is not None
    assert loaded_plotter.camera.position == (2.0, 5.0, 13.0)
    assert loaded_plotter.camera.focal_point == (0.0, 0.0, 0.0)
    assert loaded_plotter.camera.view_up == (0.0, 1.0, 0.0)


def test_mesh_pickle() -> None:
    """Test that a mesh can be pickled and unpickled."""
    import pickle  # noqa: PLC0415

    import numpy as np  # noqa: PLC0415

    mesh = Sphere()
    mesh["elevation"] = mesh.points[:, 2]

    # Pickle the mesh
    pickled = pickle.dumps(mesh)

    # Unpickle the mesh
    loaded_mesh = pickle.loads(pickled)  # noqa: S301

    # Verify the loaded mesh
    assert loaded_mesh.n_points == mesh.n_points
    assert np.array_equal(loaded_mesh.points, mesh.points)
    assert "elevation" in loaded_mesh.point_data
    assert np.array_equal(loaded_mesh["elevation"], mesh["elevation"])


def test_mesh_pickle_preserves_point_data() -> None:
    """Test that point data is preserved when pickling a mesh."""
    import pickle  # noqa: PLC0415

    import numpy as np  # noqa: PLC0415

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = PolyData(points)
    mesh["temperature"] = np.array([100.0, 200.0, 300.0])
    mesh["pressure"] = np.array([1.0, 2.0, 3.0])

    # Pickle and unpickle
    pickled = pickle.dumps(mesh)
    loaded_mesh = pickle.loads(pickled)  # noqa: S301

    # Verify point data was preserved
    assert len(loaded_mesh.point_data) == 2
    assert "temperature" in loaded_mesh.point_data
    assert "pressure" in loaded_mesh.point_data
    assert np.array_equal(loaded_mesh["temperature"], mesh["temperature"])
    assert np.array_equal(loaded_mesh["pressure"], mesh["pressure"])


def test_add_scalar_bar() -> None:
    """Test adding a scalar bar to the plotter."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_scalar_bar(title="Test", vertical=True, n_labels=5)

    assert plotter._scalar_bar is not None
    assert plotter._scalar_bar["title"] == "Test"
    assert plotter._scalar_bar["vertical"] is True
    assert plotter._scalar_bar["n_labels"] == 5


def test_add_scalar_bar_default_params() -> None:
    """Test adding a scalar bar with default parameters."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_scalar_bar()

    assert plotter._scalar_bar is not None
    assert plotter._scalar_bar["title"] == ""
    assert plotter._scalar_bar["vertical"] is True
    assert plotter._scalar_bar["n_labels"] == 5


def test_add_scalar_bar_horizontal() -> None:
    """Test adding a horizontal scalar bar."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_scalar_bar(title="Horizontal", vertical=False, n_labels=7)

    assert plotter._scalar_bar is not None
    assert plotter._scalar_bar["title"] == "Horizontal"
    assert plotter._scalar_bar["vertical"] is False
    assert plotter._scalar_bar["n_labels"] == 7


def test_scalar_bar_cleared_with_plotter() -> None:
    """Test that scalar bar is cleared when plotter is cleared."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_scalar_bar(title="Test")

    assert plotter._scalar_bar is not None

    plotter.clear()
    assert plotter._scalar_bar is None


def test_scalar_bar_updates_renderer() -> None:
    """Test that scalar bar is added to the renderer."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_scalar_bar(title="Height", vertical=True, n_labels=5)

    # Check that renderer has scalar bar
    assert plotter._renderer._scalar_bar is not None
    assert plotter._renderer._scalar_bar["title"] == "Height"


@pytest.mark.playwright
def test_screenshot_returns_array() -> None:
    """Test that screenshot returns a numpy array."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    # Get screenshot as array
    img = plotter.screenshot(return_img=True)

    assert img is not None
    assert isinstance(img, np.ndarray)
    assert img.ndim == 3
    assert img.shape[2] in (3, 4)  # RGB or RGBA


@pytest.mark.playwright
def test_screenshot_with_filename(tmp_path) -> None:
    """Test that screenshot saves to file."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    # Save screenshot to file
    filepath = tmp_path / "test_screenshot.png"
    result = plotter.screenshot(filename=str(filepath), return_img=True)

    # File should exist
    assert filepath.exists()
    # Should still return array
    assert result is not None


@pytest.mark.playwright
def test_screenshot_no_return_img(tmp_path) -> None:
    """Test screenshot with return_img=False."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    filepath = tmp_path / "test_screenshot.png"
    result = plotter.screenshot(filename=str(filepath), return_img=False)

    # Should return None when return_img=False
    assert result is None
    # But file should still be saved
    assert filepath.exists()


@pytest.mark.playwright
def test_screenshot_transparent_background() -> None:
    """Test screenshot with transparent background."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    img = plotter.screenshot(transparent_background=True, return_img=True)

    assert img is not None
    assert isinstance(img, np.ndarray)
    # Transparent background should give RGBA (4 channels)
    assert img.shape[2] == 4


@pytest.mark.playwright
def test_screenshot_window_size() -> None:
    """Test screenshot with custom window size."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    img = plotter.screenshot(window_size=(800, 600), return_img=True)

    assert img is not None
    assert isinstance(img, np.ndarray)
    assert img.shape[0] == 600  # height
    assert img.shape[1] == 800  # width


@pytest.mark.playwright
def test_screenshot_with_scale() -> None:
    """Test screenshot with scale factor."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    img = plotter.screenshot(window_size=(300, 200), scale=2, return_img=True)

    assert img is not None
    assert isinstance(img, np.ndarray)
    # Scaled dimensions: 300*2 = 600, 200*2 = 400
    assert img.shape[0] == 400  # height
    assert img.shape[1] == 600  # width


@pytest.mark.playwright
def test_screenshot_filename_only() -> None:
    """Test screenshot with only filename, no return."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        result = plotter.screenshot(filename=tmp_path, return_img=False)
        assert result is None
        assert pathlib.Path(tmp_path).exists()
    finally:
        pathlib.Path(tmp_path).unlink()


@pytest.mark.playwright
def test_screenshot_default_parameters() -> None:
    """Test screenshot with default parameters."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    # Default: return_img=True, no file, default size
    img = plotter.screenshot()

    assert img is not None
    assert isinstance(img, np.ndarray)
    # Default size should be 600x400
    assert img.shape[0] == 400  # height
    assert img.shape[1] == 600  # width
    assert img.shape[2] == 3  # RGB by default


def test_add_mesh_with_smooth_shading_default() -> None:
    """Test adding mesh with default smooth shading (True)."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["smooth_shading"] is True


def test_add_mesh_with_smooth_shading_enabled() -> None:
    """Test adding mesh with smooth shading explicitly enabled."""
    plotter = Plotter()
    plotter.add_mesh(Sphere(), smooth_shading=True)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["smooth_shading"] is True


def test_add_mesh_with_smooth_shading_disabled() -> None:
    """Test adding mesh with smooth shading explicitly disabled."""
    plotter = Plotter()
    plotter.add_mesh(Sphere(), smooth_shading=False)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["smooth_shading"] is False
