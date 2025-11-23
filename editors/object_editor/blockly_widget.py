#!/usr/bin/env python3
"""
Blockly Visual Programming Widget for PyGameMaker
Provides a Scratch-like block programming interface using Google Blockly
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Slot, QUrl, QObject
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel


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


class BlocklyWidget(QWidget):
    """Widget containing the Blockly visual programming interface"""

    # Signals
    blocks_modified = Signal()  # Emitted when blocks are modified
    events_generated = Signal(dict)  # Emitted with generated events data
    sync_requested = Signal()  # Emitted when user wants to sync from events panel

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
        self.apply_button = QPushButton("Apply to Events →")
        self.apply_button.setToolTip("Apply block changes to the Events panel")
        self.apply_button.clicked.connect(self.apply_blocks_to_events)
        toolbar.addWidget(self.apply_button)

        # Sync from Events button (Events → Blockly)
        self.sync_button = QPushButton("← Sync from Events")
        self.sync_button.setToolTip("Load events from the Events panel into blocks")
        self.sync_button.clicked.connect(self.request_sync_from_events)
        toolbar.addWidget(self.sync_button)

        # Clear button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_workspace)
        toolbar.addWidget(self.clear_button)

        # Reload button (for debugging/reloading Blockly)
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload_blockly)
        toolbar.addWidget(self.reload_button)

        toolbar.addStretch()

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
        """Load the Blockly HTML file"""
        blockly_html = Path(__file__).parent / "blockly" / "blockly_workspace.html"
        if blockly_html.exists():
            self.web_view.setUrl(QUrl.fromLocalFile(str(blockly_html)))
        else:
            # Try alternate path
            blockly_html = Path("/home/gabe/Dropbox/pygm2/editors/object_editor/blockly/blockly_workspace.html")
            if blockly_html.exists():
                self.web_view.setUrl(QUrl.fromLocalFile(str(blockly_html)))
            else:
                print(f"ERROR: Blockly HTML not found at {blockly_html}")
                self.web_view.setHtml("<h1>Blockly not found</h1><p>Could not load blockly_workspace.html</p>")

    def on_load_finished(self, ok: bool):
        """Handle page load completion"""
        # Show the web view now that it's loaded
        self.web_view.setVisible(True)

        if ok:
            self.update_status("Drag blocks from the toolbox on the left to create game logic!")
        else:
            self.update_status("Error loading Blockly - click Reload to try again")

    def reload_blockly(self):
        """Reload the Blockly workspace"""
        self.update_status("Reloading Blockly...")
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
            self.update_status(f"Blocks updated - {len(self.events_data)} events")
        except json.JSONDecodeError as e:
            print(f"Error parsing blocks JSON: {e}")

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
                self.update_status(f"Applied {len(events)} events")
            except json.JSONDecodeError as e:
                print(f"Error parsing code JSON: {e}")

    def clear_workspace(self):
        """Clear the Blockly workspace"""
        self.web_view.page().runJavaScript("window.blocklyApi.clear()")
        self.events_data = {}
        self.update_status("Workspace cleared")

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
            self.update_status("No events to load")
            return

        # Debug: Print the events data being sent
        print(f"[Blockly] Loading events data: {json.dumps(events_data, indent=2)}")

        # Convert events data to JSON and send to Blockly
        self._loading = True
        events_json = json.dumps(events_data)
        # Escape for JavaScript string - must escape backslashes first, then quotes
        escaped_json = events_json.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")

        def on_load_complete(result):
            self._loading = False
            print(f"[Blockly] Load complete, result: {result}")
            if result is not None:
                self.update_status(f"Loaded {result} events as blocks")
            else:
                self.update_status(f"Loaded {len(events_data)} events - some may not have block equivalents")

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
        pass

    def request_sync_from_events(self):
        """Request sync from events panel (emits signal for parent to handle)"""
        self.update_status("Requesting sync from events...")
        self.sync_requested.emit()


class BlocklyVisualProgrammingTab(QWidget):
    """Complete visual programming tab with Blockly"""

    # Signals
    events_modified = Signal(dict)  # Emitted when events are modified
    sync_requested = Signal()  # Emitted when user wants to sync from events panel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the complete visual programming tab"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Info bar
        info_layout = QHBoxLayout()

        title_label = QLabel("Visual Block Programming")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(title_label)

        info_layout.addStretch()

        help_label = QLabel("Drag blocks from the toolbox on the left to create game logic")
        help_label.setStyleSheet("color: #666; font-style: italic;")
        info_layout.addWidget(help_label)

        layout.addLayout(info_layout)

        # Blockly widget
        self.blockly_widget = BlocklyWidget()
        self.blockly_widget.events_generated.connect(self.on_events_generated)
        self.blockly_widget.blocks_modified.connect(self.on_blocks_modified)
        self.blockly_widget.sync_requested.connect(self.on_sync_requested)
        layout.addWidget(self.blockly_widget)

    def on_events_generated(self, events: dict):
        """Handle events generated from blocks"""
        self.events_modified.emit(events)

    def on_blocks_modified(self):
        """Handle blocks being modified"""
        # Could add auto-save or dirty state tracking here
        pass

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
