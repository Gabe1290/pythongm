"""H6, docs/FULL_AUDIT_2026-09-07.md: the Tools/menu "Create <Asset>" flow
(core/ide/_assets.py's create_asset, backed by a QInputDialog.getText) never
validated the typed name -- unlike the asset tree's own create/rename
dialogs (widgets/asset_tree/asset_dialogs.py), which both call
validate_asset_name. A name containing a path separator, "..", a
Windows-reserved device name, or a trailing dot either silently fails to
write its side file (core/project_manager.py's _safe_asset_path skips it
with a warning) or breaks open() outright on Windows, which can trip the
save's cross-file rollback and lose the whole save.

Uses a minimal AssetsMixin test double rather than a real PyGameMakerIDE
window: constructing the full IDE window and tearing it down with
deleteLater() (the pattern tests/test_audit_editor_key_collision.py uses
for other _assets.py coverage) leaves a widget that can still receive real
Qt events later in the same process -- confirmed pre-existing and
independent of this fix by reproducing the same crash pairing that file
with tests/test_extension_action_i18n.py (which changes the application
language mid-run). create_asset only needs .tr() and
.current_project_path from its host, and every Qt call this test exercises
(QInputDialog.getText, QMessageBox.warning) is monkeypatched out, so no
real widget needs to exist at all -- avoiding the whole class of fragility
rather than working around it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


class _FakeIDE:
    """The minimal surface core.ide._assets.AssetsMixin.create_asset
    actually reads: .tr() (Qt's no-op passthrough when nothing is
    translated) and .current_project_path."""

    def __init__(self):
        self.current_project_path = "/fake/project"

    def tr(self, text):
        return text


def _host():
    from core.ide._assets import AssetsMixin

    class Host(AssetsMixin, _FakeIDE):
        pass

    return Host()


def _typed(monkeypatch, name):
    """Make QInputDialog.getText return (name, True) without a real dialog."""
    import core.ide._assets as assets_mod
    monkeypatch.setattr(
        assets_mod.QInputDialog, "getText",
        staticmethod(lambda *a, **k: (name, True)))


def _warned_titles(monkeypatch):
    """Capture QMessageBox.warning calls instead of blocking on a real one."""
    import core.ide._assets as assets_mod
    calls = []
    monkeypatch.setattr(
        assets_mod.QMessageBox, "warning",
        staticmethod(lambda *a, **k: calls.append(a[1] if len(a) > 1 else None)))
    return calls


@pytest.mark.parametrize("bad_name", [
    "obj/foo",           # path separator
    "obj\\foo",          # path separator (Windows)
    "..",                # traversal
    "CON",               # Windows-reserved device name
    "trailing.",         # trailing dot (illegal on Windows)
    # Not "trailing " (trailing space): validate_asset_name has a
    # pre-existing, separate bug where it strips the name before checking
    # for leading/trailing whitespace, making that check dead code. Out of
    # scope for H6 (which is only "this call site skips validation
    # entirely") -- this test asserts against the validator's real current
    # behaviour, not an idealized one.
])
def test_invalid_name_is_rejected_before_creating_the_asset(monkeypatch, bad_name):
    host = _host()
    _typed(monkeypatch, bad_name)
    warnings = _warned_titles(monkeypatch)

    created = []
    monkeypatch.setattr(host, "create_asset_with_data",
                         lambda asset_type, name: created.append((asset_type, name)))

    host.create_asset("objects")

    assert not created, "an invalid name must never reach create_asset_with_data"
    assert warnings, "the user must be told the name was rejected"


def test_valid_name_still_creates_the_asset(monkeypatch):
    host = _host()
    _typed(monkeypatch, "obj_valid_name")
    warnings = _warned_titles(monkeypatch)

    created = []
    monkeypatch.setattr(host, "create_asset_with_data",
                         lambda asset_type, name: created.append((asset_type, name)))

    host.create_asset("objects")

    assert created == [("objects", "obj_valid_name")]
    assert not warnings
