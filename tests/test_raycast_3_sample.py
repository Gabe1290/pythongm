"""raycast_3 sample — Unit 5 baseline (maze geometry + objects).

raycast_3 is the third Doom-style raycast sample. Its headline feature is the
in-view HUD (RAYCAST_HUD_PLAN Sessions A-B), which lands as gameplay in Unit 6;
this file pins the geometry and that the sample runs at all.

Unlike raycast_2 — whose maze came from a throwaway script that was never
committed, so its rooms can't be regenerated — raycast_3's rooms are produced by
tools/gen_raycast_3_maze.py. These tests assert the shipped rooms still match
what the generator produces, so the level design stays reviewable.

Runs through the REAL GameRunner.run() loop: the raycast render path needs
set_sprites_for_instances to have run in run()'s startup (2026-07-17 lesson).
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "tools"))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

SAMPLE = REPO_ROOT / "samples" / "raycast_3"
PROJECT = str(SAMPLE / "project.json")


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
            for ev in key_script.get(f, []):
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


# --- Generator / geometry --------------------------------------------------

def test_shipped_room_matches_the_generator():
    """The committed room0.json is exactly what the generator produces, so the
    maze can be regenerated and tweaked rather than being opaque data."""
    import gen_raycast_3_maze as gen
    seed, cam, counts, goal = gen.ROOMS["room0"]
    built = gen.build_room("room0", seed, cam, counts, goal)
    shipped = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    assert built["instances"] == shipped["instances"], \
        "room0.json has drifted from tools/gen_raycast_3_maze.py"
    assert built["width"] == shipped["width"] == 480
    assert built["height"] == shipped["height"] == 480


def test_maze_is_solvable_and_the_spawn_faces_an_opening():
    """Both properties the seed was CHOSEN for. The player starts at cell (0,0)
    facing angle 0 (east); a seed whose start cell is walled to the east spawns
    you nose-to-wall, which reads as a broken game."""
    import gen_raycast_3_maze as gen
    seed = gen.ROOMS["room0"][0]
    h, v = gen.carve(seed)
    gen.check_start(h, v)          # raises if walled-east or not fully connected


def test_walls_use_the_thin_edge_model():
    """Same geometry as raycast_1/raycast_2: 8px partitions centred on cell
    boundaries, not 32px blocks filling a cell."""
    room = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    hs = [i for i in room["instances"] if i["object_name"] == "obj_wall_h"]
    vs = [i for i in room["instances"] if i["object_name"] == "obj_wall_v"]
    assert hs and vs
    for i in hs:
        assert i["x"] % 32 == 0 and (i["y"] + 4) % 32 == 0, i
    for i in vs:
        assert (i["x"] + 4) % 32 == 0 and i["y"] % 32 == 0, i


def test_room_contents():
    room = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    kinds = {}
    for i in room["instances"]:
        kinds[i["object_name"]] = kinds.get(i["object_name"], 0) + 1
    assert kinds["obj_person"] == 1
    assert kinds["obj_cam0"] == 1
    assert kinds["obj_goal"] == 1
    assert kinds["obj_gem"] == 8
    assert kinds["obj_monster"] == 3


# --- Behaviour through the real loop ---------------------------------------

def test_sample_runs_with_the_textured_first_person_camera():
    runner = _runner()
    result, frames = _run(runner, {}, 40)
    assert result is not False, "game loop reported a fatal crash"
    assert frames == 40
    assert runner.current_room.name == "room0"
    cfg = raycast_state(runner.current_room)["camera"]
    assert cfg["enabled"] is True
    assert cfg["wall_texture"] == "spr_wall_texture"
    assert cfg["sky_texture"] == "spr_sky"
    assert cfg["floor_texture"] == "spr_floor"


def test_player_can_walk_forward_from_the_spawn():
    """Guards the seed choice behaviourally, not just in the generator: holding
    Up from spawn must actually travel, rather than stalling against a wall."""
    runner = _runner()
    script = {3: [(pygame.KEYDOWN, pygame.K_UP)],
              50: [(pygame.KEYUP, pygame.K_UP)]}
    _run(runner, script, 60)
    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    assert player.x > 8 + 32, \
        f"player barely moved from spawn (x={player.x}) — start cell walled in?"


def test_player_is_blocked_by_walls():
    runner = _runner()
    script = {3: [(pygame.KEYDOWN, pygame.K_UP)]}
    _run(runner, script, 150)
    room = runner.current_room
    player = next(i for i in room.instances if i.object_name == "obj_person")
    assert 0 <= player.x <= room.width, f"player left the room: x={player.x}"
    assert 0 <= player.y <= room.height, f"player left the room: y={player.y}"


# --- Unit 6: health loop + in-view HUD -------------------------------------
# raycast_3's reason to exist: health as a resource you can SEE while playing.
# The engine side landed in RAYCAST_HUD_PLAN Sessions A-B (HUD compositing) and
# Unit 5b (health conditionals + no_more_health on the export targets).

def _pin_and_run(touch_frames, max_frames, extra=None):
    """Run the sample, teleporting the player onto a monster on the given
    frames and back home the frame after.

    Touch-and-retreat, not a continuous overlap: the runtime fires a collision
    event only when a pair STARTS overlapping (GameRoom keeps
    instance._active_collisions), so pinning the player on a monster can only
    ever deal one hit no matter how long it lasts.
    """
    from runtime.game_runner import GameInstance
    real_dq = GameInstance._process_draw_queue
    GameInstance._process_draw_queue = lambda self, screen: setattr(self, "_draw_queue", [])
    runner = _runner()
    state = {"f": 0, "home": None}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            room = runner.current_room
            if room:
                p = next(i for i in room.instances if i.object_name == "obj_person")
                ms = [i for i in room.instances if i.object_name == "obj_monster"]
                if state["home"] is None:
                    state["home"] = (p.x, p.y)
                if ms and f in touch_frames:
                    p.x, p.y = ms[0].x, ms[0].y
                elif f - 1 in touch_frames:
                    p.x, p.y = state["home"]
                if extra:
                    extra(f, runner, room, state)
            if f >= max_frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
        GameInstance._process_draw_queue = real_dq
    return runner


def test_starting_stats_come_from_game_start():
    """score/lives/health must init in game_start, NOT create — create re-runs
    on restart_room, so a create-time set_lives would refund lives on death
    (the raycast_2 landmine)."""
    obj = json.loads((SAMPLE / "objects" / "obj_person.json").read_text(encoding="utf-8"))
    gs = [a["action"] for a in obj["events"]["game_start"]["actions"]]
    assert {"set_score", "set_lives", "set_health"} <= set(gs)
    create = [a["action"] for a in obj["events"]["create"]["actions"]]
    assert "set_lives" not in create and "set_health" not in create


def test_monster_costs_health_not_a_life():
    """The core difference from raycast_2, where a touch cost a life outright."""
    runner = _pin_and_run({5}, 20)
    assert runner.health == 75.0, f"expected one 25-point hit, got {runner.health}"
    assert runner.lives == 3, "a single touch must not cost a life"


def test_invulnerability_window_blocks_a_second_hit_that_arrives_too_soon():
    """Per-touch damage plus a 45-step alarm (the model settled in the plan).
    Without it, a monster patrolling through the player would drain the whole
    bar in a handful of touches."""
    runner = _pin_and_run({5, 30}, 45)      # re-touch inside the window
    assert runner.health == 75.0, \
        f"invulnerability did not block the second hit (health={runner.health})"


def test_the_window_expires_so_damage_can_land_again():
    """The other half: a permanent invulnerability would be just as broken."""
    runner = _pin_and_run({5, 70}, 85)      # re-touch after the alarm cleared
    assert runner.health == 50.0, \
        f"second hit did not land after the window expired (health={runner.health})"


def test_emptying_the_bar_costs_exactly_one_life_and_refills_health():
    """no_more_health -> -1 life, health back to 100, room restarts. Exactly
    one life: the event fires only on the downward 0-crossing."""
    runner = _pin_and_run({5, 60, 115, 170}, 200)
    assert runner.lives == 2, f"expected exactly one life lost, got {runner.lives}"
    assert runner.health == 100, f"health not refilled after death: {runner.health}"


def test_medkit_heals_and_is_consumed():
    def touch_medkit(f, runner, room, state):
        if f == 100:
            ks = [i for i in room.instances if i.object_name == "obj_medkit"]
            if ks:
                p = next(i for i in room.instances if i.object_name == "obj_person")
                p.x, p.y = ks[0].x, ks[0].y

    runner = _pin_and_run({5, 60}, 120, extra=touch_medkit)
    assert runner.health == 90.0, f"medkit did not heal 40 (health={runner.health})"
    left = [i for i in runner.current_room.instances
            if i.object_name == "obj_medkit"]
    assert len(left) == 2, "medkit was not consumed"


def test_health_never_exceeds_full():
    """A medkit picked up at full health must not push the bar past 100 —
    draw_health_bar would render past its own right edge."""
    def touch_medkit(f, runner, room, state):
        if f == 30:
            ks = [i for i in room.instances if i.object_name == "obj_medkit"]
            if ks:
                p = next(i for i in room.instances if i.object_name == "obj_person")
                p.x, p.y = ks[0].x, ks[0].y

    runner = _pin_and_run(set(), 50, extra=touch_medkit)
    assert runner.health == 100, f"health exceeded full: {runner.health}"


# --- The HUD itself --------------------------------------------------------

def test_hud_controller_is_visible():
    """Load-bearing, not stylistic: GameMaker does not run an invisible
    instance's draw event (enforced on all three targets since 380abd2), which
    is why the HUD can't live on the invisible camera controller."""
    hud = json.loads((SAMPLE / "objects" / "obj_hud.json").read_text(encoding="utf-8"))
    assert hud["visible"] is True
    cam = json.loads((SAMPLE / "objects" / "obj_cam0.json").read_text(encoding="utf-8"))
    assert cam["visible"] is False, \
        "if the camera became visible this test no longer explains anything"


def test_hud_uses_opposite_corners():
    """Layout rule from the plan: score and health in OPPOSITE corners, so a
    wide health bar can't collide with a growing score string."""
    hud = json.loads((SAMPLE / "objects" / "obj_hud.json").read_text(encoding="utf-8"))
    by = {a["action"]: a["parameters"] for a in hud["events"]["draw"]["actions"]}
    assert int(by["draw_score"]["y"]) < 100, "score should be at the top"
    assert int(by["draw_health_bar"]["y1"]) > 380, "health bar should be at the bottom"
    # Window is 640x480; the bar must fit inside it.
    assert int(by["draw_health_bar"]["x2"]) <= 640
    assert int(by["draw_health_bar"]["y2"]) <= 480


def test_hud_renders_over_the_raycast_view():
    """End-to-end: the whole point of the sample. Captures the draw queue while
    the first-person camera is on."""
    from runtime.game_runner import GameInstance
    seen = []
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        for cmd in self._draw_queue:
            seen.append((self.object_name, cmd.get("type")))
        self._draw_queue = []

    GameInstance._process_draw_queue = spy
    try:
        runner = _runner()
        _run(runner, {}, 6)
    finally:
        GameInstance._process_draw_queue = real

    assert raycast_state(runner.current_room)["camera"]["enabled"] is True
    kinds = {k for name, k in seen if name == "obj_hud"}
    assert {"text", "lives", "health_bar"} <= kinds, \
        f"HUD did not fully render under raycast; saw {sorted(kinds)}"


# --- Unit 7: second room, per-room theme, gated exit -----------------------

def _clear_gems_then_touch_goal(runner, room):
    """Remove every gem, then put the player on the goal."""
    for g in [i for i in room.instances if i.object_name == "obj_gem"]:
        if g in room.instances:
            room.instances.remove(g)
    p = next(i for i in room.instances if i.object_name == "obj_person")
    goal = next(i for i in room.instances
                if i.object_name in ("obj_goal", "obj_goal_final"))
    p.x, p.y = goal.x, goal.y


def _play(steps, max_frames):
    """steps: {frame -> callable(runner, room)}."""
    from runtime.game_runner import GameInstance
    real_dq = GameInstance._process_draw_queue
    GameInstance._process_draw_queue = lambda self, screen: setattr(self, "_draw_queue", [])
    runner = _runner()
    msgs = []
    runner.show_message_dialog = lambda *a, **k: msgs.append(a[0] if a else "")
    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            room = runner.current_room
            if room and f in steps:
                steps[f](runner, room)
            if f >= max_frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
        GameInstance._process_draw_queue = real_dq
    return runner, msgs


def test_both_rooms_are_registered_and_ordered():
    proj = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    assert list(proj["assets"]["rooms"]) == ["room0", "room1"]
    order = proj.get("room_order") or proj["settings"].get("room_order")
    assert order == ["room0", "room1"]
    assert proj["settings"]["starting_room"] == "room0"


def test_room1_matches_the_generator_and_is_the_harder_half():
    import gen_raycast_3_maze as gen
    seed, cam, counts, goal = gen.ROOMS["room1"]
    built = gen.build_room("room1", seed, cam, counts, goal)
    shipped = json.loads((SAMPLE / "rooms" / "room1.json").read_text(encoding="utf-8"))
    assert built["instances"] == shipped["instances"]
    # More monsters and fewer medkits than room0, so the health bar matters.
    r0 = gen.ROOMS["room0"][2]
    assert counts["obj_monster"] > r0["obj_monster"]
    assert counts["obj_medkit"] < r0["obj_medkit"]


def test_each_room_carries_its_own_camera_controller():
    """Per-room theming: the camera object differs, and each names obj_person
    explicitly as the camera (the raycast_2 architecture)."""
    for room_name, cam_name in (("room0", "obj_cam0"), ("room1", "obj_cam1")):
        room = json.loads((SAMPLE / "rooms" / f"{room_name}.json").read_text(encoding="utf-8"))
        cams = [i for i in room["instances"]
                if i["object_name"].startswith("obj_cam")]
        assert [c["object_name"] for c in cams] == [cam_name], room_name
        cam = json.loads((SAMPLE / "objects" / f"{cam_name}.json").read_text(encoding="utf-8"))
        params = cam["events"]["create"]["actions"][0]["parameters"]
        assert params["camera_object"] == "obj_person", cam_name


def test_room1_uses_the_ice_theme():
    cam = json.loads((SAMPLE / "objects" / "obj_cam1.json").read_text(encoding="utf-8"))
    params = cam["events"]["create"]["actions"][0]["parameters"]
    assert params["wall_texture"] == "spr_wall_ice"
    assert params["sky_texture"] == "spr_sky_ice"
    assert params["floor_texture"] == "spr_floor_ice"


def test_the_exit_is_gated_until_every_gem_is_collected():
    runner, msgs = _play({
        5: lambda r, room: _touch_goal_only(r, room),
    }, 20)
    assert runner.current_room.name == "room0", "goal opened while gems remained"
    assert any("gem" in m.lower() for m in msgs), \
        f"no 'collect the gems' prompt was shown; msgs={msgs}"


def _touch_goal_only(runner, room):
    p = next(i for i in room.instances if i.object_name == "obj_person")
    goal = next(i for i in room.instances
                if i.object_name in ("obj_goal", "obj_goal_final"))
    p.x, p.y = goal.x, goal.y


def test_collecting_every_gem_opens_the_exit_into_the_ice_room():
    runner, _ = _play({5: _clear_gems_then_touch_goal}, 25)
    assert runner.current_room.name == "room1"
    cfg = raycast_state(runner.current_room)["camera"]
    assert cfg["enabled"] is True, "camera did not re-arm in the new room"
    assert cfg["wall_texture"] == "spr_wall_ice", \
        "room1 rendered with room0's theme — per-room camera controller broken"


def test_the_hud_still_renders_in_room1():
    """The camera re-arms per room entry; so must the HUD. A room change builds
    a FRESH room with raycast_camera=None, so this is the case most likely to
    regress — and it can only be caught by watching draws that happen AFTER the
    transition, not by checking the room name."""
    from runtime.game_runner import GameInstance
    seen = []                       # (room_name, object_name, cmd type)
    box = {"runner": None}
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        runner = box["runner"]
        room = runner.current_room if runner else None
        if room is not None:
            for cmd in self._draw_queue:
                seen.append((room.name, self.object_name, cmd.get("type")))
        self._draw_queue = []

    GameInstance._process_draw_queue = spy
    try:
        runner = _runner()
        box["runner"] = runner       # set BEFORE run(), so the spy can see it
        msgs = []
        runner.show_message_dialog = lambda *a, **k: msgs.append(a[0] if a else "")
        state = {"f": 0}

        class _Clock:
            def tick(self, fps=0):
                f = state["f"] = state["f"] + 1
                if f == 5 and runner.current_room:
                    _clear_gems_then_touch_goal(runner, runner.current_room)
                if f >= 30:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _Clock
        try:
            runner.run()
        finally:
            pygame.time.Clock = real_clock
    finally:
        GameInstance._process_draw_queue = real

    assert runner.current_room.name == "room1", "never reached room1"
    in_room1 = {kind for room, obj, kind in seen
                if room == "room1" and obj == "obj_hud"}
    assert {"text", "lives", "health_bar"} <= in_room1, \
        f"HUD did not fully render in room1; saw {sorted(in_room1)}"


def test_room1_goal_is_the_final_one():
    room = json.loads((SAMPLE / "rooms" / "room1.json").read_text(encoding="utf-8"))
    names = {i["object_name"] for i in room["instances"]}
    assert "obj_goal_final" in names and "obj_goal" not in names
    goal = json.loads((SAMPLE / "objects" / "obj_goal_final.json").read_text(encoding="utf-8"))
    acts = [a["action"] for a in goal["events"]["collision_with_obj_person"]["actions"]]
    assert "restart_game" in acts, "the final goal must end the game, not advance"
    assert "test_instance_count" in acts, "the final goal must be gem-gated too"
