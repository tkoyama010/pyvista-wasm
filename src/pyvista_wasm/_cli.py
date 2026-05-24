"""Command-line interface for pyvista-wasm.

Provides a ``pyvista-wasm`` command with subcommands modelled after the
PyVista CLI so that common tasks (plotting mesh files, printing package
information) can be done without writing any Python code.
"""

from __future__ import annotations

import logging
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from ._capture import (
    _capture_marimo_screenshots,
    _capture_screenshots,
    _capture_stlite_screenshots,
    _create_gif,
    _find_canvas_in_frames,
    _rotate_canvas_with_mouse,
    _wait_for_canvas_in_frames,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)

# Supported file extensions and the reader class name they map to.
_READER_MAP: dict[str, str] = {
    ".vtk": "PolyDataReader",
    ".ply": "PLYReader",
    ".obj": "OBJReader",
}

# Create the main Typer app
app = typer.Typer(
    name="pyvista-wasm",
    help="PyVista-like CLI for browser-based 3-D visualization with VTK.wasm.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:  # noqa: FBT001
    """Show version information and exit."""
    if value:
        typer.echo(f"pyvista-wasm {_get_version()}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """PyVista-like CLI for browser-based 3-D visualization with VTK.wasm."""


def _get_version() -> str:
    """Return the pyvista_wasm version string."""
    from pyvista_wasm import __version__  # noqa: PLC0415

    return __version__


def _read_mesh(path: Path):  # type: ignore[return]  # noqa: ANN202
    """Read a mesh file and return a PolyData object.

    Parameters
    ----------
    path : Path
        Path to the mesh file. Must have a supported extension
        (``.vtk``, ``.ply``, or ``.obj``).

    Returns
    -------
    pyvista_wasm.mesh.PolyData
        The loaded mesh.

    Raises
    ------
    SystemExit
        When the file does not exist or its extension is not supported.

    """
    import pyvista_wasm as pv  # noqa: PLC0415

    if not path.exists():
        logger.error("file not found: %s", path)
        sys.exit(1)

    suffix = path.suffix.lower()
    reader_name = _READER_MAP.get(suffix)
    if reader_name is None:
        supported = ", ".join(_READER_MAP)
        logger.error("unsupported file format '%s'. Supported: %s", suffix, supported)
        sys.exit(1)

    reader_cls = getattr(pv, reader_name)
    return reader_cls(path).read()


def _load_plotter_from_pickle(pickle_path: Path):  # type: ignore[return]  # noqa: ANN202
    """Load a Plotter object from a pickle file.

    Parameters
    ----------
    pickle_path : Path
        Path to the pickle file containing a Plotter object.

    Returns
    -------
    pyvista_wasm.Plotter
        The loaded Plotter object.

    Raises
    ------
    SystemExit
        When the file does not exist, cannot be loaded, or does not
        contain a valid Plotter object.

    """
    import pickle  # noqa: PLC0415

    import pyvista_wasm as pv  # noqa: PLC0415

    if not pickle_path.exists():
        logger.error("pickle file not found: %s", pickle_path)
        sys.exit(1)

    # Security warning
    logger.warning(
        "WARNING: Loading pickle files can execute arbitrary code. "
        "Only load pickle files from trusted sources.",
    )

    try:
        with pickle_path.open("rb") as f:
            plotter = pickle.load(f)  # noqa: S301
    except Exception:
        logger.exception("failed to load pickle file")
        sys.exit(1)

    # Validate that we loaded a Plotter object
    if not isinstance(plotter, pv.Plotter):
        logger.error(
            "pickle file does not contain a Plotter object (got %s)",
            type(plotter).__name__,
        )
        sys.exit(1)

    return plotter


def _apply_camera_movement(
    plotter,  # noqa: ANN001
    azimuth: float | None,
    elevation: float | None,
    zoom: float | None,
    roll: float | None,
) -> None:
    """Apply relative camera movements to an existing plotter camera.

    All movements are relative to the current camera state.  Delegates
    to :class:`~pyvista_wasm.Camera` methods.

    Parameters
    ----------
    plotter : pyvista_wasm.Plotter
        The plotter whose camera will be modified.
    azimuth : float or None
        Horizontal rotation around the focal point in degrees.
    elevation : float or None
        Vertical rotation around the focal point in degrees.
    zoom : float or None
        Zoom factor (>1 zooms in, <1 zooms out).
    roll : float or None
        Roll rotation around the view axis in degrees.

    """
    from .camera import Camera  # noqa: PLC0415

    if plotter.camera is None:
        plotter.camera = Camera()

    cam = plotter.camera

    if azimuth is not None:
        cam.azimuth(azimuth)
    if elevation is not None:
        cam.orbit_elevation(elevation)
    if zoom is not None:
        if zoom <= 0:
            logger.error("zoom must be positive, got %s", zoom)
            sys.exit(1)
        cam.zoom(zoom)
    if roll is not None:
        cam.roll(roll)


def _build_plotter(  # noqa: ANN202
    files: list[Path] | None,
    color: str | None,
    background: str | None,
    opacity: float,
    load_pickle: Path | None,
):  # type: ignore[return]
    """Build a Plotter from mesh files or a pickle, returning it ready to display.

    Parameters
    ----------
    files : list of Path or None
        Mesh files to load.
    color : str or None
        Mesh colour.
    background : str or None
        Background colour override.
    opacity : float
        Mesh opacity.
    load_pickle : Path or None
        Path to a pickled Plotter to load instead.

    Returns
    -------
    pyvista_wasm.Plotter
        The configured plotter.

    """
    import pyvista_wasm as pv  # noqa: PLC0415

    if load_pickle is not None:
        plotter = _load_plotter_from_pickle(load_pickle)

        if files:
            for file_path in files:
                mesh = _read_mesh(file_path)
                plotter.add_mesh(mesh, color=color, opacity=opacity)

        if background is not None:
            plotter.background_color = background
    else:
        if not files:
            logger.error(
                "no mesh files provided. Either provide mesh files or use --load-pickle.",
            )
            sys.exit(1)

        plotter = pv.Plotter()

        if background is not None:
            plotter.background_color = background

        for file_path in files:
            mesh = _read_mesh(file_path)
            plotter.add_mesh(mesh, color=color, opacity=opacity)

    return plotter


def _save_pickle(plotter, pickle_path: Path) -> None:  # noqa: ANN001
    """Serialize a Plotter to a pickle file.

    Parameters
    ----------
    plotter : pyvista_wasm.Plotter
        The plotter to save.
    pickle_path : Path
        Destination file path.

    """
    import pickle as pickle_module  # noqa: PLC0415

    with pickle_path.open("wb") as f:
        pickle_module.dump(plotter, f)
    logger.info("Plotter saved to: %s", pickle_path)


def _parse_window_size(size_str: str) -> tuple[int, int]:
    """Parse a ``'width,height'`` string into an integer pair.

    Parameters
    ----------
    size_str : str
        Window size string, e.g. ``'1920,1080'``.

    Returns
    -------
    tuple of int
        ``(width, height)``.

    Raises
    ------
    SystemExit
        When the format is invalid.

    """
    try:
        width_str, height_str = size_str.split(",")
        return (int(width_str.strip()), int(height_str.strip()))
    except (ValueError, AttributeError):
        logger.error(  # noqa: TRY400
            "Invalid window size format '%s'. Expected 'width,height' (e.g. '1920,1080')",
            size_str,
        )
        sys.exit(1)


def _take_screenshot(
    plotter,  # noqa: ANN001
    screenshot: Path,
    screenshot_transparent: bool,  # noqa: FBT001
    screenshot_scale: int | None,
    screenshot_window_size: str | None,
) -> None:
    """Save a screenshot of the plotter scene.

    Parameters
    ----------
    plotter : pyvista_wasm.Plotter
        The plotter to capture.
    screenshot : Path
        Output file path.
    screenshot_transparent : bool
        Whether to use a transparent background.
    screenshot_scale : int or None
        Resolution scale factor.
    screenshot_window_size : str or None
        Window size as ``'width,height'``.

    """
    window_size = None
    if screenshot_window_size is not None:
        window_size = _parse_window_size(screenshot_window_size)

    plotter.screenshot(
        filename=screenshot,
        transparent_background=screenshot_transparent or None,
        return_img=False,
        window_size=window_size,
        scale=screenshot_scale,
    )
    logger.info("Screenshot saved to: %s", screenshot)


@app.command()
def plot(  # noqa: PLR0913
    files: Annotated[
        list[Path] | None,
        typer.Argument(
            help="Mesh file(s) to plot. Supported formats: .vtk (ASCII), .ply (ASCII), .obj. "
            "Optional when --load-pickle is provided.",
            metavar="FILE",
        ),
    ] = None,
    color: Annotated[
        str | None,
        typer.Option(
            help="Mesh colour applied to all files (e.g. ``red``, ``#ff0000``).",
            metavar="COLOR",
        ),
    ] = None,
    background: Annotated[
        str | None,
        typer.Option(
            help="Background colour (e.g. ``white``, ``black``). Default: renderer default.",
            metavar="COLOR",
        ),
    ] = None,
    opacity: Annotated[
        float,
        typer.Option(
            help="Mesh opacity in the range [0, 1]. Default: 1.0.",
            metavar="FLOAT",
        ),
    ] = 1.0,
    pickle: Annotated[
        Path | None,
        typer.Option(
            help="Save the Plotter object to a pickle file for later reuse.",
            metavar="PATH",
        ),
    ] = None,
    load_pickle: Annotated[
        Path | None,
        typer.Option(
            help="Load a pickled Plotter object from file instead of creating a new one. "
            "WARNING: Only load pickle files from trusted sources.",
            metavar="PATH",
        ),
    ] = None,
    screenshot: Annotated[
        Path | None,
        typer.Option(
            help="Save a screenshot to the specified file (PNG/JPEG). "
            "When provided, the browser window will not open.",
            metavar="PATH",
        ),
    ] = None,
    screenshot_transparent: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            help="Use transparent background for screenshot. Default: False.",
        ),
    ] = False,
    screenshot_scale: Annotated[
        int | None,
        typer.Option(
            help="Scale factor for screenshot resolution (e.g. 2 for double resolution).",
            metavar="INT",
        ),
    ] = None,
    screenshot_window_size: Annotated[
        str | None,
        typer.Option(
            help="Window size for screenshot as 'width,height' (e.g. '1920,1080').",
            metavar="SIZE",
        ),
    ] = None,
    azimuth: Annotated[
        float | None,
        typer.Option(
            help="Rotate camera horizontally around the focal point by this many degrees.",
            metavar="DEGREES",
        ),
    ] = None,
    elevation: Annotated[
        float | None,
        typer.Option(
            help="Rotate camera vertically around the focal point by this many degrees.",
            metavar="DEGREES",
        ),
    ] = None,
    zoom: Annotated[
        float | None,
        typer.Option(
            help="Zoom factor relative to current distance (>1 zooms in, <1 zooms out).",
            metavar="FLOAT",
        ),
    ] = None,
    roll: Annotated[
        float | None,
        typer.Option(
            help="Roll camera around its view axis by this many degrees.",
            metavar="DEGREES",
        ),
    ] = None,
) -> None:
    """Plot one or more mesh files in the browser.

    Open one or more mesh files (.vtk, .ply, .obj) and render them
    in the default web browser using VTK.wasm. Alternatively, load a
    previously saved Plotter object from a pickle file.

    If ``--screenshot`` is provided, a screenshot will be saved to the
    specified file instead of opening the browser window.
    """
    plotter = _build_plotter(files, color, background, opacity, load_pickle)

    if any(opt is not None for opt in (azimuth, elevation, zoom, roll)):
        _apply_camera_movement(plotter, azimuth, elevation, zoom, roll)

    if pickle is not None:
        _save_pickle(plotter, pickle)

    if screenshot is not None:
        _take_screenshot(
            plotter,
            screenshot,
            screenshot_transparent,
            screenshot_scale,
            screenshot_window_size,
        )
    else:
        plotter.show()


@app.command()
def info() -> None:
    """Show pyvista-wasm version and environment information.

    Print the pyvista-wasm version and basic Python environment details.
    """
    import pyvista_wasm as pv  # noqa: PLC0415

    logger.info("pyvista-wasm : %s", pv.__version__)
    logger.info("Python     : %s", sys.version)
    logger.info("Platform   : %s", platform.platform())


@app.command(name="capture-preview")
def capture_preview(
    output: Annotated[
        Path,
        typer.Option(
            help="Output path for the GIF. Default: assets/preview.gif.",
            metavar="PATH",
        ),
    ] = Path("assets/preview.gif"),
    url: Annotated[
        str,
        typer.Option(
            help="URL of the JupyterLite demo.",
            metavar="URL",
        ),
    ] = "https://pyvista-js.readthedocs.io/en/latest/lite/lab/index.html",
    fps: Annotated[
        int,
        typer.Option(
            help="Frames per second for the GIF. Default: 2.",
            metavar="INT",
        ),
    ] = 2,
    rotate: Annotated[
        bool | None,
        typer.Option(
            help="Rotate the 3D model by mouse drag while capturing screenshots. "
            "Will become the default in a future version.",
        ),
    ] = None,
) -> None:
    """Capture a preview GIF of the JupyterLite demo.

    Automate capturing a preview GIF showing pyvista-wasm rendering in JupyterLite.
    Requires: playwright, imageio[ffmpeg], pillow.
    """
    import tempfile  # noqa: PLC0415
    import warnings  # noqa: PLC0415

    if rotate is None:
        warnings.warn(
            "The default behavior of 'capture-preview' will change in a future "
            "version to rotate the 3D model during capture. "
            "Pass '--rotate' to enable the new behavior now, or "
            "'--no-rotate' to silence this warning and keep the current behavior.",
            DeprecationWarning,
            stacklevel=1,
        )
        rotate = False

    output_path = output

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        screenshots_dir = _capture_screenshots(tmp_dir, url, rotate=rotate)

        screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshot_files:
            logger.error("No screenshots were captured")
            sys.exit(1)

        if not _create_gif(screenshots_dir, output_path, fps=fps):
            logger.error("Failed to create GIF")
            sys.exit(1)

    logger.info("Preview GIF saved to: %s", output_path)


@app.command(name="capture-marimo-preview")
def capture_marimo_preview(
    output: Annotated[
        Path,
        typer.Option(
            help="Output path for the GIF. Default: assets/marimo-preview.gif.",
            metavar="PATH",
        ),
    ] = Path("assets/marimo-preview.gif"),
    url: Annotated[
        str,
        typer.Option(
            help="URL of the marimo demo.",
            metavar="URL",
        ),
    ] = "https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HhCkrLqRGr4mzgwIpn-VwiQTeLSnJW1uZC8AA9EcAs8G1iA+sbmuCubsDubbs3t-uMhlY0KMPHJ3rd7j8ttM4p8IDAyFBxFsOAAFCzwxFeHYIe4MZjgz73DjkCBUAgYxCUABGGgIBDs2NhGIRxA4VMoahsdDaeNqAThrKgHG5ZOxGGAY0wBBueGwTGYLGwSEy2BYvjiAKgdOxQA",
    fps: Annotated[
        int,
        typer.Option(
            help="Frames per second for the GIF. Default: 2.",
            metavar="INT",
        ),
    ] = 2,
    rotate: Annotated[
        bool | None,
        typer.Option(
            help="Rotate the 3D model by mouse drag while capturing screenshots. Default: True.",
        ),
    ] = None,
) -> None:
    """Capture a preview GIF of the marimo demo.

    Automate capturing a preview GIF showing pyvista-wasm rendering in marimo.
    Requires: playwright, imageio[ffmpeg], pillow.
    """
    import tempfile  # noqa: PLC0415

    if rotate is None:
        rotate = True

    output_path = output

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        screenshots_dir = _capture_marimo_screenshots(tmp_dir, url, rotate=rotate)

        screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshot_files:
            logger.error("No screenshots were captured")
            sys.exit(1)

        if not _create_gif(screenshots_dir, output_path, fps=fps):
            logger.error("Failed to create GIF")
            sys.exit(1)

    logger.info("marimo preview GIF saved to: %s", output_path)


@app.command(name="capture-stlite-preview")
def capture_stlite_preview(
    output: Annotated[
        Path,
        typer.Option(
            help="Output path for the GIF. Default: assets/stlite-preview.gif.",
            metavar="PATH",
        ),
    ] = Path("assets/stlite-preview.gif"),
    url: Annotated[
        str,
        typer.Option(
            help="URL of the stlite demo.",
            metavar="URL",
        ),
    ] = "https://share.stlite.net/#!CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt",
    fps: Annotated[
        int,
        typer.Option(
            help="Frames per second for the GIF. Default: 2.",
            metavar="INT",
        ),
    ] = 2,
    rotate: Annotated[
        bool | None,
        typer.Option(
            help="Rotate the 3D model by mouse drag while capturing screenshots. Default: True.",
        ),
    ] = None,
) -> None:
    """Capture a preview GIF of the stlite demo.

    Automate capturing a preview GIF showing pyvista-wasm rendering in stlite.
    Requires: playwright, imageio[ffmpeg], pillow.
    """
    import tempfile  # noqa: PLC0415

    if rotate is None:
        rotate = True

    output_path = output

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        screenshots_dir = _capture_stlite_screenshots(tmp_dir, url, rotate=rotate)

        screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshot_files:
            logger.error("No screenshots were captured")
            sys.exit(1)

        if not _create_gif(screenshots_dir, output_path, fps=fps):
            logger.error("Failed to create GIF")
            sys.exit(1)

    logger.info("stlite preview GIF saved to: %s", output_path)


def cli_main(argv: Sequence[str] | None = None) -> None:
    """Entry point for the ``pyvista-wasm`` command-line interface.

    Parameters
    ----------
    argv : sequence of str, optional
        Argument list to parse. Defaults to ``sys.argv[1:]``.

    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # Use standalone_mode=False to prevent sys.exit(0) in tests
    app(argv, standalone_mode=False)
