"""Playwright-based screenshot and GIF capture helpers for pyvista-wasm demos."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


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

        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2
        drag_distance = box["width"] / 3

        page.mouse.move(center_x - drag_distance / 2, center_y)
        page.mouse.down()
        page.mouse.move(center_x + drag_distance / 2, center_y, steps=20)
        page.mouse.up()

        logger.info("Performed mouse drag rotation on canvas")
    except Exception:  # noqa: BLE001
        logger.warning("Failed to perform mouse drag rotation", exc_info=True)


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
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        _frame, canvas = _find_canvas_in_frames(page)
        if canvas is not None:
            logger.info("Found canvas element in iframe")
            return
        page.wait_for_timeout(2000)

    msg = f"Canvas element not found in any frame within {timeout} seconds"
    raise TimeoutError(msg)


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

    import numpy as np  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415

    logger.info("Found %d screenshots", len(screenshot_files))
    raw_images = [iio.imread(f) for f in screenshot_files]

    target_size = (raw_images[0].shape[1], raw_images[0].shape[0])
    images = []
    for img in raw_images:
        pil_img = Image.fromarray(img).convert("RGB")
        if pil_img.size != target_size:
            pil_img = pil_img.resize(target_size, Image.LANCZOS)
        images.append(np.array(pil_img))

    target_shape = images[0].shape[:2]
    if any(img.shape[:2] != target_shape for img in images):
        resized = []
        for img in images:
            pil_img = Image.fromarray(img)
            pil_img = pil_img.resize(
                (target_shape[1], target_shape[0]),
                Image.LANCZOS,
            )
            resized.append(np.array(pil_img))
        images = resized

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
                page.screenshot(path=str(screenshots_dir / "screenshot_02.png"))
                page.wait_for_timeout(300)

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
                page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
                page.wait_for_timeout(300)

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


def _capture_marimo_screenshots(output_dir: Path, demo_url: str, *, rotate: bool = True) -> Path:
    """Capture screenshots from the marimo demo using Playwright.

    Parameters
    ----------
    output_dir : Path
        Directory to save temporary screenshots.
    demo_url : str
        URL of the marimo demo.
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

    logger.info("Capturing marimo demo from: %s", demo_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()

        try:
            logger.info("Navigating to marimo demo...")
            page.goto(demo_url, wait_until="networkidle", timeout=120000)

            logger.info("Waiting for marimo to load and install dependencies...")
            page.wait_for_timeout(60000)

            logger.info("Waiting for 3D rendering to appear in iframes...")
            _wait_for_canvas_in_frames(page)

            page.wait_for_timeout(5000)

            if rotate:
                logger.info("Capturing rendering screenshots with rotation...")
                page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
                page.wait_for_timeout(300)

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
            logger.exception("Error during marimo demo capture")
            with contextlib.suppress(Exception):
                page.screenshot(path=str(screenshots_dir / "error_screenshot.png"))
        finally:
            context.close()
            browser.close()

    return screenshots_dir
