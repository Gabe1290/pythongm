# micro:bit extension plan

Written 2026-10-25. Status: **not started**. This plan is the resume state:
work the units in order, one unit ≈ one commit (code + regression test +
verification), push after each, and tick the box with the commit hash.

## Goal

Let students program a BBC micro:bit in PyGameMaker, in three layers that
share one action/event vocabulary:

1. **Stage S — simulator (this plan's first and largest stage).** A micro:bit
   drawn in the game window: 5×5 LED display, buttons A/B, touch logo,
   pins, accelerometer/gestures, compass, light, temperature, sound level,
   speaker, radio. No hardware needed.
2. **Stage L — live link.** A real micro:bit over USB serial drives the same
   simulated state, so a game can be controlled by tilting a real board and
   can light its LEDs. Same project, same actions; only the input source
   changes.
3. **Stage X — MicroPython export.** Generate a `main.py` (and, if feasible,
   a `.hex`) that runs the program on the device itself.

Stages P (HTML5/Kivy parity) and D (docs, wiki, tutorial) follow.

## Ground rules

- **Folder extension, zero core changes** — `extensions/microbit/`, built
  only on the seams in `extensions/README.md`, the way `extensions/thymio/`
  is. If a unit finds it needs a core change, stop and write it up here
  first. A new generic seam is fine; core code that names micro:bit is not.
- **Thymio is the template.** It already uses the same hooks this extension
  needs: instance-created (binding an object to a device), instance overlay
  (drawing the board), input (clickable buttons), frame update (stepping
  the simulator and firing events), Blockly categories/presets, and an
  exporter to the device's own language. Copy its structure, not its code.
- **English-first schemas.** `display_name`/`description` are English;
  French (and later other languages) come through
  `PLUGIN_BLOCK_TRANSLATIONS` / `PLUGIN_BLOCK_CATEGORY_TRANSLATIONS`.
  `multiplayer_lan` was authored French-first and that left an i18n gap
  (`TODO.md`); don't repeat it. French strings carry their accents
  (« Afficher une image », « Bouton A pressé », « Secouer »).
- **The simulator is pure.** `simulator.py` imports neither pygame nor Qt,
  just like `ThymioSimulator`, so it can be unit-tested headlessly and
  reused by the Stage-L bridge and the Stage-P ports.
- Session-limit rule from CLAUDE.md: no multi-agent workflows; one unit per
  commit; push after each.

## Design decisions (settled unless reopened in "Open decisions")

### What counts as a micro:bit

As with Thymio: an object whose name starts with `microbit` (case-
insensitive), or a room instance whose entry sets `is_microbit: true`, gets
a `MicrobitSimulator` attached by `PLUGIN_INSTANCE_CREATED`. State lives
under `instance.extension_state["microbit"]` (`state.py`:
`attach_simulator` / `simulator_of`, mirroring Thymio's). Several
micro:bits in one room are allowed; that's what makes radio worth
simulating.

### Programming model: MakeCode-style events

PyGameMaker is event-driven, and so is MakeCode, which most teachers know.
So the vocabulary follows MakeCode, not MicroPython's polling loop:

| Kind | Items |
|---|---|
| Events | `microbit_button_a`, `microbit_button_b`, `microbit_button_ab`, `microbit_logo_touched`, `microbit_pin_touched` (sub-event per pin 0/1/2), `microbit_gesture` (sub-event per gesture: shake, logo up/down, face up/down, tilt left/right, free fall), `microbit_radio_received`, `microbit_loud_sound`, `microbit_quiet_sound` |
| Display actions | `microbit_show_image` (built-in image name or a 5×5 custom grid), `microbit_scroll_text`, `microbit_show_number`, `microbit_set_pixel` (x, y, brightness 0–9), `microbit_clear_display`, `microbit_set_brightness` |
| Sound actions | `microbit_play_tone` (frequency, duration), `microbit_play_melody` (built-in melody name), `microbit_stop_sound` |
| Radio actions | `microbit_radio_set_group`, `microbit_radio_send` (number or string) |
| Sensor reads | `microbit_read_sensor` (sensor: accel x/y/z, compass, light, temperature, sound level, pin 0/1/2 analog → into a variable), like Thymio's `thymio_read_proximity` |
| Conditions | `microbit_if_button` (pressed/held), `microbit_if_gesture`, `microbit_if_tilt` (axis, comparison, value), `microbit_if_pixel` |

Every action becomes a Blockly block, the way it does for core actions.
"Forever" is the ordinary Step event, so it needs no special block.

### Time and blocking

On the device, MicroPython's `display.scroll()` and MakeCode's
`show string` **block** until the scroll finishes. Blocking the game loop is
not an option, so in the simulator display actions **queue**. A new display
action replaces a scroll that is still running (MakeCode's behaviour when
a button event interrupts), and a `microbit_display_done` event fires when
the queue empties so students can chain animations. This difference from the
real device is documented in the guide. Stage X emits blocking calls, so a
program that relies on chaining behaves the same on both.

The simulator advances with the frame `dt`. Scroll speed defaults to
MicroPython's 150 ms per column.

### Drawing the board (instance overlay)

`renderer.py` draws the board procedurally with pygame, with no sprite
asset needed:
- the board body;
- 25 LEDs whose red glow scales with brightness 0–9;
- buttons A and B and the touch logo;
- the edge connector with pads 0/1/2/3V/GND;
- a speaker indicator while a tone plays.

The board is drawn centred on the instance and sized by an optional
`microbit_scale` object property (default 1.0, about 220 px wide). If the
object has a sprite, the sprite is drawn instead of the procedural body and
the LEDs are drawn on top.

Below the board sits a **sensor strip**: small drawn controls for light,
temperature, compass and sound level, plus a tilt pad and a "shake" button.
It lives in the pygame window, not a Qt panel, so it works in Test Game,
in desktop exports and later in HTML5. It can be hidden per object
(`microbit_show_sensors: false`) for a game that only uses the display.

### Input (input hook)

- **Mouse, always on:** clicking A, B, the logo or a pin presses it (held
  while the mouse button is down; clicking A and B together fires
  `button_ab`), and the click is swallowed. Dragging on the tilt pad sets
  accelerometer x/y and derives the tilt gestures. The shake button
  produces a shake gesture. Dragging a strip slider sets that sensor.
- **Keyboard, opt-in:** Thymio grabs the arrow keys unconditionally, but
  student games often use A/B/arrow keys for themselves. So keyboard
  shortcuts are off by default and enabled per object
  (`microbit_keyboard: true`): `A`/`B` = buttons, arrows = tilt, `S` = shake.

### Sound

Thymio's tone is state-only: `play_tone` records frequency and duration and
nothing is heard. The micro:bit should actually beep. Synthesise a square
wave with `pygame.sndarray` (numpy is already a dependency, check this in
unit S4) on a dedicated mixer channel. If the mixer is unavailable
(`SDL_AUDIODRIVER=dummy`, as in tests), fall back to state-only, so tests
can still assert on the simulator's audio state.

### Radio

A process-wide bus (`radio.py`), keyed by group 0–255. `radio_send` from
one simulated micro:bit is delivered as `microbit_radio_received` to every
*other* micro:bit in the same group on the next frame. The received value
goes into the instance variables `radio_number` / `radio_string`. The
sender doesn't hear itself, as on the real device. Bridging radio over
`multiplayer_lan` is out of scope.

### Visibility in the IDE

The extension ships `enabled: true`. Its Blockly categories ("micro:bit —
Affichage", "Entrées", "Musique", "Radio", "Capteurs") are hidden by a
`ToolboxVisibilityFilter` unless the project contains a micro:bit-bound
object. A "microbit" Blockly preset shows them explicitly, and a
"New micro:bit project" welcome-tab entry (unit S10) creates a project that
already has one, so the feature is discoverable. See open decision O1.

### Built-in images and melodies

Data tables in `images.py` / `melodies.py`, copied by value from the
MicroPython documentation: `HEART`, `HAPPY`, `SAD`, `YES`, `NO`, the
arrows, `SKULL` and so on, plus `DADADADUM`, `BIRTHDAY`, `POWER_UP` and so
on. Names stay the MicroPython constants so Stage X can emit
`Image.HEART` verbatim. Display labels get translated; the identifiers
don't.

## Landmines carried in from earlier work

- **Text through `_parse_value`:** `scroll_text` with `Score - 3` is
  evaluated as an expression (CLAUDE.md "On-screen text must be QUOTED").
  The handler reads its text parameter the way `draw_text` does, and the
  sample quotes its literals. `tests/test_sample_visible_text.py` must stay
  green.
- **Plugin actions shadow nothing:** don't add any `microbit_*` name to the
  static `ACTION_TYPES`, or `plugin_loader._load_actions` skips the
  plugin's version.
- **Synthetic package name:** the loader imports the extension as
  `pygm_extension_microbit.*`, so a spy has to patch the *loaded* module
  (see `_loaded_handlers()` in `tests/test_multiplayer_lan_ghosts.py`).
- **Schemas appear only after `load_all_plugins()`.** Handler tests
  dispatch through `ex.action_handlers[...]` after loading plugins.
- **Assert *where*, not *that*:** overlay tests check that LED (2,2) lit
  at brightness 9 is red at its computed screen position, and that a click
  at button A's computed rectangle fires `microbit_button_a`. Don't just
  check that something drew (the minimap lesson).
- **Instances aren't fully initialised until `run()`:** runtime tests go
  through a real `GameRunner.run()` with `pygame.event.post` + `_FakeClock`
  + a tick hook, like `TestRaycast1SampleSmoke`.
- **Collision events fire one side only:** irrelevant to the simulator
  itself, but the sample should keep all pickup logic on one side.
- **Frozen desktop exports:** `plugin_loader` resolves `extensions/` under
  `sys._MEIPASS`. Check that a desktop export of the sample still draws the
  board (unit S11), because a missing extension fails *silently* there.

## Stage S — simulator

| Unit | What | Done |
|---|---|---|
| S0 | Commit this plan. | [ ] |
| S1 | Skeleton: `extensions/microbit/` with `extension.json`, an `__init__.py` docstring map, `state.py`, and the instance-created binding (`microbit*` prefix / `is_microbit`). Test: a room with `microbit_1` gets a simulator, `obj_player` doesn't. | [ ] |
| S2 | `simulator.py`: pure `MicrobitSimulator` with the display buffer, brightness, display queue (show image / scroll / number with timing), buttons/logo/pins state, accelerometer + gesture derivation (shake from accel-magnitude spikes, tilt thresholds as in MicroPython), compass, light, temperature, sound level, `update(dt)` returning fired events. Plus `images.py`. Exhaustive pure unit tests (scroll timing per column, gesture edges, interrupting a scroll). | [ ] |
| S3 | `actions.py` + `handlers.py`: display, sensor-read and condition actions (English schemas, `PluginExecutor`); an action-picker tab (`register_action_tabs`). Handler tests via `load_all_plugins` + `ex.action_handlers`. | [ ] |
| S4 | `events.py` + `runtime.py`: `PLUGIN_EVENTS` (with sub-events for pins/gestures) and the frame-update hook that steps every simulator and fires events, with the same early-out as Thymio when the room has no micro:bit. Real `GameRunner.run()` test: a posted button state fires `microbit_button_a`, and its handler's `show_image` lands in the buffer. | [ ] |
| S5 | `renderer.py` + overlay: procedural board, LEDs, buttons, logo, pins, scale property, sprite-body option. Pixel tests at computed LED positions; a screenshot via `PYGM_SCREENSHOT` checked by eye once. | [ ] |
| S6 | `input.py`: mouse on A/B/logo/pins (with AB chord), swallowed clicks, opt-in keyboard mapping. Click-at-computed-rect tests; a test that with keyboard off, an authored `keyboard_press` A event still fires and the micro:bit ignores it. | [ ] |
| S7 | Sensor strip: tilt pad, shake button, sliders, a `microbit_show_sensors` toggle. Drag tests (tilt pad → accel x/y → `tilt_left` gesture event). | [ ] |
| S8 | Sound: `melodies.py`, square-wave synthesis on its own mixer channel, state-only fallback under the dummy driver. Tests on the state; check by ear once on a real machine. | [ ] |
| S9 | `radio.py` bus + radio actions/event. Two-micro:bit room test: A's button sends 7 → B receives it, A doesn't, and a different group doesn't. | [ ] |
| S10 | Blockly categories + "microbit" preset + toolbox visibility filter + FR category/block translations (accents checked). Welcome-tab "New micro:bit project" template. Translation-resolution test like `tests/test_extension_ui_translations.py`. | [ ] |
| S11 | Sample `samples/microbit_1` ("Dé et humeurs"): A = happy face, B = sad face, shake = random dice face, logo = scroll a quoted score. `README.md` + `README.fr.md`, Welcome tab, `tools/smoke_run_samples.py`, `test_edition_sample_filter`'s advanced-prefix list (decide per O1), and a desktop-export render check with `tools/verify_desktop_export.py --compare`. | [ ] |
| S12 | Close-out: the extension's `README.md` (file map like Thymio's), `wiki/Microbit.md` + `_fr.md` (other languages deferred, as with `Network.md`), regenerate the action reference (`tools/gen_action_reference.py`; check `FILE_KEY` gets the new category), a CLAUDE.md session note. HTML5/Kivy: confirm the actions fall through to the existing unsupported-action warning and don't crash an export (a test; parity is Stage P). | [ ] |

Expected size: S2, S5 and S7 are the big ones; the rest are each a short
session. About 12 sessions in all.

## Stage L — live link (sketch; detail before starting)

- A fixed **bridge program** (`bridge/bridge.py`, MicroPython) flashed once
  onto the device. Over USB serial at 115200 baud it streams compact text
  lines (`B a1 b0 l0`, `A x y z`, `C heading`, `T temp`, `L light`) at
  about 20 Hz and accepts commands (`D <25 digits>`, `S <text>`,
  `P <freq> <ms>`, `R <group> <msg>`).
- `link.py`: optional `pyserial`, reported through the
  `_missing_dependency_message` pattern (`pip install --user pyserial`).
  Auto-detect the port by USB VID `0x0D28` / PID `0x0204`. Single-threaded,
  non-blocking reads pumped from the frame hook, as in `multiplayer_lan`.
- `microbit_connect(port="auto")` / `microbit_disconnect` actions and a
  `microbit_connected` / `microbit_disconnected` event pair. While
  connected, the device's readings overwrite the simulator's inputs and
  display/sound commands are mirrored to the device. Students change
  nothing else in their program.
- Known risks: Linux `dialout` group permission (needs a clear error
  message), Windows COM ports, and whether school lab machines allow USB
  serial at all. A physical micro:bit is needed for anything past the
  protocol unit tests (a fake serial port).

## Stage X — MicroPython export (sketch)

- `export/micropython_exporter.py`, in the shape of
  `extensions/thymio/export/aseba_exporter.py`: event handlers → one
  `while True:` loop polling `button_a.was_pressed()`,
  `accelerometer.was_gesture()`, `radio.receive()` and so on, with Step
  as the loop body. Supported subset only. Unsupported actions are listed
  in a warning, not silently dropped (the Kivy precedent).
- Getting it onto the device: write `main.py` and copy it with `microfs`
  onto a board already running MicroPython, or build a `.hex`. `uflash`'s
  bundled runtime is V1-only, so V2 needs the official universal hex
  (research unit: licence, size, how to embed `main.py`). Copying a `.hex`
  onto the MICROBIT USB drive needs no extra software, which matters on
  locked-down lab PCs.
- Tests: generated code compiles (`py_compile` with a stub `microbit`
  module), plus golden-output tests per action.

## Stage P — export parity (sketch)

Port the simulator, overlay and input to HTML5 (`export_html5.js` through
the engine's extension registries) and Kivy (`export_kivy.py`
`SCENE_CODE`), as `raycast_2_5d` did. Pin the pure simulator logic with a
parity test like `test_raycast_export_parity.py`. WebSerial in Chrome/Edge
would bring Stage L to HTML5.

## Open decisions

- **O1 — Discoverability vs clutter.** The recommended default (toolbox
  hidden until a micro:bit object exists, plus a preset and a Welcome-tab
  template) keeps beginners' toolboxes clean. The alternative is an
  always-visible "micro:bit" category. Also decide whether `microbit_1`
  counts as an "advanced" sample hidden by the beginner edition (it is
  arguably the most beginner-friendly sample of all).
- **O2 — V1 vs V2 features.** The plan simulates the V2 superset (logo,
  microphone, speaker). Stage X must then flag V2-only actions when
  exporting for a V1 board. Most schools now have V2 boards, so check what
  the target classrooms own.
- **O3 — Display queue semantics.** Replace-on-interrupt (MakeCode) vs
  append. The recommendation is replace, plus the `display_done` event.
- **O4 — Shipping visible.** Thymio ships hidden behind `show_thymio_tab`.
  The micro:bit doesn't need a hidden phase if O1's gating is accepted.
