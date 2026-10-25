"""Charts for pyvista-wasm.

Mirrors the PyVista ``charts`` API (``pyvista.charts.Chart2D``). Series
data is rendered by the renderer bridge as a 2D canvas overlay; when the
vtk-wasm binary exposes usable chart classes the backend can switch to
``VTK::ChartsCore`` objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

    from .texture import Texture  # noqa: F401  (keeps import order stable)


_DEFAULT_SERIES_COLORS = (
    (0.039, 0.408, 0.741),  # matplotlib C0 blue
    (0.851, 0.325, 0.098),  # matplotlib C1 orange
    (0.459, 0.678, 0.239),  # matplotlib C2 green
    (0.835, 0.369, 0.639),  # matplotlib C3 red/pink
)


class Axis:
    """Chart axis (mirrors ``pyvista.charts.Axis``).

    Parameters
    ----------
    label : str, optional
        Axis label text.

    """

    def __init__(self, label: str = "") -> None:
        """Initialize an axis with an optional label."""
        self.label = label


class Chart2D:
    """2D chart with line, scatter, and bar series (mirrors ``pyvista.charts.Chart2D``).

    Parameters
    ----------
    width : int, optional
        Chart width in pixels. Default is 640.
    height : int, optional
        Chart height in pixels. Default is 480.
    title : str, optional
        Chart title.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> import numpy as np
    >>> x = np.linspace(0, 2 * np.pi, 50)
    >>> chart = pv.Chart2D(title="sin")
    >>> _ = chart.line(x, np.sin(x))
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_chart(chart)

    """

    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        title: str = "",
    ) -> None:
        """Initialize an empty 2D chart."""
        self.width = width
        self.height = height
        self.title = title
        self.x_axis = Axis("x")
        self.y_axis = Axis("y")
        self._series: list[dict[str, object]] = []

    @property
    def _color_name_to_rgb(self) -> object:
        """Import color conversion lazily to avoid a circular import."""
        from .rendering import _color_name_to_rgb  # noqa: PLC0415

        return _color_name_to_rgb

    def _resolve_color(
        self,
        color: str | tuple[float, float, float] | None,
        index: int,
    ) -> list[float]:
        """Resolve a color spec to an RGB float triple."""
        if color is None:
            return list(_DEFAULT_SERIES_COLORS[index % len(_DEFAULT_SERIES_COLORS)])
        if isinstance(color, str):
            return list(self._color_name_to_rgb(color))  # type: ignore[operator]
        return [float(c) for c in color]

    @staticmethod
    def _validate_xy(x: ArrayLike, y: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
        """Validate matching 1D x/y arrays."""
        xv, yv = np.asarray(x), np.asarray(y)
        if xv.shape != yv.shape or xv.ndim != 1:
            msg = "x and y must be matching 1D arrays"
            raise ValueError(msg)
        return xv, yv

    def line(
        self,
        x: ArrayLike,
        y: ArrayLike,
        color: str | tuple[float, float, float] | None = None,
        width: float = 2.0,
        label: str | None = None,
    ) -> dict[str, object]:
        """Add a line series.

        Parameters
        ----------
        x : array-like
            X coordinates.
        y : array-like
            Y coordinates.
        color : str or tuple, optional
            Series color. Defaults to the palette color for this series index.
        width : float, optional
            Line width in pixels. Default is 2.0.
        label : str, optional
            Series label for the legend.

        Returns
        -------
        dict
            The stored series entry.

        """
        xv, yv = self._validate_xy(x, y)
        entry: dict[str, object] = {
            "kind": "line",
            "x": xv.tolist(),
            "y": yv.tolist(),
            "color": self._resolve_color(color, len(self._series)),
            "width": width,
            "label": label,
        }
        self._series.append(entry)
        return entry

    def scatter(
        self,
        x: ArrayLike,
        y: ArrayLike,
        color: str | tuple[float, float, float] | None = None,
        size: float = 6.0,
        label: str | None = None,
    ) -> dict[str, object]:
        """Add a scatter series.

        Parameters
        ----------
        x : array-like
            X coordinates.
        y : array-like
            Y coordinates.
        color : str or tuple, optional
            Series color.
        size : float, optional
            Marker size in pixels. Default is 6.0.
        label : str, optional
            Series label for the legend.

        Returns
        -------
        dict
            The stored series entry.

        """
        xv, yv = self._validate_xy(x, y)
        entry: dict[str, object] = {
            "kind": "scatter",
            "x": xv.tolist(),
            "y": yv.tolist(),
            "color": self._resolve_color(color, len(self._series)),
            "size": size,
            "label": label,
        }
        self._series.append(entry)
        return entry

    def bar(
        self,
        x: ArrayLike,
        y: ArrayLike,
        color: str | tuple[float, float, float] | None = None,
        label: str | None = None,
    ) -> dict[str, object]:
        """Add a bar series.

        Parameters
        ----------
        x : array-like
            Bar category positions.
        y : array-like
            Bar heights.
        color : str or tuple, optional
            Bar color.
        label : str, optional
            Series label for the legend.

        Returns
        -------
        dict
            The stored series entry.

        """
        xv, yv = self._validate_xy(x, y)
        entry: dict[str, object] = {
            "kind": "bar",
            "x": xv.tolist(),
            "y": yv.tolist(),
            "color": self._resolve_color(color, len(self._series)),
            "label": label,
        }
        self._series.append(entry)
        return entry

    def to_scene_data(self) -> dict[str, object]:
        """Return a JSON-serializable dict describing this chart."""
        return {
            "type": "chart",
            "width": self.width,
            "height": self.height,
            "title": self.title,
            "xLabel": self.x_axis.label,
            "yLabel": self.y_axis.label,
            "series": self._series,
        }
