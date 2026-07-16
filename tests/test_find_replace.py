"""Find / Find and Replace (deferred-items plan Tier 2 item 5).

Restores the Edit -> Find... (Ctrl+F) / Edit -> Find and Replace...
(Ctrl+H) menu entries removed in rc.11's "stop lying to users" cleanup
(commit 77e9dbf), which deleted the "Not Implemented" placeholder stubs
and tracked the real feature in TODO.md instead.

Scope: the code editor (editors/script_editor.py's QPlainTextEdit) only
for this first pass — see dialogs/find_replace_dialog.py's module
docstring for what's deliberately not covered yet.

FindReplaceDialog's search/replace logic is tested directly against a
real QPlainTextEdit (constructs an offscreen QApplication rather than
using pytest-qt, matching test_room_canvas_cache_clear.py's pattern so
it runs anywhere PySide6 is installed). The IDE-level dispatch
(find()/find_replace()/_find_target_text_edit()) is tested with the
lightweight SimpleNamespace-stub-calling-unbound-methods pattern
established by test_play_object.py / test_game_subprocess_supervision.py,
to avoid standing up the full Qt main window.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _identity_tr(text):
    return text


# ---------------------------------------------------------------------------
# FindReplaceDialog — search/replace logic against a real QPlainTextEdit
# ---------------------------------------------------------------------------

class TestFindReplaceDialog:
    def _dialog_with_text(self, _qapp, text):
        from PySide6.QtWidgets import QPlainTextEdit
        from dialogs.find_replace_dialog import FindReplaceDialog
        edit = QPlainTextEdit()
        edit.setPlainText(text)
        dialog = FindReplaceDialog()
        dialog.set_target(edit)
        return dialog, edit

    def test_find_next_selects_first_match(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "the cat sat on the mat")
        dialog.find_field.setText("cat")
        assert dialog.find_next() is True
        assert edit.textCursor().selectedText() == "cat"

    def test_find_next_wraps_around(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "cat dog cat")
        dialog.find_field.setText("cat")
        dialog._search()  # first match
        dialog._search()  # second match (the trailing "cat")
        cursor = edit.textCursor()
        assert cursor.selectedText() == "cat"
        assert cursor.selectionStart() == 8  # the second occurrence
        # A third search has nothing left forward, so it must wrap back
        # to the first occurrence instead of reporting not-found.
        found = dialog._search()
        assert found is True
        assert edit.textCursor().selectionStart() == 0

    def test_not_found_sets_status_label(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "hello world")
        dialog.find_field.setText("xyz")
        found = dialog._search()
        assert found is False
        assert dialog.status_label.text() == "Phrase not found"

    def test_case_sensitive_search(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "Cat cat")
        dialog.find_field.setText("cat")
        dialog.case_checkbox.setChecked(True)
        assert dialog._search() is True
        assert edit.textCursor().selectionStart() == 4  # skips "Cat"

    def test_whole_word_search_skips_partial_matches(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "concatenate cat")
        dialog.find_field.setText("cat")
        dialog.whole_word_checkbox.setChecked(True)
        assert dialog._search() is True
        assert edit.textCursor().selectionStart() == 12  # the standalone "cat"

    def test_replace_current_only_acts_on_a_live_match(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "foo bar foo")
        dialog.find_field.setText("foo")
        dialog.replace_field.setText("baz")
        dialog._search()  # selects the first "foo"
        dialog.replace_current()
        assert edit.toPlainText() == "baz bar foo"
        # replace_current also advances to (selects) the next match.
        assert edit.textCursor().selectedText() == "foo"

    def test_replace_current_noop_without_a_prior_search(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "foo bar")
        dialog.find_field.setText("foo")
        dialog.replace_field.setText("baz")
        # No _search() call yet -> nothing selected -> Replace must not
        # blindly overwrite whatever the cursor happens to be sitting on.
        dialog.replace_current()
        assert edit.toPlainText() == "foo bar"

    def test_replace_all_replaces_every_occurrence(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "cat cat cat")
        dialog.find_field.setText("cat")
        dialog.replace_field.setText("dog")
        dialog.replace_all()
        assert edit.toPlainText() == "dog dog dog"
        assert dialog.status_label.text() == "3 replacement(s) made"

    def test_replace_all_does_not_loop_when_replacement_contains_search_text(self, _qapp):
        # The classic replace-all footgun: replacing "cat" with "cats cat"
        # would re-match its own output forever with a naive
        # find-from-start-every-time implementation.
        dialog, edit = self._dialog_with_text(_qapp, "cat")
        dialog.find_field.setText("cat")
        dialog.replace_field.setText("cats cat")
        dialog.replace_all()
        assert edit.toPlainText() == "cats cat"
        assert dialog.status_label.text() == "1 replacement(s) made"

    def test_replace_all_empty_search_is_a_noop(self, _qapp):
        dialog, edit = self._dialog_with_text(_qapp, "hello")
        dialog.find_field.setText("")
        dialog.replace_all()
        assert edit.toPlainText() == "hello"

    def test_set_replace_visible_toggles_replace_widgets(self, _qapp):
        dialog, _ = self._dialog_with_text(_qapp, "x")
        dialog.set_replace_visible(False)
        # isHidden() reflects the widget's own explicit visibility flag
        # regardless of whether the (never-shown-in-this-test) parent
        # dialog is visible, unlike isVisible().
        assert dialog.replace_field.isHidden()
        assert dialog.windowTitle() == "Find"
        dialog.set_replace_visible(True)
        assert not dialog.replace_field.isHidden()
        assert dialog.windowTitle() == "Find and Replace"

    def test_set_target_resets_status_label(self, _qapp):
        from PySide6.QtWidgets import QPlainTextEdit
        dialog, edit = self._dialog_with_text(_qapp, "abc")
        dialog.find_field.setText("zzz")
        dialog._search()
        assert dialog.status_label.text() != ""
        new_edit = QPlainTextEdit()
        new_edit.setPlainText("abc")
        dialog.set_target(new_edit)
        assert dialog.status_label.text() == ""


# ---------------------------------------------------------------------------
# IDE-level dispatch
# ---------------------------------------------------------------------------

def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


class TestFindTargetTextEdit:
    def test_returns_code_edit_of_active_script_editor(self):
        ide = _ide_cls()
        fake_code_edit = object()
        fake_editor = SimpleNamespace(code_edit=fake_code_edit)
        stub = SimpleNamespace(_active_editor=lambda: fake_editor)
        assert ide._find_target_text_edit(stub) is fake_code_edit

    def test_returns_none_when_active_editor_has_no_code_edit(self):
        ide = _ide_cls()
        stub = SimpleNamespace(_active_editor=lambda: SimpleNamespace())
        assert ide._find_target_text_edit(stub) is None

    def test_returns_none_when_no_active_editor(self):
        ide = _ide_cls()
        stub = SimpleNamespace(_active_editor=lambda: None)
        assert ide._find_target_text_edit(stub) is None


class TestShowFindDialog:
    def test_no_target_shows_status_message_and_no_dialog(self):
        ide = _ide_cls()
        status_bar = MagicMock()
        stub = SimpleNamespace(
            _find_target_text_edit=lambda: None,
            status_bar=status_bar,
            tr=_identity_tr,
        )
        ide._show_find_dialog(stub, show_replace=False)
        status_bar.showMessage.assert_called_once()
        assert not hasattr(stub, "_find_dialog")

    def test_binds_target_and_shows_dialog(self, _qapp):
        ide = _ide_cls()
        fake_code_edit = object()
        mock_dialog = MagicMock()
        stub = SimpleNamespace(
            _find_target_text_edit=lambda: fake_code_edit,
            tr=_identity_tr,
        )
        with patch('dialogs.find_replace_dialog.FindReplaceDialog', return_value=mock_dialog):
            ide._show_find_dialog(stub, show_replace=True)
        assert stub._find_dialog is mock_dialog
        mock_dialog.set_target.assert_called_once_with(fake_code_edit)
        mock_dialog.set_replace_visible.assert_called_once_with(True)
        mock_dialog.show.assert_called_once()

    def test_reuses_existing_dialog_instance_on_second_call(self, _qapp):
        ide = _ide_cls()
        mock_dialog = MagicMock()
        stub = SimpleNamespace(
            _find_target_text_edit=lambda: object(),
            tr=_identity_tr,
            _find_dialog=mock_dialog,
        )
        ide._show_find_dialog(stub, show_replace=False)
        # No new FindReplaceDialog constructed; the existing one is reused
        # (and rebound) — this is what lets repeated Ctrl+F stay on one
        # window instead of piling up dialogs.
        assert stub._find_dialog is mock_dialog
        mock_dialog.set_target.assert_called_once()


class TestFindAndFindReplaceEntryPoints:
    def test_find_calls_show_find_dialog_with_replace_false(self):
        ide = _ide_cls()
        calls = []
        stub = SimpleNamespace(_show_find_dialog=lambda show_replace: calls.append(show_replace))
        ide.find(stub)
        assert calls == [False]

    def test_find_replace_calls_show_find_dialog_with_replace_true(self):
        ide = _ide_cls()
        calls = []
        stub = SimpleNamespace(_show_find_dialog=lambda show_replace: calls.append(show_replace))
        ide.find_replace(stub)
        assert calls == [True]
