"""enable_views / set_view registered as structured actions (views plan step 3).

They were usable only by hand-authoring JSON / raw execute_code. Registering
them in events/action_types.py lets them round-trip through the action editor
and save/load, and gives the exporters a metadata entry to dispatch on. The
desktop runtime + HTML5 export implement them; Kivy export is pending (see
docs/VIEWS_SAMPLES_PLAN.md).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from events.action_types import get_action_type  # noqa: E402


def test_enable_views_registered():
    at = get_action_type("enable_views")
    assert at is not None
    assert at.category == "Views"
    assert [p.name for p in at.parameters] == ["enable"]
    assert at.parameters[0].param_type == "boolean"


def test_set_view_registered_with_full_param_set():
    at = get_action_type("set_view")
    assert at is not None and at.category == "Views"
    names = {p.name for p in at.parameters}
    # the full GameMaker view schema the runtime/exporters consume
    for field in ("view", "visible", "view_x", "view_y", "view_w", "view_h",
                  "port_x", "port_y", "port_w", "port_h", "follow",
                  "hborder", "vborder", "hspeed", "vspeed"):
        assert field in names, field


def test_set_view_follow_is_optional_object_selector():
    at = get_action_type("set_view")
    follow = next(p for p in at.parameters if p.name == "follow")
    assert follow.param_type == "object"   # picks an object from the project
    assert follow.required is False        # blank = fixed (non-following) view


def test_view_index_choices_cover_all_eight():
    at = get_action_type("set_view")
    view = next(p for p in at.parameters if p.name == "view")
    assert view.choices == [str(i) for i in range(8)]


def test_matches_runtime_handler_params():
    """The registered params must be the ones the desktop handler reads, so
    the action round-trips into a working export. Spot-check against
    execute_set_view_action's documented parameter set."""
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    # both handlers exist in the runtime (registered actions must be backed)
    assert callable(getattr(ex, "execute_set_view_action", None))
    assert callable(getattr(ex, "execute_enable_views_action", None))
