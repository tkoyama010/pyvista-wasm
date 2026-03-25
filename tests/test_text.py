"""Tests for the Text class."""

import pytest

import pyvista_wasm as pv
from pyvista_wasm.text import Text, TextProperty


def test_text_defaults() -> None:
    """Test Text default values."""
    text = Text()
    assert text.input == "Text"
    assert text.position == (0.5, 0.5)
    assert text.prop is not None
    assert text.prop.font_size == 18
    assert text.prop.color == (1.0, 1.0, 1.0)
    assert text.prop.opacity == 1.0
    assert text.prop.bold is False
    assert text.prop.italic is False
    assert text.name is None


def test_text_custom_params() -> None:
    """Test Text with custom parameters."""
    prop = TextProperty(font_size=24, color="red", bold=True)
    text = Text(
        text="Hello World",
        position=(0.1, 0.9),
        prop=prop,
        name="my_text",
    )
    assert text.input == "Hello World"
    assert text.position == (0.1, 0.9)
    assert text.prop.font_size == 24
    assert text.prop.color == (1.0, 0.0, 0.0)
    assert text.prop.bold is True
    assert text.name == "my_text"


def test_text_input_setter() -> None:
    """Test setting text input."""
    text = Text()
    text.input = "New Text"
    assert text.input == "New Text"


def test_text_input_multiline() -> None:
    """Test multiline text input."""
    text = Text(text="Line 1\nLine 2\nLine 3")
    assert text.input == "Line 1\nLine 2\nLine 3"


def test_text_position_setter() -> None:
    """Test setting text position."""
    text = Text()
    text.position = (0.2, 0.8)
    assert text.position == (0.2, 0.8)


def test_text_position_converts_to_float() -> None:
    """Test that position values are converted to float."""
    text = Text(position=(1, 0))
    assert all(isinstance(v, float) for v in text.position)
    assert text.position == (1.0, 0.0)


def test_text_property_defaults() -> None:
    """Test TextProperty default values."""
    prop = TextProperty()
    assert prop.font_size == 18
    assert prop.color == (1.0, 1.0, 1.0)
    assert prop.opacity == 1.0
    assert prop.bold is False
    assert prop.italic is False


def test_text_property_custom() -> None:
    """Test TextProperty with custom values."""
    prop = TextProperty(
        font_size=32,
        color=(0.0, 1.0, 0.0),
        opacity=0.8,
        bold=True,
        italic=True,
    )
    assert prop.font_size == 32
    assert prop.color == (0.0, 1.0, 0.0)
    assert prop.opacity == 0.8
    assert prop.bold is True
    assert prop.italic is True


def test_text_property_color_name() -> None:
    """Test TextProperty accepts color names."""
    prop = TextProperty(color="blue")
    assert prop.color == (0.0, 0.0, 1.0)

    prop = TextProperty(color="green")
    assert prop.color == (0.0, 1.0, 0.0)


def test_text_property_invalid_color_name() -> None:
    """Test TextProperty raises on unknown color name."""
    with pytest.raises(ValueError, match="Unknown color name"):
        TextProperty(color="notacolor")


def test_text_generate_vtk_js_code() -> None:
    """Test JavaScript code generation for Text."""
    text = Text("Test Text", position=(0.5, 0.9))
    code = text.generate_vtk_js_code(0)
    assert 'document.createElement("div")' in code
    assert 'innerText = "Test Text"' in code
    assert "left = '50.0%'" in code
    assert "bottom = '90.0%'" in code
    assert "fontSize = '18px'" in code
    assert "container.appendChild(textOverlay0)" in code


def test_text_generate_vtk_js_code_bold() -> None:
    """Test JavaScript code generation for bold text."""
    prop = TextProperty(bold=True)
    text = Text("Bold Text", prop=prop)
    code = text.generate_vtk_js_code(0)
    assert "fontWeight = 'bold'" in code


def test_text_generate_vtk_js_code_italic() -> None:
    """Test JavaScript code generation for italic text."""
    prop = TextProperty(italic=True)
    text = Text("Italic Text", prop=prop)
    code = text.generate_vtk_js_code(0)
    assert "fontStyle = 'italic'" in code


def test_text_generate_vtk_js_code_custom_color() -> None:
    """Test JavaScript code generation with custom color."""
    prop = TextProperty(color="red", font_size=24)
    text = Text("Red Text", prop=prop)
    code = text.generate_vtk_js_code(0)
    assert "rgba(255, 0, 0," in code
    assert "fontSize = '24px'" in code


def test_text_generate_vtk_js_code_escaping() -> None:
    """Test JavaScript code generation escapes special characters."""
    text = Text('Text with "quotes" and \\backslash')
    code = text.generate_vtk_js_code(0)
    assert '\\"' in code or "\\\\backslash" in code


def test_plotter_add_text() -> None:
    """Test that add_text stores the text actor in the renderer."""
    plotter = pv.Plotter()
    text = pv.Text("Hello", position=(0.5, 0.9))
    plotter.add_text(text)
    assert len(plotter._renderer.text_actors) == 1
    assert plotter._renderer.text_actors[0] is text


def test_plotter_add_multiple_texts() -> None:
    """Test adding multiple text actors."""
    plotter = pv.Plotter()
    plotter.add_text(pv.Text("Title", position=(0.5, 0.9)))
    plotter.add_text(pv.Text("Subtitle", position=(0.5, 0.8)))
    assert len(plotter._renderer.text_actors) == 2


def test_plotter_clear_removes_texts() -> None:
    """Test that clear() removes text actors as well as regular actors."""
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere())
    plotter.add_text(pv.Text("Test"))
    plotter.clear()
    assert len(plotter._renderer.text_actors) == 0
    assert len(plotter.actors) == 0


def test_text_in_scene_data() -> None:
    """Test that text actors are included in the scene data JSON."""
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere(), color="white")
    plotter.add_text(pv.Text("Hello", position=(0.5, 0.9)))
    plotter.add_text(
        pv.Text(
            "Red Bold",
            position=(0.1, 0.1),
            prop=TextProperty(font_size=24, color="red", bold=True, italic=True),
        ),
    )

    scene = plotter._renderer._build_scene_data()
    text_actors = scene["textActors"]
    assert len(text_actors) == 2

    t0 = text_actors[0]
    assert t0["text"] == "Hello"
    assert t0["position"] == [0.5, 0.9]
    assert t0["fontSize"] == 18
    assert t0["color"] == [1.0, 1.0, 1.0]
    assert t0["bold"] is False

    t1 = text_actors[1]
    assert t1["text"] == "Red Bold"
    assert t1["position"] == [0.1, 0.1]
    assert t1["fontSize"] == 24
    assert t1["color"] == [1.0, 0.0, 0.0]
    assert t1["bold"] is True
    assert t1["italic"] is True


def test_text_scene_data_empty() -> None:
    """Test that scene data has empty textActors when none are added."""
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere())
    scene = plotter._renderer._build_scene_data()
    assert scene["textActors"] == []


def test_text_exported_from_package() -> None:
    """Test that Text is accessible from the top-level package."""
    assert hasattr(pv, "Text")
    assert pv.Text is Text


def test_text_property_exported_from_package() -> None:
    """Test that TextProperty is accessible from the top-level package."""
    assert hasattr(pv, "TextProperty")
    assert pv.TextProperty is TextProperty
