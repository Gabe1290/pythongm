# Unimplemented Actions

**Summary:** 0 unimplemented / 120 total actions (100% implemented)

This document tracks all actions that are currently marked as unimplemented (grayed out in the IDE).
Check the box when an action has been implemented and tested.

---

## Control (4 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Ask Question | `control` | Show yes/no dialog | [x] |
| Test Chance | `control` | Random probability test | [x] |
| Test Expression | `control` | Evaluate GML expression | [x] |
| Test Instance Count | `control` | Compare number of instances | [x] |

## Move (8 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Move to Contact | `move` | Move until touching an object | [x] |
| Move Towards a Point | `move` | Move towards specific coordinates | [x] |
| Set Direction and Speed | `move` | Set exact direction and speed | [x] |
| Set Friction | `move` | Set movement friction | [x] |
| Set Gravity | `move` | Apply gravity to the instance | [x] |
| Reverse Horizontal Direction | `move` | Reverse horizontal movement | [x] |
| Reverse Vertical Direction | `move` | Reverse vertical movement | [x] |
| Wrap Around Room | `move` | Wrap to opposite side when leaving room | [x] |

## Main1 (3 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Create Moving Instance | `main1` | Create instance with initial motion | [x] |
| Create Random Instance | `main1` | Create one of four random objects | [x] |
| Destroy at Position | `main1` | Destroy instances at coordinates | [x] |

## Main2 (4 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Check Sound | `main2` | Check if sound is playing | [x] |
| Stop Sound | `main2` | Stop playing a sound | [x] |
| Set Color | `main2` | Colorize the sprite | [x] |
| Transform Sprite | `main2` | Scale and rotate sprite | [x] |

## Draw (10 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Set Drawing Color | `draw` | Set color for drawing | [x] |
| Fill Color | `draw` | Fill screen with color | [x] |
| Draw Line | `draw` | Draw a line | [x] |
| Draw Ellipse | `draw` | Draw an ellipse | [x] |
| Draw Arrow | `draw` | Draw an arrow | [x] |
| Draw Scaled Text | `draw` | Draw scaled text | [x] |
| Draw Sprite | `draw` | Draw a sprite at position | [x] |
| Draw Background | `draw` | Draw a background image | [x] |
| Set Font | `draw` | Set text font | [x] |
| Create Effect | `draw` | Create visual effect | [x] |

## Timing (6 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Set Timeline | `timing` | Set instance timeline | [x] |
| Set Timeline Position | `timing` | Set timeline position | [x] |
| Set Timeline Speed | `timing` | Set timeline playback speed | [x] |
| Start Timeline | `timing` | Start timeline playback | [x] |
| Pause Timeline | `timing` | Pause timeline | [x] |
| Stop Timeline | `timing` | Stop and reset timeline | [x] |

## Info (5 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Save Game | `info` | Save game state | [x] |
| Load Game | `info` | Load game state | [x] |
| Show Game Information | `info` | Display game info screen | [x] |
| Show Video | `info` | Play video file | [x] |
| Open Web Page | `info` | Open URL in browser | [x] |

## Rooms (7 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Set Room Caption | `rooms` | Set room caption text | [x] |
| Set Room Speed | `rooms` | Set game speed (FPS) | [x] |
| Set Room Persistent | `rooms` | Make room persistent | [x] |
| Set Background Color | `rooms` | Set room background color | [x] |
| Set Background Image | `rooms` | Set room background image | [x] |
| Enable Views | `rooms` | Enable/disable view system | [x] |
| Set View | `rooms` | Configure a view | [x] |

## Extra (3 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Draw Variable | `extra` | Draw variable value on screen | [x] |
| Test Room | `extra` | Check if in specific room | [x] |
| Go to Different Room | `extra` | Go to specific room | [x] |

## Code (1 action)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Execute Script | `code` | Call a script | [x] |

## Resources (3 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Replace Sprite from File | `resources` | Load sprite from file | [x] |
| Replace Sound from File | `resources` | Load sound from file | [x] |
| Replace Background from File | `resources` | Load background from file | [x] |

## Particles (8 actions) - ✅ ALL IMPLEMENTED

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Create Particle System | `particles` | Create a particle system | [x] |
| Destroy Particle System | `particles` | Remove particle system | [x] |
| Clear All Particles | `particles` | Remove all particles | [x] |
| Create Particle Type | `particles` | Define particle type | [x] |
| Create Particle Emitter | `particles` | Create particle emitter | [x] |
| Destroy Particle Emitter | `particles` | Remove particle emitter | [x] |
| Stream Particles | `particles` | Emit particles continuously | [x] |
| Burst Particles | `particles` | Emit particles once | [x] |

---

## Remaining Unimplemented Actions (0 total)

**All GM80 actions have been implemented!** 🎉

---

## Blockly Config Unimplemented Blocks (0 total)

**All Blockly blocks are now implemented!** 🎉

---

## Priority Recommendations

### High Priority (commonly used) - ✅ ALL IMPLEMENTED
1. ~~**Set Friction** - Essential for platformers and physics~~ ✅
2. ~~**Set Gravity** - Essential for platformers and physics~~ ✅
3. ~~**Wrap Around Room** - Common for arcade games~~ ✅
4. ~~**Reverse Horizontal/Vertical Direction** - Common for bouncing~~ ✅
5. ~~**Set Drawing Color** - Needed for custom drawing~~ ✅
6. ~~**Test Chance** - Common for random events~~ ✅
7. ~~**Stop Sound** - Essential for sound control~~ ✅

### Medium Priority - ✅ MOSTLY IMPLEMENTED
1. ~~Draw actions (Line, Ellipse, Arrow, Sprite)~~ ✅
2. ~~Room settings (Caption, Speed, Background Color)~~ ✅
3. ~~Save/Load Game~~ ✅
4. ~~Move to Contact, Move Towards Point~~ ✅

### Low Priority (advanced features) - ✅ ALL IMPLEMENTED
1. ~~Timelines~~ ✅
2. ~~Particles~~ ✅
3. ~~Views~~ ✅
4. ~~Scripts~~ ✅

---

## Recent Implementation History

### January 2026
- **Extra Tab (3 actions)**: draw_variable, goto_room, check_room
- **Particles Tab (8 actions)**: create_particle_system, destroy_particle_system, clear_particles, create_particle_type, create_emitter, destroy_emitter, burst_particles, stream_particles
- **Timing Tab (6 actions)**: set_timeline, set_timeline_position, set_timeline_speed, start_timeline, pause_timeline, stop_timeline
- **Main1 Tab (3 actions)**: create_random_instance, create_moving_instance, destroy_at_position
- **Main2 Tab (3 actions)**: transform_sprite, set_color, check_sound
- **Draw Tab (4 actions)**: draw_arrow, set_draw_font, fill_color, create_effect

---

## Implementation Notes

To implement an action:
1. Find the action definition in `actions/<category>_actions.py`
2. Remove the `implemented=False` parameter (actions are implemented by default)
3. Add the execution method in `runtime/action_executor.py`
4. Add tests in `tests/test_action_executor.py`
5. Test the action in a sample game
6. Check the box in this document
