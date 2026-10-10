"""Boolean action parameters read as GameMaker means them (Blockly audit B17,
docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md).

The GMK import stores checkboxes as the TEXT "0"/"1". Plain truthiness read
"0" as true, so treasure's change_instance "perform events: no" ran the
events anyway on desktop and HTML5; Kivy pasted the raw value into code
("0" happened to work, "false" did not compile). One rule now everywhere:
False, 0, "0", "false", "no", "" are false; a missing value is the default.
"""
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("value,expected", [
    (None, True), (True, True), (False, False), (1, True), (0, False),
    ("1", True), ("0", False), ("true", True), ("false", False), ("False", False),
    ("no", False), ("yes", True), ("", False), (" 0 ", False),
])
def test_param_is_true(value, expected):
    from runtime.gm_math import param_is_true
    assert param_is_true(value, True) is expected


def _perform_events_passed(perform_events):
    """The perform_events value the desktop handler decides on (recorded at
    _change_single_instance, the one place that acts on it)."""
    from unittest.mock import patch
    from runtime.action_executor import ActionExecutor
    runner = SimpleNamespace(score=0, lives=3, health=100, global_variables={},
                             current_room=None,
                             project_data={"assets": {"objects": {"monster": {"events": {}}}}})
    ex = ActionExecutor(game_runner=runner)
    seen = []
    params = {"object": "monster"}
    if perform_events is not None:
        params["perform_events"] = perform_events
    inst = SimpleNamespace(x=0, y=0, object_name="scared")
    with patch.object(type(ex), "_change_single_instance",
                      lambda self, target, name, data, pe: seen.append(pe)):
        ex.execute_action(inst, {"action": "change_instance", "parameters": params})
    assert len(seen) == 1, "handler did not reach _change_single_instance"
    return seen[0]


@pytest.mark.parametrize("value,expected", [("0", False), ("false", False),
                                            ("1", True), (None, True), (False, False)])
def test_desktop_change_instance_decides_perform_events_by_the_shared_rule(value, expected):
    assert _perform_events_passed(value) is expected


@pytest.mark.parametrize("kivy_value,literal", [("0", "False"), ("false", "False"),
                                                ("1", "True"), (None, "True"), (True, "True")])
def test_kivy_emits_a_literal_boolean(kivy_value, literal):
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=0)
    params = {"object": "monster"}
    if kivy_value is not None:
        params["perform_events"] = kivy_value
    g.process_action({"action": "change_instance", "parameters": params}, "step")
    code = g.get_code()
    compile(code, "<gen>", "exec")
    assert f"perform_events={literal}" in code


def test_html5_change_instance_reads_perform_events_with_the_shared_rule():
    js = (REPO / "export/HTML5/templates/engine.js").read_text(encoding="utf-8")
    assert "const performEvents = gmParamIsTrue(params.perform_events, true);" in js
    helper = js[js.index("function gmParamIsTrue(value, dflt) {"):]
    helper = helper[:helper.index("\n}\n")]
    assert "['0', 'false', 'no', '']" in helper

