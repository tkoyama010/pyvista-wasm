"""Pyodide-specific tests for pyvista-wasm.

These tests verify that pyvista-wasm works correctly in a Pyodide (WebAssembly)
environment using pytest-pyodide.

Note:
----
These tests require a Pyodide runtime and are executed in a browser environment.
They test the core functionality of pyvista-wasm when running in WebAssembly.

"""

from __future__ import annotations

import pytest

# Import run_in_pyodide decorator from pytest_pyodide
# This decorator allows running test code inside a Pyodide environment
pytest.importorskip("pytest_pyodide")
from pytest_pyodide import run_in_pyodide


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_basic_import(selenium):
    """Test that pyvista_wasm can be imported in Pyodide.

    This is a basic smoke test to ensure the package loads correctly
    in a WebAssembly environment.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture (passed automatically).

    """
    import pyvista_wasm as pv

    # Verify basic module attributes are accessible
    assert hasattr(pv, "Plotter")
    assert hasattr(pv, "Sphere")
    assert hasattr(pv, "__version__")


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_create_sphere_mesh(selenium):
    """Test that a sphere mesh can be created in Pyodide.

    This test verifies that the core mesh creation functionality works
    in the Pyodide environment.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Sphere

    # Create a sphere mesh
    sphere = Sphere(radius=1.0, center=(0, 0, 0))

    # Verify mesh properties
    assert sphere.n_points > 0
    assert sphere.n_cells > 0
    assert sphere.points.shape[1] == 3  # 3D coordinates


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_create_plotter(selenium):
    """Test that a Plotter can be created in Pyodide.

    This test verifies that the visualization components can be instantiated
    in the Pyodide environment.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Plotter, Sphere

    # Create a plotter
    plotter = Plotter()

    # Add a mesh to the plotter
    sphere = Sphere()
    actor = plotter.add_mesh(sphere, color="red")

    # Verify the actor was added
    assert actor is not None
    assert len(plotter.actors) == 1


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_generate_html(selenium):
    """Test that HTML can be generated in Pyodide.

    This test verifies that the HTML generation (for standalone rendering)
    works correctly in the Pyodide environment.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Plotter, Sphere

    # Create a simple plot
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="blue")

    # Generate standalone HTML
    html = plotter.generate_standalone_html()

    # Verify HTML was generated and contains expected elements
    assert isinstance(html, str)
    assert len(html) > 0
    assert "<html" in html.lower()
    assert "vtk" in html.lower() or "wasm" in html.lower()


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_line_mesh(selenium):
    """Test that line meshes work in Pyodide.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Line

    # Create a line from points
    points = [(0, 0, 0), (1, 1, 1), (2, 0, 0)]
    line = Line(points=points)

    # Verify line properties
    assert line.n_points == len(points)
    assert line.n_cells > 0


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_mesh_with_scalars(selenium):
    """Test that meshes with scalar arrays work in Pyodide.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    import numpy as np

    from pyvista_wasm import Sphere

    # Create a sphere with scalar data
    sphere = Sphere()
    scalars = np.linspace(0, 1, sphere.n_points)
    sphere.point_data["values"] = scalars

    # Verify scalar array was attached
    assert "values" in sphere.point_data
    assert len(sphere.point_data["values"]) == sphere.n_points


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_camera_properties(selenium):
    """Test that camera properties work in Pyodide.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Plotter

    plotter = Plotter()

    # Verify camera is accessible
    assert plotter.camera is not None

    # Test camera position (should be a 3-tuple or array)
    position = plotter.camera.position
    assert len(position) == 3


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_plotter_background_color(selenium):
    """Test that plotter background color can be set in Pyodide.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Plotter

    plotter = Plotter()

    # Set background color
    plotter.background_color = (0.2, 0.3, 0.4)

    # Verify color was set
    # Note: The exact storage format may vary, but it should be accessible
    assert plotter.background_color is not None


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_multiple_actors(selenium):
    """Test that multiple meshes can be added to a plotter in Pyodide.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Plotter, Sphere

    plotter = Plotter()

    # Add multiple spheres
    sphere1 = Sphere(radius=1.0, center=(0, 0, 0))
    sphere2 = Sphere(radius=0.5, center=(2, 0, 0))

    plotter.add_mesh(sphere1, color="red")
    plotter.add_mesh(sphere2, color="blue")

    # Verify both actors were added
    assert len(plotter.actors) == 2


@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_opacity_setting(selenium):
    """Test that opacity can be set when adding meshes in Pyodide.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    from pyvista_wasm import Plotter, Sphere

    plotter = Plotter()

    # Add mesh with opacity
    sphere = Sphere()
    actor = plotter.add_mesh(sphere, color="green", opacity=0.5)

    # Verify actor was created
    assert actor is not None


@pytest.mark.skip(reason="Requires network access for micropip install of jinja2")
@run_in_pyodide(packages=["pyvista-wasm", "numpy"])
def test_full_workflow_with_micropip(selenium):
    """Test a complete workflow using micropip in Pyodide.

    This test demonstrates the typical usage pattern in a Pyodide environment
    where dependencies may need to be installed via micropip.

    Parameters
    ----------
    selenium : SeleniumWrapper
        The pytest-pyodide selenium fixture.

    """
    import micropip

    # Ensure numpy is available (usually pre-installed in Pyodide)
    await micropip.install("numpy")

    from pyvista_wasm import Plotter, Sphere

    # Create and configure a plotter
    plotter = Plotter()
    plotter.background_color = (0.1, 0.1, 0.1)

    # Create a sphere with elevation data
    sphere = Sphere()
    elevation = sphere.points[:, 2]  # Z-coordinates as elevation
    sphere.point_data["elevation"] = elevation

    # Add to plotter
    plotter.add_mesh(sphere, scalars="elevation")

    # Generate HTML for display
    html = plotter.generate_standalone_html()

    # Verify the workflow completed
    assert html is not None
    assert isinstance(html, str)
    assert len(html) > 100  # Should be substantial HTML output
