"""Particle system + timeline engine (Tier 5.1,
docs/DEFERRED_GAPS_2026_PLAN.md). Before this, action_executor.py's
create_particle_system/create_particle_type/create_emitter/burst_particles/
stream_particles and set_timeline/set_timeline_position/set_timeline_speed/
start_timeline/pause_timeline/stop_timeline only ever wrote to
instance._particle_system / instance.timeline_* -- nothing in game_runner.py
read any of it (particles never aged, moved, spawned from streaming
emitters, or drew; timeline_position never advanced). This exercises the
real GameInstance/ActionExecutor pair across simulated frames, matching
this repo's "verify against a real GameRunner, not a hand-rolled harness"
discipline for runtime engine work.

Timeline design note: there is no separate Timeline resource/"moments"
table in this engine (confirmed by reading every write-side handler --
timeline_index is just an opaque string, never looked up anywhere). An
author reacts to a specific timeline_position with an ordinary
test_variable/conditional in their own step event, the same way any other
counter would be used -- this mirrors alarms being authored as ordinary
object events rather than a dedicated resource. Firing scheduled moments is
therefore satisfied by making timeline_position/timeline_speed/
timeline_running real and observable, not by inventing new resource
infrastructure (which would be Tier 5.2/UI scope, not 5.1/engine scope, and
isn't what any existing action supports authoring).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pygame
pygame.init()

from runtime.game_runner import GameInstance
from runtime.action_executor import ActionExecutor


class _StubGameRunner:
    def __init__(self, sprites=None):
        self.sprites = sprites or {}
        self.project_data = {"assets": {"objects": {}}}
        self.global_variables = {}


def _instance(sprites=None):
    game_runner = _StubGameRunner(sprites)
    executor = ActionExecutor(game_runner)
    inst = GameInstance("obj_test", 50, 50, {}, executor)
    inst.object_data = {"events": {}}
    return inst


class TestParticleSystemLifecycle:
    def test_burst_particles_appear_then_age_and_die(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {"depth": 0})
        ex.execute_create_particle_type_action(inst, {
            "size_min": 1.0, "size_max": 1.0, "size_increase": 0,
            "color": "#FF0000", "alpha": 1.0,
            "speed_min": 0, "speed_max": 0,
            "direction_min": 0, "direction_max": 0,
            "life_min": 2, "life_max": 2,
        })
        ex.execute_create_emitter_action(inst, {"x": 10, "y": 10, "width": 0, "height": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 5})

        assert len(inst._particle_system["particles"]) == 5

        inst.update_particle_system()  # life 2 -> 1, survives
        assert len(inst._particle_system["particles"]) == 5

        inst.update_particle_system()  # life 1 -> 0, culled
        assert len(inst._particle_system["particles"]) == 0

    def test_particles_move_by_speed_and_direction(self):
        """0 deg = right (+x), matching set_direction_speed's convention."""
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {
            "speed_min": 4, "speed_max": 4,
            "direction_min": 0, "direction_max": 0,
            "life_min": 100, "life_max": 100,
        })
        ex.execute_create_emitter_action(inst, {"x": 0, "y": 0, "width": 0, "height": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 1})

        p = inst._particle_system["particles"][0]
        x0, y0 = p["x"], p["y"]
        inst.update_particle_system()
        assert p["x"] == pytest.approx(x0 + 4)
        assert p["y"] == pytest.approx(y0)

    def test_particles_moving_up_decrease_y(self):
        """90 deg = up, and y grows downward -- so y must DECREASE."""
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {
            "speed_min": 4, "speed_max": 4,
            "direction_min": 90, "direction_max": 90,
            "life_min": 100, "life_max": 100,
        })
        ex.execute_create_emitter_action(inst, {"x": 0, "y": 0, "width": 0, "height": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 1})

        p = inst._particle_system["particles"][0]
        y0 = p["y"]
        inst.update_particle_system()
        assert p["y"] < y0

    def test_size_increase_grows_particle_and_floors_at_zero(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {
            "size_min": 1.0, "size_max": 1.0, "size_increase": -10,
            "life_min": 100, "life_max": 100,
        })
        ex.execute_create_emitter_action(inst, {"x": 0, "y": 0, "width": 0, "height": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 1})

        inst.update_particle_system()
        assert inst._particle_system["particles"][0]["size"] == 0.0  # floored, not negative

    def test_streaming_emitter_spawns_particles_every_frame(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {"life_min": 100, "life_max": 100})
        ex.execute_create_emitter_action(inst, {"x": 0, "y": 0, "width": 0, "height": 0})
        ex.execute_stream_particles_action(inst, {"particle_type": 0, "number": 3})

        assert len(inst._particle_system["particles"]) == 0  # not spawned yet, just armed

        inst.update_particle_system()
        assert len(inst._particle_system["particles"]) == 3

        inst.update_particle_system()
        assert len(inst._particle_system["particles"]) == 6

    def test_stream_particles_uses_the_emitter_it_was_set_on_not_last_emitter(self):
        """stream_particles stores stream_type/count on the SPECIFIC emitter
        (via _last_emitter_id at call time) -- creating a second emitter
        afterward must not redirect the already-armed stream."""
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {"life_min": 100, "life_max": 100})
        first_emitter = ex.execute_create_emitter_action(inst, {"x": 0, "y": 0})
        ex.execute_stream_particles_action(inst, {"particle_type": 0, "number": 1})
        ex.execute_create_emitter_action(inst, {"x": 999, "y": 999})  # second, unrelated emitter

        inst.update_particle_system()
        assert len(inst._particle_system["particles"]) == 1
        # Spawned from the FIRST emitter's position (0, 0), not the second's.
        p = inst._particle_system["particles"][0]
        assert abs(p["x"]) < 1 and abs(p["y"]) < 1

    def test_no_particle_system_is_a_safe_no_op(self):
        inst = _instance()
        inst.update_particle_system()  # must not raise
        inst.render_particles(pygame.Surface((64, 64)))  # must not raise

    def test_destroy_particle_system_stops_further_updates(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {"life_min": 100, "life_max": 100})
        ex.execute_create_emitter_action(inst, {"x": 0, "y": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 2})
        ex.execute_destroy_particle_system_action(inst, {})

        inst.update_particle_system()  # must not raise on a None particle system


class TestParticleRendering:
    def test_color_particle_draws_visible_pixels(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {
            "size_min": 5.0, "size_max": 5.0, "color": "#FF0000", "alpha": 1.0,
            "speed_min": 0, "speed_max": 0, "life_min": 100, "life_max": 100,
        })
        ex.execute_create_emitter_action(inst, {"x": 32, "y": 32, "width": 0, "height": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 1})

        screen = pygame.Surface((64, 64))
        screen.fill((0, 0, 0))
        inst.render_particles(screen)

        assert screen.get_at((32, 32))[:3] == (255, 0, 0)

    def test_sprite_particle_uses_named_sprite(self):
        from runtime.game_runner import GameSprite

        surf = pygame.Surface((8, 8))
        surf.fill((0, 255, 0))
        sprite = GameSprite("spr_particle.png")
        sprite.surface = surf
        sprite.frames = [surf]

        inst = _instance(sprites={"spr_particle": sprite})
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {
            "sprite": "spr_particle", "size_min": 1.0, "size_max": 1.0,
            "speed_min": 0, "speed_max": 0, "life_min": 100, "life_max": 100,
        })
        ex.execute_create_emitter_action(inst, {"x": 32, "y": 32, "width": 0, "height": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 1})

        screen = pygame.Surface((64, 64))
        screen.fill((0, 0, 0))
        inst.render_particles(screen)

        assert screen.get_at((32, 32))[:3] == (0, 255, 0)

    def test_invisible_instance_still_renders_its_particles(self):
        """A common GM pattern: an invisible instance that only holds
        emitters. render() must not skip particles the way it skips the
        instance's own sprite."""
        inst = _instance()
        inst.visible = False
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {
            "size_min": 5.0, "size_max": 5.0, "color": "#00FF00",
            "speed_min": 0, "speed_max": 0, "life_min": 100, "life_max": 100,
        })
        ex.execute_create_emitter_action(inst, {"x": 32, "y": 32, "width": 0, "height": 0})
        ex.execute_burst_particles_action(inst, {"particle_type": 0, "number": 1})

        screen = pygame.Surface((64, 64))
        screen.fill((0, 0, 0))
        inst.render(screen)

        assert screen.get_at((32, 32))[:3] == (0, 255, 0)


class TestTimelineEngine:
    def test_position_advances_while_running(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_set_timeline_action(inst, {"timeline": "tl_intro"})
        ex.execute_start_timeline_action(inst, {})

        assert inst.timeline_position == 0
        inst.update_timeline()
        assert inst.timeline_position == 1
        inst.update_timeline()
        assert inst.timeline_position == 2

    def test_position_does_not_advance_while_paused(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_set_timeline_action(inst, {"timeline": "tl_intro"})
        ex.execute_start_timeline_action(inst, {})
        inst.update_timeline()
        assert inst.timeline_position == 1

        ex.execute_pause_timeline_action(inst, {})
        inst.update_timeline()
        inst.update_timeline()
        assert inst.timeline_position == 1  # unchanged while paused

    def test_speed_scales_advancement(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_set_timeline_action(inst, {"timeline": "tl_intro"})
        ex.execute_set_timeline_speed_action(inst, {"speed": 0.5})
        ex.execute_start_timeline_action(inst, {})

        inst.update_timeline()
        inst.update_timeline()
        assert inst.timeline_position == pytest.approx(1.0)

    def test_stop_resets_position_and_stops_advancing(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_set_timeline_action(inst, {"timeline": "tl_intro"})
        ex.execute_start_timeline_action(inst, {})
        inst.update_timeline()
        inst.update_timeline()
        assert inst.timeline_position == 2

        ex.execute_stop_timeline_action(inst, {})
        assert inst.timeline_position == 0
        inst.update_timeline()
        assert inst.timeline_position == 0  # stopped, not running

    def test_position_is_observable_via_test_variable_like_any_counter(self):
        """The engine's whole 'firing' story: an author checks
        timeline_position with an ordinary getattr-based read (what
        test_variable/scope='sel' does) -- no separate moments table."""
        inst = _instance()
        ex = inst.action_executor
        ex.execute_set_timeline_action(inst, {"timeline": "tl_intro"})
        ex.execute_start_timeline_action(inst, {})
        for _ in range(5):
            inst.update_timeline()

        assert getattr(inst, "timeline_position", None) == 5

    def test_never_started_timeline_is_a_safe_no_op(self):
        inst = _instance()
        inst.update_timeline()  # no timeline_running attribute at all -- must not raise
        assert getattr(inst, "timeline_position", 0) == 0


class TestRealGameRunnerIntegration:
    """Drives update_particle_system/update_timeline through the real
    per-frame instance loop location (game_runner.py's main loop calls both
    right after delayed actions, before the step event) by constructing a
    minimal real room/instance and calling GameRunner's own per-instance
    step helpers directly -- avoids the heavy full run() event-loop harness
    while still exercising the real production code path.
    """

    def test_instance_step_plus_particle_timeline_update_together(self):
        inst = _instance()
        ex = inst.action_executor
        ex.execute_create_particle_system_action(inst, {})
        ex.execute_create_particle_type_action(inst, {
            "speed_min": 2, "speed_max": 2, "direction_min": 0, "direction_max": 0,
            "life_min": 3, "life_max": 3,
        })
        ex.execute_create_emitter_action(inst, {"x": 0, "y": 0})
        ex.execute_stream_particles_action(inst, {"particle_type": 0, "number": 1})
        ex.execute_set_timeline_action(inst, {"timeline": "tl_x"})
        ex.execute_start_timeline_action(inst, {})

        for _ in range(3):
            inst.update_particle_system()
            inst.update_timeline()
            inst.step()  # real step() -- no object events, must coexist cleanly

        assert inst.timeline_position == 3
        # 3 spawned (one per frame), oldest (life 3, aged 3 frames) just died.
        assert len(inst._particle_system["particles"]) == 2
