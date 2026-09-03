#!/usr/bin/env python3
"""Events-tree context menu for :class:`ObjectEventsPanel`.

Extracted verbatim from ``ObjectEventsPanel.show_context_menu``
(``docs/POST_1_0_REFACTOR.md`` File 1). The only change is ``self`` ->
``panel``; the branch structure, menu wiring and ``menu.exec`` call are
untouched. ``panel.tr(...)`` keeps the "ObjectEventsPanel" translation
context (PySide6 resolves it from the concrete runtime class).
"""

from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt

from events.action_types import get_actions_by_category


def build_context_menu(panel, position):
    """Build and exec the events-tree context menu for *panel* at *position*."""
    item = panel.events_tree.itemAt(position)
    if not item:
        return

    menu = QMenu(panel)

    # Determine the item level and type
    parent = item.parent()
    grandparent = parent.parent() if parent else None

    # Level 1: Top-level event (create, step, collision, keyboard parent, etc.)
    if parent is None:
        event_name = item.data(0, Qt.UserRole)

        # Handle collision events specially
        if isinstance(event_name, str) and (event_name.startswith("collision_with_") or event_name.startswith("not_collision_with_")):
            add_action_menu = menu.addMenu(panel.tr("Add Action"))

            actions_by_category = get_actions_by_category(panel.blockly_config)
            for category, actions in actions_by_category.items():
                category_menu = add_action_menu.addMenu(category)

                for action_type in actions:
                    action_item = category_menu.addAction(f"{action_type.icon} {panel.tr(action_type.display_name)}")
                    action_item.triggered.connect(
                        lambda checked, e=event_name, a=action_type.name: panel.add_action_to_collision_event(e, a)
                    )

            # Add Thymio action option (only visible when project has playgrounds)
            if panel.project_has_playgrounds():
                add_action_menu.addSeparator()
                thymio_action = add_action_menu.addAction(panel.tr("🤖 Thymio Action..."))
                thymio_action.triggered.connect(lambda checked, e=event_name: panel.add_thymio_action_with_selector(e))

            panel._add_event_paste_menu(menu, item)
            menu.addSeparator()
            remove_action = menu.addAction(panel.tr("Remove Collision Event"))
            remove_action.triggered.connect(lambda: panel.remove_collision_event(event_name))

        # Handle mouse events specially
        elif isinstance(event_name, str) and event_name.startswith("mouse_"):
            add_action_menu = menu.addMenu(panel.tr("Add Action"))

            actions_by_category = get_actions_by_category(panel.blockly_config)
            for category, actions in actions_by_category.items():
                category_menu = add_action_menu.addMenu(category)

                for action_type in actions:
                    action_item = category_menu.addAction(f"{action_type.icon} {panel.tr(action_type.display_name)}")
                    action_item.triggered.connect(
                        lambda checked, e=event_name, a=action_type.name: panel.add_action_to_mouse_event(e, a)
                    )

            # Add Thymio action option (only visible when project has playgrounds)
            if panel.project_has_playgrounds():
                add_action_menu.addSeparator()
                thymio_action = add_action_menu.addAction(panel.tr("🤖 Thymio Action..."))
                thymio_action.triggered.connect(lambda checked, e=event_name: panel.add_thymio_action_with_selector(e))

            panel._add_event_paste_menu(menu, item)
            menu.addSeparator()
            remove_action = menu.addAction(panel.tr("Remove Mouse Event"))
            remove_action.triggered.connect(lambda: panel.remove_mouse_event(event_name))

        elif isinstance(event_name, str) and event_name in panel._CONTAINER_EVENT_HINTS:
            # Container events (keyboard/keyboard_press/keyboard_release/alarm)
            # don't accept actions directly — actions go on the sub-event
            # (SPACE, Alarm 0, etc.). Surface a contextual sub-event adder
            # instead of the misleading "Add Action" submenu so the user
            # never has to discover the matching add-sub-event button on
            # the toolbar.
            if event_name in ("keyboard", "keyboard_press", "keyboard_release"):
                add_sub = menu.addAction(panel.tr("Add Key…"))
                add_sub.triggered.connect(
                    lambda checked, e=event_name: panel.add_keyboard_event_with_selector(e)
                )
            elif event_name == "alarm":
                add_sub_menu = menu.addMenu(panel.tr("Add Alarm"))
                for alarm_num in range(12):
                    alarm_action = add_sub_menu.addAction(f"⏰ {panel.tr('Alarm')} {alarm_num}")
                    alarm_action.triggered.connect(
                        lambda checked, n=alarm_num: panel.add_alarm_event(n)
                    )

            menu.addSeparator()
            remove_action = menu.addAction(panel.tr("Remove Event"))
            remove_action.triggered.connect(panel.remove_selected_event)

        else:
            # Regular leaf events (create, step, etc.) accept actions.
            add_action_menu = menu.addMenu(panel.tr("Add Action"))

            actions_by_category = get_actions_by_category(panel.blockly_config)
            for category, actions in actions_by_category.items():
                category_menu = add_action_menu.addMenu(category)

                for action_type in actions:
                    action_item = category_menu.addAction(f"{action_type.icon} {panel.tr(action_type.display_name)}")
                    action_item.triggered.connect(
                        lambda checked, e=event_name, a=action_type.name: panel.add_action_to_event(e, a)
                    )

            # Add Thymio action option (only visible when project has playgrounds)
            if panel.project_has_playgrounds():
                add_action_menu.addSeparator()
                thymio_action = add_action_menu.addAction(panel.tr("🤖 Thymio Action..."))
                thymio_action.triggered.connect(lambda checked, e=event_name: panel.add_thymio_action_with_selector(e))

            panel._add_event_paste_menu(menu, item)
            menu.addSeparator()
            remove_action = menu.addAction(panel.tr("Remove Event"))
            remove_action.triggered.connect(panel.remove_selected_event)

    # Level 2: Could be keyboard sub-event OR action under regular event
    elif parent and grandparent is None:
        item_data = item.data(0, Qt.UserRole)

        # Check if this is a keyboard sub-event (string data) or action (dict data)
        if isinstance(item_data, str) and "_" in item_data:
            # This is a keyboard sub-event (Left Arrow, Right Arrow, etc.)
            parent_item = parent
            event_name = parent_item.data(0, Qt.UserRole)

            # Extract the key from the stored data (format: "keyboard_left" or "keyboard_press_left")
            if item_data.startswith(event_name + "_"):
                sub_event_key = item_data[len(event_name) + 1:]  # Extract the key after "event_name_"

                # Add action submenu for this specific key
                add_action_menu = menu.addMenu(panel.tr("Add Action"))

                actions_by_category = get_actions_by_category(panel.blockly_config)
                for category, actions in actions_by_category.items():
                    category_menu = add_action_menu.addMenu(category)

                    for action_type in actions:
                        action_item = category_menu.addAction(f"{action_type.icon} {panel.tr(action_type.display_name)}")
                        action_item.triggered.connect(
                            lambda checked, e=event_name, k=sub_event_key, a=action_type.name:
                            panel.add_action_to_sub_event(e, k, a)
                        )

                # Add Thymio action option (only visible when project has playgrounds)
                if panel.project_has_playgrounds():
                    add_action_menu.addSeparator()
                    thymio_action = add_action_menu.addAction(panel.tr("🤖 Thymio Action..."))
                    thymio_action.triggered.connect(
                        lambda checked, e=event_name, k=sub_event_key: panel.add_thymio_action_to_sub_event(e, k)
                    )

                panel._add_event_paste_menu(menu, item)
                menu.addSeparator()
                remove_action = menu.addAction(panel.tr("Remove {0} Event").format(sub_event_key.title()))
                remove_action.triggered.connect(lambda: panel.remove_sub_event(parent_item, item))

        elif isinstance(item_data, dict):
            # This is an action under a regular event (Create, Step, Collision, etc.)
            edit_action = menu.addAction(panel.tr("Edit Action"))
            edit_action.triggered.connect(lambda: panel.edit_action(item))

            panel._add_action_clipboard_menu(menu, item)

            remove_action = menu.addAction(panel.tr("Remove Action"))
            remove_action.triggered.connect(lambda: panel.remove_action(item))

    # Level 3: Action item (child of either regular event or keyboard sub-event)
    else:
        action_data = item.data(0, Qt.UserRole)
        if action_data and isinstance(action_data, dict):
            edit_action = menu.addAction(panel.tr("Edit Action"))
            edit_action.triggered.connect(lambda: panel.edit_action(item))

            panel._add_action_clipboard_menu(menu, item)

            remove_action = menu.addAction(panel.tr("Remove Action"))
            remove_action.triggered.connect(lambda: panel.remove_action(item))

    menu.exec(panel.events_tree.mapToGlobal(position))
