"""The `<param>_translations` convention, honoured for every display string.

`events/action_editor.py` has let an author add translations to ANY string
parameter since its translation dialog was written -- it stores them as
`<param>_translations` dicts. But the runtime only ever read
`message_translations`, and only for show_message, so translations entered for
a `draw_text` were accepted by the IDE and silently ignored by the engine.

These tests pin the general behaviour, and the fallbacks: an untranslated
string, an unknown language, an empty translation and a missing runner must all
leave the base English text exactly as it was.
"""
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

from runtime.action_executor import ActionExecutor  # noqa: E402


class _Runner:
    def __init__(self, language="en"):
        self.language = language
        self.global_variables = {}
        self.score = 7


def _ex(language="en"):
    return ActionExecutor(game_runner=_Runner(language))


class TestLocalizeParam:
    PARAMS = {"message": "Hello!",
              "message_translations": {"fr": "Bonjour !", "de": "Hallo!"}}

    def test_english_uses_the_base_value(self):
        assert _ex("en").localize_param(self.PARAMS, "message") == "Hello!"

    def test_a_translated_language_wins(self):
        assert _ex("fr").localize_param(self.PARAMS, "message") == "Bonjour !"

    def test_the_base_value_wins_even_if_the_dict_has_an_en_entry(self):
        """English is the base string by definition, so an `en` entry in the
        dict is redundant and deliberately ignored -- the same short-circuit
        show_message's original inline code had. Without a dict containing
        `en`, a test cannot tell whether that guard is still there."""
        params = {"message": "Hello!",
                  "message_translations": {"en": "SOMETHING ELSE",
                                           "fr": "Bonjour !"}}
        assert _ex("en").localize_param(params, "message") == "Hello!"

    def test_an_untranslated_language_falls_back(self):
        assert _ex("ja").localize_param(self.PARAMS, "message") == "Hello!"

    def test_no_translation_dict_falls_back(self):
        assert _ex("fr").localize_param({"message": "Hi"}, "message") == "Hi"

    def test_an_empty_translation_falls_back(self):
        """Better the English than a blank message on screen."""
        params = {"message": "Hi", "message_translations": {"fr": ""}}
        assert _ex("fr").localize_param(params, "message") == "Hi"

    def test_a_non_dict_translations_value_is_ignored(self):
        params = {"message": "Hi", "message_translations": "oops"}
        assert _ex("fr").localize_param(params, "message") == "Hi"

    def test_it_survives_having_no_runner(self):
        ex = ActionExecutor(game_runner=None)
        assert ex.localize_param(self.PARAMS, "message") == "Hello!"

    def test_the_default_is_returned_when_absent(self):
        assert _ex("fr").localize_param({}, "caption", "Score: ") == "Score: "

    @pytest.mark.parametrize("name", ["message", "text", "caption"])
    def test_it_works_for_any_parameter_name(self, name):
        """The whole point: not just `message`. The IDE offers this for every
        string parameter."""
        params = {name: "Lives:", "%s_translations" % name: {"fr": "Vies :"}}
        assert _ex("fr").localize_param(params, name) == "Vies :"


class TestTheDisplayActionsUseIt:
    """Wired through the actions that actually put text on screen."""

    class _Instance:
        object_name = "obj_test"
        x = y = 0

        def __init__(self):
            self._draw_queue = []

    def test_show_message_is_translated(self):
        ex = _ex("fr")
        seen = []
        ex._show_or_queue_message = lambda inst, msg: seen.append(msg)
        ex.execute_show_message_action(self._Instance(), {
            "message": "You win!",
            "message_translations": {"fr": "Tu as gagné !"}})
        assert seen == ["Tu as gagné !"]

    def test_draw_text_is_translated(self):
        ex = _ex("fr")
        inst = self._Instance()
        ex.execute_draw_text_action(inst, {
            "text": '"Lives:"', "x": "8", "y": "8",
            "text_translations": {"fr": '"Vies :"'}})
        assert [c["text"] for c in inst._draw_queue] == ["Vies :"]

    def test_draw_score_caption_is_translated(self):
        ex = _ex("fr")
        inst = self._Instance()
        ex.execute_draw_score_action(inst, {
            "x": "8", "y": "8", "caption": "Score: ",
            "caption_translations": {"fr": "Points : "}})
        assert inst._draw_queue[-1]["text"] == "Points : 7"

    def test_english_is_unchanged(self):
        """No regression for the 20 samples that carry no translations."""
        ex = _ex("en")
        inst = self._Instance()
        ex.execute_draw_text_action(inst, {
            "text": '"Lives:"', "x": "8", "y": "8",
            "text_translations": {"fr": '"Vies :"'}})
        assert [c["text"] for c in inst._draw_queue] == ["Lives:"]
