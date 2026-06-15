"""Regression tests for L20: Kivy buildspec package-name sanitizer.

Android applicationIds must be ASCII [a-z0-9_]. The sanitizer previously used
str.isalnum(), which is True for accented letters ('é'.isalnum() == True), so
French project names produced an invalid package name that aapt/gradle reject
late in the buildozer build. The fix folds accents to ASCII via NFKD and drops
any remaining non-ASCII characters.
"""

import re
from pathlib import Path

from export.Kivy.buildspec_generator import BuildspecGenerator

# Valid Android package-segment characters after sanitization.
_ASCII_PKG = re.compile(r'^[a-z0-9_]+$')


def _make(name):
    return BuildspecGenerator({"name": name}, Path("/tmp"))


def test_accented_project_name_yields_ascii_package():
    gen = _make("Labyrinthe de Noël")
    pkg = gen.package_name
    assert _ASCII_PKG.match(pkg), f"package name not ASCII: {pkg!r}"
    # 'ë' should fold to 'e', not survive or become a literal '_'.
    assert "noel" in pkg


def test_apostrophe_and_accents_french_title():
    gen = _make("L'épopée")
    pkg = gen.package_name
    assert _ASCII_PKG.match(pkg), pkg
    assert "epopee" in pkg


def test_all_non_ascii_falls_back_to_default():
    # A name made entirely of non-ASCII (e.g. CJK) leaves nothing after the
    # ASCII fold; must not return an empty / invalid package name.
    gen = _make("日本語")
    assert gen.package_name == "kivygame"


def test_plain_ascii_name_unchanged_behaviour():
    gen = _make("My Cool Game")
    pkg = gen.package_name
    assert _ASCII_PKG.match(pkg), pkg
    assert pkg == "my_cool_game"


def test_leading_digit_still_prefixed():
    # NFKD on a leading accented-but-folds-to-digit is rare; use a real digit.
    gen = _make("3 Petits Cochons")
    pkg = gen.package_name
    assert _ASCII_PKG.match(pkg), pkg
    assert not pkg[0].isdigit()


def test_empty_name_falls_back_to_default():
    gen = _make("")
    assert gen.package_name == "kivygame"
