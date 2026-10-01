# Beginner Preset

*[Home](Home) | [Preset Guide](Preset-Guide) | [Intermediate Preset](Intermediate-Preset)*

> **Auto-generated** from `config/blockly_config.py`'s `get_beginner()` by `tools/gen_preset_docs.py` — do not edit by hand; re-run the generator after changing the preset.

> **What this actually restricts:** this preset filters BOTH the Blockly visual-block palette *and* the structured Events/Actions panel's "Add Event"/"Add Action" menus — whichever editor you use, only the events/actions listed below appear. Which preset a *project* uses is set two ways: **`Preferences > IDE Edition`** picks the default for *new* projects (Beginner edition -> this preset; existing projects are never changed by switching edition), and **`Tools > Configure Action Blocks...`** changes the preset for the *currently open* project at any time. The IDE's default edition is Beginner, so a fresh install's new projects start on this exact list. This list doesn't cover [extension](Extensions) actions (3D View, Network, …): an extension's actions show in every preset, including this one, once it's active for the project — see [Extensions](Extensions)'s "Which extension actions show in the toolbox" section.

## Overview

This preset enables **19** event types and **54** action types.

---

## Events

| Event | Block Name | Category | Description |
|-------|------------|----------|-------------|
| Create | `create` | Object | Executed when the object is first created |
| Step | `step` | Object | Executed every frame (use for continuous checks) |
| Keyboard (held) | `keyboard` | Input | Executed continuously while a key is held down (for smooth movement) |
| Keyboard <No Key> | `keyboard_no_key` | Input | Executed when no keyboard key is currently pressed |
| Collision With... | `collision` | Collision | Executed when colliding with another object |
| Begin Step | `begin_step` | Step | Executed at the beginning of each step, before other events |
| End Step | `end_step` | Step | Executed at the end of each step, after collisions but before drawing |
| Alarm | `alarm` | Timing | Executed when an alarm clock reaches zero |
| Draw | `draw` | Drawing | Executed when the object is drawn (replaces default sprite drawing) |
| Draw GUI | `draw_gui` | Drawing | Drawn on top of everything (not affected by camera/view). Use for HUD, score, lives. |
| Room End | `room_end` | Room | Executed when the room ends |
| Room Start | `room_start` | Room | Executed when the room starts (after create events) |
| Game End | `game_end` | Game | Executed when the game ends |
| Game Start | `game_start` | Game | Executed when the game starts (in first room only) |
| Animation End | `animation_end` | Other | Fires when the sprite's animation reaches its last frame and wraps |
| Intersect Boundary | `intersect_boundary` | Other | Executed when instance intersects the room boundary |
| No More Health | `no_more_health` | Other | Executed when health becomes 0 or less |
| No More Lives | `no_more_lives` | Other | Executed when lives become 0 or less |
| Outside Room | `outside_room` | Other | Executed when instance is completely outside the room |

---

## Actions

### Movement

| Action | Block Name | Parameters |
|--------|------------|------------|
| Bounce | `bounce` | — |
| Jump To Position | `jump_to_position` | `x`, `y`, `relative` |
| Jump to Start Position | `jump_to_start` | — |
| Move to Contact | `move_to_contact` | `direction`, `max_distance`, `object` |
| Reverse Horizontal | `reverse_horizontal` | — |
| Reverse Vertical | `reverse_vertical` | — |
| Set Direction & Speed | `set_direction_speed` | `direction`, `speed` |
| Set Gravity | `set_gravity` | `direction`, `gravity` |
| Set Horizontal Speed | `set_hspeed` | `speed` |
| Set Vertical Speed | `set_vspeed` | `speed` |
| Start Moving (Direction) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Stop Movement | `stop_movement` | — |

### Grid

| Action | Block Name | Parameters |
|--------|------------|------------|
| Test Grid Alignment | `test_alignment` | `hsnap`, `vsnap` |

### Instance

| Action | Block Name | Parameters |
|--------|------------|------------|
| Change Instance | `change_instance` | `object`, `perform_events` |
| Create Instance | `create_instance` | `object`, `x`, `y`, `relative` |
| Destroy Instance | `destroy_instance` | — |
| Destroy at Position | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Test Instance Count | `test_instance_count` | `object`, `number`, `operation` |

### Score

| Action | Block Name | Parameters |
|--------|------------|------------|
| Draw Lives | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Draw Score | `draw_score` | `x`, `y`, `caption`, `relative` |
| Set Lives | `set_lives` | `value`, `relative` |
| Set Score | `set_score` | `value`, `relative` |
| Show High-Score Table | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |

### Timing

| Action | Block Name | Parameters |
|--------|------------|------------|
| Set Alarm | `set_alarm` | `alarm_number`, `steps` |
| Sleep | `sleep` | `milliseconds` |

### Room

| Action | Block Name | Parameters |
|--------|------------|------------|
| End Game | `game_end` | — |
| If Next Room Exists | `if_next_room_exists` | `then_actions`, `else_actions` |
| If Previous Room Exists | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Restart Room | `restart_room` | — |
| Set Background | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |

### Audio

| Action | Block Name | Parameters |
|--------|------------|------------|
| Check Sound Playing | `check_sound` | `sound`, `not_flag` |
| Play Music | `play_music` | `music`, `loop`, `volume` |
| Play Sound | `play_sound` | `sound`, `volume` |
| Set Volume | `set_volume` | `volume` |
| Stop Music | `stop_music` | — |
| Stop Sound | `stop_sound` | `sound` |

### Game

| Action | Block Name | Parameters |
|--------|------------|------------|
| Draw Text | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Restart Game | `restart_game` | — |
| Set Draw Color | `set_draw_color` | `color` |
| Set Window Caption | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Show Message | `show_message` | `message` |

### Control

| Action | Block Name | Parameters |
|--------|------------|------------|
| Check Empty | `check_empty` | `x`, `y`, `relative`, `objects` |
| Comment | `comment` | `text` |
| Else | `else_action` | — |
| End Block | `end_block` | — |
| Execute Code | `execute_code` | `code` |
| Execute Script | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Exit Event | `exit_event` | — |
| If Collision | `if_collision` | `x`, `y`, `object`, `not_flag` |
| If Object Exists | `if_object_exists` | `object`, `not_flag` |
| Start Block | `start_block` | — |
| Test Chance | `test_chance` | `sides` |
| Test Expression | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Test Variable | `test_variable` | `variable`, `value`, `scope`, `operation` |

---

## See Also

- [Preset Guide](Preset-Guide) — what presets are and how to change one
- [Event Reference](Event-Reference) — full description of every event
- [Full Action Reference](Full-Action-Reference) — full parameter details for every action
- [Intermediate Preset](Intermediate-Preset) — the next tier up
