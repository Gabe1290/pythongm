"""Regression tests for the Aseba exporter file-format fixes (audit M32, M33).

M32: exported .aesl must be an aesl-source XML document (so Aseba Studio's
     File -> Open can parse it), not bare source text.
M33: generated `onevent` handlers must NOT be terminated with a stray `end`
     (which is a syntax error in AESL — `end` only closes if/when/while/for).

Pure-logic tests: the exporter has no Qt dependency, so no QApplication needed.
"""

import xml.etree.ElementTree as ET

from export.Aseba.aseba_exporter import AsebaExporter


def _make_exporter():
    exp = AsebaExporter()
    exp.variables = set()
    exp.timer_periods = {}
    exp.current_object = "thymio_player"
    exp.indent_level = 0
    return exp


# --------------------------------------------------------------------------
# M33 — no stray 'end' after onevent handlers
# --------------------------------------------------------------------------

def test_event_handler_has_no_trailing_end():
    exp = _make_exporter()
    actions = [
        {"action": "thymio_move_forward", "parameters": {"speed": "200"}},
    ]
    block = exp._generate_event_handler("onevent button.forward", actions)
    lines = block.split("\n")
    assert lines[0] == "# Event: onevent button.forward"
    assert lines[1] == "onevent button.forward"
    # The motor target lines are present...
    assert any("motor.left.target = 200" in ln for ln in lines)
    # ...and the block does NOT end with a bare 'end'.
    assert lines[-1].strip() != "end", block
    assert "end" not in [ln.strip() for ln in lines], block


def test_if_block_still_emits_its_own_end():
    """The conditional translators legitimately open/close blocks; removing the
    stray onevent 'end' must not remove the if-block's matching 'end'."""
    exp = _make_exporter()
    actions = [
        {"action": "thymio_if_button_pressed", "parameters": {"button": "center"}},
        {"action": "thymio_move_forward", "parameters": {"speed": "200"}},
        {"action": "end_block", "parameters": {}},
    ]
    block = exp._generate_event_handler("onevent buttons", actions)
    stripped = [ln.strip() for ln in block.split("\n")]
    # Exactly one 'end' — the one that closes the if-block.
    assert stripped.count("end") == 1, block
    assert any(ln.startswith("if button.center == 1 then") for ln in stripped)


def test_handler_with_no_actions_has_no_end():
    exp = _make_exporter()
    block = exp._generate_event_handler("onevent timer0", [])
    assert "end" not in [ln.strip() for ln in block.split("\n")], block


# --------------------------------------------------------------------------
# M32 — .aesl output is a valid aesl-source XML document
# --------------------------------------------------------------------------

def test_wrap_produces_parseable_xml_with_doctype():
    exp = _make_exporter()
    code = "onevent button.forward\n\tmotor.left.target = 200"
    doc = exp._wrap_aesl_document(code)

    assert doc.startswith("<!DOCTYPE aesl-source>")
    # Strip the DOCTYPE (ElementTree doesn't parse DOCTYPE-prefixed docs) and
    # confirm the remainder is well-formed XML with the expected structure.
    body = doc.split("\n", 1)[1]
    root = ET.fromstring(body)
    assert root.tag == "network"
    node = root.find("node")
    assert node is not None
    assert node.get("nodeId") == "1"
    assert node.get("name") == "thymio-II"
    # The generated source is preserved verbatim inside the node text (CDATA).
    assert "onevent button.forward" in node.text
    assert "motor.left.target = 200" in node.text


def test_wrap_preserves_xml_special_chars_in_code():
    """AESL comparisons use '<', '>', '&'; CDATA must keep them literal."""
    exp = _make_exporter()
    code = "if prox.horizontal[2] > 2000 then\n\tx = a < b\nend"
    doc = exp._wrap_aesl_document(code)
    body = doc.split("\n", 1)[1]
    node = ET.fromstring(body).find("node")
    assert "prox.horizontal[2] > 2000" in node.text
    assert "x = a < b" in node.text


def test_wrap_handles_cdata_terminator_defensively():
    exp = _make_exporter()
    code = "weird ]]> sequence"
    doc = exp._wrap_aesl_document(code)
    body = doc.split("\n", 1)[1]
    # Still well-formed despite the ']]>' in the source.
    node = ET.fromstring(body).find("node")
    assert "weird ]]> sequence" == node.text.strip()


def test_export_writes_xml_aesl_file(tmp_path):
    """End-to-end: a project with one Thymio object produces a parseable
    .aesl XML document containing the event handler and no stray 'end'."""
    project = {
        "name": "TestRobot",
        "assets": {
            "objects": {
                "thymio_player": {
                    "is_thymio": True,
                    "events": {
                        "thymio_button_forward": {
                            "actions": [
                                {
                                    "action": "thymio_move_forward",
                                    "parameters": {"speed": "200"},
                                }
                            ]
                        }
                    },
                }
            }
        },
    }
    proj_path = tmp_path / "project.json"
    import json
    proj_path.write_text(json.dumps(project), encoding="utf-8")

    out_dir = tmp_path / "out"
    exp = AsebaExporter()
    assert exp.export(str(proj_path), str(out_dir)) is True

    aesl = out_dir / "thymio_player.aesl"
    assert aesl.exists()
    text = aesl.read_text(encoding="utf-8")
    assert text.startswith("<!DOCTYPE aesl-source>")

    body = text.split("\n", 1)[1]
    node = ET.fromstring(body).find("node")
    code = node.text
    assert "onevent button.forward" in code
    assert "motor.left.target = 200" in code
    # No stray 'end' from the onevent handler (M33).
    assert "end" not in [ln.strip() for ln in code.split("\n")], code
