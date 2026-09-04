#!/usr/bin/env python3
"""Asset create / import / rename / delete for :class:`PyGameMakerIDE`.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2). A mixin -- ``self`` / ``self.tr()`` / siblings
(``_iter_open_editors`` stays in the shell; the ``open_*_editor`` methods
go to ``_editor_lifecycle``) resolve on the concrete window.

No patch targets move: the block references ``ObjectEditor`` only as a
``__class__.__name__`` string; ``ResourcePackager`` / ``RobertaImporter`` /
``GMKConverter`` are lazy imports that travel with their methods; and no
test patches ``core.ide_window.<NAME>`` while exercising an asset method.
"""

import json
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QDialog

from core.logger import get_logger

logger = get_logger(__name__)


class AssetsMixin:

    def import_object_package(self):
        """Import an object package"""
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import Object Package"),
            str(Path.home()),
            self.tr("GameMaker Objects (*.gmobj)")
        )

        if file_path:
            from utils.resource_packager import ResourcePackager

            self.update_status(self.tr("Importing object..."))

            # Flush unsaved in-memory changes first: the importer read-modify-
            # writes the on-disk project.json and we reload from disk after, so
            # without this any edits since the last save are silently lost (L2).
            if getattr(self.project_manager, 'is_dirty_flag', False):
                self.project_manager.save_project()

            object_name = ResourcePackager.import_object(
                Path(file_path),
                self.current_project_path
            )

            if object_name:
                # import_object wrote the new object to project.json on disk
                # only. Fold it into the live model and redraw the tree, rather
                # than a full load_project() reload (which tears down open
                # editors and, if the project is dirty, would first save the
                # stale in-memory data back over the freshly-imported file).
                self.asset_tree.force_project_refresh(merge_from_disk=True)

                QMessageBox.information(
                    self,
                    self.tr("Import Successful"),
                    self.tr("Object '{0}' imported successfully!").format(object_name)
                )
                self.update_status(self.tr("Object imported: {0}").format(object_name))
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Import Failed"),
                    self.tr("Failed to import object package")
                )
                self.update_status(self.tr("Import failed"))

    def import_room_package(self):
        """Import a room package"""
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import Room Package"),
            str(Path.home()),
            self.tr("GameMaker Rooms (*.gmroom)")
        )

        if file_path:
            from utils.resource_packager import ResourcePackager

            self.update_status(self.tr("Importing room..."))

            # Flush unsaved changes first (see import object package, L2).
            if getattr(self.project_manager, 'is_dirty_flag', False):
                self.project_manager.save_project()

            room_name = ResourcePackager.import_room(
                Path(file_path),
                self.current_project_path
            )

            if room_name:
                # import_room wrote the new room to project.json on disk only.
                # Fold it into the live model and redraw the tree, rather than a
                # full load_project() reload (which tears down open editors and,
                # if the project is dirty, would first save the stale in-memory
                # data back over the freshly-imported file).
                self.asset_tree.force_project_refresh(merge_from_disk=True)

                QMessageBox.information(
                    self,
                    self.tr("Import Successful"),
                    self.tr("Room '{0}' imported successfully!").format(room_name)
                )
                self.update_status(self.tr("Room imported: {0}").format(room_name))
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Import Failed"),
                    self.tr("Failed to import room package")
                )
                self.update_status(self.tr("Import failed"))

    def import_roberta_xml(self):
        """Import an Open Roberta Lab XML program as a new project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import Open Roberta XML"),
            str(Path.home()),
            self.tr("Open Roberta XML (*.xml)")
        )

        if not file_path:
            return

        # Ask user where to save the new project
        output_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Output Directory for Imported Project"),
            str(Path.home())
        )

        if not output_dir:
            return

        from importers.roberta_importer import import_roberta_detailed, RobertaImportError

        self.update_status(self.tr("Importing Open Roberta program..."))

        try:
            result = import_roberta_detailed(file_path, output_dir)

            # Show warnings if any
            warning_text = ""
            if result.warnings:
                warning_text = self.tr("\n\nWarnings:\n") + "\n".join(
                    f"  - {w}" for w in result.warnings[:20])

            QMessageBox.information(
                self,
                self.tr("Import Successful"),
                self.tr("Project '{0}' imported successfully!\n"
                         "Events: {1}, Actions: {2}{3}").format(
                    result.project_name,
                    result.events_imported,
                    result.actions_imported,
                    warning_text)
            )
            self.update_status(self.tr("Roberta import complete: {0}").format(result.project_name))

            # Open the newly imported project
            project_file = Path(output_dir) / "project.json"
            if project_file.exists():
                self.load_project(Path(output_dir))

        except RobertaImportError as exc:
            QMessageBox.warning(
                self,
                self.tr("Import Failed"),
                self.tr("Failed to import Open Roberta XML:\n{0}").format(str(exc))
            )
            self.update_status(self.tr("Roberta import failed"))

    def import_gmk_file(self):
        """Import a legacy GameMaker 8.0/8.1 .gmk file as a new project."""
        gmk_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import GameMaker File"),
            str(Path.home()),
            self.tr("GameMaker Files (*.gmk)")
        )
        if not gmk_path:
            return

        gmk_file = Path(gmk_path)
        # Default output: a sibling folder named after the .gmk stem.
        # Picks a non-clashing sibling if one already exists, so grading multiple
        # submissions in the same folder doesn't silently overwrite anything.
        default_parent = gmk_file.parent
        candidate = default_parent / gmk_file.stem
        suffix = 2
        while candidate.exists() and any(candidate.iterdir()):
            candidate = default_parent / f"{gmk_file.stem}_{suffix}"
            suffix += 1
        output_dir = candidate

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(
                self,
                self.tr("Import Failed"),
                self.tr("Could not create output folder:\n{0}").format(str(exc))
            )
            return

        from importers.gmk_importer import import_gmk_detailed

        self.update_status(self.tr("Importing GameMaker file..."))
        result = import_gmk_detailed(str(gmk_file), str(output_dir))

        if not result.success:
            warning_text = "\n".join(f"  - {w}" for w in result.warnings[:20]) or self.tr("(no details)")
            QMessageBox.warning(
                self,
                self.tr("Import Failed"),
                self.tr("Failed to import {0}:\n\n{1}").format(gmk_file.name, warning_text)
            )
            self.update_status(self.tr("GMK import failed"))
            return

        stats_text = ", ".join(f"{k}: {v}" for k, v in result.stats.items() if v > 0) or self.tr("(empty project)")
        warning_text = ""
        if result.warnings:
            shown = "\n".join(f"  - {w}" for w in result.warnings[:20])
            extra = self.tr("\n  ...and {0} more").format(len(result.warnings) - 20) if len(result.warnings) > 20 else ""
            warning_text = self.tr("\n\nWarnings:\n") + shown + extra

        QMessageBox.information(
            self,
            self.tr("Import Successful"),
            self.tr("Imported '{0}' to:\n{1}\n\n{2}{3}").format(
                gmk_file.name, str(output_dir), stats_text, warning_text)
        )
        self.update_status(self.tr("GMK import complete: {0}").format(gmk_file.stem))

        if (output_dir / "project.json").exists():
            self.load_project(output_dir)

    def import_sprite(self):
        # Add the project check
        if not getattr(self, 'current_project_path', None):
            from PySide6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                self.tr("No Project Loaded"),
                self.tr("You need to create or open a project before importing sprites.\n\n"
                    "Would you like to create a new project now?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.new_project()
            else:
                logger.debug("🔥 User cancelled")
            return

        self.import_asset("sprites")

    def import_sound(self):
        if not self.ensure_project_loaded("importing sounds"):
            return
        self.import_asset("sounds")

    def import_background(self):
        if not self.ensure_project_loaded("importing backgrounds"):
            return
        self.import_asset("backgrounds")

    def import_asset(self, asset_type):
        if not self.current_project_path:
            return

        try:
            dialog = ImportAssetDialog(asset_type, self)

            if dialog.exec() == QDialog.Accepted:
                files = dialog.get_selected_files()

                if files:
                    self.asset_tree.import_asset(files, asset_type, self.current_project_path)
                else:
                    logger.debug("No files selected")
            else:
                logger.debug("Import cancelled")

        except Exception as e:
            logger.error(f"Error in import_asset: {e}")

    def on_asset_renamed(self, old_name, new_name, asset_type):
            """Handle asset rename signal - refresh UI components"""
            try:

                # Update properties panel if it's showing the renamed asset
                if hasattr(self, 'properties_panel') and self.properties_panel:
                    # Check if properties panel is currently showing the renamed asset
                    if hasattr(self.properties_panel, 'name_edit'):
                        current_displayed_name = self.properties_panel.name_edit.text()

                        if current_displayed_name == old_name:

                            # Find the updated asset data in the tree
                            updated_asset_item = self.find_renamed_asset(new_name, asset_type)
                            if updated_asset_item and hasattr(updated_asset_item, 'asset_data'):
                                # Refresh the properties panel with new data
                                self.properties_panel.set_asset(updated_asset_item.asset_data)

                # Sync in-memory project data from asset manager cache
                if hasattr(self, 'project_manager') and self.project_manager:
                    if hasattr(self.project_manager, 'asset_manager') and self.project_manager.asset_manager:
                        cache = self.project_manager.asset_manager.assets_cache
                        if self.current_project_data and 'assets' in self.current_project_data:
                            for cat_name, cat_data in cache.items():
                                self.current_project_data['assets'][cat_name] = cat_data

                # When an object is renamed, update all open editors (tabbed
                # AND detached) — palettes, room instance references, and
                # other editors' events panels.
                if asset_type == 'object':
                    for widget in self._iter_open_editors():
                        if hasattr(widget, 'rename_object_in_instances'):
                            widget.rename_object_in_instances(old_name, new_name)
                        if hasattr(widget, 'load_available_objects'):
                            widget.load_available_objects()
                        # Reload open object editors whose events were updated
                        if hasattr(widget, 'events_panel') and widget.events_panel:
                            if hasattr(widget, 'load_asset_data') and hasattr(widget, 'asset_name'):
                                obj_data = self.current_project_data.get('assets', {}).get('objects', {}).get(widget.asset_name)
                                if obj_data:
                                    widget.events_panel.load_events_data(obj_data.get('events', {}))

                # If the renamed asset itself is open as an editor, update
                # its asset_name and propagate to dicts / tab text / window
                # title so the IDE doesn't keep stale references.
                old_key = self._editor_key(asset_type, old_name)
                if old_key in self.open_editors:
                    new_key = self._editor_key(asset_type, new_name)
                    editor = self.open_editors.pop(old_key)
                    editor._open_editor_key = new_key
                    self.open_editors[new_key] = editor
                    if hasattr(editor, 'asset_name'):
                        editor.asset_name = new_name
                    # If currently floated, move the window registration too.
                    if old_key in self.detached_editor_windows:
                        self.detached_editor_windows[new_key] = self.detached_editor_windows.pop(old_key)
                    # Refresh window title if the editor knows how.
                    if hasattr(editor, 'update_window_title'):
                        try:
                            editor.update_window_title()
                        except Exception:
                            logger.debug(
                                "rename: editor.update_window_title() raised",
                                exc_info=True,
                            )
                    # Update tab text if the editor is in a tab.
                    for i in range(self.editor_tabs.count()):
                        if self.editor_tabs.widget(i) is editor:
                            self.editor_tabs.setTabText(i, new_name)
                            break

                # Refresh asset dropdowns in any open Blockly tab so the new
                # name shows up immediately (works for any asset_type).
                self._refresh_blockly_asset_lists()

            except Exception as e:
                logger.error(f"❌ Error handling asset rename in main window: {e}")

    def _refresh_blockly_asset_lists(self):
        """Push fresh asset-name lists to every open Blockly editor (tabbed
        and floated)."""
        try:
            for widget in self._iter_open_editors():
                blockly_tab = getattr(widget, 'blockly_tab', None)
                if blockly_tab and hasattr(blockly_tab, 'push_asset_lists'):
                    blockly_tab.push_asset_lists()
        except Exception as e:
            logger.debug(f"Could not refresh Blockly asset lists: {e}")

    def find_renamed_asset(self, asset_name, asset_type):
        """Find an asset item by name and type in the asset tree"""
        try:
            if not hasattr(self, 'asset_tree'):
                return None

            # Search through the asset tree
            root = self.asset_tree.invisibleRootItem()

            for i in range(root.childCount()):
                category_item = root.child(i)

                # Check if this is the right category
                category_text = category_item.text(0).lower()
                expected_category = asset_type.lower() + 's'  # sprites, sounds, etc.

                if category_text == expected_category:
                    # Search through assets in this category
                    for j in range(category_item.childCount()):
                        asset_item = category_item.child(j)

                        if (hasattr(asset_item, 'asset_data') and
                            asset_item.asset_data.get('name') == asset_name):
                            return asset_item

            return None

        except Exception as e:
            logger.error(f"❌ Error finding renamed asset: {e}")
            return None

    def on_asset_deleted(self, asset_type: str, asset_name: str):
        """Handle asset deletion - update open editors that reference the deleted asset"""
        try:
            logger.debug(f"🗑️ IDE: Asset deleted - {asset_type}/{asset_name}")

            # If a sprite was deleted, refresh all open object editors
            if asset_type == "sprites":
                for editor_name, editor in self.open_editors.items():
                    if hasattr(editor, '__class__') and editor.__class__.__name__ == 'ObjectEditor':
                        # Reload sprites in the object editor
                        if hasattr(editor, 'load_project_assets'):
                            editor.load_project_assets()
                            logger.debug(f"🔄 Refreshed sprites in object editor: {editor_name}")

                        # If this object was using the deleted sprite, update its data
                        if hasattr(editor, 'current_object_properties'):
                            if editor.current_object_properties.get('sprite') == asset_name:
                                editor.current_object_properties['sprite'] = ''
                                # Refresh the properties panel to show "None"
                                if hasattr(editor, 'properties_panel'):
                                    editor.properties_panel.load_properties(editor.current_object_properties)
                                logger.debug(f"🔄 Cleared sprite reference in object: {editor_name}")

            # If an object was deleted and it's open, close its editor. Use the
            # composite key so deleting object 'X' can't close a same-named room
            # editor (L5).
            elif asset_type == "objects":
                key = self._editor_key('objects', asset_name)
                if key in self.open_editors:
                    self.close_editor_by_name(key)
                    logger.debug(f"🔄 Closed deleted object's editor: {asset_name}")

            # Refresh asset dropdowns in any open Blockly tab so the deleted
            # name disappears from the lists.
            self._refresh_blockly_asset_lists()

        except Exception as e:
            logger.error(f"❌ Error handling asset deletion: {e}")
            import traceback
            traceback.print_exc()

    def create_object(self):
        if not self.ensure_project_loaded("creating objects"):
            return
        self.create_asset("objects")

    def create_room(self):
        if not self.ensure_project_loaded("creating rooms"):
            return
        self.create_asset("rooms")

    def create_script(self):
        if not self.ensure_project_loaded("creating scripts"):
            return
        self.create_asset("scripts")

    def create_font(self):
        if not self.ensure_project_loaded("creating fonts"):
            return
        self.create_asset("fonts")

    def create_asset(self, asset_type):
        if not self.current_project_path:
            QMessageBox.information(self, self.tr("No Project"), self.tr("Please open a project first"))
            return

        # Get asset name from user
        asset_type_singular = asset_type[:-1]  # Remove 's'
        asset_type_title = asset_type_singular.title()

        name, ok = QInputDialog.getText(
            self, self.tr("Create {0}").format(asset_type_title),
            self.tr("Enter name for new {0}:").format(asset_type_singular)
        )

        if not ok or not name:
            return

        # Create the asset data directly
        self.create_asset_with_data(asset_type, name)

    def create_asset_with_data(self, asset_type: str, asset_name: str):
        """Create asset with proper data structure and save to project"""
        try:
            # Create default asset data based on type
            if asset_type == 'rooms':
                asset_data = {
                    'name': asset_name,
                    'width': 1024,
                    'height': 768,
                    'background_color': '#87CEEB',
                    'views_enabled': False,
                    'instances': [],
                    'asset_type': 'room',
                    'imported': True
                }
            elif asset_type == 'objects':
                asset_data = {
                    'name': asset_name,
                    'sprite': '',
                    'visible': True,
                    'solid': False,
                    'persistent': False,
                    'asset_type': 'object',
                    'imported': True,
                    'events': {}
                }
            elif asset_type == 'playgrounds':
                asset_data = {
                    'name': asset_name,
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
            else:
                # Generic asset data
                asset_data = {
                    'name': asset_name,
                    'asset_type': asset_type[:-1],
                    'imported': True
                }

            # Add to project data
            if not self.current_project_data:
                logger.warning("No project data available")
                return

            assets = self.current_project_data.setdefault('assets', {})
            asset_category = assets.setdefault(asset_type, {})
            asset_category[asset_name] = asset_data

            # IMPORTANT: Also add to asset_manager's cache so it persists on save
            # The save_project() method uses assets_cache to write project data,
            # so if we only add to current_project_data, the asset gets lost on save
            if self.project_manager and self.project_manager.asset_manager:
                cache = self.project_manager.asset_manager.assets_cache
                if asset_type not in cache:
                    from collections import OrderedDict
                    cache[asset_type] = OrderedDict()
                cache[asset_type][asset_name] = asset_data
                logger.debug(f"✅ Added {asset_name} to asset_manager cache")

            # Mark project as dirty and save
            self.project_manager.mark_dirty()

            # Update the asset tree
            self.asset_tree.add_asset(asset_type, asset_name, asset_data)

            # Save the project immediately to persist the new asset
            if self.project_manager.save_project():
                self.update_status(self.tr("Created {0}").format(asset_name))

                # Refresh any open room editors' object palette when a new object is created
                if asset_type == 'objects':
                    self._refresh_room_editor_objects()

                # Push the new asset name into Blockly dropdowns of any open editor.
                self._refresh_blockly_asset_lists()
            else:
                logger.error(f"Failed to save project after creating {asset_name}")

        except Exception as e:
            logger.error(f"Error creating {asset_type[:-1]}: {e}")
            QMessageBox.warning(self, self.tr("Error"),
                            self.tr("Failed to create {0}: {1}").format(asset_type[:-1], e))

    def _refresh_room_editor_objects(self):
        """Refresh the object palette in any open room editors"""
        try:
            for i in range(self.editor_tabs.count()):
                widget = self.editor_tabs.widget(i)
                if hasattr(widget, 'load_available_objects'):
                    widget.load_available_objects()
                    logger.debug(f"✅ Refreshed object palette in room editor tab {i}")
        except Exception as e:
            logger.warning(f"⚠️ Could not refresh room editor objects: {e}")

    def on_asset_selected(self, asset_data):
        self.properties_panel.set_asset(asset_data)

    def on_asset_imported(self, asset_name, asset_type, asset_data):
        """Handle asset import with correct signal signature"""
        logger.debug(f"📥 on_asset_imported called: {asset_type}/{asset_name}")
        self.update_status(self.tr("Imported {0}").format(asset_name))

        # Update current_project_data with the new asset
        if self.current_project_data is not None:
            if 'assets' not in self.current_project_data:
                self.current_project_data['assets'] = {}
            if asset_type not in self.current_project_data['assets']:
                self.current_project_data['assets'][asset_type] = {}
            self.current_project_data['assets'][asset_type][asset_name] = asset_data

        # Refresh sprite combo if it's a sprite import
        if asset_type == 'sprites':
            if hasattr(self, 'properties_panel') and hasattr(self.properties_panel, 'refresh_sprite_combo'):
                self.properties_panel.refresh_sprite_combo()
                logger.debug(f"Refreshed sprite combo after importing {asset_name}")

            # Also refresh open object editors so they see the new sprite
            logger.debug("🔄 Refreshing open object editors after sprite import...")
            self.refresh_open_object_editors()

        # Push new asset name into Blockly dropdowns for any open editor.
        self._refresh_blockly_asset_lists()

    def on_asset_double_clicked(self, asset_data):
        """Handle double-click on assets to open in appropriate editor"""
        asset_type = asset_data.get('asset_type', '')
        asset_name = asset_data.get('name', '')
        asset_info = asset_data.get('data', {})

        if asset_type == 'rooms':
            self.open_room_editor(asset_name, asset_info)
        elif asset_type == 'objects':
            self.open_object_editor(asset_name, asset_info)
        elif asset_type == 'sprites':
            self.open_sprite_editor(asset_name, asset_info)
        elif asset_type == 'playgrounds':
            self.open_playground_editor(asset_name, asset_info)
        elif asset_type == 'scripts':
            self.open_script_editor(asset_name, asset_info)
        elif asset_type == 'sounds':
            self.open_sound_editor(asset_name, asset_info)
        elif asset_type == 'backgrounds':
            self.open_background_editor(asset_name, asset_info)
        elif asset_type == 'fonts':
            self.open_font_editor(asset_name, asset_info)
        else:
            logger.warning(f"No editor registered for asset type '{asset_type}' (asset: {asset_name})")
