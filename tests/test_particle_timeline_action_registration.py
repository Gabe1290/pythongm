"""Particle + timeline actions registered as structured actions (Tier 5.2,
docs/DEFERRED_GAPS_2026_PLAN.md). Before this they had real runtime
handlers (execute_create_particle_system_action etc., made functionally
real by Tier 5.1) but no events/action_types.py entry, so they logged
"Unknown action type: X" and were uneditable in the events panel -- the
exact class of gap the 2026-06-05 "safe bucket" sweep fixed for other
actions, explicitly deferring this bucket at the time.

Registering set_timeline with a plain string param (not a resource
picker) is deliberate: this engine has no separate Timeline resource --
see the params test below and Tier 5.1's own finding in the plan doc.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from events.action_types import get_action_type, get_actions_by_category  # noqa: E402


PARTICLE_ACTIONS = [
    "create_particle_system", "destroy_particle_system", "clear_particles",
    "create_particle_type", "create_emitter", "destroy_emitter",
    "burst_particles", "stream_particles",
]

TIMELINE_ACTIONS = [
    "set_timeline", "set_timeline_position", "set_timeline_speed",
    "start_timeline", "pause_timeline", "stop_timeline",
]


@pytest.mark.parametrize("name", PARTICLE_ACTIONS)
def test_particle_action_registered_in_particles_category(name):
    at = get_action_type(name)
    assert at is not None, name
    assert at.category == "Particles"


@pytest.mark.parametrize("name", TIMELINE_ACTIONS)
def test_timeline_action_registered_in_timing_category(name):
    at = get_action_type(name)
    assert at is not None, name
    assert at.category == "Timing"


def test_particles_category_appears_in_actions_by_category():
    cats = get_actions_by_category()
    assert "Particles" in cats
    names = {a.name for a in cats["Particles"]}
    assert names == set(PARTICLE_ACTIONS)


def test_create_particle_type_full_param_set_matches_runtime_reads():
    """The registered params must be the ones execute_create_particle_type_action
    actually reads via parameters.get(...), so authored values round-trip."""
    at = get_action_type("create_particle_type")
    names = {p.name for p in at.parameters}
    for field in ("sprite", "size_min", "size_max", "size_increase", "color",
                  "alpha", "speed_min", "speed_max", "direction_min",
                  "direction_max", "life_min", "life_max"):
        assert field in names, field


def test_create_particle_type_sprite_is_optional_sprite_selector():
    at = get_action_type("create_particle_type")
    sprite = next(p for p in at.parameters if p.name == "sprite")
    assert sprite.param_type == "sprite"
    assert sprite.required is False  # blank = plain colored circle, not a sprite


def test_create_emitter_shape_choices_match_runtime_validation():
    """execute_create_emitter_action falls back to 'rectangle' for anything
    outside this exact set."""
    at = get_action_type("create_emitter")
    shape = next(p for p in at.parameters if p.name == "shape")
    assert shape.choices == ["rectangle", "ellipse", "diamond", "line"]


def test_set_timeline_position_relative_flag():
    at = get_action_type("set_timeline_position")
    names = {p.name for p in at.parameters}
    assert names == {"position", "relative"}
    relative = next(p for p in at.parameters if p.name == "relative")
    assert relative.param_type == "boolean"


def test_set_timeline_is_a_plain_string_not_a_resource_picker():
    """No Timeline resource exists in this engine (Tier 5.1 finding) --
    the param must stay a free-text string, not param_type='room'/'object'
    style asset selector."""
    at = get_action_type("set_timeline")
    timeline = next(p for p in at.parameters if p.name == "timeline")
    assert timeline.param_type == "string"


def test_start_pause_stop_timeline_have_no_parameters():
    for name in ("start_timeline", "pause_timeline", "stop_timeline"):
        at = get_action_type(name)
        assert at.parameters == [], name


def test_matches_runtime_handlers():
    """Every registered action must be backed by a real runtime handler."""
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    for name in PARTICLE_ACTIONS + TIMELINE_ACTIONS:
        handler_name = f"execute_{name}_action"
        assert callable(getattr(ex, handler_name, None)), handler_name
