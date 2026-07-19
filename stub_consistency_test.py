#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Guard condeltri.pyi against drifting from the compiled module.

condeltri.pyi is hand-written, so nothing but this test stops it from going
stale when cdt_bindings.cpp gains, loses or renames a binding. The stub is what
every downstream type checker reads instead of the extension, so a stale one is
worse than none: it reports confident, wrong types.

The comparison is of *names*, not signatures: the public top-level attributes of
the module, and the public members each class defines itself. That catches the
realistic drift (a binding added to the .cpp and forgotten in the stub, or a
stub entry left behind after a binding is removed). It does not catch a changed
parameter or return type -- those still need review of the .pyi when touching
the .cpp.

Runtime members come from `vars(cls)`, not `dir(cls)`, so only what pybind11
defines on the class is compared and inherited machinery stays out of it.
"""

import ast
import pathlib

import pytest

import condeltri as cdt

STUB_PATH = pathlib.Path(__file__).with_name('condeltri.pyi')

# `name` and `value` are pybind11 enum members at run time; in the stub they
# come from the `enum.IntEnum` base it declares, so they are never spelled out.
ENUM_INHERITED = frozenset({'name', 'value'})


def _public(names) -> set:
    """Drop private and dunder names, which the stub deliberately omits."""
    return {n for n in names if not n.startswith('_')}


def _stub_module() -> ast.Module:
    assert STUB_PATH.is_file(), f'type stub is missing: {STUB_PATH}'
    return ast.parse(STUB_PATH.read_text(encoding='utf8'), filename=str(STUB_PATH))


def _declared_names(body) -> set:
    """Names bound by a stub body: defs, annotated names and plain assignments."""
    names = set()
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            # NO_VERTEX: int   /   x: float
            names.add(node.target.id)
        elif isinstance(node, ast.Assign):
            # enum members: AUTO = 0
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return _public(names)


def _stub_class(name: str) -> ast.ClassDef:
    for node in _stub_module().body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f'class {name!r} is missing from {STUB_PATH.name}')


def _runtime_classes() -> list:
    return sorted(
        n for n in _public(dir(cdt)) if isinstance(getattr(cdt, n), type)
    )


def test_stub_exists_and_parses() -> None:
    """The stub must be present and syntactically valid Python."""
    assert _stub_module().body, f'{STUB_PATH.name} is empty'


def test_module_attributes_match_stub() -> None:
    """Every public module attribute is declared in the stub, and vice versa."""
    runtime = _public(dir(cdt))
    stub = _declared_names(_stub_module().body)

    if runtime - stub:
        pytest.fail(
            f'{STUB_PATH.name} is missing module attributes present in the '
            f'extension: {sorted(runtime - stub)}'
        )
    if stub - runtime:
        pytest.fail(
            f'{STUB_PATH.name} declares module attributes the extension does '
            f'not have: {sorted(stub - runtime)}'
        )


@pytest.mark.parametrize('class_name', _runtime_classes())
def test_class_members_match_stub(class_name: str) -> None:
    """Every public member pybind11 defines on a class is declared in the stub."""
    cls = getattr(cdt, class_name)
    runtime = _public(vars(cls))
    stub = _declared_names(_stub_class(class_name).body) | ENUM_INHERITED

    if runtime - stub:
        pytest.fail(
            f'{STUB_PATH.name}: class {class_name} is missing members present '
            f'in the extension: {sorted(runtime - stub)}'
        )
    if stub - runtime - ENUM_INHERITED:
        pytest.fail(
            f'{STUB_PATH.name}: class {class_name} declares members the '
            f'extension does not have: '
            f'{sorted(stub - runtime - ENUM_INHERITED)}'
        )
