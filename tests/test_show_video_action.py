"""Regression for docs/DEFERRED_GAPS_2026_PLAN.md Tier 2.4.

show_video (execute_show_video_action, runtime/action_executor.py) already
worked -- OS default-player shell-out -- but had no ActionType entry, so it
was invisible in the UI. Registered it, and folded the never-reachable
splash_show_video/splash_show_webpage placeholder actions into it and
open_webpage respectively via ActionExecutor.ACTION_ALIASES, since both
were 100% dead code (no ActionType ever existed for either name).
splash_show_text/splash_show_image are untouched here -- Tier 2.5's own
real implementations, not a fold into an existing action.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from events.action_types import get_action_type, ACTION_TYPES


def test_show_video_is_registered():
    action = get_action_type("show_video")
    assert action is not None
    assert action.name == "show_video"
    param_names = {p.name for p in action.parameters}
    assert param_names == {"filename", "fullscreen"}
    desc = action.description.lower()
    assert "system" in desc or "default video player" in desc


def test_show_video_description_is_honest_about_not_being_in_engine():
    action = get_action_type("show_video")
    desc = action.description.lower()
    assert "separate window" in desc or "not rendered inside the game" in desc


def test_splash_show_video_aliases_to_show_video():
    assert get_action_type("splash_show_video") is get_action_type("show_video")


def test_splash_show_webpage_aliases_to_open_webpage():
    assert get_action_type("splash_show_webpage") is get_action_type("open_webpage")


def test_splash_show_text_and_image_are_not_aliased():
    """These stay their own thing (Tier 2.5), not folded into show_video."""
    from runtime.action_executor import ActionExecutor
    assert "splash_show_text" not in ActionExecutor.ACTION_ALIASES
    assert "splash_show_image" not in ActionExecutor.ACTION_ALIASES


def test_dead_placeholder_handlers_are_gone():
    src = (REPO_ROOT / "runtime" / "action_handlers" / "extra_handlers.py").read_text(encoding="utf-8")
    assert "def handle_splash_show_video" not in src
    assert "def handle_splash_show_webpage" not in src
    assert '"splash_show_video":' not in src
    assert '"splash_show_webpage":' not in src


def test_dispatch_routes_splash_show_video_to_the_real_show_video_handler(monkeypatch):
    """End-to-end: an action list authored with the legacy name still runs
    the real handler, not a silent no-op -- verifies alias resolution
    actually reaches execute_show_video_action, not just get_action_type."""
    from runtime.action_executor import ActionExecutor

    class _Instance:
        pass

    calls = []
    executor = ActionExecutor()
    original = executor.execute_show_video_action

    def spy(instance, parameters):
        calls.append(parameters)
        return original(instance, parameters)

    executor.action_handlers["show_video"] = spy
    executor.execute_action(_Instance(), {
        "action": "splash_show_video",
        "parameters": {"filename": "clip.mp4"},
    })
    assert calls == [{"filename": "clip.mp4"}]


def test_open_webpage_still_registered_directly():
    """Sanity: open_webpage itself is untouched by this fold."""
    assert "open_webpage" in ACTION_TYPES
