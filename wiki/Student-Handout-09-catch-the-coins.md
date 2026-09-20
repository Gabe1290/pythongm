# PyGameMaker — Tutorial 9: Catch the Coins

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Student-Handout-09-catch-the-coins.pdf) · [ODT](downloads/Student-Handout-09-catch-the-coins.odt)

---

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Catch the Coins: Win and Lose** (5 pages, about 15-20 minutes). Keep the tutorial open on one half of your screen. Tick each box when the step is done, and check the **You should see** line at the end of every phase. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

A complete game with a way to win and a way to lose: coins fall from the sky and you slide left and right to catch them. Catch every coin and you win. Touch the enemy and it is Game Over. From either ending, SPACE starts again.

## Phase 1: A Moving Player

- [ ] **1.** Make a new project `CatchTheCoins` and choose the template **With Game Over Screen**. It gives you a ready-made Game Over room.
- [ ] **2.** Create a sprite `spr_player` (32×32) and an object `obj_player` with that sprite.
- [ ] **3.** Create a room `room_main` and place `obj_player` near the bottom centre.
- [ ] **4.** In `obj_player`: **Keyboard: Left Arrow (held)** with *Set horizontal speed to -5*; **Right Arrow (held)** with *5*; **Keyboard: No key** with *Stop movement*.

> **Done:** **You should see:** press **F5**. Left and Right move the player, and it stops when you let go. It can drift off the screen for now.

## Phase 2: Coins and an Enemy

- [ ] **5.** Create sprites `spr_coin` (24×24, yellow circle) and `spr_enemy` (32×32, red square).
- [ ] **6.** Create `obj_coin` and `obj_enemy`, each with its sprite. Each gets a **Create** event: *Set vertical speed to 3*.
- [ ] **7.** Give **both** objects an **Outside Room** event with *Set variable* `y` to 0, so anything that falls off the bottom comes back at the top.
- [ ] **8.** In `room_main`, place 5 to 8 coins across the top and one enemy between them.

> **Done:** **You should see:** press **F5**. Coins and the enemy fall. Touching them does nothing yet. Anything you miss comes back at the top.

## Phase 3: Catching and Crashing

- [ ] **9.** In `obj_player`, **Create** event: *Set score to 0*.
- [ ] **10.** Add **Collision with obj_coin**: *Add to score 1*, then *Destroy other instance* (the coin, not the player!).
- [ ] **11.** Add **Collision with obj_enemy**: *Go to room* `room_gameover`.
- [ ] **12.** Add a **Draw** event: *Draw score at x 10, y 10*.

> **Done:** **You should see:** press **F5**. Catching a coin adds 1 and the coin disappears. Touching the enemy shows the Game Over screen, and SPACE starts again.

## Phase 4: Winning the Game

- [ ] **13.** Create `obj_win_text`. **Draw** event: *Draw text* "YOU WIN!" at x 412, y 320 and "Press SPACE to play again" at x 340, y 400. **Key press: space**: *Restart game*.
- [ ] **14.** Create `room_win` with a bright background colour, and place one `obj_win_text` in it.
- [ ] **15.** In `obj_player`, add a **Step** event: *If count of* `obj_coin` *equals 0* then *Go to room* `room_win`.

> **Done:** **You should see:** press **F5**. Catch every coin and the YOU WIN! room appears. Touch the enemy and you get Game Over. SPACE starts a new game from either.

## Stuck?

| What is wrong | Most likely cause | What to do |
|---|---|---|
| The game says YOU WIN! at once | There are no coins in `room_main` (the count is already 0) | Place at least one coin in the room |
| I catch every coin but nothing happens | The Step event or the room name is wrong | Check *If count of obj_coin equals 0* and the room name `room_win` |
| A missed coin makes the game impossible to win | The coin or enemy has no **Outside Room** event | Add *Set variable* `y` to 0 on both |
| My player disappears when it catches a coin | I used *Destroy this instance* | Use **Destroy other instance** |
| Touching the enemy does nothing | No **Collision with obj_enemy**, or the room name is misspelled | Add it; use exactly the game-over room's name |
| The Game Over screen is missing | The project was not made with the "With Game Over Screen" template | Create a new project from the template |
| The score does not show | No **Draw** event on the player | Add *Draw score* to a Draw event |
| SPACE does nothing on the end screen | The end room has no object with a **Key press: space** event | Add the event and place the object in the room |


## Challenges

- **Try this (5 minutes):** change the falling speed, or the number of coins.
- **Push further:** add a second enemy, or make the coins and the enemy fall at different speeds.
- **Invent:** add lives, a timer, or a coin that is worth more than one point.

## Vocabulary

| Term | What it means |
|---|---|
| Win state | What happens when the player wins |
| Lose state | What happens when the player loses |
| Room transition | Going from one room to another (here, to the Game Over or win room) |
| Instance count | How many copies of an object exist right now |
| Template | A ready-made starting project |


## Check Yourself

Write your answers in the notes below.

1. How does the game know that every coin has been caught?
2. Why do missed coins need an **Outside Room** event?
3. What is the difference between the "win" room and the "Game Over" room?

## My Notes

<br>

<br>

<br>

<br>

<br>

<br>

