# Thymio robot — a worked multi-seam extension

This folder is a real PyGameMaker feature that lives **outside** the core
engine: programming a [Thymio](https://www.thymio.org/) educational robot —
either a screen simulation driven by the pygame runtime, or (via Aseba/Open
Roberta export) the physical robot itself. It is here to be read. Where
[`raycast_2_5d/`](../raycast_2_5d/) is the worked example for *one* seam (a
room renderer), this folder is the worked example for using nearly **every**
seam `extensions/README.md` documents at once — actions, events, an instance
overlay, an input handler, a frame-update hook, an instance-created hook, an
asset type, IDE menu/toolbar entries, an object-editor panel, and curated
Blockly categories.

Shipped **hidden by default** — see "Turning it on" below. This is a product
decision, not a limitation of the extraction: every seam here works exactly
like any other extension's, whether or not its UI is visible.

## What it does

A `thymio*`-named object (or one whose room entry sets `is_thymio`) gets a
simulated Thymio robot: differential-drive motors, 7 proximity + 2 ground
sensors, 3 RGB LEDs (top, bottom-left, bottom-right) + an 8-LED circle,
tones, 2 timers, 5 buttons — all driven by 28 actions and 14 events, the same
vocabulary the real hardware's Aseba language uses. The robot draws itself
over the room (body, LEDs, sensor rays, clickable buttons), can be driven by
keyboard/mouse for testing, and can be authored/tested standalone in a
**playground** — a simple arena editor + simulation window that doesn't need
a full game project. A finished program exports to real Aseba (`.aesl`) code
for the physical robot, or imports/exports Open Roberta Lab XML.

## The files

| File / folder | What's in it |
|---|---|
| `extension.json` | The manifest. `enabled: true` — the *loader*-level switch (existing Thymio-authored projects keep working); a separate `show_thymio_tab` config flag controls UI visibility (see below). |
| `__init__.py` | The entry point. Every `PLUGIN_*` registration in one place, each pointing into the module that owns it. |
| `actions.py` | The 28 action **schemas** (`THYMIO_ACTIONS`) and `THYMIO_TAB`, the GM80-dialog action-picker tab. |
| `handlers.py` | The 28 runtime **handlers**. `PluginExecutor` is what the loader registers in the game process; `register_thymio_actions` is the same set for the playground runner, which has no plugin loader. |
| `events.py` | The 14 robot events (`THYMIO_EVENT_TYPES`). |
| `simulator.py` | `ThymioSimulator` — differential drive, proximity/ground sensors, LEDs, tones, timers. No Qt, no pygame; pure simulation state. |
| `state.py` | The robot's per-instance state, under `instance.extension_state["thymio"]`. |
| `runtime.py` | The per-frame simulator step + sensor-event firing, run through the `after_collision` frame-update hook. |
| `renderer.py` | `ThymioRenderer` — robot body, LEDs, sensor rays, button hit-testing. `draw_robot` (in `__init__.py`) is the instance overlay that calls it. |
| `input.py` | Keyboard (arrows/space) and mouse (click a drawn button) control, through the input-handler hook. |
| `tools_menu.py` | The Tools-menu / toolbar action handlers (`configure_thymio`, `toggle_thymio_tab`, `show_thymio_playground`, `show_thymio_event_selector`, `show_thymio_action_selector`). |
| `editor/` | The playground arena-authoring editor (canvas, tool palette, elements, undo commands, color manager). |
| `playground_runner.py` | `PlaygroundRunnerWindow` — a standalone pygame-in-Qt window that runs linked objects' code against a playground arena, independent of a full game project. |
| `playground_window.py` | `ThymioPlaygroundWindow` — the live test/config window for a single robot. Uses `widgets/pygame_widget.py`'s `PygameWidget`, which stayed in core since Block World reuses it too. |
| `diagram_widget.py` | `ThymioDiagramWidget` — the interactive robot diagram the config/event/action dialogs and the object-editor panel embed. |
| `dialogs/` | The config/event/action selector dialogs. `ThymioConfigDialog` shares its scaffold with core's `BlocklyConfigDialog` via `dialogs/_block_config_dialog_base.py`, which stayed in core (genuinely shared base). |
| `object_editor_panel.py` | `ThymioEventsPanel` — the object editor's dedicated "🤖 Thymio" tab. |
| `export/` | Aseba (`.aesl`) export, Open Roberta Lab XML import/export, plus the File-menu action handlers (`export_aseba_code`, `import_roberta_xml`). |
| `blockly_categories.py` | The 8 "Thymio *" Blockly toolbox categories, the `"thymio"` preset, and its 7-language category translations. |

## How it hooks in

Every seam here is declared the same declarative way `extensions/README.md`
documents — a `PLUGIN_*` module attribute the loader (`events/plugin_loader.py`)
merges in at startup:

- `PLUGIN_ACTIONS` / `PLUGIN_EVENTS` / `PLUGIN_EVENT_BLOCKLY_MAP` — the 28
  actions and 14 events.
- `PLUGIN_FRAME_UPDATES` — steps every robot's simulator once per frame,
  after collisions (`"after_collision"` phase), and fires its sensor events.
- `PLUGIN_INSTANCE_OVERLAYS` — draws each robot over its room.
- `PLUGIN_INPUT_HANDLERS` — keyboard/mouse control of a robot's buttons.
- `PLUGIN_INSTANCE_CREATED` — attaches a simulator to a `thymio*` instance
  as its room builds.
- `PLUGIN_ASSET_TYPES` / `PLUGIN_ASSET_TREE_CATEGORIES` — "Playgrounds", the
  robot-arena asset type, behaves exactly like Rooms/Objects/Sprites in the
  asset tree and on disk.
- `PLUGIN_IDE_MENUS` / `PLUGIN_IDE_TOOLBAR` — the File-menu Aseba export/
  Roberta import entries, and (gated, see below) the Tools-menu/toolbar
  Thymio-programming UI.
- `PLUGIN_OBJECT_EDITOR_PANELS` — the dedicated "🤖 Thymio" object-editor tab.
- `PLUGIN_BLOCK_CATEGORIES` / `PLUGIN_BLOCKLY_PRESETS` /
  `PLUGIN_BLOCK_CATEGORY_TRANSLATIONS` — the Blockly toolbox categories and
  preset.

None of this required a new seam — every one of the above already existed in
`runtime/extension_hooks.py` / `core/ide_extension_points.py` / the plugin
loader before Thymio's move started, mostly built *for* this move
(`docs/THYMIO_EXTENSION_PLAN.md`'s Stage 0). Core carries no Thymio-specific
code, only these generic contracts.

## What this extension reads from core, generically

- `instance.extension_state["thymio"]` / `room.extension_state` — the
  generic per-instance/per-room dicts every extension uses instead of core
  growing feature-specific attributes.
- `widgets/pygame_widget.py`'s `PygameWidget` — the pygame-in-Qt widget
  `playground_window.py` and `playground_runner.py` both need. Stayed in
  core because Block World (a different extension) needs it too; it has
  zero Thymio-specific code itself.
- `dialogs/_block_config_dialog_base.py`'s `THYMIO_CATEGORIES` (just the 8
  category *names*, no logic) — core's own `BlocklyConfigDialog` needs the
  list to exclude these categories from the generic dialog. Deliberately
  not moved; it's shared string data, not Thymio behaviour.

## What is deliberately NOT here yet

A real, previously-undiscovered gap found while verifying this extraction:
the object editor's **Standard** event panel (reachable with the Thymio tab
off) has its own, separate Thymio awareness — a "🤖 Thymio Events"/"🤖 Thymio
Action..." context-menu path, and `python_code_parser.py`'s Python↔action-JSON
round-trip logic for `thymio.*` method calls — spread across six files under
`editors/object_editor/`. It predates this plan and was never in scope for
any of Stages A–F (they only ever touched the *dedicated* Thymio tab). See
`docs/THYMIO_EXTENSION_PLAN.md`'s Stage G5 for the itemized list; it's sized
as its own follow-up, not attempted here.

## Turning it on

Two independent switches, both currently set to match pre-refactor
(pre-extraction) behaviour:

**Loader-level** (`extension.json`'s `enabled: true`) — Thymio's actions,
events, simulator and asset type are always registered, so existing
Thymio-authored projects keep working. Disabling this via the `extensions`
config key (see `extensions/README.md`) would break any such project — not
recommended unless you know none exist.

```json
"extensions": { "thymio": false }
```

**UI-level** (`show_thymio_tab` config, default `false`) — the object
editor's dedicated Thymio tab, the Tools-menu "Configure Thymio Blocks..."
item and "🤖 Thymio Programming" submenu, and the toolbar quick-add button
are all gated by this single flag (`extensions/thymio/__init__.py`'s
`_thymio_tab_visible()`). This is the 1.0 product decision to ship
game-only by default; a teacher/robotics classroom flips it on:

```python
from utils.config import Config
Config.set('show_thymio_tab', True)
```

Flipping it brings the tab, the menu entries and the toolbar button back
together — a one-line change, no code archaeology needed.

See `docs/THYMIO_EXTENSION_PLAN.md` for the full staging (A through G) and
the landmines found along the way.
