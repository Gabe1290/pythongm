"""Kivy export: play_music, stop_music and set_volume (the Audio actions that
were the only non-network actions the Kivy generator reported as unsupported).

Codegen is checked directly; the generated main.py helpers are then EXECUTED
(extracted from a real export) against a fake ``SoundLoader``, matching the
desktop semantics of plugins/audio_actions.py: one music track at a time,
loop and volume honoured, set_volume applies to the music and every loaded
sound effect.
"""
import ast
import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402
from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402

PATHS = {"snd_theme": "assets/sounds/snd_theme.ogg", "snd_boom": "assets/sounds/snd_boom.wav"}


def _gen(action, params):
    return ActionCodeGenerator(sound_paths=PATHS)._convert_simple_action(action, params, "create")


# -- codegen ---------------------------------------------------------------------

def test_play_music_codegen_defaults_match_desktop():
    assert _gen("play_music", {"music": "snd_theme"}) == \
        "from main import play_music; play_music('assets/sounds/snd_theme.ogg', True, 0.7)"


def test_play_music_loop_and_volume_are_honoured_including_string_booleans():
    code = _gen("play_music", {"music": "snd_theme", "loop": "false", "volume": "0.25"})
    assert code.endswith("play_music('assets/sounds/snd_theme.ogg', False, 0.25)")


def test_an_unknown_music_is_a_commented_noop():
    assert _gen("play_music", {"music": "nope"}).startswith("pass  # play_music: music 'nope'")


def test_stop_music_and_set_volume_codegen():
    assert _gen("stop_music", {}) == "from main import stop_music; stop_music()"
    assert _gen("set_volume", {"volume": 0.3}) == "from main import set_volume; set_volume(0.3)"
    assert _gen("set_volume", {}) == "from main import set_volume; set_volume(1)"


def test_the_three_actions_are_no_longer_reported_unsupported():
    import export.Kivy.code_generator as cg
    cg.reset_unsupported_actions()
    g = ActionCodeGenerator(sound_paths=PATHS)
    for name in ("play_music", "stop_music", "set_volume"):
        g.process_action({"action_type": name, "parameters": {"music": "snd_theme"}}, "step")
    assert not set(cg.get_unsupported_actions()) & {"play_music", "stop_music", "set_volume"}


# -- the generated helpers, executed -----------------------------------------------

class _Snd:
    def __init__(self, path):
        self.path, self.volume, self.loop, self.state = path, 1.0, False, "stop"

    def play(self):
        self.state = "play"

    def stop(self):
        self.state = "stop"


@pytest.fixture()
def helpers(tmp_path):
    pytest.importorskip("PySide6")
    from export.Kivy.kivy_exporter import KivyExporter
    sample = ROOT / "samples" / "plateforme_1"
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    out = tmp_path / "export"
    assert KivyExporter(data, sample, out).export()
    src = (out / "game" / "main.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    wanted = {"play_sound", "stop_sound", "play_music", "stop_music", "set_volume"}
    parts = [ast.get_source_segment(src, n) for n in tree.body
             if (isinstance(n, ast.FunctionDef) and n.name in wanted)
             or (isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") in ("_music", "_sound_cache"))]
    assert len(parts) == 7, len(parts)
    loaded = []

    class _Loader:
        @staticmethod
        def load(path):
            s = _Snd(path)
            loaded.append(s)
            return s

    mod = types.ModuleType("kivy.core.audio")
    mod.SoundLoader = _Loader
    saved = {k: sys.modules.get(k) for k in ("kivy", "kivy.core", "kivy.core.audio")}
    for k in ("kivy", "kivy.core"):
        sys.modules[k] = types.ModuleType(k)
    sys.modules["kivy.core.audio"] = mod
    ns = {"_log": lambda *a, **k: None}
    exec("\n\n".join(parts), ns)
    ns["_loaded"] = loaded
    yield ns
    for k, v in saved.items():
        if v is None:
            sys.modules.pop(k, None)
        else:
            sys.modules[k] = v


@skip_without_pyside6
def test_play_music_loops_sets_volume_and_replaces_the_previous_track(helpers):
    helpers["play_music"]("a.ogg", True, 0.4)
    first = helpers["_loaded"][-1]
    assert (first.state, first.loop, first.volume) == ("play", True, 0.4)
    helpers["play_music"]("b.ogg", False, 5)            # volume clamped to 1.0
    second = helpers["_loaded"][-1]
    assert first.state == "stop"
    assert (second.state, second.loop, second.volume) == ("play", False, 1.0)


@skip_without_pyside6
def test_stop_music_stops_it_and_is_safe_with_no_music(helpers):
    helpers["stop_music"]()                              # nothing playing: no error
    helpers["play_music"]("a.ogg")
    helpers["stop_music"]()
    assert helpers["_loaded"][-1].state == "stop"


@skip_without_pyside6
def test_set_volume_applies_to_music_and_every_loaded_sound_effect(helpers):
    helpers["play_sound"]("fx1.wav", 1.0)
    helpers["play_sound"]("fx2.wav", 0.5)
    helpers["play_music"]("m.ogg", True, 0.7)
    helpers["set_volume"](0.2)
    assert [s.volume for s in helpers["_loaded"]] == [0.2, 0.2, 0.2]
    helpers["set_volume"]("junk")                        # bad value: logged, no crash
    assert [s.volume for s in helpers["_loaded"]] == [0.2, 0.2, 0.2]
