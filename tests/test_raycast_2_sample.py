"""End-to-end smoke test for the raycast_2 sample (Level 2), Unit 1 baseline.

raycast_2 is a bigger Doom-style maze built on the (complete) raycast 2.5D
engine — a recursive-backtracker maze converted to raycast_1's thin edge-wall
model (obj_wall_h/obj_wall_v), reusing obj_person / obj_goal and the textured
wall/sky/floor. This pins that the sample loads, enables the first-person
camera, turns in response to input, and (crucially — see the raycast_1 lesson
about registered collision handlers gating the movement-block) that the player
is stopped by walls rather than walking out of the room.

Runs through the REAL GameRunner.run() loop: the raycast render path needs
set_sprites_for_instances to have run in run()'s startup, so a hand-built room
would smoke-pass for the wrong reason.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

PROJECT = str(REPO_ROOT / "samples" / "raycast_2" / "project.json")


def _runner():
    from runtime.game_runner import GameRunner
    runner = GameRunner(PROJECT)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None
    return runner


def _run(runner, key_script, max_frames):
    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            f = state["frames"] = state["frames"] + 1
            for at, ev in key_script.get(f, []):
                pygame.event.post(pygame.event.Event(ev[0], key=ev[1]))
            if f >= max_frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        result = runner.run()
    finally:
        pygame.time.Clock = real
    return result, state["frames"]


def test_raycast_2_runs_and_enables_first_person_camera():
    runner = _runner()
    # Hold LEFT (turn) frames 5..35 -> 30 * 3 deg = 90 degrees.
    script = {
        5: [("kd", (pygame.KEYDOWN, pygame.K_LEFT))],
        35: [("ku", (pygame.KEYUP, pygame.K_LEFT))],
    }
    result, frames = _run(runner, script, 60)

    assert result is not False, "game loop reported a fatal crash"
    assert frames == 60
    assert runner.current_room.name == "room0"
    assert runner.current_room.raycast_camera["enabled"] is True
    # Textured raycast config carried over from raycast_1's create event.
    cfg = runner.current_room.raycast_camera
    assert cfg["wall_texture"] == "spr_wall_texture"
    assert cfg["sky_texture"] == "spr_sky"
    assert cfg["floor_texture"] == "spr_floor"

    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    assert player.facing_angle == pytest.approx(90.0, abs=0.01)


def test_raycast_2_player_is_blocked_by_walls():
    runner = _runner()
    # Hold UP (move forward) far longer than the room is wide; the player must
    # stay inside the 480x480 room (registered collision_with_obj_wall_* gates
    # the movement-block — copied from raycast_1's obj_person).
    script = {3: [("kd", (pygame.KEYDOWN, pygame.K_UP))]}
    result, frames = _run(runner, script, 120)

    assert result is not False
    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    assert -8 <= player.x <= 480, f"player x escaped the room: {player.x}"
    assert -8 <= player.y <= 480, f"player y escaped the room: {player.y}"


def test_gems_placed_and_registered():
    """Unit 2: obj_gem billboards are scattered and wired to score + destroy."""
    import json
    root = REPO_ROOT / "samples" / "raycast_2"
    room = json.loads((root / "rooms" / "room0.json").read_text(encoding="utf-8"))
    gems = [i for i in room["instances"] if i.get("object_name") == "obj_gem"]
    assert len(gems) >= 4, "expected several collectible gems"

    obj = json.loads((root / "objects" / "obj_gem.json").read_text(encoding="utf-8"))
    assert obj["solid"] is False and obj["sprite"] == "spr_gem"   # billboard, not a wall
    ev = obj["events"]
    # collision destroys self; the destroy event awards score (maze_2 pattern)
    assert ev["collision_with_obj_person"]["actions"][0]["action"] == "destroy_instance"
    assert ev["destroy"]["actions"][0]["action"] == "set_score"
    assert ev["destroy"]["actions"][0]["parameters"].get("relative") is True

    proj = json.loads((root / "project.json").read_text(encoding="utf-8"))
    assert "obj_gem" in proj["assets"]["objects"]
    assert "spr_gem" in proj["assets"]["sprites"]


def test_gem_collision_awards_score_and_destroys():
    """Colliding with a gem (via the real event dispatch) destroys it and adds
    10 to the score through its destroy event — run through the loop so the
    destroy/cleanup phase actually fires."""
    runner = _runner()
    hit = {"done": False}

    def _fire(runner):
        gems = [i for i in runner.current_room.instances
                if i.object_name == "obj_gem"]
        if gems and not hit["done"]:
            hit["done"] = True
            g = gems[0]
            runner.action_executor.execute_event(
                g, "collision_with_obj_person", g.object_data["events"])

    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            f = state["frames"] = state["frames"] + 1
            if f == 5:
                _fire(runner)                 # collide with a gem
            if f >= 20:                        # let cleanup fire the destroy event
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    n_before = None
    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        # snapshot gem count after startup by hooking the first tick
        runner.run()
    finally:
        pygame.time.Clock = real

    gems_after = [i for i in runner.current_room.instances
                  if i.object_name == "obj_gem" and not getattr(i, "_destroyed", False)]
    assert hit["done"], "never found a gem to collide with"
    assert runner.score == 10, f"score should be 10 after one gem, got {runner.score}"
    assert len(gems_after) == 7, f"one gem should be gone, {len(gems_after)} remain"


def test_score_and_lives_init_in_game_start():
    """score/lives init lives in game_start (fires once), NOT create — create
    re-runs on restart_room, which would reset the score to 0 and lives to 3 on
    every death. game_start survives a room restart; only restart_game resets."""
    import json
    ev = json.loads((REPO_ROOT / "samples" / "raycast_2" / "objects"
                     / "obj_person.json").read_text(encoding="utf-8"))["events"]
    gs = [a["action"] for a in ev["game_start"]["actions"]]
    assert "set_score" in gs and "set_lives" in gs
    create = [a["action"] for a in ev["create"]["actions"]]
    assert "set_score" not in create and "set_lives" not in create

    runner = _runner()
    _run(runner, {}, 5)
    assert runner.show_score_in_caption is True
    assert runner.score == 0 and runner.lives == 3


def test_billboard_sprites_use_top_left_origin():
    """The billboard sprites are 32px with a TOP-LEFT origin (0,0), matching
    obj_person/obj_goal/obj_wall. A centred origin put their billboard centre
    half a sprite off — right on the grid lines where walls sit — so gems and
    monsters were sliced in half by the wall occlusion. Top-left origin also
    keeps all three export targets in agreement (Kivy has no origin concept)."""
    import json
    root = REPO_ROOT / "samples" / "raycast_2" / "sprites"
    for name in ("spr_gem", "spr_monster"):
        s = json.loads((root / f"{name}.json").read_text(encoding="utf-8"))
        assert s["width"] == 32 and s["height"] == 32, name
        assert s["origin_x"] == 0 and s["origin_y"] == 0, name


def test_billboards_are_not_centred_on_wall_lines():
    """Every gem/monster must sit inside a cell, not on a 32px grid line."""
    import json
    room = json.loads((REPO_ROOT / "samples" / "raycast_2" / "rooms"
                       / "room0.json").read_text(encoding="utf-8"))
    for i in room["instances"]:
        if i.get("object_name") in ("obj_gem", "obj_monster"):
            cx, cy = i["x"] + 16, i["y"] + 16      # origin (0,0) -> centre
            assert cx % 32 != 0 and cy % 32 != 0, (i["object_name"], cx, cy)


def test_monster_wired_and_placed():
    """Unit 3: obj_monster is a moving, wall-bouncing billboard enemy."""
    import json
    root = REPO_ROOT / "samples" / "raycast_2"
    room = json.loads((root / "rooms" / "room0.json").read_text(encoding="utf-8"))
    mons = [i for i in room["instances"] if i.get("object_name") == "obj_monster"]
    assert len(mons) >= 1

    obj = json.loads((root / "objects" / "obj_monster.json").read_text(encoding="utf-8"))
    assert obj["solid"] is False and obj["sprite"] == "spr_monster"
    ev = obj["events"]
    assert ev["create"]["actions"][0]["action"] == "start_moving_direction"
    # bounces off both wall orientations
    assert ev["collision_with_obj_wall_h"]["actions"][0]["action"] == "reverse_vertical"
    assert ev["collision_with_obj_wall_v"]["actions"][0]["action"] == "reverse_horizontal"

    proj = json.loads((root / "project.json").read_text(encoding="utf-8"))
    assert "obj_monster" in proj["assets"]["objects"]
    assert "spr_monster" in proj["assets"]["sprites"]


def test_monster_patrols_and_lives_init():
    """The monster moves each frame (patrol), and the player starts with 3
    lives shown in the caption HUD."""
    runner = _runner()
    start = {}

    class _FakeClock:
        def tick(self, fps=0):
            f = start.setdefault("f", 0)
            start["f"] = f + 1
            if start["f"] == 2:
                m = [i for i in runner.current_room.instances
                     if i.object_name == "obj_monster"]
                start["y0"] = m[0].y if m else None
            if start["f"] >= 20:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real

    assert runner.lives == 3
    assert runner.show_lives_in_caption is True
    mon = next(i for i in runner.current_room.instances
               if i.object_name == "obj_monster")
    assert mon.y != start["y0"], "monster should be patrolling (moving)"


def test_monster_collision_costs_a_life():
    """Touching a monster deducts a life (via the real event dispatch)."""
    runner = _runner()
    fired = {"done": False}

    class _FakeClock:
        def tick(self, fps=0):
            fired.setdefault("f", 0)
            fired["f"] += 1
            if fired["f"] == 5 and not fired["done"]:
                fired["done"] = True
                p = next(i for i in runner.current_room.instances
                         if i.object_name == "obj_person")
                fired["before"] = runner.lives
                runner.action_executor.execute_event(
                    p, "collision_with_obj_monster", p.object_data["events"])
            if fired["f"] >= 12:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real

    assert fired["done"]
    assert fired["before"] == 3
    assert runner.lives == 2, f"a monster hit should cost one life, got {runner.lives}"


def _run_capturing_messages(runner, frames):
    msgs = []
    runner.show_message_dialog = lambda m, *a, **k: msgs.append(m)
    _run(runner, {}, frames)
    return msgs


def test_goal_is_gated_on_collecting_all_gems():
    """Unit 4: reaching a goal while gems remain shows the 'collect them all'
    prompt and does NOT let you through. (room0's goal advances, room1's wins —
    the advance/win split is covered by the Unit 5 transition test.)"""
    runner = _runner()
    msgs = _run_capturing_messages(runner, 5)
    goal = next(i for i in runner.current_room.instances
                if i.object_name == "obj_goal")

    # gems still present -> prompt, and the room does not change. The runner is
    # language "en", so the ENGLISH base message is what surfaces (the French
    # etc. live in message_translations — see the IDE-language test below).
    runner.action_executor.execute_event(
        goal, "collision_with_obj_person", goal.object_data["events"])
    assert msgs and "Collect all the gems" in msgs[-1]
    assert runner.current_room.name == "room0"


def test_goal_messages_follow_the_ide_language():
    """Messages carry an ENGLISH base plus message_translations, which is what
    the runtime resolves against the IDE/game language (execute_show_message_action:
    `message` for en, message_translations[lang] otherwise)."""
    import json
    root = REPO_ROOT / "samples" / "raycast_2" / "objects"
    langs = {"fr", "de", "es", "it", "ru", "sl", "uk"}
    seen_win = False
    for name in ("obj_goal", "obj_goal_final"):
        acts = json.loads((root / f"{name}.json").read_text(encoding="utf-8")
                          )["events"]["collision_with_obj_person"]["actions"]
        assert any(a["action"] == "test_instance_count"
                   and a["parameters"]["object"] == "obj_gem" for a in acts)
        for a in acts:
            if a["action"] != "show_message":
                continue
            p = a["parameters"]
            # base must be English (the runtime's en fallback), not French
            assert p["message"].isascii(), f"{name}: base message must be English"
            tr = p.get("message_translations", {})
            assert langs <= set(tr), f"{name}: missing {langs - set(tr)}"
            # French must carry proper accents (project rule)
            if "Bravo" in tr["fr"]:
                assert "terminé" in tr["fr"]     # é, not a stripped 'termine'
                seen_win = True
    assert seen_win, "the win message should exist on obj_goal_final"


def test_two_rooms_with_per_room_camera_themes():
    """Unit 5: two rooms, each with its own camera controller enabling the
    raycast view (naming obj_person as the camera) with a distinct texture set."""
    import json
    root = REPO_ROOT / "samples" / "raycast_2"
    proj = json.loads((root / "project.json").read_text(encoding="utf-8"))
    assert proj["room_order"] == ["room0", "room1"]

    # enable_raycast_view moved off obj_person onto the per-room controllers
    person = json.loads((root / "objects" / "obj_person.json").read_text(encoding="utf-8"))
    assert not any(a["action"] == "enable_raycast_view"
                   for a in person["events"]["create"]["actions"])

    def cam_cfg(name):
        obj = json.loads((root / "objects" / f"{name}.json").read_text(encoding="utf-8"))
        a = obj["events"]["create"]["actions"][0]
        assert a["action"] == "enable_raycast_view"
        assert a["parameters"]["camera_object"] == "obj_person"
        return a["parameters"]
    warm, ice = cam_cfg("obj_cam0"), cam_cfg("obj_cam1")
    assert warm["wall_texture"] == "spr_wall_texture"
    assert ice["wall_texture"] == "spr_wall_ice"       # distinct theme
    assert warm["sky_texture"] != ice["sky_texture"]
    for s in ("spr_wall_ice", "spr_sky_ice", "spr_floor_ice"):
        assert s in proj["assets"]["sprites"]


def test_room0_goal_advances_and_room1_goal_wins():
    """room0's goal advances to room1 (both gem-gated); room1's obj_goal_final
    is the win. Drive the real loop through the transition."""
    runner = _runner()
    _run(runner, {}, 4)
    assert runner.current_room.name == "room0"
    cfg0 = runner.current_room.raycast_camera
    assert cfg0["wall_texture"] == "spr_wall_texture"
    assert runner.current_room._find_first_instance(cfg0["camera_object"]).object_name == "obj_person"

    # clear gems, hit room0 goal -> next_room
    room = runner.current_room
    for g in [i for i in room.instances if i.object_name == "obj_gem"]:
        g._destroyed = True
    room.instances = [i for i in room.instances if not getattr(i, "_destroyed", False)]
    goal = next(i for i in room.instances if i.object_name == "obj_goal")
    runner.action_executor.execute_event(goal, "collision_with_obj_person",
                                         goal.object_data["events"])
    runner.running = True
    _run(runner, {}, 4)
    assert runner.current_room.name == "room1"
    assert runner.current_room.raycast_camera["wall_texture"] == "spr_wall_ice"

    # room1 has obj_goal_final (win), not obj_goal
    names = {i.object_name for i in runner.current_room.instances}
    assert "obj_goal_final" in names


def test_raycast_2_room0_is_a_thin_wall_maze():
    """The generated room uses raycast_1's thin edge-wall objects, not
    full-cell blocks — a sanity check on the geometry conversion."""
    import json
    room = json.loads((REPO_ROOT / "samples" / "raycast_2" / "rooms"
                       / "room0.json").read_text(encoding="utf-8"))
    names = [i.get("object_name") for i in room["instances"]]
    assert names.count("obj_wall_h") > 40
    assert names.count("obj_wall_v") > 40
    assert names.count("obj_person") == 1
    assert names.count("obj_goal") == 1
    assert room["width"] == 480 and room["height"] == 480
