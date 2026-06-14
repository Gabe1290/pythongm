"""Regression tests for L20 (package name), L21 (show_message escaping),
L22 (background filename) in the Kivy export path.
"""

from pathlib import Path

import pytest


class TestPackageNameAscii:  # L20
    def _gen(self, name):
        from export.Kivy.buildspec_generator import BuildspecGenerator
        gen = BuildspecGenerator({}, Path("."))
        return gen._generate_package_name(name)

    def test_accented_name_becomes_ascii(self):
        pkg = self._gen("L'épopée")
        assert all(c.isascii() for c in pkg)
        assert pkg == "l_epopee"  # accents transliterated, apostrophe -> _

    def test_plain_name(self):
        assert self._gen("Maze Game") == "maze_game"

    def test_empty_falls_back(self):
        assert self._gen("éàü") == "kivygame" or self._gen("éàü").isascii()


class TestShowMessageEscaping:  # L21
    def _gen(self, message):
        from export.Kivy.code_generator import ActionCodeGenerator
        g = ActionCodeGenerator(base_indent=0)
        g.process_action({"action": "show_message",
                          "parameters": {"message": message}}, "step")
        return g.get_code()

    @pytest.mark.parametrize("message", [
        'plain',
        'has "double" quotes',
        "has 'single' quotes",
        "trailing backslash\\",
        "line one\nline two",
        "mixed \"q\" and \\ and \n",
    ])
    def test_generated_message_compiles(self, message):
        code = self._gen(message)
        # The generated statement must be syntactically valid Python.
        compile(code, "gen.py", "exec")


class TestBackgroundFilename:  # L22
    def test_non_png_background_uses_real_filename(self, tmp_path):
        from export.Kivy.kivy_exporter import KivyExporter
        project = {
            "name": "T",
            "assets": {
                "rooms": {"r1": {"width": 320, "height": 240,
                                 "background_image": "fond",
                                 "instances": []}},
                "objects": {},
                "sprites": {},
                "backgrounds": {"fond": {"name": "fond",
                                         "file_path": "backgrounds/fond.jpg"}},
            },
        }
        out = tmp_path / "out"
        (out / "game" / "scenes").mkdir(parents=True)
        ex = KivyExporter(project, tmp_path, out)
        ex._generate_scene("r1", project["assets"]["rooms"]["r1"])
        scene_src = (out / "game" / "scenes" / "r1.py").read_text(encoding="utf-8")
        assert "assets/images/fond.jpg" in scene_src
        assert "assets/images/fond.png" not in scene_src
