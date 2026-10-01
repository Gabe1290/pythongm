#!/usr/bin/env python3
"""Object-editor "Standard" panel menu contributions for Thymio (docs/
THYMIO_EXTENSION_PLAN.md, Stage G5b.2/G5b.3).

Distinct from ``tools_menu.py``: that module is the IDE-chrome Tools-menu/
toolbar entries (``PLUGIN_IDE_MENUS``/``PLUGIN_IDE_TOOLBAR``, Stage G), gated
by the ``show_thymio_tab`` config flag and dealing with ``ide``. This module
is the Standard panel's own "Add Event"/"Add Action" menus -- reachable with
the dedicated Thymio tab off, on any project with a ``thymio*`` object --
gated by :func:`extensions.thymio._project_has_playgrounds` and dealing with
``panel`` (an ``ObjectEventsPanel``).

``build_add_event_menu`` is moved verbatim out of
``editors/object_editor/events/_event_crud.py``'s old inline Thymio submenu
block, ``self`` -> ``panel``, ``is_thymio_event`` -> membership in the
"thymio" ``ObjectEditorPanel``'s own ``owned_events()``.
``add_thymio_event_with_selector`` is moved verbatim out of the same file,
``self`` -> ``panel``.

``add_thymio_action_with_selector``/``add_thymio_action_to_sub_event`` are
moved verbatim out of ``editors/object_editor/events/_action_crud.py``,
``self`` -> ``panel``; ``thymio_add_action_menu_handler`` is the
``AddActionMenuContribution.handler`` the events-tree context menu's "Add
Action" submenu now calls (G5b.3), dispatching on whether a sub-event key
was given.
"""
from PySide6.QtWidgets import QMessageBox, QDialog

from .events import THYMIO_EVENT_CATEGORIES


def build_add_event_menu(menu, panel, available_events) -> None:
    """``AddEventMenuContribution.build`` for the "thymio" key: a submenu of
    every enabled Thymio event, grouped by category, with a visual-selector
    entry at the bottom -- shown only when the project has a playground
    (same gate the Blockly toolbox filter uses, G5b.1)."""
    from . import _project_has_playgrounds
    from core.ide_extension_points import owned_event_names

    if not _project_has_playgrounds(panel):
        return

    owned = owned_event_names("thymio")
    thymio_events = [e for e in available_events if e.name in owned]
    if not thymio_events:
        return

    menu.addSeparator()
    thymio_menu = menu.addMenu(panel.tr("🤖 Thymio Events"))

    thymio_by_category = {}
    for event_type in thymio_events:
        thymio_by_category.setdefault(event_type.category, []).append(event_type)

    sorted_categories = sorted(
        thymio_by_category.keys(),
        key=lambda c: THYMIO_EVENT_CATEGORIES.get(c, {}).get("order", 999)
    )
    for category in sorted_categories:
        cat_info = THYMIO_EVENT_CATEGORIES.get(category, {})
        cat_icon = cat_info.get("icon", "🤖")
        # Strip "Thymio " prefix for cleaner submenu names
        cat_label = category.replace("Thymio ", "")
        cat_submenu = thymio_menu.addMenu(f"{cat_icon} {panel.tr(cat_label)}")

        for event_type in thymio_by_category[category]:
            action = cat_submenu.addAction(
                f"{event_type.icon} {panel.tr(event_type.display_name)}"
            )
            action.triggered.connect(
                lambda checked, name=event_type.name: panel.add_event(name)
            )

    thymio_menu.addSeparator()
    visual_action = thymio_menu.addAction(panel.tr("🤖 Visual Selector..."))
    visual_action.triggered.connect(lambda: add_thymio_event_with_selector(panel))


def add_thymio_event_with_selector(panel) -> None:
    """Add a Thymio event using the visual Thymio event selector dialog"""
    from .dialogs.thymio_event_selector import ThymioEventSelector

    dialog = ThymioEventSelector(panel)
    if dialog.exec() == QDialog.Accepted:
        selected_event = dialog.get_selected_event()

        if selected_event:
            # Check if event already exists
            if selected_event in panel.current_events_data:
                QMessageBox.information(
                    panel,
                    panel.tr("Thymio Event Exists"),
                    panel.tr("This Thymio event already exists.")
                )
                return

            # Add the Thymio event
            panel.current_events_data[selected_event] = {
                "actions": []
            }

            panel.refresh_events_display()
            panel.events_modified.emit()


def add_thymio_action_with_selector(panel, event_name: str) -> None:
    """Add a Thymio action using the visual Thymio action selector dialog"""
    from .dialogs.thymio_action_selector import ThymioActionSelector

    dialog = ThymioActionSelector(panel)
    if dialog.exec() == QDialog.Accepted:
        action_name, parameters = dialog.get_result()

        if action_name:
            # Create action data structure
            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            # Add to event
            if event_name not in panel.current_events_data:
                panel.current_events_data[event_name] = {"actions": []}

            panel.current_events_data[event_name]["actions"].append(action_data)
            panel.refresh_events_display()
            panel.events_modified.emit()


def add_thymio_action_to_sub_event(panel, event_name: str, sub_event_key: str) -> None:
    """Add a Thymio action to a keyboard sub-event using the visual selector dialog"""
    from .dialogs.thymio_action_selector import ThymioActionSelector

    dialog = ThymioActionSelector(panel)
    if dialog.exec() == QDialog.Accepted:
        action_name, parameters = dialog.get_result()

        if action_name:
            # Create action data structure
            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            # Add to sub-event
            if event_name in panel.current_events_data:
                if sub_event_key in panel.current_events_data[event_name]:
                    if "actions" not in panel.current_events_data[event_name][sub_event_key]:
                        panel.current_events_data[event_name][sub_event_key]["actions"] = []
                    panel.current_events_data[event_name][sub_event_key]["actions"].append(action_data)
                    panel.refresh_events_display()
                    panel.events_modified.emit()


def thymio_add_action_menu_handler(panel, event_name, sub_event_key) -> None:
    """``AddActionMenuContribution.handler`` for the events-tree context
    menu's "Add Action" submenu: dispatches to the plain-event or
    sub-event variant depending on whether a sub-event key was given."""
    if sub_event_key is None:
        add_thymio_action_with_selector(panel, event_name)
    else:
        add_thymio_action_to_sub_event(panel, event_name, sub_event_key)
