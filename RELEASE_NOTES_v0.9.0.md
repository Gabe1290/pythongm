# PyGameMaker v0.9.0 Release Notes

**Release Date:** January 2026

PyGameMaker is a GameMaker-style visual game development IDE for creating 2D games with Python.

## New Features

- **Room Preview Panel** - Rooms now display a visual preview in the properties panel when selected
- **Spanish Language Support** - Complete Español translation (650+ strings)
- **Russian Language Support** - Full Russian translation with flag icon
- **Language Menu Improvements** - Flag icons for easier language selection
- **New Actions** - Added `create_instance`, `jump_to_start`, `jump_to_random`, and `show_message` actions
- **Expression Functions** - Support for `random()`, `irandom()`, and `choose()` in expressions
- **Self Sprite Reference** - Added `<self>` option to `set_sprite` action for current sprite animation

## Bug Fixes

- Fixed infinite loop when navigating to next/previous room at boundaries
- Fixed room property cross-contamination in properties panel
- Fixed broken dependency checks in EXE and Linux exporters
- Fixed game to start at first room in room_order
- Fixed keyboard event removal in object editor
- Fixed inconsistent icon sizes in asset tree
- Fixed Blockly preset filtering issues

## UI/UX Improvements

- Events tree now expands by default to show actions immediately
- Right panel automatically collapses when object editor is active
- Room editor properties update correctly when switching rooms

## Testing & Quality

- Added comprehensive automated testing with GitHub Actions CI/CD
- 5,900+ lines of test code covering:
  - 81 ActionExecutor tests
  - 19 event system tests
  - Runtime, exporter, widget, and integration tests
- Code quality improvements with flake8 linting

## Supported Languages

English, French, German, Italian, Slovenian, Spanish, Ukrainian, Russian

## Export Targets

- HTML5
- Windows EXE
- Linux executable
- Kivy (mobile/cross-platform)
