# SMOOTH MOVEMENT EXPANSION - COMPLETE GUIDE

## Overview

Expanding the minimal labyrinth framework to support:
- ✅ **Speed-based smooth movement** (hspeed, vspeed)
- ✅ **Keyboard held events** (continuous while key is down)
- ✅ **Grid detection** (check if object is on grid, snap to grid)

---

## Files to Update

### 1. **events/event_types.py**
Replace with: [event_types_expanded.py](computer:///mnt/user-data/outputs/event_types_expanded.py)

**Changes:**
- ✅ Restored "Keyboard" event (held down for smooth movement)
- ✅ Kept "Keyboard Press" event (single press for grid movement)

**Result:** 6 events total (was 5)

---

### 2. **events/action_types.py**
Replace with: [action_types_expanded.py](computer:///mnt/user-data/outputs/action_types_expanded.py)

**Changes:**
- ✅ Added "Set Horizontal Speed" action
- ✅ Added "Set Vertical Speed" action
- ✅ Added "Stop Movement" action
- ✅ Added "Snap to Grid" action
- ✅ Added "If On Grid" action

**Result:** 10 actions total (was 6)

---

### 3. **action_executor.py** (in project root)
Replace with: [action_executor_expanded.py](computer:///mnt/user-data/outputs/action_executor_expanded.py)

**Changes:**
- ✅ Added handlers for all 5 new actions
- ✅ Kept all existing action handlers

---

### 4. **game_runner.py** (in project root)
Follow instructions in: [GAME_RUNNER_SPEED_UPDATES.md](computer:///mnt/user-data/outputs/GAME_RUNNER_SPEED_UPDATES.md)

**Changes:**
- ✅ Add hspeed/vspeed properties to GameInstance
- ✅ Add handle_keyboard_held() method
- ✅ Update handle_events() to call handle_keyboard_held()
- ✅ Apply speeds in update() method

---

## Complete Event & Action List

### 📋 Events (6 Total)

| # | Event | Icon | Description | Use Case |
|---|-------|------|-------------|----------|
| 1 | Create | 🎯 | When object created | Initialize variables |
| 2 | Step | ⭐ | Every frame | Continuous checks |
| 3 | Destroy | 💥 | When object destroyed | Cleanup |
| 4 | Collision With... | 💥 | Hitting another object | Wall collision, goal reached |
| 5 | **Keyboard** | ⌨️ | **While key held down** | **Smooth movement** |
| 6 | Keyboard Press | 🔘 | Single key press | Grid-based movement |

### 🎬 Actions (10 Total)

#### Movement (4 actions)
| # | Action | Icon | Description |
|---|--------|------|-------------|
| 1 | Move Grid | ⬛ | Instant grid movement |
| 2 | **Set Horizontal Speed** | ↔️ | **Set hspeed (smooth)** |
| 3 | **Set Vertical Speed** | ↕️ | **Set vspeed (smooth)** |
| 4 | **Stop Movement** | 🛑 | **Set hspeed & vspeed to 0** |

#### Grid (2 actions)
| # | Action | Icon | Description |
|---|--------|------|-------------|
| 5 | **Snap to Grid** | 📐 | **Align to nearest grid cell** |
| 6 | **If On Grid** | 🎯 | **Check if aligned to grid** |

#### Control (1 action)
| # | Action | Icon | Description |
|---|--------|------|-------------|
| 7 | If Collision At | 🎯 | Check collision conditionally |

#### Game (2 actions)
| # | Action | Icon | Description |
|---|--------|------|-------------|
| 8 | Show Message | 💬 | Display text |
| 9 | Restart Room | 🔄 | Reset level |
| 10 | Next Room | ➡️ | Advance level |

#### Instance (1 action)
| # | Action | Icon | Description |
|---|--------|------|-------------|
| 11 | Destroy Instance | 💀 | Remove object |

---

## Movement Comparison

### Grid-Based Movement (Original)
```
Event: Keyboard Press → right
  Action: Move Grid (right, 32)
```
**Result:** Player jumps one grid cell per key press

### Smooth Movement (New)
```
Event: Keyboard → right (held)
  Action: Set Horizontal Speed = 4

Event: Keyboard → left (held)
  Action: Set Horizontal Speed = -4

Event: Step
  Action: If On Grid
    Then: Stop Movement
```
**Result:** Player moves smoothly, stops when aligned to grid

---

## Common Patterns

### Pattern 1: Smooth Movement Until Grid
```
Object: obj_player

Event: Keyboard → right (held)
  - Set Horizontal Speed = 4

Event: Keyboard → left (held)
  - Set Horizontal Speed = -4

Event: Keyboard → up (held)
  - Set Vertical Speed = -4

Event: Keyboard → down (held)
  - Set Vertical Speed = 4

Event: Step
  - If On Grid (32)
    Then:
      - Stop Movement
      - Snap to Grid
```

### Pattern 2: Smooth Movement with Wall Stop
```
Object: obj_player

Event: Keyboard → right (held)
  - Set Horizontal Speed = 4

Event: Step
  - If Collision At (self.x + 32, self.y) with "solid"
    Then: Stop Movement
    
  - If On Grid (32)
    Then:
      - Stop Movement
      - Snap to Grid
```

### Pattern 3: Hybrid Movement
```
Object: obj_player

// Use keyboard PRESS for grid snapping
Event: Keyboard Press → right
  - Move Grid (right, 32)

// Use keyboard HELD for smooth movement
Event: Keyboard → right (held)
  - Set Horizontal Speed = 2
```

---

## Instance Properties

After updates, each instance will have:

### Position Properties
- `x` - X coordinate (float)
- `y` - Y coordinate (float)

### Speed Properties (NEW)
- `hspeed` - Horizontal speed in pixels/frame (float)
- `vspeed` - Vertical speed in pixels/frame (float)

### Movement Flags
- `intended_x` - Target X for grid movement (set by Move Grid action)
- `intended_y` - Target Y for grid movement (set by Move Grid action)

---

## Physics Update Order

Each frame, the game processes in this order:

1. **Handle Events** (keyboard input)
2. **Execute Keyboard Held Events** (if keys pressed)
3. **Update:**
   - Check room transitions
   - **Apply speeds** (x += hspeed, y += vspeed)
   - Apply intended movement (grid-based)
   - Check collisions
   - Execute step events
4. **Render**

---

## Testing Checklist

### ✅ Test Grid Movement
- [ ] Create player with Keyboard Press → Move Grid
- [ ] Press arrow key once
- [ ] Player jumps exactly one grid cell

### ✅ Test Smooth Movement
- [ ] Create player with Keyboard (held) → Set Horizontal Speed
- [ ] Hold arrow key
- [ ] Player moves continuously and smoothly

### ✅ Test Grid Detection
- [ ] Add If On Grid action to Step event
- [ ] Move player
- [ ] Console shows "On grid" when aligned

### ✅ Test Speed Stop
- [ ] Add Stop Movement action
- [ ] Move player with speed
- [ ] Trigger stop action
- [ ] Player stops immediately

### ✅ Test Snap to Grid
- [ ] Move player slightly off grid
- [ ] Trigger Snap to Grid action
- [ ] Player aligns to nearest grid cell

---

## Educational Benefits

### For Students Learning Programming:

1. **Grid Movement** (Simpler)
   - Discrete steps
   - Easier to understand
   - Good for turn-based games

2. **Speed Movement** (More Advanced)
   - Continuous motion
   - Introduces velocity concept
   - Physics-based thinking
   - Smoother gameplay

3. **Hybrid Approach** (Best of Both)
   - Use both movement types
   - Teaches when to use each
   - More game design flexibility

---

## Next Steps

1. **Update the 4 files** with the expanded versions
2. **Restart your IDE** to load new events/actions
3. **Create a test object** using smooth movement
4. **Try both movement styles** to compare

## Files Ready to Use

✅ [event_types_expanded.py](computer:///mnt/user-data/outputs/event_types_expanded.py)
✅ [action_types_expanded.py](computer:///mnt/user-data/outputs/action_types_expanded.py)
✅ [action_executor_expanded.py](computer:///mnt/user-data/outputs/action_executor_expanded.py)
✅ [Game Runner Update Instructions](computer:///mnt/user-data/outputs/GAME_RUNNER_SPEED_UPDATES.md)

---

**Your minimal framework is now expanded with smooth movement!** 🎮✨
