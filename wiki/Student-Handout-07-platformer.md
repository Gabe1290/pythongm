# PyGameMaker — Tutorial 7: Platformer

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Student-Handout-07-platformer.pdf) · [ODT](downloads/Student-Handout-07-platformer.odt)

---

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Platformer: Run, Jump, Collect** (4 pages, about 25-30 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A platform game: your character falls with gravity, runs and jumps between platforms, collects coins, avoids spikes (each hit costs a life) and reaches a flag to win.

## Phase 1: A Jumping Player

- [ ] **1.** Create two sprites (32×32): `spr_player` and `spr_ground`.
- [ ] **2.** Create `obj_ground` (sprite `spr_ground`, **Solid**) and `obj_player` (sprite `spr_player`).
- [ ] **3.** In `obj_player`, **Create** event: *Set gravity* direction **270**, strength **0.5**.
- [ ] **4.** Add **Keyboard: Left Arrow (held)** with *Set horizontal speed to -4* and **Right Arrow (held)** with *4*.
- [ ] **5.** Add **Keyboard: No key** with *Set horizontal speed to 0*. Do **not** use *Stop movement* here: it would also cancel gravity.
- [ ] **6.** Add **Key press: Up Arrow** with *Set vertical speed to -10*.
- [ ] **7.** Add **Collision with obj_ground** with *Stop movement*.
- [ ] **8.** Create `room_level1` (800×480, light blue background, Snap to Grid 32×32). Place ground along the bottom, platforms in the air, and the player standing on the ground on the left. **Keep the space above the player free** so it can jump.

> **Done:** **You should see:** press **F5**. The player falls onto the ground, runs left and right, and the up arrow makes it jump about three tiles high. It lands on platforms.

## Phase 2: Coins and Hazards

- [ ] **9.** Create sprites `spr_coin`, `spr_spike` and `spr_flag` and objects `obj_coin`, `obj_spike` and `obj_flag` (no events on them).
- [ ] **10.** In `obj_player` add **Collision with obj_coin**: *Add to score 10*, then *Destroy other instance*.
- [ ] **11.** Add **Collision with obj_spike**: *Restart room*.
- [ ] **12.** Add **Collision with obj_flag**: *Show message* "You Win!".
- [ ] **13.** In the room, put coins on platforms, spikes near pits, and the flag at the right end.

> **Done:** **You should see:** press **F5**. Coins vanish and are worth 10. A spike restarts the level. The flag shows "You Win!".

## Phase 3: Game Controller

- [ ] **14.** Create `obj_game_controller` (no sprite).
- [ ] **15.** **Game Start** event (from *Other Events*): *Set score to 0* and *Set lives to 3*.
- [ ] **16.** **Draw** event: *Draw score at x 10, y 10* and *Draw lives at x 200, y 10*.
- [ ] **17.** In `obj_player`'s spike collision, add *Add to lives -1* **before** *Restart room*.
- [ ] **18.** Place `obj_game_controller` anywhere in the room.

> **Done:** **You should see:** press **F5**. Score and lives are shown. Each spike costs one life and restarts the room, and the lives stay lower.

> **Tip:** **Game Start, not Create.** A Create event runs again every time the room restarts. If the lives were set to 3 in Create, every spike would give them back and you would never run out.

## Stuck?

| What is wrong | Most likely cause | What to do |
|---|---|---|
| The player falls through the ground | `obj_ground` is not Solid, or the player has no **Collision with obj_ground** | Tick **Solid**; add the event with *Stop movement* |
| The player does not fall at all | The **Set gravity** action is missing from **Create**, or **No key** uses *Stop movement* | Add gravity; change **No key** to *Set horizontal speed to 0* |
| The player will not jump | The Up event is *held* instead of *Key press*, or something solid is right above the player | Use **Key press: Up Arrow**; keep the space above free |
| The player jumps again and again while holding Up | It is a Keyboard (held) event | Use **Key press** so each press is one jump |
| Coins do nothing | The coin event is on the coin instead of the player, or missing | Put **Collision with obj_coin** on `obj_player` |
| Spikes never cost lives | The lives are set in **Create** instead of **Game Start**, or *Add to lives -1* is missing | Move the actions to **Game Start**; add the action before *Restart room* |
| The score and lives do not show | `obj_game_controller` is not in the room | Place it in the room |
| The flag does nothing | No **Collision with obj_flag** on the player | Add it |


## Challenges

- **Try this (5 minutes):** change the gravity (0.5) or the jump speed (-10) and see how the jump feels.
- **Push further:** add a moving platform or a patrolling enemy; make the flag go to the next room.
- **Invent:** add a double jump, or a Game Over message when the lives reach 0.

## Vocabulary

| Term | What it means |
|---|---|
| Gravity | A force that pulls an object down (direction 270) every step |
| Vertical speed | How fast something moves up (negative) or down (positive) |
| Key press | An event that happens once when a key goes down |
| Hazard | Something that hurts the player, like a spike |
| Game Start | An event that runs once, when the whole game begins |


## Check Yourself

Write your answers in the notes below.

1. Why do we use *Set horizontal speed to 0* and not *Stop movement* for **No key**?
2. Why is the jump speed negative?
3. Why are the score and lives set in **Game Start** and not in **Create**?

## My Notes

<br>

<br>

<br>

<br>

<br>

<br>

