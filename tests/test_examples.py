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


class TestLoadNeptune:
    """Tests for examples.load_neptune."""

    def test_returns_polydata(self) -> None:
        """load_neptune returns a PolyData instance."""
        neptune = examples.load_neptune()
        assert isinstance(neptune, PolyData)

    def test_has_texture_coordinates(self) -> None:
        """The returned mesh has texture coordinates."""
        neptune = examples.load_neptune()
        assert neptune.t_coords is not None
        assert neptune.t_coords.shape == (neptune.n_points, 2)

    def test_default_resolution(self) -> None:
        """Default lat/lon resolution produces expected point count."""
        neptune = examples.load_neptune()
        # lat_resolution=50, lon_resolution=100 → 2 + 100*(50-2) = 4802
        assert neptune.n_points == 4802

    def test_custom_radius(self) -> None:
        """Custom radius affects bounding sphere."""
        neptune = examples.load_neptune(radius=2.0)
        radius, _ = neptune.bounding_sphere
        assert abs(radius - 2.0) < 0.01


class TestDownloadNeptuneSurface:
    """Tests for examples.download_neptune_surface."""

    def test_returns_texture(self) -> None:
        """download_neptune_surface returns a Texture instance."""
        texture = examples.download_neptune_surface()
        assert isinstance(texture, Texture)

    def test_url_points_at_neptune_solar_texture(self) -> None:
        """The texture URL points at the Neptune solar_textures image."""
        texture = examples.download_neptune_surface()
        assert texture.url == (
            "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data/solar_textures/neptune.jpg"
        )

    def test_repr_mentions_neptune(self) -> None:
        """The Texture repr references the Neptune image."""
        texture = examples.download_neptune_surface()
        assert "neptune.jpg" in repr(texture)
