"""Regression tests for PyGameMakerIDE._reraise_blocked_modal_child
(core/ide_window.py).

A student clicking the main IDE window can bring it to the front even
while one of the IDE's own application-modal dialogs is open (the color
picker -- editors/sprite_editor/color_palette.py and others all use
QColorDialog.getColor -- but the fix is generic to any application-modal
QDialog). Confirmed on GNOME/Mutter under Wayland, the school lab's actual
environment: the window manager's raise-on-click decision doesn't consult
Qt's own modality, so the main window activates while the dialog it should
be blocked by ends up hidden behind it, with no way to alt-tab back to it
(same application). changeEvent's ActivationChange handler calls
_reraise_blocked_modal_child() to put the dialog back in front the moment
the main window notices it became active.

Only _reraise_blocked_modal_child() itself is unit-tested here (unbound on
a lightweight stub, this repo's usual pattern for PyGameMakerIDE methods --
avoids standing up the full Qt IDE window). The two-line changeEvent
dispatch that calls it isn't separately tested: exercising it would require
either a real PyGameMakerIDE instance (heavy) or calling changeEvent
unbound on a non-PyGameMakerIDE stub, which crashes at its
super().changeEvent(event) call (Python's zero-arg super() requires self
to be a real instance of the class); the dispatch itself is two lines of
low-risk glue reviewed alongside this test, not separately covered.
"""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


class TestReraiseBlockedModalChild:

    def test_reraises_and_activates_a_blocked_modal_dialog(self):
        ide = _ide_cls()
        stub = SimpleNamespace()
        modal = MagicMock()

        with patch('PySide6.QtWidgets.QApplication.activeModalWidget', return_value=modal):
            ide._reraise_blocked_modal_child(stub)

        modal.raise_.assert_called_once()
        modal.activateWindow.assert_called_once()

    def test_does_nothing_when_no_modal_dialog_is_open(self):
        ide = _ide_cls()
        stub = SimpleNamespace()

        with patch('PySide6.QtWidgets.QApplication.activeModalWidget', return_value=None):
            ide._reraise_blocked_modal_child(stub)  # must not raise

    def test_does_not_try_to_reraise_the_main_window_itself(self):
        """activeModalWidget() returning the main window itself (not a
        child dialog) must be a no-op -- there is nothing to rescue."""
        ide = _ide_cls()
        stub = SimpleNamespace(raise_=MagicMock(), activateWindow=MagicMock())

        with patch('PySide6.QtWidgets.QApplication.activeModalWidget', return_value=stub):
            ide._reraise_blocked_modal_child(stub)

        stub.raise_.assert_not_called()
        stub.activateWindow.assert_not_called()
