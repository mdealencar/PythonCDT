# Test fixtures

`Capital A.txt`, `Constrained Sweden.txt` and `ditch.txt` are copied verbatim from the upstream
CDT repository, from `visualizer/data/` at the revision pinned in
`CMakeLists.txt`:

    https://github.com/artem-ogre/CDT
    c888b30d83312114d3ff332855a97fd95ce95f17 (2.0.0)

CDT is distributed under the Mozilla Public License 2.0, the same licence as
this project. Copyright (c) 2019 Leica Geosystems Technology AB.

They are vendored rather than read out of the CMake `FetchContent` build tree so
that `cdt_bindings_test.py` can run from a plain checkout, independent of the
working directory. If the CDT pin in `CMakeLists.txt` is bumped, re-copy these
files from the new revision and re-check the expected digests in the test.
