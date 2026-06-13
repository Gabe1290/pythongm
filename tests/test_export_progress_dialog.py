"""Regression tests for the export progress dialog (audit M9/M10).

docs/FULL_AUDIT_2026-06-11.md: _run_export_with_progress built a plain
modal QDialog and ran `exec(); export_thread.wait()`. Esc or the window
close button (QDialog's default reject) returned from exec() while the
export thread was still building, and wait() then blocked the GUI thread
with no event loop — freezing the whole IDE for the multi-minute
PyInstaller/buildozer run.

The dialog is now a _ExportProgressDialog that refuses to close (Esc,
window-close, reject) until allow_close is set when the export actually
finishes, so exec() can never return early and the wait() that follows is
instant.
"""

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _dialog_cls():
    from core.ide_window import _ExportProgressDialog
    return _ExportProgressDialog


class TestCloseSuppressedUntilFinished:
    def test_close_vetoed_while_running(self, qapp):
        dlg = _dialog_cls()(None)
        assert dlg.allow_close is False
        # close() returns False when the close event is ignored
        assert dlg.close() is False

    def test_close_allowed_after_finish(self, qapp):
        dlg = _dialog_cls()(None)
        dlg.allow_close = True
        assert dlg.close() is True

    def test_reject_swallowed_while_running(self, qapp):
        dlg = _dialog_cls()(None)
        finished = []
        dlg.finished.connect(lambda code: finished.append(code))
        dlg.reject()  # Esc funnels through reject()
        assert finished == []  # dialog did not finish

    def test_reject_works_after_finish(self, qapp):
        dlg = _dialog_cls()(None)
        finished = []
        dlg.finished.connect(lambda code: finished.append(code))
        dlg.allow_close = True
        dlg.reject()
        assert finished  # finished signal fired


class TestEscapeRoutesToCancel:
    def test_reject_invokes_on_escape(self, qapp):
        calls = []
        dlg = _dialog_cls()(None, on_escape=lambda: calls.append(True))
        dlg.reject()
        assert calls == [True]

    def test_close_invokes_on_escape(self, qapp):
        calls = []
        dlg = _dialog_cls()(None, on_escape=lambda: calls.append(True))
        dlg.close()
        assert calls == [True]

    def test_on_escape_not_called_after_finish(self, qapp):
        calls = []
        dlg = _dialog_cls()(None, on_escape=lambda: calls.append(True))
        dlg.allow_close = True
        dlg.reject()
        assert calls == []  # past finish, Esc no longer routes to cancel
