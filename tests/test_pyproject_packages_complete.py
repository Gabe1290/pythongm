"""Regression test: pyproject.toml's [tool.setuptools] packages list must
name every real, git-tracked Python package under the top-level source
directories -- no more, no less.

Found live: a GitHub Actions "Build Python Package" run failed with
``error: package directory 'export/Aseba' does not exist`` -- the Aseba
exporter moved to extensions/thymio/export/ (docs/THYMIO_EXTENSION_PLAN.md
Stage D) but the old export.Aseba entry was never removed from this list.
Investigating the same list for other drift (same class of bug, same
file) found four more real packages that had quietly gone missing across
earlier refactors -- core.ide, editors.block_world_editor,
editors.object_editor.events, export.desktop -- none of which raise a
build error (setuptools just silently omits them), so a `pip install .`
build would have shipped a broken package (ImportError at runtime, e.g.
core/ide_window.py importing from core.ide.*) with no CI signal at all.

extensions/* is deliberately excluded from this check: folder extensions
(raycast_2_5d, thymio, multiplayer_lan) are loaded dynamically at
runtime under a synthetic package name (events/plugin_loader.py), not
installed as ordinary importable sub-packages, so they were never meant
to be in this list -- unlike the five gaps above, which really are.
"""
import tomllib
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Top-level source directories this project's packages actually live
# under (mirrors the directories pyproject.toml's own packages list
# draws from). extensions/ is excluded -- see module docstring.
TOP_LEVEL_SOURCE_DIRS = {
    "actions", "config", "core", "dialogs", "editors", "export",
    "importers", "plugins", "runtime", "utils", "widgets",
}


def _listed_packages():
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return set(data["tool"]["setuptools"]["packages"])


def _real_packages():
    """Every git-tracked directory (under TOP_LEVEL_SOURCE_DIRS) that has
    its own __init__.py, as a dotted package path."""
    result = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True,
        cwd=REPO_ROOT, check=True,
    )
    packages = set()
    for line in result.stdout.splitlines():
        if not line.endswith("__init__.py"):
            continue
        pkg_dir = Path(line).parent
        if str(pkg_dir) == ".":
            continue
        top = pkg_dir.parts[0]
        if top in TOP_LEVEL_SOURCE_DIRS:
            packages.add(".".join(pkg_dir.parts))
    return packages


def test_every_real_package_is_listed():
    listed = _listed_packages()
    real = _real_packages()
    missing = sorted(real - listed)
    assert not missing, (
        f"pyproject.toml's packages list is missing {missing} -- a "
        "pip-built package would silently omit these at build time "
        "(no error), shipping a broken package. Add them to "
        "[tool.setuptools] packages."
    )


def test_no_listed_package_is_stale():
    """The inverse of the Aseba bug: every listed package must actually
    exist as a real, git-tracked directory with its own __init__.py."""
    listed = _listed_packages()
    real = _real_packages()
    stale = sorted(listed - real)
    assert not stale, (
        f"pyproject.toml lists {stale} as a package, but it no longer "
        "exists (or has no __init__.py) in the tracked source tree -- "
        "this is exactly the bug that broke the 'Build Python Package' "
        "GitHub Actions job (export.Aseba moved to "
        "extensions/thymio/export/ and was never removed from this "
        "list). Remove it from [tool.setuptools] packages."
    )
