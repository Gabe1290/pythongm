"""Authored translations are baked in at EXPORT time.

The desktop runtime honours `<param>_translations` at play time. The export
engines do not and deliberately will not: `engine.js`'s `show_message` reads
`params.message` only, and `export/Kivy/` has no notion of translations. So the
exporter resolves the dict into the plain parameter and drops it, which is what
stops an exported game disagreeing with the desktop about what a message says.

That is also the answer to the objection recorded in
`tests/test_raycast_2_sample.py` -- that translating a sample would make it
"behave differently on every export target". True while the targets ignored the
dicts; false once the exporter resolves them.
"""
import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.message_localizer import (  # noqa: E402
    count_translation_dicts, resolve_translations)


def _actions(**params):
    return {"assets": {"objects": {"obj_a": {"events": {"create": {
        "actions": [{"action": "show_message", "parameters": params}]}}}}}}


def _params(project):
    return (project["assets"]["objects"]["obj_a"]["events"]["create"]
            ["actions"][0]["parameters"])


class TestResolveTranslations:
    BASE = {"message": "You win!",
            "message_translations": {"fr": "Tu as gagné !", "de": "Gewonnen!"}}

    def test_the_chosen_language_replaces_the_base(self):
        out = resolve_translations(_actions(**self.BASE), "fr")
        assert _params(out)["message"] == "Tu as gagné !"

    def test_a_different_language_gets_its_own(self):
        out = resolve_translations(_actions(**self.BASE), "de")
        assert _params(out)["message"] == "Gewonnen!"

    def test_the_dict_is_always_dropped(self):
        """An exported project must carry no dicts at all -- a leftover one
        would mean that string silently stayed English on that target."""
        for lang in ("fr", "de", "en", "", "ja"):
            out = resolve_translations(_actions(**self.BASE), lang)
            assert "message_translations" not in _params(out)
            assert count_translation_dicts(out) == 0

    @pytest.mark.parametrize("lang", ["en", "", None])
    def test_english_resolves_nothing_but_still_strips(self, lang):
        out = resolve_translations(_actions(**self.BASE), lang)
        assert _params(out)["message"] == "You win!"

    def test_an_untranslated_language_keeps_the_english(self):
        out = resolve_translations(_actions(**self.BASE), "ja")
        assert _params(out)["message"] == "You win!"

    def test_an_empty_translation_keeps_the_english(self):
        """Better English than a blank message on screen."""
        out = resolve_translations(
            _actions(message="Hi", message_translations={"fr": ""}), "fr")
        assert _params(out)["message"] == "Hi"

    def test_it_works_for_any_parameter_not_just_message(self):
        out = resolve_translations(_actions(
            text="Lives:", text_translations={"fr": "Vies :"}), "fr")
        assert _params(out)["text"] == "Vies :"

    def test_it_reaches_into_lists_and_nesting(self):
        deep = {"a": [{"b": [{"parameters": {
            "caption": "Score: ",
            "caption_translations": {"fr": "Points : "}}}]}]}
        out = resolve_translations(deep, "fr")
        assert out["a"][0]["b"][0]["parameters"]["caption"] == "Points : "

    def test_the_input_is_not_mutated(self):
        """Kivy exporters are handed project data; corrupting a caller's dict
        would be a nasty way to lose an author's translations."""
        project = _actions(**self.BASE)
        resolve_translations(project, "fr")
        assert _params(project)["message"] == "You win!"
        assert count_translation_dicts(project) == 1

    def test_a_non_dict_translations_value_is_left_alone(self):
        out = resolve_translations(
            _actions(message="Hi", message_translations="oops"), "fr")
        assert _params(out)["message"] == "Hi"
        assert _params(out)["message_translations"] == "oops"

    def test_a_bare_translations_key_is_ignored(self):
        """`_translations` with no base parameter name has nothing to apply to
        and must not crash or invent a key."""
        out = resolve_translations(_actions(**{"_translations": {"fr": "x"}}), "fr")
        assert "" not in _params(out)


@pytest.fixture
def translated_project(tmp_path):
    """A minimal but real project directory with one translated message."""
    import shutil
    dest = tmp_path / "maze_1"
    shutil.copytree(REPO_ROOT / "samples" / "maze_1", dest)

    action = {"action": "show_message",
              "parameters": {"message": "ENGLISH_SENTINEL",
                             "message_translations": {"fr": "FRENCH_SENTINEL"}}}

    # Written into the OBJECT SIDE FILE, not just project.json's embedded copy.
    # Both exporters merge objects/*.json over the embedded objects, so a
    # sentinel placed only in project.json is overwritten before it is ever
    # resolved -- which is what the first version of this fixture did, and it
    # is the same staleness the merge exists to fix.
    side = sorted((dest / "objects").glob("*.json"))[0]
    obj = json.loads(side.read_text(encoding="utf-8"))
    obj.setdefault("events", {}).setdefault("game_start", {"actions": []})
    obj["events"]["game_start"]["actions"].append(action)
    side.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    data = json.loads((dest / "project.json").read_text(encoding="utf-8"))
    embedded = data["assets"]["objects"][obj["name"]]
    embedded.setdefault("events", {}).setdefault("game_start", {"actions": []})
    embedded["events"]["game_start"]["actions"].append(dict(action))
    (dest / "project.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return dest


class TestHtml5ExportBakesTheLanguageIn:
    @staticmethod
    def _embedded_game_data(html):
        """The project JSON actually shipped inside the page.

        gameData is gzip+base64 compressed into the template, so asserting on
        the raw HTML text proves nothing: an earlier version of these tests
        "passed" while searching for a string that could not appear either way.
        Inflate it and assert on the real data.
        """
        import base64
        import gzip
        import re
        m = re.search(r'decompressData\("([A-Za-z0-9+/=]+)"\)', html)
        assert m, "could not find the embedded gameData in the export"
        return gzip.decompress(base64.b64decode(m.group(1))).decode("utf-8")

    def _export(self, project_dir, out_dir, language):
        from export.HTML5.html5_exporter import HTML5Exporter
        out_dir.mkdir(parents=True, exist_ok=True)
        exporter = HTML5Exporter()
        assert exporter.export(project_dir, out_dir, {"language": language}), \
            exporter.last_error_message
        html = list(out_dir.glob("*.html"))
        assert len(html) == 1
        return self._embedded_game_data(html[0].read_text(encoding="utf-8"))

    def test_french_export_carries_the_french_string(self, translated_project,
                                                     tmp_path):
        html = self._export(translated_project, tmp_path / "fr", "fr")
        assert "FRENCH_SENTINEL" in html
        assert "ENGLISH_SENTINEL" not in html

    def test_english_export_carries_the_english_string(self, translated_project,
                                                       tmp_path):
        html = self._export(translated_project, tmp_path / "en", "en")
        assert "ENGLISH_SENTINEL" in html
        assert "FRENCH_SENTINEL" not in html

    def test_no_translation_dict_survives_into_the_export(self, translated_project,
                                                          tmp_path):
        """engine.js would ignore one, so a survivor means a silent English
        string on the web target."""
        html = self._export(translated_project, tmp_path / "fr2", "fr")
        assert "message_translations" not in html


class TestKivyFamilyExportResolvesToo:
    """exe / linux / macos / android all share BaseKivyExporter._load_project,
    so hooking that one funnel covers every desktop and mobile target."""

    def test_load_project_resolves_translations(self, translated_project):
        from export.base_exporter import BaseKivyExporter
        exporter = BaseKivyExporter()
        exporter._load_project(str(translated_project), str(translated_project),
                               {"language": "fr"})
        blob = json.dumps(exporter.project_data, ensure_ascii=False)
        assert "FRENCH_SENTINEL" in blob
        assert "ENGLISH_SENTINEL" not in blob
        assert count_translation_dicts(exporter.project_data) == 0

    def test_it_happens_after_the_side_file_merge(self, translated_project):
        """The merge pulls objects/*.json over the embedded copies, so
        resolving before it would leave those objects' dicts untouched."""
        src = Path(__file__).resolve().parent.parent / "export" / "base_exporter.py"
        text = src.read_text(encoding="utf-8")
        assert text.index("_load_objects_from_files(project_dir)") < \
            text.index("resolve_translations(")
