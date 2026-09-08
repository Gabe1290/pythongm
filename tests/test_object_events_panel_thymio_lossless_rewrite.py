"""L14, docs/FULL_AUDIT_2026-09-07.md: _parse_execute_code_actions rewrites
saved data on load.

ObjectEventsPanel.load_events_data calls _parse_execute_code_actions the
moment an object is opened -- before any user action. It checked
`'thymio.' in code` as a raw substring against the WHOLE code text
(comments included) to decide whether to try converting an execute_code
action into real thymio_* actions. Inside the parser,
PythonToActionsParser also sets `self._code_uses_thymio = 'thymio' in
code` from the same raw text, which gates a heuristic (audit M18) that
reclassifies a plain bare-name assignment ("score = 5") as
thymio_set_variable. So an execute_code action whose code merely
MENTIONS "thymio." in a comment -- with an otherwise completely
ordinary assignment -- got that assignment silently reinterpreted as a
Thymio action and rewritten into the saved event data, just from
opening the object editor.

Fix: only accept the rewrite if it's lossless -- regenerate code from
the parsed actions and re-parse that fresh; if the fresh parse (which
only sees whatever "thymio" text genuinely survives regeneration, not
the original comment) disagrees with the first parse, the rewrite
isn't safe and the original execute_code action is kept untouched.

Verified empirically before writing these assertions (not guessed):
`score = 5` under a "# thymio.move_forward(50)" comment really does get
misclassified pre-fix, and the round-trip check really does distinguish
it from a genuine `thymio.move_forward(50)` call.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _panel(_qapp):
    from editors.object_editor.events._panel import ObjectEventsPanel
    return ObjectEventsPanel()


def _with_code(panel, code):
    panel.current_events_data = {
        "step": {"actions": [
            {"action": "execute_code", "parameters": {"code": code}}
        ]}
    }
    panel._parse_execute_code_actions()
    return panel.current_events_data["step"]["actions"]


def test_comment_only_thymio_mention_does_not_rewrite_an_ordinary_assignment(_qapp):
    """The exact bug: a bare-name assignment under a comment that merely
    mentions "thymio." must NOT be silently reclassified as a Thymio
    action -- the original execute_code action must survive unchanged."""
    panel = _panel(_qapp)
    code = "# thymio.move_forward(50) -- maybe use this later\nscore = 5"

    actions = _with_code(panel, code)

    assert len(actions) == 1
    assert actions[0]["action"] == "execute_code"
    assert actions[0]["parameters"]["code"] == code


def test_a_genuine_thymio_call_is_still_converted(_qapp):
    """The fix must not throw out the real feature -- code that actually
    calls the Thymio API still gets converted to a real thymio_* action."""
    panel = _panel(_qapp)
    code = "thymio.move_forward(50)"

    actions = _with_code(panel, code)

    assert len(actions) == 1
    assert actions[0]["action"] == "thymio_move_forward"
    assert actions[0]["parameters"]["speed"] == 50


def test_non_thymio_code_is_left_alone(_qapp):
    panel = _panel(_qapp)
    code = "score = self.score + 1"

    actions = _with_code(panel, code)

    assert len(actions) == 1
    assert actions[0]["action"] == "execute_code"
    assert actions[0]["parameters"]["code"] == code
