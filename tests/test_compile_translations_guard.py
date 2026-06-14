"""Regression test for compile_translations split-.qm guard (audit M57).

compile_translations compiled every .ts with no guard, so running it created
split French .qm files (from sparse split .ts) that the loader prefers over the
complete monolithic pygm2_fr.qm — reverting most of the French UI to English.
should_compile now skips a split .ts unless that language already uses a split
set.
"""

from pathlib import Path

from scripts.compile_translations import should_compile


def test_monolithic_always_compiles(tmp_path):
    assert should_compile(tmp_path / "pygm2_fr.ts", tmp_path) is True
    assert should_compile(tmp_path / "pygm2_en.ts", tmp_path) is True


def test_split_skipped_when_no_split_qm(tmp_path):
    # No pygm2_fr_core.qm -> French uses the monolithic set -> skip split .ts.
    assert should_compile(tmp_path / "pygm2_fr_core.ts", tmp_path) is False
    assert should_compile(tmp_path / "pygm2_fr_actions.ts", tmp_path) is False


def test_split_compiles_when_split_qm_exists(tmp_path):
    (tmp_path / "pygm2_de_core.qm").write_bytes(b"")  # German already split
    assert should_compile(tmp_path / "pygm2_de_actions.ts", tmp_path) is True
    assert should_compile(tmp_path / "pygm2_de_core.ts", tmp_path) is True
