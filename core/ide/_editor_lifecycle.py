#!/usr/bin/env python3
"""Editor lifecycle for :class:`PyGameMakerIDE`: open/close/float/reattach
every asset-type editor, plus the composite open-editor key bookkeeping and
the global tabbed/floating window-mode toggle.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2). A mixin -- ``self`` / ``self.tr()`` / siblings resolve on the
concrete window.

``_iter_open_editors`` stays in the shell (shared with ``_assets.py`` and
``_test_game.py``); ``on_room_editor_activated``/``on_object_editor_activated``
and the right-panel/properties-panel helpers (``clear_properties_contexts``,
``_collapse_right_panel``, ``_restore_right_panel``) stay too -- they're a
properties-panel-sync concern driven mainly by ``on_tab_changed``, not
editor-lifecycle tracking, even though one of them (``_collapse_right_panel``)
is called from a method here. ``_add_welcome_tab`` stays in the shell (called
from general UI setup too, not just editor-lifecycle code).

Patch-target move: ``mock.patch('core.ide_window.RoomEditor')`` /
``'core.ide_window.ObjectEditor'`` / ``'core.ide_window.SpriteEditor'`` in
test_reopen_modified_editor.py and test_open_editors_composite_key.py now
target ``core.ide._editor_lifecycle.<Name>`` -- these three editor classes
are constructed directly inside ``open_room_editor``/``open_object_editor``/
``open_sprite_editor``, which move here. The other five ``open_*_editor``
methods import their editor class locally (unaffected).
``QMessageBox`` is used throughout (every ``open_*_editor``'s error path,
plus ``on_editor_save_requested``) but no test patches it for any method
here -- the three existing ``core.ide_window.QMessageBox`` patch sites
(closeEvent, toggle_auto_save, _run_export_with_progress) all belong to
methods elsewhere and are unaffected. ``Config``/``DetachedEditorWindow``
are used but never patched by any test either.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from utils.config import Config
from editors.room_editor import RoomEditor
from editors.object_editor import ObjectEditor
from editors.sprite_editor import SpriteEditor

from core.logger import get_logger
logger = get_logger(__name__)


class EditorLifecycleMixin:

    def close_editor_tab(self, index):
            """Close an editor tab"""
            tab_text = self.editor_tabs.tabText(index).replace('*', '')  # Remove modification indicator

            # Identity check, not title text: the tab is titled with
            # self.tr("Welcome"), so in a translated UI ("Bienvenue", ...) a
            # string guard fails and the welcome tab gets deleteLater()'d,
            # breaking every subsequent project load (audit H1).
            editor_widget = self.editor_tabs.widget(index)
            if editor_widget is not self.welcome_tab:
                # Check if editor has unsaved changes
                if hasattr(editor_widget, 'is_modified') and editor_widget.is_modified:
                    from PySide6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        self, self.tr('Unsaved Changes'),
                        self.tr('"{0}" has unsaved changes. Save before closing?').format(tab_text),
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                    )

                    if reply == QMessageBox.Cancel:
                        return
                    elif reply == QMessageBox.Save:
                        if hasattr(editor_widget, 'save'):
                            if not editor_widget.save():
                                return  # Save failed, don't close

                # Disconnect editor signals before closing to prevent memory leaks
                if editor_widget:
                    # Try to disconnect common editor signals
                    if hasattr(editor_widget, 'save_requested'):
                        self.safe_disconnect_signal(editor_widget.save_requested, self.on_editor_save_requested)
                    if hasattr(editor_widget, 'close_requested'):
                        self.safe_disconnect_signal(editor_widget.close_requested, self.on_editor_close_requested)
                    if hasattr(editor_widget, 'data_modified'):
                        self.safe_disconnect_signal(editor_widget.data_modified, self.on_editor_data_modified)
                    if hasattr(editor_widget, 'float_requested'):
                        self.safe_disconnect_signal(editor_widget.float_requested, self.float_editor)
                    if hasattr(editor_widget, 'reattach_requested'):
                        self.safe_disconnect_signal(editor_widget.reattach_requested, self.reattach_editor)

                    # Disconnect editor-specific signals
                    if hasattr(editor_widget, 'room_editor_activated'):
                        self.safe_disconnect_signal(editor_widget.room_editor_activated, self.on_room_editor_activated)
                    if hasattr(editor_widget, 'object_editor_activated'):
                        self.safe_disconnect_signal(editor_widget.object_editor_activated, self.on_object_editor_activated)

                # Remove from open editors dict by widget identity (the dict is
                # keyed by a composite "<category>:<name>", not the tab text).
                if editor_widget is not None:
                    self._forget_open_editor(editor_widget)

                # Remove tab and schedule widget for deletion to free memory
                self.editor_tabs.removeTab(index)
                if editor_widget:
                    editor_widget.deleteLater()

                # Show welcome tab if no editors left
                if self.editor_tabs.count() == 0:
                    self._add_welcome_tab()

    @staticmethod
    def _canonical_category(category: str) -> str:
        """Normalize singular/plural asset-type vocabulary (the rename signal
        uses 'object', delete uses 'objects') so composite editor keys agree."""
        return {
            'object': 'objects', 'room': 'rooms', 'sprite': 'sprites',
            'script': 'scripts', 'playground': 'playgrounds',
            'sound': 'sounds', 'background': 'backgrounds', 'font': 'fonts',
        }.get(category, category)

    def _editor_key(self, category: str, name: str) -> str:
        """Composite open-editor key: "<category>:<name>" (L5)."""
        return f"{self._canonical_category(category)}:{name}"

    def _open_key(self, editor) -> str:
        """The composite key an editor was registered under (falls back to the
        bare asset_name for any editor opened via an unmigrated path)."""
        return getattr(editor, '_open_editor_key', None) or getattr(editor, 'asset_name', None)

    def _forget_open_editor(self, editor) -> None:
        """Remove an editor from open_editors by identity (key-scheme agnostic)."""
        for k, v in list(self.open_editors.items()):
            if v is editor:
                del self.open_editors[k]

    def open_room_editor(self, room_name: str, room_data: dict):
        """Open a room in the room editor"""

        # Check if room is already open — focus tab or detached window.
        key = self._editor_key('rooms', room_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                # Compare by widget identity, not tab text: a modified editor's
                # tab reads 'name*', so a text match failed exactly when dirty
                # and a duplicate editor was constructed (audit M11).
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            # Create room editor
            room_editor = RoomEditor(str(self.current_project_path), self)

            # Load the room data
            room_editor.load_asset(room_name, room_data)

            # Connect editor signals (using UniqueConnection to prevent duplicates)
            room_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            room_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            room_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            room_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            room_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            # Connect room editor activation signal
            room_editor.room_editor_activated.connect(self.on_room_editor_activated, Qt.ConnectionType.UniqueConnection)

            # Add to tabs
            tab_index = self.editor_tabs.addTab(room_editor, room_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            # Track the editor
            room_editor._open_editor_key = key
            self.open_editors[key] = room_editor

            self.update_status(self.tr("Opened room: {0}").format(room_name))

            # Honor global window mode.
            if self.window_mode == 'floating':
                self.float_editor(room_editor)

        except Exception as e:
            logger.error(f"Error opening room editor: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open room editor: {0}").format(e))

    def open_playground_editor(self, playground_name: str, playground_data: dict):
        """Open a playground in the playground editor"""

        # Check if already open — focus tab or detached window
        key = self._editor_key('playgrounds', playground_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                # Identity, not tab text (a dirty tab reads 'name*') — audit M11.
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            from editors.playground_editor import PlaygroundEditor

            editor = PlaygroundEditor(str(self.current_project_path), self)
            editor.load_asset(playground_name, playground_data)

            # Connect signals
            editor.save_requested.connect(
                self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            editor.close_requested.connect(
                self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            editor.data_modified.connect(
                self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            editor.float_requested.connect(
                self.float_editor, Qt.ConnectionType.UniqueConnection)
            editor.reattach_requested.connect(
                self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            # Add to tabs
            tab_index = self.editor_tabs.addTab(editor, playground_name)
            self.editor_tabs.setCurrentIndex(tab_index)
            editor._open_editor_key = key
            self.open_editors[key] = editor

            self.update_status(self.tr("Opened playground: {0}").format(playground_name))

            # Honor global window mode.
            if self.window_mode == 'floating':
                self.float_editor(editor)

        except Exception as e:
            logger.error(f"Error opening playground editor: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                                 self.tr("Failed to open playground editor: {0}").format(e))

    def open_object_editor(self, object_name: str, object_data: dict):
        """Open an object in the object editor"""

        # Check if object is already open — focus its tab or its detached window
        key = self._editor_key('objects', object_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                # Identity, not tab text (a dirty tab reads 'name*') — audit M11.
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            # Create object editor
            object_editor = ObjectEditor(str(self.current_project_path), self)

            # Load the object data
            object_editor.load_asset(object_name, object_data)

            # Connect editor signals (using UniqueConnection to prevent duplicates)
            object_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            object_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            object_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            object_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            object_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            # Connect object editor activation signal
            object_editor.object_editor_activated.connect(self.on_object_editor_activated, Qt.ConnectionType.UniqueConnection)

            # "Play Object" toolbar button — run this object alone in a
            # throwaway test room (TODO.md's Object test runner item).
            object_editor.test_object_requested.connect(self.test_object, Qt.ConnectionType.UniqueConnection)

            # Add to tabs - object editor occupies full center panel
            tab_index = self.editor_tabs.addTab(object_editor, object_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            # Track the editor
            object_editor._open_editor_key = key
            self.open_editors[key] = object_editor

            # Collapse right panel when object editor is active
            # (Object editor has its own internal properties)
            self._collapse_right_panel()

            self.update_status(self.tr("Opened object: {0}").format(object_name))

            # Honor global window mode — float immediately if that's the
            # current default. Done last so the editor is fully wired up.
            if self.window_mode == 'floating':
                self.float_editor(object_editor)

        except Exception:
            import traceback
            tb = traceback.format_exc()
            traceback.print_exc()
            # Write crash log for GUI-only builds (no console).
            # Swallowed intentionally: we're already in the crash handler;
            # a failure to log the crash must not raise and replace the
            # original traceback shown in the QMessageBox below.
            try:
                from pathlib import Path
                crash_log = Path.home() / 'pygamemaker_crash.log'
                with open(crash_log, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(f"\n{'='*60}\nObject editor crash:\n{tb}\n")
            except Exception:
                pass
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open object editor:\n\n{0}").format(tb))

    def open_sprite_editor(self, sprite_name: str, sprite_data: dict):
        """Open a sprite in the sprite editor"""

        # Check if sprite is already open — focus its tab or its detached window
        key = self._editor_key('sprites', sprite_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                # Identity, not tab text (a dirty tab reads 'name*') — audit M11.
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            sprite_editor = SpriteEditor(str(self.current_project_path), self)
            sprite_editor.load_asset(sprite_name, sprite_data)

            sprite_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            sprite_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            sprite_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            sprite_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            sprite_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            tab_index = self.editor_tabs.addTab(sprite_editor, sprite_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            sprite_editor._open_editor_key = key
            self.open_editors[key] = sprite_editor

            self.update_status(self.tr("Opened sprite: {0}").format(sprite_name))

            # Honor global window mode — float immediately if that's the
            # current default.
            if self.window_mode == 'floating':
                self.float_editor(sprite_editor)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open sprite editor: {0}").format(e))

    def open_script_editor(self, script_name: str, script_data: dict):
        """Open a project-level script in the minimal script editor.

        Mirrors the open_sprite_editor / open_object_editor wiring:
        single tab per asset, same save/close/modified/float signal
        connections, same focus-existing-on-reopen behaviour. The script
        editor itself (editors/script_editor.py) is a thin QPlainTextEdit
        wrapper — see the module docstring for why it's intentionally
        minimal rather than a full code IDE.
        """
        from editors.script_editor import ScriptEditor

        key = self._editor_key('scripts', script_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                # Identity, not tab text (a dirty tab reads 'name*') — audit M11.
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            script_editor = ScriptEditor(str(self.current_project_path), self)
            script_editor.load_asset(script_name, script_data)

            script_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            script_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            script_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            script_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            script_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            tab_index = self.editor_tabs.addTab(script_editor, script_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            script_editor._open_editor_key = key
            self.open_editors[key] = script_editor

            self.update_status(self.tr("Opened script: {0}").format(script_name))

            if self.window_mode == 'floating':
                self.float_editor(script_editor)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open script editor: {0}").format(e))

    def open_sound_editor(self, sound_name: str, sound_data: dict):
        """Open a sound asset in the minimal sound editor (volume/loop form
        + a preview Play button). Mirrors open_script_editor's wiring."""
        from editors.sound_editor import SoundEditor

        key = self._editor_key('sounds', sound_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            sound_editor = SoundEditor(str(self.current_project_path), self)
            sound_editor.load_asset(sound_name, sound_data)

            sound_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            sound_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            sound_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            sound_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            sound_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            tab_index = self.editor_tabs.addTab(sound_editor, sound_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            sound_editor._open_editor_key = key
            self.open_editors[key] = sound_editor

            self.update_status(self.tr("Opened sound: {0}").format(sound_name))

            if self.window_mode == 'floating':
                self.float_editor(sound_editor)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open sound editor: {0}").format(e))

    def open_background_editor(self, background_name: str, background_data: dict):
        """Open a background asset in the minimal background editor (image
        preview + tile-flags form). Mirrors open_script_editor's wiring."""
        from editors.background_editor import BackgroundEditor

        key = self._editor_key('backgrounds', background_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            background_editor = BackgroundEditor(str(self.current_project_path), self)
            background_editor.load_asset(background_name, background_data)

            background_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            background_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            background_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            background_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            background_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            tab_index = self.editor_tabs.addTab(background_editor, background_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            background_editor._open_editor_key = key
            self.open_editors[key] = background_editor

            self.update_status(self.tr("Opened background: {0}").format(background_name))

            if self.window_mode == 'floating':
                self.float_editor(background_editor)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open background editor: {0}").format(e))

    def open_font_editor(self, font_name: str, font_data: dict):
        """Open a font asset in the minimal font editor (family/size/style
        form + a live sample label). Mirrors open_script_editor's wiring."""
        from editors.font_editor import FontEditor

        key = self._editor_key('fonts', font_name)
        if key in self.open_editors:
            if self._focus_detached_editor(key):
                return
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.widget(i) is self.open_editors[key]:
                    self.editor_tabs.setCurrentIndex(i)
                    return

        try:
            font_editor = FontEditor(str(self.current_project_path), self)
            font_editor.load_asset(font_name, font_data)

            font_editor.save_requested.connect(self.on_editor_save_requested, Qt.ConnectionType.UniqueConnection)
            font_editor.close_requested.connect(self.on_editor_close_requested, Qt.ConnectionType.UniqueConnection)
            font_editor.data_modified.connect(self.on_editor_data_modified, Qt.ConnectionType.UniqueConnection)
            font_editor.float_requested.connect(self.float_editor, Qt.ConnectionType.UniqueConnection)
            font_editor.reattach_requested.connect(self.reattach_editor, Qt.ConnectionType.UniqueConnection)

            tab_index = self.editor_tabs.addTab(font_editor, font_name)
            self.editor_tabs.setCurrentIndex(tab_index)

            font_editor._open_editor_key = key
            self.open_editors[key] = font_editor

            self.update_status(self.tr("Opened font: {0}").format(font_name))

            if self.window_mode == 'floating':
                self.float_editor(font_editor)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, self.tr("Error"),
                            self.tr("Failed to open font editor: {0}").format(e))


    def on_editor_save_requested(self, asset_name: str, asset_data: dict):
        """Handle save request from editors"""

        if not self.project_manager:
            logger.error("ERROR: No project manager available")
            return

        try:
            # Determine asset type (PLURAL for category, SINGULAR for asset_type field)
            asset_category = None  # For file structure (plural)
            asset_type_field = None  # For data field (singular)

            if 'instances' in asset_data:  # Room has instances
                asset_category = 'rooms'
                asset_type_field = 'room'
            elif 'events' in asset_data or 'sprite' in asset_data:  # Object has sprite/events
                asset_category = 'objects'
                asset_type_field = 'object'
            elif 'asset_type' in asset_data:
                # Use existing asset_type, derive category
                asset_type_field = asset_data['asset_type']
                # Convert singular to plural for category
                if asset_type_field.endswith('s'):
                    asset_category = asset_type_field
                else:
                    asset_category = asset_type_field + 's'
            else:
                logger.warning("Could not determine asset type")
                return

            logger.debug(f"💾 Saving: category='{asset_category}', type_field='{asset_type_field}'")

            # Ensure required fields with CORRECT singular asset_type
            asset_data['name'] = asset_name
            asset_data['asset_type'] = asset_type_field  # SINGULAR form

            # Re-check the asset's file now that its editor has (re)written it.
            # This heals a stale "(not imported)" / file_missing badge left from
            # a load when the file was still absent — e.g. a sprite whose art
            # was being created. Falls back to marking imported when the asset
            # has no backing file (objects/rooms) or no asset manager is wired.
            if getattr(self, 'asset_manager', None):
                self.asset_manager.revalidate_asset_import_state(asset_data)
            else:
                asset_data['imported'] = True

            # Debug: Print what we're about to save
            if asset_category == 'rooms':
                logger.debug(f"💾 Room data keys: {list(asset_data.keys())}")
                logger.debug(f"💾 Background color: {asset_data.get('background_color', 'NOT SET')}")
                logger.debug(f"💾 Instances count: {len(asset_data.get('instances', []))}")

            # Use the project manager's update method with PLURAL category
            if self.project_manager.update_asset(asset_category, asset_name, asset_data):
                pass  # Success
            else:
                logger.error(f"Failed to update asset {asset_name}")
                return

            # Force immediate save
            if self.project_manager.save_project():
                # Update our local copy
                self.current_project_data = self.project_manager.get_current_project_data()

                # Update UI
                self.update_status(f"Saved: {asset_name}")
                self.update_window_title()

                # Refresh asset tree
                self.asset_tree.refresh_from_project(self.current_project_data)

                # Refresh properties panel sprite combo
                if hasattr(self.properties_panel, 'refresh_sprite_combo'):
                    self.properties_panel.refresh_sprite_combo()

                # Clear the tab asterisk to show save completed
                for i in range(self.editor_tabs.count()):
                    tab_text = self.editor_tabs.tabText(i)
                    if tab_text == asset_name + '*':
                        self.editor_tabs.setTabText(i, asset_name)
                        break

                # Broadcast so any *other* open editor (including floated
                # ones) refreshes its asset dropdowns. Cheap and idempotent.
                self._refresh_blockly_asset_lists()

                # A sprite save (new art, frame count, or an origin_x/
                # origin_y change) previously left every already-open room
                # editor's RoomCanvas.sprite_cache/origin_cache holding
                # stale data for any object using this sprite -- only an
                # object's sprite *assignment* changing (object editor)
                # triggered this refresh, not the sprite's own metadata
                # changing underneath it. refresh_object_sprites' real work
                # is a full RoomCanvas.set_project_info() re-point (which
                # clears both caches); the object_name arg only drives an
                # already-redundant single-key eviction, so reusing it here
                # with the sprite's own name is safe.
                if asset_category == 'sprites':
                    self.refresh_object_sprites(asset_name, None, None)

                logger.info(f"✅ Save completed successfully for {asset_name}")

            else:
                logger.error("Project save FAILED")
                QMessageBox.warning(self, self.tr("Save Error"),
                                  self.tr("Failed to save project to disk"))
                return

        except Exception as e:
            logger.error(f"Error in save: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, self.tr("Save Error"),
                              self.tr("Failed to save {0}: {1}").format(asset_name, e))

    def on_editor_close_requested(self, asset_name: str):
        """Handle close request from editors.

        ``close_requested`` carries the bare asset_name, but ``open_editors``
        (and ``detached_editor_windows``) are keyed by the L5 composite
        "<category>:<name>" key. Resolve the emitting editor's real key via
        ``_open_key`` instead of passing the bare name, which silently missed
        the composite-keyed registries and left the editor open.
        """
        editor = self.sender()
        if editor is not None and (getattr(editor, '_open_editor_key', None)
                                   or getattr(editor, 'asset_name', None)):
            self.close_editor_by_name(self._open_key(editor))
            return
        # Defensive fallback (e.g. a direct, non-signal call where sender() is
        # unavailable): match an open editor by its asset_name.
        for key, open_editor in self.open_editors.items():
            if getattr(open_editor, 'asset_name', None) == asset_name:
                self.close_editor_by_name(key)
                return
        self.close_editor_by_name(asset_name)

    def _flush_open_editors(self):
        """Push every open editor's live data into the project (same sync the
        Test Game path uses). Run before tearing editors down on project
        switch / IDE-close 'Save' so unsaved in-editor work isn't silently
        discarded (audit M12). Covers both tabbed and detached editors."""
        for widget in self._iter_open_editors():
            if hasattr(widget, 'get_data') and hasattr(widget, 'asset_name') and widget.asset_name:
                try:
                    self.on_editor_save_requested(widget.asset_name, widget.get_data())
                except Exception as e:
                    logger.debug(f"Could not flush editor {getattr(widget, 'asset_name', '?')}: {e}")

    def on_editor_data_modified(self, asset_name: str):
        """Handle data modification in editors"""
        # Update tab title to show modification
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i) == asset_name:
                if not self.editor_tabs.tabText(i).endswith('*'):
                    self.editor_tabs.setTabText(i, asset_name + '*')
                break

        # Reflect editor-local edits in the project's dirty state so the
        # IDE-close 'Unsaved Changes' prompt fires for editor-only changes —
        # previously is_modified was consulted only by close_editor_tab, so
        # closing the IDE (or switching projects) silently discarded them
        # (audit M12).
        if getattr(self, 'project_manager', None):
            self.project_manager.mark_dirty()

        # NOTE: Do NOT refresh the properties panel here.
        # Calling show_asset_properties triggers widget signal changes which
        # feed back into the editor (mark_modified → data_modified → here),
        # creating an infinite auto-save loop.  The properties panel is already
        # populated when the editor tab is selected.

    def close_editor_by_name(self, key: str):
        """Close an editor by its composite open-editor key (handles tabbed and
        detached editors)."""
        # Detached path: tear down the floating window and drop the editor.
        if key in self.detached_editor_windows:
            self._destroy_detached_editor(key)
            return
        editor = self.open_editors.get(key)
        if editor is None:
            return
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.widget(i) is editor:
                self.close_editor_tab(i)
                return

    def _focus_detached_editor(self, asset_name: str) -> bool:
        """If the editor is currently floated, raise its window. Returns True
        if a detached window was found and focused."""
        window = self.detached_editor_windows.get(asset_name)
        if window is None:
            return False
        window.showNormal()
        window.raise_()
        window.activateWindow()
        return True

    def float_editor(self, editor):
        """Pop an editor out of the tab strip into its own floating window."""
        from editors.detached_editor_window import DetachedEditorWindow

        asset_name = getattr(editor, "asset_name", None)
        if not asset_name:
            logger.warning("float_editor called on editor with no asset_name")
            return
        key = self._open_key(editor)
        if key in self.detached_editor_windows:
            self._focus_detached_editor(key)
            return

        # Find and remove the tab without going through close_editor_tab
        # (which would prompt about unsaved changes).
        tab_index = -1
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.widget(i) is editor:
                tab_index = i
                break
        if tab_index >= 0:
            self.editor_tabs.removeTab(tab_index)

        # Build the floating window. Keep the IDE as logical parent so the
        # window inherits stylesheet/icons but stays independently movable.
        window = DetachedEditorWindow(editor, parent=self)
        window.reattach_requested.connect(self._on_detached_reattach_requested)
        self.detached_editor_windows[key] = window

        if hasattr(editor, "set_floating_state"):
            editor.set_floating_state(True)

        window.show()
        window.raise_()
        window.activateWindow()

        # If the tab strip is now empty, restore the welcome tab so the
        # center panel doesn't look broken.
        if self.editor_tabs.count() == 0:
            self._add_welcome_tab()

        self.update_status(self.tr("Floated: {0}").format(asset_name))

    def reattach_editor(self, editor):
        """Move a floated editor back into the tab strip."""
        key = self._open_key(editor)
        if not key:
            return
        window = self.detached_editor_windows.get(key)
        if window is None:
            return
        # Closing the window triggers _on_detached_reattach_requested below.
        window.close()

    def _on_detached_reattach_requested(self, editor):
        """The detached window is closing — pull the editor back into a tab."""
        key = self._open_key(editor)
        if not key:
            return

        window = self.detached_editor_windows.pop(key, None)
        if window is not None:
            taken = window.take_editor()
            if taken is not None:
                editor = taken
            window.deleteLater()

        # Tab label uses the bare asset name, not the composite key.
        asset_name = getattr(editor, "asset_name", key)

        # Drop the welcome tab if it's the only thing showing — we're about
        # to replace it with the real editor.
        if (self.editor_tabs.count() == 1
                and self.editor_tabs.widget(0) is self.welcome_tab):
            self.editor_tabs.removeTab(0)

        tab_index = self.editor_tabs.addTab(editor, asset_name)
        self.editor_tabs.setCurrentIndex(tab_index)

        if hasattr(editor, "set_floating_state"):
            editor.set_floating_state(False)

        self.update_status(self.tr("Reattached: {0}").format(asset_name))

    def toggle_window_mode(self):
        """Flip between global tabbed / floating mode and apply immediately."""
        new_mode = 'floating' if self.window_mode == 'tabbed' else 'tabbed'
        self.set_window_mode(new_mode)

    def set_window_mode(self, mode: str):
        """Set global window mode and apply it to all currently open editors.

        ``mode='tabbed'`` reattaches every floating editor (the recovery path
        when a window has been dragged off-screen). ``mode='floating'`` pops
        every tabbed editor out into its own window.
        """
        if mode not in ('tabbed', 'floating'):
            return
        self.window_mode = mode
        Config.set('window_mode', mode)
        self._update_window_mode_action_label()

        if mode == 'tabbed':
            # Reattach every detached editor. close() routes through
            # _on_detached_reattach_requested which puts the editor back.
            for asset_name in list(self.detached_editor_windows.keys()):
                window = self.detached_editor_windows.get(asset_name)
                if window is not None:
                    window.close()
            self.update_status(self.tr("Window mode: Tabbed"))
        else:
            # Float every editor currently in the tab strip.
            to_float = []
            for i in range(self.editor_tabs.count()):
                widget = self.editor_tabs.widget(i)
                if widget is None or widget is self.welcome_tab:
                    continue
                if hasattr(widget, 'asset_name') and widget.asset_name:
                    to_float.append(widget)
            for editor in to_float:
                self.float_editor(editor)
            self.update_status(self.tr("Window mode: Floating"))

    def _update_window_mode_action_label(self):
        """Sync the toolbar action's label and tooltip to the current mode."""
        if not hasattr(self, 'window_mode_action'):
            return
        if self.window_mode == 'floating':
            self.window_mode_action.setText(self.tr("⧉ Floating"))
            self.window_mode_action.setToolTip(self.tr(
                "Window mode: Floating. Click to switch all editors back into tabs "
                "(use this if a floating window has been dragged off-screen)."
            ))
        else:
            self.window_mode_action.setText(self.tr("⊞ Tabbed"))
            self.window_mode_action.setToolTip(self.tr(
                "Window mode: Tabbed. Click to pop every editor out into its own window."
            ))

    def _destroy_detached_editor(self, asset_name: str):
        """Fully close a floated editor (used by close_editor_by_name and
        project teardown — bypasses the reattach path)."""
        window = self.detached_editor_windows.pop(asset_name, None)
        editor = self.open_editors.pop(asset_name, None)
        if window is not None:
            window.reattach_on_close = False
            # take_editor() unparents the editor so deleteLater on the
            # window doesn't take the editor down with it before we get a
            # chance to disconnect signals.
            window.take_editor()
            window.close()
            window.deleteLater()
        if editor is not None:
            try:
                if hasattr(editor, 'save_requested'):
                    self.safe_disconnect_signal(editor.save_requested, self.on_editor_save_requested)
                if hasattr(editor, 'close_requested'):
                    self.safe_disconnect_signal(editor.close_requested, self.on_editor_close_requested)
                if hasattr(editor, 'data_modified'):
                    self.safe_disconnect_signal(editor.data_modified, self.on_editor_data_modified)
                if hasattr(editor, 'float_requested'):
                    self.safe_disconnect_signal(editor.float_requested, self.float_editor)
                if hasattr(editor, 'reattach_requested'):
                    self.safe_disconnect_signal(editor.reattach_requested, self.reattach_editor)
            except Exception:
                logger.debug(
                    "editor teardown: signal disconnect raised", exc_info=True
                )
            editor.deleteLater()
