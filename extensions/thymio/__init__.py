#!/usr/bin/env python3
"""Thymio educational robot, packaged as a folder extension.

Being moved out of core one stage at a time — docs/THYMIO_EXTENSION_PLAN.md
is the map. What lives here so far:

* ``actions.py`` — ``THYMIO_ACTIONS`` (the GM80-dialog ``ActionDefinition``
  schemas the Thymio panels and the Aseba exporter read) and ``THYMIO_TAB``,
  the "Thymio" tab of the GM80 action dialog, registered below (Stage A1).
* ``handlers.py`` — the 28 runtime handlers. ``PluginExecutor`` is what the
  loader registers in the game process; ``register_thymio_actions`` is the
  same set for the playground runner, which has no plugin loader (A2).
* ``events.py`` — the 14 robot events, ``PLUGIN_EVENTS`` (A3).
* ``simulator.py`` — ``ThymioSimulator``: differential drive, proximity/
  ground sensors, LEDs, tones, timers (A4).
* ``state.py`` — the robot's per-instance state under
  ``instance.extension_state["thymio"]``; ``on_instance_created`` below
  attaches a simulator to ``thymio*`` instances as a room builds (B3).
* ``runtime.py`` — the per-frame simulator step + sensor events, run
  through the ``after_collision`` frame-update hook (A5).
* ``renderer.py`` — ``ThymioRenderer`` (robot body, LEDs, sensor rays,
  button hit-testing); ``draw_robot`` below is the instance overlay that
  draws every robot over the room (B1).
* ``input.py`` — keyboard/mouse control of the robot's buttons, through
  the input hook (B2).
* ``editor/`` — the arena-authoring editor (C1).
* ``playground_runner.py`` — ``PlaygroundRunnerWindow``: a standalone
  simulation window that embeds pygame in Qt and runs linked objects'
  code against a playground arena, independent of a full game project (C2).
* ``playground_window.py`` — ``ThymioPlaygroundWindow``: the live test/
  config window for a single robot (C3b). ``PygameWidget``, the generic
  pygame-in-Qt widget it and ``playground_runner.py`` both use, stayed in
  core (``widgets/pygame_widget.py``, C3a) since Block World reuses it too.
* ``diagram_widget.py`` — ``ThymioDiagramWidget``: the interactive robot
  diagram the config/event/action dialogs and the object-editor panel
  embed (C4).
* ``dialogs/`` — the config/event/action selector dialogs (C6).
  ``dialogs/_block_config_dialog_base.py`` (core) stays put — it's the
  genuinely shared base ``BlocklyConfigDialog`` also uses.
* ``export/`` — Aseba (.aesl) export, Open Roberta Lab XML import/export
  (D1/D2), plus ``export_aseba_code(ide)``/``import_roberta_xml(ide)``,
  the File-menu action handlers ``PLUGIN_IDE_MENUS`` below wires in (D3).
* ``object_editor_panel.py`` — ``ThymioEventsPanel``, the object editor's
  "🤖 Thymio" tab (E). ``PLUGIN_OBJECT_EDITOR_PANELS`` below is the whole
  Thymio-specific side of it now — construction, which events it owns,
  its ``show_thymio_tab`` config gate, and its event-selection label; the
  tab widget, merge-back and sync are the fully generic
  ``ObjectEditorPanel`` mechanism (core/ide_extension_points, Stage 0.5c).
* ``blockly_categories.py`` — the 8 Thymio Blockly toolbox categories, the
  "thymio" preset and its 7-language category-name translations (F).
  ``THYMIO_CATEGORIES`` (just the 8 names, for exclusion filtering) stays
  in ``dialogs/_block_config_dialog_base.py`` — core's own
  ``BlocklyConfigDialog`` needs it too.
* ``tools_menu.py`` — ``configure_thymio``/``toggle_thymio_tab``/
  ``show_thymio_playground``/``show_thymio_event_selector``/
  ``show_thymio_action_selector``, the Tools-menu + toolbar action
  handlers (G). ``_build_tools_menu``/``_build_toolbar`` below wire them
  in via ``PLUGIN_IDE_MENUS``/``PLUGIN_IDE_TOOLBAR`` — still gated by the
  ``show_thymio_tab`` config flag (default ``False``), same as the
  object-editor tab, so core carries the UI-hiding decision as data (one
  config default), not as commented-out code naming Thymio.

"Playgrounds" (the robot arena asset type) is registered below through the
Stage-0.4/0.5 seams — ``PLUGIN_ASSET_TYPES`` for its on-disk side-file
shape, ``PLUGIN_ASSET_TREE_CATEGORIES`` for its row/icon/opener/template in
the IDE (C5).

Stages A-G are closed. **Stage G5b (in progress)** is moving the remaining
Thymio-aware code out of the object editor's *Standard* panel — reachable
with the dedicated Thymio tab off, on any project with a `thymio*` object.
G5b.1 is done: ``_project_has_playgrounds``/``_register_toolbox_visibility_filter``
below hide the Thymio Blockly categories/blocks from the toolbox when the
project has no playground, through the generic ``ToolboxVisibilityFilter``
seam (``core/ide_extension_points``) — ``editors/object_editor/
blockly_widget.py`` no longer names Thymio at all. G5b.2-4 (the Standard
panel's add-event/add-action menu contributions and its execute_code
Thymio-parsing pass) are not yet moved; see
``docs/THYMIO_EXTENSION_PLAN.md``'s Stage G5b section for the design.

Whether Thymio ships *visible* by default remains a separate product call
(unchanged since 1.0): flip ``show_thymio_tab``'s default in
``extensions/thymio/__init__.py``'s ``_thymio_tab_visible()`` to bring the
tab, the Tools-menu entries and the toolbar button back together.
"""

PLUGIN_NAME = "Thymio Robot"

from core.logger import get_logger
from actions.core import register_action_tabs
from .state import attach_simulator, simulator_of, is_robot

logger = get_logger(__name__)
from .actions import THYMIO_ACTIONS, THYMIO_TAB
from .handlers import PluginExecutor, register_thymio_actions
from .events import THYMIO_EVENT_TYPES

register_action_tabs(THYMIO_TAB)

# The 14 robot events (buttons, sensors, timers, sound, IR). Each has a
# Blockly block of the same name, so it is gated by the Blockly config like
# a core event (A3).
PLUGIN_EVENTS = THYMIO_EVENT_TYPES
PLUGIN_EVENT_BLOCKLY_MAP = {name: name for name in THYMIO_EVENT_TYPES}


def _frame_update_robots(game_runner):
    # Imported lazily: pygame stays out of the IDE's schema-only load.
    from .runtime import update_thymio_robots
    update_thymio_robots(game_runner)


PLUGIN_FRAME_UPDATES = [(_frame_update_robots, "after_collision")]


def draw_robot(instance, screen):
    """Instance-overlay hook: draw a robot body over its instance (B1)."""
    sim = simulator_of(instance)
    if sim is None:
        return
    from .renderer import shared_renderer
    shared_renderer().render(screen, sim.get_render_data())


PLUGIN_INSTANCE_OVERLAYS = [draw_robot]


def on_instance_created(instance, instance_data, room):
    """Instance-created hook: a ``thymio*``-named object, or one whose room
    entry sets ``is_thymio``, gets a simulator at its start position (B3)."""
    name = instance.object_name or ''
    if name.lower().startswith('thymio') or instance_data.get('is_thymio', False):
        from .simulator import ThymioSimulator
        attach_simulator(instance, ThymioSimulator(x=instance.x, y=instance.y, angle=0))
        logger.debug(f"🤖 Created Thymio robot: {instance.object_name}")


PLUGIN_INSTANCE_CREATED = [on_instance_created]

# Arrow keys / space drive the robot's buttons; a click on a drawn button
# presses it (B2). See input.py.
from .input import INPUT_HANDLERS
PLUGIN_INPUT_HANDLERS = [INPUT_HANDLERS]


# "Playgrounds" — the robot arena asset type (C5). Storage shape (core/
# asset_types) and IDE presentation (core/ide_extension_points) used to be
# a static entry each in core; both are extension-owned now.
from core.asset_types import SideFileAssetType

PLUGIN_ASSET_TYPES = [SideFileAssetType(
    plural="playgrounds",
    singular="playground",
    description="Aseba playground environments",
    file_keys=("arena", "colors", "walls", "robots"),
    strip_keys=("walls", "robots", "colors"),
)]


def _new_playground_data(name: str) -> dict:
    return {
        'name': name,
        'asset_type': 'playground',
        'imported': True,
        'arena': {
            'width': 400,
            'height': 400,
            'color': 'white',
            'ground_texture': '',
        },
        'colors': [
            {'name': 'white', 'r': 1.0, 'g': 1.0, 'b': 1.0},
            {'name': 'wall', 'r': 0.45, 'g': 0.45, 'b': 0.5},
        ],
        'walls': [],
        'robots': [],
    }


def _open_playground_editor(ide, name, data):
    from .editor import open_playground_editor
    open_playground_editor(ide, name, data)


def _register_asset_tree_category():
    from core.ide_extension_points import AssetTreeCategory
    return AssetTreeCategory(
        plural="playgrounds", singular="playground", label="Playgrounds",
        icon="🏟️", open_editor=_open_playground_editor,
        new_asset_template=_new_playground_data,
    )


PLUGIN_ASSET_TREE_CATEGORIES = [_register_asset_tree_category()]


# File-menu entries: Aseba export, Open Roberta import (D3). Appended after
# the built-in File-menu entries (core/ide_extension_points) rather than
# interleaved at their old positions -- the generic menu-contribution
# contract only supports appending (or insertAction with a known sibling,
# which the built-in menu doesn't expose here).
def _build_file_menu(ide, menu):
    from .export import export_aseba_code, import_roberta_xml

    # Attached to ide under their pre-hidden names (bound methods before
    # this stage, plain callables now -- Python doesn't care which for a
    # `self.<name>` / `hasattr` call site). widgets/welcome_tab.py's
    # "Import Open Roberta XML..." dropdown entry (`_on_import_roberta`)
    # and core/ide_window.py's `update_ui_state()` (the export_aseba_action
    # enable/disable check below) both rely on these exact names, unchanged.
    ide.export_aseba_code = lambda: export_aseba_code(ide)
    ide.import_roberta_xml = lambda: import_roberta_xml(ide)

    menu.addSeparator()
    ide.export_aseba_action = ide.create_action(
        ide.tr("Export &Aseba (Thymio) code..."), None, ide.export_aseba_code)
    # Exporting needs an open project (same as export_html5_action/
    # export_zip_action/export_kivy_action, which core enables/disables
    # directly since those actions are core's own); flagged for core's
    # generic update_ui_state() sweep instead of a hardcoded hasattr check
    # naming this action (core/ide_window.py's pygm_requires_project check).
    ide.export_aseba_action.setProperty("pygm_requires_project", True)
    menu.addAction(ide.export_aseba_action)
    import_action = ide.create_action(
        ide.tr("Import Open &Roberta XML..."), None, ide.import_roberta_xml)
    # Imports a new PROJECT (like GameMaker .gmk import), so it must stay
    # usable with no project open -- the generic "Import" substring match
    # in update_ui_state() would otherwise grey it out (core/ide_window.py;
    # same exemption WelcomeTab._dropdown_button uses).
    import_action.setProperty("pygm_always_enabled", True)
    menu.addAction(import_action)


# Tools-menu "Configure Thymio Blocks..." + "Thymio Programming" submenu,
# and the toolbar quick-add button (Stage G). These were core's own
# hardcoded-but-commented-out `# [1.0]` UI (docs/POST_1_0_REFACTOR.md) --
# now built here, still gated by the same show_thymio_tab config flag that
# already gates the object-editor tab, so a default install shows none of
# this, unchanged from before the move. Flipping that one flag brings the
# whole UI (tab + these entries) back together -- see this plan's "Open
# decision" section; that product call is deliberately not made by this
# move.
def _build_tools_menu(ide, menu):
    if not _thymio_tab_visible():
        return
    from PySide6.QtGui import QAction
    from .tools_menu import (
        configure_thymio, toggle_thymio_tab, show_thymio_playground,
        show_thymio_event_selector, show_thymio_action_selector,
    )
    from .export import import_roberta_xml

    configure_action = ide.create_action(
        ide.tr("Configure &Thymio Blocks..."), None, lambda: configure_thymio(ide))
    configure_action.setMenuRole(QAction.NoRole)
    menu.addAction(configure_action)

    menu.addSeparator()
    thymio_menu = menu.addMenu(ide.tr("🤖 &Thymio Programming"))

    ide.show_thymio_tab_action = QAction(ide.tr("Show Thymio Tab in Object Editor"), ide)
    ide.show_thymio_tab_action.setCheckable(True)
    ide.show_thymio_tab_action.setChecked(_thymio_tab_visible())
    ide.show_thymio_tab_action.triggered.connect(lambda: toggle_thymio_tab(ide))
    thymio_menu.addAction(ide.show_thymio_tab_action)
    thymio_menu.addSeparator()

    thymio_menu.addAction(ide.create_action(
        ide.tr("Open &Playground..."), None, lambda: show_thymio_playground(ide)))
    thymio_menu.addSeparator()

    # Target the active object editor, which can't exist without an open
    # project -- flagged for core's generic update_ui_state() enable/disable
    # sweep (core/ide_window.py's pygm_requires_project check).
    ide.thymio_add_event_action = ide.create_action(
        ide.tr("Add &Event..."), None, lambda: show_thymio_event_selector(ide))
    ide.thymio_add_action_action = ide.create_action(
        ide.tr("Add &Action..."), None, lambda: show_thymio_action_selector(ide))
    ide.thymio_add_event_action.setProperty("pygm_requires_project", True)
    ide.thymio_add_action_action.setProperty("pygm_requires_project", True)
    thymio_menu.addAction(ide.thymio_add_event_action)
    thymio_menu.addAction(ide.thymio_add_action_action)
    thymio_menu.addSeparator()

    # A second copy of the File menu's Roberta import, for convenience while
    # already working in this submenu -- imports a new PROJECT, so it must
    # stay usable with no project open, same as the File-menu copy.
    ide.thymio_import_roberta_action = ide.create_action(
        ide.tr("Import Open &Roberta XML..."), None, lambda: import_roberta_xml(ide))
    ide.thymio_import_roberta_action.setProperty("pygm_always_enabled", True)
    thymio_menu.addAction(ide.thymio_import_roberta_action)


def _build_toolbar(ide, toolbar):
    if not _thymio_tab_visible():
        return
    from .tools_menu import show_thymio_event_selector

    toolbar.addSeparator()
    ide.thymio_toolbar_action = ide.create_action(
        ide.tr("Thymio"), None, lambda: show_thymio_event_selector(ide), "SP_DriveNetIcon")
    ide.thymio_toolbar_action.setToolTip(ide.tr("Add Thymio Event"))
    ide.thymio_toolbar_action.setProperty("pygm_requires_project", True)
    toolbar.addAction(ide.thymio_toolbar_action)
    toolbar.addSeparator()


PLUGIN_IDE_MENUS = [("file", _build_file_menu), ("tools", _build_tools_menu)]
PLUGIN_IDE_TOOLBAR = [_build_toolbar]


# The object-editor's Thymio tab (E). The panel widget, its merge-back and
# its event-label sync are all the fully generic ObjectEditorPanel
# mechanism (core/ide_extension_points, Stage 0.5c) now; only the
# Thymio-specific *content* of these three callables lives here.
def _thymio_panel_factory():
    from .object_editor_panel import ThymioEventsPanel
    return ThymioEventsPanel()


def _thymio_owned_events():
    return THYMIO_EVENT_TYPES.keys()


def _thymio_tab_visible():
    from utils.config import Config
    return Config.get('show_thymio_tab', False)


def _thymio_event_label(event_name):
    event_type = THYMIO_EVENT_TYPES.get(event_name)
    if event_type is None:
        return None
    return f"{event_type.icon} {event_type.display_name}"


def _register_object_editor_panel():
    from core.ide_extension_points import ObjectEditorPanel
    return ObjectEditorPanel(
        key="thymio", label="🤖 Thymio", factory=_thymio_panel_factory,
        owned_events=_thymio_owned_events, is_visible=_thymio_tab_visible,
        event_label=_thymio_event_label,
    )


PLUGIN_OBJECT_EDITOR_PANELS = [_register_object_editor_panel()]


def _project_has_playgrounds(widget) -> bool:
    """Walk up the Qt parent chain looking for ``current_project_data`` and
    report whether the project has any playground assets. Shared by the
    toolbox filter below and (from Stage G5b.2/G5b.3 on) the Standard-panel
    add-event/add-action menu contributions -- moved verbatim out of
    ``editors/object_editor/blockly_widget.py`` and
    ``editors/object_editor/events/_panel.py``, which each had their own
    byte-identical copy (docs/THYMIO_EXTENSION_PLAN.md, Stage G5b)."""
    parent = widget.parent()
    while parent:
        if hasattr(parent, 'current_project_data'):
            project_data = parent.current_project_data
            if project_data and 'assets' in project_data:
                playgrounds = project_data['assets'].get('playgrounds', {})
                return bool(playgrounds)
            break
        parent = parent.parent()
    return False


def _register_toolbox_visibility_filter():
    from core.ide_extension_points import ToolboxVisibilityFilter
    return ToolboxVisibilityFilter(
        is_enabled=_project_has_playgrounds,
        owns_block=lambda b: b.startswith("thymio_"),
        owns_category=lambda c: c.startswith("Thymio "),
    )


PLUGIN_TOOLBOX_VISIBILITY_FILTERS = [_register_toolbox_visibility_filter()]


# The Blockly toolbox: 8 categories, the "thymio" preset, category-name
# translations (F). See blockly_categories.py's module docstring for why the
# preset can't be built with BlocklyConfig.enable_category() the way core's
# own presets are.
from .blockly_categories import (
    PLUGIN_BLOCK_CATEGORIES, PLUGIN_BLOCKLY_PRESETS,
    PLUGIN_BLOCK_CATEGORY_TRANSLATIONS,
)
