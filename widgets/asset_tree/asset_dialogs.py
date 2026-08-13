#!/usr/bin/env python3
"""
Asset Dialogs for PyGameMaker IDE
UI dialogs for asset management operations
"""

from pathlib import Path

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QLabel, QMessageBox, QListWidget,
                               QListWidgetItem, QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt

from .asset_utils import validate_asset_name
from ..qt_helpers import as_hashable_tuple


class AssetRenameDialog(QDialog):
    """Dialog for renaming assets"""

    def __init__(self, current_name: str, asset_type: str, parent=None):
        super().__init__(parent)
        self.current_name = current_name
        self.asset_type = asset_type
        self.new_name = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the rename dialog UI"""
        self.setWindowTitle(self.tr("Rename {0}").format(self.asset_type.title()))
        self.setFixedSize(400, 180)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Current name label
        current_label = QLabel(self.tr("Current name: <b>{0}</b>").format(self.current_name))
        layout.addWidget(current_label)

        # New name input
        name_label = QLabel(self.tr("New name:"))
        layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setText(self.current_name)
        self.name_edit.selectAll()
        self.name_edit.setFocus()
        layout.addWidget(self.name_edit)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.rename_btn = QPushButton(self.tr("Rename"))
        self.rename_btn.clicked.connect(self.accept_rename)
        self.rename_btn.setDefault(True)
        button_layout.addWidget(self.rename_btn)

        layout.addLayout(button_layout)

        # Connect Enter key to rename
        self.name_edit.returnPressed.connect(self.accept_rename)

        # Validate input as user types
        self.name_edit.textChanged.connect(self.validate_name)

    def validate_name(self, text: str):
        """Validate the new name as user types"""
        # Remove leading/trailing whitespace
        text = text.strip()

        # Use utility function for validation
        is_valid, error_msg = validate_asset_name(text)

        # Check if name changed
        if text == self.current_name:
            self.rename_btn.setEnabled(False)
            return

        self.rename_btn.setEnabled(is_valid)

    def accept_rename(self):
        """Accept the rename if valid"""
        new_name = self.name_edit.text().strip()

        # Final validation
        is_valid, error_msg = validate_asset_name(new_name)

        if not is_valid:
            QMessageBox.warning(self, self.tr("Invalid Name"), error_msg)
            return

        if new_name == self.current_name:
            self.reject()
            return

        self.new_name = new_name
        self.accept()


class AssetPropertiesDialog(QDialog):
    """Dialog for viewing/editing detailed asset properties"""

    def __init__(self, asset_data: dict, parent=None):
        super().__init__(parent)
        self.asset_data = asset_data
        self.setup_ui()

    def setup_ui(self):
        """Setup the properties dialog UI"""
        asset_name = self.asset_data.get('name', 'Unknown')
        asset_type = self.asset_data.get('asset_type', 'Unknown')

        self.setWindowTitle(self.tr("{0} Properties - {1}").format(asset_type.title(), asset_name))
        self.setFixedSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Asset info
        info_label = QLabel(f"<h3>{asset_name}</h3>")
        layout.addWidget(info_label)

        type_label = QLabel(self.tr("Type: {0}").format(asset_type))
        layout.addWidget(type_label)

        # File path info
        if 'project_path' in self.asset_data:
            path_label = QLabel(self.tr("File: {0}").format(self.asset_data['project_path']))
            layout.addWidget(path_label)

        # Import status
        imported = self.asset_data.get('imported', False)
        status_text = self.tr("Imported") if imported else self.tr("Not imported")
        status_label = QLabel(self.tr("Status: {0}").format(status_text))
        layout.addWidget(status_label)

        # Import button for sprites without images
        if asset_type == "sprite" and not imported:
            import_button_layout = QHBoxLayout()
            self.import_btn = QPushButton(self.tr("📥 Import Image..."))
            self.import_btn.clicked.connect(self.import_sprite_image)
            import_button_layout.addWidget(self.import_btn)
            layout.addLayout(import_button_layout)

        # Creation date
        if 'created_date' in self.asset_data:
            date_label = QLabel(self.tr("Created: {0}").format(self.asset_data['created_date']))
            layout.addWidget(date_label)

        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)

        layout.addStretch()
        layout.addLayout(button_layout)

    def import_sprite_image(self):
        """Import an image for this sprite (replaces existing image)"""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path

        # Open file dialog for image selection
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Sprite Image"),
            str(Path.home()),
            self.tr("Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)")
        )

        if not file_path:
            return

        # Get the IDE window to access asset import functionality
        parent = self.parent()
        while parent and not hasattr(parent, 'asset_manager'):
            parent = parent.parent()

        if parent and hasattr(parent, 'asset_manager'):
            # Replace the sprite image (not import as new)
            sprite_name = self.asset_data.get('name')

            try:
                # Use replace_sprite_image to update existing sprite
                result = parent.asset_manager.replace_sprite_image(
                    Path(file_path),
                    sprite_name
                )

                if result:
                    QMessageBox.information(
                        self,
                        self.tr("Success"),
                        self.tr("Image imported successfully for sprite '{0}'").format(sprite_name)
                    )
                    # Update the dialog to show new status
                    self.asset_data = result
                    self.accept()  # Close and let parent refresh
                else:
                    QMessageBox.warning(
                        self,
                        self.tr("Import Failed"),
                        self.tr("Failed to import the image. Please try again.")
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Error"),
                    self.tr("Error importing image: {0}").format(str(e))
                )
        else:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Could not access asset manager. Please try again.")
            )

class CreateAssetDialog(QDialog):
    """Dialog for creating new assets"""

    def __init__(self, asset_type: str, parent=None):
        super().__init__(parent)
        self.asset_type = asset_type
        self.asset_name = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the create asset dialog UI"""
        self.setWindowTitle(self.tr("Create {0}").format(self.asset_type.title()))
        self.setFixedSize(400, 150)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(self.tr("<h3>Create New {0}</h3>").format(self.asset_type.title()))
        layout.addWidget(title_label)

        # Name input
        name_label = QLabel(self.tr("Asset name:"))
        layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(self.tr("Enter {0} name...").format(self.asset_type))
        self.name_edit.setFocus()
        layout.addWidget(self.name_edit)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.create_btn = QPushButton(self.tr("Create"))
        self.create_btn.clicked.connect(self.accept_create)
        self.create_btn.setDefault(True)
        self.create_btn.setEnabled(False)
        button_layout.addWidget(self.create_btn)

        layout.addLayout(button_layout)

        # Connect Enter key to create
        self.name_edit.returnPressed.connect(self.accept_create)

        # Validate input as user types
        self.name_edit.textChanged.connect(self.validate_name)

    def validate_name(self, text: str):
        """Validate the asset name as user types"""
        text = text.strip()
        is_valid, _ = validate_asset_name(text)
        self.create_btn.setEnabled(is_valid)

    def accept_create(self):
        """Accept the create if valid"""
        name = self.name_edit.text().strip()

        is_valid, error_msg = validate_asset_name(name)

        if not is_valid:
            QMessageBox.warning(self, self.tr("Invalid Name"), error_msg)
            return

        self.asset_name = name
        self.accept()


class TrashDialog(QDialog):
    """Restore or permanently delete soft-deleted assets.

    See utils/asset_trash.py's module docstring for why deleted assets go
    here instead of a QUndoCommand-based undo/redo — this dialog is the
    UI half of that decision. Deliberately depends only on asset_manager
    (list_trash/restore_from_trash/empty_trash), not on the asset tree or
    project manager directly, so it stays testable without a full IDE
    window; the caller is responsible for refreshing the tree / saving
    after a successful restore (see on_restored).
    """

    def __init__(self, asset_manager, parent=None):
        super().__init__(parent)
        self.asset_manager = asset_manager
        # Called with (asset_type, asset_name, asset_data) after a
        # successful restore, so the caller can refresh the asset tree
        # and persist the change. None (the default) means "don't notify".
        self.on_restored = None
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        self.setWindowTitle(self.tr("Trash"))
        self.setMinimumSize(480, 360)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        info_label = QLabel(self.tr(
            "Deleted assets stay here until you permanently remove them."))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self._update_button_states)
        layout.addWidget(self.list_widget)

        self.detail_label = QLabel("")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)

        button_layout = QHBoxLayout()

        self.restore_btn = QPushButton(self.tr("Restore"))
        self.restore_btn.clicked.connect(self._restore_selected)
        self.restore_btn.setEnabled(False)
        button_layout.addWidget(self.restore_btn)

        self.delete_btn = QPushButton(self.tr("Delete Permanently"))
        self.delete_btn.clicked.connect(self._delete_selected)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        self.empty_btn = QPushButton(self.tr("Empty Trash"))
        self.empty_btn.clicked.connect(self._empty_all)
        button_layout.addWidget(self.empty_btn)

        button_layout.addStretch()

        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def refresh_list(self):
        self.list_widget.clear()
        entries = self.asset_manager.list_trash()
        for entry in entries:
            label = self.tr("{0} / {1}  —  deleted {2}").format(
                entry["asset_type"], entry["asset_name"],
                entry.get("deleted_at", "")[:19].replace("T", " "))
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, entry)
            self.list_widget.addItem(item)
        self.empty_btn.setEnabled(bool(entries))
        self._update_button_states()

    def _selected_entry(self):
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _update_button_states(self):
        entry = self._selected_entry()
        self.restore_btn.setEnabled(entry is not None)
        self.delete_btn.setEnabled(entry is not None)
        if entry and entry.get("cleared_references"):
            names = ", ".join(c["object"] for c in entry["cleared_references"])
            self.detail_label.setText(self.tr(
                "Deleting this cleared a reference in: {0}. Restoring "
                "brings the file back but does not re-link that "
                "reference automatically.").format(names))
        else:
            self.detail_label.setText("")

    def _restore_selected(self):
        entry = self._selected_entry()
        if not entry:
            return
        asset_data = self.asset_manager.restore_from_trash(entry["id"])
        if asset_data is None:
            QMessageBox.warning(
                self, self.tr("Restore Failed"),
                self.tr(
                    "Could not restore '{0}' — an asset with that name "
                    "already exists. Rename or remove it first, then try "
                    "again.").format(entry["asset_name"]))
            return
        if self.on_restored:
            self.on_restored(entry["asset_type"], entry["asset_name"], asset_data)
        self.refresh_list()

    def _delete_selected(self):
        entry = self._selected_entry()
        if not entry:
            return
        reply = QMessageBox.question(
            self, self.tr("Delete Permanently"),
            self.tr(
                "Permanently delete '{0}'? This cannot be undone."
            ).format(entry["asset_name"]),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.asset_manager.empty_trash(entry["id"])
            self.refresh_list()

    def _empty_all(self):
        reply = QMessageBox.question(
            self, self.tr("Empty Trash"),
            self.tr("Permanently delete everything in the trash? This "
                    "cannot be undone."),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.asset_manager.empty_trash()
            self.refresh_list()


class UnusedAssetsDialog(QDialog):
    """List assets with zero references (utils/asset_usage.find_unused_assets)
    and delete the checked ones — Tier 4 of docs/ASSET_MANAGER_PLAN.md.

    Deletion routes through AssetManager.delete_asset, so a checked item
    lands in the Trash (utils/asset_trash.py) like any other delete, not a
    permanent removal — this dialog adds no new undo story of its own,
    reusing the one item 10.5 already settled.
    """

    def __init__(self, project_data: dict, asset_manager, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.asset_manager = asset_manager
        # Called with (asset_type, asset_name) after each successful
        # delete, so the caller can update the asset tree. None (the
        # default) means "don't notify".
        self.on_deleted = None
        self.deleted_count = 0
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        self.setWindowTitle(self.tr("Unused Assets"))
        self.setMinimumSize(480, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        info_label = QLabel(self.tr(
            "Assets not referenced by any object, room, or action. "
            "Deleted items go to the Trash, not removed permanently. "
            "References inside execute_code/execute_script can't be "
            "detected and may cause false positives here. Rooms are "
            "listed as \"not explicitly navigated to\" rather than "
            "unused — a starting room is often never referenced by name "
            "anywhere, so that alone doesn't mean it's safe to delete."))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemChanged.connect(self._update_button_states)
        layout.addWidget(self.tree_widget)

        select_layout = QHBoxLayout()
        select_all_btn = QPushButton(self.tr("Select All"))
        select_all_btn.clicked.connect(lambda: self._set_all_checked(True))
        select_layout.addWidget(select_all_btn)
        select_none_btn = QPushButton(self.tr("Select None"))
        select_none_btn.clicked.connect(lambda: self._set_all_checked(False))
        select_layout.addWidget(select_none_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)

        button_layout = QHBoxLayout()

        self.delete_btn = QPushButton(self.tr("Move Selected to Trash"))
        self.delete_btn.clicked.connect(self._delete_selected)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()

        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def refresh_list(self):
        # save_assets_to_project_data folds the live in-memory cache into
        # project_data first — the same pattern AssetTreeWidget's own
        # force_project_refresh uses — so a delete made moments ago (or by
        # any other in-session edit) is reflected before re-scanning for
        # usages, without ever reading from disk.
        if hasattr(self.asset_manager, 'save_assets_to_project_data'):
            self.asset_manager.save_assets_to_project_data(self.project_data)

        from utils.asset_usage import find_unused_assets
        unused = find_unused_assets(self.project_data)

        self.tree_widget.blockSignals(True)
        self.tree_widget.clear()
        for category in sorted(unused):
            names = unused[category]
            if category == "rooms":
                # A room with zero AssetUsage records may just be a
                # starting room nothing ever explicitly navigates TO by
                # name (asset_usage.py's own docstring) — real, but not
                # the same claim as "unused", so label and treat it
                # differently rather than implying it's obviously safe.
                label = self.tr("Rooms — not explicitly navigated to ({0})").format(len(names))
            else:
                label = self.tr("{0} ({1})").format(category.title(), len(names))
            cat_item = QTreeWidgetItem([label])
            cat_item.setFlags(Qt.ItemIsEnabled)
            cat_item.setData(0, Qt.UserRole, category)
            self.tree_widget.addTopLevelItem(cat_item)
            for name in names:
                child = QTreeWidgetItem([name])
                child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
                child.setCheckState(0, Qt.Unchecked)
                child.setData(0, Qt.UserRole, (category, name))
                cat_item.addChild(child)
            cat_item.setExpanded(True)
        self.tree_widget.blockSignals(False)

        if not unused:
            empty_item = QTreeWidgetItem([self.tr("No unused assets found.")])
            empty_item.setFlags(Qt.ItemIsEnabled)
            self.tree_widget.addTopLevelItem(empty_item)

        self._update_button_states()

    @staticmethod
    def item_key(item):
        """The ``(asset_type, asset_name)`` pair a leaf item carries, or None
        for a category/placeholder row.

        Always read the pair through here rather than calling ``data(0,
        Qt.UserRole)`` directly -- see ``widgets.qt_helpers.as_hashable_tuple``
        for why (a real, version-dependent PySide6 hashability hazard, not a
        hypothetical one)."""
        return as_hashable_tuple(item.data(0, Qt.UserRole))

    def _checked_items(self):
        result = []
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                if child.checkState(0) == Qt.Checked:
                    result.append(self.item_key(child))
        return result

    def _set_all_checked(self, checked: bool):
        """Select All/None. Rooms are deliberately excluded from Select
        All — it's easy to one-click sweep in a starting room that's
        never explicitly navigated to by name but is still very much in
        use (see refresh_list's comment); individual room checkboxes stay
        available for a deliberate choice. Select None still clears them,
        since un-checking is always safe."""
        state = Qt.Checked if checked else Qt.Unchecked
        self.tree_widget.blockSignals(True)
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            if checked and cat_item.data(0, Qt.UserRole) == "rooms":
                continue
            for j in range(cat_item.childCount()):
                cat_item.child(j).setCheckState(0, state)
        self.tree_widget.blockSignals(False)
        self._update_button_states()

    def _update_button_states(self, *_):
        self.delete_btn.setEnabled(bool(self._checked_items()))

    def _delete_selected(self):
        items = self._checked_items()
        if not items:
            return
        reply = QMessageBox.question(
            self, self.tr("Move to Trash"),
            self.tr("Move {0} unused asset(s) to the Trash?").format(len(items)),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        for asset_type, asset_name in items:
            if self.asset_manager.delete_asset(asset_type, asset_name):
                self.deleted_count += 1
                if self.on_deleted:
                    self.on_deleted(asset_type, asset_name)
        self.refresh_list()


class OrphanedFilesDialog(QDialog):
    """Find physical asset files with no project.json entry pointing at
    them (utils.project_cleanup.find_orphaned_physical_files) and manage
    this feature's own trash store — Tier 3 of docs/CLEAN_PROJECT_PLAN.md.

    Deliberately its own trash mechanism (utils/project_cleanup.py's
    trash_orphaned_file/list_orphan_trash/restore_orphaned_file/
    empty_orphan_trash, backed by .trash_orphaned_files/), NOT
    AssetManager.delete_asset / the asset Trash — see project_cleanup.py's
    module docstring for why: these files have no project.json entry at
    all, and AssetManager.restore_from_trash unconditionally re-inserts a
    restored entry into assets_cache, which would plant a fake asset for
    a bare file.
    """

    def __init__(self, project_data: dict, asset_manager, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.asset_manager = asset_manager
        self.trashed_count = 0
        self.setup_ui()
        self.refresh()

    def _project_dir(self):
        project_dir = getattr(self.asset_manager, 'project_directory', None)
        return Path(project_dir) if project_dir else None

    def setup_ui(self):
        self.setWindowTitle(self.tr("Orphaned Files"))
        self.setMinimumSize(520, 560)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        info_label = QLabel(self.tr(
            "Physical files under sprites/sounds/backgrounds/fonts/"
            "thumbnails that nothing in this project references — usually "
            "left behind by a deleted asset entry, or a file copied in by "
            "hand. Trashed files can be restored below until permanently "
            "removed."))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addWidget(QLabel(self.tr("Found on disk:")))
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemChanged.connect(self._update_button_states)
        layout.addWidget(self.tree_widget)

        select_layout = QHBoxLayout()
        select_all_btn = QPushButton(self.tr("Select All"))
        select_all_btn.clicked.connect(lambda: self._set_all_checked(True))
        select_layout.addWidget(select_all_btn)
        select_none_btn = QPushButton(self.tr("Select None"))
        select_none_btn.clicked.connect(lambda: self._set_all_checked(False))
        select_layout.addWidget(select_none_btn)
        select_layout.addStretch()
        self.trash_btn = QPushButton(self.tr("Move Selected to Trash"))
        self.trash_btn.clicked.connect(self._trash_selected)
        self.trash_btn.setEnabled(False)
        select_layout.addWidget(self.trash_btn)
        layout.addLayout(select_layout)

        layout.addWidget(QLabel(self.tr("Trashed:")))
        self.trash_list = QListWidget()
        self.trash_list.itemSelectionChanged.connect(self._update_button_states)
        layout.addWidget(self.trash_list)

        trash_button_layout = QHBoxLayout()
        self.restore_btn = QPushButton(self.tr("Restore"))
        self.restore_btn.clicked.connect(self._restore_selected)
        self.restore_btn.setEnabled(False)
        trash_button_layout.addWidget(self.restore_btn)
        self.delete_permanently_btn = QPushButton(self.tr("Delete Permanently"))
        self.delete_permanently_btn.clicked.connect(self._delete_selected_permanently)
        self.delete_permanently_btn.setEnabled(False)
        trash_button_layout.addWidget(self.delete_permanently_btn)
        self.empty_btn = QPushButton(self.tr("Empty"))
        self.empty_btn.clicked.connect(self._empty_all)
        self.empty_btn.setEnabled(False)
        trash_button_layout.addWidget(self.empty_btn)
        trash_button_layout.addStretch()
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        trash_button_layout.addWidget(close_btn)
        layout.addLayout(trash_button_layout)

    def refresh(self):
        self._refresh_found()
        self._refresh_trash()

    def _refresh_found(self):
        if hasattr(self.asset_manager, 'save_assets_to_project_data'):
            self.asset_manager.save_assets_to_project_data(self.project_data)

        project_dir = self._project_dir()
        orphaned = {}
        if project_dir:
            from utils.project_cleanup import find_orphaned_physical_files
            orphaned = find_orphaned_physical_files(project_dir, self.project_data)

        self.tree_widget.blockSignals(True)
        self.tree_widget.clear()
        for category in sorted(orphaned):
            paths = orphaned[category]
            cat_item = QTreeWidgetItem([self.tr("{0} ({1})").format(category.title(), len(paths))])
            cat_item.setFlags(Qt.ItemIsEnabled)
            self.tree_widget.addTopLevelItem(cat_item)
            for path in paths:
                rel = path.relative_to(project_dir).as_posix()
                child = QTreeWidgetItem([rel])
                child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
                child.setCheckState(0, Qt.Unchecked)
                child.setData(0, Qt.UserRole, rel)
                cat_item.addChild(child)
            cat_item.setExpanded(True)
        if not orphaned:
            empty_item = QTreeWidgetItem([self.tr("No orphaned files found.")])
            empty_item.setFlags(Qt.ItemIsEnabled)
            self.tree_widget.addTopLevelItem(empty_item)
        self.tree_widget.blockSignals(False)
        self._update_button_states()

    def _refresh_trash(self):
        self.trash_list.clear()
        project_dir = self._project_dir()
        if project_dir:
            from utils.project_cleanup import list_orphan_trash
            for entry in list_orphan_trash(project_dir):
                label = self.tr("{0}  —  deleted {1}").format(
                    entry["relative_path"], entry.get("deleted_at", "")[:19].replace("T", " "))
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, entry)
                self.trash_list.addItem(item)
        self._update_button_states()

    def _checked_paths(self):
        result = []
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                if child.checkState(0) == Qt.Checked:
                    result.append(child.data(0, Qt.UserRole))
        return result

    def _set_all_checked(self, checked: bool):
        state = Qt.Checked if checked else Qt.Unchecked
        self.tree_widget.blockSignals(True)
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                cat_item.child(j).setCheckState(0, state)
        self.tree_widget.blockSignals(False)
        self._update_button_states()

    def _selected_trash_entry(self):
        item = self.trash_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _update_button_states(self, *_):
        self.trash_btn.setEnabled(bool(self._checked_paths()))
        entry = self._selected_trash_entry()
        self.restore_btn.setEnabled(entry is not None)
        self.delete_permanently_btn.setEnabled(entry is not None)
        self.empty_btn.setEnabled(self.trash_list.count() > 0)

    def _trash_selected(self):
        paths = self._checked_paths()
        if not paths:
            return
        reply = QMessageBox.question(
            self, self.tr("Move to Trash"),
            self.tr("Move {0} orphaned file(s) to the trash?").format(len(paths)),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        project_dir = self._project_dir()
        from utils.project_cleanup import trash_orphaned_file
        for rel in paths:
            if trash_orphaned_file(project_dir, rel):
                self.trashed_count += 1
        self.refresh()

    def _restore_selected(self):
        entry = self._selected_trash_entry()
        if not entry:
            return
        from utils.project_cleanup import restore_orphaned_file
        restored = restore_orphaned_file(self._project_dir(), entry["id"])
        if restored is None:
            QMessageBox.warning(
                self, self.tr("Restore Failed"),
                self.tr(
                    "Could not restore '{0}' — a file already exists "
                    "there. Move or remove it first, then try again."
                ).format(entry["relative_path"]))
            return
        self.refresh()

    def _delete_selected_permanently(self):
        entry = self._selected_trash_entry()
        if not entry:
            return
        reply = QMessageBox.question(
            self, self.tr("Delete Permanently"),
            self.tr("Permanently delete '{0}'? This cannot be undone."
                    ).format(entry["relative_path"]),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            from utils.project_cleanup import empty_orphan_trash
            empty_orphan_trash(self._project_dir(), entry["id"])
            self.refresh()

    def _empty_all(self):
        reply = QMessageBox.question(
            self, self.tr("Empty Trash"),
            self.tr("Permanently delete every trashed orphaned file? This "
                    "cannot be undone."),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            from utils.project_cleanup import empty_orphan_trash
            empty_orphan_trash(self._project_dir())
            self.refresh()
