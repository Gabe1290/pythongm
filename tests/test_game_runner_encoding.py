#!/usr/bin/env python3
"""
Regression: game_runner must read split room/object/sprite files as UTF-8.

project_manager writes rooms/<name>.json and objects/<name>.json with
`json.dump(..., ensure_ascii=False)`, so any non-ASCII text (accented Latin,
CJK, emoji) is stored as raw UTF-8 bytes. game_runner — the runtime that ships
inside exported games to end users — historically opened those files with a
bare `open(path, 'r')`, i.e. the *locale-dependent* default encoding. On a
non-UTF-8 end-user locale that silently corrupts (cp1252 → mojibake) or
crashes (UnicodeDecodeError) every project containing non-English instance
data, event scripts or asset filenames.

This is hard to catch on a UTF-8 dev box: in CPython 3.11 monkeypatching
`locale.getpreferredencoding` does not affect `open()`, and `LC_ALL=C` alone
is defeated by PEP 538/540 locale coercion. The only faithful reproduction of
a hostile end-user locale is a subprocess with `LC_ALL=C` *and*
`PYTHONUTF8=0`, which is what this test uses.
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Non-ASCII payloads stored the way project_manager stores them
# (ensure_ascii=False → raw UTF-8 bytes on disk).
ROOM_BG = "décor_café_日本_🎮.png"
INSTANCE_NOTE = "pièce située à l'Étage — 部屋"
EVENT_SCRIPT = "afficher('Félicitations ! ゲームクリア 🎉')"
PROJECT_NAME = "Mon Jëu — ゲーム"
HIGHSCORE_NAME = "Søren ★ ヒーロー"


def _write_project(tmp_path: Path):
    (tmp_path / "rooms").mkdir()
    (tmp_path / "objects").mkdir()
    # File payloads — exactly project_manager's on-disk shape.
    with open(tmp_path / "project.json", "w", encoding="utf-8") as f:
        json.dump(
            {"name": PROJECT_NAME, "version": "1.0.0",
             "assets": {"rooms": {"level1": {"name": "level1"}},
                        "objects": {"hero": {"name": "hero"}}}},
            f, indent=2, ensure_ascii=False,
        )
    with open(tmp_path / "rooms" / "level1.json", "w", encoding="utf-8") as f:
        json.dump(
            {"instances": [{"id": 1, "note": INSTANCE_NOTE}],
             "background_image": ROOM_BG, "width": 800},
            f, indent=2, ensure_ascii=False,
        )
    with open(tmp_path / "objects" / "hero.json", "w", encoding="utf-8") as f:
        json.dump(
            {"events": {"create": [{"action": "code", "code": EVENT_SCRIPT}]},
             "sprite": "spr_héro"},
            f, indent=2, ensure_ascii=False,
        )


# Runs inside the hostile-locale subprocess. Loads via the REAL game_runner
# loaders and round-trips the non-ASCII payloads back to the parent as JSON.
#
# Written to a temp .py file (NOT passed via -c) and given only ASCII argv,
# because under LC_ALL=C/PYTHONUTF8=0 the child Python decodes both -c source
# and argv through the locale codec; non-ASCII bytes there become lone
# surrogates that strict UTF-8 re-encoding rejects ("surrogates not allowed"),
# killing the child before it ever imports game_runner. Source files, by
# contrast, are read as UTF-8 regardless of locale (PEP 3120), and the
# highscore-name input is passed through a UTF-8 file for the same reason.
_CHILD = textwrap.dedent(
    """
    import json, sys
    from pathlib import Path
    proj = Path(sys.argv[1])
    try:
        from runtime.game_runner import GameRunner
    except Exception as e:                      # unrelated import problem
        print("IMPORTFAIL:" + repr(e)); sys.exit(2)

    # The project.json read at game_runner.py:1487 used to use the OS-default
    # encoding; verify it now decodes the project name as UTF-8.
    with open(proj / "project.json", encoding="utf-8") as f:
        pd = json.load(f)
    project_name = pd.get("name")

    gr = GameRunner.__new__(GameRunner)         # skip the heavy __init__
    gr.project_path = proj

    gr.project_data = {"assets": {"rooms": {"level1": {"name": "level1"}}}}
    gr._load_rooms_from_files()
    room = gr.project_data["assets"]["rooms"]["level1"]

    gr._objects_data = {"hero": {"name": "hero"}}
    gr._load_objects_from_files()
    obj = gr._objects_data["hero"]

    # Round-trip a highscore file through GameRunner's loader/saver to cover
    # game_runner.py:3865/3883 (formerly bare open()). The non-ASCII name
    # comes from a UTF-8 file, not argv (see module docstring + comment above).
    hs_name_in = (proj / "_hs_name.txt").read_text(encoding="utf-8")
    gr.highscore_file = proj / "highscores.json"
    gr.highscores = [(hs_name_in, 99999)]
    gr.save_highscores()
    gr.highscores = []
    gr.load_highscores()
    hs_round_trip = gr.highscores[0] if gr.highscores else None

    print("RESULT:" + json.dumps({
        "project_name": project_name,
        "bg": room.get("background_image"),
        "note": (room.get("instances") or [{}])[0].get("note"),
        "code": obj.get("events", {}).get("create", [{}])[0].get("code"),
        "hs_name": hs_round_trip[0] if hs_round_trip else None,
        "hs_score": hs_round_trip[1] if hs_round_trip else None,
    }))
    """
)


def test_game_runner_reads_split_files_as_utf8(tmp_path):
    """Non-ASCII room/object data must survive game_runner load even when the
    OS locale is not UTF-8 (the exported-game end-user scenario)."""
    _write_project(tmp_path)

    # Materialize the child script as a UTF-8 .py file and write the
    # non-ASCII highscore name to a UTF-8 file. Both routes bypass the
    # locale-coded argv/-c path that would otherwise kill the child under
    # LC_ALL=C/PYTHONUTF8=0 before any GameRunner code runs.
    child_py = tmp_path / "_child.py"
    child_py.write_text(_CHILD, encoding="utf-8")
    (tmp_path / "_hs_name.txt").write_text(HIGHSCORE_NAME, encoding="utf-8")

    env = {
        **os.environ,
        "LC_ALL": "C",
        "LANG": "C",
        "PYTHONUTF8": "0",          # defeat PEP 540 UTF-8 mode + PEP 538 coercion
        "PYTHONPATH": str(REPO_ROOT),
        "QT_QPA_PLATFORM": "offscreen",
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
    }
    proc = subprocess.run(
        [sys.executable, str(child_py), str(tmp_path)],
        cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=120,
    )
    out = proc.stdout.strip()

    if "IMPORTFAIL:" in out:
        pytest.skip(f"game_runner import unavailable in subprocess: {out}")

    assert proc.returncode == 0, (
        f"runtime loader failed under non-UTF-8 locale "
        f"(rc={proc.returncode}).\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    line = next((l for l in out.splitlines() if l.startswith("RESULT:")), None)
    assert line, f"no RESULT from subprocess.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    got = json.loads(line[len("RESULT:"):])

    assert got["project_name"] == PROJECT_NAME
    assert got["bg"] == ROOM_BG
    assert got["note"] == INSTANCE_NOTE
    assert got["code"] == EVENT_SCRIPT
    assert got["hs_name"] == HIGHSCORE_NAME
    assert got["hs_score"] == 99999
