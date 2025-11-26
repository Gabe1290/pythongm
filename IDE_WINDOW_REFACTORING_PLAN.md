# IDE Window Refactoring Plan

## Current Status
- Total size: 2,486 lines
- Too large to maintain effectively
- Multiple responsibilities mixed together

## Proposed Module Structure

### 1. core/ide_window.py (500 lines) - Main Window
- Window initialization
- Layout management
- Tab coordination
- Signal routing
- Imports from other modules

### 2. core/ide_menus.py (300 lines) - Menu System
- create_menubar() method
- Menu action handlers
- Context menu management
- Keyboard shortcuts

### 3. core/ide_exporters.py (400 lines) - Export Functions
- export_html5()
- export_kivy()
- export_zip()
- export_windows_exe()
- Export dialog handlers

### 4. core/ide_assets.py (600 lines) - Asset Management
- create_sprite()
- create_sound()
- create_background()
- create_object()
- create_room()
- import_* methods

### 5. core/ide_editors.py (400 lines) - Editor Management
- open_asset_editor()
- close_asset_editor()
- Editor tab management
- Edit operations (undo/redo/copy/paste)

### 6. core/ide_settings.py (286 lines) - Settings
- preferences()
- Auto-save management
- Language changing
- Settings persistence

## Implementation Strategy

1. Extract exporters first (most independent)
2. Extract settings (also independent)
3. Extract asset management
4. Extract menu system
5. Refactor main window to use extracted modules

## Manual Extraction Required
This file is too complex for automated splitting.
Requires careful extraction with import management.
