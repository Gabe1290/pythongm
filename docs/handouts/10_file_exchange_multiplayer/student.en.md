# PyGameMaker — Tutorial 10: Turn-Based Multiplayer by File Exchange

## How to Use This Handout

This handout goes with the in-app tutorial **Help > Tutorials > Turn-Based Multiplayer: Tic-Tac-Toe by File Exchange** (5 pages, about 25-30 minutes). Keep the tutorial open on one half of your screen; it has the full details of every step. Tick each box when the step is done, and check the **You should see** line at the end of every phase. From Phase 2 you need a partner and a **shared folder** that both computers can use. If something does not match, look at **Stuck?** before you call your teacher.

## What You Will Make

Tic-Tac-Toe for two players on two computers, with no live connection: each move is written as a small file in a shared folder, and the other computer reads it. One computer **hosts** (press H) and plays X; the other **joins** (press J) and plays O.

## Phase 1: The Board

- [ ] **1.** Create a project `TicTacToeFiles` with the **Empty Project** template. Create `obj_game` (no sprite) and a room `room_board`, and place one `obj_game` in it.
- [ ] **2.** In `obj_game`, **Create** event: set nine variables to an empty text: `cell_0_0`, `cell_1_0`, `cell_2_0`, `cell_0_1`, `cell_1_1`, `cell_2_1`, `cell_0_2`, `cell_1_2`, `cell_2_2` (column first, then row).
- [ ] **3.** **Draw** event: first *Set draw color* white. Then four *Draw line* actions for the grid: x 270 and 370 from y 90 to 390, and y 190 and 290 from x 170 to 470.
- [ ] **4.** **Mouse: Left Button Pressed**: nine **If** checks, one per cell, like `cell_0_0 == "" and mouse_x >= 170 and mouse_x < 270 and mouse_y >= 90 and mouse_y < 190` then *Set variable* `cell_0_0` to X.
- [ ] **5.** In the **Draw** event: for each cell, *If* the variable is not empty, *Draw text* it in the cell (add 100 to x per column and to y per row).

> DONE: **You should see:** press **F5**. A white grid appears. Clicking a cell puts an X in it; clicking it again does nothing.

## Phase 2: Host a Game / Join a Game

- [ ] **6.** Pick a folder both computers can use (a network drive, or a synced folder). For solo testing, a plain folder name like `tictactoe_files` is fine.
- [ ] **7.** **Key press H**: *Host a Game (File Exchange)* with that folder, max players 2, name "Player 1"; then set `my_mark` to X. **Key press J**: *Join a Game (File Exchange)* with the same folder and name "Player 2"; then set `my_mark` to O.
- [ ] **8.** In the **Draw** event, before the grid: *If* `global.waiting_for_players == 1` then draw "Waiting for opponent..." and *Exit event*; otherwise draw "You are " + `my_mark`.

> DONE: **You should see:** run the game on both computers. Press H on one and J on the other. "Waiting for opponent..." disappears and each screen says "You are X" or "You are O".

## Phase 3: Taking Real Turns

- [ ] **9.** **Create**: set `last_round_acted` and `my_turn` to 0.
- [ ] **10.** **Step**: if it is my turn (`global.round_number` odd and I am X, or even and I am O) set `my_turn` to 1, otherwise 0. Then: if `my_turn == 0` and `last_round_acted != global.round_number`, *End Turn (File Exchange)* and set `last_round_acted` to `global.round_number` (a "pass").
- [ ] **11.** Rewrite the nine click checks: add `my_turn == 1`, and instead of setting the variable, *Set a Shared Variable (File Exchange)* with the cell's own name and the value `my_mark`, then *End Turn (File Exchange)*.
- [ ] **12.** In the **Draw** event, draw each cell from `global.cell_0_0` etc. (draw it only if it is not 0; an unset shared variable reads as 0).

> DONE: **You should see:** only the player whose turn it is can place a mark. A mark shows on **both** screens a moment after the click, and turns alternate X, O, X.

## Phase 4: Winning and Playing Again

- [ ] **13.** In `obj_game` add the **Round Resolved** event with eight **If** checks, one per line (three rows, three columns, two diagonals): if the three `global.cell_*` are equal and not 0, set `winner` to that mark.
- [ ] **14.** **Create**: set `winner` to an empty text. **Draw** (last): if `winner != ""`, draw `winner + " wins! Press SPACE to play again."`.
- [ ] **15.** **Key press Space**: if `winner != ""`, *Leave the Game (File Exchange)*. Press H and J again for a new game.

> DONE: **You should see:** get three in a row and both screens show who won.

## Stuck?

| What is wrong | Most likely cause | What to do |
| The screen is empty | The drawing is black on the black room | Add *Set draw color* white at the top of the **Draw** event |
| It says "Waiting for opponent..." forever | The two computers use different folders, or a computer cannot reach the folder | Use exactly the same folder path; test that both can create a file there |
| Both computers say "You are X" | Both pressed H | One presses H, the other J |
| A click does nothing | It is not your turn, the cell is already used, or `my_turn` is not set | Wait for your turn; check the **Step** event |
| My mark shows only after a moment | That is normal: it appears after the round resolves (about a second) | Wait about a second |
| One player's mark never appears | They forgot *End Turn* after the click | Add *End Turn (File Exchange)* to the click handler |
| Nobody wins even with three in a row | The **Round Resolved** checks are missing a line or use the wrong names | Check all eight lines and the cell names |
| The names of the cells do not match | A typo, for example `cell_1_0` vs `cell_0_1` | Cell names are column first, then row |

## Challenges

- **Try this (5 minutes):** change the player names, or the folder.
- **Push further:** reset the nine cells and `winner` when leaving the game, for a rematch without restarting.
- **Invent:** show a message when the board is full with no winner, or keep a score across several games with another shared variable.

## Vocabulary

| Term | What it means |
| Host | The computer that runs the game and decides each round |
| Shared folder | A folder both computers can read and write |
| Shared variable | A value that every player can read as `global.name` |
| Round | One turn of the game, resolved by the host |
| Turn-based | Players act one after another, not at the same time |

## Check Yourself

Write your answers in the notes below.

1. How does a move get from one computer to the other?
2. Why must the player who is not on turn still "pass" with *End Turn*?
3. Why is the mark drawn from `global.cell_0_0` and not from the local variable?

## My Notes

[[notes:10]]
