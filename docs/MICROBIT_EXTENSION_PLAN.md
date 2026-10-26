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
not an option, so in the simulator display actions **queue** and play one
after another. That is also what the device does: the runtime makes a
second `scroll`/`show` wait for the display to be free, in MakeCode fibers
and MicroPython alike (O3, settled in S2). `clear` empties the queue. A
`microbit_display_done` event fires when the queue empties, so students can
chain animations. Stage X emits blocking calls, so a program behaves the
same on both.

Two guards stop a Step event that shows something every frame from piling
up a backlog the device would never have (its loop blocks instead):
showing exactly what is already displayed is a no-op, and the queue holds
at most 16 items (`MAX_QUEUE`), refusing more.

The simulator advances with the frame `dt`. Scroll speed defaults to
MicroPython's 150 ms per column. Scrolling is monospaced (5 columns per
character plus a 1-column gap, as MakeCode scrolls); MicroPython's default
is proportional, so Stage X passes `monospace=True` to match. Characters
outside printable ASCII, accented letters included, show as `?`, as on
the device.

*Sources (S2):* the font and the 64 built-in images are generated from the
MIT-licensed micro:bit runtime and MicroPython sources
(`extensions/microbit/THIRD_PARTY_LICENSES.md`). Gestures are codal-core's
`Accelerometer::updateGesture`/`instantaneousPosture`, ported line for
line and run on a fixed 20 ms sample clock so the damping counts mean the
same time as on the device. Sound thresholds are codal-microbit-v2's
85 dB / 65 dB, which is 196 / 118 on MicroPython's 0–255 `sound_level`
scale. A resting board reports "face up" about 120 ms after start,
as a real one does at boot.

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
unit S8) on a dedicated mixer channel. If the mixer is unavailable
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

*Found in S1:* core already has a per-project mechanism for this
(`config/toolbox_visibility.py` `active_extensions`, decided 2026-09-30).
An extension's actions show only when the project uses one of them or
lists the extension in `settings.active_extensions`, which the Project
Settings dialog offers as a checkbox for every extension whose manifest
`provides_actions` names real actions. S10 should rely on that instead of a
bespoke `ToolboxVisibilityFilter`, and the S10 project template just sets
`active_extensions: ["microbit"]`. Until S3 fills `provides_actions`, the
extension doesn't appear in that dialog (`tests/test_project_settings_extensions.py`
pins the current list).

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
| S0 | Commit this plan. | [x] |
| S1 | Skeleton: `extensions/microbit/` with `extension.json`, an `__init__.py` docstring map, `state.py`, and the instance-created binding (`microbit*` prefix / `is_microbit`). Test: a room with `microbit_1` gets a simulator, `obj_player` doesn't. | [x] `c2f56b16` |
| S2 | `simulator.py`: pure `MicrobitSimulator` with the display buffer, brightness, display queue (show image / scroll / number with timing), buttons/logo/pins state, accelerometer + gesture derivation (shake from accel-magnitude spikes, tilt thresholds as in MicroPython), compass, light, temperature, sound level, `update(dt)` returning fired events. Plus `images.py`. Exhaustive pure unit tests (scroll timing per column, gesture edges, interrupting a scroll). | [x] `8705cd5e` |
| S3 | `actions.py` + `handlers.py`: display, sensor-read and condition actions (English schemas, `PluginExecutor`); an action-picker tab (`register_action_tabs`). Handler tests via `load_all_plugins` + `ex.action_handlers`. | [x] `dc90f303` |
| S4 | `events.py` + `runtime.py`: `PLUGIN_EVENTS` (with sub-events for pins/gestures) and the frame-update hook that steps every simulator and fires events, with the same early-out as Thymio when the room has no micro:bit. Real `GameRunner.run()` test: a posted button state fires `microbit_button_a`, and its handler's `show_image` lands in the buffer. | [x] `9e935dec` |
| S5 | `renderer.py` + overlay: procedural board, LEDs, buttons, logo, pins, scale property, sprite-body option. Pixel tests at computed LED positions; a screenshot via `PYGM_SCREENSHOT` checked by eye once. | [x] `cfff9d8d` |
| S6 | `input.py`: mouse on A/B/logo/pins (with AB chord), swallowed clicks, opt-in keyboard mapping. Click-at-computed-rect tests; a test that with keyboard off, an authored `keyboard_press` A event still fires and the micro:bit ignores it. | [x] `6e5f4b8b` |
| S7 | Sensor strip: tilt pad, shake button, sliders, a `microbit_show_sensors` toggle. Drag tests (tilt pad → accel x/y → `tilt_left` gesture event). | [x] `3d375ee9` |
| S8 | Sound: `melodies.py`, square-wave synthesis on its own mixer channel, state-only fallback under the dummy driver. Tests on the state; check by ear once on a real machine. | [x] `2aff9268` |
| S9 | `radio.py` bus + radio actions/event. Two-micro:bit room test: A's button sends 7 → B receives it, A doesn't, and a different group doesn't. | [x] `b8ea92fb` |
| S10 | Blockly categories + "microbit" preset + visibility through `active_extensions` (see "Visibility in the IDE") + FR category/block translations (accents checked). Welcome-tab "New micro:bit project" template. Translation-resolution test like `tests/test_extension_ui_translations.py`. | [ ] |
| S11 | Sample `samples/microbit_1` ("Dé et humeurs"): A = happy face, B = sad face, shake = random dice face, logo = scroll a quoted score. `README.md` + `README.fr.md`, Welcome tab, `tools/smoke_run_samples.py`, `test_edition_sample_filter`'s advanced-prefix list (decide per O1), and a desktop-export render check with `tools/verify_desktop_export.py --compare`. | [ ] |
| S12 | Close-out: the extension's `README.md` (file map like Thymio's), `wiki/Microbit.md` + `_fr.md` (other languages deferred, as with `Network.md`), regenerate the action reference (`tools/gen_action_reference.py`; check `FILE_KEY` gets the new category), a CLAUDE.md session note. HTML5/Kivy: confirm the actions fall through to the existing unsupported-action warning and don't crash an export (a test; parity is Stage P). | [ ] |

*Found in S3:* the actions are plain `PLUGIN_ACTIONS` (`ActionType`, category
"micro:bit") like `raycast_2_5d`'s, not Thymio's `ActionDefinition` set; the
`microbit` picker tab is registered through `register_action_tabs` as the plan
said, but only Thymio's own dialogs read those tabs. Conditions just return a
bool and core's generic then/else handling does the rest. One known limit of
the zero-core rule: a *false* micro:bit condition whose guarded unit is itself
another micro:bit condition doesn't chain-skip, because core's
`ActionExecutor._QUESTION_ACTIONS` lists the question names (Thymio's and
`is_instance_owner` have the same gap). *(Corrected in S10: Blockly does NOT
emit then/else for these -- the generated blocks are plain statement blocks,
so a condition guards the next block GameMaker-style, with the core
`start_block`/`end_block`/`else_action` blocks for groups. The gap therefore
only shows for a condition directly followed by another micro:bit condition.)*
Revisit only if a generic "question" flag on `ActionType` is ever added.

*Decided in S4:* events are **flat names**, not sub-events:
`microbit_button_a/b/ab`, `microbit_logo_touched`, `microbit_pin_0/1/2`,
`microbit_gesture_<shake|logo_up|logo_down|tilt_left|tilt_right|screen_up|
screen_down|free_fall|2g|3g|6g|8g>`, `microbit_loud_sound`,
`microbit_quiet_sound`, `microbit_display_done` (22 in all). Same vocabulary
as the table above, but it needs no sub-event selector in the editor and
maps one-to-one onto Blockly blocks, as `collision_with_<object>` does.
`microbit_radio_received` waits for S9. Events fire on the board's own
instance, stepped by `1/fps` per frame from the `after_collision` hook. The
Blockly event map (`PLUGIN_EVENT_BLOCKLY_MAP`) is left to S10, when the
blocks exist.

*Decided in S6:* a mouse can't press two buttons, so the **A+B chord is a
right-click on either A or B** (left-click presses one, held until release).
Pressing only sets simulator state; the S4 frame update fires the events, so
a click whose down and up land in the same frame still registers. Pad 3V/GND
aren't touch pins and don't respond. Keyboard (`microbit_keyboard`, instance
variable or object property, default off): `A`/`B` buttons, arrows hold a
1000 mg tilt on x/y (opposite keys cancel, release returns to rest), `S`
shakes. The tilt directions follow the gesture names, so the S7 tilt pad
should use the same mapping. `layout_for`/`scale_of`/`center_of` live in the
pure `layout.py` so `input.py` never imports pygame (the IDE loads the
extension's schemas without it). Overlays and hit-testing both work in
screen space, so a room with views would misplace the board; revisit if a
sample ever needs scrolling.

*Decided in S7:* the strip is a panel under the board (tilt pad, SHAKE
button, light / temperature / compass / sound sliders) drawn and hit-tested
from the same pure `layout.py`. The tilt pad edge is one g (1024 mg), so
dragging to an edge triggers the real tilt gesture; **releasing springs back
to rest**, like the keyboard arrows, while sliders keep their value. The input
hook has no mouse-motion kind, so instead of a core change the frame update
polls `pygame.mouse.get_pos()` while a tilt/slider drag is held
(`input.drags()` / `follow()`); a lost release would leave a drag running, the
same exposure buttons have. The sound slider goes through `set_sound_level`,
so crossing the thresholds fires `microbit_loud_sound` / `quiet_sound`.
`microbit_show_sensors: false` (instance variable or object property) hides
the strip and makes it unclickable. Slider hit areas overhang the track by a
few pixels so the knob is grabbable at both ends.

*Decided in S8:* `sound.py` (pure) ports MicroPython's `music.play` note
format and timing: octave/duration persist within one melody (reset per
call), a quarter note is 4 ticks, 4 ticks make a beat, 120 bpm, and each note
sounds for its length less a 10 ms articulation. Deliberate deviation: the
device is silent or garbled for `E#`/`B#`/`Cb`/`Fb`; here they are the
enharmonic natural note. `melodies.py` is generated from the MicroPython
source (21 tunes) and `microbit_play_melody` also takes your own notes
(`"C4:4 E G C5:8 R:4"`) and a tempo. Sounds queue like the display (16
items, repeats not stacked); `microbit_sound_done` chains them and
`microbit_stop_sound` cuts them off without firing it. The simulator stays
pure and *reports* `sound_note`/`sound_stop`; `audio.py` turns those into a
16-bit square wave on mixer channel 0, reserved. It caches raw PCM bytes and
fetches the channel fresh every call, never `Sound`/`Channel` objects (they
dangle after `pygame.quit()`, the same crash the S5 Font cache hit). With no
mixer the calls do nothing and `sim.tone` is the record. One speaker channel
is shared, so two boards sounding at once interrupt each other. **By-ear
check still owed** on a real machine.

*Decided in S9:* the radio is **not a global bus**: `radio.deliver(sims)` is
a pure function that, once per frame ahead of the boards' updates, moves each
board's outbox to the *other* boards in its group, so a room change or a new
game starts clean and there is no process-wide state for a test to leak. A
board never hears itself; every board starts in group 0; groups clamp to
0-255. Numbers stay numbers, anything else is text cut to 32 characters (the
device's default payload). A received message fires
`microbit_radio_received` and sets the receiving instance's `radio_number`
(0 if the text isn't numeric) and `radio_string` (always the text), even when
no handler is authored, so a Step event can read them. Messages sent in a
frame arrive in the same frame's hook pass at the latest, otherwise the next.
The radio is always on (no `radio.on()` step to forget), and bridging it over
`multiplayer_lan` stays out of scope.

*Decided in S10 (what the plan got wrong, found by reading core first):*
- **No hand-written Blockly at all.** Every `ActionType` is auto-generated
  into a toolbox category named after `ActionType.category` ("micro:bit"),
  extension events ride core's generic `event_extension` block, and per-project
  visibility is `active_extensions` (S1 note). So no `PLUGIN_BLOCK_CATEGORIES`
  and no five-way "Affichage/Entrées/Musique/Radio/Capteurs" split: that would
  need curated categories nothing else shows.
- **`provides_events` was missing from the manifest** (S4 oversight, caught by
  the S10 visibility test): without it core treated the 24 events as plain core
  events -- always offered, never in the extension event block. The manifest now
  lists them, so they follow the same activation rule as the actions.
- **French for the generated blocks** goes through a new generic seam,
  `config.blockly_generated_block_i18n.register_generated_block_translations`
  (first entry wins, so an extension can't change a core label), fed by
  `PLUGIN_GENERATED_BLOCK_TRANSLATIONS` and loaded by `plugin_loader`. French
  only, matching that table; other languages fall back to English. The seam
  also lets raycast/multiplayer translate their canvas blocks later.
- **No "microbit" preset.** Active extensions override the preset, and the
  Blockly config dialog's preset list is fixed (Thymio needed its own dialog),
  so a dedicated preset would be unreachable and change nothing but core blocks.
  A project that wants a tidy toolbox uses `beginner` plus
  `active_extensions: ["microbit"]`.
- **No "New micro:bit project" template.** Templates are core
  (`resources/templates/<id>` and a fixed combo in the New Project dialog), so
  a template would mean a core change naming micro:bit or a new seam. The S11
  sample (a ready project that already lists the extension) and the Project
  Settings checkbox cover discovery instead; revisit if teachers ask.
- **Known cosmetic gaps, left alone:** the micro:bit blocks draw in the default
  grey (the colour table in `blockly_workspace.html` is core and has no
  extension entry), and the event drop-down labels are the English display
  names. Both would need a small core JS/Python seam.
- **Not verified in a real Blockly canvas** (no web engine in this environment):
  the tests pin what Python sends -- category, label, param types, XML-safe
  defaults -- not the rendered toolbox. Eyeball it once.

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
- ~~**O3 — Display queue semantics.**~~ Settled in S2: append, because
  the device makes display commands wait for each other (see "Time and
  blocking").
- **O4 — Shipping visible.** Thymio ships hidden behind `show_thymio_tab`.
  The micro:bit doesn't need a hidden phase if O1's gating is accepted.
