"""The generic core seams extensions plug into (docs/THYMIO_EXTENSION_PLAN.md
Stage 0).

Each Stage-0 unit adds one seam to core and one section here proving it with
a DUMMY registrant — no Thymio code involved — so a seam bug can never be
confused with a bug in the code that later moves onto it.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# 0.1 — Instance.extension_state
# ---------------------------------------------------------------------------

def _instance(name="obj_a"):
    from runtime.instance import GameInstance
    return GameInstance(name, 0, 0, {}, action_executor=None)


def test_instance_has_empty_extension_state_by_default():
    inst = _instance()
    assert inst.extension_state == {}


def test_instance_extension_state_is_per_instance():
    """A shared class-level dict would leak one robot's state into every
    instance; each instance must own its own mapping."""
    a, b = _instance("obj_a"), _instance("obj_b")
    a.extension_state["dummy"] = {"hp": 3}
    assert b.extension_state == {}
    assert a.extension_state is not b.extension_state


def test_instance_extension_state_mirrors_room_pattern():
    """Same shape as GameRoom.extension_state so an extension namespaces the
    two identically (room.extension_state['x'] / inst.extension_state['x'])."""
    from runtime.game_runner import GameRoom
    room = GameRoom("r", {"width": 64, "height": 64}, action_executor=None)
    inst = _instance()
    assert type(inst.extension_state) is type(room.extension_state) is dict
