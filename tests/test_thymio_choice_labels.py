"""Regression tests for Thymio choice-param labels (audit M1).

docs/FULL_AUDIT_2026-06-11.md: sensor_index / sound_id choice options are
persisted as their full label string ("2 - Front Center", "0 - Startup")
because the GM80 action dialog saves widget.currentText(). The simulator's
_parse_value int()-parsed that and fell through to 0, so every non-default
sensor/sound selection silently used index 0; the Aseba exporter split
sound_id but passed sensor_index raw, emitting invalid Aseba like
`prox.horizontal[2 - Front Center]`.

Now _parse_value recovers the leading index from the label, and the Aseba
exporter routes sensor_index through the same split it already used for
sound_id.
"""

from conftest import import_module_directly

_handlers = import_module_directly("runtime/thymio_action_handlers.py")
_parse_value = _handlers._parse_value


class _Inst:
    pass


class TestParseValueChoiceLabels:
    def test_label_returns_leading_index(self):
        assert _parse_value("2 - Front Center", _Inst()) == 2
        assert _parse_value("0 - Startup", _Inst()) == 0
        assert _parse_value("1 - Right", _Inst()) == 1
        assert _parse_value("7 - Target Detected", _Inst()) == 7

    def test_plain_numbers_unaffected(self):
        assert _parse_value("440", _Inst()) == 440
        assert _parse_value("1.5", _Inst()) == 1.5
        assert _parse_value(3, _Inst()) == 3

    def test_variable_reference_still_resolves(self):
        inst = _Inst()
        inst.my_speed = 250
        assert _parse_value("my_speed", inst) == 250

    def test_unknown_string_still_zero(self):
        assert _parse_value("nonsense", _Inst()) == 0

    def test_arithmetic_like_string_not_misread_as_choice(self):
        # "5 - 1" is not a choice label (label text never starts with a
        # digit), so it must not be read as index 5.
        assert _parse_value("5 - 1", _Inst()) == 0


class TestAsebaSensorIndex:
    def _exporter(self):
        from export.Aseba.aseba_exporter import AsebaExporter
        return AsebaExporter()

    def test_if_proximity_strips_label(self):
        exp = self._exporter()
        line = exp._translate_if_proximity(
            {'sensor_index': '2 - Front Center', 'threshold': '2000', 'comparison': '>'})
        assert 'prox.horizontal[2]' in line
        assert 'Front Center' not in line

    def test_if_ground_dark_strips_label(self):
        exp = self._exporter()
        line = exp._translate_if_ground_dark(
            {'sensor_index': '1 - Right', 'threshold': '300'})
        assert 'prox.ground.delta[1]' in line

    def test_play_system_sound_still_strips(self):
        exp = self._exporter()
        line = exp._translate_play_system_sound({'sound_id': '3 - Free-fall'})
        assert 'sound.system(3)' in line

    def test_plain_sensor_index_passes_through(self):
        exp = self._exporter()
        line = exp._translate_if_proximity(
            {'sensor_index': '4', 'threshold': '2000', 'comparison': '>'})
        assert 'prox.horizontal[4]' in line
