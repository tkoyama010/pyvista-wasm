"""Text class for pyvista-wasm.

This module provides the Text class for adding text annotations to 3D scenes.
"""

# ruff: noqa: A003
from __future__ import annotations


class TextProperty:
    """Properties for text rendering.

    Provides control over text appearance including font size, color, and opacity.

    Parameters
    ----------
    font_size : int, optional
        Font size in points. Default is ``18``.
    color : tuple of float or str, optional
        RGB color with values between 0 and 1, or a color name. Default is white.
    opacity : float, optional
        Text opacity between 0 (transparent) and 1 (opaque). Default is ``1.0``.
    bold : bool, optional
        Enable bold text. Default is ``False``.
    italic : bool, optional
        Enable italic text. Default is ``False``.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> prop = pv.TextProperty(font_size=24, color="red", bold=True)
    >>> prop.font_size
    24

    """

    def __init__(
        self,
        font_size: int = 18,
        color: tuple[float, float, float] | str = (1.0, 1.0, 1.0),
        opacity: float = 1.0,
        bold: bool = False,  # noqa: FBT001 FBT002
        italic: bool = False,  # noqa: FBT001 FBT002
    ) -> None:
        """Initialize a TextProperty instance."""
        self.font_size = int(font_size)
        if isinstance(color, str):
            color = _color_name_to_rgb(color)
        self.color: tuple[float, float, float] = color
        self.opacity = float(opacity)
        self.bold = bool(bold)
        self.italic = bool(italic)


class Text:
    r"""A text annotation actor for 3D rendering.

    Wraps ``vtk.Rendering.Core.vtkTextActor`` to display 2D text overlays on 3D scenes.
    Text is positioned in normalized viewport coordinates (0 to 1 in both x and y).

    Parameters
    ----------
    text : str, optional
        Text string to be displayed. ``"\n"`` is recognized as a line separator.
        Characters must be UTF-8 encoded. Default is ``"Text"``.
    position : tuple of float, optional
        Position coordinate in normalized viewport space (x, y) where
        (0, 0) is bottom-left and (1, 1) is top-right. Default is ``(0.5, 0.5)``.
    prop : TextProperty, optional
        The property of this text actor controlling appearance. If ``None``,
        creates a default TextProperty. Default is ``None``.
    name : str, optional
        The name of this actor used when tracking on a plotter. Default is ``None``.

    Examples
    --------
    Create a text overlay:

    >>> import pyvista_wasm as pv
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(pv.Sphere(), color='white')
    >>> text = pv.Text("Hello World", position=(0.5, 0.9))
    >>> plotter.add_text(text)
    >>> plotter.show()

    Customize text appearance:

    >>> text = pv.Text(
    ...     "Custom Text",
    ...     position=(0.1, 0.1),
    ...     prop=pv.TextProperty(font_size=24, color="red", bold=True),
    ... )

    """

    def __init__(
        self,
        text: str = "Text",
        position: tuple[float, float] = (0.5, 0.5),
        prop: TextProperty | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize a Text instance."""
        self._input = str(text)
        self.position = position
        self.prop = prop if prop is not None else TextProperty()
        self.name = name

    @property
    def input(self) -> str:
        r"""Get or set the text string to be displayed.

        Parameters
        ----------
        value : str
            Text string to display. Newline characters (``"\n"``) are recognized
            as line separators. Characters must be UTF-8 encoded.

        Returns
        -------
        str
            The current text string.

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> text = pv.Text()
        >>> text.input = "Hello\nWorld"
        >>> text.input
        'Hello\nWorld'

        """
        return self._input

    @input.setter
    def input(self, value: str) -> None:
        """Set the text string."""
        self._input = str(value)

    @property
    def position(self) -> tuple[float, float]:
        """Get or set the text position in normalized viewport coordinates.

        Position is specified in normalized viewport coordinates where
        (0, 0) is the bottom-left corner and (1, 1) is the top-right corner.

        Parameters
        ----------
        value : tuple of float
            Position as (x, y) in normalized viewport coordinates.

        Returns
        -------
        tuple of float
            Position as (x, y).

        Examples
        --------
        >>> import pyvista_wasm as pv
        >>> text = pv.Text()
        >>> text.position = (0.1, 0.9)
        >>> text.position
        (0.1, 0.9)

        """
        return self._position

    @position.setter
    def position(self, value: tuple[float, float]) -> None:
        """Set the text position."""
        self._position = (float(value[0]), float(value[1]))

    # ------------------------------------------------------------------
    # JavaScript code generation
    # ------------------------------------------------------------------

    def generate_vtk_js_code(self, idx: int) -> str:
        """Generate JavaScript code for this text actor as an HTML overlay div.

        Parameters
        ----------
        idx : int
            Unique index used to avoid variable name collisions in JavaScript.

        Returns
        -------
        str
            JavaScript code that creates and configures the text overlay div.
            Uses an absolutely positioned div over the rendering container
            because ``vtkTextActor`` is not available in the VTK.wasm bundle.

        """
        pos_x, pos_y = self.position
        r, g, b = self.prop.color
        r_css = int(r * 255)
        g_css = int(g * 255)
        b_css = int(b * 255)
        font_weight = "bold" if self.prop.bold else "normal"
        font_style = "italic" if self.prop.italic else "normal"

        # Escape text for JavaScript string
        text_escaped = self._input.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

        left_pct = pos_x * 100
        bottom_pct = pos_y * 100

        lines = [
            "(function() {",
            f'  var textOverlay{idx} = document.createElement("div");',
            f'  textOverlay{idx}.innerText = "{text_escaped}";',
            f"  textOverlay{idx}.style.position = 'absolute';",
            f"  textOverlay{idx}.style.left = '{left_pct}%';",
            f"  textOverlay{idx}.style.bottom = '{bottom_pct}%';",
            f"  textOverlay{idx}.style.color = "
            f"'rgba({r_css}, {g_css}, {b_css}, {self.prop.opacity})';",
            f"  textOverlay{idx}.style.fontSize = '{self.prop.font_size}px';",
            f"  textOverlay{idx}.style.fontWeight = '{font_weight}';",
            f"  textOverlay{idx}.style.fontStyle = '{font_style}';",
            f"  textOverlay{idx}.style.pointerEvents = 'none';",
            f"  textOverlay{idx}.style.zIndex = '10';",
            f"  textOverlay{idx}.style.whiteSpace = 'pre';",
            f"  textOverlay{idx}.style.textShadow = "
            f"'1px 1px 2px rgba(0,0,0,0.8), -1px -1px 2px rgba(0,0,0,0.8)';",
            f"  container.appendChild(textOverlay{idx});",
            "})();",
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
