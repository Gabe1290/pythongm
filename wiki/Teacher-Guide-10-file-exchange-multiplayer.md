# PyGameMaker — Tutorial 10: Turn-Based Multiplayer by File Exchange — Teacher Guide

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Teacher-Guide-10-file-exchange-multiplayer.pdf) · [ODT](downloads/Teacher-Guide-10-file-exchange-multiplayer.odt) · [Reference projects (ZIP)](downloads/solutions/10_file_exchange_multiplayer_checkpoints.zip)

---

Companion for the in-app tutorial (**Help > Tutorials > Turn-Based Multiplayer: Tic-Tac-Toe by File Exchange**, 5 pages) and the matching student handout and worksheet. Students should have finished Tutorial 4 or 6 and be comfortable with variables, conditions and the Draw event. This is the most demanding tutorial in the series and the only one that needs two computers.

## Overview

Students build Tic-Tac-Toe for two computers in four phases: the board (single player), host and join, taking real turns, and winning and playing again. New ideas: **turn-based multiplayer through a shared folder** (no live connection, so it works through school firewalls), **global variables set by the network** (`global.player_id`, `global.round_number`, `global.waiting_for_players`), **shared variables**, **End Turn**, and the **Round Resolved** event.

> **Info:** The historical note in the tutorial (play-by-mail, VGA Planets) makes a good opening: the game exchanges files exactly as players once exchanged letters.

## Suggested Timing (75-90 minutes, best over two sessions)

The tutorial says 25-30 minutes for a confident student; the nine repeated cell checks, the eight win lines and the lab setup take much longer.

| Segment | Time | What happens |
|---|---|---|
| Introduction and pairs | 10 min | Explain the idea; form pairs; prepare the shared folder |
| Phase 1: the board | 20 min | Pages 1-2; the nine repeated checks are tedious but identical in shape |
| Phase 2: host and join | 15 min | Page 3; first real test between two computers |
| Phase 3: taking turns | 20 min | Page 4 |
| Phase 4: winning | 15 min | Page 5; eight win lines |
| Worksheet / exit ticket | 5-10 min | Worksheet parts A-C |


Phase 1 needs no second computer. A good split: session 1 = Phase 1 (and Phase 2 if time), session 2 = the rest with the lab set up.

## Lab Setup (do this before the lesson)

- **The shared folder is the whole trick.** Both computers of a pair must read and write the *same* folder. Options: a mapped network drive or UNC path on the school server (best: `\\server\share\tictactoe` or a drive letter), or a synced folder (Dropbox, OneDrive). Give each pair its **own subfolder** (for example `tictactoe_pair3`) so pairs do not interfere.
- Both computers must type the **exact same folder path** in the Host and Join actions. A drive letter that means something different on each computer is a common trap; a UNC path is safest.
- The game checks the folder about **once per second**, so a move takes roughly a second (sometimes two) to appear on the other screen. With a synced cloud folder, sync delays add to that.
- **Solo testing on one computer:** use a plain folder name (`tictactoe_files`) and run two Test Game windows, one pressing H and one pressing J. The bundled `fichier_1` sample works the same way and is a finished version students can compare with.
- The game never freezes if the folder cannot be reached: it keeps running single-player (and "Waiting for opponent..." simply stays).
- The host waits for the other player's move only up to the **round deadline** (30 seconds by default); after that a missing player is skipped for that round.

## Step-by-Step Walkthrough and Common Issues

**Phase 1: the board**

- Everything lives on one object, `obj_game`. The nine cells are nine plain variables (`cell_column_row`), each with a fixed name, because there is no way to build a variable name from other values in this engine.
- The nine click checks and the nine draw checks are identical in shape; the tutorial's tables give the rectangles. Students often make typos in the numbers. Consider pairing students or giving the tables on paper.
- **Set draw color white first.** The tutorial draws black by default and a new room is black, so without *Set draw color* the whole board is invisible (the reference project shows nothing at all until the colour is set). The tutorial now includes that block.

**Phase 2: host and join**

- H hosts and becomes X; J joins and becomes O. Both computers run the same project. If both press H, both say "You are X" and nothing works.
- `global.waiting_for_players` stays 1 until the host has as many players as the Max players setting (2). No counting is needed.

**Phase 3: taking real turns**

- Round 1 is X's; odd rounds are X's, even rounds O's. The player who is *not* on turn must still submit something, so the game does not wait for the deadline: the Step event sends an empty **End Turn** once per round (the `last_round_acted` variable stops it from firing every frame).
- The click handler writes the mark with **Set a Shared Variable** using the cell's *literal name*, then **End Turn**. The mark appears on both screens only when the round resolves, about a second later; students think "it did not work" and click again.
- Marks are drawn from `global.cell_*`. A shared variable nobody has set reads as the number **0**, not empty text, so the drawing checks compare with 0.
- In the reference project, a click made out of turn is ignored, and the two computers always show the same board.

**Phase 4: winning and playing again**

- The **Round Resolved** event runs on both computers after each confirmed round, so both compute the winner themselves.
- Eight lines, eight **If** blocks: rows, columns, both diagonals. Wrong cell names in one line means that line never wins.
- **What the finished game does not do:** it does not stop play after a win (the other player can still place marks; the winner message stays), and it does not announce a draw when the board is full. Both are good extension tasks.
- **Space** runs **Leave the Game**, which ends this computer's session cleanly. For a clean rematch, students press H and J again; resetting the cells and `winner` is the tutorial's "try this next".

> **Tip:** **Reference projects.** Download the checkpoint projects from the wiki (`10_file_exchange_multiplayer_checkpoints.zip`): one project for the end of each phase, built exactly as the tutorial describes. Phase 2-4 projects use a plain folder name (`tictactoe_files`); change it to your shared folder in the Host and Join actions before using them on two computers.

## Vocabulary Introduced

| Term | What it means here |
|---|---|
| Host / join | The two roles: the host runs rounds; the other players join |
| Shared folder | The place where moves are exchanged as small files |
| Round | One turn, resolved by the host |
| Shared variable | A value written by one player and readable by all as `global.name` |
| Pass | Ending your turn without a move |


## Discussion Questions

- Why does this game use files instead of a live connection? (No firewall or port problems; works asynchronously.)
- What are the drawbacks? (Slower, needs a shared folder.)
- Why must both computers run the same project?
- How could two players play at different times of day with this system?

## Differentiation

- **Support:** give the Phase 1 checkpoint; pair a stronger and a weaker student; provide the cell tables on paper.
- **Extension:** rematch reset; draw detection; stop play after a win; a score across games; a title screen instead of the H/J keys.

## Worksheet Answer Key

**Part A:** 1-C, 2-B, 3-D, 4-A.

**Part B:** 1. Host a Game (File Exchange). 2. Set a Shared Variable (File Exchange). 3. End Turn (File Exchange). 4. Leave the Game (File Exchange). 5. The Round Resolved event.

**Part C:**

1. Advantage: it works through firewalls and needs no live connection (players can even play at different times). Disadvantage: a move takes about a second or more to appear, and both computers need a shared folder.
2. Round 5 is odd, so it is X's turn. The game tests whether `global.round_number` is odd (X) or even (O) and compares it with `my_mark`.
3. The mark only appears after the round has been confirmed by the host and published, which takes about a second (longer over a slow shared drive).

**Parts D and E:** completion and reflection.

## Rubric: File-Exchange Tic-Tac-Toe

| Level | What the game shows |
|---|---|
| 4 - Complete | Board and marks work; host and join connect two computers; only the player on turn can move and both screens agree; a win is shown on both; the players can leave and start again |
| 3 - Working | Two computers connect and take turns; the win check or the rematch is missing |
| 2 - Partly there | The board works and the computers connect, but moves do not reach the other computer |
| 1 - Started | Phase 1 board works on one computer only |


## End-of-Session Checklist

- [ ] Every student has a saved project (`Ctrl+S`)
- [ ] Every pair has connected at least once (H and J)
- [ ] Shared subfolders are cleaned up or can be reused next time
- [ ] Note who needs the checkpoint project next time
