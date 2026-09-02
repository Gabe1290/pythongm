# Control

*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*

> **Auto-generated** from the IDE's action registry by `tools/gen_action_reference.py` — do not edit by hand; re-run the generator after changing actions.

### Check Empty

| Property | Value |
|----------|-------|
| **Name** | `check_empty` |
| **Icon** | 🔍 |
| **Category** | Control |

True when (x, y) is collision-free. Use with start_block/end_block to gate the following action(s), GM-style

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Text | `self.x` | X position to check (expression OK, e.g. self.x + 32) |
| `y` | Text | `self.y` | Y position to check (expression OK, e.g. self.y + 32) |
| `relative` | Yes/No | No | Treat X/Y as offsets from this instance's position instead of absolute coordinates; optional |
| `objects` | Choice | `solid` | Which instances count as occupying the position; Choices: `solid`, `all` |

### Comment

| Property | Value |
|----------|-------|
| **Name** | `comment` |
| **Icon** | ⚠️ |
| **Category** | Control |

A comment in the action list (no runtime effect)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `text` | Text | — | Free-form comment text; optional |

### Else

| Property | Value |
|----------|-------|
| **Name** | `else_action` |
| **Icon** | ⚡ |
| **Category** | Control |

Marks the else branch of a conditional

*Parameters:* none

### End Block

| Property | Value |
|----------|-------|
| **Name** | `end_block` |
| **Icon** | 📁 |
| **Category** | Control |

End a block of actions

*Parameters:* none

### Execute Code

| Property | Value |
|----------|-------|
| **Name** | `execute_code` |
| **Icon** | 📜 |
| **Category** | Control |

Run an inline block of Python code

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `code` | Code | — | Python source to evaluate against the instance |

### Execute Script

| Property | Value |
|----------|-------|
| **Name** | `execute_script` |
| **Icon** | 📜 |
| **Category** | Control |

Run one of the project's script assets

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `script` | Script | — | Name of the project script to run |
| `arg0` | Text | — | Available in the script as argument0; optional |
| `arg1` | Text | — | Available in the script as argument1; optional |
| `arg2` | Text | — | Available in the script as argument2; optional |
| `arg3` | Text | — | Available in the script as argument3; optional |
| `arg4` | Text | — | Available in the script as argument4; optional |

### Exit Event

| Property | Value |
|----------|-------|
| **Name** | `exit_event` |
| **Icon** | 🚪 |
| **Category** | Control |

Stop executing remaining actions in this event

*Parameters:* none

### If Can Push

| Property | Value |
|----------|-------|
| **Name** | `if_can_push` |
| **Icon** | 📦 |
| **Category** | Control |

Check if a box/object can be pushed in the current direction (Sokoban-style)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `direction` | Choice | `facing` | Direction to check for push; Choices: `facing` |
| `object_type` | Text | `box` | Type of object being pushed |
| `then_action` | Choice | `push_and_move` | Action if push is possible; Choices: `push_and_move`, `none` |
| `else_action` | Choice | `stop_movement` | Action if push is blocked; Choices: `stop_movement`, `none` |

### If Collision

| Property | Value |
|----------|-------|
| **Name** | `if_collision` |
| **Icon** | ❓💥 |
| **Category** | Control |

Conditional: true if the instance would collide at offset (x, y)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Number | `0` | Horizontal offset to test |
| `y` | Number | `0` | Vertical offset to test |
| `object` | Text | `any` | 'any', 'solid', or an object name; Choices: `any`, `solid`; optional |
| `not_flag` | Yes/No | No | Negate the result; optional |

### If Collision At

| Property | Value |
|----------|-------|
| **Name** | `if_collision_at` |
| **Icon** | 🎯 |
| **Category** | Control |

Check for collision at a position

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `x` | Text | `self.x + 32` | X position expression |
| `y` | Text | `self.y` | Y position expression |
| `object_type` | Choice | `any` | Object type to check; Choices: `any`, `solid` |
| `then_actions` | Action list | — | Actions if collision found |
| `else_actions` | Action list | — | Actions if no collision |

### If Condition

| Property | Value |
|----------|-------|
| **Name** | `if_condition` |
| **Icon** | ❓ |
| **Category** | Control |

Conditional check with then/else actions

*Parameters:* none

### If Object Exists

| Property | Value |
|----------|-------|
| **Name** | `if_object_exists` |
| **Icon** | ❓ |
| **Category** | Control |

Conditional: true if at least one instance of object exists

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `object` | Object | — | Object type to check |
| `not_flag` | Yes/No | No | Negate the result (act when the object does NOT exist); optional |

### Repeat

| Property | Value |
|----------|-------|
| **Name** | `repeat` |
| **Icon** | 🔁 |
| **Category** | Control |

Repeat next action/block N times

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `times` | Number | `10` | Number of times to repeat |
| `actions` | Action list | — | Actions to repeat |

### Set Variable

| Property | Value |
|----------|-------|
| **Name** | `set_variable` |
| **Icon** | 📝 |
| **Category** | Control |

Set an instance or global variable

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `variable` | Text | — | Variable name |
| `value` | Text | `0` | Value (number, string, or expression) |
| `scope` | Choice | `self` | Variable scope; Choices: `self`, `other`, `global` |
| `relative` | Yes/No | No | Add to current value instead of replacing |

### Start Block

| Property | Value |
|----------|-------|
| **Name** | `start_block` |
| **Icon** | 📂 |
| **Category** | Control |

Start a block of actions (for grouping)

*Parameters:* none

### Test Chance

| Property | Value |
|----------|-------|
| **Name** | `test_chance` |
| **Icon** | 🎲❓ |
| **Category** | Control |

Conditional: true with probability 1 in 'sides'

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `sides` | Number | `6` | A 1-in-N chance of being true |

### Test Expression

| Property | Value |
|----------|-------|
| **Name** | `test_expression` |
| **Icon** | ❓ |
| **Category** | Control |

Test if an expression is true

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `expression` | Text | — | Expression to evaluate (true if >= 0.5) |
| `then_actions` | Action list | — | Actions if true |
| `else_actions` | Action list | — | Actions if false |

### Test Question

| Property | Value |
|----------|-------|
| **Name** | `test_question` |
| **Icon** | ❓💬 |
| **Category** | Control |

Conditional: show a yes/no dialog; true if the user answers yes

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `question` | Text | `Continue?` | Question shown to the player |

### Test Variable

| Property | Value |
|----------|-------|
| **Name** | `test_variable` |
| **Icon** | ❓ |
| **Category** | Control |

Test an instance or global variable value

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `variable` | Text | — | Variable name |
| `value` | Text | `0` | Value to compare |
| `scope` | Choice | `self` | Variable scope; Choices: `self`, `other`, `global` |
| `operation` | Choice | `equal` | Comparison operator; Choices: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Other Categories

- [Movement](Full-Action-Reference-Movement) (20)
- [Instance](Full-Action-Reference-Instance) (12)
- [Score](Full-Action-Reference-Score) (11)
- [Room](Full-Action-Reference-Room) (13)
- [Timing](Full-Action-Reference-Timing) (8)
- [Audio](Full-Action-Reference-Audio) (6)
- [Game](Full-Action-Reference-Game) (25)
- [Grid](Full-Action-Reference-Grid) (4)
- [Views](Full-Action-Reference-Views) (2)
- [3D View](Full-Action-Reference-3D-View-Actions) (16)
- [Particles](Full-Action-Reference-Particles) (8)
- [Network](Full-Action-Reference-Network-Actions) (15)

[← Back to Full Action Reference](Full-Action-Reference)
