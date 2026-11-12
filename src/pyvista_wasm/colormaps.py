"""Colormap utilities for pyvista-wasm.

Maps scalar values to RGB colors for named colormaps, mirroring the
matplotlib colormaps PyVista supports. The tables are control-point
colors sampled from matplotlib's colormaps (matplotlib itself is not a
dependency).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

# Control-point colors sampled from the matplotlib colormaps.
_CMAP_STOPS: dict[str, list[tuple[int, int, int]]] = {
    "viridis": [
        (68, 1, 84),
        (72, 40, 120),
        (62, 74, 137),
        (49, 104, 142),
        (38, 130, 189),
        (31, 158, 137),
        (53, 183, 121),
        (109, 205, 89),
        (180, 222, 44),
        (253, 231, 37),
    ],
    "plasma": [
        (13, 8, 135),
        (84, 2, 163),
        (139, 10, 165),
        (185, 50, 137),
        (219, 92, 104),
        (244, 136, 73),
        (254, 188, 43),
        (240, 249, 33),
    ],
    "inferno": [
        (0, 0, 4),
        (40, 11, 84),
        (101, 21, 110),
        (159, 42, 99),
        (212, 72, 66),
        (245, 125, 21),
        (250, 193, 39),
        (252, 255, 164),
    ],
    "magma": [
        (0, 0, 4),
        (42, 13, 84),
        (101, 26, 110),
        (183, 54, 105),
        (249, 142, 8),
        (244, 199, 69),
        (252, 253, 191),
    ],
    "jet": [
        (0, 0, 143),
        (0, 0, 255),
        (0, 190, 255),
        (56, 255, 254),
        (149, 255, 166),
        (239, 217, 9),
        (254, 99, 24),
        (222, 13, 5),
    ],
}

_RGB_COMPONENTS = 3


def available_colormaps() -> list[str]:
    """Return the supported colormap names."""
    return sorted(_CMAP_STOPS)


def map_to_rgb(
    values: ArrayLike,
    cmap: str = "viridis",
    clim: tuple[float, float] | None = None,
) -> np.ndarray:
    """Map scalar values to ``(n, 3)`` uint8 RGB colors.

    Parameters
    ----------
    values : array-like
        Scalar values.
    cmap : str, optional
        Colormap name (see :func:`available_colormaps`). Default is
        ``'viridis'``.
    clim : tuple, optional
        ``(vmin, vmax)`` normalization range. Defaults to the data range.

    Returns
    -------
    numpy.ndarray
        An ``(n, 3)`` uint8 array of RGB colors.

    Raises
    ------
    ValueError
        If ``cmap`` is not a supported colormap name.

    Examples
    --------
    >>> import numpy as np
    >>> from pyvista_wasm.colormaps import map_to_rgb
    >>> rgb = map_to_rgb(np.array([0.0, 1.0]), cmap="viridis")
    >>> rgb.shape
    (2, 3)

    """
    stops = _CMAP_STOPS.get(cmap)
    if stops is None:
        msg = f"cmap must be one of {sorted(_CMAP_STOPS)}, got {cmap!r}"
        raise ValueError(msg)
    scalars = np.asarray(values, dtype=float).ravel()
    vmin, vmax = clim if clim is not None else (float(scalars.min()), float(scalars.max()))
    normalized = np.zeros_like(scalars) if vmax <= vmin else (scalars - vmin) / (vmax - vmin)
    positions = np.linspace(0.0, 1.0, len(stops))
    channels = np.asarray(stops, dtype=float).T
    rgb = np.column_stack(
        [np.interp(normalized, positions, channel) for channel in channels],
    )
    return np.clip(rgb, 0, 255).astype(np.uint8)
