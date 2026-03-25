"""File readers for pyvista-wasm.

Provides readers for loading mesh file formats into Mesh objects,
using VTK.wasm built-in readers for parsing on the JavaScript side.
"""

from __future__ import annotations

import base64
import json
import logging
import struct
from pathlib import Path

import numpy as np

from .mesh import PolyData

logger = logging.getLogger(__name__)

# Minimum number of lines in a valid VTK legacy file
# (version header, title, format, dataset declaration)
_MIN_VTK_LINES = 4

# Number of coordinate components per vertex (x, y, z)
_N_COORDS = 3


class _OBJMesh(PolyData):
    """Mesh loaded from an OBJ file, rendered via VTK.wasm OBJ reader."""

    def __init__(self, points: np.ndarray, obj_base64: str) -> None:
        """Initialize with points and base64-encoded OBJ file content."""
        super().__init__(points)
        self._obj_base64 = obj_base64

    def to_scene_data(self) -> dict[str, object]:
        """Return scene data using VTK.wasm OBJ reader."""
        return {"type": "objReader", "data": self._obj_base64}


class _GLTFMesh(PolyData):
    """Mesh loaded from a glTF file, rendered via VTK.wasm GLTF importer."""

    def __init__(
        self,
        points: np.ndarray,
        gltf_base64: str,
        gltf_url: str | None = None,
    ) -> None:
        """Initialize with points and base64-encoded glTF file content."""
        super().__init__(points)
        self._gltf_base64 = gltf_base64
        self._gltf_url = gltf_url

    def to_scene_data(self) -> dict[str, object]:
        """Return scene data using VTK.wasm GLTF importer."""
        data: dict[str, object] = {"type": "gltfReader", "data": self._gltf_base64}
        if self._gltf_url is not None:
            data["url"] = self._gltf_url
        return data


class _PolyDataMesh(PolyData):
    """Mesh loaded from a legacy VTK file, rendered via VTK.wasm reader."""

    def __init__(self, points: np.ndarray, vtk_text: str) -> None:
        """Initialize with points and raw VTK file content."""
        super().__init__(points)
        self._vtk_text = vtk_text

    def to_scene_data(self) -> dict[str, object]:
        """Return scene data using VTK.wasm VTK reader."""
        return {
            "type": "vtkReader",
            "data": base64.b64encode(self._vtk_text.encode()).decode("ascii"),
        }


class _PLYMesh(PolyData):
    """Mesh loaded from a PLY file, rendered using extracted geometry."""

    def __init__(self, points: np.ndarray, polys: np.ndarray) -> None:
        """Initialize with points and face connectivity."""
        super().__init__(points, faces=polys if len(polys) > 0 else None)


class _STLMesh(PolyData):
    """Mesh loaded from an STL file, rendered via VTK.wasm STL reader."""

    def __init__(self, points: np.ndarray, stl_base64: str) -> None:
        """Initialize with points and base64-encoded STL file content."""
        super().__init__(points)
        self._stl_base64 = stl_base64

    def to_scene_data(self) -> dict[str, object]:
        """Return scene data using VTK.wasm STL reader."""
        return {"type": "stlReader", "data": self._stl_base64}


class PolyDataReader:
    """Reader for legacy VTK PolyData files (``.vtk``).

    Reads a legacy VTK ASCII file and produces a :class:`Mesh` that
    delegates parsing to VTK.wasm's ``vtkPolyDataReader`` at render time.
    Python extracts only the point coordinates so that camera framing
    and bounding-sphere queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.vtk`` file.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> reader = pv.PolyDataReader("sphere.vtk")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".vtk":
            msg = f"Expected a .vtk file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the VTK file.

        """
        return self._path

    def read(self) -> _PolyDataMesh:
        """Read the VTK file and return a Mesh.

        The full file content is stored so that VTK.wasm can parse it at
        render time.  Point coordinates are extracted on the Python side
        for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the VTK file content.

        Raises
        ------
        ValueError
            If the file format is invalid or unsupported.

        """
        vtk_text = self._path.read_text()
        lines = vtk_text.splitlines()

        if len(lines) < _MIN_VTK_LINES:
            msg = "Invalid VTK file: too few lines"
            raise ValueError(msg)

        if "vtk" not in lines[0].lower():
            msg = "Invalid VTK file: missing version header"
            raise ValueError(msg)

        file_format = lines[2].strip().upper()
        if file_format != "ASCII":
            msg = f"Only ASCII VTK files are supported, got: {file_format}"
            raise ValueError(msg)

        points = self._extract_points(lines)
        logger.info("Read %d points from %s", len(points), self._path)
        return _PolyDataMesh(points=points, vtk_text=vtk_text)

    @staticmethod
    def _extract_points(lines: list[str]) -> np.ndarray:
        """Extract point coordinates from VTK ASCII lines.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by VTK.wasm at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the VTK file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        i = 3
        while i < len(lines):
            line = lines[i].strip()
            if line.upper().startswith("POINTS"):
                parts = line.split()
                n_points = int(parts[1])
                values: list[float] = []
                i += 1
                needed = n_points * 3
                while len(values) < needed and i < len(lines):
                    row = lines[i].strip()
                    if row:
                        values.extend(float(v) for v in row.split())
                    i += 1
                return np.array(values[: n_points * 3]).reshape(n_points, 3)
            i += 1
        return np.empty((0, 3))


class PLYReader:
    """Reader for PLY (Polygon File Format) files (``.ply``).

    Reads a PLY ASCII file and produces a :class:`Mesh` that delegates
    parsing to VTK.wasm's ``vtkPLYReader`` at render time. Python extracts
    only the vertex coordinates so that camera framing and bounding-sphere
    queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.ply`` file.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> reader = pv.PLYReader("model.ply")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".ply":
            msg = f"Expected a .ply file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the PLY file.

        """
        return self._path

    def read(self) -> _PLYMesh:
        """Read the PLY file and return a Mesh.

        Vertex coordinates and face connectivity are extracted on the Python
        side so that the mesh can be rendered via the standard geometry
        pipeline without requiring a VTK.wasm file reader.

        Returns
        -------
        Mesh
            A mesh with extracted points and face connectivity.

        Raises
        ------
        ValueError
            If the file format is invalid or unsupported.

        """
        raw = self._path.read_bytes()
        text = raw.decode("ascii", errors="replace")
        lines = text.splitlines()

        if not lines or lines[0].strip() != "ply":
            msg = "Invalid PLY file: missing 'ply' magic number"
            raise ValueError(msg)

        header_end = None
        header_byte_offset = 0
        for i, line in enumerate(lines):
            if line.strip() == "end_header":
                header_end = i
                # Calculate byte offset after header
                header_byte_offset = raw.find(b"end_header") + len(b"end_header") + 1
                break

        if header_end is None:
            msg = "Invalid PLY file: missing 'end_header'"
            raise ValueError(msg)

        fmt = self._parse_format(lines[1 : header_end + 1])
        header_lines = lines[1 : header_end + 1]

        if fmt == "ascii":
            points = self._extract_points(lines, header_end)
            polys = self._extract_polys(lines, header_end, len(points))
        elif fmt in ("binary_little_endian", "binary_big_endian"):
            points = self._extract_points_binary(raw, header_lines, header_byte_offset, fmt)
            polys = self._extract_polys_binary(raw, header_lines, header_byte_offset, fmt)
        else:
            msg = f"Unsupported PLY format: {fmt}"
            raise ValueError(msg)

        logger.info("Read %d points from %s", len(points), self._path)
        return _PLYMesh(points=points, polys=polys)

    @staticmethod
    def _parse_format(header_lines: list[str]) -> str:
        """Extract the format from PLY header lines.

        Parameters
        ----------
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.

        Returns
        -------
        str
            The format string (e.g. ``'ascii'``, ``'binary_little_endian'``).

        Raises
        ------
        ValueError
            If no format line is found.

        """
        for line in header_lines:
            parts = line.strip().split()
            if parts and parts[0] == "format":
                return parts[1]
        msg = "Invalid PLY file: missing 'format' declaration"
        raise ValueError(msg)

    @staticmethod
    def _extract_points(lines: list[str], header_end: int) -> np.ndarray:
        """Extract vertex coordinates from PLY ASCII data.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by VTK.wasm at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the PLY file.
        header_end : int
            Index of the 'end_header' line.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        # Find vertex count from header
        n_vertices = 0
        for line in lines[1 : header_end + 1]:
            parts = line.strip().split()
            if len(parts) >= _N_COORDS and parts[0] == "element" and parts[1] == "vertex":
                n_vertices = int(parts[2])
                break

        if n_vertices == 0:
            return np.empty((0, 3))

        data_start = header_end + 1
        points = []
        for i in range(n_vertices):
            if data_start + i >= len(lines):
                break
            parts = lines[data_start + i].strip().split()
            if len(parts) >= _N_COORDS:
                points.append([float(parts[0]), float(parts[1]), float(parts[2])])

        if not points:
            return np.empty((0, 3))
        return np.array(points)

    @staticmethod
    def _parse_vertex_info(header_lines: list[str]) -> tuple[int, list[str]]:
        """Extract vertex count and property types from PLY header lines.

        Parameters
        ----------
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.

        Returns
        -------
        tuple[int, list[str]]
            Vertex count and list of property type strings.

        """
        n_vertices = 0
        vertex_properties: list[str] = []
        in_vertex_element = False

        for line in header_lines:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "element":
                if len(parts) >= _N_COORDS and parts[1] == "vertex":
                    n_vertices = int(parts[2])
                    in_vertex_element = True
                else:
                    in_vertex_element = False
            elif parts[0] == "property" and in_vertex_element and len(parts) >= _N_COORDS:
                vertex_properties.append(parts[1])

        return n_vertices, vertex_properties

    @staticmethod
    def _extract_points_binary(
        raw: bytes,
        header_lines: list[str],
        data_offset: int,
        fmt: str,
    ) -> np.ndarray:
        """Extract vertex coordinates from binary PLY data.

        Parameters
        ----------
        raw : bytes
            Raw binary content of the PLY file.
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.
        data_offset : int
            Byte offset where vertex data starts (after 'end_header').
        fmt : str
            Format string ('binary_little_endian' or 'binary_big_endian').

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        endian = "<" if fmt == "binary_little_endian" else ">"

        n_vertices, vertex_properties = PLYReader._parse_vertex_info(header_lines)

        if n_vertices == 0:
            return np.empty((0, 3))

        # Build struct format for one vertex
        # We need to know the size of each property to skip them
        type_map = {
            "char": "b",
            "uchar": "B",
            "short": "h",
            "ushort": "H",
            "int": "i",
            "uint": "I",
            "float": "f",
            "double": "d",
        }

        # Calculate bytes per vertex
        vertex_fmt = endian
        bytes_per_vertex = 0
        for prop_type in vertex_properties:
            if prop_type in type_map:
                vertex_fmt += type_map[prop_type]
                bytes_per_vertex += struct.calcsize(endian + type_map[prop_type])

        # Extract points (first 3 properties assumed to be x, y, z)
        points = []
        offset = data_offset

        for _ in range(n_vertices):
            if offset + bytes_per_vertex > len(raw):
                break

            try:
                vertex_data = struct.unpack_from(vertex_fmt, raw, offset)
                # Take only first 3 values (x, y, z)
                points.append([float(vertex_data[0]), float(vertex_data[1]), float(vertex_data[2])])
                offset += bytes_per_vertex
            except struct.error:
                break

        if not points:
            return np.empty((0, 3))
        return np.array(points)

    @staticmethod
    def _parse_face_count(header_lines: list[str]) -> int:
        """Extract the face element count from PLY header lines.

        Parameters
        ----------
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.

        Returns
        -------
        int
            Number of faces declared in the header, or 0 if not found.

        """
        in_face = False
        for line in header_lines:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "element":
                min_parts = 3
                in_face = len(parts) >= min_parts and parts[1] == "face"
                if in_face:
                    return int(parts[2])
        return 0

    @staticmethod
    def _extract_polys(lines: list[str], header_end: int, n_vertices: int) -> np.ndarray:
        """Extract face connectivity from PLY ASCII data.

        Parameters
        ----------
        lines : list[str]
            All lines of the PLY file.
        header_end : int
            Index of the 'end_header' line.
        n_vertices : int
            Number of vertex lines to skip before face data begins.

        Returns
        -------
        np.ndarray
            Flat integer array in VTK cell format: ``[n, i0, i1, ..., n, i0, ...]``.

        """
        face_start = header_end + 1 + n_vertices
        polys: list[int] = []
        for line in lines[face_start:]:
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if not parts:
                continue
            count = int(parts[0])
            if len(parts) >= count + 1:
                polys.append(count)
                polys.extend(int(parts[j]) for j in range(1, count + 1))
        if not polys:
            return np.empty((0,), dtype=np.int64)
        return np.array(polys, dtype=np.int64)

    @staticmethod
    def _extract_polys_binary(
        raw: bytes,
        header_lines: list[str],
        data_offset: int,
        fmt: str,
    ) -> np.ndarray:
        """Extract face connectivity from binary PLY data.

        Assumes face list properties use a 1-byte count (``uchar``/``uint8``)
        followed by 4-byte signed integer indices (``int``/``int32``), which is
        the standard format produced by VTK and most 3D tools.

        Parameters
        ----------
        raw : bytes
            Raw binary content of the PLY file.
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.
        data_offset : int
            Byte offset where vertex data starts (after 'end_header').
        fmt : str
            Format string ('binary_little_endian' or 'binary_big_endian').

        Returns
        -------
        np.ndarray
            Flat integer array in VTK cell format: ``[n, i0, i1, ..., n, i0, ...]``.

        """
        endian = "<" if fmt == "binary_little_endian" else ">"

        n_vertices, vertex_properties = PLYReader._parse_vertex_info(header_lines)
        n_faces = PLYReader._parse_face_count(header_lines)

        type_sizes = {
            "char": 1, "uchar": 1, "short": 2, "ushort": 2,
            "int": 4, "uint": 4, "float": 4, "double": 8,
        }
        bytes_per_vertex = sum(type_sizes.get(pt, 0) for pt in vertex_properties)
        offset = data_offset + n_vertices * bytes_per_vertex

        polys: list[int] = []
        for _ in range(n_faces):
            if offset >= len(raw):
                break
            # Read 1-byte face vertex count
            count = raw[offset]
            offset += 1
            polys.append(count)
            # Read 'count' 4-byte signed integer vertex indices
            for _ in range(count):
                if offset + 4 > len(raw):
                    break
                (idx,) = struct.unpack_from(endian + "i", raw, offset)
                polys.append(idx)
                offset += 4

        if not polys:
            return np.empty((0,), dtype=np.int64)
        return np.array(polys, dtype=np.int64)


class OBJReader:
    """Reader for Wavefront OBJ files (``.obj``).

    Reads an OBJ ASCII file and produces a :class:`Mesh` that delegates
    parsing to VTK.wasm's ``vtkOBJReader`` at render time. Python extracts
    only the vertex coordinates so that camera framing and bounding-sphere
    queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.obj`` file.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> reader = pv.OBJReader("model.obj")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".obj":
            msg = f"Expected a .obj file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the OBJ file.

        """
        return self._path

    def read(self) -> _OBJMesh:
        """Read the OBJ file and return a Mesh.

        The full file content is base64-encoded and stored so that VTK.wasm
        can parse it at render time.  Vertex coordinates are extracted on
        the Python side for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the OBJ file content.

        Raises
        ------
        ValueError
            If the file contains no vertex data.

        """
        raw = self._path.read_bytes()
        text = raw.decode("ascii", errors="replace")
        lines = text.splitlines()

        points = self._extract_points(lines)
        obj_base64 = base64.b64encode(raw).decode("ascii")
        logger.info("Read %d points from %s", len(points), self._path)
        return _OBJMesh(points=points, obj_base64=obj_base64)

    @staticmethod
    def _extract_points(lines: list[str]) -> np.ndarray:
        """Extract vertex coordinates from OBJ lines.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by VTK.wasm at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the OBJ file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        points = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("v "):
                parts = stripped.split()
                if len(parts) >= _N_COORDS + 1:
                    points.append(
                        [float(parts[1]), float(parts[2]), float(parts[3])],
                    )
        if not points:
            return np.empty((0, 3))
        return np.array(points)


class STLReader:
    """Reader for STL (STereoLithography) files (``.stl``).

    Reads an STL file (ASCII or binary) and produces a :class:`Mesh` that
    delegates parsing to VTK.wasm's ``vtkSTLReader`` at render time. Python
    extracts only the vertex coordinates so that camera framing and
    bounding-sphere queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.stl`` file.

    Examples
    --------
    >>> from pyvista_wasm import examples
    >>> mesh = examples.download_cad_model()  # doctest: +SKIP
    >>> mesh.plot()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".stl":
            msg = f"Expected a .stl file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the STL file.

        """
        return self._path

    def read(self) -> _STLMesh:
        """Read the STL file and return a Mesh.

        The full file content is base64-encoded and stored so that VTK.wasm
        can parse it at render time.  Vertex coordinates are extracted on
        the Python side for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the STL file content.

        Raises
        ------
        ValueError
            If the file format is invalid or unsupported.

        """
        raw = self._path.read_bytes()

        if self._is_binary_stl(raw):
            points = self._extract_points_binary(raw)
        else:
            text = raw.decode("ascii", errors="replace")
            lines = text.splitlines()
            if not lines or "solid" not in lines[0].lower():
                msg = "Invalid STL file: missing 'solid' header"
                raise ValueError(msg)
            points = self._extract_points(lines)

        stl_base64 = base64.b64encode(raw).decode("ascii")
        logger.info("Read %d points from %s", len(points), self._path)
        return _STLMesh(points=points, stl_base64=stl_base64)

    @staticmethod
    def _extract_points(lines: list[str]) -> np.ndarray:
        """Extract vertex coordinates from STL ASCII data.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by VTK.wasm at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the STL file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        points = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("vertex"):
                parts = stripped.split()
                if len(parts) >= _N_COORDS + 1:
                    points.append(
                        [float(parts[1]), float(parts[2]), float(parts[3])],
                    )
        if not points:
            return np.empty((0, 3))
        return np.array(points)

    @staticmethod
    def _is_binary_stl(raw: bytes) -> bool:
        """Check whether raw bytes represent a binary STL file.

        Binary STL is exactly 84 + 50*N bytes (80-byte header, 4-byte
        triangle count, 50 bytes per triangle). This size check
        reliably distinguishes binary from ASCII.

        Parameters
        ----------
        raw : bytes
            Raw file content.

        Returns
        -------
        bool
            True if the file appears to be binary STL.

        """
        _header_size = 80
        _count_size = 4
        _triangle_size = 50

        if len(raw) < _header_size + _count_size:
            return False

        (n_triangles,) = struct.unpack_from("<I", raw, _header_size)
        expected = _header_size + _count_size + _triangle_size * n_triangles
        return len(raw) == expected

    @staticmethod
    def _extract_points_binary(raw: bytes) -> np.ndarray:
        """Extract vertex coordinates from a binary STL file.

        Binary STL layout: 80-byte header, 4-byte triangle count,
        then 50 bytes per triangle (12 normal + 36 vertices + 2 attr).

        Parameters
        ----------
        raw : bytes
            Raw file content.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        _header_size = 80
        _count_size = 4
        _triangle_size = 50

        if len(raw) < _header_size + _count_size:
            return np.empty((0, 3))

        (n_triangles,) = struct.unpack_from("<I", raw, _header_size)
        offset = _header_size + _count_size
        points = []

        for _ in range(n_triangles):
            if offset + _triangle_size > len(raw):
                break
            # Skip 12-byte normal, read 3 vertices (each 3 floats = 12 bytes)
            v = struct.unpack_from("<9f", raw, offset + 12)
            points.append([v[0], v[1], v[2]])
            points.append([v[3], v[4], v[5]])
            points.append([v[6], v[7], v[8]])
            offset += _triangle_size

        if not points:
            return np.empty((0, 3))
        return np.array(points)


class GLTFReader:
    """Reader for glTF (GL Transmission Format) files (``.gltf`` or ``.glb``).

    Reads a glTF file and produces a :class:`Mesh` that delegates parsing
    to VTK.wasm's ``vtkGLTFImporter`` at render time. Python extracts
    vertex coordinates from the JSON structure so that camera framing and
    bounding-sphere queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.gltf`` or ``.glb`` file.

    See Also
    --------
    :ref:`using-download-damaged-helmet`
        Interactive browser tutorial for glTF rendering.

    Examples
    --------
    >>> import pyvista_wasm as pv
    >>> reader = pv.GLTFReader("model.gltf")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path, gltf_url: str | None = None) -> None:
        """Initialize the reader with a file path.

        Parameters
        ----------
        path : str or Path
            Path to the ``.gltf`` or ``.glb`` file.
        gltf_url : str or None, optional
            Source URL of the glTF file. When provided, the returned mesh will
            render using the URL directly (avoiding large base64 embedding).

        """
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() not in (".gltf", ".glb"):
            msg = f"Expected a .gltf or .glb file, got: {self._path.suffix}"
            raise ValueError(msg)
        self._gltf_url = gltf_url

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the glTF file.

        """
        return self._path

    def read(self) -> _GLTFMesh:
        """Read the glTF file and return a Mesh.

        The full file content is base64-encoded and stored so that VTK.wasm
        can parse it at render time.  Vertex coordinates are extracted on
        the Python side for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the glTF file content.

        Raises
        ------
        ValueError
            If the file format is invalid.

        """
        raw = self._path.read_bytes()

        # Extract points from glTF JSON structure
        points = self._extract_points(raw)
        gltf_base64 = base64.b64encode(raw).decode("ascii")
        logger.info("Read %d points from %s", len(points), self._path)
        return _GLTFMesh(points=points, gltf_base64=gltf_base64, gltf_url=self._gltf_url)

    @staticmethod
    def _extract_points(raw: bytes) -> np.ndarray:
        """Extract vertex coordinates from glTF file.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by VTK.wasm at render time.

        Parameters
        ----------
        raw : bytes
            Raw content of the glTF file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        # Parse glTF JSON
        try:
            text = raw.decode("utf-8")
            gltf_data = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return np.empty((0, 3))

        # Extract position accessor
        accessor = GLTFReader._get_position_accessor(gltf_data)
        if accessor is None:
            return np.empty((0, 3))

        # Extract bounding box from accessor min/max
        return GLTFReader._extract_bounds_points(accessor)

    @staticmethod
    def _get_position_accessor(gltf_data: dict) -> dict | None:
        """Get the position accessor from glTF data.

        Parameters
        ----------
        gltf_data : dict
            Parsed glTF JSON data.

        Returns
        -------
        dict or None
            The position accessor or None if not found.

        """
        if "meshes" not in gltf_data or not gltf_data["meshes"]:
            return None

        first_mesh = gltf_data["meshes"][0]
        if "primitives" not in first_mesh or not first_mesh["primitives"]:
            return None

        primitives = first_mesh["primitives"][0]
        if "attributes" not in primitives or "POSITION" not in primitives["attributes"]:
            return None

        position_accessor_idx = primitives["attributes"]["POSITION"]
        if "accessors" not in gltf_data or position_accessor_idx >= len(
            gltf_data["accessors"],
        ):
            return None

        return gltf_data["accessors"][position_accessor_idx]

    @staticmethod
    def _extract_bounds_points(accessor: dict) -> np.ndarray:
        """Extract bounding box corners from accessor.

        Parameters
        ----------
        accessor : dict
            The position accessor from glTF.

        Returns
        -------
        np.ndarray
            Array of 8 bounding box corners or empty array.

        """
        if "min" not in accessor or "max" not in accessor:
            return np.empty((0, 3))

        min_vals = accessor["min"]
        max_vals = accessor["max"]
        if len(min_vals) < _N_COORDS or len(max_vals) < _N_COORDS:
            return np.empty((0, 3))

        # Generate 8 corners of bounding box
        points = [
            [x, y, z]
            for x in [min_vals[0], max_vals[0]]
            for y in [min_vals[1], max_vals[1]]
            for z in [min_vals[2], max_vals[2]]
        ]
        return np.array(points)
