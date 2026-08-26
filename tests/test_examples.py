"""Test the planet surface example helper."""

from pyvista_wasm import Texture, examples


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
