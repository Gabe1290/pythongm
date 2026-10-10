"""Regression test for PyGameMaker.spec's _exclude_shadowing_runtime_libs().

Real classroom crash, 2026-10-10: a user's compiled Linux build died the
instant the Blockly tab was opened. Terminal output traced it to PyInstaller
bundling its own (older) libstdc++.so.6, which shadows the system's newer
copy in the onefile's extraction dir -- breaking Mesa's Intel GPU driver
(dlopen of libigdgmm.so.12 failed on a missing GLIBCXX symbol), which broke
EGL/OpenGL context creation, which crashed the Blockly tab's QWebEngineView
(the only thing in this app needing an RHI-backed window). See the function's
own docstring in PyGameMaker.spec for the full chain.

PyGameMaker.spec can't be imported or exec'd wholesale in a test -- calling
Analysis() requires PyInstaller to actually scan the whole project and would
be slow and have real side effects. Instead this extracts just the pure
function definition via AST and execs that single node in an isolated
namespace, so the exact filtering logic the real build uses is tested
directly rather than re-implemented or string-matched.
"""
import ast
from pathlib import Path

import pytest

SPEC_PATH = Path(__file__).parent.parent / "PyGameMaker.spec"


def _load_exclude_function():
    source = SPEC_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SPEC_PATH))
    func_node = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_exclude_shadowing_runtime_libs"
    )
    namespace = {"os": __import__("os")}
    exec(compile(ast.Module(body=[func_node], type_ignores=[]), str(SPEC_PATH), "exec"), namespace)
    return namespace["_exclude_shadowing_runtime_libs"]


@pytest.fixture(scope="module")
def exclude_fn():
    return _load_exclude_function()


def test_function_exists_in_spec():
    # If this fails, the spec no longer defines the function at all --
    # _load_exclude_function()'s own StopIteration would already say so,
    # but a dedicated test gives a clearer failure message.
    assert _load_exclude_function() is not None


def test_bare_libstdcxx_is_excluded(exclude_fn):
    binaries = [("libstdc++.so.6", "/some/src/libstdc++.so.6", "BINARY")]
    assert exclude_fn(binaries) == []


def test_bare_libgcc_s_is_excluded(exclude_fn):
    binaries = [("libgcc_s.so.1", "/some/src/libgcc_s.so.1", "BINARY")]
    assert exclude_fn(binaries) == []


def test_nested_qt_path_libstdcxx_is_still_excluded(exclude_fn):
    """dest paths aren't always bare basenames -- Qt plugins often keep a
    subdirectory structure (e.g. PySide6/Qt/lib/...). The filter must match
    on the basename, not require an exact bare-name match."""
    entry = ("PySide6/Qt/lib/libstdc++.so.6", "/some/src/libstdc++.so.6", "BINARY")
    assert exclude_fn([entry]) == []


def test_unrelated_libraries_are_kept(exclude_fn):
    binaries = [
        ("libQt6Core.so.6", "/some/src/libQt6Core.so.6", "BINARY"),
        ("libstdc++fs.so", "/some/src/libstdc++fs.so", "BINARY"),  # distinct lib, not excluded
        ("_pygame_mixer.so", "/some/src/_pygame_mixer.so", "EXTENSION"),
    ]
    assert exclude_fn(binaries) == binaries


def test_mixed_list_keeps_only_non_shadowing_entries(exclude_fn):
    keep_a = ("libQt6Gui.so.6", "/src/libQt6Gui.so.6", "BINARY")
    keep_b = ("libpng16.so.16", "/src/libpng16.so.16", "BINARY")
    drop_a = ("libstdc++.so.6", "/src/libstdc++.so.6", "BINARY")
    drop_b = ("libgcc_s.so.1", "/src/libgcc_s.so.1", "BINARY")
    result = exclude_fn([keep_a, drop_a, keep_b, drop_b])
    assert result == [keep_a, keep_b]


def test_empty_list_is_a_noop(exclude_fn):
    assert exclude_fn([]) == []


def test_spec_calls_the_filter_on_a_binaries_after_analysis():
    """Mutation guard: the function existing and working in isolation isn't
    enough if the spec never actually calls it. Confirms the real call site
    (a.binaries = _exclude_shadowing_runtime_libs(a.binaries)) is present and
    textually follows the Analysis(...) assignment, not preceding it (a.binaries
    doesn't exist yet before Analysis() runs)."""
    source = SPEC_PATH.read_text(encoding="utf-8")
    analysis_idx = source.index("a = Analysis(")
    call_idx = source.index("a.binaries = _exclude_shadowing_runtime_libs(a.binaries)")
    assert call_idx > analysis_idx
