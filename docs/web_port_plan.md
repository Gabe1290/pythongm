# PyGameMaker → Web (Django + JS) — Feasibility Study & Migration Plan

The repo is well-structured for this port: visual-scripting *semantics* live in Qt-free modules (`events/`, `actions/`, `events/event_types.py`, `events/action_types.py`), the project file format is just zipped JSON + assets, Blockly already runs in a browser, and an HTML5 export pipeline already produces a runnable game. The hard work is (1) reimplementing the PyQt editor surfaces in JS, and (2) closing the runtime parity gap between `engine.js` (1.8 K lines, ~64 action cases) and `runtime/action_executor.py` + `runtime/action_handlers/` (~10 K lines, ~130 handler methods plus Thymio/particles/views).

---

## 1. Architecture map

Grep-based classification (`from PyQt|from PySide|import pygame` + spot reads). Counts are file-level.

### `core/` (7 454 LOC) — mostly portable

| File | LOC | Class | Notes |
|---|---|---|---|
| `core/ide_window.py` | 3 788 | **Reimplement (web)** | The PyQt main window — equivalent becomes a Django/JS shell. |
| `core/project_manager.py` | 1 415 | **Adapt** | Imports `PySide6.QtCore (QObject, Signal, QTimer)` only for signal plumbing. The project loading / saving / metadata logic is pure JSON + filesystem; can be made Qt-free by replacing signals with plain callbacks or events. |
| `core/asset_manager.py` | 1 096 | **Adapt** | Same Qt-signal coupling + `pygame.mixer.init()` solely for sound preview (lines 43, 840, 1024). Strip Qt signals + the pygame preview path → portable. |
| `core/event_system.py` | 349 | **Adapt** | Light Qt coupling. |
| `core/language_manager.py` | 360 | **Reimplement (web)** | Wraps `QTranslator`. Web side will use a separate i18n stack (gettext or JS i18next). The `.ts/.qm` source strings are still useful — re-extract as PO/JSON. |
| `core/ide_exporters.py` | 175 | **Adapt** | Thin wrapper around exporters; trivial port. |
| `core/logger.py` | 151 | **Portable as-is** | Pure stdlib logging. |

### `editors/` (15 710 LOC) — almost entirely **must reimplement**

Every file imports `PySide6` (the grep matched 22/22 modules under `editors/`). The only web asset already present is `editors/object_editor/blockly/` (HTML/JS, **already web**). The Python wrappers like `blockly_widget.py` (799 LOC) are the Qt↔JS bridge and must be replaced by direct browser code. Detailed inventory in §2.

### `runtime/` (17 570 LOC) — split

| File | LOC | Class |
|---|---|---|
| `runtime/action_executor.py` | 5 644 | **Adapt server-side** (1 stray `from PySide6.QtWidgets import QMessageBox` at line 4053 in the `show_message` action — easy to factor out). Logic itself is Python-only. |
| `runtime/game_runner.py` | 4 548 | **Reimplement (web)** — heavy `pygame` use (window, surfaces, blit). Browser equivalent is `engine.js`. |
| `runtime/action_handlers/*.py` | ~3 600 | **Portable as-is** server-side, but **must be re-implemented in JS** for browser play. They have no Qt deps and very light pygame use. |
| `runtime/collision_system.py` | 281 | **Reimplement (JS)** for browser; pure Python otherwise. |
| `runtime/input_handler.py` | 332 | **Reimplement (JS)** — pygame event loop. |
| `runtime/thymio_simulator.py` | 530 | **Reimplement (JS)** — pygame-based renderer + physics. Currently absent from `engine.js`. |
| `runtime/thymio_renderer.py`, `thymio_action_handlers.py` | 456 + 452 | Same. |
| `runtime/network/` (untracked) | 229 | **Adapt server-side**. TCP newline-JSON; for web, replace transport with WebSocket. |
| `runtime/playground_runner.py`, `runtime/room_preview.py` | 463 + 210 | **Reimplement (JS)** — pygame surfaces. |

### `events/` (4 813 LOC) — overwhelmingly portable

| File | LOC | Class |
|---|---|---|
| `events/event_types.py` | 380 | **Portable as-is** (no Qt). |
| `events/action_types.py` | 1 253 | **Portable as-is** — defines the visual-scripting parameter schemas. **This is the canonical contract** between editor UI, exporter, and runtime. |
| `events/keyboard_events_complete.py`, `mouse_events_complete.py`, `thymio_events.py`, `gm80_events.py`, `plugin_loader.py` | ~1 750 | **Portable as-is**. |
| `events/action_editor.py`, `events/conditional_editor.py` | 815 + 610 | **Reimplement (web)** — PyQt UI. |

### `actions/` (2 666 LOC) — **fully portable as-is**

Grep: zero Qt/pygame imports across all 14 files. These are dataclass-style action definitions used by both the editor (for palette/toolbox) and the runtime. They are **the single source of truth** to replicate into `engine.js` for runtime parity, and into a JS toolbox spec for the web editor.

### `widgets/`, `dialogs/` (~11 666 LOC combined) — **must reimplement**

All Qt. Asset tree, properties panel, project dialogs, Thymio dialogs, sprite-strip dialog, etc.

### `export/HTML5/` — **already web**

`export/HTML5/html5_exporter.py` (218 LOC) is a thin Python builder that gzips `project.json` + base64-bundles sprites and inlines `engine.js` into one HTML file. `engine.js` (1 810 LOC, 64 action `case`s) is the browser runtime. **Already web; reusable directly from a Django view.**

### Other

- `export/Android,Aseba,Kivy,Roberta,exe,linux,macos,ios` — desktop/native exporters. **Out of scope for web port**, but not in the way.
- `importers/`, `utils/`, `config/`, `plugins/` — mostly portable Python helpers.
- `translations/` — French is already complete (all 6 `.qm` groups present at `translations/pygm2_fr_*.qm`).

---

## 2. Editor inventory

The 15.7 K LOC under `editors/` is the bulk of the port. Difficulty is 1 (trivial) to 5 (research-level). All entries are PyQt and have no web equivalent except where noted.

| Editor / module | LOC | What it edits | Sub-widgets / dialogs | Difficulty | Key challenge | Blockly covers? |
|---|---|---|---|---|---|---|
| `editors/object_editor/object_editor_main.py` | 1 735 | Game objects (sprite, events, actions, props) | event panel + actions panel + properties panel + Blockly | **3** | Wiring three sub-views and keeping them in sync. The shell. | Partially — the action list inside an event. |
| `editors/object_editor/object_events_panel.py` | 1 830 | Event list per object (create/step/keyboard/collision/…) | `dialogs/key_selector_dialog.py`, `mouse_event_selector_dialog.py`, `thymio_event_selector.py` | **3** | Tree of events with type-specific sub-pickers. | No — Blockly is per-event, not the event list. |
| `editors/object_editor/blockly_widget.py` | 799 | Hosts the Blockly workspace inside Qt | wraps `blockly/blockly_workspace.html` (3 146 lines), `blockly_blocks.js` (1 706), `blockly_generators.js` (469), `blockly_i18n.js` (1 480) | **1** in browser (just drop the QtWebEngine wrapper) | None — Blockly is already JS. | **Yes — direct port.** |
| `editors/object_editor/python_code_parser.py` | 1 254 | Round-trips Python ↔ visual actions (alt to Blockly) | `python_syntax_highlighter.py` (132) | **4** | Code-mirror integration + AST parsing logic carries over (pure Python — runs server-side). | No. |
| `editors/object_editor/gm80_action_dialog.py` | 345 | "Drag-and-drop GM 8.0-style" action picker | many forms | **3** | Lots of small parameter forms; all driven by `events/action_types.py`. | Partial — Blockly is the modern alternative. |
| `editors/object_editor/object_actions_formatter.py` | 135 | Pretty-prints actions for display | — | **1** | Pure logic. | n/a |
| `editors/object_editor/sync_coordinator.py` | 121 | Keeps Blockly XML and action JSON in sync | — | **2** | Already JSON-based; just needs an event bus. | n/a |
| `editors/object_editor/object_properties_panel.py` | 204 | Object-level props (sprite, solid, depth) | sprite picker | **2** | Standard form. | n/a |
| `editors/object_editor/thymio_events_panel.py` | 454 | Thymio-specific event list | `dialogs/thymio_event_selector.py` (329), `thymio_action_selector.py` (442) | **3** | Same as events panel + Thymio domain. | Partial. |
| `editors/room_editor/room_canvas.py` | 1 402 | Room layout (place instances, paint tiles, set background) | `tile_palette.py` (348), `object_palette.py` (180), `instance_properties.py` (178), `room_undo_commands.py` (378) | **5** | Real-time canvas rendering, drag-drop, tile/instance placement, multi-select, undo/redo, view config. **The biggest single-editor port.** | No. |
| `editors/sprite_editor/sprite_editor_main.py` | 1 092 | Frame-by-frame sprite editing | `sprite_canvas.py` (489), `sprite_tools.py` (682), `color_palette.py` (192), `sprite_frames.py` (347), `dialogs/sprite_strip_dialog.py` (508) | **4** | Pixel canvas + brush/eraser/fill tools + frame timeline + sprite-strip slicer. | No. |
| `editors/playground_editor/playground_canvas.py` | 694 | Aseba/Thymio playground (worlds for Thymio) | `playground_properties.py` (312), `playground_tool_palette.py` (71), `playground_elements.py` (97), `color_manager.py` (128), `playground_undo_commands.py` (157) | **4** | Vector-style scene with shapes; less complex than room editor but still drag-drop. | No. |
| `editors/base_editor.py`, `editor_status_widget.py`, `object_editor_components.py` | ~609 | Base classes/widgets shared by editors | — | **2** | Pure abstractions, easy to re-express in JS. | n/a |

**Difficulty totals (excl. Blockly which is free):** 5 × room canvas, 4 × sprite editor, 4 × playground, 4 × code parser, 3 × object events panel + main + Thymio panel + GM80 dialog. Realistically a single competent JS dev does the object editor MVP in ~3–4 weeks, room canvas in ~6–8 weeks, sprite editor in ~4–6 weeks, playground in ~3 weeks.

---

## 3. Project data model

### File format

- **`.gmk`** — a zip (per `utils/project_compression.py`) containing `project.json` plus subdirs (`sprites/`, `sounds/`, `backgrounds/`, `objects/`, `rooms/`, `playgrounds/`, `scripts/`, `fonts/`, `data/`). The 4 `maze_*.gmk` and `treasure.gmk` at repo root confirm `file: data` (zip).
- **`project.json`** — schema visible in `tests/netdemo_project/project.json:1-97`. Keys: `name`, `version`, `settings { window_*, starting_* }`, `room_order`, `assets { sprites, objects, rooms, sounds, backgrounds, fonts }`. Each object carries an `events` map; each event a list of `{action, parameters}` dicts. **The same shape feeds both the desktop runtime and the HTML5 exporter** — see `export/HTML5/html5_exporter.py:32-34`.
- **`.playground`** — Thymio worlds; same zip-of-JSON pattern.
- Rooms can be split out into `rooms/<name>.json` referenced by `_external_file` (see `html5_exporter.py:120-143`).

### What `project_manager.py` and `asset_manager.py` do

- `project_manager.py` (`core/project_manager.py:1415`) handles project lifecycle: `new_project`, `load_project`, `save_project`, `is_dirty`, recent-projects, autosave, version migration. Pure-JSON beneath the Qt signals.
- `asset_manager.py` (`core/asset_manager.py:1096`) imports media into the project tree, generates 64×64 thumbnails via PIL, validates extensions (`SUPPORTED_FORMATS` at line 24), and previews sounds via `pygame.mixer`. Touches the filesystem directly.

### Filesystem → Django ORM + object storage

| Today (desktop) | Web equivalent |
|---|---|
| Project = a directory on disk | `Project` model (id, owner, name, settings JSON, updated_at) + serialized `project.json` blob |
| `assets/sprites/foo.png` | `Asset` model (project_id, type, name, file → Django FileField → S3/MinIO/local media root) |
| `rooms/room_main.json` | Either denormalized into `project.json` blob, or a `Room` row with JSON content |
| Thumbnails generated by PIL into `.thumbnails/` | `ImageField` with Django `easy_thumbnails` or generated on first request |
| `.gmk` save | Server-side recompose: zip `project.json` + asset files on demand |
| Sound preview via `pygame.mixer` | Just stream the file URL to a `<audio>` tag |

### Binary / FS assumptions that break

- `pygame.mixer.Sound` instantiation in `asset_manager.py:840, 1024` — only used to validate sound files. Replace with `mutagen` or just MIME-sniff.
- Thumbnails written next to the asset (`.thumbnails/` siblings) — fine to keep server-side, but bypass with `ImageField.thumbnail` in Django.
- Path separators / hardcoded `Path(__file__).parent` in `html5_exporter.py:22` — fine; runs server-side.
- `_external_file` references in rooms (`html5_exporter.py:127`) need re-resolving when assets live in object storage rather than a sibling directory.

No format-level break: the **`project.json`/zip schema can be the wire-and-storage format unchanged**. That is a major win.

---

## 4. Runtime parity gap

`runtime/action_executor.py` + `runtime/action_handlers/` define **~130 handler methods**. `engine.js` has **64 `case` branches**. The deltas matter for classroom use because students will assemble actions via Blockly and discover at run-time that some don't work in browser.

| Domain | Python (runtime/) | JS (`engine.js`) | Gap |
|---|---|---|---|
| Movement | full set incl. `move_towards_point`, `move_to_contact`, `wrap_around_room`, `start_moving_direction`, `check_keys_and_move` | `set_hspeed/vspeed/speed/direction`, `move_fixed`, `move_free`, `move_towards`, `set_gravity/friction`, `reverse_*`, `bounce`, `stop_movement`, `jump_to_*`, `grid_move`, `snap_to_grid` | `move_to_contact`, `wrap_around_room`, `check_keys_and_move`, `if_can_push` are missing in JS |
| Rooms | restart, next, previous, change, if-exists, plus **8 views/cameras** (`game_runner.py:925-940`) | restart, next, previous, change, if-exists | **No view/camera system in `engine.js`** — silent break for any room using views. |
| Score / lives / health | full + `test_score`, `draw_score`, `draw_health_bar` | `set_score`, `set_lives`, `set_health`, `show_highscore` | Missing `draw_*`, `test_*` arithmetic branches. |
| Drawing | text, scaled text, rectangle, ellipse, circle, line, sprite, background, set_color | sprite/text/shapes in renderer; only `display_message`/`show_message` as actions | Most explicit `draw_*` actions absent in JS — they work only inside the engine's render loop, not as runnable steps. |
| Particles | full system (`runtime/action_handlers/particle_handlers.py:237`) | none | **Entirely missing.** |
| Sounds | play, stop, replace_sprite | partial | Audio actions are sparse in JS. |
| Variables | set/test/if | `if_variable`, `set_*` via expressions | Likely OK; check expression engine. |
| Alarms | 12 alarms | 12 alarms (`engine.js:100-101, 200-204, 915-919`) | **Parity** ✓ |
| Collision | `runtime/collision_system.py` (281 LOC) — bbox + can-move-with-blocker semantics | basic `if_collision`, `if_collision_at` | Missing nuanced blocker semantics; may differ. |
| Input | `runtime/input_handler.py` 332 LOC | inline JS keyboard | Likely OK for keys; gamepad/mouse-button parity not verified. |
| Thymio (motors, LEDs, sensors, tones, simulator) | `thymio_action_handlers.py` 452 LOC + `thymio_simulator.py` 530 LOC + `thymio_renderer.py` 456 LOC | **0 lines** | **Entirely missing.** This is the biggest single gap and matters for the educational use case. |
| Playground (Aseba worlds) | `playground_runner.py` 463 LOC | none | Missing. |
| Networking | `runtime/network/` (untracked, 229 LOC, TCP+JSON snapshots, host-authoritative) | none | If desired in browser → WebSocket bridge. |
| Save/load game | `execute_save_game_action`, `execute_load_game_action` | none visible | Missing — would need IndexedDB or server endpoint. |

**Student-visible silent breaks today** (top priority for the parity backlog):
1. **Views/cameras** — any scrolling game silently shows the whole room.
2. **Thymio actions** — every robot block becomes a no-op.
3. **Particles** — visual feedback disappears.
4. **`draw_*` actions** — anything using "draw text in step" is silent.
5. **`wrap_around_room`** — the `obj_drifter` in `tests/netdemo_project/project.json:75-79` literally exercises this; verify it works in the HTML5 export before phase 1.
6. **`save_game` / `load_game`** — silent.

---

## 5. Web architecture proposal

### Django apps layout

```
pygm_web/
  accounts/      # Django auth: students, teachers, classes
  projects/      # Project + Room + Asset models, zip import/export
  editor/        # editor views; thin — most logic is JS
  runner/        # /play/<project_id>/ → HTML5Exporter → iframe
  classroom/     # assignments, sharing, submissions (post-MVP)
  api/           # DRF endpoints
```

### API style — REST + WebSocket, with HTMX for non-editor UI

The editor itself talks to the backend via a **small REST API** (load project, save project, list/upload assets, build HTML5 export). REST because:
- The data shape (`project.json`) is genuinely JSON-document-shaped, not page-shaped.
- The frontend will be a real interactive app (canvas-based room editor, Blockly), not document-with-fragments — HTMX is the wrong fit *inside* editors.
- It plays well with file uploads.

Use **DRF (Django REST Framework)**. Reserve **HTMX** for the project-list / dashboard / classroom surfaces, where it shines. Use **WebSockets (Django Channels)** for: live preview reload, collaborative editing later, multiplayer demos that match `runtime/network/`.

### Frontend stack — vanilla JS + Blockly + a thin canvas framework

Recommendation: **vanilla JS modules + ES build (Vite) + Blockly + Konva.js for the room/sprite canvases**, no React/Vue.

Why no SPA framework:
- Blockly is the centerpiece of the existing UI and is framework-agnostic.
- The room editor and sprite editor are *canvas*-driven, not DOM-driven; React buys little there.
- The student-facing nature favors a small dependency tree and short load time.
- Reduces JS bundle and onboarding tax for new contributors.

Konva.js (or Pixi.js if performance is critical) handles: tile placement, instance drag, selection, layers, undo overlays. For the sprite editor a plain `<canvas>` with custom brushes is simpler.

### "Run in browser" wiring

```
[Save button] → POST /api/projects/<id>/save (project.json + dirty assets)
[Run button]  → POST /api/projects/<id>/build/html5
                 → server: HTML5Exporter().export(project_dir, build_dir)
                 → returns build URL
              → iframe src="/builds/<id>/<name>.html"
```

`HTML5Exporter` already produces a **single self-contained HTML file** — no static-asset wrangling. Two improvements worth making early:
1. Stop base64-inlining sprites (currently `html5_exporter.py:145-194`); serve them as URLs from `MEDIA_ROOT` so the HTML stays small and the browser can cache.
2. Add a `?dev=1` mode that points `engine.js` at a dev server with hot-reload.

### Asset storage

Local filesystem behind Django's `MEDIA_ROOT` for v1, abstracted via `default_storage` so an S3/MinIO swap is one config flip later. Each `Project` gets a directory; each `Asset` row holds a path inside it. The on-disk layout matches `project.json`'s `file_path` keys, so `HTML5Exporter` keeps working.

### Auth / multi-tenant for classroom use

- Standard `django.contrib.auth` with two profile roles: **teacher**, **student**.
- `Classroom` model: many students, one teacher.
- `Project.owner` + `Project.shared_with_classrooms`. Per-project ACL at the view layer (Django Guardian or a hand-rolled mixin).
- Magic-link / class-code login for students (no email needed). Django-allauth covers this.
- A "submitted" flag for assignment workflows (post-MVP).

### French i18n carry-over

- The `.qm` files at `translations/pygm2_fr_*.qm` are Qt-binary; the readable source is the sibling `.ts` files (XML). Write a one-shot extractor that turns each `<source>/<translation>` pair into either Django `.po` (for server templates) or a JSON dict for client-side i18n (e.g. i18next).
- Blockly's i18n is already isolated (`blockly_i18n.js`, 1 480 LOC) — keep using it for blocks.
- `core/language_manager.py` maps cleanly to a Django `LANGUAGES` setting + `LocaleMiddleware`.
- French is the only language with **all 6 groups present**, confirming it is the polished translation today (`translations/pygm2_fr_actions.qm`, `_blockly`, `_core`, `_dialogs`, `_editors`, `_misc`).

---

## 6. Migration phases

Each phase ends with the desktop IDE *still working* and a defensible artifact. Effort is rough person-time on a focused single dev (S=days, M=1–2 weeks, L=3–6 weeks, XL=2–3 months).

### Phase 0 — Harden the current IDE and close runtime parity gaps (M, **prerequisite**)
- Test current desktop IDE end-to-end (see §8).
- Build `treasure.gmk` and the four `maze_*.gmk` to HTML5; record which actions/events misbehave.
- Add the missing actions in `engine.js` that show up in those tests, prioritized: views, `wrap_around_room`, particles, `draw_*` actions, `save_game`/`load_game`.
- Decide Thymio policy for web (see §7).
- **Deliverable:** parity gap survey turned into GitHub issues; a few critical fixes landed in `engine.js`.
- **Unblocks:** Phase 2 (the "play in browser" promise must hold).

### Phase 1 — Extract a portable core library (M)
- Create `pygm_core/` (or `core_portable/`) Python package with **no Qt or pygame imports**:
  - `events/event_types.py`, `events/action_types.py`, `events/keyboard_events_complete.py`, `events/mouse_events_complete.py`, `events/thymio_events.py` (already clean — just move).
  - All of `actions/` (already clean).
  - Strip Qt signals from `core/project_manager.py` and `core/asset_manager.py`; replace with `blinker` or a tiny callback hub.
  - Strip `pygame.mixer` from `core/asset_manager.py:43` (gate behind `if pygame_available`).
  - Move `utils/project_compression.py`.
- Both `main.py` (desktop) and the future Django app import from this package.
- **Deliverable:** `pip install -e .` of the portable library; desktop IDE still works against it.
- **Unblocks:** Phase 2 backend.

### Phase 2 — Django backend + "play exported game" web flow (L)
- Django project skeleton, accounts, project upload (`.gmk`), project list dashboard.
- `Project` / `Asset` / `Room` ORM. Import a `.gmk` → unpack → DB rows. Export DB → `.gmk`.
- View: **upload `.gmk`, click "play", iframe shows running game.** This is the smallest end-to-end loop and proves the pipeline.
- French + English already done at this point because translations carry over.
- **Deliverable:** a teacher can sign in, upload an existing `.gmk`, and play it in a browser. No editing.
- **Unblocks:** Phase 3 (web editor MVP).

### Phase 3 — Web editor MVP: object editor (L)
- Why object editor first: Blockly is **already** the centerpiece and runs in browser. The wrappers (`blockly_widget.py` 799 LOC, `sync_coordinator.py` 121 LOC) are exactly the bridge code we no longer need.
- Reimplement: object properties form, event list (left tree), action list per event (Blockly inside the right pane), save/load roundtrip to `project.json`.
- Reuse `blockly_blocks.js`, `blockly_generators.js`, `blockly_i18n.js`, `blockly_workspace.html` directly.
- Web sprite picker = list project's sprite assets via the API.
- **Deliverable:** create new project, define an object, attach a Step event with Blockly actions, run it.
- **Unblocks:** asset management and room editor.

### Phase 4 — Sprite editor + asset upload UX (L)
- Asset uploader (drag-drop into the asset tree).
- Sprite editor: frame strip, basic pixel tools, frame-by-frame view. Aim for **viable for kids**, not Photoshop.
- Sprite-strip slicer (port `dialogs/sprite_strip_dialog.py`).
- **Deliverable:** import or paint a sprite, assign to an object, see it in play.

### Phase 5 — Room editor (XL)
- This is the heaviest single web component. Konva.js canvas, instance placement, tile painting, layers, undo/redo (port the JSON-shaped commands from `editors/room_undo_commands.py`), background/view configuration.
- Honest scope: **~6–8 weeks of focused work**.
- **Deliverable:** build a complete level from scratch in browser; play it.

### Phase 6 — Sound, fonts, settings, polish (M)
- Sound preview (HTML5 `<audio>`).
- Project settings dialog port.
- Recent projects, autosave, dirty indicator.

### Phase 7 — Thymio support in browser (L) *— optional, depends on policy*
- If WebSerial route: implement Thymio Aseba protocol over `navigator.serial`.
- If simulator-only: port `thymio_simulator.py` (530 LOC physics) and `thymio_renderer.py` (456 LOC) into `engine.js`, plus the 30+ Thymio action cases.

### Phase 8 — Classroom features (M–L)
- Student/teacher roles, classes, assignments, share-by-link, basic submission tracking.
- Live preview via WebSockets (re-export on save).

### Phase 9 — Multiplayer / collab (M, optional)
- Repurpose `runtime/network/` over WebSockets for the same host-authoritative snapshot model — already 60 Hz JSON, already works with the engine.

---

## 7. Risks and unknowns

1. **Silent semantic divergence between `engine.js` and `runtime/`.** `engine.js` has ~half the action count and lacks views, particles, Thymio, several `draw_*` and movement actions. In a classroom setting, students will encounter "this works on my teacher's machine but not in browser" — the worst possible failure mode. **Mitigation:** before phase 2, run every existing `.gmk` through HTML5 export and triage. Track each missing action as a numbered issue.
2. **Action parameter drift.** `events/action_types.py` is canonical; any drift between Python handlers and JS handlers must be caught. **Mitigation:** generate a JSON schema from `action_types.py` and use it in tests on both sides.
3. **Base64 sprite bundling** (`html5_exporter.py:145-194`) inflates payload ~33%. For a sprite-heavy project this becomes a multi-MB single HTML file. **Mitigation:** add a "URL mode" that emits `<img src="/media/...">` instead — appropriate when the build is served by Django anyway.
4. **Thymio in browser is genuinely unsolved.** Three options:
   - **WebSerial** (`navigator.serial`): supported in Chromium-based browsers only, requires HTTPS, requires Thymio firmware to speak Aseba over USB-CDC. Workable but excludes Firefox/Safari and any iPad in the classroom.
   - **Simulator-only**: port `thymio_simulator.py` to JS. No real hardware.
   - **Hybrid via local helper**: a small native helper app brokers between browser (WebSocket) and the robot. Adds installation overhead — defeats the point of a web port.
   The educational workflow may favor **simulator in browser, real-robot via desktop IDE** for now. Decide before phase 7.
5. **QtWebEngine → no longer needed.** `core/ide_window.py:1-25` includes special handling for QtWebEngine paths under Nuitka — the web port removes this entire concern. Net positive.
6. **Blockly version drift.** The bundled `editors/object_editor/blockly/lib/blockly_compressed.js` is pinned. Decide upgrade cadence; pin in the web project too.
7. **Django LTS / Python version.** Recommend Django 5.x LTS + Python 3.12 (matches the existing `python312.bat` at repo root).
8. **`sprite_editor` accessibility.** A pixel editor in the browser is doable but easy to half-build. Set the bar at "edit existing sprite, save, draw a missing missing-asset placeholder" — not "replace Aseprite".
9. **`runtime/network/` is untracked.** Active development territory — the port plan should not assume its API is stable. Wire it in only at phase 9.
10. **Hand-wired coupling spotted:** `runtime/action_executor.py:4053` imports `PySide6.QtWidgets` for a single message-box call — a one-line factor-out, but it indicates the layering isn't airtight. Audit similar imports during phase 1.
11. **Translation extraction is one-shot work.** `.qm` is binary; you'll work from `.ts`. The XML format is straightforward but requires writing a tiny extractor. ~1 day.

---

## 8. Recommended first concrete step

> **Build every `.gmk` in the repo to HTML5 and play-test each one in a browser. Record what's broken vs. desktop in a single shared spreadsheet keyed by `(project, room, object, event, action)`.**

The user said "we first have to fully test the current IDE" — make that test **double as the parity audit** that derisks the entire web port. Concretely:

1. For each of `treasure.gmk`, `maze_1.gmk`, `maze_2.gmk`, `maze_3.gmk`, `maze_4.gmk`, `maze.playground`, `tests/netdemo_project/`:
   - Run desktop. Verify expected behavior. Take screen-recording.
   - Run `HTML5Exporter` (it's already a CLI: `python -m export.HTML5.html5_exporter <project> <out>`).
   - Open the produced HTML in Chrome and Firefox. Compare.
2. For each discrepancy, add a row to the parity sheet: project, scenario, expected, actual, suspected missing action/event, severity (silent / visible / crash), screenshot.
3. Add a **`__pygm_action_executed__` console-log instrumentation** in `engine.js`'s switch statement (one-line at the top of the action dispatch) so every play-test produces a log of which action cases were exercised. After all six projects you have empirical coverage data — the actions that *never logged* are either dead in `engine.js` or untested by your projects.
4. Cross-reference logged actions vs. `events/action_types.py` definitions to find the actions students *can author* but `engine.js` *cannot run*. Each one is a sleeper bug for the web port.

This single exercise produces: (a) confidence in the desktop IDE today, (b) a prioritized backlog of `engine.js` work, (c) the test corpus for phase 2's "play in browser" deliverable. Doing it before any web work starts is the single highest-leverage thing.

---

### Critical Files for Implementation
- `export/HTML5/html5_exporter.py`
- `export/HTML5/templates/engine.js`
- `events/action_types.py`
- `core/project_manager.py`
- `runtime/action_executor.py`
