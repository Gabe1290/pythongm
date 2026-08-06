# Beginner Preset

*[Home](Home) | [Preset Guide](Preset-Guide) | [Intermediate Preset](Intermediate-Preset)*

> **Auto-generated** from `config/blockly_config.py`'s `get_beginner()` by `tools/gen_preset_docs.py` — do not edit by hand; re-run the generator after changing the preset.

> **What this actually restricts:** this preset filters BOTH the Blockly visual-block palette *and* the structured Events/Actions panel's "Add Event"/"Add Action" menus — whichever editor you use, only the events/actions listed below appear. Which preset a *project* uses is set two ways: **`Preferences > IDE Edition`** picks the default for *new* projects (Beginner edition -> this preset; existing projects are never changed by switching edition), and **`Tools > Configure Action Blocks...`** changes the preset for the *currently open* project at any time. The IDE's default edition is Beginner, so a fresh install's new projects start on this exact list.

## Overview

This preset enables **19** event types and **83** action types.

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
| Jump to Random Position | `jump_to_random` | `snap_h`, `snap_v` |
| Jump to Start Position | `jump_to_start` | — |
| Move Towards Point | `move_towards_point` | `x`, `y`, `speed` |
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
| Create Moving Instance | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Create Random Instance | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Destroy Instance | `destroy_instance` | — |
| Destroy at Position | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Set Image Index | `set_image_index` | `frame` |
| Set Image Speed | `set_image_speed` | `speed` |
| Start Animation | `start_animation` | — |
| Stop Animation | `stop_animation` | — |
| Test Instance Count | `test_instance_count` | `object`, `number`, `operation` |

### Score

| Action | Block Name | Parameters |
|--------|------------|------------|
| Clear High-Score Table | `clear_highscore` | — |
| Draw Lives | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Draw Score | `draw_score` | `x`, `y`, `caption`, `relative` |
| Set Lives | `set_lives` | `value`, `relative` |
| Set Score | `set_score` | `value`, `relative` |
| Show High-Score Table | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Test Health | `test_health` | `operation`, `value` |
| Test Lives | `test_lives` | `value`, `operation` |
| Test Score | `test_score` | `value`, `operation` |

### Timing

| Action | Block Name | Parameters |
|--------|------------|------------|
| Set Alarm | `set_alarm` | `alarm_number`, `steps` |
| Sleep | `sleep` | `milliseconds` |

### Room

| Action | Block Name | Parameters |
|--------|------------|------------|
| Check Room | `check_room` | `room`, `not_flag` |
| End Game | `game_end` | — |
| If Next Room Exists | `if_next_room_exists` | `then_actions`, `else_actions` |
| If Previous Room Exists | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Restart Room | `restart_room` | — |
| Set Room Caption | `set_room_caption` | `caption` |

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
| Draw Arrow | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Draw Background | `draw_background` | `background`, `x`, `y`, `tiled` |
| Draw Ellipse | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Draw Line | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Draw Scaled Text | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Draw Sprite | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Draw Text | `draw_text` | `text`, `x`, `y`, `relative` |
| Draw Variable | `draw_variable` | `x`, `y`, `variable` |
| Fill Screen Color | `fill_color` | `color` |
| Open Webpage | `open_webpage` | `url` |
| Restart Game | `restart_game` | — |
| Set Color | `set_color` | `color`, `alpha` |
| Set Draw Color | `set_draw_color` | `color` |
| Set Draw Font | `set_draw_font` | `font`, `halign`, `valign` |
| Set Window Caption | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Show Game Info | `show_info` | — |
| Show Message | `show_message` | `message` |

### Control

| Action | Block Name | Parameters |
|--------|------------|------------|
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
| Test Question | `test_question` | `question` |
| Test Variable | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Views

| Action | Block Name | Parameters |
|--------|------------|------------|
| Enable Views | `enable_views` | `enable` |
| Set View | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### 3D View

| Action | Block Name | Parameters |
|--------|------------|------------|
| Draw DOOM HUD | `draw_doom_hud` | `x`, `y`, `width`, `height`, `back_color`, `divider_color`, `text_color`, `health_label`, `health_bar_width`, `health_bar_height`, `bar_color`, `face_sprite`, `face_frames`, `score_label`, `lives_sprite`, `lives_scale`, `objective_value`, `objective_label` |
| Draw Minimap | `draw_minimap` | `x`, `y`, `size`, `back_color`, `wall_color`, `player_color` |
| Enable Raycast View | `enable_raycast_view` | `enable`, `camera_object`, `fov`, `render_distance`, `cell_size`, `columns`, `wall_color`, `floor_color`, `ceiling_color`, `wall_texture`, `sky_texture`, `floor_texture`, `ceiling_texture`, `wall_textured`, `floor_cast_res`, `viewport_height` |
| Set Facing Angle | `set_facing_angle` | `angle`, `relative` |

---

## See Also

- [Preset Guide](Preset-Guide) — what presets are and how to change one
- [Event Reference](Event-Reference) — full description of every event
- [Full Action Reference](Full-Action-Reference) — full parameter details for every action
- [Intermediate Preset](Intermediate-Preset) — the next tier up
