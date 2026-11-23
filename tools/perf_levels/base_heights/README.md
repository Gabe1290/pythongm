# Base heights test level

An original 2.5D test level for the stairs renderer, bigger and taller than
`stairs_speed`: a 32 × 24 grid with **17 floor heights**, from the ground (0 px) to
128 px in steps of 8 px. Not a copy of any existing game's map.

Open this folder with **File → Open Project** and press **Test Game**. Arrow keys move
and turn. You can climb 12 px at a time, so every 8 px step is walkable and you can
drop from any height.

## What is in it

- **Entrance hall** (where you start, ground level), with pedestals at 24, 48, 72 and
  96 px. They are decoration: too tall to climb.
- **Grand staircase**: 10 steps of 8 px up to a **balcony** at 80 px. Turn round at the
  top to look down into the hall.
- **Tower**: a stepped path along the balcony's north edge up to a **lookout at 128 px**,
  the highest level.
- **Zig-zag corridor**: it goes down from the balcony (72 → 32 px) to a courtyard with
  pillars and a raised platform (56 px).
- **Pit room**: a walkway at 32 px around a pool of green sludge (8 px). Steps lead
  back out of the pool.
- Monsters and flags stand at different heights. They do not move and cannot hurt you.

## The yellow line

- **ms/image**: average *work* time per frame over the last 30 frames (update and
  drawing, without the wait that caps the game at 60 frames per second).
- **i/s**: frames per second (at most 60).
- **hauteur**: the floor height under you.

The small map at the top right shows walls and monsters (red).

Measured on the dev box (Linux, headless): 21–30 ms per frame (34–48 frames per
second), the most in the pit room and on the staircase; the `stairs_speed` level costs
about 17 ms.

## Map

`#` wall, `.` ground, `1`–`9` = 8–72 px, `a`–`g` = 80–128 px, `n` = sludge (8 px).
North is up.

```
################################
#....................abcdefgggg#
#....................aaaaaaaggg#
#..33..66............aaaaaaaaaa#
#..33..66..123456789aaaaaaaaaaa#
#..........123456789aaaaaaaaaaa#
#..........123456789aaaaaaaaaaa#
#..........123456789aaaaaaaaaaa#
#..99..cc............aaaaaaaaaa#
#..99..cc............aaaaaaaaaa#
#....................aaaaaaaaaa#
#....................aaaaaaaaaa#
####11####################99####
####22####################88####
####33####################77####
#4444444444###55555555555566####
#4444444444###55555555555566####
#44nn3nnn44###55################
#44nn2nnn44###55555555555555555#
#44nnnnnn44###5555#55#555555555#
#44nnnnnn4444455555555555777775#
#44nnnnnn444445555#555556777775#
#4444444444#####555555555777775#
################################
```

The level is generated from `samples/raycast_5` by `tools/gen_heights_perf_level.py`;
re-run that script after changing the sample rather than editing these files by hand.
Opening the level in the IDE and saving it changes these files: put them back with
`git checkout -- tools/perf_levels/`.
