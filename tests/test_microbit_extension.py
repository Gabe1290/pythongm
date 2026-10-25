"""The micro:bit simulator extension (docs/MICROBIT_EXTENSION_PLAN.md).

Stage S1: the extension is discovered, and building a room attaches a
simulator to ``microbit*`` instances (or ones flagged ``is_microbit``)
through the instance-created hook -- with nothing micro:bit-specific in
core.
"""
import ast
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
EXT_DIR = REPO_ROOT / "extensions" / "microbit"


# ---------------------------------------------------------------------------
# S1 — skeleton + instance binding
# ---------------------------------------------------------------------------

def test_extension_is_discovered_and_enabled():
    from events.plugin_loader import list_available_extensions
    found = {e["folder"]: e for e in list_available_extensions()}
    assert "microbit" in found
    assert found["microbit"]["enabled"] is True
    assert found["microbit"]["name"] == "micro:bit"


def test_extension_loads_and_registers_its_instance_created_hook():
    from events.plugin_loader import load_all_plugins
    from runtime.extension_hooks import get_instance_created_hooks
    load_all_plugins()
    modules = {h.__module__ for h in get_instance_created_hooks()}
    assert "pygm_extension_microbit" in modules


def _build_room(instances):
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRoom
    load_all_plugins()
    return GameRoom("r", {"width": 200, "height": 200, "instances": instances},
                    action_executor=None)


def _simulator_of(instance):
    # Read the state the way the extension stores it, rather than importing
    # extensions.microbit.state: the loader imports the extension under a
    # synthetic package name, so that would be a second copy of the module.
    entry = instance.extension_state.get("microbit")
    return entry.get("simulator") if entry else None


def test_room_build_attaches_a_simulator_by_name_or_flag():
    room = _build_room([
        {"object": "microbit_1", "x": 40, "y": 50},
        {"object": "MicroBit_Left", "x": 0, "y": 0},
        {"object": "obj_wall", "x": 10, "y": 10},
        {"object": "obj_flagged", "x": 1, "y": 2, "is_microbit": True},
        {"object": "obj_my_microbit", "x": 3, "y": 4},
    ])
    named, mixed_case, wall, flagged, suffix_only = room.instances
    assert _simulator_of(named) is not None
    assert _simulator_of(mixed_case) is not None
    assert _simulator_of(flagged) is not None
    assert _simulator_of(wall) is None
    # The name must START with "microbit"; containing it isn't enough.
    assert _simulator_of(suffix_only) is None


def test_each_board_gets_its_own_simulator_with_a_dark_display():
    room = _build_room([
        {"object": "microbit_a", "x": 0, "y": 0},
        {"object": "microbit_b", "x": 0, "y": 0},
    ])
    sim_a, sim_b = (_simulator_of(i) for i in room.instances)
    assert sim_a is not sim_b
    assert sim_a.display == [[0] * 5 for _ in range(5)]
    sim_a.display[2][2] = 9
    assert sim_b.display[2][2] == 0


def test_binding_leaves_the_instance_drawn_normally():
    # No overlay exists yet (S5), so the engine must keep drawing the sprite.
    room = _build_room([{"object": "microbit_1", "x": 0, "y": 0}])
    assert room.instances[0].custom_rendered is False


def test_thymio_and_microbit_bindings_do_not_cross():
    room = _build_room([
        {"object": "thymio_bot", "x": 0, "y": 0},
        {"object": "microbit_1", "x": 0, "y": 0},
    ])
    bot, board = room.instances
    assert "microbit" not in bot.extension_state
    assert "thymio" not in board.extension_state


def test_simulator_is_pure_no_pygame_or_qt():
    tree = ast.parse((EXT_DIR / "simulator.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not imported & {"pygame", "PySide6"}


def test_core_carries_no_microbit_code():
    for fname in ("runtime/room.py", "runtime/instance.py",
                  "runtime/game_runner.py", "runtime/extension_hooks.py",
                  "events/plugin_loader.py"):
        src = (REPO_ROOT / fname).read_text(encoding="utf-8")
        assert "microbit" not in src.lower(), fname
