"""Test readers module."""

from pathlib import Path

import numpy as np
import pytest

from pyvista_wasm import GLTFReader, OBJReader, PLYReader, PolyDataReader, STLReader, examples

DATA_DIR = Path(__file__).parent / "data"
TRIANGLE_VTK = DATA_DIR / "triangle.vtk"
TRIANGLE_PLY = DATA_DIR / "triangle.ply"
TRIANGLE_OBJ = DATA_DIR / "triangle.obj"
TRIANGLE_STL = DATA_DIR / "triangle.stl"
TRIANGLE_GLTF = DATA_DIR / "triangle.gltf"


# --- PolyDataReader tests ---


def test_poly_data_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = PolyDataReader(TRIANGLE_VTK)
    assert reader.path == TRIANGLE_VTK


def test_poly_data_reader_read_points() -> None:
    """Test reading points from a VTK file."""
    reader = PolyDataReader(TRIANGLE_VTK)
    mesh = reader.read()

    assert mesh.n_points == 3
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_poly_data_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = PolyDataReader(str(TRIANGLE_VTK))
    mesh = reader.read()
    assert mesh.n_points == 3


def test_poly_data_reader_scene_data() -> None:
    """Test that reader mesh returns valid scene data."""
    mesh = PolyDataReader(TRIANGLE_VTK).read()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "vtkReader"
    assert "data" in scene


@pytest.mark.parametrize(
    ("filename", "content", "error_type", "match"),
    [
        (
            "bad.vtk",
            "INVALID HEADER\nfoo\nASCII\nDATASET POLYDATA\n",
            ValueError,
            "missing version header",
        ),
        (
            "binary.vtk",
            "# vtk DataFile Version 3.0\ntitle\nBINARY\nDATASET POLYDATA\n",
            ValueError,
            "Only ASCII",
        ),
        ("short.vtk", "# vtk DataFile Version 3.0\ntitle\n", ValueError, "too few lines"),
    ],
)
def test_poly_data_reader_invalid_files(
    tmp_path: Path,
    filename: str,
    content: str,
    error_type: type,
    match: str,
) -> None:
    """Test ValueError for various invalid VTK files."""
    bad_file = tmp_path / filename
    bad_file.write_text(content)
    with pytest.raises(error_type, match=match):
        PolyDataReader(bad_file).read()


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .vtk file"),
    ],
)
def test_poly_data_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            PolyDataReader("nonexistent.vtk")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            PolyDataReader(bad_file)


def test_poly_data_reader_no_points(tmp_path: Path) -> None:
    """Test reading a VTK file with no POINTS section yields empty mesh."""
    vtk_file = tmp_path / "empty.vtk"
    vtk_file.write_text(
        "# vtk DataFile Version 3.0\ntitle\nASCII\nDATASET POLYDATA\n",
    )
    mesh = PolyDataReader(vtk_file).read()
    assert mesh.n_points == 0


# --- PLYReader tests ---


def test_ply_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = PLYReader(TRIANGLE_PLY)
    assert reader.path == TRIANGLE_PLY


def test_ply_reader_read_points() -> None:
    """Test reading points from a PLY file."""
    reader = PLYReader(TRIANGLE_PLY)
    mesh = reader.read()

    assert mesh.n_points == 3
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_ply_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = PLYReader(str(TRIANGLE_PLY))
    mesh = reader.read()
    assert mesh.n_points == 3


def test_ply_reader_scene_data() -> None:
    """Test that PLY reader mesh returns valid scene data."""
    mesh = PLYReader(TRIANGLE_PLY).read()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "mesh"
    assert "points" in scene
    assert "polys" in scene


@pytest.mark.parametrize(
    ("filename", "content", "error_type", "match"),
    [
        (
            "bad.ply",
            "NOT A PLY FILE\nformat ascii 1.0\nend_header\n",
            ValueError,
            "missing 'ply' magic number",
        ),
        (
            "no_header_end.ply",
            "ply\nformat ascii 1.0\nelement vertex 0\n",
            ValueError,
            "missing 'end_header'",
        ),
        (
            "no_format.ply",
            "ply\nelement vertex 0\nend_header\n",
            ValueError,
            "missing 'format' declaration",
        ),
    ],
)
def test_ply_reader_invalid_files(
    tmp_path: Path,
    filename: str,
    content: str,
    error_type: type,
    match: str,
) -> None:
    """Test ValueError for various invalid PLY files."""
    bad_file = tmp_path / filename
    bad_file.write_text(content)
    with pytest.raises(error_type, match=match):
        PLYReader(bad_file).read()


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .ply file"),
    ],
)
def test_ply_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            PLYReader("nonexistent.ply")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            PLYReader(bad_file)


def test_ply_reader_no_vertices(tmp_path: Path) -> None:
    """Test reading a PLY file with no vertices yields empty mesh."""
    ply_file = tmp_path / "empty.ply"
    ply_file.write_text(
        "ply\nformat ascii 1.0\nelement vertex 0\nend_header\n",
    )
    mesh = PLYReader(ply_file).read()
    assert mesh.n_points == 0


# --- OBJReader tests ---


def test_obj_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = OBJReader(TRIANGLE_OBJ)
    assert reader.path == TRIANGLE_OBJ


def test_obj_reader_read_points() -> None:
    """Test reading points from an OBJ file."""
    reader = OBJReader(TRIANGLE_OBJ)
    mesh = reader.read()

    assert mesh.n_points == 3
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_obj_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = OBJReader(str(TRIANGLE_OBJ))
    mesh = reader.read()
    assert mesh.n_points == 3


def test_obj_reader_scene_data() -> None:
    """Test that OBJ reader mesh returns valid scene data."""
    mesh = OBJReader(TRIANGLE_OBJ).read()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "objReader"
    assert "data" in scene


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .obj file"),
    ],
)
def test_obj_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            OBJReader("nonexistent.obj")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            OBJReader(bad_file)


def test_obj_reader_no_vertices(tmp_path: Path) -> None:
    """Test reading an OBJ file with no vertices yields empty mesh."""
    obj_file = tmp_path / "empty.obj"
    obj_file.write_text("# empty obj file\n")
    mesh = OBJReader(obj_file).read()
    assert mesh.n_points == 0


# --- STLReader tests ---


def test_stl_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = STLReader(TRIANGLE_STL)
    assert reader.path == TRIANGLE_STL


def test_stl_reader_read_points() -> None:
    """Test reading points from an STL file."""
    reader = STLReader(TRIANGLE_STL)
    mesh = reader.read()

    assert mesh.n_points == 3
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_stl_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = STLReader(str(TRIANGLE_STL))
    mesh = reader.read()
    assert mesh.n_points == 3


# --- GLTFReader tests ---


def test_gltf_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = GLTFReader(TRIANGLE_GLTF)
    assert reader.path == TRIANGLE_GLTF


def test_gltf_reader_read_points() -> None:
    """Test reading points from a glTF file."""
    reader = GLTFReader(TRIANGLE_GLTF)
    mesh = reader.read()

    # glTF file extracts bounding box corners (8 points)
    assert mesh.n_points == 8
    # Verify bounds are correct
    assert mesh.points[:, 0].min() == 0.0
    assert mesh.points[:, 0].max() == 1.0
    assert mesh.points[:, 1].min() == 0.0
    assert mesh.points[:, 1].max() == 1.0
    assert mesh.points[:, 2].min() == 0.0
    assert mesh.points[:, 2].max() == 0.0


def test_gltf_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = GLTFReader(str(TRIANGLE_GLTF))
    mesh = reader.read()
    assert mesh.n_points == 8


def test_stl_reader_scene_data() -> None:
    """Test that STL reader mesh returns valid scene data."""
    mesh = STLReader(TRIANGLE_STL).read()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "stlReader"
    assert "data" in scene


@pytest.mark.parametrize(
    ("filename", "content", "error_type", "match"),
    [
        (
            "bad.stl",
            "NOT AN STL FILE\nfacet normal 0.0 0.0 1.0\nendsolid\n",
            ValueError,
            "missing 'solid' header",
        ),
    ],
)
def test_stl_reader_invalid_files(
    tmp_path: Path,
    filename: str,
    content: str,
    error_type: type,
    match: str,
) -> None:
    """Test ValueError for various invalid STL files."""
    bad_file = tmp_path / filename
    bad_file.write_text(content)
    with pytest.raises(error_type, match=match):
        STLReader(bad_file).read()


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .stl file"),
    ],
)
def test_stl_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            STLReader("nonexistent.stl")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            STLReader(bad_file)


def test_stl_reader_no_vertices(tmp_path: Path) -> None:
    """Test reading an STL file with no vertices yields empty mesh."""
    stl_file = tmp_path / "empty.stl"
    stl_file.write_text("solid empty\nendsolid empty\n")
    mesh = STLReader(stl_file).read()
    assert mesh.n_points == 0


# --- download_damaged_helmet tests ---


def test_download_damaged_helmet_returns_gltf_mesh() -> None:
    """Test that download_damaged_helmet returns a mesh with points."""
    mesh = examples.download_damaged_helmet()
    assert mesh.n_points > 0


def test_download_damaged_helmet_scene_data() -> None:
    """Test that download_damaged_helmet mesh generates valid scene data."""
    mesh = examples.download_damaged_helmet()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "gltfReader"
    assert "data" in scene


# --- download_cad_model tests ---


def test_download_cad_model_returns_stl_mesh() -> None:
    """Test that download_cad_model returns an _STLMesh."""
    mesh = examples.download_cad_model()
    assert mesh.n_points > 0


def test_download_cad_model_scene_data() -> None:
    """Test that download_cad_model mesh generates valid scene data."""
    mesh = examples.download_cad_model()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "stlReader"
    assert "data" in scene


def test_gltf_reader_scene_data() -> None:
    """Test that GLTF reader mesh returns valid scene data."""
    mesh = GLTFReader(TRIANGLE_GLTF).read()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "gltfReader"
    assert "data" in scene


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .gltf or .glb file"),
    ],
)
def test_gltf_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            GLTFReader("nonexistent.gltf")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            GLTFReader(bad_file)


def test_gltf_reader_invalid_json(tmp_path: Path) -> None:
    """Test reading an invalid JSON file yields empty mesh."""
    gltf_file = tmp_path / "invalid.gltf"
    gltf_file.write_text("not valid json")
    mesh = GLTFReader(gltf_file).read()
    assert mesh.n_points == 0


def test_gltf_reader_no_meshes(tmp_path: Path) -> None:
    """Test reading a glTF file with no meshes yields empty mesh."""
    gltf_file = tmp_path / "empty.gltf"
    gltf_file.write_text('{"asset": {"version": "2.0"}}')
    mesh = GLTFReader(gltf_file).read()
    assert mesh.n_points == 0


# --- download_bunny tests ---


def test_download_bunny_returns_ply_mesh() -> None:
    """Test that download_bunny returns a _PLYMesh."""
    mesh = examples.download_bunny()
    assert mesh.n_points > 0


def test_download_bunny_scene_data() -> None:
    """Test that download_bunny mesh generates valid scene data."""
    mesh = examples.download_bunny()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "mesh"
    assert "points" in scene
    assert "polys" in scene


def test_download_lucy_returns_ply_mesh() -> None:
    """Test that download_lucy returns a _PLYMesh."""
    mesh = examples.download_lucy()
    assert mesh.n_points > 0


def test_download_lucy_scene_data() -> None:
    """Test that download_lucy mesh generates valid scene data."""
    mesh = examples.download_lucy()
    scene = mesh.to_scene_data()
    assert scene is not None
    assert scene["type"] == "mesh"
    assert "points" in scene
    assert "polys" in scene
