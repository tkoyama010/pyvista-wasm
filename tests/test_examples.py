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


class TestDownloadStarsSkyBackground:
    """Tests for examples.download_stars_sky_background."""

    def test_returns_texture(self) -> None:
        """download_stars_sky_background returns a Texture instance."""
        texture = examples.download_stars_sky_background()
        assert isinstance(texture, Texture)

    def test_url_points_at_stars_sky_texture(self) -> None:
        """The texture URL points at the stars planet3d-matlab image."""
        texture = examples.download_stars_sky_background()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/planet3d-matlab/stars.jpg"
        )

    def test_repr_mentions_stars(self) -> None:
        """The Texture repr references the stars image."""
        texture = examples.download_stars_sky_background()
        assert "stars.jpg" in repr(texture)


class TestDownloadMilkywaySkyBackground:
    """Tests for examples.download_milkyway_sky_background."""

    def test_returns_texture(self) -> None:
        """download_milkyway_sky_background returns a Texture instance."""
        texture = examples.download_milkyway_sky_background()
        assert isinstance(texture, Texture)

    def test_url_points_at_milkyway_sky_texture(self) -> None:
        """The texture URL points at the milkyway planet3d-matlab image."""
        texture = examples.download_milkyway_sky_background()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/planet3d-matlab/milkyway.jpg"
        )

    def test_repr_mentions_milkyway(self) -> None:
        """The Texture repr references the milkyway image."""
        texture = examples.download_milkyway_sky_background()
        assert "milkyway.jpg" in repr(texture)


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
