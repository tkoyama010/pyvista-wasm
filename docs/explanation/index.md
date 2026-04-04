# Explanation

Deeper understanding of pyvista-wasm concepts and architecture.

## Overview

pyvista-wasm is a PyVista-like API for VTK.wasm, bringing the intuitive PyVista interface
to WebAssembly-based 3D visualization. It enables 3D visualization in browser environments
including Pyodide, JupyterLite, and Streamlit applications.

## Architecture

pyvista-wasm separates concerns between Python and JavaScript:

- **Python side**: Handles geometry preparation, scene configuration, and API surface.
- **JavaScript side (VTK.wasm)**: Handles the actual geometry parsing and WebGL rendering via WebAssembly.

## Features

- PyVista-like API for familiar usage
- Integration with VTK.wasm for web-based visualization
- Support for JupyterLite and Streamlit
- Physically Based Rendering (PBR) with metallic and roughness controls
- PLY, OBJ, STL, GLTF, and PolyData file format readers
