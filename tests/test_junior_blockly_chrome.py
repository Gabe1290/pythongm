"""docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 4: the junior edition loads the
Blockly page with ?junior=1, which unregisters the advanced right-click
entries. (Verified once in a real QtWebEngine page: the normal page has 12
registered entries, junior=1 leaves undo/redo/cleanup/duplicate/delete.)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from config.editions import EDITIONS

HTML = Path(__file__).parent.parent / "editors/object_editor/blockly/blockly_workspace.html"


@pytest.fixture
def _edition(monkeypatch):
    from utils.config import Config

    def pick(key):
        monkeypatch.setattr(Config, "get",
                            classmethod(lambda cls, k, d=None: key if k == "edition" else d))
    return pick


def test_only_junior_simplifies_blockly_chrome():
    assert EDITIONS["junior"]["simplify_blockly_chrome"] is True
    for key in ("beginner", "advanced", "development"):
        assert not EDITIONS[key].get("simplify_blockly_chrome")


def test_query_has_junior_flag_only_for_junior(_edition):
    pytest.importorskip("PySide6")
    from editors.object_editor.blockly_widget import blockly_url_query
    _edition("junior")
    assert blockly_url_query("fr") == "lang=fr&junior=1"
    _edition("beginner")
    assert blockly_url_query("fr") == "lang=fr"


def test_page_unregisters_the_advanced_entries_only_when_flagged():
    src = HTML.read_text(encoding="utf-8")
    assert "get('junior') === '1'" in src
    for entry in ("blockCollapseExpand", "blockDisable", "blockInline",
                  "blockComment", "workspaceDelete"):
        assert f"'{entry}'" in src
    for kept in ("blockDuplicate", "blockDelete", "undoWorkspace", "cleanWorkspace"):
        assert f"'{kept}'" not in src
