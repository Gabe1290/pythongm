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
            .appendField(new Blockly.FieldTextInput("# code here"), "CODE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#4A90D9");  // Blue color for code blocks
        this.setTooltip("Execute custom Python code");
    }
};

// ============================================================================
// THYMIO EVENT BLOCKS
// ============================================================================

Blockly.Blocks['event_thymio_button_forward'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio button Forward pressed");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when the forward button is pressed");
    }
};

Blockly.Blocks['event_thymio_button_backward'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio button Backward pressed");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when the backward button is pressed");
    }
};

Blockly.Blocks['event_thymio_button_left'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio button Left pressed");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when the left button is pressed");
    }
};

Blockly.Blocks['event_thymio_button_right'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio button Right pressed");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when the right button is pressed");
    }
};

Blockly.Blocks['event_thymio_button_center'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio button Center pressed");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when the center button is pressed");
    }
};

Blockly.Blocks['event_thymio_any_button'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When any Thymio button changes");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when any button state changes");
    }
};

Blockly.Blocks['event_thymio_proximity_update'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When proximity sensors update");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when proximity sensors update (10 Hz)");
    }
};

Blockly.Blocks['event_thymio_ground_update'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When ground sensors update");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when ground sensors update (10 Hz)");
    }
};

Blockly.Blocks['event_thymio_timer_0'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio timer 0 triggers");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when timer 0 period expires");
    }
};

Blockly.Blocks['event_thymio_timer_1'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio timer 1 triggers");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when timer 1 period expires");
    }
};

Blockly.Blocks['event_thymio_tap'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When Thymio is tapped/shaken");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when accelerometer detects a tap or shock");
    }
};

Blockly.Blocks['event_thymio_sound_detected'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When sound detected");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when microphone detects sound above threshold");
    }
};

Blockly.Blocks['event_thymio_sound_finished'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When sound playback finishes");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when sound playback completes");
    }
};

Blockly.Blocks['event_thymio_message_received'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("When message received");
        this.appendStatementInput("DO")
            .setCheck(null);
        this.setColour("#FF6B6B");
        this.setTooltip("Runs when IR communication receives message from another Thymio");
    }
};

// ============================================================================
// THYMIO MOTOR ACTION BLOCKS
// ============================================================================

Blockly.Blocks['thymio_set_motor_speed'] = {
    init: function() {
        this.appendValueInput("LEFT_SPEED")
            .setCheck("Number")
            .appendField("Set motor speeds - Left:");
        this.appendValueInput("RIGHT_SPEED")
            .setCheck("Number")
            .appendField("Right:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#27AE60");
        this.setTooltip("Set left and right motor speeds (-500 to 500)");
    }
};

Blockly.Blocks['thymio_move_forward'] = {
    init: function() {
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("Move forward at speed");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#27AE60");
        this.setTooltip("Move forward at specified speed (0-500)");
    }
};

Blockly.Blocks['thymio_move_backward'] = {
    init: function() {
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("Move backward at speed");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#27AE60");
        this.setTooltip("Move backward at specified speed (0-500)");
    }
};

Blockly.Blocks['thymio_turn_left'] = {
    init: function() {
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("Turn left at speed");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#27AE60");
        this.setTooltip("Turn left in place (0-500)");
    }
};

Blockly.Blocks['thymio_turn_right'] = {
    init: function() {
        this.appendValueInput("SPEED")
            .setCheck("Number")
            .appendField("Turn right at speed");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#27AE60");
        this.setTooltip("Turn right in place (0-500)");
    }
};

Blockly.Blocks['thymio_stop_motors'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Stop motors");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#27AE60");
        this.setTooltip("Stop both motors");
    }
};

// ============================================================================
// THYMIO LED ACTION BLOCKS
// ============================================================================

Blockly.Blocks['thymio_set_led_top'] = {
    init: function() {
        this.appendValueInput("RED")
            .setCheck("Number")
            .appendField("Set top LED - Red:");
        this.appendValueInput("GREEN")
            .setCheck("Number")
            .appendField("Green:");
        this.appendValueInput("BLUE")
            .setCheck("Number")
            .appendField("Blue:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F1C40F");
        this.setTooltip("Set top RGB LED color (0-32 for each channel)");
    }
};

Blockly.Blocks['thymio_set_led_bottom_left'] = {
    init: function() {
        this.appendValueInput("RED")
            .setCheck("Number")
            .appendField("Set bottom left LED - Red:");
        this.appendValueInput("GREEN")
            .setCheck("Number")
            .appendField("Green:");
        this.appendValueInput("BLUE")
            .setCheck("Number")
            .appendField("Blue:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F1C40F");
        this.setTooltip("Set bottom left RGB LED color (0-32 for each channel)");
    }
};

Blockly.Blocks['thymio_set_led_bottom_right'] = {
    init: function() {
        this.appendValueInput("RED")
            .setCheck("Number")
            .appendField("Set bottom right LED - Red:");
        this.appendValueInput("GREEN")
            .setCheck("Number")
            .appendField("Green:");
        this.appendValueInput("BLUE")
            .setCheck("Number")
            .appendField("Blue:");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F1C40F");
        this.setTooltip("Set bottom right RGB LED color (0-32 for each channel)");
    }
};

Blockly.Blocks['thymio_set_led_circle'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Set circle LED")
            .appendField(new Blockly.FieldDropdown([
                ["0 - Front", "0"],
                ["1", "1"],
                ["2", "2"],
                ["3 - Right", "3"],
                ["4 - Back", "4"],
                ["5", "5"],
                ["6", "6"],
                ["7 - Left", "7"]
            ]), "LED_INDEX");
        this.appendValueInput("INTENSITY")
            .setCheck("Number")
            .appendField("to intensity");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F1C40F");
        this.setTooltip("Set one of the 8 circle LEDs (0-32)");
    }
};

Blockly.Blocks['thymio_set_led_circle_all'] = {
    init: function() {
        this.appendValueInput("LED0")
            .setCheck("Number")
            .appendField("Set all circle LEDs - 0:");
        this.appendValueInput("LED1")
            .setCheck("Number")
            .appendField("1:");
        this.appendValueInput("LED2")
            .setCheck("Number")
            .appendField("2:");
        this.appendValueInput("LED3")
            .setCheck("Number")
            .appendField("3:");
        this.appendValueInput("LED4")
            .setCheck("Number")
            .appendField("4:");
        this.appendValueInput("LED5")
            .setCheck("Number")
            .appendField("5:");
        this.appendValueInput("LED6")
            .setCheck("Number")
            .appendField("6:");
        this.appendValueInput("LED7")
            .setCheck("Number")
            .appendField("7:");
        this.setInputsInline(false);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F1C40F");
        this.setTooltip("Set all 8 circle LEDs at once (0-32 each)");
    }
};

Blockly.Blocks['thymio_leds_off'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Turn off all LEDs");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#F1C40F");
        this.setTooltip("Turn off all LEDs");
    }
};

// ============================================================================
// THYMIO SOUND ACTION BLOCKS
// ============================================================================

Blockly.Blocks['thymio_play_tone'] = {
    init: function() {
        this.appendValueInput("FREQUENCY")
            .setCheck("Number")
            .appendField("Play tone at frequency");
        this.appendValueInput("DURATION")
            .setCheck("Number")
            .appendField("Hz for");
        this.appendDummyInput()
            .appendField("sixtieths of second");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Play a tone (frequency in Hz, duration in 1/60 second units)");
    }
};

Blockly.Blocks['thymio_play_system_sound'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Play system sound")
            .appendField(new Blockly.FieldDropdown([
                ["0 - Startup", "0"],
                ["1 - Shutdown", "1"],
                ["2 - Arrow", "2"],
                ["3 - Central", "3"],
                ["4 - Free Fall", "4"],
                ["5 - Collision", "5"],
                ["6 - Target Friendly", "6"],
                ["7 - Target Detected", "7"]
            ]), "SOUND_ID");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Play a built-in system sound");
    }
};

Blockly.Blocks['thymio_stop_sound'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Stop sound");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#9B59B6");
        this.setTooltip("Stop currently playing sound");
    }
};

// ============================================================================
// THYMIO SENSOR READING ACTION BLOCKS
// ============================================================================

Blockly.Blocks['thymio_read_proximity'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Read proximity sensor")
            .appendField(new Blockly.FieldDropdown([
                ["0 - Front Left Far", "0"],
                ["1 - Front Left", "1"],
                ["2 - Front Center", "2"],
                ["3 - Front Right", "3"],
                ["4 - Front Right Far", "4"],
                ["5 - Back Left", "5"],
                ["6 - Back Right", "6"]
            ]), "SENSOR_INDEX");
        this.appendDummyInput()
            .appendField("into variable")
            .appendField(new Blockly.FieldTextInput("prox_value"), "VARIABLE");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#3498DB");
        this.setTooltip("Read proximity sensor value (0-4000) into variable");
    }
};

Blockly.Blocks['thymio_read_ground'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Read ground sensor")
            .appendField(new Blockly.FieldDropdown([
                ["0 - Left", "0"],
                ["1 - Right", "1"]
            ]), "SENSOR_INDEX");
        this.appendDummyInput()
            .appendField("into variable")
            .appendField(new Blockly.FieldTextInput("ground_value"), "VARIABLE");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#3498DB");
        this.setTooltip("Read ground sensor value into variable");
    }
};

Blockly.Blocks['thymio_read_button'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Read button")
            .appendField(new Blockly.FieldDropdown([
                ["forward", "forward"],
                ["backward", "backward"],
                ["left", "left"],
                ["right", "right"],
                ["center", "center"]
            ]), "BUTTON");
        this.appendDummyInput()
            .appendField("into variable")
            .appendField(new Blockly.FieldTextInput("button_state"), "VARIABLE");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#3498DB");
        this.setTooltip("Read button state (0=released, 1=pressed) into variable");
    }
};

// ============================================================================
// THYMIO CONDITION ACTION BLOCKS
// ============================================================================

Blockly.Blocks['thymio_if_proximity'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If proximity sensor")
            .appendField(new Blockly.FieldDropdown([
                ["0 - Front Left Far", "0"],
                ["1 - Front Left", "1"],
                ["2 - Front Center", "2"],
                ["3 - Front Right", "3"],
                ["4 - Front Right Far", "4"],
                ["5 - Back Left", "5"],
                ["6 - Back Right", "6"]
            ]), "SENSOR_INDEX")
            .appendField(new Blockly.FieldDropdown([
                [">", ">"],
                [">=", ">="],
                ["<", "<"],
                ["<=", "<="],
                ["==", "=="],
                ["!=", "!="]
            ]), "COMPARISON");
        this.appendValueInput("THRESHOLD")
            .setCheck("Number");
        this.appendStatementInput("DO")
            .setCheck(null)
            .appendField("then");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#E67E22");
        this.setTooltip("Execute actions if proximity sensor matches condition (0-4000)");
    }
};

Blockly.Blocks['thymio_if_ground_dark'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If ground sensor")
            .appendField(new Blockly.FieldDropdown([
                ["0 - Left", "0"],
                ["1 - Right", "1"]
            ]), "SENSOR_INDEX")
            .appendField("is dark (below");
        this.appendValueInput("THRESHOLD")
            .setCheck("Number");
        this.appendDummyInput()
            .appendField(")");
        this.appendStatementInput("DO")
            .setCheck(null)
            .appendField("then");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#E67E22");
        this.setTooltip("Execute actions if ground sensor detects dark surface");
    }
};

Blockly.Blocks['thymio_if_ground_light'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If ground sensor")
            .appendField(new Blockly.FieldDropdown([
                ["0 - Left", "0"],
                ["1 - Right", "1"]
            ]), "SENSOR_INDEX")
            .appendField("is light (above");
        this.appendValueInput("THRESHOLD")
            .setCheck("Number");
        this.appendDummyInput()
            .appendField(")");
        this.appendStatementInput("DO")
            .setCheck(null)
            .appendField("then");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#E67E22");
        this.setTooltip("Execute actions if ground sensor detects light surface");
    }
};

Blockly.Blocks['thymio_if_button_pressed'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If button")
            .appendField(new Blockly.FieldDropdown([
                ["forward", "forward"],
                ["backward", "backward"],
                ["left", "left"],
                ["right", "right"],
                ["center", "center"]
            ]), "BUTTON")
            .appendField("is pressed");
        this.appendStatementInput("DO")
            .setCheck(null)
            .appendField("then");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#E67E22");
        this.setTooltip("Execute actions if button is currently pressed");
    }
};

Blockly.Blocks['thymio_if_button_released'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If button")
            .appendField(new Blockly.FieldDropdown([
                ["forward", "forward"],
                ["backward", "backward"],
                ["left", "left"],
                ["right", "right"],
                ["center", "center"]
            ]), "BUTTON")
            .appendField("is released");
        this.appendStatementInput("DO")
            .setCheck(null)
            .appendField("then");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#E67E22");
        this.setTooltip("Execute actions if button is currently released");
    }
};

Blockly.Blocks['thymio_if_variable'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("If variable")
            .appendField(new Blockly.FieldTextInput("state"), "VARIABLE")
            .appendField(new Blockly.FieldDropdown([
                ["==", "=="],
                ["!=", "!="],
                ["<", "<"],
                ["<=", "<="],
                [">", ">"],
                [">=", ">="]
            ]), "COMPARISON");
        this.appendValueInput("VALUE")
            .setCheck("Number");
        this.appendStatementInput("DO")
            .setCheck(null)
            .appendField("then");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#E67E22");
        this.setTooltip("Execute actions if variable matches condition");
    }
};

// ============================================================================
// THYMIO TIMING ACTION BLOCKS
// ============================================================================

Blockly.Blocks['thymio_set_timer_period'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Set Thymio timer")
            .appendField(new Blockly.FieldDropdown([
                ["0", "0"],
                ["1", "1"]
            ]), "TIMER_ID");
        this.appendValueInput("PERIOD")
            .setCheck("Number")
            .appendField("period to");
        this.appendDummyInput()
            .appendField("ms");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#FF6B6B");
        this.setTooltip("Set timer period in milliseconds");
    }
};

// ============================================================================
// THYMIO VARIABLE ACTION BLOCKS
// ============================================================================

Blockly.Blocks['thymio_set_variable'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Set Thymio variable")
            .appendField(new Blockly.FieldTextInput("state"), "VARIABLE");
        this.appendValueInput("VALUE")
            .setCheck("Number")
            .appendField("to");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#2ECC71");
        this.setTooltip("Set a Thymio variable (-32768 to 32767)");
    }
};

Blockly.Blocks['thymio_increase_variable'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Increase Thymio variable")
            .appendField(new Blockly.FieldTextInput("counter"), "VARIABLE");
        this.appendValueInput("AMOUNT")
            .setCheck("Number")
            .appendField("by");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#2ECC71");
        this.setTooltip("Increase a Thymio variable by amount");
    }
};

Blockly.Blocks['thymio_decrease_variable'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Decrease Thymio variable")
            .appendField(new Blockly.FieldTextInput("counter"), "VARIABLE");
        this.appendValueInput("AMOUNT")
            .setCheck("Number")
            .appendField("by");
        this.setInputsInline(true);
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#2ECC71");
        this.setTooltip("Decrease a Thymio variable by amount");
    }
};
