# micro:bit extension -- Stage X plan (MicroPython export)

Written 2026-10-27. Status: **MVP (X0-X7) done, same day.** X8 (the
combined/universal-hex path) remains deferred behind O5's unstarted
licensing research. Expands the Stage X
sketch in `docs/MICROBIT_EXTENSION_PLAN.md` (that file's own goal/ground
rules/"what counts as a micro:bit" sections still apply and aren't repeated
here). Work the units in order, one unit >= one commit (code + regression
test + verification), push after each, tick the box with the commit hash --
same discipline as Stage S.

## Goal

Generate a `main.py` that runs a `microbit*` object's own program on a real
BBC micro:bit, with no engine, no pygame, no PyGameMaker installed on the
target device -- just the board and (for the MVP) a USB cable.

## Where this lives

`extensions/microbit/export/micropython_exporter.py`, **inside the
extension**, not `export/` (core's desktop/HTML5/Kivy/mobile exporters).
The original Stage-X sketch's `export/micropython_exporter.py` path was
shorthand; the ground rule ("folder extension, zero core changes") and the
Thymio precedent it names (`extensions/thymio/export/aseba_exporter.py`)
both put it under the extension's own `export/` subfolder. The menu entry
needs a new `PLUGIN_IDE_MENUS` hook in `extensions/microbit/__init__.py`
(Thymio's `_build_file_menu` is the template; the micro:bit extension has
no such hook yet).

## Scope decision: which path onto the device, and why

Two genuinely different mechanisms exist for getting code onto a micro:bit,
and they are **not freely combinable** -- confirmed from BBC's own
MicroPython storage docs: a device with a script *embedded in its firmware
hex* ignores any `main.py` on its filesystem outright. So this plan treats
them as alternatives, not a combined pipeline.

- **Path A -- copy onto a board already running MicroPython (the MVP,
  X1-X7 below).** The device shows up as both a USB mass-storage drive
  *and* a serial REPL once MicroPython is on it. `microfs` (pure Python,
  wraps `pyserial`) can `put()` a `main.py` over that serial connection in
  one call; no `.hex` building, no firmware licensing question, works
  identically on V1 and V2. This is almost exactly Stage L's `link.py`
  dependency story (`pyserial`, `_missing_dependency_message`,
  auto-detect by USB VID/PID) reused for a one-shot write instead of a
  live stream.
- **Path B -- a combined/universal `.hex` a factory-fresh board can be
  flashed with by drag-and-drop, no prior setup.** This is real and
  documented (`tools/makecombinedhex.py` / `tools/hexlify.py` in the
  official `micropython/micropython` microbit port, or the `uflash`
  package for a V1-only runtime), but it means vendoring a compiled
  firmware binary per hardware revision (V1 ihex, V2 "universal hex") --
  a license question distinct from the MIT-licensed *source* this repo
  already vendors for images/fonts (`extensions/microbit/
  THIRD_PARTY_LICENSES.md`), a real size cost, and no in-repo way to
  build it without either shipping those binaries or a JS/Node tool this
  repo has deliberately avoided depending on elsewhere (Stage P's own
  "no Node in CI" constraint). **Deferred to its own unit (X8, optional)**
  with its own research pass before any code is written -- not assumed,
  not started here.

The MVP's own boundary, stated plainly for the export dialog's copy: **the
student's board must already be running MicroPython** before this feature
helps them. Getting MicroPython onto a brand-new board is a one-time step
via the official python.microbit.org editor or offline flasher, outside
this tool's scope for the MVP -- same shape as Stage L already accepting
"a physical micro:bit is needed" as a known limit.

## The generated program's shape

One `main.py` per micro:bit object found in the project (mirrors Thymio's
one-file-per-object `_find_thymio_objects` pattern) -- each board is its
own physical device, flashed separately.

```
from microbit import *
import music, radio                 # only the modules actions/events need

# -- one-time setup (from the object's Create event, plus anything an
#    action needs primed before the loop) --
display.set_brightness(...)          # if set in Create
radio.config(group=...)              # if any radio action/event is used
radio.on()
compass.calibrate()                  # if "compass heading" is read anywhere
...

while True:
    # -- Step event body, verbatim --
    ...

    # -- one polled check per event type the object actually listens for --
    if button_a.was_pressed():
        ...                           # that event's action list
    if accelerometer.was_gesture("shake"):
        ...
    if pin0.is_touched() and not _pin0_was_touched:
        ...
    _pin0_was_touched = pin0.is_touched()
    msg = radio.receive()
    if msg is not None:
        radio_string, radio_number = msg, _as_number(msg)
        ...
```

No event-handler functions, no classes -- one flat script, top-level
`while True:` loop. That's a deliberate simplicity choice, not a
shortcut: it means a `read_sensor` write to a plain variable name is
already a top-level global, so the generator never needs `global`
declarations anywhere, and there's no call-stack indirection to debug in
generated code a student might open out of curiosity.

**Edge detection, per event type:**
- Buttons A/B/AB and gestures already have **blocking-free, edge-reporting
  calls built into MicroPython** -- `button_a.was_pressed()` /
  `accelerometer.was_gesture(name)` return True once per press/occurrence
  since they were last checked. No hand-rolled state needed; this is
  exactly what the original sketch assumed.
- **Pin touches have no `was_touched()` equivalent** -- only
  `pinN.is_touched()`, a level read. The generator emits one
  `_pinN_was_touched` module-level bool per touch event used and does the
  rising-edge check by hand.
- **Loud/quiet sound (microphone, V2 only)** needs the same hand-rolled
  edge tracking against `microphone.sound_level()` crossing the
  simulator's own threshold (`sound.py`'s existing constants, reused
  verbatim so the exported behaviour matches what the student tested in
  the simulator).
- **Radio** has no edge concept to begin with -- `radio.receive()` returns
  the next queued message or `None`; "received" means "not None this
  pass," checked once per loop.
- **`microbit_display_done` / `microbit_sound_done` have no real-device
  equivalent and are explicitly unsupported.** On the device,
  `display.show()`/`display.scroll()`/`music.play()` are *already*
  blocking by construction -- "done" is simply "the next line of code
  runs." The simulator's queue exists purely to reproduce that blocking
  behaviour inside a non-blocking game loop; real hardware needs none of
  it. These two event types go straight into the unsupported-action
  warning list (see Testing/Warnings below), not a crash and not a
  silent drop.

## Action -> MicroPython mapping

All 16 `PLUGIN_ACTIONS` (confirmed by reading `actions.py`: 6 display + 3
sound + 2 radio + 1 sensor-read + 4 conditions), with the exact call and
every conversion found while researching this:

| micro:bit action | MicroPython call | Notes |
|---|---|---|
| `microbit_show_image` | `display.show(Image("r0:r1:r2:r3:r4"))` then `sleep_ms(hold)` if `hold > 0` | `display.show()` for a single image doesn't block for a hold time on its own; the generator adds the sleep explicitly. Built-in names pass straight through as `Image.<NAME>` (that's *why* `images.py` stores MicroPython's own constant names -- see its docstring). |
| `microbit_scroll_text` | `display.scroll(text, delay=delay_ms)` | Default `wait=True` already blocks until done -- the "queue and play one after another" behaviour is native, no queue code needed. |
| `microbit_show_number` | `display.show(number)` | `display.show()` accepts a number directly and scrolls automatically past one digit -- exact match, no translation. |
| `microbit_set_pixel` | `display.set_pixel(x, y, brightness)` | Direct 1:1 -- both sides already use the 0-9 scale (`simulator.py`'s own comment: "brightness 0-9 like MicroPython's display.get_pixel"). |
| `microbit_clear_display` | `display.clear()` | Direct. |
| `microbit_set_brightness` | `display.set_brightness(round(value / 255 * 9))` | **Scale conversion, found while researching this plan.** `MicrobitSimulator.set_brightness` clamps to 0-255 (confirmed in `simulator.py:230`), matching the action schema's "Brightness (0-255)" description, but the real device's `display.set_brightness()` takes 0-9. Silently emitting the raw 0-255 value would set every real brightness to 9 (clamped) for any value above 9. |
| `microbit_play_tone` | `music.pitch(frequency, duration)` | `music.pitch()` is the single-tone call with an explicit millisecond duration -- a closer match than composing a one-note `music.play()` string. |
| `microbit_play_melody` | `music.<NAME>` for a built-in name, else `music.play(notes, tempo=(4, tempo_bpm))` | Built-in names pass straight through, by design (`melodies.py`'s docstring). `music.play()`'s `tempo` kwarg is a `(ticks_per_beat, bpm)` tuple, not a bare bpm -- conversion needed. |
| `microbit_stop_sound` | `music.stop()` | Direct. |
| `microbit_radio_set_group` | `radio.config(group=group)` (+ `radio.on()` once, emitted in setup the first time any radio action/event is used) | `radio.on()` must run once; re-running `radio.config()` on a later call is fine and simply changes the group. |
| `microbit_radio_send` | `radio.send(str(value))` | `radio.send()` only takes strings on the device; the generator wraps every value, same as the simulator's `clean_message()` does today. |
| `microbit_read_sensor` | one call per `SENSORS` entry, see table below | Writes a plain module-level global (`global.X` and a bare name both collapse to the same thing on a single-board export -- see "Variable semantics"). |
| `microbit_if_button` | `button_a.is_pressed()` / `button_b.is_pressed()` / `button_a.is_pressed() and button_b.is_pressed()` / `pin_logo.is_touched()` for `"logo"` | `pin_logo` is V2-only (Open Decision O2, below). |
| `microbit_if_gesture` | `accelerometer.is_gesture(name)` | Level check, not edge -- matches the simulator's `current_gesture ==` comparison exactly (the edge-triggered `was_gesture()` is reserved for the *event* polling loop, a different action). |
| `microbit_if_tilt` | compare `accelerometer.get_x()/get_y()/get_z()` against the value with the chosen operator | Direct; no calibration needed for raw accelerometer axes (unlike compass, next). |
| `microbit_if_pixel` | compare `display.get_pixel(x, y)` against the value | Direct -- both sides 0-9. |

`microbit_read_sensor`'s `SENSORS` list, one call each:

| sensor name | call |
|---|---|
| accelerometer x/y/z | `accelerometer.get_x()` / `get_y()` / `get_z()` |
| acceleration strength | `accelerometer.get_strength()` |
| compass heading | `compass.heading()` -- **needs `compass.calibrate()` run at least once first.** An uncalibrated compass starts an on-device calibration dance (tilt the board to light every LED) the moment `heading()` is first called -- surprising mid-game. The generator emits `compass.calibrate()` in setup, with a comment, whenever "compass heading" is read anywhere in the object. |
| light level | `display.read_light_level()` |
| temperature | `temperature()` (module-level builtin) |
| sound level | `microphone.sound_level()` -- V2 only (O2) |
| pin 0/1/2 analog | `pin0.read_analog()` / `pin1...` / `pin2...` |

## Variable semantics

On the simulator, `global.X` writes to `GameRunner.global_variables` and a
plain name writes to the instance via `setattr`, because many simulated
boards can share one game process. **A real export has none of that**:
each physical board runs its own standalone `main.py`, so both forms
collapse to the same thing -- a plain top-level Python name in that one
file. No cross-board state exists post-export; two exported boards that
both read into `global.score` do not share a score (only `radio_send`/
`radio_receive` cross boards, same as the simulator). Worth a line in the
generated file's header comment so this isn't a silent surprise.

**Generic actions in scope.** The Aseba exporter's own precedent is
narrower than it first looks: its "variable" translators
(`thymio_set_variable`, `thymio_if_variable`, ...) are Thymio-namespaced
actions, not core's generic `set_variable`/`test_variable` -- those two
*fall through unsupported* on Thymio's export today (confirmed: they're
absent from `_get_action_translator`'s dict). Stage X makes a deliberate,
narrow improvement here rather than copying that gap: core's
`set_variable`, `test_variable`, `comment`, and the block-structure
actions (`start_block`/`end_block`/`else_action`) are supported directly
(plain Python assignment / `if`-`else` / a `#` comment / block
indentation), because "read a sensor into a variable, then compare it" is
exactly the kind of program this feature is for. Everything else outside
the micro:bit's own 16 actions and this short list goes into the
unsupported-action warning, not a crash and not a silent drop -- the
sketch's own stated improvement over the Aseba exporter's silent
`_translate_action` fallthrough (confirmed: an unknown action type there
just returns `""`, with no warning at all).

## Open Decision O2, resolved concretely for Stage X

The existing plan's O2 ("the simulator models the V2 superset... Stage X
must then flag V2-only actions when exporting for a V1 board") becomes: the
export dialog asks **V1 or V2** (default V2, per O2's own note that most
schools now have V2 boards), and the generator **skips + warns** rather
than emitting code that will raise `AttributeError` on an older board, for:
- `microbit_if_button` with `button == "logo"` (`pin_logo` is V2-only),
- "sound level" in `microbit_read_sensor` and the loud/quiet-sound events
  (`microphone` is V2-only).

## New Open Decisions from this plan

- **O5 -- the combined/universal-hex path (Path B above) is deferred, not
  rejected.** Needs its own research unit before any code: confirm the
  compiled-firmware binaries' actual license terms (distinct from the MIT
  *source* license already on file), their size, and whether
  `makecombinedhex.py`'s logic is reimplementable without a Node/JS
  dependency this repo has avoided elsewhere. Do not start X8 without
  that research written down first.
- **O6 -- where the V1/V2 choice lives.** A per-export dialog option (like
  picking a desktop export platform) versus a per-project setting next to
  `is_microbit`. Leaning per-export-dialog: a classroom with mixed V1/V2
  boards shouldn't need two project copies. Settle when X3 is written.

## Units

| Unit | What | Done |
|---|---|---|
| X0 | Commit this plan. | [x] `9f55d14d` |
| X1 | `export/micropython_exporter.py` skeleton: find `microbit*` objects (mirrors Thymio's `_find_thymio_objects`), load merged object data (`utils.project_file_merge`), emit one `main.py` per object with just the Create-event setup lines and an empty `while True: pass` loop. Test: a two-board sample project produces two distinct files, non-microbit objects are skipped, output is valid Python (`py_compile`). | [x] `d2516c16` |
| X2 | Display + sound action translators (the first two mapping-table sections above), plus the brightness 255->9 conversion and the melody-tempo conversion, each with a dedicated test asserting the exact emitted line. | [x] `31d49148` |
| X3 | Radio + sensor-read translators, the V1/V2 export-dialog option (O6), and the V1/V2 skip-and-warn behaviour (O2) with tests for both a V1 and a V2 export of the same project. | [x] `e389cb79` |
| X4 | Condition translators (`if_button`/`if_gesture`/`if_tilt`/`if_pixel`) plus the generic `set_variable`/`test_variable`/`comment`/block-structure subset, with indent-level tracking (same approach as `AsebaExporter.indent_level`). | [x] `cd46d868` |
| X5 | Event polling: the flat `while True:` body wiring for every supported event type, including the pin-touch and loud/quiet-sound hand-rolled edge tracking and the `compass.calibrate()` auto-insert rule. `microbit_display_done`/`microbit_sound_done` land in the unsupported-action warning here. Test: a project using every event type compiles and the generated source contains the expected `if`/edge-tracking shape for each. | [x] `ead51201` |
| X6 | The unsupported-action warning collection (actions AND events outside the supported set get named, not dropped -- the Kivy-warning precedent) surfaced through the export result and the generated file's own header comment. | [x] `104e3a7d` |
| X7 | Getting it onto the device (Path A, MVP): `microfs` + `pyserial` through `_missing_dependency_message`, USB VID/PID auto-detect port (reuses Stage L's own approach), the IDE menu entry via a new `PLUGIN_IDE_MENUS` hook on `extensions/microbit/__init__.py` (Thymio's `_build_file_menu` is the template), the UI flow (`export_microbit_code(ide)`, modeled on `extensions/thymio/export/__init__.py`'s `export_aseba_code`: project-open check, output picker, try/except with a critical dialog, no-boards-found warning, success dialog naming any warnings). Tests: the file-generation side fully (headless); the actual serial write is marked "needs real hardware," matching Stage L's own standing exception to CI coverage. | [x] (commit pending) |
| X8 (optional, gated on O5) | The combined/universal-hex path (Path B), only after O5's research is written up and the licensing question is answered. Not started as part of this plan's main line. | [ ] |

## Testing strategy

- **`py_compile` against a stub `microbit` module** -- the same tier this
  repo already uses for Kivy (`test_kivy_raycast.py`'s stub-kivy harness):
  a hand-written `microbit`/`music`/`radio` stub package with the real
  function signatures but no hardware behind them, so generated code is
  proven syntactically and structurally correct (right call, right
  argument count) without needing a board in CI.
- **Golden-output tests per action/event** -- exact expected source lines,
  one assertion per mapping-table row, so a future change to a translator
  is caught precisely (same granularity as `test_draw_action_codegen.py`'s
  HTML5/Kivy precedent).
- **A real-hardware tier, explicitly out of CI** -- like Stage L's
  fake-serial-port unit tests versus its "needs a physical micro:bit"
  exception, `microfs`'s actual `put()` call and a real device's actual
  behaviour (timing, the compass-calibration gesture, V1-vs-V2 attribute
  errors) can only be verified by hand, once, and that gap gets written
  into the QA checklist the same way Stage S/P's "still needs human eyes"
  notes already do.

## Expected size

X1-X2 are the largest (the full action-mapping surface); X3-X6 are each a
short session; X7 (device I/O + menu wiring) is comparable to Stage L's own
`link.py` unit. About 6-7 sessions for the MVP (X0-X7); X8 is explicitly
not sized until O5 is answered.
