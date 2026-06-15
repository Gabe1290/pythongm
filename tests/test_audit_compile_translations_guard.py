"""Regression test for M57: compile_translations.should_compile guard.

The language manager prefers split .qm files (pygm2_<lang>_<group>.qm) over
the monolithic pygm2_<lang>.qm whenever ANY split .qm exists. French ships
split .ts files but only the complete monolithic pygm2_fr.qm — compiling the
incomplete fr split .ts set would create split .qm files that hijack the
loader and drop the full translation. should_compile() must refuse to compile
a split *_<group>.ts unless that language already has a split set
(pygm2_<lang>_core.qm on disk).

Pure logic — no Qt/pygame needed.
"""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "compile_translations.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("compile_translations_mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_monolithic_ts_always_compiles(tmp_path):
    mod = _load_module()
    # pygm2_<lang>.ts has exactly two underscore-split parts -> always safe.
    assert mod.should_compile(tmp_path / "pygm2_fr.ts") is True
    assert mod.should_compile(tmp_path / "pygm2_de.ts") is True


def test_split_ts_skipped_when_no_split_set(tmp_path):
    mod = _load_module()
    # French: split .ts present, NO pygm2_fr_core.qm on disk -> must skip.
    for group in ("actions", "blockly", "core", "dialogs", "editors", "misc"):
        (tmp_path / f"pygm2_fr_{group}.ts").write_text("<TS></TS>", encoding="utf-8")
    # Only the monolithic fr .qm exists (the complete hand translation).
    (tmp_path / "pygm2_fr.qm").write_bytes(b"")
    for group in ("actions", "blockly", "core", "dialogs", "editors", "misc"):
        assert mod.should_compile(tmp_path / f"pygm2_fr_{group}.ts") is False, group


def test_split_ts_compiles_when_split_set_exists(tmp_path):
    mod = _load_module()
    # German already uses a split set: pygm2_de_core.qm exists -> compile.
    (tmp_path / "pygm2_de_core.qm").write_bytes(b"")
    for group in ("actions", "blockly", "core", "dialogs", "editors", "misc"):
        (tmp_path / f"pygm2_de_{group}.ts").write_text("<TS></TS>", encoding="utf-8")
        assert mod.should_compile(tmp_path / f"pygm2_de_{group}.ts") is True, group


def test_real_repo_state_french_is_guarded():
    """Against the actual translations/ dir: fr split .ts must be skipped."""
    mod = _load_module()
    trans = REPO_ROOT / "translations"
    fr_core_qm = trans / "pygm2_fr_core.qm"
    fr_actions_ts = trans / "pygm2_fr_actions.ts"
    if not fr_actions_ts.exists():
        return  # translation layout changed; nothing to assert
    if fr_core_qm.exists():
        # If a split set was intentionally introduced for fr, the guard
        # correctly allows compilation; the hazard no longer applies.
        assert mod.should_compile(fr_actions_ts) is True
    else:
        # Current repo state: fr has no split .qm -> guard must skip.
        assert mod.should_compile(fr_actions_ts) is False
        # Monolithic fr stays compilable.
        assert mod.should_compile(trans / "pygm2_fr.ts") is True
