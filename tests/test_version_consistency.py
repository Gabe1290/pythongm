"""Every place the shipped version number appears must agree.

A release bump (see CLAUDE.md's 2026-09-04 / 2026-09-28 session notes) is a
sed sweep across several files -- __init__.py x3, pyproject.toml,
version_info.txt, PyGameMaker.spec, main.py's applicationVersion, and
README.md's version badge -- plus two README *prose* spots (the "Download
PyGameMaker X.Y" heading and the "Version X.Y is here" line right under it)
that aren't a version-number sed target at all, just text a human has to
remember to edit by hand. Twice now (the 1.2 bump per the 2026-09-04 note,
then the 1.4.0 bump) the badge got updated and the prose didn't, so GitHub's
front page told visitors to download a version older than the one actually
released. This test makes that a CI failure instead of something a session
happens to notice.

pyproject.toml is treated as the source of truth (arbitrary but has to be
something); every other location is asserted equal to it.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _read(name):
    return (REPO / name).read_text(encoding="utf-8")


def _pyproject_version():
    m = re.search(r'^version\s*=\s*"([\d.]+)"', _read("pyproject.toml"), re.M)
    assert m, "pyproject.toml: no [project] version= line found"
    return m.group(1)


VERSION = _pyproject_version()
MAJOR_MINOR = ".".join(VERSION.split(".")[:2])  # "1.4.0" -> "1.4"


def test_pyproject_version_looks_sane():
    assert re.fullmatch(r"\d+\.\d+\.\d+", VERSION), VERSION


def test_dunder_versions_match_pyproject():
    for rel in ("__init__.py", "core/__init__.py", "utils/__init__.py"):
        src = _read(rel)
        m = re.search(r'^__version__\s*=\s*"([\d.]+)"', src, re.M)
        assert m, f"{rel}: no __version__ = \"...\" line found"
        assert m.group(1) == VERSION, f"{rel} __version__ is {m.group(1)!r}, pyproject.toml is {VERSION!r}"


def test_version_info_txt_matches_pyproject():
    src = _read("version_info.txt")
    parts = tuple(int(p) for p in VERSION.split("."))
    assert f"filevers=({parts[0]}, {parts[1]}, {parts[2]}, 0)" in src, \
        f"version_info.txt filevers doesn't match {VERSION}"
    assert f"prodvers=({parts[0]}, {parts[1]}, {parts[2]}, 0)" in src, \
        f"version_info.txt prodvers doesn't match {VERSION}"
    assert f"u'FileVersion', u'{VERSION}'" in src
    assert f"u'ProductVersion', u'{VERSION}'" in src


def test_pyinstaller_spec_matches_pyproject():
    m = re.search(r"^VERSION\s*=\s*'([\d.]+)'", _read("PyGameMaker.spec"), re.M)
    assert m, "PyGameMaker.spec: no VERSION = '...' line found"
    assert m.group(1) == VERSION


def test_main_py_application_version_matches_pyproject():
    m = re.search(r'setApplicationVersion\("([\d.]+)"\)', _read("main.py"))
    assert m, "main.py: no app.setApplicationVersion(\"...\") call found"
    assert m.group(1) == VERSION


def test_readme_badge_matches_pyproject():
    m = re.search(r"badge/version-([\d.]+)-blue", _read("README.md"))
    assert m, "README.md: no version badge found"
    assert m.group(1) == VERSION, \
        f"README badge is {m.group(1)!r}, pyproject.toml is {VERSION!r}"


def test_readme_download_prose_matches_pyproject():
    """The bug this test exists for: the badge (previous test) got bumped and
    these two hand-written lines didn't, twice. Checked against MAJOR_MINOR
    ("1.4"), matching how the prose has always been phrased (never the patch
    digit)."""
    readme = _read("README.md")
    m = re.search(r"^## .*Download PyGameMaker ([\d.]+)\s*$", readme, re.M)
    assert m, "README.md: no '## ... Download PyGameMaker X.Y' heading found"
    assert m.group(1) == MAJOR_MINOR, \
        f"README download heading says {m.group(1)!r}, expected {MAJOR_MINOR!r} (pyproject.toml is {VERSION!r})"

    m = re.search(r"\*\*Version ([\d.]+) is here\*\*", readme)
    assert m, "README.md: no '**Version X.Y is here**' line found"
    assert m.group(1) == MAJOR_MINOR, \
        f"README 'Version ... is here' line says {m.group(1)!r}, expected {MAJOR_MINOR!r}"


def test_changelog_top_entry_matches_pyproject():
    """The topmost dated [x.y.z] entry (skipping an [Unreleased] header, if
    present) must be the shipped version -- not a stale patch bump nor a
    forgotten empty [Unreleased] left behind after the entry was written."""
    changelog = _read("CHANGELOG.md")
    m = re.search(r"^## \[([\d.]+)\]", changelog, re.M)
    assert m, "CHANGELOG.md: no '## [x.y.z]' entry found"
    assert m.group(1) == VERSION, \
        f"CHANGELOG.md's top dated entry is [{m.group(1)}], expected [{VERSION}]"
