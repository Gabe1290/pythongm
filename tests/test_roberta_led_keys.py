"""Regression test for Roberta LED colour import (audit M42).

The importer emitted LED actions with keys r/g/b, but the runtime, action
editor and Aseba exporter all read red/green/blue — so imported LED colours
were silently lost (every consumer defaulted to 0). The importer now emits the
canonical keys.
"""

import xml.etree.ElementTree as ET

import pytest

from importers.roberta_importer import _convert_block, RobertaImportResult


def _led_block(led="TOP", hex_colour="#ff0000"):
    xml = f"""
    <block type="mbedActions_leds_on">
      <field name="LED">{led}</field>
      <value name="COLOR">
        <block type="robColour_picker">
          <field name="COLOUR">{hex_colour}</field>
        </block>
      </value>
    </block>
    """
    return ET.fromstring(xml)


def _convert(led="TOP", hex_colour="#ff0000"):
    actions = _convert_block(_led_block(led, hex_colour), RobertaImportResult())
    assert len(actions) == 1
    return actions[0]


def test_led_top_uses_canonical_keys():
    action = _convert("TOP", "#ff0000")
    assert action["action"] == "thymio_set_led_top"
    params = action["parameters"]
    assert set(params) == {"red", "green", "blue"}
    assert "r" not in params and "g" not in params and "b" not in params


def test_led_colour_value_preserved():
    # #ff0000 -> red scaled to the 0-32 Thymio range (255*32//255 = 32).
    params = _convert("TOP", "#ff0000")["parameters"]
    assert params["red"] == "32"
    assert params["green"] == "0"
    assert params["blue"] == "0"


def test_led_bottom_left_and_right():
    assert _convert("BOTTOM_LEFT")["action"] == "thymio_set_led_bottom_left"
    assert _convert("BOTTOM_RIGHT")["action"] == "thymio_set_led_bottom_right"
    assert set(_convert("BOTTOM_LEFT")["parameters"]) == {"red", "green", "blue"}
