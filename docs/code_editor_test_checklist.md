# PyGameMaker Code Editor Test Checklist

A comprehensive checklist for testing events and actions in the Python Code Editor.

## Overview

The Code Editor provides bidirectional sync between visual Blockly blocks and Python code. This checklist covers all events and actions that have Python code equivalents.

---

## 1. Event Testing

### Object Events
- [ ] **Create Event** - Executes when instance is created
- [ ] **Destroy Event** - Executes when instance is destroyed
- [ ] **Step Event** - Executes every frame

### Step Events
- [ ] **Begin Step** - Executes at start of step, before other events
- [ ] **End Step** - Executes at end of step, after collisions

### Drawing Events
- [ ] **Draw Event** - Executes when object is drawn (replaces default sprite)

### Alarm Events
- [ ] **Alarm 0** - Timer countdown trigger
- [ ] **Alarm 1** - Timer countdown trigger
- [ ] **Alarm 2** - Timer countdown trigger
- [ ] **Alarm 3** - Timer countdown trigger
- [ ] **Alarm 4** - Timer countdown trigger
- [ ] **Alarm 5** - Timer countdown trigger
- [ ] **Alarm 6** - Timer countdown trigger
- [ ] **Alarm 7** - Timer countdown trigger
- [ ] **Alarm 8** - Timer countdown trigger
- [ ] **Alarm 9** - Timer countdown trigger
- [ ] **Alarm 10** - Timer countdown trigger
- [ ] **Alarm 11** - Timer countdown trigger

### Keyboard Events
- [ ] **Keyboard (held)** - Fires continuously while key is held
- [ ] **Keyboard Press** - Fires once when key is first pressed
- [ ] **Keyboard Release** - Fires once when key is released
- [ ] Arrow keys (Left, Right, Up, Down)
- [ ] WASD keys
- [ ] Space key
- [ ] Enter key
- [ ] Escape key
- [ ] Any key detection

### Collision Events
- [ ] **Collision With Object** - Fires when colliding with specific object type

---

## 2. Movement Actions

### Speed Control
- [ ] **Set Horizontal Speed (hspeed)** - Set X velocity
  ```python
  self.hspeed = 5
  ```
- [ ] **Set Vertical Speed (vspeed)** - Set Y velocity
  ```python
  self.vspeed = -3
  ```
- [ ] **Stop Movement** - Set both speeds to 0
  ```python
  self.hspeed = 0
  self.vspeed = 0
  ```

### Direction Reversal
- [ ] **Reverse Horizontal** - Flip X direction
  ```python
  self.hspeed = -self.hspeed
  ```
- [ ] **Reverse Vertical** - Flip Y direction
  ```python
  self.vspeed = -self.vspeed
  ```

### Physics
- [ ] **Set Gravity** - Apply downward acceleration
  ```python
  self.gravity = 0.5
  self.gravity_direction = 270
  ```
- [ ] **Set Friction** - Apply deceleration
  ```python
  self.friction = 0.1
  ```

### Position
- [ ] **Jump to Position** - Teleport to coordinates
  ```python
  self.x = 100
  self.y = 200
  ```
- [ ] **Snap to Grid** - Align to grid
  ```python
  self.snap_to_grid(32)
  ```
- [ ] **Set Direction and Speed** - Combined movement
  ```python
  self.direction = 45
  self.speed = 5
  ```

---

## 3. Instance Actions

### Instance Management
- [ ] **Destroy Instance (self)** - Remove current instance
  ```python
  self.destroy()
  ```
- [ ] **Destroy Instance (other)** - Remove colliding instance
  ```python
  other.destroy()
  ```
- [ ] **Create Instance** - Spawn new instance
  ```python
  game.create_instance("obj_bullet", self.x, self.y)
  ```

---

## 4. Room Actions

### Room Navigation
- [ ] **Next Room** - Go to next room in order
  ```python
  game.goto_next_room()
  ```
- [ ] **Previous Room** - Go to previous room in order
  ```python
  game.goto_previous_room()
  ```
- [ ] **Restart Room** - Reload current room
  ```python
  game.restart_room()
  ```
- [ ] **Go to Room** - Go to specific room by name
  ```python
  game.goto_room("room_level2")
  ```

---

## 5. Game Actions

### Game Control
- [ ] **End Game** - Quit the game
  ```python
  game.end_game()
  ```
- [ ] **Restart Game** - Restart from beginning
  ```python
  game.restart_game()
  ```

---

## 6. Score/Lives/Health Actions

### Score
- [ ] **Set Score** - Set score value
  ```python
  game.score = 100
  ```
- [ ] **Add to Score** - Increase score
  ```python
  game.score += 10
  ```
- [ ] **Draw Score** - Display score on screen
  ```python
  game.draw_score(10, 10)
  ```

### Lives
- [ ] **Set Lives** - Set lives value
  ```python
  game.lives = 3
  ```
- [ ] **Add Lives** - Increase/decrease lives
  ```python
  game.lives += 1
  game.lives -= 1
  ```
- [ ] **Draw Lives** - Display lives on screen
  ```python
  game.draw_lives(10, 30)
  ```

### Health
- [ ] **Set Health** - Set health value (0-100)
  ```python
  game.health = 100
  ```
- [ ] **Add Health** - Increase/decrease health
  ```python
  game.health += 25
  game.health -= 10
  ```
- [ ] **Draw Health Bar** - Display health bar
  ```python
  game.draw_health_bar(10, 50, 200, 20)
  ```

---

## 7. Sprite Actions

### Sprite Control
- [ ] **Set Sprite** - Change instance sprite
  ```python
  self.sprite = "spr_player_jump"
  ```
- [ ] **Set Alpha** - Set transparency (0.0 to 1.0)
  ```python
  self.alpha = 0.5
  ```

---

## 8. Timing Actions

### Alarms
- [ ] **Set Alarm** - Start countdown timer
  ```python
  self.alarm[0] = 60  # 60 steps = 1 second at 60 FPS
  ```

---

## 9. Sound Actions

### Sound Playback
- [ ] **Play Sound** - Play sound effect once
  ```python
  game.play_sound("snd_explosion")
  ```
- [ ] **Play Music** - Play background music (loops)
  ```python
  game.play_music("mus_background")
  ```
- [ ] **Stop Music** - Stop background music
  ```python
  game.stop_music()
  ```

---

## 10. Output Actions

### Messages
- [ ] **Display Message** - Show dialog box
  ```python
  game.show_message("Hello World!")
  ```
- [ ] **Execute Code** - Run custom Python code
  ```python
  # Custom Python code executes directly
  print("Debug output")
  ```

---

## 11. Bidirectional Sync Testing

### Code to Blocks
- [ ] Write Python code and verify Blockly blocks update
- [ ] Edit code and confirm block parameters change
- [ ] Delete code and verify blocks are removed

### Blocks to Code
- [ ] Add Blockly blocks and verify Python code generates
- [ ] Modify block parameters and confirm code updates
- [ ] Delete blocks and verify code is removed

### Round-Trip Testing
- [ ] Create blocks, switch to code, edit, switch back to blocks
- [ ] Verify no data loss in multiple switches
- [ ] Test complex event with multiple actions

---

## Test Environment Notes

**Date Tested:** _______________

**Version:** _______________

**OS:** _______________

**Tester:** _______________

**Notes:**
