"""No action is offered twice in the Blockly toolbox (2026-11-19).

An action with no ``actionToBlockType`` entry in blockly_workspace.html gets a
generated ``custom_<action>`` block from registerCustomBlocks -- that is the
block a saved project reloads as. If the preset toolbox ALSO lists a
hand-written block of the same name, students see two look-alike blocks. This
happened to Set variable (the hand-written one has no Relative field, so
Pong's "+1 to the score" couldn't be built with it), Set speed, Set direction
and Exit event. Source-level so it runs without a browser; the real-page check
that every preset's toolbox has no duplicates was done when this was fixed.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

PAGE = Path(__file__).parent.parent / "editors" / "object_editor" / "blockly" / "blockly_workspace.html"


def _source():
    return PAGE.read_text(encoding="utf-8")


def _toolbox_block_types(src):
    start = src.index("var categories = {")
    end = src.index("pushToGroup('Math'", start)
    return set(re.findall(r"<block type=\"([a-z_0-9]+)\"", src[start:end]))


def _mapped_actions(src):
    start = src.index("var actionToBlockType = {")
    end = src.index("\n        };", start)
    return set(re.findall(r"'([a-z_0-9]+)'\s*:", src[start:end]))


def test_no_hand_written_toolbox_block_duplicates_a_generated_one():
    from events.plugin_loader import load_all_plugins
    from events.action_types import ACTION_TYPES
    load_all_plugins()
    src = _source()
    dups = sorted(t for t in _toolbox_block_types(src)
                  if t in ACTION_TYPES and t not in _mapped_actions(src))
    assert not dups, (
        "these hand-written toolbox blocks duplicate the generated custom_* block "
        f"the page uses for the same action: {dups}")


def test_the_four_known_duplicates_are_gone():
    types = _toolbox_block_types(_source())
    for t in ("set_variable", "set_speed", "set_direction", "exit_event"):
        assert t not in types, t


def test_the_parser_sees_the_toolbox():
    """Guard the guard: the regexes really find the lists they read."""
    src = _source()
    assert {"if_condition", "test_variable", "move_direction"} <= _toolbox_block_types(src)
    assert {"stop_movement", "set_score"} <= _mapped_actions(src)
