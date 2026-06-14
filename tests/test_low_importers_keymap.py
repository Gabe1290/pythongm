"""Regression tests for L25 (keymap), L26 (BMP dimension cap), L27 (Roberta RGB).

L25: runtime keymap never produced numpad/punctuation names the GMK importer
emits, so those imported keyboard events could never fire.
L26: untrusted BMP header dimensions were unbounded -> huge allocation / hang.
L27: non-literal Roberta LED RGB channel crashed the import with ValueError.
"""

import struct
import xml.etree.ElementTree as ET

import pytest


class TestKeymapExtended:  # L25
    def test_numpad_and_punctuation_names(self):
        pygame = pytest.importorskip("pygame")
        from runtime._keymap import pygame_key_name

        # Sample of names the GMK importer emits (gmk_mappings.py).
        checks = {
            "K_KP5": "numpad_5", "K_KP_5": "numpad_5",
            "K_SEMICOLON": "semicolon",
            "K_COMMA": "comma",
            "K_PERIOD": "period",
            "K_SLASH": "slash",
            "K_QUOTE": "quote",
        }
        seen = set()
        for attr, expected in checks.items():
            code = getattr(pygame, attr, None)
            if code is not None:
                assert pygame_key_name(code) == expected
                seen.add(expected)
        # At least the core punctuation set must resolve on any pygame version.
        assert {"semicolon", "comma", "period", "slash"} <= seen

    def test_arrows_and_letters_unchanged(self):
        pygame = pytest.importorskip("pygame")
        from runtime._keymap import pygame_key_name
        assert pygame_key_name(pygame.K_LEFT) == "left"
        assert pygame_key_name(pygame.K_a) == "a"


class TestBmpDimensionCap:  # L26
    def _bmp_header(self, width, height, bpp=24, data_len=4):
        # Minimal BM header (54 bytes) with the given dimensions.
        hdr = bytearray(54 + data_len)
        hdr[0:2] = b"BM"
        struct.pack_into("<I", hdr, 10, 54)        # data offset
        struct.pack_into("<i", hdr, 18, width)
        struct.pack_into("<i", hdr, 22, height)
        struct.pack_into("<H", hdr, 28, bpp)
        return bytes(hdr)

    def test_oversized_rejected(self):
        from importers.gmk_parser import _bmp_to_bgra
        with pytest.raises(ValueError):
            _bmp_to_bgra(self._bmp_header(46340, 46340))

    def test_zero_rejected(self):
        from importers.gmk_parser import _bmp_to_bgra
        with pytest.raises(ValueError):
            _bmp_to_bgra(self._bmp_header(0, 10))

    def test_small_ok(self):
        from importers.gmk_parser import _bmp_to_bgra
        w, h, data = _bmp_to_bgra(self._bmp_header(2, 2, 24, data_len=2 * 2 * 4))
        assert (w, h) == (2, 2)


class TestRobertaRgbGuard:  # L27
    def _rgb_led_block(self, red_block):
        xml = f"""
        <block type="mbedActions_leds_on">
          <field name="LED">TOP</field>
          <value name="COLOR">
            <block type="robColour_rgb">
              <value name="RED">{red_block}</value>
              <value name="GREEN"><block type="math_number"><field name="NUM">0</field></block></value>
              <value name="BLUE"><block type="math_number"><field name="NUM">0</field></block></value>
            </block>
          </value>
        </block>
        """
        return ET.fromstring(xml)

    def test_variable_driven_channel_does_not_crash(self):
        from importers.roberta_importer import _convert_block, RobertaImportResult
        # RED driven by a variable block -> non-literal; must not raise.
        var_block = '<block type="variables_get"><field name="VAR">x</field></block>'
        actions = _convert_block(self._rgb_led_block(var_block), RobertaImportResult())
        assert len(actions) == 1
        params = actions[0]["parameters"]
        assert params["red"] == "0"  # fell back to 0
