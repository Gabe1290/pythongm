# micro:bit — a worked extension (a simulated board)

This folder is a real PyGameMaker feature that lives **outside** the core
engine: a simulated **BBC micro:bit** drawn in the game window, with a 5×5 LED
display, buttons, a touch logo, pins, an accelerometer, light / temperature /
compass / sound sensors, a speaker and a radio. It is here to be read, and it
is the second worked example next to `raycast_2_5d/`: where that one adds a new
way to draw a *room*, this one adds a new kind of *object* — one that owns
state, draws itself, takes input and fires its own events.

The plan it was built from, unit by unit, is `docs/MICROBIT_EXTENSION_PLAN.md`.
The user-facing page is `wiki/Microbit.md`; the sample is `samples/microbit_1/`.

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
| `renderer.py` | The pygame drawing: board, LEDs, controls, speaker indicator, sensor strip. |
| `input.py` | Mouse clicks and drags on the drawn controls, and the opt-in keyboard shortcuts. |
| `audio.py` | A square wave on a reserved mixer channel; a silent no-op without a mixer. |
| `events.py` | The 24 `microbit_*` event types and the mapping from what the simulator reports. |
| `runtime.py` | The per-frame update: follow drags, deliver radio, step every board, fire events, drive the speaker. |
| `actions.py` | The 16 action **schemas** (`PLUGIN_ACTIONS`), English. |
| `handlers.py` | The action **handlers** (`PluginExecutor`). |
| `translations.py` | French text for the auto-generated Blockly blocks. |
| `README.md` | This file. |
| `export/` | MicroPython export (Stage X, `docs/MICROBIT_STAGE_X_PLAN.md`): `export/micropython_exporter.py` generates a standalone real-device program per micro:bit object; `export/device.py` copies it onto a connected board over USB serial (`microfs`); `export/hex_build.py` + the vendored `export/firmware/micropython-microbit-v1.1.1.hex` build a ready-to-flash combined hex for a factory-fresh V1 board (V2's combined hex needs a real flash-filesystem builder, a separate, bigger, not-yet-started task); this folder's own `__init__.py` wires the File-menu entry via `PLUGIN_IDE_MENUS`. |

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
- **Frozen desktop builds find the extension under `sys._MEIPASS`**; a missing one
  fails *silently* (no board drawn). `tools/verify_desktop_export.py --compare
  microbit_1` is the check.

## Exports

The desktop export freezes the real engine, so the board works there. HTML5 and
Kivy/Android have no simulator yet: the actions are skipped (Kivy lists them in
its warning), and the micro:bit **events are dropped without a warning** on
Kivy. `tests/test_microbit_export_fallthrough.py` pins that nothing crashes.

**MicroPython export** (a different kind of export — *onto a real micro:bit*,
not another PyGameMaker platform target) lives in `export/`: File menu →
"Export micro:bit (MicroPython) code..." generates a `main.py` per object,
offers to copy it straight onto a board already running MicroPython, and (V1
only) offers to build a ready-to-flash combined `.hex` for a board that isn't.
`docs/MICROBIT_STAGE_X_PLAN.md` is the plan.

## The tests

`tests/test_microbit_*.py` — simulator, actions, events, renderer, input, strip,
sound, radio, Blockly, the sample, and the export fall-through. They assert
*where* things land (LED (2,2) is red at its computed position; a click at A's
computed rectangle fires `microbit_button_a`), and several run a real
`GameRunner.run()` loop.

## What is not here yet

A live link to a real micro:bit over USB serial (Stage L), a combined-hex
export for a factory-fresh V2 board (needs a real flash-filesystem builder,
see `docs/MICROBIT_STAGE_X_PLAN.md`'s O5), and HTML5/Kivy parity (Stage P).
