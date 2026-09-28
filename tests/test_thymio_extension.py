"""Thymio is becoming an EXTENSION (docs/THYMIO_EXTENSION_PLAN.md).

These pin each move: what now lives in extensions/thymio, that core no
longer carries a copy, and that the extension is discovered and wired
through the loader. Behavioural Thymio coverage stays in the test_thymio_*
files -- this file is only about WHERE the code lives.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# A1 — action schemas
# ---------------------------------------------------------------------------

def test_action_schemas_live_in_the_extension():
    from extensions.thymio.actions import THYMIO_ACTIONS, THYMIO_TAB
    from actions.core import ActionDefinition
    assert len(THYMIO_ACTIONS) == 28
    assert all(isinstance(a, ActionDefinition) for a in THYMIO_ACTIONS.values())
    assert all(a.tab == "thymio" for a in THYMIO_ACTIONS.values())
    assert THYMIO_TAB["thymio"]["name"] == "Thymio"


def test_core_no_longer_carries_the_schemas():
    assert not (REPO_ROOT / "actions" / "thymio_actions.py").exists()
    import actions
    assert not hasattr(actions, "THYMIO_ACTIONS")
    src = (REPO_ROOT / "actions" / "core.py").read_text(encoding="utf-8")
    assert '"thymio":' not in src, "the Thymio tab is the extension's now"


def test_manifest_declares_every_action():
    from extensions.thymio.actions import THYMIO_ACTIONS
    manifest = json.loads((REPO_ROOT / "extensions" / "thymio" / "extension.json")
                          .read_text(encoding="utf-8"))
    assert set(manifest["provides_actions"]) == set(THYMIO_ACTIONS)
    assert manifest["enabled"] is True


# ---------------------------------------------------------------------------
# A2 — runtime handlers
# ---------------------------------------------------------------------------

def test_handlers_live_in_the_extension_as_a_plugin_executor():
    from extensions.thymio.actions import THYMIO_ACTIONS
    from extensions.thymio.handlers import PluginExecutor, register_thymio_actions
    ex = PluginExecutor()
    for name in THYMIO_ACTIONS:
        assert callable(getattr(ex, f"execute_{name}_action", None)), name
    captured = {}

    class _Sink:
        def register_custom_action(self, n, h):
            captured[n] = h

    register_thymio_actions(_Sink())
    assert set(captured) == set(THYMIO_ACTIONS)


def test_core_no_longer_carries_the_handlers():
    assert not (REPO_ROOT / "runtime" / "thymio_action_handlers.py").exists()
    src = (REPO_ROOT / "runtime" / "game_runner.py").read_text(encoding="utf-8")
    assert "register_thymio_actions" not in src
    assert "thymio_action_handlers" not in src


def test_game_executor_gets_the_handlers_through_the_loader():
    """GameRunner no longer registers Thymio handlers itself; load_all_plugins
    (which it calls) does, via the extension's PluginExecutor."""
    from runtime.action_executor import ActionExecutor
    from events.plugin_loader import load_all_plugins
    ex = ActionExecutor(game_runner=None)
    assert "thymio_set_motor_speed" not in ex.action_handlers
    load_all_plugins(ex)
    assert "thymio_set_motor_speed" in ex.action_handlers
    assert "thymio_if_variable" in ex.action_handlers

    class _Inst:
        thymio_simulator = None

    assert ex.action_handlers["thymio_if_proximity"](_Inst(), {}) is False


# ---------------------------------------------------------------------------
# A3 — event types
# ---------------------------------------------------------------------------

def test_events_live_in_the_extension_and_use_the_real_event_type():
    from extensions.thymio import PLUGIN_EVENTS, PLUGIN_EVENT_BLOCKLY_MAP
    from extensions.thymio.events import THYMIO_EVENT_TYPES, is_thymio_event
    from events.event_types import EventType
    assert PLUGIN_EVENTS is THYMIO_EVENT_TYPES and len(THYMIO_EVENT_TYPES) == 14
    assert all(type(e) is EventType for e in THYMIO_EVENT_TYPES.values())
    assert PLUGIN_EVENT_BLOCKLY_MAP == {n: n for n in THYMIO_EVENT_TYPES}
    assert is_thymio_event("thymio_button_forward") and not is_thymio_event("create")


def test_core_no_longer_carries_the_events():
    assert not (REPO_ROOT / "events" / "thymio_events.py").exists()
    src = (REPO_ROOT / "events" / "event_types.py").read_text(encoding="utf-8")
    assert "THYMIO_EVENT_TYPES" not in src and "thymio_events" not in src


def test_events_register_through_the_loader_with_blockly_gating():
    from events.plugin_loader import load_all_plugins
    from events.event_types import (
        EVENT_TYPES, EVENT_TO_BLOCKLY_MAP, get_available_events,
    )
    from config.blockly_config import BlocklyConfig
    load_all_plugins()
    assert "thymio_button_forward" in EVENT_TYPES
    assert EVENT_TO_BLOCKLY_MAP["thymio_button_forward"] == "thymio_button_forward"
    # Gated by the Blockly config exactly as before the move.
    names = {e.name for e in get_available_events(BlocklyConfig.get_beginner())}
    assert "thymio_button_forward" not in names
    names = {e.name for e in get_available_events(BlocklyConfig.get_thymio())}
    assert "thymio_button_forward" in names


# ---------------------------------------------------------------------------
# A4 — simulator
# ---------------------------------------------------------------------------

def test_simulator_lives_in_the_extension():
    from extensions.thymio.simulator import ThymioSimulator
    sim = ThymioSimulator(x=10, y=20, angle=0)
    assert (sim.x, sim.y) == (10, 20)
    assert not (REPO_ROOT / "runtime" / "thymio_simulator.py").exists()


def test_extension_is_discovered_and_registers_its_tab():
    from events.plugin_loader import list_available_extensions, load_all_plugins
    found = {e["folder"]: e for e in list_available_extensions()}
    assert "thymio" in found and found["thymio"]["enabled"] is True
    load_all_plugins()
    from actions.core import GM80_ACTION_TABS, get_action_tabs_ordered
    assert GM80_ACTION_TABS["thymio"]["order"] == 100
    assert get_action_tabs_ordered()[-1][0] == "thymio"
