"""Regression test locking in the current state of GMK import for
treasure/maze_4 (docs/GMK_IMPORTER_HARDENING_PLAN.md, Tier 3 item 8).

Both samples were dropped from the bundled set in rc.12 after user
testing surfaced action-parameter/mapping bugs; their .gmk sources were
recovered from git history 2026-07-16 (samples/treasure.gmk,
samples/maze_4.gmk -- see that commit) specifically to re-run the
importer against them. A fresh import of both now produces zero
"Unmapped GM action" placeholder comments and the expected asset counts
-- this test pins that state so a future importer regression (e.g. a
GM_ACTION_MAP entry accidentally removed) surfaces here instead of
silently reintroducing the exact class of bug that got these samples
dropped in the first place.

This is NOT a claim that either sample is fully correct or ready to
reintroduce -- only that the importer no longer falls through to unmapped
stubs, and every object.sprite / room-instance.object / background_image
reference actually resolves to a real asset, for anything either
project's data touches. Full re-validation (visual playtest, a real
test-game run) is still open, per the plan doc.
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

from importers.gmk_importer import import_gmk_detailed  # noqa: E402


def _all_action_dicts(events: dict):
    """Yield every action dict nested anywhere under an object's `events`
    (then/else branches, repeat/block bodies, sub_actions, ...)."""
    def walk(node):
        if isinstance(node, dict):
            if "action" in node:
                yield node
            for value in node.values():
                yield from walk(value)
        elif isinstance(node, list):
            for item in node:
                yield from walk(item)
    yield from walk(events)


def _import(gmk_name, tmp_path):
    gmk_path = REPO_ROOT / "samples" / gmk_name
    assert gmk_path.exists(), f"{gmk_path} missing (recovered from git history in c6682d9)"
    out_dir = tmp_path / "reimport"
    import_gmk_detailed(str(gmk_path), str(out_dir))
    return out_dir


def _no_unmapped_actions(out_dir):
    unmapped = []
    for obj_file in sorted((out_dir / "objects").glob("*.json")):
        data = json.loads(obj_file.read_text(encoding="utf-8"))
        for action in _all_action_dicts(data.get("events", {})):
            if action.get("action") == "comment" and "Unmapped GM action" in str(
                    action.get("parameters", {}).get("text", "")):
                unmapped.append((obj_file.name, action))
    return unmapped


def _dangling_asset_references(out_dir):
    """Every object.sprite / room-instance.object_name / room
    background_image reference must resolve to a real asset name --
    catches the "silently-renamed sprite/object references on case or
    whitespace conflicts" category TODO.md's GMK hardening notes flag as
    a plausible importer failure mode, distinct from the unmapped-action
    check above (a reference can be present and well-formed but still
    point at nothing)."""
    project = json.loads((out_dir / "project.json").read_text(encoding="utf-8"))
    assets = project["assets"]
    object_names = set(assets.get("objects", {}).keys())
    sprite_names = set(assets.get("sprites", {}).keys())
    background_names = set(assets.get("backgrounds", {}).keys())

    dangling = []
    for obj_name, obj_data in assets.get("objects", {}).items():
        sprite = obj_data.get("sprite")
        if sprite and sprite != "<self>" and sprite not in sprite_names:
            dangling.append(("object.sprite", obj_name, sprite))

    for room_name, room_data in assets.get("rooms", {}).items():
        external = room_data.get("_external_file")
        full_room = json.loads((out_dir / external).read_text(encoding="utf-8")) \
            if external else room_data
        for inst in full_room.get("instances", []):
            obj_ref = inst.get("object_name") or inst.get("object")
            if obj_ref and obj_ref not in object_names:
                dangling.append(("room.instance.object", room_name, obj_ref))
        bg = full_room.get("background_image")
        if bg and bg not in background_names:
            dangling.append(("room.background_image", room_name, bg))
        for layer in full_room.get("backgrounds", []):
            layer_bg = layer.get("background_image")
            if layer_bg and layer_bg not in background_names:
                dangling.append(("room.backgrounds[].background_image", room_name, layer_bg))
    return dangling


class TestTreasureImport:
    def test_imports_without_raising(self, tmp_path):
        _import("treasure.gmk", tmp_path)

    def test_no_unmapped_action_stubs(self, tmp_path):
        out_dir = _import("treasure.gmk", tmp_path)
        assert _no_unmapped_actions(out_dir) == []

    def test_expected_asset_counts(self, tmp_path):
        out_dir = _import("treasure.gmk", tmp_path)
        project = json.loads((out_dir / "project.json").read_text(encoding="utf-8"))
        assets = project["assets"]
        assert len(assets["objects"]) == 7
        assert len(assets["rooms"]) == 4
        assert len(assets["sprites"]) == 10
        assert len(assets["sounds"]) == 6
        assert len(assets["scripts"]) == 1

    def test_monster_script_calls_survive_as_execute_script(self, tmp_path):
        """treasure is the one sample using project-level scripts
        (adapt_direction) -- confirm the importer still emits
        execute_script rather than inlining or dropping the call."""
        out_dir = _import("treasure.gmk", tmp_path)
        data = json.loads((out_dir / "objects" / "monster.json").read_text(encoding="utf-8"))
        script_calls = [a for a in _all_action_dicts(data.get("events", {}))
                         if a.get("action") == "execute_script"]
        assert script_calls
        assert all(a["parameters"].get("script") == "adapt_direction" for a in script_calls)

    def test_no_dangling_asset_references(self, tmp_path):
        out_dir = _import("treasure.gmk", tmp_path)
        assert _dangling_asset_references(out_dir) == []


class TestMaze4Import:
    def test_imports_without_raising(self, tmp_path):
        _import("maze_4.gmk", tmp_path)

    def test_no_unmapped_action_stubs(self, tmp_path):
        out_dir = _import("maze_4.gmk", tmp_path)
        assert _no_unmapped_actions(out_dir) == []

    def test_expected_asset_counts(self, tmp_path):
        out_dir = _import("maze_4.gmk", tmp_path)
        project = json.loads((out_dir / "project.json").read_text(encoding="utf-8"))
        assets = project["assets"]
        assert len(assets["objects"]) == 24
        assert len(assets["rooms"]) == 21
        assert len(assets["sprites"]) == 24
        assert len(assets["sounds"]) == 10

    def test_no_dangling_asset_references(self, tmp_path):
        out_dir = _import("maze_4.gmk", tmp_path)
        assert _dangling_asset_references(out_dir) == []


# ---------------------------------------------------------------------------
# Full re-validation (plan doc: "Remaining full re-validation of
# treasure/maze_4" — the gate before re-adding either to the bundled set).
# Two layers the earlier checks can't see:
#  - room-content fidelity: an instance could be silently dropped or placed at
#    the wrong coordinates, or a tile layer lost, without tripping the
#    unmapped-action or dangling-reference checks; and
#  - the imported project must actually RUN through the real GameRunner.
# ---------------------------------------------------------------------------

def _room_json(out_dir, project, name):
    room = project["assets"]["rooms"][name]
    ext = room.get("_external_file")
    if ext:
        return json.loads((out_dir / ext).read_text(encoding="utf-8"))
    return room


@pytest.mark.parametrize("gmk_name", ["treasure.gmk", "maze_4.gmk"])
def test_room_content_fidelity_vs_raw_parse(gmk_name, tmp_path):
    """Per-room instance/tile counts and the multiset of instance positions in
    the import must match the raw .gmk parse exactly; every instance must sit
    within (or hang slightly off) its room bounds."""
    from importers.gmk_parser import GmkParser
    out = _import(gmk_name, tmp_path)
    project = json.loads((out / "project.json").read_text(encoding="utf-8"))
    parsed = GmkParser().parse(str(REPO_ROOT / "samples" / gmk_name))
    # GM files keep placeholder slots for deleted resources -> None entries
    src_rooms = {r.name: r for r in parsed.rooms if r is not None}
    assert src_rooms, "raw parse produced no rooms"
    for rname, src in src_rooms.items():
        assert rname in project["assets"]["rooms"], f"room {rname} missing from import"
        imp = _room_json(out, project, rname)
        insts = imp.get("instances", [])
        assert len(insts) == len(src.instances), f"{rname}: instance count"
        assert len(imp.get("tiles", [])) == len(src.tiles), f"{rname}: tile count"
        assert (sorted((i.get("x"), i.get("y")) for i in insts)
                == sorted((i.x, i.y) for i in src.instances)), \
            f"{rname}: instance positions differ from the .gmk"
        w, h = imp.get("width", 0), imp.get("height", 0)
        oob = [i for i in insts
               if not (-64 <= i.get("x", 0) <= w + 64 and -64 <= i.get("y", 0) <= h + 64)]
        assert not oob, f"{rname}: instances far outside {w}x{h}: {oob[:3]}"


@pytest.mark.parametrize("gmk_name", ["treasure.gmk", "maze_4.gmk"])
def test_fresh_import_smoke_runs_headlessly(gmk_name, tmp_path):
    """The freshly imported project actually runs: 120 frames through the real
    GameRunner (SDL dummy) with injected input and no loop crash — the
    test_game-equivalent gate from the hardening plan. random is seeded (both
    games use it: monster movement / adapt_direction), and cleanup() is
    no-opped so pygame stays initialized for the rest of the suite."""
    import random
    import pygame
    from runtime.game_runner import GameRunner

    random.seed(20260716)
    out = _import(gmk_name, tmp_path)
    runner = GameRunner(str(out / "project.json"))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None
    runner.cleanup = lambda: None          # keep pygame alive for later tests

    state = {"frames": 0, "cap": False}

    class _FakeClock:
        def tick(self, fps=0):
            f = state["frames"] = state["frames"] + 1
            if f == 3:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
            if f == 40:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT))
            if f % 20 == 0:
                for k in (pygame.K_UP, pygame.K_SPACE):
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k))
                    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=k))
            if f >= 120:
                state["cap"] = True
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        result = runner.run()
    finally:
        pygame.time.Clock = real_clock

    assert result is not False, "game loop crashed"
    assert state["cap"], (
        f"game exited after only {state['frames']} frames — unexpected auto-end")
    assert runner.current_room is not None
    assert len(runner.current_room.instances) > 0


@pytest.mark.parametrize("gmk_name", ["treasure.gmk", "maze_4.gmk"])
def test_no_sprite_decodes_fully_transparent(gmk_name, tmp_path):
    """The pre-v800 sprite reader honored GM's per-sprite Transparent flag only
    nominally — it read the flag into a discarded local and hardcoded the BMP
    key-color pass ON for every sprite. A non-transparent sprite whose
    bottom-left pixel color appears in its artwork lost those pixels: maze_4's
    sprite_hole (a solid black hole, transparency OFF in GM) decoded to a 100%
    transparent PNG and rendered invisible in-game (playtest finding #9).
    No imported sprite may decode to zero opaque pixels."""
    from PIL import Image
    out = _import(gmk_name, tmp_path)
    blank = []
    for png in sorted((out / "sprites").glob("*.png")):
        img = Image.open(png).convert("RGBA")
        if not any(px[3] > 0 for px in img.getdata()):
            blank.append(png.stem)
    assert blank == []


def test_transparent_flag_still_keys_when_set(tmp_path):
    """Sprites WITH transparency enabled still get the key-color pass:
    maze_4's sprite_person keeps a transparent background (mixed alpha)."""
    from PIL import Image
    out = _import("maze_4.gmk", tmp_path)
    img = Image.open(out / "sprites" / "sprite_person.png").convert("RGBA")
    alphas = {px[3] > 0 for px in img.getdata()}
    assert alphas == {True, False}   # some opaque art, some keyed background


def test_hole_destroy_order_is_faithful_and_both_die(tmp_path):
    """Playtest query: the hole's collision destroys SELF then OTHER — that IS
    the .gmk's own action order (applies_to -1 then -2, raw-verified), and the
    runtime destroys BOTH in that order (the event continues after a self
    destroy and 'other' resolves from the executor context). Faithful import,
    working behavior — pinned so neither layer regresses."""
    import json
    out = _import("maze_4.gmk", tmp_path)
    hole = json.loads((out / "objects" / "hole.json").read_text(encoding="utf-8"))
    actions = hole["events"]["collision_with_block"]["actions"]
    kills = [a["parameters"].get("target", "self")
             for a in actions if a["action"] == "destroy_instance"]
    assert kills == ["self", "other"]
