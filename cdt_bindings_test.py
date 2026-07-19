#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

""" Tests for CDT Python bindings """

import numpy as np
import pytest
import tempfile
import hashlib
from pathlib import Path

import condeltri as cdt

# fixtures vendored from CDT's visualizer/data (see test_data/README.md)
DATA_DIR = Path(__file__).parent / "test_data"


def test_constants() -> None:
    """Test that constants have proper values"""
    assert cdt.NO_NEIGHBOR == np.iinfo(np.uintc).max, "NO_NEIGHBOR constant has wrong value"
    assert cdt.NO_VERTEX == np.iinfo(np.uintc).max, "NO_VERTEX constant has wrong value"


def test_V2d() -> None:
    """Test 2D vector"""
    p = cdt.V2d(42, 42)
    assert p.x == 42 and p.y == 42, "Error in constructing 2D vector with int"
    p = cdt.V2d(42.0, 42.0)
    assert p.x == 42 and p.y == 42, "Error in constructing 2D vector with float"
    p = cdt.V2d(np.array([42., 42.]))
    assert p.x == 42 and p.y == 42, "Error in constructing 2D vector with buffer protocol"

    assert cdt.V2d(1.23, 2).__repr__() == "V2d(1.23, 2)", "Wrong __repr__ output for V2d"


def test_Edge() -> None:
    """Test Edge class"""
    e = cdt.Edge(1, 2)
    assert e.v1 == 1 and e.v2 == 2, "Constructed wrong edge"
    e = cdt.Edge(2, 1)
    assert e.v1 == 1 and e.v2 == 2, "Constructed wrong edge"
    e = cdt.Edge(np.array([2, 1], dtype=np.uintc))
    assert e.v1 == 1 and e.v2 == 2, "Constructed wrong edge"

    assert cdt.Edge(1, 2).__repr__() == "Edge(1, 2)", "Wrong __repr__ output for Edge"


def test_Triangulation() -> None:
    """Test Triangulation class"""
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.NOT_ALLOWED, 0.0)
    assert len(t.vertices) == 0, "Wrong vertex count in empty triangulation"
    assert len(t.triangles) == 0, "Wrong triangle count in empty triangulation"
    assert len(t.fixed_edges) == 0, "Wrong fixed edge count in empty triangulation"

    vv = [cdt.V2d(-1, 0), cdt.V2d(0, 0.5), cdt.V2d(1, 0), cdt.V2d(0, -0.5)]
    t.insert_vertices(vv)
    assert len(t.vertices) == 7, "Wrong vertex count in triangulation"
    assert len(t.triangles) == 9, "Wrong triangle count in triangulation"
    assert len(t.fixed_edges) == 0, "Wrong fixed edge count in triangulation"

    ee = [cdt.Edge(0, 2)]
    t.insert_edges(ee)
    assert len(t.fixed_edges) == 1, "Wrong fixed edge count in triangulation"
    assert cdt.Edge(0 + 3, 2 + 3) in t.fixed_edges, "Constraint edge was not properly added"

    t.erase_super_triangle()
    assert cdt.Edge(0, 2) in t.fixed_edges, "Constraint edge was not properly added"
    assert len(t.vertices) == 4, "Wrong vertex count in triangulation"
    assert len(t.triangles) == 2, "Wrong triangle count in triangulation"
    assert len(t.fixed_edges) == 1, "Wrong fixed edge count in triangulation"

    # test retrieving triangulation data using iterators
    assert t.vertices_count() == len(t.vertices), "Wrong vertex count"
    assert t.triangles_count() == len(t.triangles), "Wrong triangle count"
    assert t.fixed_edges_count() == len(t.fixed_edges), "Wrong fixed edge count"
    assert t.overlap_count_count() == len(t.overlap_count), "Wrong number of overlap-count"
    assert t.piece_to_originals_count() == len(t.piece_to_originals), "Wrong piece-to-originals count"
    for i, v in enumerate(t.vertices_iter()):
        assert v == t.vertices[i], "Wrong vertex from iterable"
    for i, tri in enumerate(t.triangles_iter()):
        assert tri == t.triangles[i], "Wrong triangle from iterable"
    for fe in t.fixed_edges_iter():
        assert fe in t.fixed_edges, "Wrong fixed edges from iterable"
    for key, val in t.overlap_count_iter():
        assert t.overlap_count[key] == val, "Wrong overlap-count from iterable"
    for key, val in t.piece_to_originals_iter():
        assert t.piece_to_originals[key] == val, "Wrong piece-to-originals from iterable"

    #  Test resolving fixed edge intersections
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.TRY_RESOLVE, 0.0)
    ee = [cdt.Edge(0, 2), cdt.Edge(1, 3)]
    t.insert_vertices(vv)
    t.insert_edges(ee)
    t.erase_super_triangle()
    assert len(t.vertices) == 5, "Wrong vertex count in triangulation"
    assert len(t.triangles) == 4, "Wrong triangle count in triangulation"


def test_verify_topology() -> None:
    """Test verifying CDT topology"""
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.TRY_RESOLVE, 0.0)
    t.insert_vertices([cdt.V2d(-1, 0), cdt.V2d(0, 0.5), cdt.V2d(1, 0), cdt.V2d(0, -0.5)])
    t.insert_edges([cdt.Edge(0, 2), cdt.Edge(1, 3)])
    assert cdt.verify_topology(t), "Verifying topology produced wrong result"


def save_triangulation_as_off(t: cdt.Triangulation, off_file) -> None:
    with open(off_file, "w") as f:
        f.write(f"OFF\n")
        f.write(f"{t.vertices_count()} {t.triangles_count()} 0\n")
        for v in t.vertices_iter():
            f.write(f"{v.x} {v.y} 0\n")
        for tri in t.triangles_iter():
            vv = tri.vertices
            f.write(f"3 {int(vv[0])} {int(vv[1])} {int(vv[2])}\n")


def read_input_file(input_file):
    with open(input_file, "r") as f:
        n_verts, n_edges = (int(s) for s in f.readline().split())
        verts = [cdt.V2d(*(float(s) for s in f.readline().split())) for _ in range(n_verts)]
        edges = [cdt.Edge(*(int(s) for s in f.readline().split())) for _ in range(n_edges)]
        return verts, edges

def md5_checksum(file_path):
    with open(file_path, 'r') as f:
        return hashlib.md5(f.read().encode('utf-8')).hexdigest()

def triangulation_md5_checksum(t: cdt.Triangulation):
    with tempfile.TemporaryDirectory() as tmp_dir:
        off_file = f"{tmp_dir}/cdt.off"
        save_triangulation_as_off(t, off_file)
        return md5_checksum(off_file)


def triangles_of(t: cdt.Triangulation):
    """Triangles as a canonical, order-independent set of vertex-index triples.

    CDT is free to emit triangles in any order, and to name a triangle's
    vertices starting from any of its three corners, without the triangulation
    being any different. Sorting both levels compares the topology itself.
    """
    return sorted(tuple(sorted(int(i) for i in tri.vertices)) for tri in t.triangles_iter())


def fixed_edges_of(t: cdt.Triangulation):
    """Fixed edges as a canonical, order-independent set of index pairs."""
    return sorted(tuple(sorted((e.v1, e.v2))) for e in t.fixed_edges_iter())


def assert_vertices(t: cdt.Triangulation, expected, skip: int = 0) -> None:
    """Assert the vertex coordinates, comparing floats with a tolerance.

    `skip` drops leading vertices from the comparison, used to ignore the
    super-triangle: its coordinates are CDT's own scratch geometry and have
    changed between CDT releases without the triangulation being any different.
    """
    got = [c for v in list(t.vertices_iter())[skip:] for c in (v.x, v.y)]
    assert got == pytest.approx([c for xy in expected for c in xy]), "Wrong vertex coordinates"

def test_triangulate_input_file() -> None:
    vv, ee = read_input_file(DATA_DIR / "Constrained Sweden.txt")
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.TRY_RESOLVE, 0.0)
    t.insert_vertices(vv)
    t.insert_edges(ee)
    t.erase_outer_triangles_and_holes()
    assert t.vertices_count() == 2619, "Wrong vertex count in triangulation"
    assert t.triangles_count() == 2580, "Wrong triangle count in triangulation"
    assert t.fixed_edges_count() == 2619, "Wrong fixed edge count in triangulation"
    assert cdt.verify_topology(t), "Verifying topology produced wrong result"
    # At 2619 vertices the connectivity is too large to assert on directly, so
    # this one case keeps a digest as a regression tripwire. Unlike the smaller
    # tests it is sensitive to vertex ordering and float formatting: re-record
    # it when the CDT pin in CMakeLists.txt moves, after checking the counts and
    # verify_topology above still hold.
    assert triangulation_md5_checksum(t) == 'db59c00d9dad866781cd96779e5262b7', "Wrong OFF file contents"


def test_conform_to_edges() -> None:
    vv, ee = read_input_file(DATA_DIR / "ditch.txt")
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.TRY_RESOLVE, 0.0)
    t.insert_vertices(vv)
    t.conform_to_edges(ee)
    t.erase_outer_triangles_and_holes()
    assert len(t.vertices) == 14, "Wrong vertex count in triangulation"
    assert len(t.triangles) == 15, "Wrong triangle count in triangulation"
    assert len(t.fixed_edges) == 15, "Wrong fixed edge count in triangulation"
    assert cdt.verify_topology(t), "Verifying topology produced wrong result"
    # The 11 input vertices come first and unchanged; conforming splits the
    # three constraint edges that cross the ditch, appending their midpoints.
    assert_vertices(t, [
        (15.2817039560085, -35.8482583312558), (16.9298083110526, -19.5320252163193),
        (15.2817039560085, 0.9044687862274401), (17.5890500530702, 18.044754078686),
        (16.1057561335305, 40.7061889605422), (-16.6915205318468, -35.6010426779992),
        (-14.3017692170329, -14.9173330221958), (-14.9610109590506, 14.006898408828),
        (-15.0434161768028, 37.9044115569673), (1.27281693813374, -36.0954739845124),
        (1.27281693813374, 40.62378374279), (1.27281693813374, 2.2641548791388004),
        (1.27281693813374, -16.9156595526868), (1.27281693813374, 21.443969310964402)])
    assert triangles_of(t) == [
        (0, 1, 9), (1, 2, 12), (1, 9, 12), (2, 3, 11), (2, 11, 12), (3, 4, 13), (3, 11, 13),
        (4, 10, 13), (5, 6, 12), (5, 9, 12), (6, 7, 11), (6, 11, 12), (7, 8, 13), (7, 11, 13),
        (8, 10, 13)], "Wrong triangle connectivity"
    assert fixed_edges_of(t) == [
        (0, 1), (0, 9), (1, 2), (2, 3), (3, 4), (4, 10), (5, 6), (5, 9), (6, 7), (7, 8),
        (8, 10), (9, 12), (10, 13), (11, 12), (11, 13)], "Wrong fixed edges"


@pytest.mark.parametrize("vv", [[cdt.V2d(-1, 0), cdt.V2d(0, 0.5), cdt.V2d(1, 0), cdt.V2d(0, -0.5)],
                                np.array([[-1, 0], [0, 0.5], [1, 0], [0, -0.5]], dtype=np.float64),
                                np.array([-1, 0, 0, 0.5, 1, 0, 0, -0.5], dtype=np.float64)])
def test_insert_vertices(vv) -> None:
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.NOT_ALLOWED, 0.0)
    t.insert_vertices(vv)
    assert len(t.vertices) == 7, "Wrong vertex count in triangulation"
    assert len(t.triangles) == 9, "Wrong triangle count in triangulation"
    assert len(t.fixed_edges) == 0, "Wrong fixed edge count in triangulation"
    assert cdt.verify_topology(t), "Verifying topology produced wrong result"
    # The three super-triangle vertices come first, then the four inputs
    # unchanged. The super-triangle's own coordinates are CDT's choice and are
    # deliberately not asserted on; erase_super_triangle below drops them.
    assert_vertices(t, [(-1.0, 0.0), (0.0, 0.5), (1.0, 0.0), (0.0, -0.5)], skip=3)
    assert triangles_of(t) == [
        (0, 1, 6), (0, 2, 3), (0, 3, 6), (1, 2, 5), (1, 5, 6),
        (2, 3, 4), (2, 4, 5), (3, 4, 6), (4, 5, 6)], "Wrong triangle connectivity"

    t.erase_super_triangle()
    assert_vertices(t, [(-1.0, 0.0), (0.0, 0.5), (1.0, 0.0), (0.0, -0.5)])
    assert triangles_of(t) == [(0, 1, 3), (1, 2, 3)], "Wrong triangle connectivity"


@pytest.mark.parametrize("ee", [[cdt.Edge(0, 1), cdt.Edge(2, 3), cdt.Edge(3, 4), cdt.Edge(5, 6)],
                                np.array([[0, 1], [2, 3], [3, 4], [5, 6]], dtype=np.uintc),
                                np.array([0, 1, 2, 3, 3, 4, 5, 6], dtype=np.uintc)])
def test_insert_conform_edges(ee) -> None:
    pts = [(0, 0), (4, 0), (5, 1), (2, 1), (-1, 1), (0, 2), (4, 2)]

    # insert edges
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.NOT_ALLOWED, 0.0)
    t.insert_vertices(np.array(pts, dtype=float))
    t.insert_edges(ee)
    assert len(t.vertices) == 10, "Wrong vertex count in triangulation"
    assert len(t.triangles) == 15, "Wrong triangle count in triangulation"
    assert len(t.fixed_edges) == 4, "Wrong fixed edge count in triangulation"
    assert cdt.verify_topology(t), "Verifying topology produced wrong result"
    assert_vertices(t, pts, skip=3)
    assert triangles_of(t) == [
        (0, 1, 4), (0, 2, 8), (0, 3, 4), (0, 3, 7), (0, 7, 8), (1, 2, 9), (1, 4, 5), (1, 5, 9),
        (2, 8, 9), (3, 4, 6), (3, 6, 7), (4, 5, 6), (5, 6, 9), (6, 7, 8), (6, 8, 9),
    ], "Wrong triangle connectivity"
    # the requested constraints, shifted by the three super-triangle vertices
    assert fixed_edges_of(t) == [(3, 4), (5, 6), (6, 7), (8, 9)], "Wrong fixed edges"

    # conform to edges
    t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.NOT_ALLOWED, 0.0)
    t.insert_vertices(np.array(pts, dtype=float))
    t.conform_to_edges(ee)
    assert len(t.vertices) == 12, "Wrong vertex count in triangulation"
    assert len(t.triangles) == 19, "Wrong triangle count in triangulation"
    assert len(t.fixed_edges) == 6, "Wrong fixed edge count in triangulation"
    assert cdt.verify_topology(t), "Verifying topology produced wrong result"
    # conforming splits edges (2,3) and (3,4) at their midpoints, appending
    # (3.5, 1) on (5,1)-(2,1) and (0.5, 1) on (2,1)-(-1,1)
    assert_vertices(t, [*pts, (3.5, 1.0), (0.5, 1.0)], skip=3)
    assert triangles_of(t) == [
        (0, 1, 4), (0, 2, 8), (0, 3, 4), (0, 3, 7), (0, 7, 8), (1, 2, 9), (1, 4, 5), (1, 5, 9),
        (2, 8, 9), (3, 4, 6), (3, 6, 11), (3, 7, 11), (4, 5, 10), (4, 6, 10), (5, 9, 10),
        (6, 8, 9), (6, 8, 11), (6, 9, 10), (7, 8, 11),
    ], "Wrong triangle connectivity"
    assert fixed_edges_of(t) == [
        (3, 4), (5, 10), (6, 10), (6, 11), (7, 11), (8, 9)], "Wrong fixed edges"
