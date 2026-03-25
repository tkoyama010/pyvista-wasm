"""Tests for Light class and lighting configuration."""

import pyvista_wasm as pv


def test_light_basic_properties() -> None:
    """Test basic light property access."""
    light = pv.Light(position=(1, 2, 3), color="red", intensity=0.5)
    assert light.position == (1, 2, 3)
    assert light.color == (1.0, 0.0, 0.0)
    assert light.intensity == 0.5


def test_light_default_properties() -> None:
    """Test default light properties."""
    light = pv.Light()
    assert light.position == (0, 0, 1)
    assert light.color == (1.0, 1.0, 1.0)
    assert light.intensity == 1.0
    assert light.light_type == "SceneLight"


def test_light_focal_point() -> None:
    """Test light focal point property."""
    light = pv.Light(focal_point=(1, 2, 3))
    assert light.focal_point == (1, 2, 3)


def test_light_positional() -> None:
    """Test positional light properties."""
    light = pv.Light(positional=True, cone_angle=30.0, cone_falloff=5.0)
    assert light.positional is True
    assert light.cone_angle == 30.0
    assert light.cone_falloff == 5.0


def test_light_attenuation() -> None:
    """Test light attenuation values."""
    light = pv.Light(attenuation_values=(1.0, 0.5, 0.1))
    assert light.attenuation_values == (1.0, 0.5, 0.1)


def test_light_type() -> None:
    """Test light type property."""
    scene_light = pv.Light(light_type="SceneLight")
    assert scene_light.light_type == "SceneLight"

    headlight = pv.Light(light_type="Headlight")
    assert headlight.light_type == "Headlight"


def test_light_default_attenuation() -> None:
    """Test default attenuation values."""
    light = pv.Light()
    assert light.attenuation_values == (1, 0, 0)


def test_light_default_positional() -> None:
    """Test default positional setting."""
    light = pv.Light()
    assert light.positional is False


def test_light_default_cone_angle() -> None:
    """Test default cone angle."""
    light = pv.Light()
    assert light.cone_angle == 30.0


def test_light_default_cone_falloff() -> None:
    """Test default cone falloff."""
    light = pv.Light()
    assert light.cone_falloff == 5.0


def test_light_default_focal_point() -> None:
    """Test default focal point."""
    light = pv.Light()
    assert light.focal_point == (0, 0, 0)


def test_light_color_tuple() -> None:
    """Test light with color as RGB tuple."""
    light = pv.Light(color=(0.5, 0.3, 0.1))
    assert light.color == (0.5, 0.3, 0.1)


def test_light_color_string() -> None:
    """Test light with named color string."""
    light = pv.Light(color="blue")
    assert light.color == (0.0, 0.0, 1.0)


def test_light_intensity_range() -> None:
    """Test light intensity values."""
    light_zero = pv.Light(intensity=0.0)
    assert light_zero.intensity == 0.0

    light_high = pv.Light(intensity=5.0)
    assert light_high.intensity == 5.0


def test_plotter_add_light() -> None:
    """Test adding a light to the plotter."""
    plotter = pv.Plotter()
    light = pv.Light(position=(1, 2, 3))
    plotter.add_light(light)
    assert len(plotter._renderer.lights) == 1


def test_plotter_multiple_lights() -> None:
    """Test adding multiple lights to the plotter."""
    plotter = pv.Plotter()
    light1 = pv.Light(position=(1, 0, 0))
    light2 = pv.Light(position=(0, 1, 0))
    plotter.add_light(light1)
    plotter.add_light(light2)
    assert len(plotter._renderer.lights) == 2


def test_plotter_clear_removes_lights() -> None:
    """Test that clear() removes all lights."""
    plotter = pv.Plotter()
    plotter.add_light(pv.Light())
    plotter._renderer.clear()
    assert len(plotter._renderer.lights) == 0


def test_plotter_lighting_default() -> None:
    """Test that Plotter() creates default lighting."""
    plotter = pv.Plotter()
    assert plotter._renderer.lighting == "default"
    lights = plotter._renderer._build_lights_data()
    assert len(lights) > 0
    assert lights[0]["position"] == [1, 1, 1]


def test_plotter_lighting_explicit_default() -> None:
    """Test that Plotter(lighting='default') creates default lighting."""
    plotter = pv.Plotter(lighting="default")
    assert plotter._renderer.lighting == "default"
    lights = plotter._renderer._build_lights_data()
    assert len(lights) > 0


def test_plotter_lighting_none() -> None:
    """Test that Plotter(lighting=None) disables default lighting."""
    plotter = pv.Plotter(lighting=None)
    assert plotter._renderer.lighting is None
    lights = plotter._renderer._build_lights_data()
    assert len(lights) == 0


def test_plotter_lighting_none_with_custom_lights() -> None:
    """Test that custom lights work with lighting=None."""
    plotter = pv.Plotter(lighting=None)
    light1 = pv.Light(position=(1, 0, 0), color="red", intensity=2.0)
    light2 = pv.Light(position=(-1, 0, 0), color="blue", intensity=1.5)
    plotter.add_light(light1)
    plotter.add_light(light2)

    assert len(plotter._renderer.lights) == 2
    lights = plotter._renderer._build_lights_data()
    assert len(lights) == 2
    assert lights[0]["position"] == [1, 0, 0]
    assert lights[1]["position"] == [-1, 0, 0]


def test_plotter_lighting_default_with_custom_lights() -> None:
    """Test that custom lights override default lighting."""
    plotter = pv.Plotter(lighting="default")
    light = pv.Light(position=(2, 2, 2), intensity=3.0)
    plotter.add_light(light)

    lights = plotter._renderer._build_lights_data()
    assert len(lights) == 1
    assert lights[0]["position"] == [2, 2, 2]
    assert lights[0]["intensity"] == 3.0
