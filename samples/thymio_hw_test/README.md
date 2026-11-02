# Thymio — Hardware test

Six tiny programs, one per robot in the room, to find out whether what PyGameMaker exports
runs on a **real Thymio**. In PyGameMaker you can try them in the simulator first, then export
them and load them onto the robot one at a time.

The first time this is tried on a real robot is the interesting part: please write down what
happens (a results table is at the end).

## Before you start

1. **Switch the Thymio features on** (they are off by default):
   *Tools → Preferences → Extensions* → tick **Thymio Robot**, and tick the checkbox under it
   (*Show this extension's tab, menus and toolbar button*). Press OK and **restart** the IDE.
2. **Install the Thymio software** (Thymio Suite). You need *Aseba Studio*, which comes with it
   (on Windows: `C:\Program Files\Thymio\bin\asebastudio.exe`).
3. Have a **Thymio II** and a USB cable (or the wireless dongle). Charge it.

## Step 1 — try them in the simulator

Open this sample and press **Test Game**. **Click the drawn arrow buttons** on one robot with the
mouse: its LEDs and wheels react. (The keyboard arrows and space press that button on **all six**
robots at once, which is also fun, but confusing for the motor test.) This tells you whether the
*program logic* is what you meant, before the robot is involved.

Two things the simulator does differently from the robot, on purpose or not:

- It fires a button's event **only when you press**, not when you let go. So in program 2 the
  robot keeps driving after you release the button; click the centre button to stop it. On the real
  Thymio, letting go stops it.
- The proximity and ground sensors read "clear / light" unless you place obstacles in a playground.

## Step 2 — export the Aseba code

*File → Export Aseba (Thymio) code…* and choose a folder. You get **one file per robot**:

| File | What it tests |
|---|---|
| `thymio_hw_1_leds.aesl` | LEDs: top, bottom-left, bottom-right, all off |
| `thymio_hw_2_motors.aesl` | Motors: drives only while a button is held |
| `thymio_hw_3_counter.aesl` | Variables and a condition: count button presses |
| `thymio_hw_4_proximity.aesl` | Proximity sensors: stop in front of an obstacle |
| `thymio_hw_5_ground.aesl` | Ground sensors: stop at a dark line |
| `thymio_hw_6_timer.aesl` | Timer and tone: a beep every second |

(Without the IDE, from the PyGameMaker folder:
`py -3.12 -m extensions.thymio.export.aseba_exporter samples/thymio_hw_test/project.json C:	empesl`
writes the same six files.)

## Step 3 — run one on the robot

1. Plug in the Thymio and switch it on.
2. Open **Aseba Studio**; it finds the robot.
3. *File → Open* the `.aesl` file, press **Load**, then **Run**.
4. Do what the table says. Press the red **Stop** (or switch the robot off) when you are done.
5. Next file: open it, **Load**, **Run**.

Start with `1_leds` — it moves nothing. When a program is loaded and running, the **top LED is dim
blue** (except the timer program) — if you do not see that, the code did not load.

## What you should see

| # | Do this | You should see |
|---|---|---|
| 1 | Press forward / backward | Top LED red / green |
|   | Press left / right | Bottom-left / bottom-right LED blue |
|   | Press centre | All LEDs off |
| 2 | Hold forward, backward, left, right | It drives (slowly), stops when you let go |
|   | Press centre | It stops |
| 3 | Press centre three times | Top LED turns green after the third press |
|   | Press backward | Back to dim blue (count reset) |
| 4 | Press centre | It drives slowly forward |
|   | Put a hand or a book in front | It stops, top LED red; clear again: green |
| 5 | Press centre on a light table | It drives slowly forward, top LED green |
|   | Black tape under the **left** ground sensor | It stops, top LED red |
| 6 | (nothing) | A beep and a blue top LED once a second |
|   | Press centre / forward | Timer stops (silence) / starts again |

**Safety:** programs 2, 4 and 5 move the robot, but only after you press a button, at low speed.
Keep it on the floor or in the middle of a table and watch it.

## What we are not sure about (look at these first)

This is the first run on real hardware, so some things in the exported code are educated guesses:

- **Stopping a sound** (program 6, centre button) uses `call sound.freq(0, -1)`. If the beep does
  not stop, tell us.
- **Counting** (program 3) uses the `count++` form. If Aseba Studio reports a syntax error there,
  that is a finding.
- **Thresholds**: 2000 for the front proximity sensor and 300 for the ground sensor are the
  defaults. Your table, lighting and tape decide whether they are right.
- **Speeds** 80 and 100 are in the Thymio's own units (the maximum is about 500).
- A button event fires on **press and on release**, which is why the programs check
  `button.xxx == 1` before acting.
- The simulator and the robot will not behave identically; the interesting question is *how*
  they differ.

## Results

Copy this table and fill it in:

| # | Loaded without an error? | Did what the table says? | What was different |
|---|---|---|---|
| 1 LEDs | | | |
| 2 Motors | | | |
| 3 Counter | | | |
| 4 Proximity | | | |
| 5 Ground | | | |
| 6 Timer + tone | | | |

Send it back (an error message from Aseba Studio, copied as text, is the most useful thing), and
whatever differs gets fixed.

*Note:* the sample's six robots and its labels live in one room only so you can see all six
programs at once in the simulator. On the robot you always load **one** `.aesl` file at a time.
