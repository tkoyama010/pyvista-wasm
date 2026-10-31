"""Tests for the rendering backend option (issue #801)."""

import pytest

import pyvista_wasm as pv


class TestBackendOption:
    """Tests for the wasm_rendering backend argument."""

    @pytest.mark.parametrize("backend", ["auto", "webgl", "webgl2", "webgpu"])
    def test_valid_backends(self, backend: str) -> None:
        """Test each backend name is accepted and stored."""
        renderer = pv.Plotter(wasm_rendering=backend)._renderer
        assert renderer._wasm_rendering == backend

    def test_invalid_backend_raises(self) -> None:
        """Test an unknown backend raises ValueError."""
        with pytest.raises(ValueError, match="wasm_rendering"):
            pv.Plotter(wasm_rendering="vulkan")

    def test_scene_data_carries_backend(self) -> None:
        """Test the backend reaches the scene config."""
        plotter = pv.Plotter(wasm_rendering="auto")
        scene = plotter._renderer._build_scene_data()
        assert scene["wasmConfig"]["rendering"] == "auto"
