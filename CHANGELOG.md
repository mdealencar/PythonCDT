# Unreleased

- Updated CDT to 2.0.0 (`c888b30`), still fetched by commit ID through CMake.
- Ported the refinement API, triangle collection and finalization methods, winding verification, triangle geometry helpers, and edge ordering from PythonCDT commit `00b219c6`.
- Added matching type stubs, refinement tests with a vendored fixture, and usage examples.

# v0.0.6

[Commit history since v0.0.5](https://github.com/mdealencar/PythonCDT/compare/v0.0.5...v0.0.6)

## Important Changes

- Added `Triangulation.vertices_array()` and `triangles_array()` for structured NumPy arrays. They return copies by default; `copy=False` returns a read-only view that becomes invalid after the triangulation changes.
- Triangulation operations now release the Python GIL, allowing separate triangulations to run on different Python threads. Calls on the same triangulation are serialized. Iterators and `copy=False` views must not be used while another thread modifies their triangulation.
- Vertex and edge buffers must contain pairs in C-contiguous `(N, 2)` or `(2N,)` form. Invalid shapes and noncontiguous buffers now raise an error instead of being interpreted as contiguous pairs.
- NumPy is now a declared runtime dependency. The type stub includes the new array methods, and the README documents array access and threading.

## Packaging & Maintenance

- Added musllinux 1.2 wheel builds, with separate manylinux and musllinux jobs and artifacts to avoid duplicate uploads.
- Updated `setup-python` and `cibuildwheel` for Python 3.15 wheel builds.

# v0.0.5

[Commit history since v0.0.4](https://github.com/mdealencar/PythonCDT/compare/v0.0.4...v0.0.5)

- Updated the CDT source used by the build from v1.4.4 to v1.4.5.
- Fixed `condeltri.__version__` to report the package version instead of `"dev"`.

# v0.0.4

[Commit history since v0.0.3](https://github.com/mdealencar/PythonCDT/compare/v0.0.3...v0.0.4)

- Added PEP 561 typing support through `condeltri.pyi` and `py.typed`, with a check that the stub matches the built extension.
- Updated the triangulation tests with vendored CDT fixtures and corrected expected results.
- Expanded Linux wheel coverage, added tests for each built wheel, and documented the conda-forge package.

# v0.0.3

[Commit history since v0.0.2](https://github.com/mdealencar/PythonCDT/compare/v0.0.2...v0.0.3)

- Updated CDT to v1.4.4.
- Pointed the project metadata to the ConDelTri branch of the repository.

# v0.0.2

Initial ConDelTri release: the PythonCDT fork was renamed and packaged for PyPI with scikit-build-core and wheels for multiple platforms.
