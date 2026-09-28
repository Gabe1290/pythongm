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
from typing import Callable, Dict, List, Tuple

from core.logger import get_logger

logger = get_logger(__name__)

MENU_KEYS = ("file", "edit", "assets", "build", "tools", "help")

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
