"""Integration test to verify scalar rendering generates correct HTML."""

import webbrowser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from pyvista_wasm import Plotter, Sphere


def test_scalar_rendering_html_generation(monkeypatch) -> None:
    """Test that scalar coloring generates correct HTML with vtk.js code."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    # Create mesh with scalars
    mesh = Sphere()
    mesh["elevation"] = mesh.points[:, 2]

    # Create plotter and add mesh with scalar coloring
    plotter = Plotter()
    plotter.add_mesh(mesh, scalars="elevation", cmap="viridis")
    plotter.show()

    # Verify browser was opened
    assert len(opened) == 1
    assert opened[0].startswith("file://")

    # Read the generated HTML file
    html_path = url2pathname(urlparse(opened[0]).path)
    with Path(html_path).open(encoding="utf-8") as f:
        html_content = f.read()

    # Verify scalar-related data is present in the scene JSON
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    scene = extract_scene_data(html_content)
    actor = scene["actors"][0]
    assert actor["scalars"] is not None
    assert actor["scalars"]["arrayName"] == "elevation"
    assert actor["scalars"]["cmap"] == "viridis"
    assert "range" in actor["scalars"]


def test_multiple_colormaps_html_generation(monkeypatch) -> None:
    """Test that different colormaps generate different lookup tables."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    # Test viridis
    mesh1 = Sphere()
    mesh1["data"] = mesh1.points[:, 2]
    plotter1 = Plotter()
    plotter1.add_mesh(mesh1, scalars="data", cmap="viridis")
    plotter1.show()

    html_path1 = url2pathname(urlparse(opened[-1]).path)
    with Path(html_path1).open(encoding="utf-8") as f:
        html1 = f.read()

    assert "viridis" in html1

    # Test plasma
    mesh2 = Sphere()
    mesh2["data"] = mesh2.points[:, 2]
    plotter2 = Plotter()
    plotter2.add_mesh(mesh2, scalars="data", cmap="plasma")
    plotter2.show()

    html_path2 = url2pathname(urlparse(opened[-1]).path)
    with Path(html_path2).open(encoding="utf-8") as f:
        html2 = f.read()

    assert "plasma" in html2


def test_no_scalars_no_lut(monkeypatch) -> None:
    """Test that meshes without scalars don't generate lookup table code."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    mesh = Sphere()
    plotter = Plotter()
    plotter.add_mesh(mesh, color="red")
    plotter.show()

    html_path = url2pathname(urlparse(opened[0]).path)
    with Path(html_path).open(encoding="utf-8") as f:
        html_content = f.read()

    # Verify scalar-related code is NOT present
    assert "vtkColorTransferFunction" not in html_content
    assert "setScalarVisibility" not in html_content
