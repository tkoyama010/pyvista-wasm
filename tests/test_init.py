"""Test package initialization and metadata."""

import pytest

import pyvista_wasm


def test_import() -> None:
    """Test that package can be imported."""
    assert pyvista_wasm is not None


@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        ("__version__", "0.1.0"),
        ("__author__", "Tetsuo Koyama"),
        ("__license__", "Apache-2.0"),
    ],
)
def test_metadata_attributes(attr, expected) -> None:
    """Test that metadata attributes exist and have correct values."""
    assert hasattr(pyvista_wasm, attr)
    assert getattr(pyvista_wasm, attr) == expected
    assert isinstance(getattr(pyvista_wasm, attr), str)


@pytest.mark.parametrize(
    "name",
    [
        "Plotter",
        "PolyData",
        "Sphere",
        "Cube",
        "Cylinder",
    ],
)
def test_exports(name) -> None:
    """Test that main classes are exported."""
    assert hasattr(pyvista_wasm, name)


def test_all_attribute() -> None:
    """Test that __all__ is properly defined."""
    assert hasattr(pyvista_wasm, "__all__")
    assert isinstance(pyvista_wasm.__all__, list)

    expected_exports = ["__version__", "Plotter", "PolyData", "Sphere", "Cube", "Cylinder"]
    for name in expected_exports:
        assert name in pyvista_wasm.__all__
