#!/usr/bin/env python3
"""
Blockly Visual Programming Widget for PyGameMaker
Provides a Scratch-like block programming interface using Google Blockly
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow
from PySide6.QtCore import Signal, Slot, QUrl, QObject, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QCloseEvent

from core.logger import get_logger
logger = get_logger(__name__)


class BlocklyBridge(QObject):
    """Bridge between Python and JavaScript for Blockly communication"""

    # Signal emitted when blocks change
    blocks_changed = Signal(str)  # JSON string of generated events/actions

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)
    def onBlocksChanged(self, code_json: str):
        """Called from JavaScript when blocks change"""
        self.blocks_changed.emit(code_json)


class DetachedBlocklyWindow(QMainWindow):
    """Detached window for Blockly visual programming editor"""

    # Signal emitted when the window is closed (to re-attach the widget)
    window_closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Visual Block Programming (Detached)"))
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # Central widget container
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.container)

    def set_widget(self, widget: QWidget):
        """Set the widget to display in this window"""
        self.container_layout.addWidget(widget)

    def take_widget(self) -> Optional[QWidget]:
        """Remove and return the widget from this window"""
        if self.container_layout.count() > 0:
            item = self.container_layout.takeAt(0)
            if item and item.widget():
                return item.widget()
        return None

    def closeEvent(self, event: QCloseEvent):
        """Handle window close - emit signal to re-attach widget"""
        self.window_closed.emit()
        event.accept()


class BlocklyWidget(QWidget):
    """Widget containing the Blockly visual programming interface"""

    # Signals
    blocks_modified = Signal()  # Emitted when blocks are modified
    events_generated = Signal(dict)  # Emitted with generated events data
    sync_requested = Signal()  # Emitted when user wants to sync from events panel
    detach_requested = Signal()  # Emitted when user wants to detach the editor
    config_changed = Signal(object)  # Emitted when Blockly config changes (passes BlocklyConfig)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.events_data = {}
        self._loading = False

        self.setup_ui()
        self.setup_web_channel()

    def setup_ui(self):
        """Setup the Blockly widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)

        # Apply button (Blockly → Events)
        self.apply_button = QPushButton(self.tr("Apply to Events →"))
        self.apply_button.setToolTip(self.tr("Apply block changes to the Events panel"))
        self.apply_button.clicked.connect(self.apply_blocks_to_events)
        toolbar.addWidget(self.apply_button)

        # Sync from Events button (Events → Blockly)
        self.sync_button = QPushButton(self.tr("← Sync from Events"))
        self.sync_button.setToolTip(self.tr("Load events from the Events panel into blocks"))
        self.sync_button.clicked.connect(self.request_sync_from_events)
        toolbar.addWidget(self.sync_button)

        # Clear button
        self.clear_button = QPushButton(self.tr("Clear All"))
        self.clear_button.clicked.connect(self.clear_workspace)
        toolbar.addWidget(self.clear_button)

        # Reload button (for debugging/reloading Blockly)
        self.reload_button = QPushButton(self.tr("Reload"))
        self.reload_button.clicked.connect(self.reload_blockly)
        toolbar.addWidget(self.reload_button)

        # Configure blocks button
        self.configure_btn = QPushButton(self.tr("Configure Blocks..."))
        self.configure_btn.setToolTip(self.tr("Choose which blocks are available in the toolbox"))
        self.configure_btn.clicked.connect(self.open_configure_dialog)
        toolbar.addWidget(self.configure_btn)

        toolbar.addStretch()

        # Detach button
        self.detach_btn = QPushButton(self.tr("⬜ Detach"))
        self.detach_btn.setToolTip(self.tr("Open Blockly editor in a separate window"))
        self.detach_btn.clicked.connect(self.request_detach)
        toolbar.addWidget(self.detach_btn)

        layout.addLayout(toolbar)

        # Web view for Blockly
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)

        # Hide web view until loaded to prevent visual flickering
        self.web_view.setVisible(False)

        # Configure web settings to allow external scripts
        settings = self.web_view.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        # Connect load finished signal
        self.web_view.loadFinished.connect(self.on_load_finished)

        # Load the Blockly HTML
        self._load_blockly_html()

        layout.addWidget(self.web_view)

    def _load_blockly_html(self):
        """Load the Blockly HTML file with language parameter"""
        from core.language_manager import get_language_manager

        # Get current language to pass to the HTML
        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()

        blockly_html = Path(__file__).parent / "blockly" / "blockly_workspace.html"
        if blockly_html.exists():
            # Pass language as URL fragment to be read by JavaScript
            url = QUrl.fromLocalFile(str(blockly_html))
            url.setQuery(f"lang={current_lang}")
            self.web_view.setUrl(url)
        else:
            # Try alternate path
            blockly_html = Path("/home/gabe/Dropbox/pygm2/editors/object_editor/blockly/blockly_workspace.html")
            if blockly_html.exists():
                url = QUrl.fromLocalFile(str(blockly_html))
                url.setQuery(f"lang={current_lang}")
                self.web_view.setUrl(url)
            else:
                logger.error(f"Blockly HTML not found at {blockly_html}")
                self.web_view.setHtml("<h1>Blockly not found</h1><p>Could not load blockly_workspace.html</p>")

    def on_load_finished(self, ok: bool):
        """Handle page load completion"""
        # Show the web view now that it's loaded
        self.web_view.setVisible(True)

        if ok:
            # Set the language for Blockly blocks
            self._set_blockly_language()

            # Apply saved configuration to toolbox
            self._apply_saved_configuration()
            self.update_status(self.tr("Drag blocks from the toolbox on the left to create game logic!"))
        else:
            self.update_status(self.tr("Error loading Blockly - click Reload to try again"))

    def _set_blockly_language(self):
        """Set the Blockly language based on IDE language setting"""
        from core.language_manager import get_language_manager

        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()

        logger.debug(f"Setting Blockly language to: {current_lang}")

        # Call JavaScript function to set the language
        self.web_view.page().runJavaScript(
            f"if (typeof setBlocklyLanguage !== 'undefined') {{ setBlocklyLanguage('{current_lang}'); }}"
        )

    def reload_blockly(self):
        """Reload the Blockly workspace"""
        self.update_status(self.tr("Reloading Blockly..."))
        self.web_view.setVisible(False)  # Hide during reload
        self._load_blockly_html()

    def setup_web_channel(self):
        """Setup Qt WebChannel for JavaScript communication"""
        self.bridge = BlocklyBridge(self)
        self.bridge.blocks_changed.connect(self.on_blocks_changed)

        self.channel = QWebChannel()
        self.channel.registerObject("pyBridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

    @Slot(str)
    def on_blocks_changed(self, code_json: str):
        """Handle blocks changed from JavaScript"""
        if self._loading:
            return

        try:
            self.events_data = json.loads(code_json)
            self.blocks_modified.emit()
            self.update_status(self.tr("Blocks updated - {0} events").format(len(self.events_data)))
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing blocks JSON: {e}")

    def apply_blocks_to_events(self):
        """Apply the current blocks to the object's events"""
        # Get the generated events from Blockly
        self.web_view.page().runJavaScript(
            "window.blocklyApi.getCode()",
            self._on_code_received
        )

    def _on_code_received(self, code_json: str):
        """Callback when code is received from JavaScript"""
        if code_json:
            try:
                events = json.loads(code_json)
                self.events_data = events
                self.events_generated.emit(events)
                self.update_status(self.tr("Applied {0} events").format(len(events)))
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing code JSON: {e}")

    def clear_workspace(self):
        """Clear the Blockly workspace"""
        self.web_view.page().runJavaScript("window.blocklyApi.clear()")
        self.events_data = {}
        self.update_status(self.tr("Workspace cleared"))

    def get_workspace_xml(self) -> str:
        """Get the current workspace as XML (for saving)"""
        # This is async, so we use a callback pattern
        result = {"xml": ""}

        def callback(xml):
            result["xml"] = xml

        self.web_view.page().runJavaScript(
            "window.blocklyApi.getXml()",
            callback
        )

        return result["xml"]

    def load_workspace_xml(self, xml: str):
        """Load workspace from XML"""
        if not xml:
            return

        self._loading = True
        # Escape the XML for JavaScript
        escaped_xml = xml.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        self.web_view.page().runJavaScript(
            f"window.blocklyApi.loadXml('{escaped_xml}')"
        )
        self._loading = False

    def get_events_data(self) -> Dict[str, Any]:
        """Get the current events data"""
        return self.events_data

    def load_events_data(self, events_data: Dict[str, Any]):
        """Load events data and convert to Blockly blocks (bidirectional sync)"""
        self.events_data = events_data

        if not events_data:
            self.update_status(self.tr("No events to load"))
            return

        # Debug: Log the events data being sent
        logger.debug(f"Loading events data: {json.dumps(events_data, indent=2)}")

        # Convert events data to JSON and send to Blockly
        self._loading = True
        events_json = json.dumps(events_data)
        # Escape for JavaScript string - must escape backslashes first, then quotes
        escaped_json = events_json.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")

        def on_load_complete(result):
            self._loading = False
            logger.debug(f"Blockly load complete, result: {result}")
            if result is not None:
                self.update_status(self.tr("Loaded {0} events as blocks").format(result))
            else:
                self.update_status(self.tr("Loaded {0} events - some may not have block equivalents").format(len(events_data)))

        # Check if blocklyApi is available before calling
        check_and_load_script = f"""
            (function() {{
                if (typeof window.blocklyApi === 'undefined') {{
                    console.error('[Blockly] blocklyApi not available yet');
                    return null;
                }}
                if (typeof window.blocklyApi.loadEvents !== 'function') {{
                    console.error('[Blockly] loadEvents function not available');
                    return null;
                }}
                try {{
                    var eventsData = JSON.parse('{escaped_json}');
                    console.log('[Blockly] Parsed events data:', JSON.stringify(eventsData, null, 2));
                    return window.blocklyApi.loadEvents(eventsData);
                }} catch (e) {{
                    console.error('[Blockly] Error loading events:', e);
                    return null;
                }}
            }})()
        """

        self.web_view.page().runJavaScript(check_and_load_script, on_load_complete)

    def update_status(self, message: str):
        """Update status (no-op - status label removed to save space)"""

    def request_sync_from_events(self):
        """Request sync from events panel (emits signal for parent to handle)"""
        self.update_status(self.tr("Requesting sync from events..."))
        self.sync_requested.emit()

    def open_configure_dialog(self):
        """Open the block configuration dialog"""
        from dialogs.blockly_config_dialog import BlocklyConfigDialog
        from config.blockly_config import load_config, PRESETS, BlocklyConfig

        # Try to load preset from project settings first
        current_config = None
        project_preset = self._get_project_preset()
        if project_preset and project_preset in PRESETS:
            # Make a copy to avoid modifying the original preset
            current_config = BlocklyConfig.from_dict(PRESETS[project_preset].to_dict())
        else:
            current_config = load_config()

        dialog = BlocklyConfigDialog(self, current_config)
        dialog.config_changed.connect(self.apply_configuration)
        if dialog.exec():
            # Save preset to project settings
            self._save_project_preset(dialog.config.preset_name)

    def _get_project_preset(self) -> Optional[str]:
        """Get Blockly preset from project settings"""
        try:
            # Navigate up to find the object editor which has project_path
            parent = self.parent()
            while parent and not hasattr(parent, 'project_path'):
                parent = parent.parent()

            if parent and parent.project_path:
                project_file = Path(parent.project_path) / "project.json"
                if project_file.exists():
                    with open(project_file, 'r') as f:
                        data = json.load(f)
                    return data.get('settings', {}).get('blockly_preset')
        except Exception as e:
            logger.error(f"Error loading project preset: {e}")
        return None

    def _save_project_preset(self, preset_name: str):
        """Save Blockly preset to project settings"""
        try:
            # Navigate up to find the object editor which has project_path
            parent = self.parent()
            while parent and not hasattr(parent, 'project_path'):
                parent = parent.parent()

            if parent and parent.project_path:
                project_file = Path(parent.project_path) / "project.json"
                if project_file.exists():
                    with open(project_file, 'r') as f:
                        data = json.load(f)

                    if 'settings' not in data:
                        data['settings'] = {}
                    data['settings']['blockly_preset'] = preset_name

                    with open(project_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    logger.info(f"Saved Blockly preset '{preset_name}' to project")
        except Exception as e:
            logger.error(f"Error saving project preset: {e}")

    def apply_configuration(self, config):
        """Apply a new block configuration to the toolbox"""

        # Convert config to JSON format expected by JavaScript
        config_dict = {
            'enabled_blocks': list(config.enabled_blocks),
            'enabled_categories': list(config.enabled_categories),
            'preset_name': config.preset_name
        }
        config_json = json.dumps(config_dict)

        # Call JavaScript to reconfigure toolbox
        self.web_view.page().runJavaScript(
            f"window.blocklyApi.reconfigureToolbox({config_json})"
        )

        # Update status
        total_blocks = len(config.enabled_blocks)
        total_categories = len(config.enabled_categories)
        self.update_status(self.tr("Configuration applied: {0} blocks, {1} categories").format(total_blocks, total_categories))

        # Emit signal so other components (events panel) can update
        self.config_changed.emit(config)

    def _apply_saved_configuration(self):
        """Apply the saved configuration on startup"""
        from config.blockly_config import load_config

        config = load_config()
        self.apply_configuration(config)

    def request_detach(self):
        """Request to detach the editor to a separate window"""
        self.detach_requested.emit()


class BlocklyVisualProgrammingTab(QWidget):
    """Complete visual programming tab with Blockly"""

    # Signals
    events_modified = Signal(dict)  # Emitted when events are modified
    sync_requested = Signal()  # Emitted when user wants to sync from events panel
    config_changed = Signal(object)  # Emitted when Blockly config changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.detached_window = None
        self.is_detached = False
        self.setup_ui()

    def setup_ui(self):
        """Setup the complete visual programming tab"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Info bar
        info_layout = QHBoxLayout()

        self.title_label = QLabel(self.tr("Visual Block Programming"))
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.title_label)

        info_layout.addStretch()

        self.help_label = QLabel(self.tr("Drag blocks from the toolbox on the left to create game logic"))
        self.help_label.setStyleSheet("color: #666; font-style: italic;")
        info_layout.addWidget(self.help_label)

        self.main_layout.addLayout(info_layout)

        # Placeholder label shown when editor is detached
        self.detached_placeholder = QLabel(self.tr("Editor is detached. Close the detached window to return it here."))
        self.detached_placeholder.setAlignment(Qt.AlignCenter)
        self.detached_placeholder.setStyleSheet("color: #888; font-size: 14px; padding: 50px;")
        self.detached_placeholder.hide()
        self.main_layout.addWidget(self.detached_placeholder)

        # Blockly widget
        self.blockly_widget = BlocklyWidget()
        self.blockly_widget.events_generated.connect(self.on_events_generated)
        self.blockly_widget.blocks_modified.connect(self.on_blocks_modified)
        self.blockly_widget.sync_requested.connect(self.on_sync_requested)
        self.blockly_widget.detach_requested.connect(self.detach_editor)
        self.blockly_widget.config_changed.connect(self.config_changed)  # Forward config changes
        self.main_layout.addWidget(self.blockly_widget)

    def detach_editor(self):
        """Detach the Blockly editor to a separate window"""
        if self.is_detached:
            # Already detached, bring window to front
            if self.detached_window:
                self.detached_window.raise_()
                self.detached_window.activateWindow()
            return

        # Create detached window
        self.detached_window = DetachedBlocklyWindow()
        self.detached_window.window_closed.connect(self.attach_editor)

        # Remove widget from layout and add to detached window
        self.main_layout.removeWidget(self.blockly_widget)
        self.detached_window.set_widget(self.blockly_widget)

        # Show placeholder in tab
        self.detached_placeholder.show()

        # Update button text
        self.blockly_widget.detach_btn.setText(self.tr("📥 Attach"))
        self.blockly_widget.detach_btn.setToolTip(self.tr("Return editor to the tab"))
        self.blockly_widget.detach_btn.clicked.disconnect()
        self.blockly_widget.detach_btn.clicked.connect(self.attach_editor)

        # Show detached window
        self.detached_window.show()
        self.is_detached = True

    def attach_editor(self):
        """Attach the Blockly editor back to the tab"""
        if not self.is_detached:
            return

        # Mark as attached early to prevent re-entry from Qt signals
        self.is_detached = False

        # Get widget from detached window (defensive check for None)
        if self.detached_window is not None:
            widget = self.detached_window.take_widget()
            if widget:
                # Hide placeholder
                self.detached_placeholder.hide()

                # Add widget back to layout
                self.main_layout.addWidget(widget)

                # Update button text
                self.blockly_widget.detach_btn.setText(self.tr("⬜ Detach"))
                self.blockly_widget.detach_btn.setToolTip(self.tr("Open Blockly editor in a separate window"))
                self.blockly_widget.detach_btn.clicked.disconnect()
                self.blockly_widget.detach_btn.clicked.connect(self.detach_editor)

            # Close and cleanup detached window
            self.detached_window.close()
            self.detached_window.deleteLater()
            self.detached_window = None

    def on_events_generated(self, events: dict):
        """Handle events generated from blocks"""
        self.events_modified.emit(events)

    def on_blocks_modified(self):
        """Handle blocks being modified"""
        # Could add auto-save or dirty state tracking here

    def on_sync_requested(self):
        """Handle sync request from Blockly widget"""
        self.sync_requested.emit()

    def get_events_data(self) -> Dict[str, Any]:
        """Get events data from blocks"""
        return self.blockly_widget.get_events_data()

    def load_events_data(self, events_data: Dict[str, Any]):
        """Load events data into blocks"""
        self.blockly_widget.load_events_data(events_data)

    def get_workspace_xml(self) -> str:
        """Get workspace XML for saving"""
        return self.blockly_widget.get_workspace_xml()

    def load_workspace_xml(self, xml: str):
        """Load workspace from XML"""
        self.blockly_widget.load_workspace_xml(xml)
