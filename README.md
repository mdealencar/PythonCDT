# ConDelTri: Constrained Delaunay Triangulation

This is a rebranded fork of [PythonCDT](https://github.com/artem-ogre/PythonCDT) by Leica Geosystems, maintained by [Artem Amirkhanov](https://github.com/artem-ogre).

Python bindings for [CDT: C++ library for constrained Delaunay triangulation](https://github.com/artem-ogre/CDT) implemented with [pybind11](https://github.com/pybind/pybind11)

## Installation

```
pip install condeltri
```
Or:
```
conda install --channel=conda-forge condeltri
```

## Usage

```python
import numpy as np
import condeltri as cdt

t = cdt.Triangulation(cdt.VertexInsertionOrder.AUTO, cdt.IntersectingConstraintEdges.TRY_RESOLVE, 0.0)
t.insert_vertices(np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]))
t.insert_edges(np.array([[0, 3]], dtype=np.uintc))
t.erase_super_triangle()

vertices = t.vertices_array()    # structured array with fields 'x' and 'y'
triangles = t.triangles_array()  # structured array with fields 'vertices' and 'neighbors'
triangles["vertices"]            # (T, 3) vertex indices into vertices
```

`vertices_array()` and `triangles_array()` return copies by default. Pass `copy=False` for read-only views without copying. A view becomes invalid after any call that changes the triangulation. Vertex and edge input arrays must be C-contiguous with shape `(N, 2)` or `(2N,)`.

### Threads

Triangulation work releases Python's GIL, so separate triangulations can run in parallel on Python threads. Calls on one triangulation wait for each other. Iterators (`*_iter()`) and `copy=False` views are not protected while another thread changes the triangulation.

## License
[Mozilla Public License, v. 2.0](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)

## Contributors
- [SioulisChris](https://github.com/SioulisChris): fixing the tests on Windows
