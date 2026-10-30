# micro:bit — a worked extension (a simulated board)

This folder is a real PyGameMaker feature that lives **outside** the core
engine: a simulated **BBC micro:bit** drawn in the game window, with a 5×5 LED
display, buttons, a touch logo, pins, an accelerometer, light / temperature /
compass / sound sensors, a speaker and a radio. It is here to be read, and it
is the second worked example next to `raycast_2_5d/`: where that one adds a new
way to draw a *room*, this one adds a new kind of *object* — one that owns
state, draws itself, takes input and fires its own events.

The plan it was built from, unit by unit, is `docs/MICROBIT_EXTENSION_PLAN.md`.
The user-facing page is `wiki/Microbit.md` (and `Microbit_<lang>.md` in the eight other
languages); the sample is `samples/microbit_1/`.

## The files

| File | What's in it |
|---|---|
| `extension.json` | The manifest: name, `enabled: true`, and `provides_actions` / `provides_events`. Those two lists are what make the actions and events appear **only in projects that activate the extension** (core's `active_extensions`) — leave an event out and core treats it as a plain core event. |
| `__init__.py` | The entry point. Declares every hook the extension uses (below) and the instance-created binding: an object named `microbit*`, or an instance flagged `is_microbit`, gets a simulator. |
| `state.py` | Where per-instance state lives (`instance.extension_state["microbit"]`), plus `option_of` for the per-board object properties. |
| `simulator.py` | `MicrobitSimulator` — the pure board: display and its queue, buttons, logo, pins, accelerometer + gesture recognition, sensors, sound queue, radio outbox. **No pygame, no Qt**, so it runs in a test, and later in a serial bridge or an exporter. `update(dt)` returns the events that happened. |
| `font.py`, `images.py`, `melodies.py` | Data generated from the MIT-licensed micro:bit sources (the 5×5 font, the 64 built-in images, the 21 melodies). Notices in `THIRD_PARTY_LICENSES.md`. |
| `sound.py` | Pure note / melody parsing, a port of MicroPython's `music.play` timing. |
| `radio.py` | Pure delivery of radio messages between the boards in a room, by group. |
| `layout.py` | Pure geometry — where the LEDs, buttons, logo, pads and the sensor strip are — shared by drawing and hit-testing, so what you see is what you click. |
| `kivy_audio.py` | The speaker on a Kivy export (pure): a note rendered to a mono WAV and played with `SoundLoader`; `audio.py` is its pygame twin. |
| `kivy_touch.py` | Touch and keyboard control of the drawn board for a Kivy export (pure); `input.py` is its desktop twin. |
| `kivy_draw.py` | The board and sensor strip as draw-queue commands (pure), shipped into a Kivy export; `renderer.py` is its pygame twin. |
| `export_html5.js` | The HTML5 export's port of the simulator, board, input and speaker (Stage P, H1-H6), injected into the exported `engine.js` through its extension registries. |
| `export_kivy.py` | The Kivy (Android/iOS) export's side (Stage P, K1-K6). Plain data, because the loader `exec`s it without `__file__`: `SUPPORT_FILES` (which pure modules ship as `microbit_sim/`), `ACTION_CODEGEN`, `CONDITION_CODEGEN`, `EVENT_METHODS`, `SCENE_CODE` (the per-frame step, touch and key hooks, as `_ext_<hook>__microbit` methods) and `BASE_OBJECT_CODE` (the `_mb_*` helpers). |
| `renderer.py` | The pygame drawing: board, LEDs, controls, speaker indicator, sensor strip. |
| `input.py` | Mouse clicks and drags on the drawn controls, and the opt-in keyboard shortcuts. |
| `audio.py` | A square wave on a reserved mixer channel; a silent no-op without a mixer. |
| `events.py` | The 24 `microbit_*` event types and the mapping from what the simulator reports. |
| `runtime.py` | The per-frame update: follow drags, deliver radio, step every board, fire events, drive the speaker. |
| `actions.py` | The 16 action **schemas** (`PLUGIN_ACTIONS`), English. |
| `handlers.py` | The action **handlers** (`PluginExecutor`). |
| `translations.py` | French text for the auto-generated Blockly blocks. |
| `README.md` | This file. |
| `export/` | MicroPython export (Stage X, `docs/MICROBIT_STAGE_X_PLAN.md`): `export/micropython_exporter.py` generates a standalone real-device program per micro:bit object; `export/device.py` copies it onto a connected board over USB serial (`microfs`); `export/hex_build.py` + the vendored firmware in `export/firmware/` (V1 v1.1.1, V2 v2.1.2) build a ready-to-flash hex for a factory-fresh board: V1 (script appended at a fixed address), V2 (the program saved as main.py in the MicroPython file system, via `export/intel_hex.py`, `export/flash_regions.py` and `export/mpfs.py`), or ONE Universal Hex for both (`export/universal_hex.py`), all described in `docs/MICROBIT_V2_HEX_PLAN.md`; `export/kivy_sim_init.py` and `export/kivy_state.py` are never imported by the extension itself: they are the two small shims shipped into a Kivy export (the package `__init__` and a `state.py` for the verbatim `layout.py`); this folder's own `__init__.py` wires the File-menu entry via `PLUGIN_IDE_MENUS`. |

## How it hooks in

Everything goes through seams core already had (plus one small generic one, the
generated-block translation registry); **no core engine, runtime or editor code
names micro:bit** (tests pin the main files). Core's only mentions are data: the
sample's folder name in the Welcome tab and edition lists, and the docs
generator's tables. The hooks `__init__.py` declares:

| Hook | What the extension does with it |
|---|---|
| `PLUGIN_ACTIONS` + `PluginExecutor` | Adds the 16 actions and their handlers. A handler reaches the engine through `instance.action_executor`. A condition just returns `True`/`False`; core turns that into "guard the next action". |
| `PLUGIN_EVENTS` | Adds the 24 events. Each is a **flat name** (`microbit_gesture_shake`, `microbit_pin_0`), so the editor and Blockly need no sub-event selector. |
| `PLUGIN_INSTANCE_CREATED` | Attaches a simulator to a `microbit*` instance as the room builds. |
| `PLUGIN_FRAME_UPDATES` (`after_collision`) | `runtime.update_microbits`: steps every board by `1/fps` and fires its events. Returns at once for a room with no micro:bit. |
| `PLUGIN_INSTANCE_OVERLAYS` | Draws the board over its instance (or over its sprite, if it has one). |
| `PLUGIN_INPUT_HANDLERS` | Clicks on the board's controls (swallowed, so no authored mouse event also fires) and the keyboard shortcuts. |
| `PLUGIN_IDE_MENUS` (`file`) | The File-menu entry "Export micro:bit (MicroPython) code..." (`export/`). |
| `PLUGIN_GENERATED_BLOCK_TRANSLATIONS` | French for the Blockly blocks core auto-generates from the schemas. |
| `register_action_tabs` | The "micro:bit" tab in the action picker. |

Blockly needs no hand-written blocks: every `ActionType` becomes a generated
block in a "micro:bit" category, and the events appear in core's generic
"extension event" block.

## The design in one paragraph

The simulator is **pure and reports**; everything with a side effect is a thin
layer around it. A click only *sets state* (`set_button("a", True)`); the frame
update calls `update(dt)`, which returns `("button", "a")`; the runtime turns
that into the event. The same split puts the speaker behind `sound_note` /
`sound_stop` reports and the radio behind `take_radio_outbox` / `radio_receive`.
That is why a down-and-up click in a single frame still registers, why the whole
thing is testable without a window, and why a future serial bridge (a real board
over USB) can drive the same simulator.

## Landmines worth knowing

- **Name your object `microbit…`, and put the events on it.** Each action works
  on the micro:bit that runs it.
- **Text is a quoted expression.** `Scroll Text` reads its text through
  `_parse_value` like `draw_text`, so `Score - 3` is arithmetic; the sample and
  the docs write `"Rolls"`.
- **Never cache pygame `Font`, `Sound` or `Channel` objects across calls** (the
  renderer caches rendered label *surfaces*, the audio caches raw PCM *bytes*).
  They dangle after `pygame.quit()` and crash the process with an access
  violation — found twice, by the full suite, not by the targeted tests.
- **The plugin loader imports the extension under a synthetic package name**
  (`pygm_extension_microbit`), so a test that spies on a hook must patch the
  *loaded* module, not `extensions.microbit.*`.
- **`provides_events` in the manifest is load-bearing**, not documentation.
- **Core's list of "question" actions is fixed**, so a false micro:bit condition
  directly followed by another micro:bit condition doesn't chain-skip.
- **The export ports are twins, and each is pinned to its pygame original** (`kivy_draw.py` <-> `renderer.py`,
  `kivy_touch.py` <-> `input.py`, `kivy_audio.py` <-> `audio.py`, `export_html5.js` <-> the whole Python
  side) by a differential test. Change the original and the twin's test fails: that is the point.
- **`kivy_draw.py` and `kivy_touch.py` sit next to `layout.py`** because they import it relatively; the
  export ships `layout.py` verbatim as `microbit_sim/layout.py`. `BASE_OBJECT_CODE` is a plain string but
  `SCENE_CODE` is %-formatted (double any `%` there).
- **A new event type needs a row in each export port.** Kivy needs an `EVENT_METHODS` entry (without one
  the export *warns* that the event's actions are skipped); HTML5 needs a row in the generated tables
  (`tools/gen_microbit_js_tables.py --check`; without one the event just never fires there).
- **Kivy scene hooks are `_ext_<hook>__<extension>` methods, never overrides.** The scene's dispatchers
  (`_update_extensions`, `_extension_touch_down`, `_render_extension_overlay`, ...) call every one, in name
  order; a plain override of a shared name made the last-injected extension win (raycast silently shadowed
  Block World's renderer). `tests/test_kivy_extension_hook_coexistence.py` exports with every extension
  enabled and pins one definition per hook.
- **A test must not use a repo-relative path**: CI runs pytest from `tests/`, so `samples/...` only exists
  from the repo root (six of the MicroPython export tests failed in CI for exactly that).
- **Frozen desktop builds find the extension under `sys._MEIPASS`**; a missing one
  fails *silently* (no board drawn). `tools/verify_desktop_export.py --compare
  microbit_1` is the check.

## Exports

The desktop export freezes the real engine, so the board works there. The
**HTML5** export carries a line-for-line JavaScript port of the simulator
(`export_html5.js`): the board and sensor strip are drawn on the canvas, the
actions, conditions and events run, the board answers mouse, touch and
(opt-in) keyboard, and the speaker plays through WebAudio. It is checked
against the Python simulator by fuzz and pixel comparison, and
`tests/test_microbit_html5_playtest.py` compares a whole exported frame of
`microbit_1` with the pygame one (dev box only: it needs Playwright +
Chromium). Known differences: events fire at the start of the frame, the text
labels use a browser font, and only the first finger of a multi-touch is read.
Kivy/Android has the whole simulator (Stage P, K1-K6 done): it ships in the export
(`microbit_sim`, `export_kivy.py`), the actions and conditions run, the boards are
stepped each frame and the micro:bit events fire (radio included) and the board and
sensor strip are drawn (a simplified look), you can touch the buttons, logo, pins, tilt pad, shake
button and sliders (and use the opt-in keyboard), and the speaker plays its notes
(a rendered WAV through `SoundLoader`).
A board is recognised by its object name (`microbit*`) or by `is_microbit` on its room entry, and the
object properties `microbit_scale` / `microbit_show_sensors` / `microbit_keyboard` work (the exporter copies
the keys listed in `export_kivy.py`'s `INSTANCE_ATTRS` onto the instance it builds and its `OBJECT_ATTRS` into
the generated object class; an instance variable still wins, as on the desktop).
`tests/test_kivy_microbit_{actions,events,draw,touch,sound,e2e,room_flag,object_attrs}.py`
(the last plays the real `microbit_1` sample) and `tests/test_microbit_export_fallthrough.py`
pin the behaviour.

**MicroPython export** (a different kind of export — *onto a real micro:bit*, not
another PyGameMaker platform target) lives in `export/`. File menu → "Export
micro:bit (MicroPython) code..." asks for the board (**V2**, **V1** or **Both**; a
per-export choice, so a mixed classroom needs no second copy of the project) and a
folder, then writes one standalone `<folder>/<object>/main.py` per micro:bit
object. Every micro:bit action and condition is translated, plus `set_variable` /
`test_variable`, blocks and comments; each event becomes a check inside one loop;
`irandom` / `random` / `choose` are rewritten onto Python's `random`, any other
GameMaker function passes through unchanged. What cannot be exported is *reported*
in the finish dialog, never dropped silently: `microbit_display_done` /
`microbit_sound_done` (the device's own calls already block), and on V1 the
V2-only features (sound level, the logo, loud/quiet sound).

When exactly one object was exported the dialog offers two ways onto a board:
**copy** `main.py` to one already running MicroPython (`export/device.py`, through
`microfs`; the program then runs by itself), or **build a ready-to-flash `.hex`**
(`export/hex_build.py`) to drag onto the `MICROBIT` drive of even a factory-fresh
board. The `.hex` is V1 (script appended at a fixed address, at most 8,187 bytes),
V2 (the program saved as `main.py` in the MicroPython file system the firmware
describes; at most 20,150 bytes) or one **Universal Hex** for both, which exports
under V1's rules and is limited by V1's size. The vendored firmware is MIT
(`THIRD_PARTY_LICENSES.md`). Plans: `docs/MICROBIT_STAGE_X_PLAN.md` and
`docs/MICROBIT_V2_HEX_PLAN.md`. The user-facing description is the "MicroPython
export" section of `wiki/Microbit.md`; `tests/test_wiki_microbit_pages.py` pins its
size limits and dialog wording to this code.

## The tests

`tests/test_microbit_*.py` — simulator, actions, events, renderer, input, strip,
sound, radio, Blockly, the sample, the docs, and the export fall-through — plus
the export families:

- **HTML5:** `test_microbit_html5_{sim,actions,draw,input,sound,playtest}.py`. The
  browser ones skip where Playwright + Chromium are absent (CI); the structural
  ones pin every table, constant and colour to the Python source.
- **Kivy:** `test_kivy_microbit_{actions,events,draw,touch,sound,e2e}.py`, driven
  under a stub `kivy` (Kivy cannot run in CI); the last plays the real
  `microbit_1` sample.
- **MicroPython / hex:** `test_microbit_micropython_export*.py`,
  `test_microbit_{intel_hex,flash_regions,mpfs,hex_build,v2_hex_build,universal_hex,universal_build}.py`.
- **Wiki:** `test_wiki_microbit_pages.py` keeps the nine language pages in step.

They assert *where* things land (LED (2,2) is red at its computed position; a
click at A's computed rectangle fires `microbit_button_a`), and several run a real
`GameRunner.run()` loop.

## What is not here yet

- **Stage L, a live link** to a real micro:bit over USB serial (needs a board).
- **A real board for the `.hex` files.** The V1, V2 and Universal files are
  verified against the real firmware and by independent checks, but **not yet on
  a physical board**, and neither is the `microfs` copy — see
  `docs/RELEASE_QA_CHECKLIST.md` s11a.
- **Human eyes on the exports.** Nobody has used the exported HTML5 board on a
  touch screen, run the Kivy game on Android or iOS, or heard the beep. The Kivy
  board is drawn in a simplified look (square corners, no corner wedge or A/B
  tags: the draw queue has no polygon).
