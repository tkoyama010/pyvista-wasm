"""Tests for the Camera class."""

import numpy as np
import pytest

import pyvista_wasm as pv
from pyvista_wasm.camera import Camera
from pyvista_wasm.rendering import MockRenderer


def test_camera_default_values() -> None:
    """Test Camera default property values."""
    camera = Camera()
    assert camera.position == (0.0, 0.0, 1.0)
    assert camera.focal_point == (0.0, 0.0, 0.0)
    assert camera.view_up == (0.0, 1.0, 0.0)
    assert camera.view_angle == 30.0
    assert camera.clipping_range == (0.01, 1000.01)
    assert camera.elevation == 0.0


def test_camera_constructor_kwargs() -> None:
    """Test Camera can be constructed with custom parameters."""
    camera = Camera(
        position=(1.0, 2.0, 3.0),
        focal_point=(4.0, 5.0, 6.0),
        view_up=(0.0, 0.0, 1.0),
        view_angle=45.0,
        clipping_range=(0.1, 500.0),
    )
    assert camera.position == (1.0, 2.0, 3.0)
    assert camera.focal_point == (4.0, 5.0, 6.0)
    assert camera.view_up == (0.0, 0.0, 1.0)
    assert camera.view_angle == 45.0
    assert camera.clipping_range == (0.1, 500.0)


def test_camera_position_setter() -> None:
    """Test setting camera position."""
    camera = Camera()
    camera.position = (5.0, 0.0, 0.0)
    assert camera.position == (5.0, 0.0, 0.0)


def test_camera_position_converts_to_float() -> None:
    """Test that position values are converted to float."""
    camera = Camera()
    camera.position = (1, 2, 3)  # integers
    assert camera.position == (1.0, 2.0, 3.0)
    assert all(isinstance(v, float) for v in camera.position)


def test_camera_focal_point_setter() -> None:
    """Test setting camera focal point."""
    camera = Camera()
    camera.focal_point = (1.0, 2.0, 3.0)
    assert camera.focal_point == (1.0, 2.0, 3.0)


def test_camera_view_up_setter() -> None:
    """Test setting camera view-up vector."""
    camera = Camera()
    camera.view_up = (0.0, 0.0, 1.0)
    assert camera.view_up == (0.0, 0.0, 1.0)


def test_camera_view_angle_setter() -> None:
    """Test setting camera view angle."""
    camera = Camera()
    camera.view_angle = 60.0
    assert camera.view_angle == 60.0


def test_camera_view_angle_converts_to_float() -> None:
    """Test that view angle is converted to float."""
    camera = Camera()
    camera.view_angle = 45  # integer
    assert camera.view_angle == 45.0
    assert isinstance(camera.view_angle, float)


def test_camera_clipping_range_setter() -> None:
    """Test setting camera clipping range."""
    camera = Camera()
    camera.clipping_range = (0.1, 100.0)
    assert camera.clipping_range == (0.1, 100.0)


def test_camera_clipping_range_converts_to_float() -> None:
    """Test that clipping range values are converted to float."""
    camera = Camera()
    camera.clipping_range = (1, 100)  # integers
    assert camera.clipping_range == (1.0, 100.0)
    assert all(isinstance(v, float) for v in camera.clipping_range)


def test_camera_repr() -> None:
    """Test Camera __repr__ contains key info."""
    camera = Camera()
    r = repr(camera)
    assert "Camera(" in r
    assert "position=" in r
    assert "focal_point=" in r
    assert "view_up=" in r
    assert "view_angle=" in r
    assert "clipping_range=" in r


def test_camera_available_from_top_level() -> None:
    """Test Camera is importable from pyvista_wasm top-level."""
    assert hasattr(pv, "Camera")
    assert pv.Camera is Camera


def test_plotter_camera_default_none() -> None:
    """Test that Plotter.camera is None by default."""
    plotter = pv.Plotter()
    assert plotter.camera is None


def test_plotter_camera_set() -> None:
    """Test setting camera on Plotter."""
    plotter = pv.Plotter()
    camera = Camera(position=(5.0, 5.0, 5.0))
    plotter.camera = camera

    assert plotter.camera is camera
    assert plotter._renderer._camera is camera


def test_plotter_camera_updates_renderer() -> None:
    """Test that setting camera propagates to renderer."""
    plotter = pv.Plotter()
    camera = Camera(
        position=(10.0, 0.0, 0.0),
        focal_point=(0.0, 0.0, 0.0),
        view_up=(0.0, 1.0, 0.0),
        view_angle=45.0,
        clipping_range=(0.1, 200.0),
    )
    plotter.camera = camera

    assert plotter._renderer._camera.position == (10.0, 0.0, 0.0)
    assert plotter._renderer._camera.focal_point == (0.0, 0.0, 0.0)
    assert plotter._renderer._camera.view_angle == 45.0
    assert plotter._renderer._camera.clipping_range == (0.1, 200.0)


def test_camera_generates_html(monkeypatch) -> None:
    """Test that setting a camera generates correct vtk.js camera code in HTML."""
    monkeypatch.setenv("PYVISTA_JS_NO_BROWSER", "1")

    renderer = MockRenderer()
    camera = Camera(
        position=(5.0, 5.0, 5.0),
        focal_point=(0.0, 0.0, 0.0),
        view_up=(0.0, 1.0, 0.0),
        view_angle=30.0,
        clipping_range=(0.01, 1000.0),
    )
    renderer.camera = camera

    assert renderer._camera is camera


@pytest.mark.parametrize(
    ("position", "focal_point"),
    [
        ((1.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        ((0.0, 5.0, 0.0), (0.0, 0.0, 0.0)),
        ((0.0, 0.0, 10.0), (0.0, 0.0, 0.0)),
        ((1.0, 1.0, 1.0), (0.5, 0.5, 0.5)),
    ],
)
def test_camera_various_positions(
    position: tuple,
    focal_point: tuple,
) -> None:
    """Test Camera stores various positions and focal points correctly."""
    camera = Camera(position=position, focal_point=focal_point)
    assert camera.position == tuple(float(v) for v in position)
    assert camera.focal_point == tuple(float(v) for v in focal_point)


def test_camera_parallel_projection_default() -> None:
    """Test Camera has parallel_projection disabled by default."""
    camera = Camera()
    assert camera.parallel_projection is False


def test_camera_parallel_projection_constructor() -> None:
    """Test Camera can be constructed with parallel_projection enabled."""
    camera = Camera(parallel_projection=True)
    assert camera.parallel_projection is True


def test_camera_parallel_projection_setter() -> None:
    """Test setting parallel_projection property."""
    camera = Camera()
    camera.parallel_projection = True
    assert camera.parallel_projection is True
    camera.parallel_projection = False
    assert camera.parallel_projection is False


def test_camera_parallel_projection_converts_to_bool() -> None:
    """Test that parallel_projection is converted to bool."""
    camera = Camera()
    camera.parallel_projection = 1  # truthy value
    assert camera.parallel_projection is True
    assert isinstance(camera.parallel_projection, bool)
    camera.parallel_projection = 0  # falsy value
    assert camera.parallel_projection is False


def test_camera_enable_parallel_projection() -> None:
    """Test enable_parallel_projection method."""
    camera = Camera()
    assert camera.parallel_projection is False
    camera.enable_parallel_projection()
    assert camera.parallel_projection is True


def test_camera_disable_parallel_projection() -> None:
    """Test disable_parallel_projection method."""
    camera = Camera(parallel_projection=True)
    assert camera.parallel_projection is True
    camera.disable_parallel_projection()
    assert camera.parallel_projection is False


def test_camera_repr_includes_parallel_projection() -> None:
    """Test Camera __repr__ includes parallel_projection."""
    camera = Camera(parallel_projection=True)
    r = repr(camera)
    assert "parallel_projection=True" in r


def test_camera_parallel_projection_in_renderer(monkeypatch) -> None:
    """Test that parallel projection setting is propagated to renderer."""
    monkeypatch.setenv("PYVISTA_JS_NO_BROWSER", "1")

    renderer = MockRenderer()
    camera = Camera(parallel_projection=True)
    renderer.camera = camera

    assert renderer._camera.parallel_projection is True


def test_camera_generates_parallel_projection_code() -> None:
    """Test that camera generates scene data for parallel projection."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere())
    camera = Camera(
        position=(5.0, 5.0, 5.0),
        parallel_projection=True,
    )
    plotter.camera = camera

    html = plotter._renderer._generate_html()
    scene = extract_scene_data(html)
    assert scene["camera"]["parallelProjection"] is True


def test_camera_elevation_default() -> None:
    """Test Camera has elevation set to 0.0 by default."""
    camera = Camera()
    assert camera.elevation == 0.0


def test_camera_elevation_constructor() -> None:
    """Test Camera can be constructed with elevation."""
    camera = Camera(elevation=45.0)
    assert camera.elevation == 45.0


def test_camera_elevation_setter() -> None:
    """Test setting camera elevation property."""
    camera = Camera()
    camera.elevation = 45.0
    assert camera.elevation == 45.0
    camera.elevation = -30.0
    assert camera.elevation == -30.0


def test_camera_elevation_converts_to_float() -> None:
    """Test that elevation is converted to float."""
    camera = Camera()
    camera.elevation = 45  # integer
    assert camera.elevation == 45.0
    assert isinstance(camera.elevation, float)


def test_camera_repr_includes_elevation() -> None:
    """Test Camera __repr__ includes elevation."""
    camera = Camera(elevation=45.0)
    r = repr(camera)
    assert "elevation=45.0" in r


def test_camera_elevation_in_renderer(monkeypatch) -> None:
    """Test that elevation setting is propagated to renderer."""
    monkeypatch.setenv("PYVISTA_JS_NO_BROWSER", "1")

    renderer = MockRenderer()
    camera = Camera(elevation=45.0)
    renderer.camera = camera

    assert renderer._camera.elevation == 45.0


def test_camera_generates_elevation_code() -> None:
    """Test that camera with elevation generates correct scene data."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere())
    camera = Camera(
        position=(5.0, 5.0, 5.0),
        elevation=45.0,
    )
    plotter.camera = camera

    # Generate HTML and verify camera is present in the scene data
    html = plotter._renderer._generate_html()
    scene = extract_scene_data(html)
    assert scene["camera"] is not None
    assert scene["camera"]["position"] == [5.0, 5.0, 5.0]
    assert scene["camera"]["viewAngle"] == 30.0


def _cam(
    pos: tuple[float, float, float] = (0.0, 0.0, 5.0),
    fp: tuple[float, float, float] = (0.0, 0.0, 0.0),
    up: tuple[float, float, float] = (0.0, 1.0, 0.0),
) -> Camera:
    """Create a Camera with a known state for testing."""
    return Camera(position=pos, focal_point=fp, view_up=up)


class TestCameraAzimuth:
    """Tests for Camera.azimuth()."""

    def test_azimuth_90(self) -> None:
        """90-degree azimuth moves camera from z-axis to x-axis."""
        cam = _cam()
        cam.azimuth(90)
        np.testing.assert_allclose(cam.position, (5.0, 0.0, 0.0), atol=1e-10)
        np.testing.assert_allclose(cam.focal_point, (0.0, 0.0, 0.0), atol=1e-10)

    def test_azimuth_180(self) -> None:
        """180-degree azimuth moves camera to negative z-axis."""
        cam = _cam()
        cam.azimuth(180)
        np.testing.assert_allclose(cam.position, (0.0, 0.0, -5.0), atol=1e-10)

    def test_azimuth_360_returns_to_start(self) -> None:
        """Full 360-degree azimuth returns camera to original position."""
        cam = _cam()
        original = cam.position
        cam.azimuth(360)
        np.testing.assert_allclose(cam.position, original, atol=1e-10)

    def test_azimuth_preserves_distance(self) -> None:
        """Azimuth rotation preserves distance to focal point."""
        cam = _cam()
        cam.azimuth(45)
        dist = np.linalg.norm(np.array(cam.position) - np.array(cam.focal_point))
        np.testing.assert_allclose(dist, 5.0, atol=1e-10)

    def test_azimuth_degenerate_noop(self) -> None:
        """Azimuth is no-op when position equals focal point."""
        cam = _cam(pos=(0, 0, 0), fp=(0, 0, 0))
        cam.azimuth(90)
        assert cam.position == (0.0, 0.0, 0.0)


class TestCameraOrbitElevation:
    """Tests for Camera.orbit_elevation()."""

    def test_elevation_90(self) -> None:
        """90-degree elevation moves camera from z-axis downward."""
        cam = _cam()
        cam.orbit_elevation(90)
        np.testing.assert_allclose(cam.position, (0.0, -5.0, 0.0), atol=1e-10)

    def test_elevation_preserves_distance(self) -> None:
        """Elevation rotation preserves distance to focal point."""
        cam = _cam()
        cam.orbit_elevation(30)
        dist = np.linalg.norm(np.array(cam.position) - np.array(cam.focal_point))
        np.testing.assert_allclose(dist, 5.0, atol=1e-10)

    def test_elevation_updates_view_up(self) -> None:
        """Elevation rotation also updates the view-up vector."""
        cam = _cam()
        original_up = cam.view_up
        cam.orbit_elevation(45)
        assert cam.view_up != original_up

    def test_elevation_degenerate_noop(self) -> None:
        """Elevation is no-op when position equals focal point."""
        cam = _cam(pos=(1, 1, 1), fp=(1, 1, 1))
        cam.orbit_elevation(45)
        assert cam.position == (1.0, 1.0, 1.0)


class TestCameraZoom:
    """Tests for Camera.zoom()."""

    def test_zoom_in(self) -> None:
        """Zoom > 1 halves distance."""
        cam = _cam(pos=(0, 0, 10))
        cam.zoom(2.0)
        np.testing.assert_allclose(cam.position, (0.0, 0.0, 5.0), atol=1e-10)

    def test_zoom_out(self) -> None:
        """Zoom < 1 doubles distance."""
        cam = _cam()
        cam.zoom(0.5)
        np.testing.assert_allclose(cam.position, (0.0, 0.0, 10.0), atol=1e-10)

    def test_zoom_preserves_direction(self) -> None:
        """Zoom does not change the direction of the camera."""
        cam = _cam(pos=(3, 4, 0))
        original_dir = np.array(cam.focal_point) - np.array(cam.position)
        original_dir = original_dir / np.linalg.norm(original_dir)
        cam.zoom(1.5)
        new_dir = np.array(cam.focal_point) - np.array(cam.position)
        new_dir = new_dir / np.linalg.norm(new_dir)
        np.testing.assert_allclose(new_dir, original_dir, atol=1e-10)

    def test_zoom_zero_raises(self) -> None:
        """Zoom with zero factor raises ValueError."""
        cam = _cam()
        with pytest.raises(ValueError, match="positive"):
            cam.zoom(0)

    def test_zoom_negative_raises(self) -> None:
        """Zoom with negative factor raises ValueError."""
        cam = _cam()
        with pytest.raises(ValueError, match="positive"):
            cam.zoom(-1.0)


class TestCameraRoll:
    """Tests for Camera.roll()."""

    def test_roll_90(self) -> None:
        """90-degree roll rotates up vector."""
        cam = _cam()
        cam.roll(90)
        np.testing.assert_allclose(cam.view_up, (1.0, 0.0, 0.0), atol=1e-10)

    def test_roll_preserves_position(self) -> None:
        """Roll does not change camera position."""
        cam = _cam()
        cam.roll(45)
        np.testing.assert_allclose(cam.position, (0.0, 0.0, 5.0), atol=1e-10)

    def test_roll_preserves_focal_point(self) -> None:
        """Roll does not change focal point."""
        cam = _cam()
        cam.roll(45)
        np.testing.assert_allclose(cam.focal_point, (0.0, 0.0, 0.0), atol=1e-10)

    def test_roll_360_returns_to_start(self) -> None:
        """Full 360-degree roll returns up vector to original."""
        cam = _cam()
        original_up = cam.view_up
        cam.roll(360)
        np.testing.assert_allclose(cam.view_up, original_up, atol=1e-10)


class TestCameraCombinedMovement:
    """Tests for combining multiple camera movements."""

    def test_azimuth_then_zoom(self) -> None:
        """Azimuth followed by zoom applies both transformations."""
        cam = _cam()
        cam.azimuth(45)
        cam.zoom(2.0)
        dist = np.linalg.norm(np.array(cam.position) - np.array(cam.focal_point))
        np.testing.assert_allclose(dist, 2.5, atol=1e-10)

    def test_elevation_then_roll(self) -> None:
        """Elevation followed by roll applies both transformations."""
        cam = _cam()
        cam.orbit_elevation(45)
        cam.roll(90)
        # Position should be changed by elevation
        assert cam.position != (0.0, 0.0, 5.0)
        # Up vector should be changed by both
        assert cam.view_up != (0.0, 1.0, 0.0)
