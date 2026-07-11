"""Export feature-parity matrix: bundled samples x export targets.

Static audits review code that exists; they cannot see integrations that
don't (the July 2026 lesson: Kivy had no draw-queue/mouse, HTML5 had no
execute_code/mouse, maze_1 couldn't move in HTML5 — none of it flagged
by the 111-finding audit). This test is the systematic complement: it
cross-references every ACTION and EVENT actually used by the bundled
samples against what each export target implements.

Contract:
- The IDE runtime must cover everything the samples use (hard failure).
- HTML5 / Kivy gaps must exactly match the curated KNOWN_*_GAPS
  registries below. A NEW gap (new sample, new feature use, or a
  regression in an exporter) fails the test with the missing names; a
  STALE entry (you implemented something — thank you) also fails so the
  registry stays honest. Deliberate deferrals belong in the registry
  AND in TODO.md's export section.

Implemented-feature sets are extracted from the exporter sources at test
time (dispatch-case string literals), so newly added support is picked
up automatically.
"""
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from utils.project_file_merge import merge_object_file  # noqa: E402

SAMPLES = ["maze_1", "maze_2", "maze_3",
           "plateforme_1", "plateforme_2", "plateforme_3",
           "plateforme_4", "plateforme_5", "match3_1"]

KEYBOARD_FAMILY = ("keyboard", "keyboard_press", "keyboard_release")

# Pseudo-actions consumed by block/structure handling, not dispatch cases.
STRUCTURAL_ACTIONS = {"else_block", "else_action", "start_block", "end_block", "comment"}


# ---------------------------------------------------------------------------
# Feature extraction: what each sample actually uses
# ---------------------------------------------------------------------------

def _load_project(sample: str) -> dict:
    root = REPO_ROOT / "samples" / sample
    data = json.loads((root / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        side = root / "objects" / f"{name}.json"
        if side.exists() and isinstance(obj, dict):
            merge_object_file(obj, json.loads(side.read_text(encoding="utf-8")))
    return data


def _walk_actions(actions, out: set):
    for a in actions or []:
        if not isinstance(a, dict):
            continue
        name = a.get("action") or a.get("action_type") or ""
        if name:
            out.add(name)
        p = a.get("parameters") or {}
        for key in ("then_actions", "else_actions", "actions"):
            _walk_actions(p.get(key), out)
        _walk_actions(a.get("sub_actions"), out)


def sample_features(sample: str):
    """Return (actions_used, events_used). Events are normalized:
    collision_with_<obj> -> 'collision_with_*', alarm_<n> -> 'alarm_*'."""
    data = _load_project(sample)
    actions, events = set(), set()
    for obj in data["assets"]["objects"].values():
        if not isinstance(obj, dict):
            continue
        for ev_key, ev in (obj.get("events") or {}).items():
            if not isinstance(ev, dict):
                continue
            if ev_key in KEYBOARD_FAMILY:
                for sub in ev.values():
                    if isinstance(sub, dict):
                        events.add(ev_key)
                        _walk_actions(sub.get("actions"), actions)
                continue
            if ev_key.startswith("collision_with_"):
                events.add("collision_with_*")
            elif re.fullmatch(r"alarm_\d+", ev_key):
                events.add("alarm_*")
            else:
                events.add(ev_key)
            _walk_actions(ev.get("actions"), actions)
            for sub in ev.values():  # nested sub-maps (legacy dict forms)
                if isinstance(sub, dict) and "actions" in sub:
                    _walk_actions(sub.get("actions"), actions)
    return actions, events


# ---------------------------------------------------------------------------
# Implemented features per export target
# ---------------------------------------------------------------------------

def runtime_actions() -> set:
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from runtime.action_executor import ActionExecutor
    executor = ActionExecutor()
    names = set(executor.action_handlers.keys())
    names |= set(getattr(executor, "ACTION_ALIASES", {}).keys())
    return names


def html5_actions() -> set:
    src = (REPO_ROOT / "export/HTML5/templates/engine.js").read_text(encoding="utf-8")
    found = set(re.findall(r"case '([a-z_0-9]+)':", src))
    # draw-event actions are dispatched in GameObject.onDraw by comparison,
    # not switch cases
    found |= set(re.findall(r"action\.action === '([a-z_0-9]+)'", src))
    return found


def kivy_actions() -> set:
    src = (REPO_ROOT / "export/Kivy/code_generator.py").read_text(encoding="utf-8")
    found = set(re.findall(r"action_type == '([a-z_0-9]+)'", src))
    for group in re.findall(r"action_type in \(([^)]+)\)", src):
        found |= set(re.findall(r"'([a-z_0-9]+)'", group))
    return found


# Events the HTML5 engine dispatches (see GameRoom.step / Game.setupMouse /
# GameObject.on* in export/HTML5/templates/engine.js). 'draw' is dispatched
# for execute_code actions; draw-action gaps show up in the ACTION matrix.
HTML5_EVENTS = {
    "create", "step", "begin_step", "end_step", "draw", "destroy",
    "game_start", "no_more_lives", "outside_room", "animation_end",
    "keyboard", "keyboard_press", "keyboard_release",
    "collision_with_*", "alarm_*",
    "mouse_left_press", "mouse_left_button", "mouse_left_down",
    "mouse_left_release",
}


def kivy_supports_event(ev: str) -> bool:
    # collision_with_* / keyboard families are handled by dedicated
    # generator paths (see _generate_event_methods; pinned by
    # tests/test_kivy_collision_export.py and test_kivy_keyboard_export.py).
    if ev in ("collision_with_*",) or ev in KEYBOARD_FAMILY:
        return True
    from export.Kivy.kivy_exporter import KivyExporter
    exporter = KivyExporter({}, REPO_ROOT, REPO_ROOT)
    probe = "alarm_0" if ev == "alarm_*" else ev
    return bool(exporter._get_event_method_name({"event_type": probe}))


# ---------------------------------------------------------------------------
# Known-gap registries (curated; keep in sync with TODO.md's export section)
# ---------------------------------------------------------------------------

# Snapshot 2026-07-10 (the state the exporters shipped in for years,
# quantified for the first time). maze_1 and match3_1 are deliberately
# absent: they are the verified classroom demonstrators and must stay
# fully covered (see test_classroom_pair_is_gap_free). Shrink these by
# implementing features; never grow them silently.
# 2026-07-11 (fifth pass): the HTML5 matrix is CLOSED — every action and
# every event used by every bundled sample is implemented. Sprite-strip
# animation (frame slicing, image_index/image_speed, animation_end on
# wrap, frame-sized collision boxes) was the last subsystem;
# browser-verified end-to-end (maze_3's spawned explosion plays its 16
# frames and destroys itself via its authored animation_end). Keep these
# registries empty: a NEW entry means an exporter regressed or a new
# sample outgrew the engine — fix the engine, don't register.
KNOWN_HTML5_ACTION_GAPS = {}

KNOWN_HTML5_EVENT_GAPS = {}

KNOWN_KIVY_ACTION_GAPS = {
    "maze_2": ["draw_score"],
    "maze_3": ["destroy_at_position", "draw_lives", "draw_score", "draw_text",
               "set_direction_speed", "set_draw_color", "set_draw_font"],
    "plateforme_4": ["create_moving_instance", "create_random_instance",
                     "draw_score", "jump_to_random", "test_score"],
    "plateforme_5": ["create_moving_instance", "create_random_instance",
                     "draw_lives", "draw_score", "draw_sprite",
                     "jump_to_random", "set_draw_color", "test_score"],
}

KNOWN_KIVY_EVENT_GAPS = {
    "maze_3": ["animation_end", "no_more_lives"],
    "plateforme_3": ["animation_end", "no_more_lives"],
    "plateforme_4": ["animation_end", "no_more_lives"],
    "plateforme_5": ["no_more_lives"],
}


def _gap_matrix(implemented_fn, feature_index):
    implemented = implemented_fn()
    gaps = {}
    for sample in SAMPLES:
        used = sample_features(sample)[feature_index]
        missing = sorted(used - implemented - STRUCTURAL_ACTIONS)
        if missing:
            gaps[sample] = missing
    return gaps


def _assert_matches_registry(computed: dict, registry: dict, target: str, kind: str):
    computed = {k: sorted(v) for k, v in computed.items()}
    registry = {k: sorted(v) for k, v in registry.items()}
    if computed == registry:
        return
    lines = [f"{target} {kind} gap matrix drifted from the registry."]
    for sample in sorted(set(computed) | set(registry)):
        new = sorted(set(computed.get(sample, [])) - set(registry.get(sample, [])))
        fixed = sorted(set(registry.get(sample, [])) - set(computed.get(sample, [])))
        if new:
            lines.append(f"  NEW gap  {sample}: {new} — implement in the "
                         f"{target} exporter or register here + TODO.md")
        if fixed:
            lines.append(f"  STALE    {sample}: {fixed} — now implemented; "
                         f"remove from the registry")
    pytest.fail("\n".join(lines))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_runtime_covers_every_sample_action():
    """The IDE runtime must implement every action a bundled sample uses."""
    gaps = _gap_matrix(runtime_actions, 0)
    assert gaps == {}, f"runtime is missing sample actions: {gaps}"


def test_html5_action_gaps_match_registry():
    _assert_matches_registry(
        _gap_matrix(html5_actions, 0), KNOWN_HTML5_ACTION_GAPS, "HTML5", "action")


def test_html5_event_gaps_match_registry():
    computed = {}
    for sample in SAMPLES:
        missing = sorted(sample_features(sample)[1] - HTML5_EVENTS)
        if missing:
            computed[sample] = missing
    _assert_matches_registry(computed, KNOWN_HTML5_EVENT_GAPS, "HTML5", "event")


def test_kivy_action_gaps_match_registry():
    _assert_matches_registry(
        _gap_matrix(kivy_actions, 0), KNOWN_KIVY_ACTION_GAPS, "Kivy", "action")


def test_kivy_event_gaps_match_registry():
    computed = {}
    for sample in SAMPLES:
        missing = sorted(ev for ev in sample_features(sample)[1]
                         if not kivy_supports_event(ev))
        if missing:
            computed[sample] = missing
    _assert_matches_registry(computed, KNOWN_KIVY_EVENT_GAPS, "Kivy", "event")


def test_classroom_pair_is_gap_free():
    """maze_1 (keyboard game) and match3_1 (touch game) are the verified
    classroom demonstrators: they must stay FULLY exportable — no one may
    'register' a gap for them instead of fixing it."""
    for sample in ("maze_1", "match3_1"):
        for fn in (html5_actions, kivy_actions, runtime_actions):
            used = sample_features(sample)[0]
            missing = used - fn() - STRUCTURAL_ACTIONS
            assert not missing, f"{sample} vs {fn.__name__}: {sorted(missing)}"
        assert not (sample_features(sample)[1] - HTML5_EVENTS)
        assert all(kivy_supports_event(ev) for ev in sample_features(sample)[1])
