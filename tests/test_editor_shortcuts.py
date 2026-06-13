"""Regression tests for editor keyboard shortcuts (audit M15).

docs/FULL_AUDIT_2026-06-11.md: BaseEditor registered Ctrl+S twice
(save_action.setShortcut + a QShortcut) plus the IDE menubar's Ctrl+S, and
an F5 QShortcut colliding with the IDE's Test Game F5 — all window-context
in the same window. Qt resolved the duplicates as an 'Ambiguous shortcut
overload' and fired NEITHER handler, so Ctrl+S and F5 were dead whenever a
BaseEditor-derived tab was current. The editor-level Ctrl+S/F5 are now
gone (the IDE menu owns them); Ctrl+W stays (editor-specific, no collision).
"""

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _base_editor(qapp):
    from editors.base_editor import BaseEditor
    return BaseEditor()


class TestNoAmbiguousShortcuts:
    def test_no_editor_level_ctrl_s(self, qapp):
        from PySide6.QtGui import QShortcut, QKeySequence
        ed = _base_editor(qapp)
        seqs = [s.key() for s in ed.findChildren(QShortcut)]
        assert QKeySequence(QKeySequence.Save) not in seqs

    def test_no_editor_level_f5(self, qapp):
        from PySide6.QtGui import QShortcut, QKeySequence
        ed = _base_editor(qapp)
        seqs = [s.key() for s in ed.findChildren(QShortcut)]
        assert QKeySequence("F5") not in seqs

    def test_save_action_has_no_shortcut(self, qapp):
        ed = _base_editor(qapp)
        assert ed.save_action.shortcut().isEmpty()

    def test_ctrl_w_still_registered(self, qapp):
        from PySide6.QtGui import QShortcut, QKeySequence
        ed = _base_editor(qapp)
        seqs = [s.key() for s in ed.findChildren(QShortcut)]
        assert QKeySequence("Ctrl+W") in seqs

    def test_save_button_still_callable(self, qapp):
        # Removing the shortcut must not remove the toolbar Save action.
        ed = _base_editor(qapp)
        assert ed.save_action is not None
        assert ed.save_action.text()  # has a label
