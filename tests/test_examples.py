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
