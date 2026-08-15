"""HTML5 export structural + parity coverage for particles + timelines
(Tier 5.3, docs/DEFERRED_GAPS_2026_PLAN.md / Section A of
docs/REMAINING_WORK_2026-08-15.md).

No JS engine/Playwright in this environment (same standing limitation as
every other HTML5 test in this repo) -- source-level structural assertions
for the 14 new `case` branches, plus a numeric parity test that
reimplements the deterministic half of the JS particle-aging formula
(movement/size, fixed direction+speed so there's no RNG to reconcile) in
Python and drives it step-for-step against the real desktop
GameInstance.update_particle_system, matching Block World's own established
two-tier HTML5 approach.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def _case_body(action):
    m = re.search(rf"case '{action}':(.*?)\n(?=\s*case '|\s*default:)", ENGINE, re.S)
    assert m, action
    return m.group(1)


def test_all_fourteen_actions_present():
    for action in (
        "create_particle_system", "destroy_particle_system", "clear_particles",
        "create_particle_type", "create_emitter", "destroy_emitter",
        "burst_particles", "stream_particles",
        "set_timeline", "set_timeline_position", "set_timeline_speed",
        "start_timeline", "pause_timeline", "stop_timeline",
    ):
        assert re.search(rf"case '{action}':", ENGINE), action


def test_spawn_particles_helper_exists_and_is_shared():
    assert "function spawnParticles(system, emitter, ptype, number)" in ENGINE
    burst = _case_body("burst_particles")
    stream_body = re.search(r"3d\. Particles.*?\n(.*?)\n\s*//\s*4\.", ENGINE, re.S)
    assert "spawnParticles(this._particleSystem" in burst
    # The streaming spawn call lives in updateParticleSystem, not a case body.
    m = re.search(r"updateParticleSystem\(\) \{(.*?)\n    \}", ENGINE, re.S)
    assert m and "spawnParticles(ps, emitter, ptype, emitter.streamCount)" in m.group(1)


def test_burst_particles_requires_type_and_emitter():
    body = _case_body("burst_particles")
    assert "this._particleSystem.particleTypes[particleType]" in body
    assert "this._lastEmitterId" in body


def test_stream_particles_arms_the_emitter_not_last_id():
    body = _case_body("stream_particles")
    assert "emitter.streamType = particleType" in body
    assert "emitter.streamCount = number" in body


def test_timeline_position_relative_and_clamped():
    body = _case_body("set_timeline_position")
    assert "relative" in body
    assert "if (this.timelinePosition < 0)" in body


def test_stop_timeline_resets_position_and_running():
    body = _case_body("stop_timeline")
    assert "this.timelineRunning = false" in body
    assert "this.timelinePosition = 0" in body


def test_update_and_render_methods_exist_on_gameobject():
    for name in ("updateParticleSystem", "updateTimeline", "renderParticles"):
        assert f"{name}(" in ENGINE, name


def test_ondraw_renders_particles_before_visibility_check():
    m = re.search(r"onDraw\(ctx\) \{(.*?)\n    \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    render_idx = body.index("this.renderParticles(ctx)")
    sprite_idx = body.index("this.render(ctx)")
    assert render_idx < sprite_idx  # particles called first, ahead of the visibility gate


def test_step_loop_updates_particles_and_timeline_every_frame():
    m = re.search(r"3d\. Particles.*?\n(.*?)\n\s*// 4\. Step events", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "inst.updateParticleSystem()" in body
    assert "inst.updateTimeline()" in body


# ---------------------------------------------------------------------------
# Numeric parity: deterministic particle aging (fixed speed/direction, no
# RNG spread) reimplemented from the JS formula, driven against the real
# desktop GameInstance.update_particle_system.
# ---------------------------------------------------------------------------

def _js_age_particle(p):
    p['life'] -= 1
    if p['life'] <= 0:
        return None
    import math
    angle_rad = p['direction'] * math.pi / 180
    p['x'] += math.cos(angle_rad) * p['speed']
    p['y'] -= math.sin(angle_rad) * p['speed']
    p['size'] = max(0.0, p['size'] + p['sizeIncrease'])
    return p


def test_js_aging_formula_matches_desktop_over_several_steps():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    from runtime.game_runner import GameInstance
    from runtime.action_executor import ActionExecutor

    class _Runner:
        sprites = {}
        project_data = {"assets": {"objects": {}}}
        global_variables = {}

    ex = ActionExecutor(_Runner())
    inst = GameInstance("obj_test", 0, 0, {}, ex)
    inst.object_data = {"events": {}}
    ex.execute_create_particle_system_action(inst, {})
    ex.execute_create_particle_type_action(inst, {
        "size_min": 2.0, "size_max": 2.0, "size_increase": -0.1,
        "speed_min": 3, "speed_max": 3, "direction_min": 37, "direction_max": 37,
        "life_min": 10, "life_max": 10,
    })
    ex.execute_create_emitter_action(inst, {"x": 5, "y": 5, "width": 0, "height": 0})
    ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 1})

    p_desktop = inst._particle_system["particles"][0]
    p_js = dict(x=5.0, y=5.0, size=2.0, sizeIncrease=-0.1, speed=3, direction=37, life=10)

    for _ in range(9):
        inst.update_particle_system()
        result = _js_age_particle(p_js)
        assert result is not None
        assert abs(p_desktop["x"] - p_js["x"]) < 1e-9
        assert abs(p_desktop["y"] - p_js["y"]) < 1e-9
        assert abs(p_desktop["size"] - p_js["size"]) < 1e-9

    inst.update_particle_system()
    assert inst._particle_system["particles"] == []  # culled at life 0, matching JS
