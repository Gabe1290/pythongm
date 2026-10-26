# micro:bit — Dice and Moods (microbit_1)

A simulated **BBC micro:bit** in your game window — no hardware needed. Click
its buttons, shake it, and watch the 5×5 LED display react to the events you
program.

## Run it

Open the project and press **Test Game** (or run
`python runtime/run_game.py samples/microbit_1/project.json`).

| Do this | What happens |
|---|---|
| Click **A** | a happy face |
| Click **B** | a sad face |
| Press the **SHAKE** button (or the **S** key) | the board "rolls a die": a face with 1–6 pips |
| Touch the gold **logo** | it scrolls the word *Rolls*, then how many times you have shaken it |

Everything else on the board works too, even though this game doesn't use it:
**right-click** A or B to press **A+B** together, touch the pads marked 0, 1
and 2, drag the **tilt pad** to tilt the board, and drag the sliders to change
the light level, temperature, compass heading and sound level. The keys **A**,
**B**, **S** and the arrow keys do the same things from the keyboard — this
object opts in with `microbit_keyboard`.

## How it works

| Object | Role |
|---|---|
| `microbit_1` | The board. Any object whose name **starts with `microbit`** becomes a micro:bit: the engine draws the board over it and runs its simulator. Its events are the buttons, shake and logo; its actions draw on the LED display. |
| `obj_help` | Draws the three lines of instructions under the board. |

The events on `microbit_1`:

- **Create** — `rolls = 0`, and show a `HEART`.
- **Button A pressed** — *Show Image* `HAPPY`.
- **Button B pressed** — *Show Image* `SAD`.
- **Gesture: Shake** — picks `roll = irandom(5) + 1`, then six *Test Variable*
  / *Show Image* pairs show the face that matches it (each pair is "if `roll`
  is *k*, show the dice-*k* picture"), and adds 1 to `rolls`.
- **Logo touched** — *Scroll Text* `"Rolls"`, then *Show Number* `rolls`.
  Display actions **queue**: the number waits until the word has finished
  scrolling, just like on the real board.

A dice face is a custom image: five rows of five brightness digits, `0`
(off) to `9` (full), separated by colons — for example the middle pip is
`00000:00000:00900:00000:00000`.

## Things to try

- Change the two moods to `HEART`, `SKULL`, `YES` or `NO` — there are 64
  built-in images (see the *Show Image* tooltip), or draw your own.
- Add **Play Melody** `POWER_UP` to the shake event, or **Play Tone** with
  your own frequency. Add **Stop Sound** on button B.
- Use **If Tilt** (axis x, `>` 300) in a Step event to show an arrow when you
  tilt the board right.
- Copy the object as `microbit_2`, give both a **Set Radio Group**, and make
  button A **Send Radio Message** `1`: the other board gets a *Radio Message
  Received* event, with the value in `radio_number`.

## Good to know

- The events must be on the **board's own object** (`microbit_1`): each
  micro:bit action works on the micro:bit that runs it.
- Text you want to display literally goes **in double quotes**
  (`"Rolls"`), as everywhere in PyGameMaker; without them a dash or a plus
  would be read as arithmetic.
- This project lists the extension under **Project Settings → Extensions**,
  which is what makes the micro:bit blocks and actions appear in its editors.
  A project that does not activate it never shows them.
- The display shows only printable ASCII; accented letters appear as `?`, as
  on the real board.
- The simulator is for **Test Game and desktop exports**. HTML5 and Android
  exports run but do not draw the board yet.
