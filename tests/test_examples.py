"""Test the example helper functions."""

from pyvista_wasm import PolyData, Texture, examples


class TestLoadEarth:
    """Tests for examples.load_earth."""

    def test_returns_polydata(self) -> None:
        """load_earth returns a PolyData instance."""
        earth = examples.load_earth()
        assert isinstance(earth, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        earth = examples.load_earth()
        assert earth.t_coords is not None
        assert earth.t_coords.shape == (earth.n_points, 2)

    def test_default_resolution(self) -> None:
        """Default lat/lon resolution produces expected point count."""
        earth = examples.load_earth()
        # lat_resolution=50, lon_resolution=100 → 2 + 100*(50-2) = 4802
        assert earth.n_points == 4802

    def test_custom_radius(self) -> None:
        """Custom radius affects bounding sphere."""
        earth = examples.load_earth(radius=2.0)
        radius, _ = earth.bounding_sphere
        assert abs(radius - 2.0) < 0.01


class TestLoadVenus:
    """Tests for examples.load_venus."""

    def test_returns_polydata(self) -> None:
        """load_venus returns a PolyData instance."""
        venus = examples.load_venus()
        assert isinstance(venus, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        venus = examples.load_venus()
        assert venus.t_coords is not None
        assert venus.t_coords.shape == (venus.n_points, 2)

    def test_default_resolution(self) -> None:
        """Default lat/lon resolution produces expected point count."""
        venus = examples.load_venus()
        # lat_resolution=50, lon_resolution=100 → 2 + 100*(50-2) = 4802
        assert venus.n_points == 4802

    def test_custom_radius(self) -> None:
        """Custom radius affects bounding sphere."""
        venus = examples.load_venus(radius=2.0)
        radius, _ = venus.bounding_sphere
        assert abs(radius - 2.0) < 0.01


class TestDownloadMarsSurface:
    """Tests for examples.download_mars_surface."""

    def test_returns_texture(self) -> None:
        """download_mars_surface returns a Texture instance."""
        texture = examples.download_mars_surface()
        assert isinstance(texture, Texture)

    def test_url_points_at_mars_solar_texture(self) -> None:
        """The texture URL points at the Mars solar_textures image."""
        texture = examples.download_mars_surface()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/mars.jpg"
        )

    def test_repr_mentions_mars(self) -> None:
        """The Texture repr references the Mars image."""
        texture = examples.download_mars_surface()
        assert "mars.jpg" in repr(texture)


class TestDownloadVenusSurface:
    """Tests for examples.download_venus_surface."""

    def test_returns_texture(self) -> None:
        """download_venus_surface returns a Texture instance."""
        texture = examples.download_venus_surface()
        assert isinstance(texture, Texture)

    def test_url_points_at_venus_solar_texture(self) -> None:
        """The texture URL points at the Venus solar_textures image."""
        texture = examples.download_venus_surface()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/venus_surface.jpg"
        )

    def test_repr_mentions_venus(self) -> None:
        """The Texture repr references the Venus image."""
        texture = examples.download_venus_surface()
        assert "venus_surface.jpg" in repr(texture)


class TestLoadSaturn:
    """Tests for examples.load_saturn."""

    def test_returns_polydata(self) -> None:
        """load_saturn returns a PolyData instance."""
        saturn = examples.load_saturn()
        assert isinstance(saturn, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        saturn = examples.load_saturn()
        assert saturn.t_coords is not None
        assert saturn.t_coords.shape == (saturn.n_points, 2)

    def test_default_resolution(self) -> None:
        """Default lat/lon resolution produces expected point count."""
        saturn = examples.load_saturn()
        # lat_resolution=50, lon_resolution=100 → 2 + 100*(50-2) = 4802
        assert saturn.n_points == 4802

    def test_custom_radius(self) -> None:
        """Custom radius affects bounding sphere."""
        saturn = examples.load_saturn(radius=2.0)
        radius, _ = saturn.bounding_sphere
        assert abs(radius - 2.0) < 0.01


class TestLoadSaturnRings:
    """Tests for examples.load_saturn_rings."""

    def test_returns_polydata(self) -> None:
        """load_saturn_rings returns a PolyData instance."""
        rings = examples.load_saturn_rings()
        assert isinstance(rings, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        rings = examples.load_saturn_rings()
        assert rings.t_coords is not None
        assert rings.t_coords.shape == (rings.n_points, 2)

    def test_texture_u_is_radial(self) -> None:
        """The U texture coordinate is radial from inner to outer radius."""
        rings = examples.load_saturn_rings()
        t_coords = rings.t_coords
        assert t_coords is not None
        assert (t_coords[:, 1] == 0.0).all()
        assert (t_coords[:, 0] >= 0.0).all()
        assert (t_coords[:, 0] <= 1.0).all()
        assert (t_coords[:, 0] == t_coords[:, 0].max()).any()

    def test_custom_radii(self) -> None:
        """Custom inner/outer radii affect bounding sphere."""
        rings = examples.load_saturn_rings(inner=0.1, outer=0.4)
        radius, _ = rings.bounding_sphere
        assert abs(radius - 0.4) < 0.01


class TestDownloadSaturnSurface:
    """Tests for examples.download_saturn_surface."""

    def test_returns_texture(self) -> None:
        """download_saturn_surface returns a Texture instance."""
        texture = examples.download_saturn_surface()
        assert isinstance(texture, Texture)

    def test_url_points_at_saturn_solar_texture(self) -> None:
        """The texture URL points at the Saturn solar_textures image."""
        texture = examples.download_saturn_surface()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/saturn.jpg"
        )

    def test_repr_mentions_saturn(self) -> None:
        """The Texture repr references the Saturn image."""
        texture = examples.download_saturn_surface()
        assert "saturn.jpg" in repr(texture)


class TestDownloadSaturnRings:
    """Tests for examples.download_saturn_rings."""

    def test_returns_texture(self) -> None:
        """download_saturn_rings returns a Texture instance."""
        texture = examples.download_saturn_rings()
        assert isinstance(texture, Texture)

    def test_url_points_at_saturn_rings_solar_texture(self) -> None:
        """The texture URL points at the Saturn's rings solar_textures image."""
        texture = examples.download_saturn_rings()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/saturn_ring_alpha.png"
        )

    def test_repr_mentions_saturn_rings(self) -> None:
        """The Texture repr references the Saturn's rings image."""
        texture = examples.download_saturn_rings()
        assert "saturn_ring_alpha.png" in repr(texture)


class TestLoadUranus:
    """Tests for examples.load_uranus."""

    def test_returns_polydata(self) -> None:
        """load_uranus returns a PolyData instance."""
        uranus = examples.load_uranus()
        assert isinstance(uranus, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        uranus = examples.load_uranus()
        assert uranus.t_coords is not None
        assert uranus.t_coords.shape == (uranus.n_points, 2)

    def test_default_resolution(self) -> None:
        """Default lat/lon resolution produces expected point count."""
        uranus = examples.load_uranus()
        # lat_resolution=50, lon_resolution=100 → 2 + 100*(50-2) = 4802
        assert uranus.n_points == 4802

    def test_custom_radius(self) -> None:
        """Custom radius affects bounding sphere."""
        uranus = examples.load_uranus(radius=2.0)
        radius, _ = uranus.bounding_sphere
        assert abs(radius - 2.0) < 0.01


class TestDownloadUranusSurface:
    """Tests for examples.download_uranus_surface."""

    def test_returns_texture(self) -> None:
        """download_uranus_surface returns a Texture instance."""
        texture = examples.download_uranus_surface()
        assert isinstance(texture, Texture)

    def test_url_points_at_uranus_solar_texture(self) -> None:
        """The texture URL points at the Uranus solar_textures image."""
        texture = examples.download_uranus_surface()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/uranus.jpg"
        )

    def test_repr_mentions_uranus(self) -> None:
        """The Texture repr references the Uranus image."""
        texture = examples.download_uranus_surface()
        assert "uranus.jpg" in repr(texture)


class TestLoadSun:
    """Tests for examples.load_sun."""

    def test_returns_polydata(self) -> None:
        """load_sun returns a PolyData instance."""
        sun = examples.load_sun()
        assert isinstance(sun, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        sun = examples.load_sun()
        assert sun.t_coords is not None
        assert sun.t_coords.shape == (sun.n_points, 2)

    def test_default_resolution(self) -> None:
        """Default lat/lon resolution produces expected point count."""
        sun = examples.load_sun()
        # lat_resolution=50, lon_resolution=100 → 2 + 100*(50-2) = 4802
        assert sun.n_points == 4802

    def test_custom_radius(self) -> None:
        """Custom radius affects bounding sphere."""
        sun = examples.load_sun(radius=2.0)
        radius, _ = sun.bounding_sphere
        assert abs(radius - 2.0) < 0.01


class TestDownloadSunSurface:
    """Tests for examples.download_sun_surface."""

    def test_returns_texture(self) -> None:
        """download_sun_surface returns a Texture instance."""
        texture = examples.download_sun_surface()
        assert isinstance(texture, Texture)

    def test_url_points_at_sun_solar_texture(self) -> None:
        """The texture URL points at the Sun solar_textures image."""
        texture = examples.download_sun_surface()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/sun.jpg"
        )

    def test_repr_mentions_sun(self) -> None:
        """The Texture repr references the Sun image."""
        texture = examples.download_sun_surface()
        assert "sun.jpg" in repr(texture)


class TestLoadMercury:
    """Tests for examples.load_mercury."""

    def test_returns_polydata(self) -> None:
        """load_mercury returns a PolyData instance."""
        mercury = examples.load_mercury()
        assert isinstance(mercury, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        mercury = examples.load_mercury()
        assert mercury.t_coords is not None
        assert mercury.t_coords.shape == (mercury.n_points, 2)

    def test_default_resolution(self) -> None:
        """Default lat/lon resolution produces expected point count."""
        mercury = examples.load_mercury()
        # lat_resolution=50, lon_resolution=100 → 2 + 100*(50-2) = 4802
        assert mercury.n_points == 4802

    def test_custom_radius(self) -> None:
        """Custom radius affects bounding sphere."""
        mercury = examples.load_mercury(radius=2.0)
        radius, _ = mercury.bounding_sphere
        assert abs(radius - 2.0) < 0.01


class TestDownloadMercurySurface:
    """Tests for examples.download_mercury_surface."""

    def test_returns_texture(self) -> None:
        """download_mercury_surface returns a Texture instance."""
        texture = examples.download_mercury_surface()
        assert isinstance(texture, Texture)

    def test_url_points_at_mercury_solar_texture(self) -> None:
        """The texture URL points at the Mercury solar_textures image."""
        texture = examples.download_mercury_surface()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/mercury.jpg"
        )

    def test_repr_mentions_mercury(self) -> None:
        """The Texture repr references the Mercury image."""
        texture = examples.download_mercury_surface()
        assert "mercury.jpg" in repr(texture)
