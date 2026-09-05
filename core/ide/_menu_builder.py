#!/usr/bin/env python3
"""Menu bar / toolbar / status bar construction for :class:`PyGameMakerIDE`,
plus the generic ``create_action`` helper and the recent-projects menu.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2) -- the LAST File 2 cluster, deliberately: it wires together a call
to nearly every action from every other mixin (``self.new_project``,
``self.export_game``, ``self.build_and_run``, ...), so doing it last means
any slot missed by an earlier extraction would already have surfaced as an
``AttributeError`` at menu-construction time, not been silently masked here.
A mixin -- ``self`` / ``self.tr()`` / siblings resolve on the concrete
window through the full mixin chain.

The three module-level icon-helper functions (``_green_play_icon``,
``_contrasting_icon_color``, ``_tinted_standard_icon``) are used only by
``create_toolbar``/``create_action`` and move here with them, same
precedent as ``_export.py``'s ``ExportThread``/``_ExportProgressDialog``.

No patch-target moves: no test mocks anything from this cluster
(``QMessageBox``, ``QAction``, etc. are all exercised for real against a
constructed menu/toolbar, never patched) -- confirmed by searching
``tests/`` for every method/function name below before editing.
"""

from pathlib import Path
from PySide6.QtWidgets import QLabel, QProgressBar, QStyle, QMessageBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction

from utils.config import Config
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


class MenuBuilderMixin:

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

    def create_status_bar(self):
        self.status_bar = self.statusBar()

        self.status_label = QLabel(self.tr("Ready"))
        self.status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.project_label = QLabel(self.tr("No project loaded"))
        self.status_bar.addPermanentWidget(self.project_label)

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

