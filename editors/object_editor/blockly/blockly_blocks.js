/**
 * PyGameMaker Blockly Block Definitions
 * All custom block types for visual programming
 */

// Complete list of all available keys for the key selector
var ALL_KEYS = [
    // Arrow keys
    ["Right Arrow", "right"],
    ["Left Arrow", "left"],
    ["Up Arrow", "up"],
    ["Down Arrow", "down"],
    // Common keys
    ["Space", "space"],
    ["Enter", "enter"],
    ["Escape", "escape"],
    ["Tab", "tab"],
    ["Backspace", "backspace"],
    ["Delete", "delete"],
    // Modifier keys
    ["Left Shift", "lshift"],
    ["Right Shift", "rshift"],
    ["Left Ctrl", "lctrl"],
    ["Right Ctrl", "rctrl"],
    ["Left Alt", "lalt"],
    ["Right Alt", "ralt"],
    // Letters A-Z
    ["A", "a"], ["B", "b"], ["C", "c"], ["D", "d"], ["E", "e"],
    ["F", "f"], ["G", "g"], ["H", "h"], ["I", "i"], ["J", "j"],
    ["K", "k"], ["L", "l"], ["M", "m"], ["N", "n"], ["O", "o"],
    ["P", "p"], ["Q", "q"], ["R", "r"], ["S", "s"], ["T", "t"],
    ["U", "u"], ["V", "v"], ["W", "w"], ["X", "x"], ["Y", "y"], ["Z", "z"],
    // Numbers 0-9
    ["0", "0"], ["1", "1"], ["2", "2"], ["3", "3"], ["4", "4"],
    ["5", "5"], ["6", "6"], ["7", "7"], ["8", "8"], ["9", "9"],
    // Function keys
    ["F1", "f1"], ["F2", "f2"], ["F3", "f3"], ["F4", "f4"],
    ["F5", "f5"], ["F6", "f6"], ["F7", "f7"], ["F8", "f8"],
    ["F9", "f9"], ["F10", "f10"], ["F11", "f11"], ["F12", "f12"],
    // Navigation keys
    ["Home", "home"], ["End", "end"],
    ["Page Up", "pageup"], ["Page Down", "pagedown"],
    ["Insert", "insert"],
    // Numpad
    ["Numpad 0", "numpad_0"], ["Numpad 1", "numpad_1"], ["Numpad 2", "numpad_2"],
    ["Numpad 3", "numpad_3"], ["Numpad 4", "numpad_4"], ["Numpad 5", "numpad_5"],
    ["Numpad 6", "numpad_6"], ["Numpad 7", "numpad_7"], ["Numpad 8", "numpad_8"],
    ["Numpad 9", "numpad_9"],
    ["Numpad +", "numpad_plus"], ["Numpad -", "numpad_minus"],
    ["Numpad *", "numpad_multiply"], ["Numpad /", "numpad_divide"],
    ["Numpad Enter", "numpad_enter"], ["Numpad .", "numpad_period"]
];

// ============================================================================
// EVENT BLOCKS
// ============================================================================

Blockly.Blocks['event_create'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When created");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs when the object is created");
    }
};

Blockly.Blocks['event_step'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Every step");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs every frame");
    }
};

Blockly.Blocks['event_draw'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When drawing");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs during the draw phase");
    }
};

Blockly.Blocks['event_destroy'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When destroyed");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs when the object is destroyed");
    }
};

// ============ KEYBOARD EVENT BLOCKS (5 separate blocks) ============

Blockly.Blocks['event_keyboard_nokey'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Keyboard: No key");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs when no keyboard key is pressed");
    }
};

Blockly.Blocks['event_keyboard_anykey'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Keyboard: Any key");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs when any keyboard key is pressed");
    }
};

Blockly.Blocks['event_keyboard_held'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Keyboard:")
            .appendField(new Blockly.FieldDropdown(ALL_KEYS), "KEY")
            .appendField("(held)");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs continuously while the key is held down");
    }
};

Blockly.Blocks['event_keyboard_press'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Key press:")
            .appendField(new Blockly.FieldDropdown(ALL_KEYS), "KEY");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs once when the key is first pressed");
    }
};

Blockly.Blocks['event_keyboard_release'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Key release:")
            .appendField(new Blockly.FieldDropdown(ALL_KEYS), "KEY");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs once when the key is released");
    }
};

Blockly.Blocks['event_mouse'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When mouse")
            .appendField(new Blockly.FieldDropdown([
                ["Left Button Pressed", "left_press"],
                ["Left Button Released", "left_release"],
                ["Right Button Pressed", "right_press"],
                ["Right Button Released", "right_release"],
                ["Mouse Enters", "enter"],
                ["Mouse Leaves", "leave"]
            ]), "BUTTON");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs on mouse events");
    }
};

Blockly.Blocks['event_collision'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When colliding with")
            .appendField(new Blockly.FieldTextInput("obj_wall"), "OBJECT");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs when colliding with another object");
    }
};

// ============ ALARM EVENT BLOCK ============
Blockly.Blocks['event_alarm'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When alarm")
            .appendField(new Blockly.FieldDropdown([
                ["0", "0"], ["1", "1"], ["2", "2"], ["3", "3"],
                ["4", "4"], ["5", "5"], ["6", "6"], ["7", "7"],
                ["8", "8"], ["9", "9"], ["10", "10"], ["11", "11"]
            ]), "ALARM_NUM")
            .appendField("triggers");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FFD500");
        this.setTooltip("Runs when the alarm reaches zero");
    }
};

// ============================================================================
// MOVEMENT ACTION BLOCKS
// ============================================================================

Blockly.Blocks['move_set_hspeed'] = {
    init: function() {
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("Set horizontal speed to");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Set horizontal movement speed");
    }
};

Blockly.Blocks['move_set_vspeed'] = {
    init: function() {
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("Set vertical speed to");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Set vertical movement speed");
    }
};

Blockly.Blocks['move_stop'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Stop movement");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Stop all movement");
    }
};

Blockly.Blocks['move_direction'] = {
    init: function() {
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("Move")
            .appendField(new Blockly.FieldDropdown([
                ["right", "right"],
                ["left", "left"],
                ["up", "up"],
                ["down", "down"]
            ]), "DIRECTION")
            .appendField("at speed");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Move in a direction");
    }
};

Blockly.Blocks['move_towards'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Move towards x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("at speed:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Move towards a point");
    }
};

Blockly.Blocks['move_snap_to_grid'] = {
    init: function() {
        this.appendValueInput("GRID_SIZE")
            .setCheck("Number")
            .appendField("Snap to grid (size:");
        this.appendDummyInput()
            .appendField(")");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Align position to grid");
    }
};

Blockly.Blocks['move_jump_to'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Jump to x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Instantly move to position");
    }
};

// Grid movement blocks
Blockly.Blocks['grid_stop_if_no_keys'] = {
    init: function() {
        this.appendValueInput("GRID_SIZE")
            .setCheck("Number")
            .appendField("Stop if no arrow keys (grid:");
        this.appendDummyInput()
            .appendField(")");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Stop if no arrow keys are pressed (grid-based)");
    }
};

Blockly.Blocks['grid_check_keys_and_move'] = {
    init: function() {
        this.appendValueInput("GRID_SIZE")
            .setCheck("Number")
            .appendField("Check keys and move (grid:");
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("speed:");
        this.appendDummyInput()
            .appendField(")");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Check arrow keys and restart grid movement");
    }
};

Blockly.Blocks['grid_if_on_grid'] = {
    init: function() {
        this.appendValueInput("GRID_SIZE")
            .setCheck("Number")
            .appendField("If on grid (size:");
        this.appendDummyInput()
            .appendField(")");
        this.appendStatementInput("DO")
            .setCheck(null)
            .appendField("then");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Execute actions if on grid alignment");
    }
};

// ============ PHYSICS BLOCKS ============
Blockly.Blocks['set_gravity'] = {
    init: function() {
        this.appendValueInput("DIRECTION")
            .setCheck("Number")
            .appendField("Set gravity direction:");
        this.appendValueInput("STRENGTH")
            .setCheck("Number")
            .appendField("strength:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Apply gravity to this instance");
    }
};

Blockly.Blocks['set_friction'] = {
    init: function() {
        this.appendValueInput("FRICTION")
            .setCheck("Number")
            .appendField("Set friction to");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Set movement friction");
    }
};

Blockly.Blocks['reverse_horizontal'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Reverse horizontal movement");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Reverse horizontal direction");
    }
};

Blockly.Blocks['reverse_vertical'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Reverse vertical movement");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Reverse vertical direction");
    }
};

Blockly.Blocks['wrap_around_room'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Wrap around room")
            .appendField(new Blockly.FieldCheckbox("TRUE"), "HORIZONTAL")
            .appendField("horizontal")
            .appendField(new Blockly.FieldCheckbox("FALSE"), "VERTICAL")
            .appendField("vertical");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5C81A6");
        this.setTooltip("Wrap instance to opposite side when leaving room boundaries");
    }
};

// ============================================================================
// TIMING BLOCKS
// ============================================================================

Blockly.Blocks['set_alarm'] = {
    init: function() {
        this.appendValueInput("STEPS")
            .setCheck("Number")
            .appendField("Set alarm")
            .appendField(new Blockly.FieldDropdown([
                ["0", "0"], ["1", "1"], ["2", "2"], ["3", "3"],
                ["4", "4"], ["5", "5"], ["6", "6"], ["7", "7"],
                ["8", "8"], ["9", "9"], ["10", "10"], ["11", "11"]
            ]), "ALARM_NUM")
            .appendField("to");
        this.appendDummyInput()
            .appendField("steps");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#FF6B6B");
        this.setTooltip("Set an alarm to trigger after specified steps");
    }
};

// ============================================================================
// DRAWING BLOCKS
// ============================================================================

Blockly.Blocks['draw_text'] = {
    init: function() {
        this.appendValueInput("TEXT")
            .setCheck("String")
            .appendField("Draw text");
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("at x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Draw text on screen");
    }
};

Blockly.Blocks['draw_rectangle'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Draw rectangle at x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.appendValueInput("WIDTH")
            .setCheck("Number")
            .appendField("width:");
        this.appendValueInput("HEIGHT")
            .setCheck("Number")
            .appendField("height:");
        this.appendValueInput("COLOR")
            .setCheck("String")
            .appendField("color:");
        this.setInputsInline(false);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Draw a filled rectangle");
    }
};

Blockly.Blocks['draw_circle'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Draw circle at x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.appendValueInput("RADIUS")
            .setCheck("Number")
            .appendField("radius:");
        this.appendValueInput("COLOR")
            .setCheck("String")
            .appendField("color:");
        this.setInputsInline(false);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Draw a filled circle");
    }
};

Blockly.Blocks['set_sprite'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Set sprite to")
            .appendField(new Blockly.FieldDropdown([
                ["<self> (current)", "<self>"],
                ["other...", "other"]
            ], this.validateSprite.bind(this)), "SPRITE_MODE");
        this.appendDummyInput("SPRITE_NAME_INPUT")
            .appendField(new Blockly.FieldTextInput("spr_player"), "SPRITE");
        this.appendValueInput("SUBIMAGE")
            .setCheck("Number")
            .appendField("frame:");
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("speed:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Change the sprite or modify current sprite animation. Use <self> to modify the current sprite's animation.");
        // Hide sprite name input initially since default is <self>
        this.getInput("SPRITE_NAME_INPUT").setVisible(false);
    },
    validateSprite: function(newValue) {
        var spriteInput = this.getInput("SPRITE_NAME_INPUT");
        if (spriteInput) {
            spriteInput.setVisible(newValue === "other");
        }
        return newValue;
    }
};

Blockly.Blocks['set_alpha'] = {
    init: function() {
        this.appendValueInput("ALPHA")
            .setCheck("Number")
            .appendField("Set transparency to");
        this.appendDummyInput()
            .appendField("(0-1)");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Set sprite transparency (0=invisible, 1=solid)");
    }
};

// ============================================================================
// SCORE/LIVES/HEALTH BLOCKS
// ============================================================================

Blockly.Blocks['score_set'] = {
    init: function() {
        this.appendValueInput("VALUE")
            .setCheck("Number")
            .appendField("Set score to");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Set the score");
    }
};

Blockly.Blocks['score_add'] = {
    init: function() {
        this.appendValueInput("VALUE")
            .setCheck("Number")
            .appendField("Add to score");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Add or subtract from score");
    }
};

Blockly.Blocks['lives_set'] = {
    init: function() {
        this.appendValueInput("VALUE")
            .setCheck("Number")
            .appendField("Set lives to");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Set the number of lives");
    }
};

Blockly.Blocks['lives_add'] = {
    init: function() {
        this.appendValueInput("VALUE")
            .setCheck("Number")
            .appendField("Add to lives");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Add or subtract lives");
    }
};

Blockly.Blocks['health_set'] = {
    init: function() {
        this.appendValueInput("VALUE")
            .setCheck("Number")
            .appendField("Set health to");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Set the health");
    }
};

Blockly.Blocks['health_add'] = {
    init: function() {
        this.appendValueInput("VALUE")
            .setCheck("Number")
            .appendField("Add to health");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Add or subtract health");
    }
};

Blockly.Blocks['draw_score'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Draw score at x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Display the score");
    }
};

Blockly.Blocks['draw_lives'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Draw lives at x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Display lives as icons");
    }
};

Blockly.Blocks['draw_health_bar'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Draw health bar at x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.appendValueInput("WIDTH")
            .setCheck("Number")
            .appendField("width:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#5CA65C");
        this.setTooltip("Draw a health bar");
    }
};

// ============================================================================
// INSTANCE BLOCKS
// ============================================================================

Blockly.Blocks['instance_destroy'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Destroy this instance");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A65C81");
        this.setTooltip("Destroy the current instance");
    }
};

Blockly.Blocks['instance_destroy_other'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Destroy other instance");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A65C81");
        this.setTooltip("Destroy the colliding instance");
    }
};

Blockly.Blocks['instance_create'] = {
    init: function() {
        this.appendValueInput("X")
            .setCheck("Number")
            .appendField("Create")
            .appendField(new Blockly.FieldTextInput("obj_bullet"), "OBJECT")
            .appendField("at x:");
        this.appendValueInput("Y")
            .setCheck("Number")
            .appendField("y:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A65C81");
        this.setTooltip("Create a new instance");
    }
};

// ============================================================================
// ROOM BLOCKS
// ============================================================================

Blockly.Blocks['room_goto_next'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Go to next room");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A6745C");
        this.setTooltip("Go to the next room");
    }
};

Blockly.Blocks['room_restart'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Restart room");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A6745C");
        this.setTooltip("Restart the current room");
    }
};

Blockly.Blocks['room_goto'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Go to room")
            .appendField(new Blockly.FieldTextInput("room0"), "ROOM");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A6745C");
        this.setTooltip("Go to a specific room");
    }
};

Blockly.Blocks['room_goto_previous'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Go to previous room");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A6745C");
        this.setTooltip("Go to the previous room");
    }
};

Blockly.Blocks['room_if_next_exists'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If next room exists");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A6745C");
        this.setTooltip("Execute actions only if there is a next room");
    }
};

Blockly.Blocks['room_if_previous_exists'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If previous room exists");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#A6745C");
        this.setTooltip("Execute actions only if there is a previous room");
    }
};

// ============================================================================
// VALUE BLOCKS
// ============================================================================

Blockly.Blocks['value_x'] = {
    init: function() {
        this.appendDummyInput().appendField("x position");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get x position");
    }
};

Blockly.Blocks['value_y'] = {
    init: function() {
        this.appendDummyInput().appendField("y position");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get y position");
    }
};

Blockly.Blocks['value_hspeed'] = {
    init: function() {
        this.appendDummyInput().appendField("horizontal speed");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get horizontal speed");
    }
};

Blockly.Blocks['value_vspeed'] = {
    init: function() {
        this.appendDummyInput().appendField("vertical speed");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get vertical speed");
    }
};

Blockly.Blocks['value_score'] = {
    init: function() {
        this.appendDummyInput().appendField("score");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get current score");
    }
};

Blockly.Blocks['value_lives'] = {
    init: function() {
        this.appendDummyInput().appendField("lives");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get current lives");
    }
};

Blockly.Blocks['value_health'] = {
    init: function() {
        this.appendDummyInput().appendField("health");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get current health");
    }
};

Blockly.Blocks['value_mouse_x'] = {
    init: function() {
        this.appendDummyInput().appendField("mouse x");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get mouse x position");
    }
};

Blockly.Blocks['value_mouse_y'] = {
    init: function() {
        this.appendDummyInput().appendField("mouse y");
        this.setOutput(true, "Number");
        this.setColour("#5C68A6");
        this.setTooltip("Get mouse y position");
    }
};

// ============================================================================
// SOUND BLOCKS
// ============================================================================

Blockly.Blocks['sound_play'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Play sound")
            .appendField(new Blockly.FieldTextInput("snd_jump"), "SOUND");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9966FF");
        this.setTooltip("Play a sound effect");
    }
};

Blockly.Blocks['music_play'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Play music")
            .appendField(new Blockly.FieldTextInput("bgm_main"), "MUSIC");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9966FF");
        this.setTooltip("Play background music");
    }
};

Blockly.Blocks['music_stop'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Stop music");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9966FF");
        this.setTooltip("Stop background music");
    }
};

// ============================================================================
// OUTPUT BLOCKS
// ============================================================================

Blockly.Blocks['output_message'] = {
    init: function() {
        this.appendValueInput("MESSAGE")
            .setCheck("String")
            .appendField("Show message");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#745CA6");
        this.setTooltip("Show a message");
    }
};

// ============ EXECUTE CODE BLOCK ============
Blockly.Blocks['execute_code'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Execute Python code:");
        this.appendDummyInput()
            .appendField(new Blockly.FieldMultilineInput("# Write your Python code here\n"), "CODE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#4A90D9");  // Blue color for code blocks
        this.setTooltip("Execute custom Python code");
    }
};
