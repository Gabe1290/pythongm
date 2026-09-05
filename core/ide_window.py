#!/usr/bin/env python3

from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                               QSplitter, QMessageBox, QInputDialog,
                               QProgressBar, QLabel, QStyle, QTabWidget,
                               QToolBar, QApplication, QLineEdit)

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction

from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
# from widgets.properties_panel import PropertiesPanel
from widgets.enhanced_properties_panel import EnhancedPropertiesPanel
from core.project_manager import ProjectManager
from core.asset_manager import AssetManager
from core.ide_exporters import IDEExporters
from dialogs.project_dialogs import NewProjectDialog, ProjectSettingsDialog
from dialogs.import_dialogs import ImportAssetDialog
from dialogs.blockly_config_dialog import BlocklyConfigDialog
from dialogs.thymio_config_dialog import ThymioConfigDialog
from utils.config import Config
from runtime.game_runner import GameRunner

from core.logger import get_logger
logger = get_logger(__name__)


def _green_play_icon():
    """A filled green play-triangle for the toolbar 'Test Game' action.

    Drawn rather than taken from the style: the standard SP_MediaPlay is a
    monochrome, theme-tinted glyph, so 'Test Game' reads as the unambiguous
    green Run action on every platform/theme only if we paint it ourselves.
    """
    from PySide6.QtGui import QPixmap, QPainter, QColor, QPolygonF, QIcon
    from PySide6.QtCore import QPointF
    pm = QPixmap(16, 16)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(46, 158, 68))  # a clear, mid "go" green
    p.drawPolygon(QPolygonF([QPointF(4, 3), QPointF(13, 8), QPointF(4, 13)]))
    p.end()
    return QIcon(pm)


def _contrasting_icon_color(palette):
    """Pick an icon foreground (light or dark) that contrasts with the
    toolbar button background, so tinted icons stay legible on both light
    and dark themes."""
    from PySide6.QtGui import QColor, QPalette
    btn = palette.color(QPalette.ColorRole.Button)
    lum = 0.299 * btn.red() + 0.587 * btn.green() + 0.114 * btn.blue()
    return QColor(235, 235, 235) if lum < 128 else QColor(60, 60, 60)


def _tinted_standard_icon(style, icon_name, color):
    """Recolour a standard pixmap to ``color`` (preserving its alpha
    silhouette). The style's SP_MediaVolume speaker is near-black and
    vanishes on a dark toolbar (Windows dark theme); tinting it to a
    palette-contrasting colour keeps it visible on any theme. Returns None
    if the named standard pixmap is unavailable."""
    from PySide6.QtGui import QPixmap, QPainter, QIcon
    pixmap_enum = getattr(QStyle.StandardPixmap, icon_name, None)
    if pixmap_enum is None:
        return None
    base = style.standardIcon(pixmap_enum)
    if base.isNull():
        return None
    pm = base.pixmap(16, 16)
    if pm.isNull():
        return None
    out = QPixmap(pm.size())
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.drawPixmap(0, 0, pm)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    p.fillRect(out.rect(), color)
    p.end()
    return QIcon(out)




from core.ide._samples import SamplesMixin
from core.ide._edit_actions import EditActionsMixin
from core.ide._dialogs import DialogsMixin
from core.ide._test_game import TestGameMixin
from core.ide._project_actions import ProjectActionsMixin
from core.ide._assets import AssetsMixin
from core.ide._editor_lifecycle import EditorLifecycleMixin
from core.ide._export import ExportMixin


class PyGameMakerIDE(SamplesMixin, EditActionsMixin, DialogsMixin, TestGameMixin,
                     ProjectActionsMixin, AssetsMixin, EditorLifecycleMixin,
                     ExportMixin, QMainWindow):

    def __init__(self):
        super().__init__()

        # Create managers in the right order
        self.asset_manager = AssetManager()  # CREATE ASSET MANAGER FIRST
        self.project_manager = ProjectManager()  # CREATE PROJECT MANAGER SECOND

        # Connect them together - THIS IS CRITICAL
        try:
            self.project_manager.set_asset_manager(self.asset_manager)
        except Exception as e:
            logger.error(f"ERROR in set_asset_manager: {e}")
            import traceback
            traceback.print_exc()

        # Load auto-save settings from config. The Preferences dialog writes
        # these under the editor config as auto_save_interval in MINUTES; the
        # old code read a never-written top-level key (default 30) as seconds,
        # so the user's interval choice never took effect.
        from utils.config import Config
        editor_cfg = Config.get_editor_config()
        auto_save_enabled = editor_cfg.get('auto_save_enabled', True)
        auto_save_interval = editor_cfg.get('auto_save_interval', 5) * 60 * 1000  # minutes -> ms
        self.project_manager.set_auto_save(auto_save_enabled, auto_save_interval)

        self.current_project_path = None
        self.current_project_data = None

        # Global preferred window mode for new editor opens. Read here so
        # create_toolbar (called from setup_ui) can label its toggle button
        # correctly. The detached-windows registry is initialized later in
        # create_center_panel_with_editors but stays consistent with this.
        self.window_mode = Config.get('window_mode', 'tabbed')
        if self.window_mode not in ('tabbed', 'floating'):
            self.window_mode = 'tabbed'

        # Initialize export helper module
        self.exporters = IDEExporters(self)

        # Add game runner
        self.game_runner = None  # Will be initialized when project is loaded

        self.setup_ui()
        self.setup_connections()
        self.restore_geometry()

        # One-time cleanup of pre-rc.12 in-place sample paths that may
        # be sitting in the user's recent_projects from older sessions.
        # See _strip_samples_from_recent_projects() for why.
        self._strip_samples_from_recent_projects()

        self.update_window_title()
        self.update_ui_state()

    def setup_ui(self):
        self.setWindowTitle("PyGameMaker IDE")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        try:
            self.create_menu_bar()

            # Set initial auto-save checkbox state from the SAME store that
            # wires the timer (editor config), so the menu checkbox can't
            # desynchronize from the actual auto-save state (audit M6).
            from utils.config import Config
            auto_save_enabled = Config.get_editor_config().get('auto_save_enabled', True)
            if hasattr(self, 'auto_save_action'):
                self.auto_save_action.setChecked(auto_save_enabled)

        except Exception as e:
            logger.error(f"ERROR in create_menu_bar: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_toolbar()
        except Exception as e:
            logger.error(f"ERROR in create_toolbar: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_main_widget()
        except Exception as e:
            logger.error(f"ERROR in create_main_widget: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            self.create_status_bar()
        except Exception as e:
            logger.error(f"ERROR in create_status_bar: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Connect the rename signal
        self.asset_tree.asset_renamed.connect(self.on_asset_renamed)

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu(self.tr("&File"))
        # Store references so the toolbar can reuse the same QAction
        # instances. Qt then shares enable/disable state automatically.
        self.new_project_action = self.create_action(self.tr("&New Project..."), "Ctrl+N", self.new_project)
        self.open_project_action = self.create_action(self.tr("&Open Project..."), "Ctrl+O", self.open_project)
        self.save_project_action = self.create_action(self.tr("&Save Project"), "Ctrl+S", self.save_project)
        self.save_project_as_action = self.create_action(self.tr("Save Project &As..."), "Ctrl+Shift+S", self.save_project_as)
        file_menu.addAction(self.new_project_action)
        file_menu.addAction(self.open_project_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_project_action)
        file_menu.addAction(self.save_project_as_action)
        # Close the current project (back to the Welcome tab) without quitting
        # the IDE. No accelerator: Ctrl+W is already the per-editor close
        # (BaseEditor), so binding it here would be ambiguous.
        self.close_project_action = self.create_action(self.tr("&Close Project"), None, self.close_project)
        file_menu.addAction(self.close_project_action)
        file_menu.addSeparator()

        self.recent_projects_menu = file_menu.addMenu(self.tr("Recent Projects"))
        self.update_recent_projects_menu(self.recent_projects_menu)

        file_menu.addSeparator()
        # Export menu items
        # Store references to export actions
        self.export_html5_action = self.create_action(self.tr("Export as HTML5..."), None, self.export_html5)
        self.export_zip_action = self.create_action(self.tr("Export as &Zip..."), None, self.export_project_zip)
        self.export_kivy_action = self.create_action(self.tr("Export to Kivy..."), None, self.export_kivy)
        # [1.0] Aseba/Thymio export hidden from the menu — see docs/POST_1_0_REFACTOR.md.
        # The export_aseba_code method is retained for the planned Thymio extension.
        # self.export_aseba_action = self.create_action(self.tr("Export &Aseba (Thymio) code..."), None, self.export_aseba_code)
        self.export_project_action = self.create_action(self.tr("Export Project..."), "Ctrl+E", self.export_project)

        file_menu.addAction(self.export_html5_action)
        file_menu.addAction(self.export_zip_action)
        file_menu.addAction(self.export_kivy_action)
        # file_menu.addAction(self.export_aseba_action)
        file_menu.addAction(self.export_project_action)

        file_menu.addAction(self.create_action(self.tr("Open &Zip Project..."), None, self.open_project_zip))
        # Import-as-new-project actions: stored on self so update_ui_state can keep
        # them enabled regardless of whether a project is currently loaded.
        # [1.0] Open Roberta import hidden from the menu — see docs/POST_1_0_REFACTOR.md.
        # The import_roberta_xml method is retained for the planned Thymio extension.
        # self.import_roberta_action = self.create_action(self.tr("Import Open &Roberta XML..."), None, self.import_roberta_xml)
        self.import_gmk_action = self.create_action(self.tr("Import &GameMaker .gmk File..."), None, self.import_gmk_file)
        # file_menu.addAction(self.import_roberta_action)
        file_menu.addAction(self.import_gmk_action)
        file_menu.addSeparator()

        # Auto-save as zip toggle
        self.auto_save_zip_action = QAction(self.tr("Auto-Save to Zip"), self)
        self.auto_save_zip_action.setCheckable(True)
        self.auto_save_zip_action.setChecked(False)
        self.auto_save_zip_action.triggered.connect(self.toggle_auto_save_zip)
        file_menu.addAction(self.auto_save_zip_action)

        # Auto-save toggle (NEW)
        self.auto_save_action = QAction(self.tr("Enable Auto-Save"), self)
        self.auto_save_action.setCheckable(True)
        self.auto_save_action.setChecked(True)  # Enabled by default
        self.auto_save_action.triggered.connect(self.toggle_auto_save)
        file_menu.addAction(self.auto_save_action)

        # Auto-save settings
        auto_save_settings_action = QAction(self.tr("Auto-Save Settings..."), self)
        auto_save_settings_action.triggered.connect(self.show_auto_save_settings)
        file_menu.addAction(auto_save_settings_action)

        file_menu.addSeparator()
        file_menu.addAction(self.create_action(self.tr("Project &Settings..."), None, self.project_settings))
        file_menu.addSeparator()
        file_menu.addAction(self.create_action(self.tr("E&xit"), "Ctrl+Q", self.close))

        edit_menu = menubar.addMenu(self.tr("&Edit"))
        edit_menu.addAction(self.create_action(self.tr("&Undo"), "Ctrl+Z", self.undo))
        edit_menu.addAction(self.create_action(self.tr("&Redo"), "Ctrl+Y", self.redo))
        edit_menu.addSeparator()
        edit_menu.addAction(self.create_action(self.tr("Cu&t"), "Ctrl+X", self.cut))
        edit_menu.addAction(self.create_action(self.tr("&Copy"), "Ctrl+C", self.copy))
        edit_menu.addAction(self.create_action(self.tr("&Paste"), "Ctrl+V", self.paste))
        edit_menu.addAction(self.create_action(self.tr("&Duplicate"), "Ctrl+D", self.duplicate))
        edit_menu.addSeparator()
        edit_menu.addAction(self.create_action(self.tr("&Find..."), "Ctrl+F", self.find))
        edit_menu.addAction(self.create_action(self.tr("Find and &Replace..."), "Ctrl+H", self.find_replace))

        # Store references to all asset actions and enable them
        self.import_sprite_action = self.create_action(self.tr("Import &Sprite..."), None, self.import_sprite)
        self.import_sound_action = self.create_action(self.tr("Import &Sound..."), None, self.import_sound)
        self.import_background_action = self.create_action(self.tr("Import &Background..."), None, self.import_background)
        self.create_object_action = self.create_action(self.tr("Create &Object..."), None, self.create_object)
        self.create_room_action = self.create_action(self.tr("Create &Room..."), None, self.create_room)
        self.create_room_action.setShortcut("Ctrl+R")
        self.create_script_action = self.create_action(self.tr("Create S&cript..."), None, self.create_script)
        self.create_font_action = self.create_action(self.tr("Create &Font..."), None, self.create_font)

        # Enable all asset actions regardless of project state
        asset_actions = [
            self.import_sprite_action, self.import_sound_action, self.import_background_action,
            self.create_object_action, self.create_room_action, self.create_script_action, self.create_font_action
        ]
        for action in asset_actions:
            action.setEnabled(True)

        # Add to menu
        assets_menu = menubar.addMenu(self.tr("&Assets"))
        assets_menu.addAction(self.import_sprite_action)
        assets_menu.addAction(self.import_sound_action)
        assets_menu.addAction(self.import_background_action)
        assets_menu.addSeparator()
        assets_menu.addAction(self.create_object_action)
        assets_menu.addAction(self.create_room_action)
        assets_menu.addAction(self.create_script_action)
        assets_menu.addAction(self.create_font_action)
        assets_menu.addSeparator()

        # Import resource packages (NEW)
        import_object_action = self.create_action(self.tr("Import Object Package..."), None, self.import_object_package)
        import_room_action = self.create_action(self.tr("Import Room Package..."), None, self.import_room_package)
        assets_menu.addAction(import_object_action)
        assets_menu.addAction(import_room_action)

        self.build_menu = menubar.addMenu(self.tr("&Build"))
        # Store references to build actions
        self.test_game_action = self.create_action(self.tr("&Test Game"), "F5", self.test_game)
        self.debug_game_action = self.create_action(self.tr("&Debug Game"), "F6", self.debug_game)
        self.build_game_action = self.create_action(self.tr("&Build Game..."), "F7", self.build_game)
        self.build_and_run_action = self.create_action(self.tr("Build and &Run"), "F8", self.build_and_run)
        self.export_game_action = self.create_action(self.tr("&Export Game..."), None, self.export_game)

        self.build_menu.addAction(self.test_game_action)
        self.build_menu.addAction(self.debug_game_action)
        self.build_menu.addSeparator()
        self.build_menu.addAction(self.build_game_action)
        self.build_menu.addAction(self.build_and_run_action)
        self.build_menu.addSeparator()
        self.build_menu.addAction(self.export_game_action)

        tools_menu = menubar.addMenu(self.tr("&Tools"))
        # On macOS, Qt auto-promotes actions to the App menu via text heuristics
        # ("Preferences", "Settings", "Config", "Setup" all match PreferencesRole).
        # Pin the real Preferences to PreferencesRole and force NoRole on the
        # Configure ... actions so the App-menu Preferences slot doesn't get
        # hijacked by "Configure Thymio Blocks..." etc.
        preferences_action = self.create_action(self.tr("&Preferences..."), None, self.preferences)
        preferences_action.setMenuRole(QAction.PreferencesRole)
        tools_menu.addAction(preferences_action)
        configure_blockly_action = self.create_action(self.tr("Configure &Action Blocks..."), None, self.configure_blockly)
        configure_blockly_action.setMenuRole(QAction.NoRole)
        tools_menu.addAction(configure_blockly_action)
        # [1.0] Configure Thymio Blocks hidden from the menu — see docs/POST_1_0_REFACTOR.md.
        # The configure_thymio method is retained for the planned Thymio extension.
        # configure_thymio_action = self.create_action(self.tr("Configure &Thymio Blocks..."), None, self.configure_thymio)
        # configure_thymio_action.setMenuRole(QAction.NoRole)
        # tools_menu.addAction(configure_thymio_action)
        tools_menu.addSeparator()
        # Project-scoped tools: stored on self so update_ui_state() can
        # disable them when no project is open. Without the stored
        # reference, these used to be clickable from the menu and would
        # only show a "Please open a project first" dialog after the fact.
        self.validate_project_action = self.create_action(
            self.tr("&Validate Project"), None, self.validate_project)
        self.migrate_project_action = self.create_action(
            self.tr("&Migrate to Modular Structure"), None, self.migrate_project_structure)
        self.show_trash_action = self.create_action(
            self.tr("&Restore Deleted Assets..."), None, self.show_trash_dialog)
        self.show_unused_assets_action = self.create_action(
            self.tr("Find &Unused Assets..."), None, self.show_unused_assets_dialog)
        self.clean_project_action = self.create_action(
            self.tr("Clean &Project"), None, self.clean_project)
        self.show_orphaned_files_action = self.create_action(
            self.tr("Find &Orphaned Files..."), None, self.show_orphaned_files_dialog)
        tools_menu.addAction(self.validate_project_action)
        tools_menu.addAction(self.migrate_project_action)
        tools_menu.addAction(self.show_trash_action)
        tools_menu.addAction(self.show_unused_assets_action)
        tools_menu.addAction(self.clean_project_action)
        tools_menu.addAction(self.show_orphaned_files_action)
        tools_menu.addSeparator()

        # Language submenu
        language_menu = tools_menu.addMenu(self.tr("🌐 &Language"))
        self.create_language_menu(language_menu)

        # [1.0] Thymio Programming submenu hidden — see docs/POST_1_0_REFACTOR.md.
        # All underlying methods (toggle_thymio_tab, show_thymio_playground,
        # show_thymio_event_selector, show_thymio_action_selector,
        # import_roberta_xml) are retained for the planned Thymio extension.
        # tools_menu.addSeparator()
        # thymio_menu = tools_menu.addMenu(self.tr("🤖 &Thymio Programming"))
        #
        # # Show Thymio Tab checkbox
        # self.show_thymio_tab_action = QAction(self.tr("Show Thymio Tab in Object Editor"), self)
        # self.show_thymio_tab_action.setCheckable(True)
        # self.show_thymio_tab_action.setChecked(Config.get('show_thymio_tab', False))
        # self.show_thymio_tab_action.triggered.connect(self.toggle_thymio_tab)
        # thymio_menu.addAction(self.show_thymio_tab_action)
        # thymio_menu.addSeparator()
        #
        # thymio_menu.addAction(self.create_action(self.tr("Open &Playground..."), None, self.show_thymio_playground))
        # thymio_menu.addSeparator()
        # # Add Event/Action target the currently active object editor, which
        # # can only exist when a project is open. Stored on self so
        # # update_ui_state() can disable them in that case.
        # self.thymio_add_event_action = self.create_action(
        #     self.tr("Add &Event..."), None, self.show_thymio_event_selector)
        # self.thymio_add_action_action = self.create_action(
        #     self.tr("Add &Action..."), None, self.show_thymio_action_selector)
        # thymio_menu.addAction(self.thymio_add_event_action)
        # thymio_menu.addAction(self.thymio_add_action_action)
        # thymio_menu.addSeparator()
        # self.thymio_import_roberta_action = self.create_action(self.tr("Import Open &Roberta XML..."), None, self.import_roberta_xml)
        # thymio_menu.addAction(self.thymio_import_roberta_action)

        help_menu = menubar.addMenu(self.tr("&Help"))
        help_menu.addAction(self.create_action(self.tr("&Documentation"), "F1", self.show_documentation))
        help_menu.addAction(self.create_action(self.tr("&Online Documentation"), None, self.show_online_documentation))
        help_menu.addAction(self.create_action(self.tr("&Tutorials"), None, self.show_tutorials))
        help_menu.addSeparator()
        help_menu.addAction(self.create_action(self.tr("&About PyGameMaker"), None, self.about))

    def create_language_menu(self, menu):
        """Create language selection submenu"""
        from core.language_manager import get_language_manager
        from PySide6.QtGui import QActionGroup, QIcon

        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()

        # Create action group for radio buttons
        self.language_action_group = QActionGroup(self)
        self.language_action_group.setExclusive(True)

        # Hotkey mapping: language code -> hotkey character
        # Each hotkey should be unique and present in the language name
        # Uses & before the letter to create underlined hotkey (e.g., "&English" -> E)
        language_hotkeys = {
            'en': 'E',  # English
            'fr': 'F',  # Français
            'es': 'S',  # eSpañol (E taken by English)
            'de': 'D',  # Deutsch
            'it': 'I',  # Italiano
            'pt': 'P',  # Português
            'ru': 'R',  # Русский (use R for Russian)
            'uk': 'U',  # Українська (use U for Ukrainian)
            'sl': 'L',  # SLovenščina (S taken by Spanish)
        }

        def add_hotkey_to_name(name, code):
            """Insert & before the hotkey character in the language name"""
            hotkey = language_hotkeys.get(code)
            if not hotkey:
                return name
            # Find the hotkey character (case-insensitive)
            idx = name.lower().find(hotkey.lower())
            if idx >= 0:
                return name[:idx] + '&' + name[idx:]
            return name

        # Separate languages into available and unavailable
        available_languages = []
        unavailable_languages = []

        for code, name, flag in language_manager.get_available_languages():
            if language_manager.is_translation_available(code) or code == 'en':
                available_languages.append((code, name, flag))
            else:
                unavailable_languages.append((code, name, flag))

        # Add available languages first
        for code, name, flag in available_languages:
            # Add hotkey to name
            display_name = add_hotkey_to_name(name, code)
            # Try to load flag icon, fall back to emoji text
            flag_path = language_manager.get_flag_icon_path(code)
            if flag_path and flag_path.exists():
                action = menu.addAction(QIcon(str(flag_path)), display_name)
            else:
                action = menu.addAction(f"{flag} {display_name}")
            action.setCheckable(True)
            action.setData(code)

            action.blockSignals(True)
            action.setChecked(code == current_lang)
            action.blockSignals(False)

            action.triggered.connect(lambda checked, lang=code: self.change_language(lang))
            self.language_action_group.addAction(action)

        # Add separator if there are unavailable languages
        if unavailable_languages:
            menu.addSeparator()

            # Add unavailable languages
            for code, name, flag in unavailable_languages:
                # Add hotkey to name (even for unavailable, for consistency)
                display_name = add_hotkey_to_name(name, code)
                flag_path = language_manager.get_flag_icon_path(code)
                if flag_path and flag_path.exists():
                    action = menu.addAction(QIcon(str(flag_path)), f"{display_name} (translation not available)")
                else:
                    action = menu.addAction(f"{flag} {display_name} (translation not available)")
                action.setCheckable(True)
                action.setData(code)

                action.blockSignals(True)
                action.setChecked(code == current_lang)
                action.blockSignals(False)

                action.triggered.connect(lambda checked, lang=code: self.change_language(lang))
                self.language_action_group.addAction(action)

    def change_language(self, language_code: str):
        """Change the application language"""
        from core.language_manager import get_language_manager
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import QCoreApplication

        language_manager = get_language_manager()

        # Get language name for display
        lang_name = ""
        for code, name, flag in language_manager.get_available_languages():
            if code == language_code:
                lang_name = name
                break

        # Set the language
        success = language_manager.set_language(language_code)

        # Process events to ensure translation changes are fully applied
        # This is critical when switching TO English - the translator removal must be processed
        QCoreApplication.processEvents()

        if success or language_code == 'en':
            # Save config to ensure language setting is persisted
            from utils.config import Config
            Config.save()

            # Inform user to restart manually
            if language_code == 'en':
                title = "Language Changed"
                message = (
                    f"Language changed to {lang_name}.\n\n"
                    "Please close and restart the IDE for the change to take effect.")
            else:
                title = QCoreApplication.translate("PyGameMakerIDE", "Language Changed")
                message = QCoreApplication.translate("PyGameMakerIDE",
                    "Language changed to {0}.\n\n"
                    "Please close and restart the IDE for the change to take effect.").format(lang_name)

            QMessageBox.information(self, title, message)
        else:
            # Translation file not found
            # Use QCoreApplication.translate() for consistency
            title = QCoreApplication.translate("PyGameMakerIDE", "Translation Not Available")
            message = QCoreApplication.translate("PyGameMakerIDE",
                "Translation file for {0} is not available.\n\n"
                "The language has been set, but the interface will remain in English until "
                "a translation file is provided.\n\n"
                "Expected file: translations/pygamemaker_{1}.qm").format(lang_name, language_code)

            QMessageBox.warning(self, title, message)



    def toggle_auto_save_zip(self):
        """Toggle auto-save to zip mode"""
        enabled = self.auto_save_zip_action.isChecked()

        if self.project_manager:
            self.project_manager.set_auto_save_as_zip(enabled)

            if enabled:
                # Check if project is from zip
                if self.project_manager.is_project_from_zip():
                    QMessageBox.information(
                        self,
                        self.tr("Auto-Save to Zip Enabled"),
                        self.tr("The project will now automatically save to the original zip file.")
                    )
                else:
                    # Offer to export current project as zip
                    reply = QMessageBox.question(
                        self,
                        self.tr("Export as Zip?"),
                        self.tr("Would you like to export the current project as a zip file now?\n\n"
                            "This will allow auto-save to work with the zip file."),
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        self.export_project_zip()
            else:
                self.update_status(self.tr("Auto-save to zip disabled"))

    def toggle_auto_save(self):
        """Toggle auto-save on/of"""
        enabled = self.auto_save_action.isChecked()

        if self.project_manager:
            # Get current interval from project manager or default to 30 seconds
            current_interval = getattr(self.project_manager, 'auto_save_interval', 30000)
            self.project_manager.set_auto_save(enabled, current_interval)

            # Persist to the editor config that startup reads, so the menu
            # toggle survives a restart and stays in sync with the dialog and
            # the checkbox init (audit M6).
            from utils.config import Config
            Config.set_editor_config(auto_save_enabled=enabled)

            if enabled:
                self.update_status(self.tr("Auto-save enabled"))
                QMessageBox.information(
                    self,
                    self.tr("Auto-Save Enabled"),
                    self.tr("Your project will be automatically saved every {0} seconds.").format(current_interval // 1000)
                )
            else:
                self.update_status(self.tr("Auto-save disabled"))
                QMessageBox.information(
                    self,
                    self.tr("Auto-Save Disabled"),
                    self.tr("Remember to save your project manually (Ctrl+S).")
                )

    def show_auto_save_settings(self):
        """Show auto-save settings dialog"""
        from dialogs.auto_save_dialog import AutoSaveSettingsDialog

        # Get current settings
        if self.project_manager:
            current_enabled = self.project_manager.auto_save_enabled
            current_interval = self.project_manager.auto_save_interval // 1000  # Convert to seconds
        else:
            current_enabled = True
            current_interval = 30

        # Show dialog
        dialog = AutoSaveSettingsDialog(current_enabled, current_interval, self)
        if dialog.exec():
            enabled, interval_seconds = dialog.get_settings()

            # Apply settings
            if self.project_manager:
                self.project_manager.set_auto_save(enabled, interval_seconds * 1000)

                # Update menu checkbox
                self.auto_save_action.setChecked(enabled)

                # Persist to the SAME store startup reads (editor config, in
                # minutes). The old top-level 'auto_save_interval' (seconds)
                # key was never read by anyone and 'auto_save_enabled' drove
                # only the menu checkbox, so the dialog's choice evaporated on
                # restart while the timer re-armed from editor config (audit
                # M6). Sub-minute intervals clamp to 1 minute on persistence
                # (editor-config granularity); the live session still uses the
                # exact seconds via set_auto_save above.
                from utils.config import Config
                Config.set_editor_config(
                    auto_save_enabled=enabled,
                    auto_save_interval=max(1, round(interval_seconds / 60)),
                )

                self.update_status(self.tr("Auto-save settings updated"))





    def create_toolbar(self):
        toolbar = self.addToolBar(self.tr("Main"))
        toolbar.setObjectName("MainToolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        # Reuse the QAction instances from the menus so a single Qt object
        # drives both menu and toolbar — enable/disable state from
        # update_ui_state() then applies to the toolbar automatically.
        # Apply icons here (the menu definitions stayed iconless).
        style = self.style()

        def _icon(icon_name: str):
            try:
                pixmap_enum = getattr(QStyle.StandardPixmap, icon_name, None)
                if pixmap_enum is not None:
                    icon = style.standardIcon(pixmap_enum)
                    if not icon.isNull():
                        return icon
            except Exception:
                pass
            return None

        def _attach(action, icon_name, tooltip, icon=None):
            """Set the toolbar icon + tooltip on a shared menu action.

            ``tooltip`` is the descriptive hover text the user sees on the
            toolbar (e.g., "New Project (Ctrl+N)"). Setting it via
            setToolTip on the QAction also improves the menu hover tooltip,
            which is fine — descriptive tooltips help in both contexts.

            Pass an explicit ``icon`` (QIcon) to override the standard-pixmap
            lookup — used for the painted/tinted toolbar icons below.
            """
            if icon is None:
                icon = _icon(icon_name)
            if icon is not None:
                action.setIcon(icon)
            action.setToolTip(tooltip)
            toolbar.addAction(action)

        # Icon foreground that contrasts with the toolbar background, so
        # tinted icons stay legible on both light and dark themes.
        _icon_fg = _contrasting_icon_color(toolbar.palette())

        # Project group ------------------------------------------------
        _attach(self.new_project_action,  "SP_FileIcon",        self.tr("New Project (Ctrl+N)"))
        _attach(self.open_project_action, "SP_DialogOpenButton", self.tr("Open Project (Ctrl+O)"))
        _attach(self.save_project_action, "SP_DialogSaveButton", self.tr("Save Project (Ctrl+S)"))

        toolbar.addSeparator()

        # Build group --------------------------------------------------
        _attach(self.test_game_action,   "SP_MediaPlay",         self.tr("Test Game (F5)"), icon=_green_play_icon())
        _attach(self.debug_game_action,  "SP_ComputerIcon",      self.tr("Debug Game (F6)"))
        _attach(self.export_game_action, "SP_DialogApplyButton", self.tr("Export Game…"))

        toolbar.addSeparator()

        # Asset import group -------------------------------------------
        _attach(self.import_sprite_action, "SP_FileIcon",     self.tr("Import Sprite…"))
        _attach(self.import_sound_action,  "SP_MediaVolume",  self.tr("Import Sound…"), icon=_tinted_standard_icon(style, "SP_MediaVolume", _icon_fg))

        toolbar.addSeparator()

        # [1.0] Thymio quick-add toolbar button hidden — see docs/POST_1_0_REFACTOR.md.
        # The show_thymio_event_selector method is retained for the planned extension.
        # self.thymio_toolbar_action = self.create_action(
        #     self.tr("Thymio"), None, self.show_thymio_event_selector, "SP_DriveNetIcon"
        # )
        # self.thymio_toolbar_action.setToolTip(self.tr("Add Thymio Event"))
        # toolbar.addAction(self.thymio_toolbar_action)
        #
        # toolbar.addSeparator()

        # Window-mode toggle — doubles as the recovery affordance when a
        # floating editor has been dragged off-screen (clicking "Tabbed"
        # snaps every detached window back into the tab strip).
        self.window_mode_action = self.create_action(
            self.tr("Tabbed"), None, self.toggle_window_mode, None
        )
        self.window_mode_action.setToolTip(
            self.tr("Toggle between Tabbed and Floating editor layouts")
        )
        self._update_window_mode_action_label()
        toolbar.addAction(self.window_mode_action)

        toolbar.update()

    def create_main_widget(self):
        """Modified to include editor tabs in center"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Asset tree, with a filter box above it
        try:
            self.asset_tree = AssetTreeWidget(self)
        except Exception as e:
            logger.error(f"Failed to create AssetTreeWidget: {e}")
            import traceback
            traceback.print_exc()

        asset_panel = QWidget()
        asset_panel_layout = QVBoxLayout(asset_panel)
        asset_panel_layout.setContentsMargins(0, 0, 0, 0)
        asset_panel_layout.setSpacing(2)

        self.asset_filter_box = QLineEdit()
        self.asset_filter_box.setPlaceholderText(self.tr("Filter assets…"))
        self.asset_filter_box.setClearButtonEnabled(True)
        self.asset_filter_box.textChanged.connect(self.asset_tree.apply_asset_filter)
        asset_panel_layout.addWidget(self.asset_filter_box)
        asset_panel_layout.addWidget(self.asset_tree)

        asset_panel.setMinimumWidth(200)
        asset_panel.setMaximumWidth(300)

        # Center panel - NEW: Tabbed editors
        center_panel = self.create_center_panel_with_editors()

        # Right panel - Properties panel
        from PySide6.QtWidgets import QStackedWidget

        self.right_panel_stack = QStackedWidget()
        self.right_panel_stack.setMinimumWidth(250)

        # Properties panel (index 0)
        self.properties_panel = EnhancedPropertiesPanel()
        self.right_panel_stack.addWidget(self.properties_panel)

        # Start with properties panel visible
        self.right_panel_stack.setCurrentIndex(0)

        # Add panels to main splitter
        self.main_splitter.addWidget(asset_panel)
        self.main_splitter.addWidget(center_panel)
        self.main_splitter.addWidget(self.right_panel_stack)

        # Set proportions: asset tree, editors, properties
        self.main_splitter.setSizes([250, 800, 300])
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setCollapsible(2, True)  # Allow right panel to collapse

        # Store default sizes for restoring right panel
        self._default_splitter_sizes = [250, 800, 300]

        layout.addWidget(self.main_splitter)

    def create_center_panel_with_editors(self):
        """Create center panel with tabbed editors"""
        from widgets.welcome_tab import WelcomeTab

        center_widget = QWidget()
        layout = QVBoxLayout(center_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget for editors
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)

        # Store reference to open editors, keyed by a composite
        # "<category>:<name>" so a room and an object that legally share a name
        # don't collide (L5).
        self.open_editors = {}  # "<category>:<name>" -> editor_widget
        # Composite key -> DetachedEditorWindow for editors floated out of the
        # tab strip. Editors in this dict still appear in self.open_editors
        # but are NOT in self.editor_tabs.
        self.detached_editor_windows = {}

        # Welcome tab (default)
        self.welcome_tab = WelcomeTab(self)
        self._add_welcome_tab()

        layout.addWidget(self.editor_tabs)
        return center_widget

    def _add_welcome_tab(self):
        """(Re-)add the welcome tab without a close button.

        The tab title is self.tr("Welcome"), so it must never be identified
        by its text (translated UIs would mismatch); close_editor_tab guards
        by widget identity instead.
        """
        from PySide6.QtWidgets import QTabBar
        index = self.editor_tabs.addTab(self.welcome_tab, self.tr("Welcome"))
        tab_bar = self.editor_tabs.tabBar()
        tab_bar.setTabButton(index, QTabBar.RightSide, None)
        tab_bar.setTabButton(index, QTabBar.LeftSide, None)


    def on_tab_changed(self, index):
        """Handle tab change"""
        widget = self.editor_tabs.widget(index)

        if not widget:
            return

        # Update properties panel visibility and context based on current editor type
        if hasattr(widget, '__class__'):
            editor_class = widget.__class__.__name__

            if editor_class == 'RoomEditor':
                # Room editor is active - restore right panel with room properties
                self._restore_right_panel()

                try:
                    room_name = widget.asset_name
                    room_data = widget.get_data() if hasattr(widget, 'get_data') else widget.current_room_properties

                    self.properties_panel.set_room_editor_context(widget, room_name, room_data)

                except Exception as e:
                    logger.error(f"Error setting room editor context: {e}")

            elif editor_class == 'ObjectEditor':
                # Object editor is active - COLLAPSE right panel (object editor has its own properties)
                self._collapse_right_panel()

                # Clear the context since we're not using the external properties panel
                self.clear_properties_contexts()

            else:
                # Other editor type - restore right panel and clear contexts
                self._restore_right_panel()
                self.clear_properties_contexts()

        else:
            # Welcome tab or other non-editor - restore right panel
            self._restore_right_panel()
            self.clear_properties_contexts()

    def clear_properties_contexts(self):
        """Clear all properties panel contexts"""
        if hasattr(self, 'properties_panel'):
            # Clear the current editor references
            if hasattr(self.properties_panel, 'current_object_editor'):
                self.properties_panel.current_object_editor = None
            if hasattr(self.properties_panel, 'current_room_editor'):
                self.properties_panel.current_room_editor = None

            if hasattr(self.properties_panel, 'clear_room_context'):
                self.properties_panel.clear_room_context()
            if hasattr(self.properties_panel, 'clear_object_context'):
                self.properties_panel.clear_object_context()

    def _collapse_right_panel(self):
        """Collapse the right panel to give more space to the center editor"""
        if hasattr(self, 'main_splitter') and hasattr(self, 'right_panel_stack'):
            # Store current sizes before collapsing (only if right panel is visible)
            current_sizes = self.main_splitter.sizes()
            if current_sizes[2] > 0:
                self._last_splitter_sizes = current_sizes

            # Hide the right panel and redistribute space to center
            self.right_panel_stack.hide()
            # Set right panel size to 0, add its space to center
            new_sizes = [current_sizes[0], current_sizes[1] + current_sizes[2], 0]
            self.main_splitter.setSizes(new_sizes)

    def _restore_right_panel(self):
        """Restore the right panel to its previous size"""
        if hasattr(self, 'main_splitter') and hasattr(self, 'right_panel_stack'):
            # Show the right panel
            self.right_panel_stack.show()
            if hasattr(self, 'properties_panel'):
                self.properties_panel.show()

            # Restore previous sizes or use defaults
            if hasattr(self, '_last_splitter_sizes'):
                self.main_splitter.setSizes(self._last_splitter_sizes)
            elif hasattr(self, '_default_splitter_sizes'):
                self.main_splitter.setSizes(self._default_splitter_sizes)

    def create_status_bar(self):
        self.status_bar = self.statusBar()

        self.status_label = QLabel(self.tr("Ready"))
        self.status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.project_label = QLabel(self.tr("No project loaded"))
        self.status_bar.addPermanentWidget(self.project_label)

    def setup_connections(self):
        self.asset_tree.asset_selected.connect(self.on_asset_selected, Qt.ConnectionType.UniqueConnection)
        self.asset_tree.asset_imported.connect(self.on_asset_imported, Qt.ConnectionType.UniqueConnection)
        # Connect the double-click signal
        self.asset_tree.asset_double_clicked.connect(self.on_asset_double_clicked, Qt.ConnectionType.UniqueConnection)
        # Connect asset deletion signal to update open editors
        self.asset_tree.assetDeleted.connect(self.on_asset_deleted, Qt.ConnectionType.UniqueConnection)

        self.project_manager.project_loaded.connect(self.on_project_loaded, Qt.ConnectionType.UniqueConnection)
        self.project_manager.project_saved.connect(self.on_project_saved, Qt.ConnectionType.UniqueConnection)
        self.project_manager.status_changed.connect(self.update_status, Qt.ConnectionType.UniqueConnection)
        # Refresh the window title when the project's dirty state flips so
        # the trailing " *" appears as soon as the user makes an unsaved
        # change and clears when they save. Qt's UniqueConnection only
        # works with bound methods (not lambdas), so we route through
        # `_on_dirty_changed` to keep the connection deduplicated across
        # re-entries of setup_connections.
        self.project_manager.dirty_changed.connect(
            self._on_dirty_changed, Qt.ConnectionType.UniqueConnection
        )

    def create_action(self, text, shortcut, slot, icon_name=None):
        """Create a QAction with optional icon, shortcut, and slot

        Args:
            text: Action text
            shortcut: Keyboard shortcut (e.g., "Ctrl+S")
            slot: Function to call when action is triggered
            icon_name: QStyle.StandardPixmap enum name (e.g., "SP_FileIcon")

        Returns:
            QAction: The created action
        """
        action = QAction(text, self)

        if shortcut:
            action.setShortcut(shortcut)

        if icon_name:
            try:
                style = self.style()
                # Try to get the enum value from QStyle.StandardPixmap
                pixmap_enum = getattr(QStyle.StandardPixmap, icon_name, None)
                if pixmap_enum is not None:
                    icon = style.standardIcon(pixmap_enum)
                    if not icon.isNull():
                        action.setIcon(icon)
                else:
                    # Invalid icon name provided
                    logger.warning(f"⚠️ Warning: Invalid icon name '{icon_name}' - no such StandardPixmap")
            except AttributeError as e:
                logger.warning(f"⚠️ Warning: Could not access QStyle.StandardPixmap.{icon_name}: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Warning: Could not load icon '{icon_name}': {e}")

        if slot:
            action.triggered.connect(slot)

        return action

    def update_recent_projects_menu(self, menu):
        menu.clear()

        recent_projects = Config.get("recent_projects", [])

        if not recent_projects:
            action = menu.addAction(self.tr("No recent projects"))
            action.setEnabled(False)
            return

        for project_path in recent_projects[:10]:
            if Path(project_path).exists():
                project_name = Path(project_path).name
                action = menu.addAction(project_name)
                action.triggered.connect(lambda checked, path=project_path: self.open_recent_project(path))

        # Add separator and clear option
        menu.addSeparator()
        clear_action = menu.addAction(self.tr("Clear Recent Projects"))
        clear_action.triggered.connect(self.clear_recent_projects)

    def clear_recent_projects(self):
        """Clear the recent projects list"""
        reply = QMessageBox.question(
            self,
            self.tr("Clear Recent Projects"),
            self.tr("Are you sure you want to clear the recent projects list?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            Config.set("recent_projects", [])
            Config.save()
            # Update the menu
            self.update_recent_projects_menu(self.recent_projects_menu)
            # Refresh the Welcome tab's inline list too
            if hasattr(self, 'welcome_tab') and hasattr(self.welcome_tab, 'refresh_recent_projects'):
                self.welcome_tab.refresh_recent_projects()
            self.update_status(self.tr("Recent projects list cleared"))




    # ------------------------------------------------------------------
    # Bundled-samples protection helpers
    # ------------------------------------------------------------------
    #
    # The Welcome tab ships a samples/ folder of native pygm2 projects
    # (maze_1..4, treasure). Those folders are tracked in git and must
    # NEVER be modified by the IDE — otherwise editing inside a sample
    # leaks back into the repo, and Dropbox / file-system permissions
    # produce confusing PermissionError noise when the IDE tries to
    # auto-save.
    #
    # We enforce "samples/ is read-only" structurally rather than via a
    # filesystem chmod (which Dropbox + Windows happily ignore): any
    # path under samples/ that reaches load_project gets transparently
    # copied to the user's working area first, and the copy is what the
    # IDE opens.
    # ------------------------------------------------------------------

















    def _iter_open_editors(self):
        """Yield every open editor widget regardless of whether it's currently
        in a tab or floated. Used by cross-editor refresh paths so that
        detached windows stay in sync with tabbed ones."""
        seen = set()
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if widget is None or widget is self.welcome_tab:
                continue
            seen.add(id(widget))
            yield widget
        for editor in self.open_editors.values():
            if editor is None or id(editor) in seen:
                continue
            yield editor






















































    def on_object_editor_activated(self, object_name: str, object_properties: dict):
        """Handle object editor activation"""
        logger.debug(f"🚨🚨🚨 IDE: on_object_editor_activated called for {object_name}")
        logger.debug(f"🚨 IDE: properties_panel exists? {hasattr(self, 'properties_panel')}")
        logger.debug(f"🚨 IDE: properties_panel type: {type(self.properties_panel).__name__ if hasattr(self, 'properties_panel') else 'N/A'}")

        # Find the object editor widget
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if (hasattr(widget, '__class__') and
                widget.__class__.__name__ == 'ObjectEditor' and
                hasattr(widget, 'asset_name') and
                widget.asset_name == object_name):

                # Set properties panel context
                self.properties_panel.set_object_editor_context(widget, object_name, object_properties)

                break

    def on_room_editor_activated(self, room_name: str, room_properties: dict):
        """Handle room editor activation"""
        # Find the room editor widget
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if (hasattr(widget, '__class__') and
                widget.__class__.__name__ == 'RoomEditor' and
                hasattr(widget, 'asset_name') and
                widget.asset_name == room_name):

                # Set properties panel context
                self.properties_panel.set_room_editor_context(widget, room_name, room_properties)

                break





    def update_window_title(self):
        """Update the main window title to reflect the loaded project.

        Format follows the Windows/Linux convention "<Document> — <App>"
        so the project name shows in taskbar previews and Alt-Tab
        switchers (those clip the right-hand app name first). A trailing
        " *" marks the project as having unsaved changes, matching the
        per-editor dirty marker used by BaseEditor.
        """
        if self.current_project_data:
            project_name = self.current_project_data.get('name', 'Untitled')
            dirty = ' *' if self.project_manager.is_dirty() else ''
            title = f"{project_name}{dirty} — PyGameMaker IDE"
        else:
            title = "PyGameMaker IDE"
        self.setWindowTitle(title)

    def _on_dirty_changed(self, _is_dirty: bool):
        """Slot bound to project_manager.dirty_changed.

        Kept as a real bound method (rather than the obvious lambda)
        because Qt's UniqueConnection flag requires a pointer to a member
        function — passing a lambda fails with a runtime warning and the
        connection silently becomes non-unique (re-entries of
        setup_connections would then double-fire the slot).
        """
        self.update_window_title()

    def update_ui_state(self):
        has_project = self.current_project_path is not None

        # Import-as-new-project actions create a project from a source file, so
        # they must stay enabled even when no project is currently loaded. The
        # generic "Import" substring match below would otherwise grey them out.
        always_enabled_imports = set()
        for attr in ('import_roberta_action', 'import_gmk_action', 'thymio_import_roberta_action'):
            if hasattr(self, attr):
                always_enabled_imports.add(getattr(self, attr))

        for action in self.findChildren(QAction):
            if action in always_enabled_imports:
                action.setEnabled(True)
                continue
            # Actions marked exempt (e.g. the Welcome tab's "More options"
            # entry points) must stay usable with no project loaded; the
            # findChildren sweep would otherwise grey them via the Import/
            # Create substring match below. See WelcomeTab._dropdown_button.
            if action.property("pygm_always_enabled"):
                action.setEnabled(True)
                continue
            if action.text() in [self.tr("Save Project"), self.tr("Save Project As..."), self.tr("Project Settings...")]:
                action.setEnabled(has_project)
            elif self.tr("Import") in action.text() or self.tr("Create") in action.text():
                action.setEnabled(has_project)
            elif action.text() in [self.tr("Test Game"), self.tr("Debug Game"), self.tr("Build Game"),
                                self.tr("Build and Run"), self.tr("Export Game...")]:
                action.setEnabled(has_project)

        # Enable/disable export actions based on project state
        if hasattr(self, 'export_html5_action'):
            self.export_html5_action.setEnabled(has_project)
        if hasattr(self, 'export_zip_action'):
            self.export_zip_action.setEnabled(has_project)
        if hasattr(self, 'export_kivy_action'):
            self.export_kivy_action.setEnabled(has_project)
        if hasattr(self, 'export_aseba_action'):
            self.export_aseba_action.setEnabled(has_project)
        if hasattr(self, 'export_project_action'):
            self.export_project_action.setEnabled(has_project)
        # Tools-menu items that only make sense with an open project
        if hasattr(self, 'validate_project_action'):
            self.validate_project_action.setEnabled(has_project)
        if hasattr(self, 'migrate_project_action'):
            self.migrate_project_action.setEnabled(has_project)
        if hasattr(self, 'show_trash_action'):
            self.show_trash_action.setEnabled(has_project)
        if hasattr(self, 'show_unused_assets_action'):
            self.show_unused_assets_action.setEnabled(has_project)
        if hasattr(self, 'clean_project_action'):
            self.clean_project_action.setEnabled(has_project)
        if hasattr(self, 'show_orphaned_files_action'):
            self.show_orphaned_files_action.setEnabled(has_project)
        # Thymio Add Event/Action target the active object editor, which
        # cannot exist without an open project.
        if hasattr(self, 'thymio_add_event_action'):
            self.thymio_add_event_action.setEnabled(has_project)
        if hasattr(self, 'thymio_add_action_action'):
            self.thymio_add_action_action.setEnabled(has_project)
        # File-menu / toolbar shared actions. Save and Save As require a
        # project; New and Open stay always-enabled (they're entry points).
        # These are stored as attributes specifically so update_ui_state
        # can drive both the menu copy and the toolbar copy through one
        # call (Qt shares QAction state across containers).
        if hasattr(self, 'save_project_action'):
            self.save_project_action.setEnabled(has_project)
        if hasattr(self, 'save_project_as_action'):
            self.save_project_as_action.setEnabled(has_project)
        if hasattr(self, 'close_project_action'):
            self.close_project_action.setEnabled(has_project)
        # Toolbar quick-add for Thymio events — same constraint as the
        # submenu Add Event/Action (needs an object editor, which needs
        # a project as the minimum precondition).
        if hasattr(self, 'thymio_toolbar_action'):
            self.thymio_toolbar_action.setEnabled(has_project)
        # Enable/disable build actions based on project state
        if hasattr(self, 'test_game_action'):
            self.test_game_action.setEnabled(has_project)
        if hasattr(self, 'debug_game_action'):
            self.debug_game_action.setEnabled(has_project)
        if hasattr(self, 'build_game_action'):
            self.build_game_action.setEnabled(has_project)
        if hasattr(self, 'build_and_run_action'):
            self.build_and_run_action.setEnabled(has_project)
        if hasattr(self, 'export_game_action'):
            self.export_game_action.setEnabled(has_project)

        # Enable/disable Build menu based on project state
        if hasattr(self, 'build_menu'):
            self.build_menu.setEnabled(has_project)

        if has_project:
            self.project_label.setText(self.tr("Project: {0}").format(self.current_project_data['name']))
        else:
            self.project_label.setText(self.tr("No project loaded"))

    def update_status(self, message):
        self.status_label.setText(message)

        QTimer.singleShot(3000, lambda: self.status_label.setText(self.tr("Ready")))

    def refresh_open_object_editors(self):
        """Refresh sprite lists in all open object editors (tabbed + floated)."""
        # The IDE's live project data already holds a just-imported sprite,
        # which isn't written to project.json until save. Push it directly so
        # floated editors — whose parent chain may not reach the IDE, so they
        # can't find this data themselves — still pick up the new sprite.
        sprites = None
        if self.current_project_data:
            sprites = self.current_project_data.get('assets', {}).get('sprites')

        for widget in self._iter_open_editors():
            if hasattr(widget, 'load_project_assets'):
                widget.load_project_assets()
                logger.debug(f"🔄 Refreshed sprites in object editor: {getattr(widget, 'asset_name', '?')}")
            if sprites is not None and hasattr(widget, 'apply_available_sprites'):
                widget.apply_available_sprites(sprites)

    def refresh_object_sprites(self, object_name: str, old_sprite: str, new_sprite: str):
        """Refresh object sprites in room editors when they change.

        Walks both tabbed and detached editors so floated rooms see the
        new sprite assignment without a manual refresh.
        """
        logger.debug(f"Refreshing sprite for object {object_name}: {old_sprite} -> {new_sprite}")

        for widget in self._iter_open_editors():
            if hasattr(widget, 'room_canvas') and hasattr(widget, 'object_palette'):
                # Update room canvas with latest project data so it sees the new sprite assignment
                if hasattr(widget.room_canvas, 'set_project_info') and self.current_project_data:
                    project_path = self.current_project_path if hasattr(self, 'current_project_path') else None
                    widget.room_canvas.set_project_info(project_path, self.current_project_data)

                # Clear sprite cache for the object (set_project_info clears all, but be explicit)
                if hasattr(widget.room_canvas, 'sprite_cache') and object_name in widget.room_canvas.sprite_cache:
                    del widget.room_canvas.sprite_cache[object_name]

                # Refresh the object palette
                if hasattr(widget.object_palette, 'refresh_object_list'):
                    widget.object_palette.refresh_object_list()

                # Force canvas update
                widget.room_canvas.update()

        # DON'T refresh sprite combo here - it causes loops
        # The combo will be refreshed when the object editor updates



    def restore_geometry(self):
        geometry = Config.get("window_geometry")
        state = Config.get("window_state")

        if geometry:
            self.restoreGeometry(geometry)

        if state:
            self.restoreState(state)

    def safe_disconnect_signal(self, signal, slot=None):
        """Safely disconnect a signal, avoiding warnings"""
        if not signal:
            return False
        try:
            if slot:
                # Disconnect specific slot
                try:
                    signal.disconnect(slot)
                    return True
                except (RuntimeError, TypeError):
                    # Connection doesn't exist, that's fine
                    return False
            else:
                # Disconnect all connections
                if hasattr(signal, 'isSignalConnected') and signal.isSignalConnected():
                    signal.disconnect()
                    return True
                else:
                    signal.disconnect()
                    return True
        except (RuntimeError, TypeError, AttributeError):
            return False

    def closeEvent(self, event):
        Config.set("window_geometry", self.saveGeometry())
        Config.set("window_state", self.saveState())

        if self.project_manager.is_dirty():
            reply = QMessageBox.question(
                self, self.tr("Unsaved Changes"),
                self.tr("You have unsaved changes. Do you want to save before closing?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                # Pull any in-editor edits into the project first, otherwise
                # 'Save' would persist the project without the unsaved editor
                # work it was meant to preserve (audit M12).
                self._flush_open_editors()
                if not self.save_project():
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        # Close any detached editor windows without trying to reattach —
        # the IDE itself is going away, so there's nowhere to attach to.
        for window in list(self.detached_editor_windows.values()):
            window.reattach_on_close = False

        # Same for a floated tutorial window: don't try to re-dock into
        # an IDE that is tearing down.
        tutorial_win = getattr(self, '_tutorial_detached_window', None)
        if tutorial_win is not None:
            tutorial_win.reattach_on_close = False

        # Don't orphan a running Test Game: the subprocess outlives the IDE
        # otherwise (closeEvent never touched it). Past the cancel paths above,
        # so a cancelled close leaves the game running.
        self.stop_game()

        # Remove the temp extraction dir of an open .zip project so it isn't
        # left behind in TEMP for the session (close_project is never called;
        # _reset_zip_state rmtrees it without the side effects of a full
        # close_project during teardown) (L7).
        try:
            self.project_manager._reset_zip_state()
        except Exception:
            pass

        event.accept()


    def changeEvent(self, event):
        """Handle events, including language changes"""
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.Type.LanguageChange:
            # Recreate menu bar with new translations
            logger.debug("🔄 Language change event detected, recreating menus...")
            self.menuBar().clear()
            self.create_menu_bar()

            # Remove existing toolbar before creating new one
            existing_toolbar = self.findChild(QToolBar, "MainToolbar")
            if existing_toolbar:
                self.removeToolBar(existing_toolbar)
                existing_toolbar.deleteLater()
            self.create_toolbar()

            # Update UI state to enable/disable actions based on project state
            self.update_ui_state()
            logger.debug("✅ Menus and toolbars recreated with new language")

        # Call parent class handler
        super().changeEvent(event)
