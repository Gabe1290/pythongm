"""IDE-chrome extension points: what an extension may add to the IDE window.

``runtime/extension_hooks`` is the engine-side contract (rendering, input,
frame updates). This is the IDE-side one — menus, the toolbar — so a feature
like the Thymio robot tooling can put its "Thymio Programming" submenu and
quick-add toolbar button back without ``core/ide/_menu_builder.py`` naming
it (docs/THYMIO_EXTENSION_PLAN.md, Stage 0.5).

Kept separate from ``runtime/extension_hooks`` on purpose: that module is
dependency-free so the game process can import it; this one is only ever
used by the Qt IDE. It still imports no Qt itself — builders receive the
live ``QMenu``/``QToolBar`` and use ``ide.create_action`` like the built-in
menus do.

An extension declares contributions the same declarative way it declares
actions::

    def build_tools_menu(ide, menu):          # menu is the Tools QMenu
        menu.addSeparator()
        sub = menu.addMenu(ide.tr("My Feature"))
        sub.addAction(ide.create_action(ide.tr("Do It..."), None, lambda: ...))

    def build_toolbar(ide, toolbar):
        toolbar.addAction(ide.create_action(ide.tr("Do It"), None, lambda: ...))

    PLUGIN_IDE_MENUS = [("tools", build_tools_menu)]
    PLUGIN_IDE_TOOLBAR = [build_toolbar]

Menu keys are the IDE's top-level menus: ``file``, ``edit``, ``assets``,
``build``, ``tools``, ``help``. Contributions are appended after the built-in
entries of that menu (a builder may ``insertAction`` earlier if it must).
A builder that raises is logged and skipped — a broken extension must not
stop the IDE from starting.
"""
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)

MENU_KEYS = ("file", "edit", "assets", "build", "tools", "help")


# ---------------------------------------------------------------------------
# Asset-tree categories: a new kind of asset the tree shows and can open.
#
# Pairs with core/asset_types (which stores the asset on disk). This is the
# IDE half: the category row in the asset tree (slotted after "Rooms"), its
# icon, how to open one in an editor, and what a freshly created one looks
# like. Registering here also enters the type in ASSET_TYPE_REGISTRY
# (widgets/asset_tree/asset_utils) so double-click dispatch, editor keys
# and the singular/plural vocabulary all know it.
#
#     PLUGIN_ASSET_TREE_CATEGORIES = [AssetTreeCategory(
#         plural="arenas", singular="arena", label="Arenas", icon="🏟️",
#         open_editor=lambda ide, name, data: ...,
#         new_asset_template=lambda name: {...},
#     )]
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AssetTreeCategory:
    plural: str
    singular: str
    label: str
    icon: str
    open_editor: Callable                      # (ide, name, data) -> None
    new_asset_template: Optional[Callable] = None   # (name) -> dict
    importable: bool = False


_asset_tree_categories: Dict[str, AssetTreeCategory] = {}


# ---------------------------------------------------------------------------
# Object-editor panels: an extra tab beside "Standard" in the object editor's
# events column, owning a family of events (a robot's sensor/button events).
#
# The panel widget the factory returns must provide:
#   events_modified  Signal()      emitted after the user edits in the panel
#   event_selected   Signal(str)   emitted with an event name on selection
#   load_events_data(dict)         given the object's whole events dict
#   get_events_data() -> dict      the panel's own events (subset)
# The editor merges get_events_data() back into the object's events and
# drops any event in owned_events() the panel no longer lists.
#
#     PLUGIN_OBJECT_EDITOR_PANELS = [ObjectEditorPanel(
#         key="robot", label="🤖 Robot", factory=RobotEventsPanel,
#         owned_events=lambda: ROBOT_EVENT_TYPES.keys(),
#         is_visible=lambda: Config.get("show_robot_tab", False),
#         event_label=lambda name: ...,   # optional, for the info label
#     )]
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObjectEditorPanel:
    key: str
    label: str
    factory: Callable                       # () -> QWidget
    owned_events: Callable                  # () -> Iterable[str]
    is_visible: Callable = lambda: True     # () -> bool
    event_label: Optional[Callable] = None  # (event_name) -> Optional[str]


_object_editor_panels: Dict[str, ObjectEditorPanel] = {}


def register_object_editor_panel(spec: ObjectEditorPanel) -> None:
    if (not isinstance(spec, ObjectEditorPanel) or not callable(spec.factory)
            or not callable(spec.owned_events) or not callable(spec.is_visible)):
        logger.error(f"Object-editor panel is not a valid ObjectEditorPanel: {spec!r}")
        return
    existing = _object_editor_panels.get(spec.key)
    if existing is not None:
        if existing != spec:
            logger.error(f"Object-editor panel {spec.key!r} already registered; kept first")
        return
    _object_editor_panels[spec.key] = spec
    logger.debug(f"Registered object-editor panel: {spec.key}")


def get_object_editor_panels() -> List[ObjectEditorPanel]:
    return list(_object_editor_panels.values())


def clear_object_editor_panels() -> None:
    _object_editor_panels.clear()


def register_asset_tree_category(spec: AssetTreeCategory) -> None:
    if not isinstance(spec, AssetTreeCategory) or not callable(spec.open_editor):
        logger.error(f"Asset tree category is not a valid AssetTreeCategory: {spec!r}")
        return
    existing = _asset_tree_categories.get(spec.plural)
    if existing is not None:
        if existing != spec:
            logger.error(f"Asset tree category {spec.plural!r} already registered; kept first")
        return
    _asset_tree_categories[spec.plural] = spec
    from widgets.asset_tree.asset_utils import ASSET_TYPE_REGISTRY
    ASSET_TYPE_REGISTRY.setdefault(spec.plural, {
        "singular": spec.singular, "open_editor": spec.open_editor,
    })
    logger.debug(f"Registered asset tree category: {spec.plural}")


def get_asset_tree_categories() -> List[AssetTreeCategory]:
    return list(_asset_tree_categories.values())


def get_asset_tree_category(plural: str) -> Optional[AssetTreeCategory]:
    return _asset_tree_categories.get(plural)


def clear_asset_tree_categories() -> None:
    """Drop every registered category (and its ASSET_TYPE_REGISTRY entry)."""
    from widgets.asset_tree.asset_utils import ASSET_TYPE_REGISTRY
    for plural in _asset_tree_categories:
        entry = ASSET_TYPE_REGISTRY.get(plural)
        if entry is not None and "open_editor" in entry:
            del ASSET_TYPE_REGISTRY[plural]
    _asset_tree_categories.clear()

# Registered (menu_key, build) pairs, in registration order.
_menu_builders: List[Tuple[str, Callable]] = []
# Registered build(ide, toolbar) callables, in registration order.
_toolbar_builders: List[Callable] = []


def register_menu_contribution(menu_key: str, build: Callable) -> None:
    """Register ``build(ide, qmenu)`` to run on the named top-level menu."""
    if menu_key not in MENU_KEYS:
        logger.error(f"Unknown IDE menu {menu_key!r} for {build!r}; valid: {MENU_KEYS}")
        return
    if not callable(build):
        logger.error(f"Menu contribution is not callable: {build!r}")
        return
    entry = (menu_key, build)
    if entry in _menu_builders:
        return                      # idempotent: the loader may re-run
    _menu_builders.append(entry)
    logger.debug(f"Registered menu contribution: {menu_key} <- {getattr(build, '__name__', build)}")


def register_toolbar_contribution(build: Callable) -> None:
    """Register ``build(ide, toolbar)`` to run on the main toolbar."""
    if not callable(build):
        logger.error(f"Toolbar contribution is not callable: {build!r}")
        return
    if build in _toolbar_builders:
        return
    _toolbar_builders.append(build)
    logger.debug(f"Registered toolbar contribution: {getattr(build, '__name__', build)}")


def get_menu_contributions() -> List[Tuple[str, Callable]]:
    return list(_menu_builders)


def get_toolbar_contributions() -> List[Callable]:
    return list(_toolbar_builders)


def clear_ide_contributions() -> None:
    """Drop every registered contribution. For tests and for reloading."""
    _menu_builders.clear()
    _toolbar_builders.clear()
    clear_asset_tree_categories()
    clear_object_editor_panels()
    clear_toolbox_visibility_filters()
    clear_add_event_menu_contributions()


def apply_menu_contributions(ide, menus: Dict[str, object]) -> None:
    """Run every registered menu builder against ``menus`` (key -> QMenu).

    Called by the IDE once its own menus are built. A builder that raises is
    logged and skipped.
    """
    for key, build in _menu_builders:
        menu = menus.get(key)
        if menu is None:
            logger.error(f"IDE has no {key!r} menu for {getattr(build, '__name__', build)}")
            continue
        try:
            build(ide, menu)
        except Exception as exc:
            logger.error(
                f"Menu contribution {getattr(build, '__name__', build)} failed: {exc}")


def apply_toolbar_contributions(ide, toolbar) -> None:
    """Run every registered toolbar builder against the main toolbar."""
    for build in _toolbar_builders:
        try:
            build(ide, toolbar)
        except Exception as exc:
            logger.error(
                f"Toolbar contribution {getattr(build, '__name__', build)} failed: {exc}")


# ---------------------------------------------------------------------------
# Toolbox visibility filters: an extension's blocks/categories shouldn't
# show in the Blockly toolbox when they can't do anything yet (e.g. Thymio
# blocks in a project with no playground to run them against). Lets a
# widget stay ignorant of any particular extension while still hiding its
# blocks conditionally (docs/THYMIO_EXTENSION_PLAN.md, Stage G5b.1).
#
#     PLUGIN_TOOLBOX_VISIBILITY_FILTERS = [ToolboxVisibilityFilter(
#         is_enabled=lambda widget: project_has_robots(widget),
#         owns_block=lambda block_type: block_type.startswith("robot_"),
#         owns_category=lambda category: category.startswith("Robot "),
#     )]
#
# ``is_enabled`` returning True means "show them"; the filter only hides its
# own blocks/categories when it returns False.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ToolboxVisibilityFilter:
    is_enabled: Callable       # (widget) -> bool
    owns_block: Callable       # (block_type: str) -> bool
    owns_category: Callable    # (category: str) -> bool


_toolbox_visibility_filters: List[ToolboxVisibilityFilter] = []


def register_toolbox_visibility_filter(spec: ToolboxVisibilityFilter) -> None:
    if (not isinstance(spec, ToolboxVisibilityFilter) or not callable(spec.is_enabled)
            or not callable(spec.owns_block) or not callable(spec.owns_category)):
        logger.error(f"Toolbox visibility filter is not valid: {spec!r}")
        return
    _toolbox_visibility_filters.append(spec)


def get_toolbox_visibility_filters() -> List[ToolboxVisibilityFilter]:
    return list(_toolbox_visibility_filters)


def clear_toolbox_visibility_filters() -> None:
    _toolbox_visibility_filters.clear()


def apply_toolbox_visibility_filters(enabled_blocks, enabled_categories, widget):
    """Drop any extension's blocks/categories whose filter says "not now"
    for this ``widget`` (a Blockly-hosting widget with the same parent-chain
    shape every caller here already has). A filter that raises is logged and
    skipped -- a broken extension can't corrupt the whole toolbox."""
    for f in _toolbox_visibility_filters:
        try:
            if f.is_enabled(widget):
                continue
            enabled_blocks = {b for b in enabled_blocks if not f.owns_block(b)}
            enabled_categories = {c for c in enabled_categories if not f.owns_category(c)}
        except Exception as exc:
            logger.error(f"Toolbox visibility filter failed: {exc}")
    return enabled_blocks, enabled_categories


# ---------------------------------------------------------------------------
# Add-event-menu contributions: an extension's own events submenu in the
# object editor's "Add Event" menu (docs/THYMIO_EXTENSION_PLAN.md, G5b.2).
#
# ``key`` matches an already-registered ``ObjectEditorPanel.key``, so
# ``owned_event_names`` can answer "which of these events are mine" from
# that panel's own ``owned_events()`` instead of a second, divergeable copy.
# ``build`` receives the FULL ``available_events`` list (not pre-filtered)
# and is responsible for both picking its own events out of it and deciding
# whether to show anything at all this time (e.g. Thymio's events stay
# hidden with no playground asset, independent of its events being
# "available" under the current preset).
#
#     PLUGIN_ADD_EVENT_MENU_CONTRIBUTIONS = [AddEventMenuContribution(
#         key="robot",
#         build=lambda menu, panel, available_events: ...,
#     )]
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AddEventMenuContribution:
    key: str
    build: Callable   # (menu, panel, available_events) -> None


_add_event_menu_contributions: List[AddEventMenuContribution] = []


def register_add_event_menu_contribution(spec: AddEventMenuContribution) -> None:
    if not isinstance(spec, AddEventMenuContribution) or not callable(spec.build):
        logger.error(f"Add-event-menu contribution is not valid: {spec!r}")
        return
    _add_event_menu_contributions.append(spec)


def get_add_event_menu_contributions() -> List[AddEventMenuContribution]:
    return list(_add_event_menu_contributions)


def clear_add_event_menu_contributions() -> None:
    _add_event_menu_contributions.clear()


def owned_event_names(key: str) -> set:
    """Event names ``owned_events()`` reports for the ``ObjectEditorPanel``
    registered under ``key`` -- an empty set if no panel is registered under
    it (a contribution naming one that doesn't exist owns nothing, rather
    than erroring)."""
    for panel in get_object_editor_panels():
        if panel.key == key:
            return set(panel.owned_events())
    return set()


def apply_add_event_menu_contributions(menu, panel, available_events) -> None:
    """Run every registered add-event-menu contribution's ``build``. A
    contribution that raises is logged and skipped -- a broken extension
    can't break the whole Add Event menu."""
    for spec in _add_event_menu_contributions:
        try:
            spec.build(menu, panel, available_events)
        except Exception as exc:
            logger.error(f"Add-event-menu contribution {spec.key!r} failed: {exc}")
