# micro:bit (BBC micro:bit simulator)

*[Home](Home) | [Full Action Reference](Full-Action-Reference-Microbit-Actions) | [Extensions](Extensions)*

---

PyGameMaker can put a **simulated BBC micro:bit** in your game window: a 5×5
LED display, buttons **A** and **B**, a touch logo, pins 0/1/2, an
accelerometer, light/temperature/compass/sound sensors, a speaker and a radio
— all drawn on the screen and programmed with the same events and actions as
the rest of the IDE. No hardware is needed. It is provided by the built-in
**micro:bit** [extension](Extensions), which ships enabled.

The bundled sample **`microbit_1`** ("Dice and Moods") is a complete example:
A and B show a happy and a sad face, a shake rolls a die, and touching the logo
scrolls how many rolls you have made.

---

## Getting started

1. Make an object whose **name starts with `microbit`** (for example
   `microbit_1`) and place one instance of it in a room. That object *is* the
   micro:bit: the engine draws the board over it and runs its simulator.
2. In **Project Settings → Extensions**, tick **micro:bit**. (A project that
   already uses a micro:bit action has it on automatically; one that does not
   never shows the micro:bit blocks or actions.)
3. Put the events on **that same object**: each micro:bit action works on the
   micro:bit that runs it. For example *Button A Pressed* → *Show Image*
   `HAPPY`.
4. **Test Game.** Click the buttons on the board.

An object can also be made a micro:bit by ticking `is_microbit` on its room
instance. Several micro:bits in one room are fine — that is what makes the
radio worth using.

---

## The board and how to drive it

| On screen | Mouse | Keyboard (opt-in) |
|---|---|---|
| Button **A** / **B** | Click (held while the mouse is down) | `A` / `B` |
| **A+B** together | Right-click either button | hold `A` and `B` |
| Touch **logo** (gold, above the display) | Click | — |
| Pins **0, 1, 2** (pads along the bottom) | Click | — |
| **Tilt pad** | Drag; the edge is one g, and it springs back to level on release | arrow keys |
| **SHAKE** button | Click | `S` |
| **Light / Temp / Compass / Sound** sliders | Drag; the value stays | — |

The keyboard shortcuts are **off by default** so they never steal your game's
own keys. Switch them on for a board with the object property
`microbit_keyboard` (the instance variable of the same name works too).

Other object properties: `microbit_scale` (size multiplier, default `1.0`, about
220 px wide) and `microbit_show_sensors` (set to `false` to hide the sensor
strip). If the object has a **sprite**, the sprite is used as the board's body
and only the LEDs and controls are drawn on top.

A click on the board never also reaches your own mouse events.

---

## The actions (category **micro:bit**)

| Action | What it does |
|--------|--------------|
| **Show Image** (`microbit_show_image`) | A built-in image name (`HEART`, `HAPPY`, `SAD`, `YES`, `NO`, `ARROW_N`, `SKULL`… 64 in all) or five rows of five brightness digits such as `09090:99999:99999:09990:00900`. |
| **Scroll Text** (`microbit_scroll_text`) | Scroll text across the display (150 ms per column by default). |
| **Show Number** (`microbit_show_number`) | One digit stays still; longer numbers scroll. |
| **Set LED** (`microbit_set_pixel`) | Light one LED now: `x`, `y` 0–4, brightness 0–9. |
| **Clear Display** (`microbit_clear_display`) | Turn every LED off and drop anything queued. |
| **Set Display Brightness** (`microbit_set_brightness`) | Overall brightness, 0–255. |
| **Play Tone** (`microbit_play_tone`) | A beep at a frequency for a number of milliseconds. |
| **Play Melody** (`microbit_play_melody`) | One of the 21 built-in melodies (`DADADADUM`, `ENTERTAINER`, `POWER_UP`…) or your own notes: `"C4:4 E G C5:8 R:4"` (note, octave, `:length`; `R` is a rest). |
| **Stop Sound** (`microbit_stop_sound`) | Silence the speaker and drop queued sounds. |
| **Set Radio Group** (`microbit_radio_set_group`) | Choose the radio group, 0–255. |
| **Send Radio Message** (`microbit_radio_send`) | Send a number or text to the other micro:bits in the group. |
| **Read Sensor** (`microbit_read_sensor`) | Put a reading (accelerometer x/y/z, strength, compass, light, temperature, sound level, pin 0–2 analog) into a variable — or a global variable if the name starts with `global.`. |
| **If Button Pressed** (`microbit_if_button`) | Condition: A, B, A+B or the logo is held down. |
| **If Gesture** (`microbit_if_gesture`) | Condition: the board is in a gesture/posture (`shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`…`8g`). |
| **If Tilt** (`microbit_if_tilt`) | Condition: compare an accelerometer axis (milli-g) with a value. |
| **If LED Brightness** (`microbit_if_pixel`) | Condition: compare one LED's brightness with a value. |

The conditions guard the action or block that follows them, GameMaker-style.
See the [Full Action Reference](Full-Action-Reference-Microbit-Actions) for
every parameter.

> **Text goes in double quotes.** `Scroll Text` and `Send Radio Message`
> read their value like any other expression, so `Score - 3` is arithmetic.
> Write literal text as `"Hello"`. The display only has printable ASCII;
> accented letters appear as `?`, as on the real board.

---

## The events

Fired on the micro:bit's own object:

| Event | Fires when |
|-------|------------|
| **Button A Pressed**, **Button B Pressed**, **Buttons A+B Pressed** | The button(s) go down. |
| **Logo Touched** | The logo is touched. |
| **Pin 0 / 1 / 2 Touched** | That pin is touched. |
| **Shake**, **Logo Up**, **Logo Down**, **Tilt Left**, **Tilt Right**, **Screen Up**, **Screen Down**, **Free Fall**, **2g / 3g / 6g / 8g Impact** | The board detects that gesture (the same algorithm as the real micro:bit). |
| **Loud Sound** / **Quiet Sound** | The microphone level crosses the loud / quiet threshold. |
| **Display Finished** | The display queue has played everything. |
| **Sound Finished** | Every queued tone and melody has played. |
| **Radio Message Received** | Another micro:bit in the same group sent a message. |

"Forever" is the ordinary **Step** event.

### Radio

Every board starts in group 0. **Send Radio Message** delivers to every
*other* micro:bit in the same group (a board never hears itself, and a
different group hears nothing). The receiver gets the event and two
variables: `radio_number` (0 if the text is not a number) and `radio_string`
(always the text). Text is cut to 32 characters, like the real radio.

---

## Time: display and sound queue

On a real micro:bit, scrolling text *blocks* the program. A game cannot
block, so display actions **queue** and play one after another (16 at most;
asking for what is already showing does nothing). **Clear Display** empties
the queue and **Display Finished** tells you when it ran dry, so you can chain
animations. Sounds queue the same way, with **Stop Sound** and **Sound
Finished**.

Sound is a square wave, like the board's buzzer. If the computer has no audio
device it is silently skipped (the simulator still tracks it).

---

## Exports

The **desktop** export (Windows, Linux, macOS) packages the real engine, so the
micro:bit works exactly as in Test Game. The **HTML5** export has the
simulator too: the board and sensor strip are drawn in the browser, you can
click or touch the buttons, logo and pins, drag the tilt pad and sliders, and
the speaker beeps (browsers only allow sound after the first click or key
press). The **Android/Kivy** export has it too: the board and sensor strip are
drawn (in a simplified look, with square corners), you can touch the buttons,
logo, pins, tilt pad, shake button and sliders, the events fire, and the
speaker plays its notes. The keyboard shortcuts work only for a board whose
`microbit_keyboard` property (or variable) is set. A board is recognised by its object name
(it must start with `microbit`) or by `is_microbit` on its room instance.

---

## MicroPython export (onto a real micro:bit)

This is a different kind of export. Instead of a game for another computer, it
turns the program of your micro:bit objects into real **MicroPython** code that
runs on a physical board.

1. Open **File → Export micro:bit (MicroPython) code...** (a project must be
   open).
2. Say which board you have: **V2 (2020 or later)**, **V1 (original,
   2016-2020)** or **Both (one .hex for V1 and V2 boards)**.
3. Pick a folder. Every micro:bit object gets its own program,
   `<folder>/<object name>/main.py`.
4. When exactly one object was exported, the IDE offers two ways to put it on
   the board. **Copy to micro:bit?** copies `main.py` to a board that is
   plugged in over USB and already runs MicroPython (the program then starts by
   itself). **Build a ready-to-flash .hex?** makes a `.hex` file that you drag
   onto the board's **MICROBIT** USB drive — this also works on a brand-new
   board that has never run MicroPython.

All the micro:bit actions and conditions are translated, and so are *Set
Variable*, *Test Variable*, blocks and comments. Each event becomes a check
inside one loop. Game actions that mean nothing on a board (rooms, sprites,
scores…) are not exported. In expressions, `irandom`, `random` and `choose`
work; other GameMaker functions are not translated.

The export dialog lists what could not be exported:

- **Display Finished** and **Sound Finished** (the board's own display and
  sound calls already wait until they are done).
- On a V1 board, what needs a V2: reading the sound level, the touch logo
  (*If Button Pressed* with the logo, **Logo Touched**) and the **Loud Sound**
  / **Quiet Sound** events.
- Anything else that has no MicroPython equivalent.

**Size:** the program must fit in 8,187 bytes on a V1 board and 20,150 bytes on
a V2. **Both** builds one Universal Hex, so it is limited by V1's size and
exports under V1's rules.

> The `.hex` files were checked against the real micro:bit firmware, but not
> yet on a physical board.

---

## Where next

- Open the **`microbit_1`** sample from the Welcome tab and read its guide.
- Try two boards in one room, each with a *Set Radio Group*, and send a
  message from a button.
- Planned: a live link to a real micro:bit over USB. It is not available yet.

See also: [Extensions](Extensions), [Full Action Reference](Full-Action-Reference-Microbit-Actions), [Event Reference](Event-Reference).
