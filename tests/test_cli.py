"""Tests for the pyvista-wasm CLI."""

import logging
import pickle
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import pyvista_wasm as pv
from pyvista_wasm._cli import (
    _apply_camera_movement,
    _capture_stlite_screenshots,
    _find_canvas_in_frames,
    _rotate_canvas_with_mouse,
    _wait_for_canvas_in_frames,
    capture_preview,
    capture_stlite_preview,
    cli_main,
)

DATA_DIR = Path(__file__).parent / "data"
VTK_FILE = DATA_DIR / "triangle.vtk"
PLY_FILE = DATA_DIR / "triangle.ply"
OBJ_FILE = DATA_DIR / "triangle.obj"


def test_info_logs_version(caplog) -> None:
    """``pyvista-wasm info`` logs version, Python, and platform lines."""
    with caplog.at_level(logging.INFO, logger="pyvista_wasm._cli"):
        cli_main(["info"])

    messages = "\n".join(caplog.messages)
    assert "pyvista-wasm" in messages
    assert "Python" in messages
    assert "Platform" in messages


def test_plot_vtk() -> None:
    """``pyvista-wasm plot`` runs without error on a .vtk file."""
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", str(VTK_FILE)])


def test_plot_ply() -> None:
    """``pyvista-wasm plot`` runs without error on a .ply file."""
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", str(PLY_FILE)])


def test_plot_obj() -> None:
    """``pyvista-wasm plot`` runs without error on a .obj file."""
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", str(OBJ_FILE)])


def test_plot_with_color_and_background() -> None:
    """``--color`` and ``--background`` options are forwarded to the plotter."""
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", str(VTK_FILE), "--color", "red", "--background", "white"])


def test_plot_missing_file_exits() -> None:
    """``pyvista-wasm plot`` exits with code 1 when the file does not exist."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", "nonexistent.vtk"])
    assert exc_info.value.code == 1


def test_plot_unsupported_extension_exits(tmp_path) -> None:
    """``pyvista-wasm plot`` exits with code 1 for unsupported file formats."""
    bad_file = tmp_path / "mesh.stl"
    bad_file.write_text("solid\nendsolid\n")
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", str(bad_file)])
    assert exc_info.value.code == 1


def test_plot_with_pickle_option(tmp_path) -> None:
    """``--pickle`` option saves the Plotter object to a file."""
    pickle_file = tmp_path / "plotter.pkl"
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", str(VTK_FILE), "--pickle", str(pickle_file)])

    # Verify pickle file was created
    assert pickle_file.exists()

    # Load and verify the plotter
    with pickle_file.open("rb") as f:
        plotter = pickle.load(f)  # noqa: S301

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["mesh"].n_points == 3


def test_plot_with_pickle_and_options(tmp_path) -> None:
    """``--pickle`` option preserves color, background, and opacity settings."""
    pickle_file = tmp_path / "plotter_with_options.pkl"
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                "--color",
                "red",
                "--background",
                "white",
                "--opacity",
                "0.5",
                "--pickle",
                str(pickle_file),
            ],
        )

    # Load and verify the plotter
    with pickle_file.open("rb") as f:
        plotter = pickle.load(f)  # noqa: S301

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[0]["opacity"] == 0.5
    assert plotter.background_color == (1.0, 1.0, 1.0)  # white


def test_plot_with_pickle_multiple_meshes(tmp_path) -> None:
    """``--pickle`` option works with multiple mesh files."""
    pickle_file = tmp_path / "plotter_multi.pkl"
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                str(PLY_FILE),
                "--pickle",
                str(pickle_file),
            ],
        )

    # Load and verify the plotter
    with pickle_file.open("rb") as f:
        plotter = pickle.load(f)  # noqa: S301

    assert len(plotter.actors) == 2


def test_find_canvas_in_frames_finds_canvas() -> None:
    """``_find_canvas_in_frames`` returns frame and canvas from nested iframes."""
    canvas = MagicMock()
    frame = MagicMock()
    frame.query_selector.return_value = canvas
    page = MagicMock()
    page.frames = [frame]

    found_frame, found_canvas = _find_canvas_in_frames(page)

    assert found_frame is frame
    assert found_canvas is canvas


def test_find_canvas_in_frames_returns_none_when_no_canvas() -> None:
    """``_find_canvas_in_frames`` returns (None, None) when no canvas exists."""
    frame = MagicMock()
    frame.query_selector.return_value = None
    page = MagicMock()
    page.frames = [frame]

    found_frame, found_canvas = _find_canvas_in_frames(page)

    assert found_frame is None
    assert found_canvas is None


def test_find_canvas_in_frames_skips_frames_that_raise() -> None:
    """``_find_canvas_in_frames`` skips frames that raise and continues searching."""
    bad_frame = MagicMock()
    bad_frame.query_selector.side_effect = Exception("detached")
    canvas = MagicMock()
    good_frame = MagicMock()
    good_frame.query_selector.return_value = canvas
    page = MagicMock()
    page.frames = [bad_frame, good_frame]

    found_frame, found_canvas = _find_canvas_in_frames(page)

    assert found_frame is good_frame
    assert found_canvas is canvas


def test_wait_for_canvas_in_frames_succeeds() -> None:
    """``_wait_for_canvas_in_frames`` returns when canvas is found."""
    canvas = MagicMock()
    frame = MagicMock()
    frame.query_selector.return_value = canvas
    page = MagicMock()
    page.frames = [frame]

    # Should not raise
    _wait_for_canvas_in_frames(page, timeout=5)


def test_wait_for_canvas_in_frames_raises_on_timeout() -> None:
    """``_wait_for_canvas_in_frames`` raises TimeoutError when canvas is not found."""
    frame = MagicMock()
    frame.query_selector.return_value = None
    page = MagicMock()
    page.frames = [frame]

    with pytest.raises(TimeoutError, match="Canvas element not found"):
        _wait_for_canvas_in_frames(page, timeout=0)


def test_rotate_canvas_with_mouse_performs_drag() -> None:
    """``_rotate_canvas_with_mouse`` performs mouse drag on canvas."""
    canvas = MagicMock()
    canvas.bounding_box.return_value = {"x": 100, "y": 100, "width": 600, "height": 400}
    frame = MagicMock()
    frame.query_selector.return_value = canvas
    page = MagicMock()
    page.frames = [frame]

    _rotate_canvas_with_mouse(page)

    canvas.bounding_box.assert_called_once()
    page.mouse.move.assert_called()
    page.mouse.down.assert_called_once()
    page.mouse.up.assert_called_once()


def test_rotate_canvas_with_mouse_handles_missing_canvas() -> None:
    """``_rotate_canvas_with_mouse`` handles gracefully when canvas is not found."""
    frame = MagicMock()
    frame.query_selector.return_value = None
    page = MagicMock()
    page.frames = [frame]

    _rotate_canvas_with_mouse(page)

    page.mouse.move.assert_not_called()


def test_rotate_canvas_with_mouse_handles_missing_bounding_box() -> None:
    """``_rotate_canvas_with_mouse`` handles gracefully when bounding box is unavailable."""
    canvas = MagicMock()
    canvas.bounding_box.return_value = None
    frame = MagicMock()
    frame.query_selector.return_value = canvas
    page = MagicMock()
    page.frames = [frame]

    _rotate_canvas_with_mouse(page)

    canvas.bounding_box.assert_called_once()
    page.mouse.move.assert_not_called()


def test_capture_preview_no_rotate_emits_deprecation_warning(tmp_path) -> None:
    """``capture-preview`` without ``--rotate`` emits a DeprecationWarning."""
    with (
        warnings.catch_warnings(record=True) as w,
        patch("pyvista_wasm._cli._capture_screenshots") as mock_capture,
        patch("pyvista_wasm._cli._create_gif", return_value=True),
    ):
        warnings.simplefilter("always")
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_preview(output=tmp_path / "out.gif", url="http://example.com")

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) == 1
        assert "--rotate" in str(deprecation_warnings[0].message)
        assert mock_capture.call_args.kwargs["rotate"] is False


def test_capture_preview_with_rotate_no_warning(tmp_path) -> None:
    """``capture-preview --rotate`` does not emit a DeprecationWarning."""
    with (
        warnings.catch_warnings(record=True) as w,
        patch("pyvista_wasm._cli._capture_screenshots") as mock_capture,
        patch("pyvista_wasm._cli._create_gif", return_value=True),
    ):
        warnings.simplefilter("always")
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=True)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) == 0
        assert mock_capture.call_args.kwargs["rotate"] is True


def test_capture_preview_with_no_rotate_no_warning(tmp_path) -> None:
    """``capture-preview --no-rotate`` does not emit a DeprecationWarning."""
    with (
        warnings.catch_warnings(record=True) as w,
        patch("pyvista_wasm._cli._capture_screenshots") as mock_capture,
        patch("pyvista_wasm._cli._create_gif", return_value=True),
    ):
        warnings.simplefilter("always")
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=False)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) == 0
        assert mock_capture.call_args.kwargs["rotate"] is False


def test_plot_load_pickle_with_plotter(tmp_path) -> None:
    """``pyvista-wasm plot --load-pickle`` loads and displays a pickled Plotter."""
    # Create a simple plotter and pickle it
    plotter = pv.Plotter()
    plotter._background_color = (0.5, 0.5, 0.5)  # Set background directly
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    # Test loading the pickle file
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", "--load-pickle", str(pickle_file)])


def test_plot_load_pickle_missing_file() -> None:
    """``pyvista-wasm plot --load-pickle`` exits when pickle file doesn't exist."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", "--load-pickle", "nonexistent.pkl"])
    assert exc_info.value.code == 1


def test_plot_load_pickle_invalid_content(tmp_path) -> None:
    """``pyvista-wasm plot --load-pickle`` exits when pickle contains non-Plotter object."""
    # Create a pickle file with a non-Plotter object
    pickle_file = tmp_path / "invalid.pkl"
    with pickle_file.open("wb") as f:
        pickle.dump({"not": "a plotter"}, f)

    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", "--load-pickle", str(pickle_file)])
    assert exc_info.value.code == 1


def test_plot_load_pickle_with_additional_files(tmp_path) -> None:
    """``pyvista-wasm plot --load-pickle`` can add additional mesh files to loaded plotter."""
    # Create a simple plotter and pickle it
    plotter = pv.Plotter()
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    # Test loading the pickle file with additional mesh
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", "--load-pickle", str(pickle_file), str(VTK_FILE)])


def test_plot_no_files_and_no_pickle_exits() -> None:
    """``pyvista-wasm plot`` exits when neither files nor --load-pickle are provided."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot"])
    assert exc_info.value.code == 1


def test_plot_load_pickle_with_background_override(tmp_path) -> None:
    """``pyvista-wasm plot --load-pickle --background`` overrides loaded plotter background."""
    # Create a plotter with one background color
    plotter = pv.Plotter()
    plotter.background_color = "black"
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    # Load with different background color
    with patch("pyvista_wasm.Plotter.show") as mock_show:
        cli_main(["plot", "--load-pickle", str(pickle_file), "--background", "white"])
        mock_show.assert_called_once()


def test_plot_with_screenshot(tmp_path) -> None:
    """``pyvista-wasm plot --screenshot`` saves screenshot and doesn't open browser."""
    screenshot_file = tmp_path / "output.png"
    with (
        patch("pyvista_wasm.Plotter.screenshot") as mock_screenshot,
        patch(
            "pyvista_wasm.Plotter.show",
        ) as mock_show,
    ):
        cli_main(["plot", str(VTK_FILE), "--screenshot", str(screenshot_file)])

        # Verify screenshot was called with correct parameters
        mock_screenshot.assert_called_once_with(
            filename=screenshot_file,
            transparent_background=None,
            return_img=False,
            window_size=None,
            scale=None,
        )
        # Verify show was NOT called when screenshot is provided
        mock_show.assert_not_called()


def test_plot_with_screenshot_transparent(tmp_path) -> None:
    """``pyvista-wasm plot --screenshot --screenshot-transparent`` enables transparency."""
    screenshot_file = tmp_path / "transparent.png"
    with (
        patch("pyvista_wasm.Plotter.screenshot") as mock_screenshot,
        patch(
            "pyvista_wasm.Plotter.show",
        ),
    ):
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                "--screenshot",
                str(screenshot_file),
                "--screenshot-transparent",
            ],
        )

        # Verify screenshot was called with transparent_background=True
        mock_screenshot.assert_called_once_with(
            filename=screenshot_file,
            transparent_background=True,
            return_img=False,
            window_size=None,
            scale=None,
        )


def test_plot_with_screenshot_scale(tmp_path) -> None:
    """``pyvista-wasm plot --screenshot --screenshot-scale`` sets scale factor."""
    screenshot_file = tmp_path / "scaled.png"
    with (
        patch("pyvista_wasm.Plotter.screenshot") as mock_screenshot,
        patch(
            "pyvista_wasm.Plotter.show",
        ),
    ):
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                "--screenshot",
                str(screenshot_file),
                "--screenshot-scale",
                "2",
            ],
        )

        # Verify screenshot was called with scale=2
        mock_screenshot.assert_called_once_with(
            filename=screenshot_file,
            transparent_background=None,
            return_img=False,
            window_size=None,
            scale=2,
        )


def test_plot_with_screenshot_window_size(tmp_path) -> None:
    """``pyvista-wasm plot --screenshot --screenshot-window-size`` sets window dimensions."""
    screenshot_file = tmp_path / "custom_size.png"
    with (
        patch("pyvista_wasm.Plotter.screenshot") as mock_screenshot,
        patch(
            "pyvista_wasm.Plotter.show",
        ),
    ):
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                "--screenshot",
                str(screenshot_file),
                "--screenshot-window-size",
                "1920,1080",
            ],
        )

        # Verify screenshot was called with correct window_size tuple
        mock_screenshot.assert_called_once_with(
            filename=screenshot_file,
            transparent_background=None,
            return_img=False,
            window_size=(1920, 1080),
            scale=None,
        )


def test_plot_with_screenshot_all_options(tmp_path) -> None:
    """``pyvista-wasm plot --screenshot`` with all screenshot options combined."""
    screenshot_file = tmp_path / "full_options.png"
    with (
        patch("pyvista_wasm.Plotter.screenshot") as mock_screenshot,
        patch(
            "pyvista_wasm.Plotter.show",
        ),
    ):
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                "--screenshot",
                str(screenshot_file),
                "--screenshot-transparent",
                "--screenshot-scale",
                "3",
                "--screenshot-window-size",
                "2560,1440",
            ],
        )

        # Verify all options were passed correctly
        mock_screenshot.assert_called_once_with(
            filename=screenshot_file,
            transparent_background=True,
            return_img=False,
            window_size=(2560, 1440),
            scale=3,
        )


def test_plot_with_screenshot_invalid_window_size(tmp_path) -> None:
    """``pyvista-wasm plot --screenshot-window-size`` exits on invalid format."""
    screenshot_file = tmp_path / "output.png"
    with pytest.raises(SystemExit) as exc_info:
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                "--screenshot",
                str(screenshot_file),
                "--screenshot-window-size",
                "invalid",
            ],
        )
    assert exc_info.value.code == 1


def test_plot_without_screenshot_still_shows() -> None:
    """``pyvista-wasm plot`` without --screenshot calls show() normally."""
    with (
        patch("pyvista_wasm.Plotter.show") as mock_show,
        patch(
            "pyvista_wasm.Plotter.screenshot",
        ) as mock_screenshot,
    ):
        cli_main(["plot", str(VTK_FILE)])

        # Verify show was called and screenshot was NOT called
        mock_show.assert_called_once()
        mock_screenshot.assert_not_called()


def test_capture_stlite_preview_with_rotate(tmp_path) -> None:
    """``capture-stlite-preview --rotate`` calls stlite capture with rotation."""
    with (
        patch("pyvista_wasm._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_wasm._cli._create_gif", return_value=True),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=True)

        assert mock_capture.call_args.kwargs["rotate"] is True


def test_capture_stlite_preview_with_no_rotate(tmp_path) -> None:
    """``capture-stlite-preview --no-rotate`` calls stlite capture without rotation."""
    with (
        patch("pyvista_wasm._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_wasm._cli._create_gif", return_value=True),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=False)

        assert mock_capture.call_args.kwargs["rotate"] is False


def _make_mock_playwright():
    """Create mock Playwright objects for testing screenshot capture."""
    mock_canvas = MagicMock()
    mock_canvas.bounding_box.return_value = {"x": 100, "y": 100, "width": 600, "height": 400}
    mock_frame = MagicMock()
    mock_frame.query_selector.return_value = mock_canvas
    mock_page = MagicMock()
    # page.frames returns all frames including nested iframes
    mock_page.frames = [mock_frame]
    mock_context = MagicMock()
    mock_context.new_page.return_value = mock_page
    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_pw = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_pw_cm = MagicMock()
    mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw)
    mock_pw_cm.__exit__ = MagicMock(return_value=False)
    return mock_pw_cm, mock_page, mock_context, mock_browser


def test_capture_stlite_screenshots_with_rotate(tmp_path) -> None:
    """_capture_stlite_screenshots creates screenshots with rotation."""
    mock_pw_cm, mock_page, mock_context, mock_browser = _make_mock_playwright()

    def fake_screenshot(path: str) -> None:
        Path(path).write_bytes(b"fake-png")

    mock_page.screenshot.side_effect = fake_screenshot

    with patch("playwright.sync_api.sync_playwright", return_value=mock_pw_cm):
        result = _capture_stlite_screenshots(tmp_path, "http://example.com", rotate=True)

    assert result == tmp_path / "screenshots"
    # 1 initial + 13 rotated = 14 screenshots
    assert mock_page.screenshot.call_count == 14
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()


def test_capture_stlite_screenshots_without_rotate(tmp_path) -> None:
    """_capture_stlite_screenshots creates screenshots without rotation."""
    mock_pw_cm, mock_page, mock_context, mock_browser = _make_mock_playwright()

    def fake_screenshot(path: str) -> None:
        Path(path).write_bytes(b"fake-png")

    mock_page.screenshot.side_effect = fake_screenshot

    with patch("playwright.sync_api.sync_playwright", return_value=mock_pw_cm):
        result = _capture_stlite_screenshots(tmp_path, "http://example.com", rotate=False)

    assert result == tmp_path / "screenshots"
    assert mock_page.screenshot.call_count == 14
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()


def test_capture_stlite_screenshots_handles_exception(tmp_path) -> None:
    """_capture_stlite_screenshots handles exceptions gracefully."""
    mock_pw_cm, mock_page, mock_context, mock_browser = _make_mock_playwright()
    mock_page.goto.side_effect = Exception("Connection refused")

    with patch("playwright.sync_api.sync_playwright", return_value=mock_pw_cm):
        result = _capture_stlite_screenshots(tmp_path, "http://example.com", rotate=True)

    assert result == tmp_path / "screenshots"
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()


def test_capture_stlite_preview_no_screenshots(tmp_path) -> None:
    """capture_stlite_preview exits when no screenshots are captured."""
    with patch("pyvista_wasm._cli._capture_stlite_screenshots") as mock_capture:
        mock_capture.return_value = tmp_path
        # No screenshot files created in tmp_path
        with pytest.raises(SystemExit, match="1"):
            capture_stlite_preview(
                output=tmp_path / "out.gif",
                url="http://example.com",
                rotate=True,
            )


def test_capture_stlite_preview_gif_creation_fails(tmp_path) -> None:
    """capture_stlite_preview exits when GIF creation fails."""
    with (
        patch("pyvista_wasm._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_wasm._cli._create_gif", return_value=False),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")
        with pytest.raises(SystemExit, match="1"):
            capture_stlite_preview(
                output=tmp_path / "out.gif",
                url="http://example.com",
                rotate=True,
            )


def test_capture_stlite_preview_rotate_default(tmp_path) -> None:
    """capture_stlite_preview defaults to rotate=True when None."""
    with (
        patch("pyvista_wasm._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_wasm._cli._create_gif", return_value=True),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com")

        assert mock_capture.call_args.kwargs["rotate"] is True


def _make_plotter_with_camera():
    """Create a Plotter with a known camera state for testing."""
    plotter = pv.Plotter()
    cam = pv.Camera(
        position=(0.0, 0.0, 5.0),
        focal_point=(0.0, 0.0, 0.0),
        view_up=(0.0, 1.0, 0.0),
    )
    plotter.camera = cam
    return plotter


def test_apply_camera_movement_azimuth() -> None:
    """Azimuth rotates the camera horizontally around the focal point."""
    plotter = _make_plotter_with_camera()
    _apply_camera_movement(plotter, azimuth=90.0, elevation=None, zoom=None, roll=None)

    pos = np.array(plotter.camera.position)
    # After 90-degree azimuth from (0,0,5), camera should move to approximately (5,0,0)
    # (rotating around up=(0,1,0) axis)
    np.testing.assert_allclose(pos, [5.0, 0.0, 0.0], atol=1e-10)
    # Focal point should remain unchanged
    np.testing.assert_allclose(plotter.camera.focal_point, (0.0, 0.0, 0.0), atol=1e-10)


def test_apply_camera_movement_elevation() -> None:
    """Elevation rotates the camera vertically around the focal point."""
    plotter = _make_plotter_with_camera()
    _apply_camera_movement(plotter, azimuth=None, elevation=90.0, zoom=None, roll=None)

    pos = np.array(plotter.camera.position)
    # After 90-degree elevation from (0,0,5), camera should move to approximately (0,-5,0)
    np.testing.assert_allclose(pos, [0.0, -5.0, 0.0], atol=1e-10)


def test_apply_camera_movement_zoom_in() -> None:
    """Zoom > 1 moves the camera closer to the focal point."""
    plotter = _make_plotter_with_camera()
    _apply_camera_movement(plotter, azimuth=None, elevation=None, zoom=2.0, roll=None)

    pos = np.array(plotter.camera.position)
    # Distance should be halved: 5/2 = 2.5
    np.testing.assert_allclose(pos, [0.0, 0.0, 2.5], atol=1e-10)


def test_apply_camera_movement_zoom_out() -> None:
    """Zoom < 1 moves the camera farther from the focal point."""
    plotter = _make_plotter_with_camera()
    _apply_camera_movement(plotter, azimuth=None, elevation=None, zoom=0.5, roll=None)

    pos = np.array(plotter.camera.position)
    # Distance should be doubled: 5/0.5 = 10
    np.testing.assert_allclose(pos, [0.0, 0.0, 10.0], atol=1e-10)


def test_apply_camera_movement_roll() -> None:
    """Roll rotates the up vector around the view axis."""
    plotter = _make_plotter_with_camera()
    _apply_camera_movement(plotter, azimuth=None, elevation=None, zoom=None, roll=90.0)

    up = np.array(plotter.camera.view_up)
    # After 90-degree roll, up=(0,1,0) rotates around forward=(0,0,-1) to (1,0,0)
    np.testing.assert_allclose(up, [1.0, 0.0, 0.0], atol=1e-10)
    # Position should be unchanged
    np.testing.assert_allclose(plotter.camera.position, (0.0, 0.0, 5.0), atol=1e-10)


def test_apply_camera_movement_combined() -> None:
    """Multiple camera movements are applied together."""
    plotter = _make_plotter_with_camera()
    _apply_camera_movement(plotter, azimuth=45.0, elevation=None, zoom=2.0, roll=None)

    pos = np.array(plotter.camera.position)
    # After 45-degree azimuth, distance=5, then zoom 2x -> distance=2.5
    dist = np.linalg.norm(pos)
    np.testing.assert_allclose(dist, 2.5, atol=1e-10)


def test_apply_camera_movement_no_camera() -> None:
    """Camera movement creates a default camera if none exists."""
    plotter = pv.Plotter()
    assert plotter.camera is None
    _apply_camera_movement(plotter, azimuth=45.0, elevation=None, zoom=None, roll=None)
    assert plotter.camera is not None


def test_apply_camera_movement_zero_zoom_exits() -> None:
    """Zoom of zero or negative exits with error."""
    plotter = _make_plotter_with_camera()
    with pytest.raises(SystemExit) as exc_info:
        _apply_camera_movement(plotter, azimuth=None, elevation=None, zoom=0.0, roll=None)
    assert exc_info.value.code == 1


def test_plot_load_pickle_with_azimuth(tmp_path) -> None:
    """``--azimuth`` option modifies camera after loading pickle."""
    plotter = pv.Plotter()
    cam = pv.Camera(position=(0.0, 0.0, 5.0), focal_point=(0.0, 0.0, 0.0))
    plotter.camera = cam
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", "--load-pickle", str(pickle_file), "--azimuth", "90"])


def test_plot_load_pickle_with_zoom(tmp_path) -> None:
    """``--zoom`` option modifies camera after loading pickle."""
    plotter = pv.Plotter()
    cam = pv.Camera(position=(0.0, 0.0, 5.0), focal_point=(0.0, 0.0, 0.0))
    plotter.camera = cam
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", "--load-pickle", str(pickle_file), "--zoom", "2.0"])


def test_plot_new_plotter_with_camera_movement() -> None:
    """Camera movement options work with new plotters (not just pickle)."""
    with patch("pyvista_wasm.Plotter.show"):
        cli_main(["plot", str(VTK_FILE), "--azimuth", "45", "--zoom", "1.5"])
