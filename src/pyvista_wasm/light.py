"""Light class for pyvista-wasm.

This module provides the Light class for adding light sources to 3D scenes.
"""

from __future__ import annotations

SCENE_LIGHT = "SceneLight"
CAMERA_LIGHT = "CameraLight"
HEADLIGHT = "Headlight"

_LIGHT_TYPES = (SCENE_LIGHT, CAMERA_LIGHT, HEADLIGHT)


class Light:
    """Light class.

    Parameters
    ----------
    position : sequence[float], optional
        The position of the light. The interpretation of the position
        depends on the type of the light and whether the light has a
        transformation matrix.

    focal_point : sequence[float], optional
        The focal point of the light. The interpretation of the focal
        point depends on the type of the light and whether the light
        has a transformation matrix.

    color : sequence[float] | str, optional
        The color of the light. The ambient, diffuse and specular
        colors will all be set to this color on creation.

    light_type : str, default: ``'SceneLight'``
        The type of the light. One of ``'Headlight'``,
        ``'CameraLight'`` or ``'SceneLight'``.

            - A headlight is attached to the camera, looking at its
              focal point along the axis of the camera.

            - A camera light also moves with the camera, but it can
              occupy a general position with respect to it.

            - A scene light is stationary with respect to the scene,
              as it does not follow the camera. This is the default.

    intensity : float, optional
        The brightness of the light (between 0 and 1).

    positional : bool, optional
        Set if the light is positional.

        The default is a directional light, i.e. an infinitely distant
        point source. A positional light with a cone angle of at least
        90 degrees acts like a spherical point source. A positional
        light with a cone angle that is less than 90 degrees is known
        as a spotlight.

    cone_angle : float, optional
        Cone angle of a positional light in degrees.

    cone_falloff : float, optional
        The exponent of the cosine used for spotlights.

    attenuation_values : sequence[float], optional
        Quadratic attenuation constants.

        The values are a 3-length sequence which specifies the constant,
        linear and quadratic constants in this order. These parameters
        only have an effect for positional lights.

    Examples
    --------
    Headlight. For headlights the position and focal point properties
    are meaningless. No matter where you move the camera, the light
    always emanates from the view point:

    >>> import pyvista_wasm as pv
    >>> from pyvista_wasm import examples
    >>> mesh = examples.download_bunny()
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(mesh, color='lightblue')
    >>> light = pv.Light(light_type='Headlight')
    >>> # these don't do anything for a headlight:
    >>> light.position = (1, 2, 3)
    >>> light.focal_point = (4, 5, 6)
    >>> plotter.add_light(light)
    >>> plotter.show()  # doctest: +SKIP

    Camera light. Camera lights move together with the camera, but
    can occupy any fixed relative position with respect to the camera:

    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(mesh, color='lightblue')
    >>> # a light that always shines from the right of the camera
    >>> light = pv.Light(position=(1, 0, 0), light_type='CameraLight')
    >>> plotter.add_light(light)
    >>> plotter.show()  # doctest: +SKIP

    Scene light. Scene lights are attached to the scene, their position
    and focal point are interpreted as global coordinates:

    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(mesh, color='lightblue')
    >>> # a light that always shines on the left side of the bunny
    >>> light = pv.Light(position=(0, 1, 0), light_type='SceneLight')
    >>> plotter.add_light(light)
    >>> plotter.show()  # doctest: +SKIP

    """

    def __init__(  # noqa: PLR0913
        self,
        position: tuple[float, float, float] = (0.0, 0.0, 1.0),
        focal_point: tuple[float, float, float] = (0.0, 0.0, 0.0),
        color: tuple[float, float, float] | str = (1.0, 1.0, 1.0),
        intensity: float = 1.0,
        light_type: str = SCENE_LIGHT,
        positional: bool = False,  # noqa: FBT001 FBT002
        cone_angle: float = 30.0,
        cone_falloff: float = 5.0,
        attenuation_values: tuple[float, float, float] = (1.0, 0.0, 0.0),
    ) -> None:
        """Initialize a Light instance."""
        if light_type not in _LIGHT_TYPES:
            msg = f"light_type must be one of {_LIGHT_TYPES}, got '{light_type}'"
            raise ValueError(msg)

        self.position = (float(position[0]), float(position[1]), float(position[2]))
        self.focal_point = (
            float(focal_point[0]),
            float(focal_point[1]),
            float(focal_point[2]),
        )
        if isinstance(color, str):
            color = _color_name_to_rgb(color)
        self.color: tuple[float, float, float] = (
            float(color[0]),
            float(color[1]),
            float(color[2]),
        )
        self.intensity = float(intensity)
        self.light_type = light_type
        self.positional = bool(positional)
        self.cone_angle = float(cone_angle)
        self.cone_falloff = float(cone_falloff)
        self.attenuation_values = (
            float(attenuation_values[0]),
            float(attenuation_values[1]),
            float(attenuation_values[2]),
        )

    # ------------------------------------------------------------------
    # Convenience setters matching VTK.wasm / PyVista naming
    # ------------------------------------------------------------------

    def set_light_type_to_scene_light(self) -> None:
        """Set light type to SceneLight (fixed in world space)."""
        self.light_type = SCENE_LIGHT

    def set_light_type_to_camera_light(self) -> None:
        """Set light type to CameraLight (moves with the camera)."""
        self.light_type = CAMERA_LIGHT

    def set_light_type_to_headlight(self) -> None:
        """Set light type to Headlight (at camera position)."""
        self.light_type = HEADLIGHT

    # ------------------------------------------------------------------
    # JavaScript code generation
    # ------------------------------------------------------------------

    def generate_vtk_js_code(self, idx: int) -> str:
        """Generate VTK.wasm JavaScript code for this light.

        Parameters
        ----------
        idx : int
            Unique index used to avoid variable name collisions in JavaScript.

        Returns
        -------
        str
            JavaScript code that creates and configures the light.

        """
        px, py, pz = self.position
        fx, fy, fz = self.focal_point
        cr, cg, cb = self.color
        av0, av1, av2 = self.attenuation_values
        positional_js = "true" if self.positional else "false"

        light_type_call = {
            SCENE_LIGHT: "light{idx}.setLightTypeToSceneLight();",
            CAMERA_LIGHT: "light{idx}.setLightTypeToCameraLight();",
            HEADLIGHT: "light{idx}.setLightTypeToHeadLight();",
        }[self.light_type].format(idx=idx)

        lines = [
            f"const light{idx} = vtk.Rendering.Core.vtkLight.newInstance();",
            light_type_call,
            f"light{idx}.setPosition({px}, {py}, {pz});",
            f"light{idx}.setFocalPoint({fx}, {fy}, {fz});",
            f"light{idx}.setColor({cr}, {cg}, {cb});",
            f"light{idx}.setIntensity({self.intensity});",
            f"light{idx}.setPositional({positional_js});",
            f"light{idx}.setConeAngle({self.cone_angle});",
            f"light{idx}.setExponent({self.cone_falloff});",
            f"light{idx}.setAttenuationValues({av0}, {av1}, {av2});",
            f"renderer.addLight(light{idx});",
        ]
        return "\n".join(lines)


def _color_name_to_rgb(color_name: str) -> tuple[float, float, float]:
    """Convert a color name to an RGB tuple."""
    colors = {
        "red": (1.0, 0.0, 0.0),
        "green": (0.0, 1.0, 0.0),
        "blue": (0.0, 0.0, 1.0),
        "yellow": (1.0, 1.0, 0.0),
        "cyan": (0.0, 1.0, 1.0),
        "magenta": (1.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0),
        "black": (0.0, 0.0, 0.0),
        "orange": (1.0, 0.647, 0.0),
        "purple": (0.5, 0.0, 0.5),
    }
    result = colors.get(color_name.lower())
    if result is None:
        msg = f"Unknown color name: '{color_name}'. Supported: {', '.join(colors)}"
        raise ValueError(msg)
    return result
