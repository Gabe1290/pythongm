"""Regression tests for the Open Roberta importer LED-colour handling.

Covers two audit findings (docs/FULL_AUDIT_2026-06-11.md):

- M42: the importer must emit LED colour params under the canonical keys
  ``red``/``green``/``blue`` (what the runtime handler + action editor read),
  not ``r``/``g``/``b`` (which every consumer ignores → silent 0/0/0 LEDs).
- L27: a robColour_rgb block whose channel is a variable / arithmetic
  expression (a non-literal string) must not crash the import with an
  unhandled ValueError — it falls back to 0 with a warning.

Pure-logic tests (XML element fixtures), no Qt needed.
"""

import xml.etree.ElementTree as ET

from importers.roberta_importer import (
    _convert_block,
    _extract_color,
    RobertaImportResult,
)


def _block(xml: str):
    """Parse a single <block> fragment into an Element."""
    return ET.fromstring(xml)


# Canonical key names read by the runtime + action editor.
CANON_KEYS = {"red", "green", "blue"}


def _leds_on_block(led, color_inner):
    """Build an mbedActions_leds_on block with a COLOR value sub-block."""
    return _block(
        f"""
        <block type="mbedActions_leds_on">
          <field name="LED">{led}</field>
          <value name="COLOR">
            {color_inner}
          </value>
        </block>
        """
    )


def _rgb_color(red, green, blue):
    """Build a robColour_rgb COLOR sub-block with the given channel inners."""
    return (
        '<block type="robColour_rgb">'
        f'<value name="RED">{red}</value>'
        f'<value name="GREEN">{green}</value>'
        f'<value name="BLUE">{blue}</value>'
        "</block>"
    )


def _color_carrier(color_inner):
    """Wrap a colour sub-block in a host block exposing it under COLOR.

    ``_extract_color`` reads ``<value name="COLOR">`` from the block it's
    given, so the direct-call tests need an enclosing block.
    """
    return _block(
        '<block type="mbedActions_leds_on">'
        f'<value name="COLOR">{color_inner}</value>'
        "</block>"
    )


def _num(n):
    return f'<block type="math_number"><field name="NUM">{n}</field></block>'


# --------------------------------------------------------------------------
# M42 — canonical red/green/blue keys
# --------------------------------------------------------------------------

def test_led_top_uses_canonical_keys():
    result = RobertaImportResult()
    block = _leds_on_block("TOP", _rgb_color(_num(255), _num(0), _num(0)))
    actions = _convert_block(block, result)
    assert len(actions) == 1
    params = actions[0]["parameters"]
    assert actions[0]["action"] == "thymio_set_led_top"
    assert set(params.keys()) == CANON_KEYS
    # 255 scaled to Thymio 0-32 range.
    assert int(params["red"]) == 32
    assert int(params["green"]) == 0
    assert int(params["blue"]) == 0


def test_led_bottom_left_uses_canonical_keys():
    result = RobertaImportResult()
    block = _leds_on_block(
        "BOTTOM_LEFT", _rgb_color(_num(0), _num(255), _num(0)))
    actions = _convert_block(block, result)
    params = actions[0]["parameters"]
    assert actions[0]["action"] == "thymio_set_led_bottom_left"
    assert set(params.keys()) == CANON_KEYS
    assert int(params["green"]) == 32


def test_led_bottom_right_uses_canonical_keys():
    result = RobertaImportResult()
    block = _leds_on_block(
        "BOTTOM_RIGHT", _rgb_color(_num(0), _num(0), _num(255)))
    actions = _convert_block(block, result)
    params = actions[0]["parameters"]
    assert actions[0]["action"] == "thymio_set_led_bottom_right"
    assert set(params.keys()) == CANON_KEYS
    assert int(params["blue"]) == 32


def test_no_legacy_rgb_keys_emitted():
    result = RobertaImportResult()
    block = _leds_on_block("TOP", _rgb_color(_num(10), _num(20), _num(30)))
    params = _convert_block(block, result)[0]["parameters"]
    for legacy in ("r", "g", "b"):
        assert legacy not in params


# --------------------------------------------------------------------------
# L27 — non-literal RGB channels must not crash
# --------------------------------------------------------------------------

def test_rgb_variable_channel_does_not_crash():
    # variables_get resolves to the variable name (non-numeric string).
    var = '<block type="variables_get"><field name="VAR">myColor</field></block>'
    block = _color_carrier(_rgb_color(var, _num(0), _num(0)))
    result = RobertaImportResult()
    # Must not raise ValueError.
    rgb = _extract_color(block, result)
    assert rgb == (0, 0, 0)
    assert any("RED" in w for w in result.warnings)


def test_rgb_arithmetic_channel_does_not_crash():
    # math_arithmetic resolves to "(a + b)" — float() would raise.
    arith = (
        '<block type="math_arithmetic">'
        '<field name="OP">ADD</field>'
        f'<value name="A">{_num(0)}</value>'
        f'<value name="B">{_num(0)}</value>'
        "</block>"
    )
    block = _color_carrier(_rgb_color(arith, _num(255), arith))
    result = RobertaImportResult()
    rgb = _extract_color(block, result)
    # GREEN is a literal 255 → 32; RED/BLUE expressions fall back to 0.
    assert rgb == (0, 32, 0)
    # One warning per bad channel.
    assert sum("expression" in w for w in result.warnings) == 2


def test_rgb_full_import_path_with_expression_does_not_crash():
    # End-to-end through _convert_block (the path that previously crashed).
    var = '<block type="variables_get"><field name="VAR">c</field></block>'
    block = _leds_on_block("TOP", _rgb_color(var, var, var))
    result = RobertaImportResult()
    actions = _convert_block(block, result)
    params = actions[0]["parameters"]
    assert params["red"] == "0"
    assert params["green"] == "0"
    assert params["blue"] == "0"


def test_extract_color_works_without_result_arg():
    # Backward-compatible: result is optional.
    var = '<block type="variables_get"><field name="VAR">c</field></block>'
    block = _color_carrier(_rgb_color(var, _num(0), _num(0)))
    assert _extract_color(block) == (0, 0, 0)
