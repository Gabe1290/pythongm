"""IDE-chrome extension points (core/ide_extension_points) —
docs/THYMIO_EXTENSION_PLAN.md Stage 0.5. Proven with DUMMY contributions
against the real PyGameMakerIDE constructed offscreen (no pytest-qt),
matching tests/test_asset_type_registry.py's pattern.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def clean_points():
    from core import ide_extension_points as pts
    saved = (pts.get_menu_contributions(), pts.get_toolbar_contributions())
    pts.clear_ide_contributions()
    yield pts
    pts.clear_ide_contributions()
    for key, build in saved[0]:
        pts.register_menu_contribution(key, build)
    for build in saved[1]:
        pts.register_toolbar_contribution(build)


def _menu_titles(menu):
    return [a.text() for a in menu.actions()]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_registry_validates_and_is_idempotent(clean_points):
    pts = clean_points

    def b(ide, menu):
        pass

    pts.register_menu_contribution("tools", b)
    pts.register_menu_contribution("tools", b)          # loader may re-run
    pts.register_menu_contribution("bogus", b)          # unknown menu
    pts.register_menu_contribution("file", "nope")      # not callable
    pts.register_toolbar_contribution(b)
    pts.register_toolbar_contribution(b)
    pts.register_toolbar_contribution(42)
    assert pts.get_menu_contributions() == [("tools", b)]
    assert pts.get_toolbar_contributions() == [b]


def test_loader_registers_plugin_ide_contributions(clean_points):
    from types import SimpleNamespace
    from events.plugin_loader import PluginLoader

    def bm(ide, menu):
        pass

    def bt(ide, toolbar):
        pass

    module = SimpleNamespace(PLUGIN_IDE_MENUS=[("tools", bm)], PLUGIN_IDE_TOOLBAR=[bt])
    assert PluginLoader._load_ide_contributions(object.__new__(PluginLoader), module) == 2
    assert ("tools", bm) in clean_points.get_menu_contributions()
    assert bt in clean_points.get_toolbar_contributions()
    # A module with neither attribute is fine.
    assert PluginLoader._load_ide_contributions(object.__new__(PluginLoader), SimpleNamespace()) == 0


def test_apply_skips_missing_menu_and_survives_a_raise(clean_points):
    pts = clean_points
    calls = []
    pts.register_menu_contribution("help", lambda ide, m: 1 / 0)
    pts.register_menu_contribution("tools", lambda ide, m: calls.append(m))
    pts.register_menu_contribution("file", lambda ide, m: calls.append(m))
    pts.apply_menu_contributions(object(), {"tools": "T", "help": "H"})   # no file
    assert calls == ["T"]

    pts.register_toolbar_contribution(lambda ide, tb: 1 / 0)
    pts.register_toolbar_contribution(lambda ide, tb: calls.append(tb))
    pts.apply_toolbar_contributions(object(), "TB")
    assert calls == ["T", "TB"]


# ---------------------------------------------------------------------------
# The real IDE window honours contributions
# ---------------------------------------------------------------------------

def test_ide_builds_contributed_menu_and_toolbar_entries(_qapp, clean_points):
    pts = clean_points
    seen = {}

    def build_tools(ide, menu):
        seen["tools_before"] = _menu_titles(menu)
        sub = menu.addMenu("Dummy Feature")
        sub.addAction(ide.create_action("Dummy Action...", None, lambda: None))

    def build_file(ide, menu):
        menu.addAction(ide.create_action("Export Dummy...", None, lambda: None))

    def build_toolbar(ide, toolbar):
        toolbar.addAction(ide.create_action("Dummy Tool", None, lambda: None))

    pts.register_menu_contribution("tools", build_tools)
    pts.register_menu_contribution("file", build_file)
    pts.register_menu_contribution("help", lambda ide, m: 1 / 0)   # must not break startup
    pts.register_toolbar_contribution(build_toolbar)

    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    try:
        menus = ide._extension_menus
        assert set(menus) == {"file", "edit", "assets", "build", "tools", "help"}
        # Appended after the built-in entries: the Tools menu already had its
        # own actions when the builder ran, and the dummy submenu is last.
        assert seen["tools_before"], "builder ran before Tools was populated"
        assert _menu_titles(menus["tools"])[-1] == "Dummy Feature"
        assert _menu_titles(menus["file"])[-1] == "Export Dummy..."
        from PySide6.QtWidgets import QToolBar
        toolbar = ide.findChild(QToolBar, "MainToolbar")
        assert "Dummy Tool" in [a.text() for a in toolbar.actions()]
    finally:
        ide.deleteLater()


# ---------------------------------------------------------------------------
# Asset-tree categories (0.5b)
# ---------------------------------------------------------------------------

def _arena_category(opened):
    from core.ide_extension_points import AssetTreeCategory
    return AssetTreeCategory(
        plural="arenas", singular="arena", label="Arenas", icon="🏟️",
        open_editor=lambda ide, name, data: opened.append((name, data)),
        new_asset_template=lambda name: {"name": name, "asset_type": "arena",
                                         "imported": True, "size": [1, 2]},
    )


def test_category_registry_feeds_asset_type_registry(clean_points):
    from widgets.asset_tree.asset_utils import ASSET_TYPE_REGISTRY
    opened = []
    spec = _arena_category(opened)
    clean_points.register_asset_tree_category(spec)
    clean_points.register_asset_tree_category(spec)             # idempotent
    clean_points.register_asset_tree_category("nope")           # invalid
    assert clean_points.get_asset_tree_categories() == [spec]
    assert ASSET_TYPE_REGISTRY["arenas"]["singular"] == "arena"
    assert ASSET_TYPE_REGISTRY["arenas"]["open_editor"] is spec.open_editor
    clean_points.clear_asset_tree_categories()
    assert "arenas" not in ASSET_TYPE_REGISTRY
    assert "rooms" in ASSET_TYPE_REGISTRY                       # core untouched


def test_loader_registers_asset_tree_categories(clean_points):
    from types import SimpleNamespace
    from events.plugin_loader import PluginLoader
    spec = _arena_category([])
    module = SimpleNamespace(PLUGIN_ASSET_TREE_CATEGORIES=[spec])
    assert PluginLoader._load_ide_contributions(object.__new__(PluginLoader), module) == 1
    assert spec in clean_points.get_asset_tree_categories()


def test_asset_tree_shows_category_after_rooms_with_icons(_qapp, clean_points):
    from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
    from widgets.asset_tree.asset_tree_item import AssetTreeItem
    from widgets.asset_tree.asset_utils import get_asset_icon_emoji
    clean_points.register_asset_tree_category(_arena_category([]))
    tree = AssetTreeWidget()
    cats = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
    types = [c.asset_type for c in cats if isinstance(c, AssetTreeItem) and c.is_category]
    assert types.index("arenas") == types.index("rooms") + 1
    arena_cat = next(c for c in cats if getattr(c, "asset_type", "") == "arenas")
    assert arena_cat.text(0) == "🏟️ Arenas"
    tree.add_asset("arenas", "a1", {"imported": True})
    assert arena_cat.child(0).text(0) == "🏟️ a1"
    assert get_asset_icon_emoji("arenas") == "🏟️"
    assert "arenas" in tree._non_importable_categories()


def test_ide_dispatches_and_creates_registered_category(_qapp, clean_points):
    opened = []
    clean_points.register_asset_tree_category(_arena_category(opened))
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()             # _verify_asset_editor_registry must pass
    try:
        ide.on_asset_double_clicked({"asset_type": "arenas", "name": "a1", "data": {"k": 1}})
        assert opened == [("a1", {"k": 1})]
        assert ide._canonical_category("arena") == "arenas"
        ide.current_project_data = {"assets": {}}
        ide.create_asset_with_data("arenas", "a2")
        assert ide.current_project_data["assets"]["arenas"]["a2"]["size"] == [1, 2]
    finally:
        ide.deleteLater()


# ---------------------------------------------------------------------------
# Object-editor panels (0.5c)
# ---------------------------------------------------------------------------

def _dummy_panel_class():
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import QWidget

    class DummyPanel(QWidget):
        events_modified = Signal()
        event_selected = Signal(str)
        instances = []

        def __init__(self):
            super().__init__()
            self.loaded = []
            self.own = {}
            DummyPanel.instances.append(self)

        def load_events_data(self, events):
            self.loaded.append(dict(events))

        def get_events_data(self):
            return dict(self.own)

    return DummyPanel


def _panel_spec(cls, visible=True):
    from core.ide_extension_points import ObjectEditorPanel
    return ObjectEditorPanel(
        key="dummy", label="Dummy Panel", factory=cls,
        owned_events=lambda: ["dummy_evt", "dummy_evt2"],
        is_visible=lambda: visible,
        event_label=lambda name: f"label:{name}",
    )


def test_panel_registry_validates(clean_points):
    from core.ide_extension_points import ObjectEditorPanel
    cls = _dummy_panel_class()
    spec = _panel_spec(cls)
    clean_points.register_object_editor_panel(spec)
    clean_points.register_object_editor_panel(spec)
    clean_points.register_object_editor_panel(
        ObjectEditorPanel("bad", "x", factory="nope", owned_events=list))
    assert clean_points.get_object_editor_panels() == [spec]

    from types import SimpleNamespace
    from events.plugin_loader import PluginLoader
    clean_points.clear_object_editor_panels()
    module = SimpleNamespace(PLUGIN_OBJECT_EDITOR_PANELS=[spec])
    assert PluginLoader._load_ide_contributions(object.__new__(PluginLoader), module) == 1
    assert clean_points.get_object_editor_panels() == [spec]


def test_object_editor_hosts_registered_panel(_qapp, clean_points):
    cls = _dummy_panel_class()
    cls.instances.clear()
    clean_points.register_object_editor_panel(_panel_spec(cls))
    from editors.object_editor.object_editor_main import ObjectEditor
    editor = ObjectEditor()
    try:
        tabs = editor.events_tab_widget
        labels = [tabs.tabText(i) for i in range(tabs.count())]
        assert "Dummy Panel" in labels
        panel = cls.instances[-1]

        # load_data syncs the whole events dict into the panel.
        act = {"action": "set_variable", "parameters": {"name": "x", "value": "1"}}
        editor.load_data({"name": "obj", "events": {
            "create": {"actions": []}, "dummy_evt": {"actions": [act]}}})
        assert panel.loaded[-1] == {"create": {"actions": []}, "dummy_evt": {"actions": [act]}}

        # The panel edits its own family: one owned event dropped, one added;
        # the merge keeps "create" untouched.
        saved = []
        editor.events_panel.events_modified.connect(lambda: saved.append(True))
        panel.own = {"dummy_evt2": {"actions": [act]}}
        panel.events_modified.emit()
        current = editor.events_panel.current_events_data
        assert "dummy_evt" not in current
        assert current["dummy_evt2"] == {"actions": [act]}
        assert current["create"] == {"actions": []}
        assert saved == [True]

        # Selection feeds the info label (when the editor has one) through
        # event_label — same hasattr guard the Thymio tab uses.
        from PySide6.QtWidgets import QLabel
        editor.event_info_label = QLabel()
        panel.event_selected.emit("dummy_evt2")
        assert editor.event_info_label.text() == "label:dummy_evt2"

        # Visibility toggling removes/re-adds the tab; switch_to makes it current.
        editor.set_extension_panel_visible("dummy", False)
        assert "Dummy Panel" not in [tabs.tabText(i) for i in range(tabs.count())]
        editor.switch_to_extension_panel("dummy")
        assert tabs.tabText(tabs.currentIndex()) == "Dummy Panel"
        assert panel.loaded[-1] == current
    finally:
        editor.deleteLater()


def test_hidden_panel_is_built_but_not_shown(_qapp, clean_points):
    cls = _dummy_panel_class()
    clean_points.register_object_editor_panel(_panel_spec(cls, visible=False))
    from editors.object_editor.object_editor_main import ObjectEditor
    editor = ObjectEditor()
    try:
        tabs = editor.events_tab_widget
        assert "Dummy Panel" not in [tabs.tabText(i) for i in range(tabs.count())]
        assert "dummy" in editor._extension_panels
    finally:
        editor.deleteLater()


def test_ide_without_contributions_has_no_extra_entries(_qapp, clean_points):
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    try:
        assert "Dummy Feature" not in _menu_titles(ide._extension_menus["tools"])
    finally:
        ide.deleteLater()
