# PyGameMaker Blockly Visual Programming

This directory contains the visual block programming interface for PyGameMaker, built on Google Blockly 12.x.

## File Structure

```
blockly/
├── blockly_workspace.html    # Main Blockly workspace (2120 lines)
├── blockly_blocks.js          # Block definitions (extracted)
├── blockly_generators.js      # Code generation (extracted)
└── README.md                  # This file
```

## Architecture Overview

### blockly_workspace.html
The main HTML file containing the complete Blockly implementation. While this is a large file (2120 lines), it's intentionally kept as a single unit due to:
- Tight coupling with the `workspace` variable
- Bidirectional sync requiring shared state
- WebChannel communication with Qt/PySide6

**Structure** (by line number):
- **Lines 1-110**: HTML head, CSS, Blockly CDN imports
- **Lines 113-430**: Toolbox XML (all block categories)
- **Lines 436-1162**: Block Definitions (all Blockly.Blocks[...])
- **Lines 1164-1354**: Theme & Workspace initialization
- **Lines 1356-1561**: Code Generation Functions
- **Lines 1563-1576**: Workspace Change Listener
- **Lines 1578-1720**: Bidirectional Sync (Events→Blocks)
- **Lines 1722-2098**: Block Creation & Parameter Setting
- **Lines 2100-2120**: API Exports

### blockly_blocks.js
Extracted block definitions for reference and potential future modularization.
Contains all `Blockly.Blocks['...']` definitions organized by category.

### blockly_generators.js
Extracted code generation functions that convert blocks to PyGameMaker events/actions format.
Contains `generateActionCode()` with all action mappings.

## Block Categories

### Events (Yellow #FFD500)
- **Object Events**: create, step, draw, destroy
- **Alarm Events**: alarm_0 through alarm_11 (12 alarms)
- **Keyboard Events**: nokey, anykey, held, press, release (60+ keys)
- **Mouse Events**: left/right press/release, enter, leave
- **Collision Events**: Dynamic based on objects

### Movement (Blue #5C81A6)
- **Basic**: set_hspeed, set_vspeed, stop, move_direction
- **Advanced**: move_towards, snap_to_grid, jump_to
- **Grid**: stop_if_no_keys, check_keys_and_move, if_on_grid
- **Physics**: set_gravity, set_friction, reverse_horizontal, reverse_vertical

### Timing (Red #FF6B6B)
- **Alarms**: set_alarm (0-11)

### Drawing (Purple #9B59B6)
- **Shapes**: draw_text, draw_rectangle, draw_circle
- **Appearance**: set_sprite, set_alpha

### Score/Lives/Health (Green #5CA65C)
- **Setters**: score_set, lives_set, health_set
- **Adders**: score_add, lives_add, health_add
- **Display**: draw_score, draw_lives, draw_health_bar

### Instance (Pink #A65C81)
- **Actions**: instance_destroy, instance_destroy_other, instance_create

### Room (Brown #A6745C)
- **Navigation**: room_goto_next, room_restart, room_goto

### Values (Blue #5C68A6)
- **Position**: value_x, value_y, value_hspeed, value_vspeed
- **Game**: value_score, value_lives, value_health
- **Mouse**: value_mouse_x, value_mouse_y

### Sound (Purple #9966FF)
- **Audio**: sound_play, music_play, music_stop

### Output (Purple #745CA6)
- **Display**: output_message

## Bidirectional Sync

The system supports two-way synchronization between the visual blocks and the IDE's text-based events panel:

### Blocks → Events (Export)
1. User builds program with blocks
2. `generatePyGameMakerCode()` converts blocks to JSON
3. JSON contains events with nested actions
4. "Apply to Events →" button sends to IDE

### Events → Blocks (Import)
1. User creates events in IDE text panel
2. "← Sync from Events" button loads into Blockly
3. `loadEventsData()` parses events JSON
4. `createEventBlock()` creates event blocks
5. `createActionBlock()` creates action blocks with parameters
6. `setBlockParameters()` populates block fields

## Code Generation

Blocks are converted to PyGameMaker's internal format:

```javascript
{
  "create": {
    "actions": [
      {"action": "set_hspeed", "parameters": {"value": 4}},
      {"action": "set_vspeed", "parameters": {"value": 0}}
    ]
  },
  "keyboard": {
    "right": {
      "actions": [{"action": "set_hspeed", "parameters": {"value": 4}}]
    },
    "left": {
      "actions": [{"action": "set_hspeed", "parameters": {"value": -4}}]
    }
  }
}
```

## Adding New Blocks

To add a new block type:

1. **Add to Toolbox** (lines 113-430)
   ```xml
   <block type="my_new_block">
       <field name="PARAM">default</field>
   </block>
   ```

2. **Define Block** (lines 436-1162)
   ```javascript
   Blockly.Blocks['my_new_block'] = {
       init: function() {
           this.appendDummyInput()
               .appendField("My new action");
           this.setPreviousStatement(true, null);
           this.setNextStatement(true, null);
           this.setColour("#5C81A6");
       }
   };
   ```

3. **Add Code Generation** (in `generateActionCode`, lines 1441-1538)
   ```javascript
   case 'my_new_block':
       return {action: 'my_action', parameters: {...}};
   ```

4. **Add Sync Mapping** (lines 1580-1616)
   ```javascript
   'my_action': 'my_new_block'
   ```

5. **Add Parameter Handler** (in `setBlockParameters`, lines 1906-2098)
   ```javascript
   case 'my_new_block':
       block.setFieldValue(params.value, 'PARAM');
       break;
   ```

## Integration with Qt/PySide6

The Blockly workspace communicates with the Python IDE through Qt WebChannel:

### Python → JavaScript
- `blockly_widget.py` loads events via `window.blocklyApi.loadEvents(eventsData)`
- WebChannel bridge: `QWebChannel` + `QWebEngineView`

### JavaScript → Python
- Blocks emit changes via `window.pyBridge.onBlocksChanged(json)`
- Python receives through `BlocklyBridge.blocks_changed` signal

## Keyboard Support

All keyboard blocks support 60+ keys:
- Arrow keys (4)
- Common keys (6): space, enter, escape, tab, backspace, delete
- Modifiers (6): left/right shift, ctrl, alt
- Letters (26): A-Z
- Numbers (10): 0-9
- Function keys (12): F1-F12
- Navigation (5): home, end, page up/down, insert
- Numpad (16): 0-9, +, -, *, /, enter, .

Keys defined in `ALL_KEYS` array (lines 420-465).

## Maintenance Notes

### Why One Large File?
The file is kept as a single unit because:
1. **Shared workspace**: All functions need access to the global `workspace` variable
2. **Tight coupling**: Sync functions directly call generation functions
3. **State management**: The `ignoreChanges` flag prevents infinite loops
4. **WebChannel**: Single context for Qt communication

### Future Modularization
If splitting becomes necessary:
1. Use ES6 modules with `export`/`import`
2. Pass `workspace` as parameter to all functions
3. Create a central state manager
4. Update `blockly_widget.py` to handle multiple script files

### Performance Considerations
- 2120 lines is manageable for modern browsers
- Blockly itself is ~1MB from CDN
- File loads once and stays in memory
- No runtime performance impact

## Testing New Blocks

1. Add block to toolbox and define it
2. Reload Blockly with "Reload" button
3. Drag block onto workspace
4. Click "Apply to Events →"
5. Check IDE events panel for correct JSON
6. Add event in IDE, click "← Sync from Events"
7. Verify block appears with correct parameters

## Troubleshooting

### Block doesn't appear in toolbox
- Check XML in toolbox section (lines 113-430)
- Verify block type name matches definition
- Check browser console for JavaScript errors

### Block doesn't generate code
- Add case in `generateActionCode()` (lines 1441-1538)
- Check browser console for warnings
- Verify action name matches IDE expectations

### Sync from Events fails
- Add mapping in `actionToBlockType` (lines 1580-1616)
- Implement parameter handler in `setBlockParameters()` (lines 1906-2098)
- Check console logs: `[Blockly]` prefix

### Visual flickering on load
- Handled by `setVisible(False)` in `blockly_widget.py`
- Don't remove `ignoreChanges` flag

## References

- [Blockly Documentation](https://developers.google.com/blockly)
- [Qt WebChannel](https://doc.qt.io/qt-6/qtwebchannel-index.html)
- [PySide6 WebEngine](https://doc.qt.io/qtforpython-6/PySide6/QtWebEngineWidgets/)
- Main IDE code: `blockly_widget.py`
- Event definitions: `events/gm80_events.py`
- Action executor: `core/action_executor.py`
