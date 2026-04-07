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


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


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


def _open_notebook(page, screenshots_dir: Path) -> bool:  # noqa: ANN001
    """Find and open the demo notebook in the JupyterLite file browser.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.
    screenshots_dir : Path
        Directory to save fallback screenshots.

    Returns
    -------
    bool
        ``True`` if the notebook was opened successfully.

    """
    notebook_selectors = [
        "text=intro.ipynb",
        "[title*='intro']",
        ".jp-DirListing-itemText:has-text('intro')",
    ]

    for selector in notebook_selectors:
        element = page.query_selector(selector)
        if element is not None:
            element.dblclick()
            logger.info("Double-clicked on notebook using selector: %s", selector)
            return True

    logger.warning("Could not find notebook, taking screenshot of main page")
    page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
    return False


def _run_notebook_cells(page) -> None:  # noqa: ANN001
    """Execute all cells in the currently open notebook.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.

    """
    page.wait_for_selector(".jp-Cell", timeout=10000)
    page.click(".jp-Cell")
    page.wait_for_timeout(1000)

    try:
        page.click("text=Run", timeout=5000)
        page.wait_for_timeout(500)
        page.click("text=Run All Cells", timeout=5000)
        logger.info("Clicked 'Run All Cells' from menu")
    except Exception:  # noqa: BLE001
        logger.info("Could not use menu, trying keyboard shortcuts")
        page.keyboard.press("Control+Shift+Enter")
        page.wait_for_timeout(1000)
        page.keyboard.press("Shift+Enter")
        page.wait_for_timeout(1000)
        page.keyboard.press("Shift+Enter")


def _find_canvas_in_frames(page) -> tuple:  # noqa: ANN001
    """Find a canvas element by searching through all frames (including nested iframes).

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.

    Returns
    -------
    tuple
        A (frame, element_handle) pair, or (None, None) if not found.

    """
    for frame in page.frames:
        try:
            canvas = frame.query_selector("canvas")
            if canvas is not None:
                return frame, canvas
        except Exception:  # noqa: BLE001
            logger.debug("Failed to query canvas in frame", exc_info=True)
            continue
    return None, None


def _rotate_canvas_with_mouse(page) -> None:  # noqa: ANN001
    """Rotate the 3D model by dragging the mouse across the canvas.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.

    """
    try:
        _frame, canvas = _find_canvas_in_frames(page)
        if canvas is None:
            logger.warning("Canvas element not found in any frame, skipping rotation")
            return

        box = canvas.bounding_box()
        if box is None:
            logger.warning("Canvas bounding box not available, skipping rotation")
            return

        # Calculate center and drag path
        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2
        drag_distance = box["width"] / 3  # Drag 1/3 of canvas width

        # Perform mouse drag: click + move to simulate rotation
        page.mouse.move(center_x - drag_distance / 2, center_y)
        page.mouse.down()
        page.mouse.move(center_x + drag_distance / 2, center_y, steps=20)
        page.mouse.up()

        logger.info("Performed mouse drag rotation on canvas")
    except Exception:  # noqa: BLE001
        logger.warning("Failed to perform mouse drag rotation", exc_info=True)


def _capture_screenshots(output_dir: Path, demo_url: str, *, rotate: bool = False) -> Path:
    """Capture screenshots from the JupyterLite demo using Playwright.

    Parameters
    ----------
    output_dir : Path
        Directory to save temporary screenshots.
    demo_url : str
        URL of the JupyterLite demo.
    rotate : bool
        If ``True``, rotate the 3D model by mouse drag between
        screenshots. Default: ``False``.

    Returns
    -------
    Path
        Path to the directory containing screenshots.

    """
    import contextlib  # noqa: PLC0415

    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Capturing demo from: %s", demo_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()

        try:
            logger.info("Navigating to JupyterLite demo...")
            page.goto(demo_url, wait_until="domcontentloaded", timeout=60000)

            logger.info("Waiting for JupyterLite to load...")
            page.wait_for_timeout(15000)

            logger.info("Looking for intro.ipynb...")
            page.wait_for_selector(".jp-DirListing-content", timeout=60000)

            if not _open_notebook(page, screenshots_dir):
                return screenshots_dir

            logger.info("Waiting for notebook to open...")
            page.wait_for_timeout(5000)
            page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))

            logger.info("Attempting to run notebook cells...")
            _run_notebook_cells(page)

            logger.info("Waiting for 3D rendering to appear...")
            page.wait_for_timeout(15000)

            if rotate:
                logger.info("Capturing rendering screenshots with rotation...")
                # Capture first screenshot at initial position
                page.screenshot(path=str(screenshots_dir / "screenshot_02.png"))
                page.wait_for_timeout(300)

                # Capture remaining screenshots while rotating
                for i in range(3, 15):
                    _rotate_canvas_with_mouse(page)
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(300)
            else:
                logger.info("Capturing rendering screenshots...")
                for i in range(2, 15):
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(500)

            logger.info("Captured 14 screenshots successfully")

        except Exception:
            logger.exception("Error during demo capture")
            with contextlib.suppress(Exception):
                page.screenshot(path=str(screenshots_dir / "error_screenshot.png"))
        finally:
            context.close()
            browser.close()

    return screenshots_dir


def _create_gif(screenshots_dir: Path, output_path: Path, fps: int = 2) -> bool:
    """Create a GIF from a directory of screenshot PNGs.

    Parameters
    ----------
    screenshots_dir : Path
        Directory containing ``screenshot_*.png`` files.
    output_path : Path
        Destination path for the GIF.
    fps : int
        Frames per second. Default: 2.

    Returns
    -------
    bool
        ``True`` if the GIF was created successfully.

    """
    import imageio.v3 as iio  # noqa: PLC0415

    screenshot_files = sorted(screenshots_dir.glob("screenshot_*.png"))
    if not screenshot_files:
        logger.error("No screenshots found!")
        return False

    logger.info("Found %d screenshots", len(screenshot_files))
    images = [iio.imread(f) for f in screenshot_files]

    duration_ms = int(1000 / fps)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Creating GIF at %s (%d fps)...", output_path, fps)
    iio.imwrite(output_path, images, duration=duration_ms, loop=0)

    logger.info(
        "GIF created: %s (%.1f KB, %d frames)",
        output_path,
        output_path.stat().st_size / 1024,
        len(images),
    )
    return True


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


def _wait_for_canvas_in_frames(page, timeout: int = 120) -> None:  # noqa: ANN001
    """Poll all frames until a canvas element appears or *timeout* seconds elapse.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.
    timeout : int
        Maximum seconds to wait.  Default: 120.

    Raises
    ------
    TimeoutError
        If no canvas is found within *timeout* seconds.

    """
    import time  # noqa: PLC0415

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        _frame, canvas = _find_canvas_in_frames(page)
        if canvas is not None:
            logger.info("Found canvas element in iframe")
            return
        page.wait_for_timeout(2000)

    msg = f"Canvas element not found in any frame within {timeout} seconds"
    raise TimeoutError(msg)


def _capture_stlite_screenshots(output_dir: Path, demo_url: str, *, rotate: bool = True) -> Path:
    """Capture screenshots from the stlite demo using Playwright.

    Parameters
    ----------
    output_dir : Path
        Directory to save temporary screenshots.
    demo_url : str
        URL of the stlite demo.
    rotate : bool
        If ``True``, rotate the 3D model by mouse drag between
        screenshots. Default: ``True``.

    Returns
    -------
    Path
        Path to the directory containing screenshots.

    """
    import contextlib  # noqa: PLC0415

    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Capturing stlite demo from: %s", demo_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()

        try:
            logger.info("Navigating to stlite demo...")
            page.goto(demo_url, wait_until="networkidle", timeout=120000)

            logger.info("Waiting for stlite to load and install dependencies...")
            # Wait for stlite to initialize Python and install pyvista-wasm
            page.wait_for_timeout(60000)

            logger.info("Waiting for 3D rendering to appear in iframes...")
            # stlite renders the Streamlit app in iframes, and
            # components.html() creates another nested iframe for the
            # Three.js canvas.  page.wait_for_selector only searches the
            # top-level document, so we poll all frames instead.
            _wait_for_canvas_in_frames(page)

            page.wait_for_timeout(5000)

            if rotate:
                logger.info("Capturing rendering screenshots with rotation...")
                # Capture first screenshot at initial position
                page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
                page.wait_for_timeout(300)

                # Capture remaining screenshots while rotating
                for i in range(2, 15):
                    _rotate_canvas_with_mouse(page)
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(300)
            else:
                logger.info("Capturing rendering screenshots...")
                for i in range(1, 15):
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(500)

            logger.info("Captured 14 screenshots successfully")

        except Exception:
            logger.exception("Error during stlite demo capture")
            with contextlib.suppress(Exception):
                page.screenshot(path=str(screenshots_dir / "error_screenshot.png"))
        finally:
            context.close()
            browser.close()

    return screenshots_dir


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


# ---------------------------------------------------------------------------
# CLI entry point wrapper for backwards compatibility
# ---------------------------------------------------------------------------


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
