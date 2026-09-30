#!/usr/bin/env python3
"""Tools-menu / toolbar action handlers for the Thymio UI (docs/
THYMIO_EXTENSION_PLAN.md, Stage G). Moved verbatim out of
``core/ide/_dialogs.py`` -- ``self`` renamed to the explicit ``ide``
parameter, same pattern ``extensions/thymio/export``'s
``export_aseba_code``/``import_roberta_xml`` and ``extensions/thymio/editor``'s
``open_playground_editor`` already established (Stages D/C5).

Wired in by ``extensions/thymio/__init__.py``'s ``_build_tools_menu``/
``_build_toolbar`` (``PLUGIN_IDE_MENUS``/``PLUGIN_IDE_TOOLBAR``), gated by the
same ``show_thymio_tab`` config flag that already gates the object-editor
panel -- kept hidden by default (the 1.0 decision), so this module has no
effect on a default install; flipping that one flag brings the whole UI
(tab + these menu/toolbar entries) back together.
"""
from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import Qt

from utils.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


def configure_thymio(ide) -> None:
    """Open Thymio configuration dialog to customize available Thymio blocks"""
    from config.blockly_config import load_config, save_config, PRESETS, BlocklyConfig
    from .dialogs.thymio_config_dialog import ThymioConfigDialog

    # Try to load preset from current project settings first
    current_config = None
    if ide.current_project_data:
        project_preset = ide.current_project_data.get('settings', {}).get('blockly_preset')
        if project_preset and project_preset in PRESETS:
            current_config = BlocklyConfig.from_dict(PRESETS[project_preset].to_dict())

    # Fall back to global config if no project preset
    if not current_config:
        current_config = load_config()

    # Show Thymio-specific dialog
    dialog = ThymioConfigDialog(ide, current_config)
    if dialog.exec() == QDialog.Accepted:
        # Save the new configuration
        new_config = dialog.config
        save_config(new_config)

        # Also save to project settings if a project is open
        if ide.current_project_path and ide.current_project_data:
            if 'settings' not in ide.current_project_data:
                ide.current_project_data['settings'] = {}
            ide.current_project_data['settings']['blockly_preset'] = new_config.preset_name
            ide.save_project()
            logger.info("✅ Saved Thymio preset to project")

        # Refresh any open events panels
        ide.refresh_event_panels_config()

        # Show confirmation
        QMessageBox.information(
            ide,
            ide.tr("Thymio Configuration Saved"),
            ide.tr("Thymio block configuration has been saved.\n\n"
                    "The new Thymio event/action selection is now active.")
        )

        logger.info("✅ Thymio configuration updated")


def toggle_thymio_tab(ide) -> None:
    """Toggle visibility of Thymio tab in object editors"""
    show_thymio = ide.show_thymio_tab_action.isChecked()

    # Save preference
    Config.set('show_thymio_tab', show_thymio)

    # Update all open object editors
    for i in range(ide.editor_tabs.count()):
        widget = ide.editor_tabs.widget(i)
        if hasattr(widget, 'set_thymio_tab_visible'):
            widget.set_thymio_tab_visible(show_thymio)

    logger.info(f"Thymio tab visibility: {'shown' if show_thymio else 'hidden'}")


def show_thymio_playground(ide) -> None:
    """Open the Thymio Playground simulator window.

    Reuse a still-live window instead of leaking a new one on every open,
    and mark it WA_DeleteOnClose so closing it frees the C++ object rather
    than keeping a dangling handle around.
    """
    from extensions.thymio.playground_window import ThymioPlaygroundWindow
    import shiboken6

    existing = getattr(ide, "thymio_playground", None)
    if existing is not None and shiboken6.isValid(existing):
        # Already open and live — raise it instead of spawning another.
        existing.showNormal()
        existing.raise_()
        existing.activateWindow()
        logger.info("Raised existing Thymio Playground window")
        return

    ide.thymio_playground = ThymioPlaygroundWindow(ide)
    ide.thymio_playground.setAttribute(Qt.WA_DeleteOnClose)
    ide.thymio_playground.show()
    logger.info("Opened Thymio Playground window")


def show_thymio_event_selector(ide) -> None:
    """Show the Thymio event selector dialog"""
    from .dialogs.thymio_event_selector import ThymioEventSelector

    dialog = ThymioEventSelector(ide)
    if dialog.exec() == QDialog.Accepted:
        selected_event = dialog.get_selected_event()
        if selected_event:
            # Try to add event to current object editor
            current_widget = ide.editor_tabs.currentWidget()
            if hasattr(current_widget, 'events_panel'):
                # Call the panel's Thymio event method
                if hasattr(current_widget.events_panel, 'add_thymio_event_with_selector'):
                    # Directly add the event since we already selected it
                    events_panel = current_widget.events_panel
                    if selected_event in events_panel.current_events_data:
                        QMessageBox.information(
                            ide,
                            ide.tr("Event Exists"),
                            ide.tr("This Thymio event already exists in the object.")
                        )
                    else:
                        events_panel.current_events_data[selected_event] = {"actions": []}
                        events_panel.refresh_events_display()
                        events_panel.events_modified.emit()
            else:
                QMessageBox.information(
                    ide,
                    ide.tr("No Object Editor"),
                    ide.tr("Please open an object editor first to add Thymio events.")
                )


def show_thymio_action_selector(ide) -> None:
    """Show the Thymio action selector dialog"""
    from .dialogs.thymio_action_selector import ThymioActionSelector

    # Check if we have an object editor open
    current_widget = ide.editor_tabs.currentWidget()
    if not hasattr(current_widget, 'events_panel'):
        QMessageBox.information(
            ide,
            ide.tr("No Object Editor"),
            ide.tr("Please open an object editor first to add Thymio actions.")
        )
        return

    events_panel = current_widget.events_panel
    # Get the currently selected event
    current_item = events_panel.events_tree.currentItem()
    if not current_item:
        QMessageBox.information(
            ide,
            ide.tr("No Event Selected"),
            ide.tr("Please select an event first to add actions to it.")
        )
        return

    # Get event name (handle both top-level events and sub-events)
    event_name = current_item.data(0, Qt.UserRole)
    if not event_name or not isinstance(event_name, str):
        QMessageBox.information(
            ide,
            ide.tr("Invalid Selection"),
            ide.tr("Please select an event (not an action) to add Thymio actions.")
        )
        return

    dialog = ThymioActionSelector(ide)
    if dialog.exec() == QDialog.Accepted:
        action_name, parameters = dialog.get_result()
        if action_name:
            # Add action to the selected event
            action_data = {
                "action": action_name,
                "parameters": parameters
            }

            if event_name in events_panel.current_events_data:
                events_panel.current_events_data[event_name]["actions"].append(action_data)
                events_panel.refresh_events_display()
                events_panel.events_modified.emit()
