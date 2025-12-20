# PyGameMaker Complete Events and Actions Reference

## Events Available in IDE and Blockly

### Object Events (4)
| Event | IDE | Blockly | Description |
|-------|-----|---------|-------------|
| Create | ✅ | ✅ | Executed when the instance is created |
| Destroy | ✅ | ✅ | Executed when the instance is destroyed |
| Step | ✅ | ✅ | Normal step event - executed every frame |
| Draw | ✅ | ✅ | Custom drawing event - overrides default sprite drawing |

### Step Events (3 total, 1 in Blockly)
| Event | IDE | Blockly | Description |
|-------|-----|---------|-------------|
| Begin Step | ✅ | ❌ | Executed at the beginning of each step, before instances move |
| Step | ✅ | ✅ | Normal step event - executed every frame |
| End Step | ✅ | ❌ | Executed at the end of each step, after instances move |

### Keyboard Events (5 types + 60+ keys)
| Event Type | IDE | Blockly | Description |
|------------|-----|---------|-------------|
| No Key | ✅ | ✅ | No keyboard key is currently pressed |
| Any Key | ✅ | ✅ | Any keyboard key is pressed |
| Keyboard (held) | ✅ | ✅ | Specific key is held down (continuous) |
| Key Press | ✅ | ✅ | Specific key is pressed (once) |
| Key Release | ✅ | ✅ | Specific key is released |

**Available Keys (60+):**
- Arrow Keys: Up, Down, Left, Right
- Common: Space, Enter, Escape, Tab, Backspace, Delete
- Modifiers: Left/Right Shift, Ctrl, Alt
- Letters: A-Z (26 keys)
- Numbers: 0-9 (10 keys)
- Function: F1-F12 (12 keys)
- Navigation: Home, End, Page Up, Page Down, Insert
- Numpad: 0-9, +, -, *, /, Enter, . (16 keys)

### Mouse Events (24 total, 6 in Blockly)
| Event | IDE | Blockly | Description |
|-------|-----|---------|-------------|
| Left Button (held) | ✅ | ❌ | Left mouse button is held (continuous) |
| Right Button (held) | ✅ | ❌ | Right mouse button is held (continuous) |
| Middle Button (held) | ✅ | ❌ | Middle mouse button is held (continuous) |
| No Button | ✅ | ❌ | No mouse button is pressed |
| Left Pressed | ✅ | ✅ | Left mouse button pressed (once) |
| Right Pressed | ✅ | ✅ | Right mouse button pressed (once) |
| Middle Pressed | ✅ | ❌ | Middle mouse button pressed (once) |
| Left Released | ✅ | ✅ | Left mouse button released |
| Right Released | ✅ | ✅ | Right mouse button released |
| Middle Released | ✅ | ❌ | Middle mouse button released |
| Mouse Enter | ✅ | ✅ | Mouse enters instance bounding box |
| Mouse Leave | ✅ | ✅ | Mouse leaves instance bounding box |
| Mouse Wheel Up | ✅ | ❌ | Mouse wheel scrolled up |
| Mouse Wheel Down | ✅ | ❌ | Mouse wheel scrolled down |
| Global Left Button | ✅ | ❌ | Left button anywhere in room (continuous) |
| Global Right Button | ✅ | ❌ | Right button anywhere in room (continuous) |
| Global Middle Button | ✅ | ❌ | Middle button anywhere in room (continuous) |
| Global Left Pressed | ✅ | ❌ | Left button pressed anywhere (once) |
| Global Right Pressed | ✅ | ❌ | Right button pressed anywhere (once) |
| Global Middle Pressed | ✅ | ❌ | Middle button pressed anywhere (once) |
| Global Left Released | ✅ | ❌ | Left button released anywhere |
| Global Right Released | ✅ | ❌ | Right button released anywhere |
| Global Middle Released | ✅ | ❌ | Middle button released anywhere |

### Collision Events
| Event | IDE | Blockly | Description |
|-------|-----|---------|-------------|
| Collision with [object] | ✅ | ✅ | Collision with another object (dynamic list) |

### Alarm Events (12 total, 0 in Blockly)
| Event | IDE | Blockly | Description |
|-------|-----|---------|-------------|
| Alarm 0-11 | ✅ | ❌ | Executes when alarm reaches zero (12 independent alarms) |

### Other Events (19 total, 0 in Blockly)
| Event | IDE | Blockly | Description |
|-------|-----|---------|-------------|
| Outside Room | ✅ | ❌ | Instance completely outside room boundaries |
| Intersect Boundary | ✅ | ❌ | Instance intersects room boundary |
| Game Start | ✅ | ❌ | Executed once when game starts |
| Game End | ✅ | ❌ | Executed when game ends |
| Room Start | ✅ | ❌ | Executed when room starts |
| Room End | ✅ | ❌ | Executed when room ends |
| No More Lives | ✅ | ❌ | Lives become 0 or less |
| No More Health | ✅ | ❌ | Health becomes 0 or less |
| Animation End | ✅ | ❌ | Sprite animation reaches last frame |
| End of Path | ✅ | ❌ | Instance reaches end of path |
| Close Button | ✅ | ❌ | Game window close button pressed |
| User Event 0-15 | ✅ | ❌ | Custom user-defined events (16 total) |

---

## Actions Available in IDE and Blockly

### Movement Actions (19 total, 10 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Set Horizontal Speed | ✅ | ✅ | Set horizontal movement speed |
| Set Vertical Speed | ✅ | ✅ | Set vertical movement speed |
| Stop Movement | ✅ | ✅ | Stop all movement (speed = 0) |
| Start Moving Direction | ✅ | ✅ | Move in 8-way direction |
| Move Towards Point | ✅ | ✅ | Move towards specific coordinates |
| Snap to Grid | ✅ | ✅ | Align position to grid |
| Jump to Position | ✅ | ✅ | Instantly move to coordinates |
| Stop If No Keys | ✅ | ✅ | Stop if no arrow keys pressed (grid) |
| Check Keys and Move | ✅ | ✅ | Check keys and restart grid movement |
| If On Grid | ✅ | ✅ | Execute actions if on grid |
| Set Direction and Speed | ✅ | ❌ | Set exact direction and speed |
| Set Gravity | ✅ | ❌ | Apply gravity |
| Set Friction | ✅ | ❌ | Set movement friction |
| Reverse Horizontal | ✅ | ❌ | Reverse horizontal movement |
| Reverse Vertical | ✅ | ❌ | Reverse vertical movement |
| Jump to Start | ✅ | ❌ | Return to creation position |
| Jump to Random | ✅ | ❌ | Move to random position |
| Wrap Around Room | ✅ | ❌ | Wrap to opposite side |
| Move to Contact | ✅ | ❌ | Move until touching object |
| Bounce | ✅ | ❌ | Bounce off objects |

### Score/Lives/Health Actions (9 total, 9 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Set Score | ✅ | ✅ | Set score to value |
| Add to Score | ✅ | ✅ | Add/subtract from score |
| Set Lives | ✅ | ✅ | Set lives to value |
| Add to Lives | ✅ | ✅ | Add/subtract lives |
| Set Health | ✅ | ✅ | Set health to value |
| Add to Health | ✅ | ✅ | Add/subtract health |
| Draw Score | ✅ | ✅ | Display score text |
| Draw Lives | ✅ | ✅ | Display lives icons |
| Draw Health Bar | ✅ | ✅ | Display health bar |

### Instance Actions (3 total, 3 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Destroy Instance | ✅ | ✅ | Destroy this instance |
| Destroy Other | ✅ | ✅ | Destroy other instance (collision) |
| Create Instance | ✅ | ✅ | Create object instance |

### Room Actions (3 total, 3 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Go to Next Room | ✅ | ✅ | Move to next room |
| Restart Room | ✅ | ✅ | Restart current room |
| Go to Room | ✅ | ✅ | Go to specific room |

### Sound Actions (4 total, 3 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Play Sound | ✅ | ✅ | Play sound effect |
| Play Music | ✅ | ✅ | Play background music (looping) |
| Stop Music | ✅ | ✅ | Stop background music |
| Set Volume | ✅ | ❌ | Set global volume |

### Output Actions (1 total, 1 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Show Message | ✅ | ✅ | Display message dialog |

### Drawing Actions (5 total, 0 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Draw Text | ✅ | ❌ | Draw text on screen |
| Draw Rectangle | ✅ | ❌ | Draw filled rectangle |
| Draw Circle | ✅ | ❌ | Draw filled circle |
| Set Sprite | ✅ | ❌ | Change sprite |
| Set Alpha | ✅ | ❌ | Set transparency |

### Control/Conditional Actions (9 total, 0 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Test Expression | ✅ | ❌ | Test if expression is true |
| Check Empty | ✅ | ❌ | Check if position is empty |
| Check Collision | ✅ | ❌ | Check collision at position |
| Start Block | ✅ | ❌ | Start action block |
| End Block | ✅ | ❌ | End action block |
| Else Action | ✅ | ❌ | Else branch |
| Repeat | ✅ | ❌ | Repeat actions N times |
| Exit Event | ✅ | ❌ | Stop executing event |

### Timing Actions (1 total, 0 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Set Alarm | ✅ | ❌ | Set alarm clock |

### Appearance Actions (3 total, 0 in Blockly)
| Action | IDE | Blockly | Description |
|--------|-----|---------|-------------|
| Set Sprite | ✅ | ❌ | Change sprite |
| Transform Sprite | ✅ | ❌ | Scale and rotate |
| Set Color | ✅ | ❌ | Colorize sprite |

---

## Summary

### Events Coverage
- **Total IDE Events**: 71+ (including dynamic collision, alarm, keyboard, mouse)
- **Total Blockly Events**: 13 event types + 60+ keys
- **Coverage**: ~18% base events + all keyboard variations

### Actions Coverage
- **Total IDE Actions**: 56+ actions
- **Total Blockly Actions**: 29 actions
- **Coverage**: ~52%

### Blockly Has Full Support For:
✅ Basic object events (create, destroy, step, draw)
✅ Complete keyboard input (5 types, 60+ keys)
✅ Basic mouse input (6 events)
✅ Collision detection
✅ Movement and positioning (10 actions)
✅ Score/lives/health system (9 actions)
✅ Instance management (3 actions)
✅ Room navigation (3 actions)
✅ Sound/music (3 actions)
✅ Grid-based movement (3 custom actions)

### Blockly Missing:
❌ Alarm events and set_alarm action
❌ Step variants (begin_step, end_step)
❌ Advanced mouse events (wheel, global, middle button)
❌ Other events (room_start, game_start, animation_end, etc.)
❌ Drawing actions (draw_text, draw_rectangle, etc.)
❌ Control flow actions (test_expression, check_empty, repeat, etc.)
❌ Appearance actions (transform_sprite, set_color)
❌ Advanced movement (gravity, friction, bounce, wrap)
