# Unimplemented Actions

**Summary:** 54 unimplemented / 120 total actions (55% implemented)

This document tracks all actions that are currently marked as unimplemented (grayed out in the IDE).
Check the box when an action has been implemented and tested.

---

## Control (4 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Ask Question | `control` | Show yes/no dialog | [ ] |
| Test Chance | `control` | Random probability test | [x] |
| Test Expression | `control` | Evaluate GML expression | [ ] |
| Test Instance Count | `control` | Compare number of instances | [ ] |

## Move (8 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Move to Contact | `move` | Move until touching an object | [ ] |
| Move Towards a Point | `move` | Move towards specific coordinates | [ ] |
| Set Direction and Speed | `move` | Set exact direction and speed | [ ] |
| Set Friction | `move` | Set movement friction | [x] |
| Set Gravity | `move` | Apply gravity to the instance | [x] |
| Reverse Horizontal Direction | `move` | Reverse horizontal movement | [x] |
| Reverse Vertical Direction | `move` | Reverse vertical movement | [x] |
| Wrap Around Room | `move` | Wrap to opposite side when leaving room | [x] |

## Main1 (3 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Create Moving Instance | `main1` | Create instance with initial motion | [ ] |
| Create Random Instance | `main1` | Create one of four random objects | [ ] |
| Destroy at Position | `main1` | Destroy instances at coordinates | [ ] |

## Main2 (4 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Check Sound | `main2` | Check if sound is playing | [ ] |
| Stop Sound | `main2` | Stop playing a sound | [x] |
| Set Color | `main2` | Colorize the sprite | [ ] |
| Transform Sprite | `main2` | Scale and rotate sprite | [ ] |

## Draw (10 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Set Drawing Color | `draw` | Set color for drawing | [x] |
| Fill Color | `draw` | Fill screen with color | [ ] |
| Draw Line | `draw` | Draw a line | [ ] |
| Draw Ellipse | `draw` | Draw an ellipse | [ ] |
| Draw Arrow | `draw` | Draw an arrow | [ ] |
| Draw Scaled Text | `draw` | Draw scaled text | [ ] |
| Draw Sprite | `draw` | Draw a sprite at position | [ ] |
| Draw Background | `draw` | Draw a background image | [ ] |
| Set Font | `draw` | Set text font | [ ] |
| Create Effect | `draw` | Create visual effect | [ ] |

## Timing (6 actions)

Timelines are not yet supported in PyGameMaker.

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Set Timeline | `timing` | Set instance timeline | [ ] |
| Set Timeline Position | `timing` | Set timeline position | [ ] |
| Set Timeline Speed | `timing` | Set timeline playback speed | [ ] |
| Start Timeline | `timing` | Start timeline playback | [ ] |
| Pause Timeline | `timing` | Pause timeline | [ ] |
| Stop Timeline | `timing` | Stop and reset timeline | [ ] |

## Info (5 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Save Game | `info` | Save game state | [ ] |
| Load Game | `info` | Load game state | [ ] |
| Show Game Information | `info` | Display game info screen | [ ] |
| Show Video | `info` | Play video file | [ ] |
| Open Web Page | `info` | Open URL in browser | [ ] |

## Rooms (7 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Set Room Caption | `rooms` | Set room caption text | [ ] |
| Set Room Speed | `rooms` | Set game speed (FPS) | [ ] |
| Set Room Persistent | `rooms` | Make room persistent | [ ] |
| Set Background Color | `rooms` | Set room background color | [ ] |
| Set Background Image | `rooms` | Set room background image | [ ] |
| Enable Views | `rooms` | Enable/disable view system | [ ] |
| Set View | `rooms` | Configure a view | [ ] |

## Extra (3 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Draw Variable | `extra` | Draw variable value on screen | [ ] |
| Test Room | `extra` | Check if in specific room | [ ] |
| Go to Different Room | `extra` | Go to specific room | [ ] |

## Code (1 action)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Execute Script | `code` | Call a script | [ ] |

## Resources (3 actions)

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Replace Sprite from File | `resources` | Load sprite from file | [ ] |
| Replace Sound from File | `resources` | Load sound from file | [ ] |
| Replace Background from File | `resources` | Load background from file | [ ] |

## Particles (8 actions)

Particle systems are not yet supported in PyGameMaker.

| Action | Type | Description | Status |
|--------|------|-------------|--------|
| Create Particle System | `particles` | Create a particle system | [ ] |
| Destroy Particle System | `particles` | Remove particle system | [ ] |
| Clear All Particles | `particles` | Remove all particles | [ ] |
| Create Particle Type | `particles` | Define particle type | [ ] |
| Create Particle Emitter | `particles` | Create particle emitter | [ ] |
| Destroy Particle Emitter | `particles` | Remove particle emitter | [ ] |
| Stream Particles | `particles` | Emit particles continuously | [ ] |
| Burst Particles | `particles` | Emit particles once | [ ] |

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

### Medium Priority
1. Draw actions (Line, Ellipse, Arrow, Sprite)
2. Room settings (Caption, Speed, Background Color)
3. Save/Load Game
4. Move to Contact, Move Towards Point

### Low Priority (advanced features)
1. Timelines (requires timeline editor first)
2. Particles (requires particle system implementation)
3. Views (requires view system implementation)
4. Scripts (requires script editor)

---

## Implementation Notes

To implement an action:
1. Find the action definition in `actions/<category>_actions.py`
2. Change `implemented=False` to `implemented=True`
3. Add the execution method in `runtime/action_executor.py`
4. Test the action in a sample game
5. Check the box in this document
