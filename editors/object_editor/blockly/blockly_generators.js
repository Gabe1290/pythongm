/**
 * PyGameMaker Blockly Code Generators
 * Converts blocks to PyGameMaker event/action format
 */

// ============================================================================
// CODE GENERATION FUNCTIONS
// ============================================================================

function generatePythonCode() {
    return generatePyGameMakerCode(workspace);
}

// Custom Python code generator for PyGameMaker
function generatePyGameMakerCode(workspace) {
    var events = {};
    var topBlocks = workspace.getTopBlocks(true);

    for (var i = 0; i < topBlocks.length; i++) {
        var block = topBlocks[i];
        var eventType = getEventType(block);
        if (eventType) {
            var code = generateBlockCode(block);

            // Handle keyboard and alarm events with nested format
            // Output: {"keyboard": {"right": {"actions": [...]}}} or {"alarm": {"alarm_0": {"actions": [...]}}}
            if (eventType.subtype && (eventType.event === 'keyboard' || eventType.event === 'keyboard_press' || eventType.event === 'keyboard_release' || eventType.event === 'alarm')) {
                if (!events[eventType.event]) {
                    events[eventType.event] = {};
                }
                // Create nested structure: keyboard -> key -> actions
                events[eventType.event][eventType.subtype] = {actions: code.actions || []};
            } else {
                // Regular event (create, step, draw, etc.)
                if (!events[eventType.event]) {
                    events[eventType.event] = {actions: []};
                }
                events[eventType.event].actions = events[eventType.event].actions.concat(code.actions || []);
            }
        }
    }

    return JSON.stringify(events, null, 2);
}

function getEventType(block) {
    switch (block.type) {
        case 'event_create': return {event: 'create'};
        case 'event_step': return {event: 'step'};
        case 'event_draw': return {event: 'draw'};
        case 'event_destroy': return {event: 'destroy'};
        case 'event_alarm': return {event: 'alarm', subtype: 'alarm_' + block.getFieldValue('ALARM_NUM')};
        case 'event_keyboard_nokey': return {event: 'keyboard', subtype: 'nokey'};
        case 'event_keyboard_anykey': return {event: 'keyboard', subtype: 'anykey'};
        case 'event_keyboard_held': return {event: 'keyboard', subtype: block.getFieldValue('KEY')};
        case 'event_keyboard_press': return {event: 'keyboard_press', subtype: block.getFieldValue('KEY')};
        case 'event_keyboard_release': return {event: 'keyboard_release', subtype: block.getFieldValue('KEY')};
        case 'event_mouse': return {event: 'mouse_' + block.getFieldValue('BUTTON')};
        case 'event_collision': return {event: 'collision_with_' + block.getFieldValue('OBJECT')};
        // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B3: the EVENT_NAME dropdown
        // value IS the real event name -- no lookup table to keep in sync.
        case 'event_other': return {event: block.getFieldValue('EVENT_NAME')};
        // Thymio events
        case 'event_thymio_button_forward': return {event: 'thymio_button_forward'};
        case 'event_thymio_button_backward': return {event: 'thymio_button_backward'};
        case 'event_thymio_button_left': return {event: 'thymio_button_left'};
        case 'event_thymio_button_right': return {event: 'thymio_button_right'};
        case 'event_thymio_button_center': return {event: 'thymio_button_center'};
        case 'event_thymio_any_button': return {event: 'thymio_any_button'};
        case 'event_thymio_proximity_update': return {event: 'thymio_proximity_update'};
        case 'event_thymio_ground_update': return {event: 'thymio_ground_update'};
        case 'event_thymio_timer_0': return {event: 'thymio_timer_0'};
        case 'event_thymio_timer_1': return {event: 'thymio_timer_1'};
        case 'event_thymio_tap': return {event: 'thymio_tap'};
        case 'event_thymio_sound_detected': return {event: 'thymio_sound_detected'};
        case 'event_thymio_sound_finished': return {event: 'thymio_sound_finished'};
        case 'event_thymio_message_received': return {event: 'thymio_message_received'};
        default: return null;
    }
}

function generateBlockCode(eventBlock) {
    var actions = [];
    var doBlock = eventBlock.getInputTargetBlock('DO');

    while (doBlock) {
        var action = generateActionCode(doBlock);
        if (action) {
            actions.push(action);
        }
        doBlock = doBlock.getNextBlock();
    }

    return {actions: actions};
}

// docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B4: draw_health_bar models x2/y2 as
// x1+width/y1+20 rather than storing them directly, computed with a plain JS
// `+`. That silently did STRING CONCATENATION the moment x1/y1 became an
// authored expression instead of always being a number (e.g. "self.x" + 100
// -> "self.x100", not a usable expression) -- a direct consequence of this
// same fix making a non-numeric X/Y possible at all. Real arithmetic when
// both sides are genuinely numbers (preserves the exact prior behavior);
// otherwise builds an expression string ActionExecutor._evaluate_expression
// can evaluate at runtime.
function addExpr(a, b) {
    if (typeof a === 'number' && typeof b === 'number') return a + b;
    return '(' + a + ') + (' + b + ')';
}

// parseScopedVariable: split a 'scope.name' user-typed variable expression
// into the (scope, name) pair the runtime's set_variable / test_variable
// actions expect. Accepted prefixes: 'self.' (or 'sel.'), 'global.', 'other.'.
// A bare name defaults to instance scope ("sel"), the runtime default.
function parseScopedVariable(raw) {
    var name = (raw || '').trim();
    var scope = 'sel';
    var dotIdx = name.indexOf('.');
    if (dotIdx > 0) {
        var prefix = name.substring(0, dotIdx).toLowerCase();
        var rest = name.substring(dotIdx + 1);
        if (prefix === 'self' || prefix === 'sel') { scope = 'sel'; name = rest; }
        else if (prefix === 'global') { scope = 'global'; name = rest; }
        else if (prefix === 'other')  { scope = 'other';  name = rest; }
    }
    return {name: name, scope: scope};
}

function generateActionCode(block) {
    var result = generateActionCodeInner(block);
    // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B5: merge back whatever the
    // LOAD side (createActionBlock, blockly_workspace.html) saw but this
    // block's own case below never mentions -- translations, an "applies
    // to" target, a colour, anything the hand-written block simply has no
    // field for. Keys the case DID explicitly set always win (the merge
    // order below puts them on top), since those reflect the block's real
    // current state, not the stale original.
    if (result && result.parameters && block.pygmExtraParams) {
        var merged = {};
        for (var k in block.pygmExtraParams) merged[k] = block.pygmExtraParams[k];
        for (var k2 in result.parameters) merged[k2] = result.parameters[k2];
        result.parameters = merged;
    }
    return result;
}

function generateActionCodeInner(block) {
    switch (block.type) {
        case 'move_set_hspeed':
            return {action: 'set_hspeed', parameters: {value: getInputValue(block, 'SPEED', 0)}};
        case 'move_set_vspeed':
            return {action: 'set_vspeed', parameters: {value: getInputValue(block, 'SPEED', 0)}};
        case 'move_stop':
            return {action: 'stop_movement', parameters: {}};
        case 'move_direction':
            var dir = block.getFieldValue('DIRECTION');
            var speed = getInputValue(block, 'SPEED', 4);
            // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B5: "stop" is a real
            // sentinel the runtime zeroes both speeds for (not "move at 0
            // degrees", i.e. right) -- falling through the degrees switch
            // below silently turned every authored "stop" into "move
            // right", a real behaviour change, not just a representation
            // difference.
            if (dir === 'stop') {
                return {action: 'start_moving_direction', parameters: {directions: 'stop', speed: speed}};
            }
            // Convert direction string to numeric degrees for game compatibility
            var directionDegrees;
            switch (dir) {
                case 'right': directionDegrees = 0; break;
                case 'up': directionDegrees = 90; break;
                case 'left': directionDegrees = 180; break;
                case 'down': directionDegrees = 270; break;
                default: directionDegrees = 0;
            }
            return {action: 'start_moving_direction', parameters: {directions: directionDegrees, speed: speed}};
        case 'move_towards':
            // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B7: the block existed with
            // no generator, so it saved nothing at all.
            return {action: 'move_towards_point', parameters: {
                x: getInputValue(block, 'X', 0),
                y: getInputValue(block, 'Y', 0),
                speed: getInputValue(block, 'SPEED', 4)
            }};
        case 'move_free':
            return {action: 'move_free', parameters: {
                direction: getInputValue(block, 'DIRECTION', 0),
                speed: getInputValue(block, 'SPEED', 4)
            }};
        case 'set_speed':
            return {action: 'set_speed', parameters: {speed: getInputValue(block, 'SPEED', 0)}};
        case 'set_direction':
            return {action: 'set_direction', parameters: {direction: getInputValue(block, 'DIRECTION', 0)}};
        case 'move_snap_to_grid':
            return {action: 'snap_to_grid', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32)}};
        case 'grid_move':
            return {action: 'move_grid', parameters: {direction: block.getFieldValue('DIRECTION') || 'right', grid_size: getInputValue(block, 'GRID_SIZE', 32)}};
        case 'move_jump_to':
            var relative = block.getFieldValue('RELATIVE') === 'TRUE';
            return {action: 'jump_to_position', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0), relative: relative}};
        case 'grid_stop_if_no_keys':
            return {action: 'stop_if_no_keys', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32)}};
        case 'grid_check_keys_and_move':
            return {action: 'check_keys_and_move', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32), speed: getInputValue(block, 'SPEED', 4)}};
        case 'grid_if_on_grid':
            // This is a wrapper action - collect inner actions
            var innerActions = [];
            var innerBlock = block.getInputTargetBlock('DO');
            while (innerBlock) {
                var innerAction = generateActionCode(innerBlock);
                if (innerAction) {
                    innerActions.push(innerAction);
                }
                innerBlock = innerBlock.getNextBlock();
            }
            return {action: 'if_on_grid', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32), then_actions: innerActions}};
        case 'score_set':
            return {action: 'set_score', parameters: {value: getInputValue(block, 'VALUE', 0), relative: false}};
        case 'score_add':
            return {action: 'set_score', parameters: {value: getInputValue(block, 'VALUE', 0), relative: true}};
        case 'lives_set':
            return {action: 'set_lives', parameters: {value: getInputValue(block, 'VALUE', 0), relative: false}};
        case 'lives_add':
            return {action: 'set_lives', parameters: {value: getInputValue(block, 'VALUE', 0), relative: true}};
        case 'health_set':
            return {action: 'set_health', parameters: {value: getInputValue(block, 'VALUE', 0), relative: false}};
        case 'health_add':
            return {action: 'set_health', parameters: {value: getInputValue(block, 'VALUE', 0), relative: true}};
        case 'draw_score':
            return {action: 'draw_score', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0), caption: "Score: "}};
        case 'draw_lives':
            return {action: 'draw_lives', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0)}};
        case 'draw_health_bar':
            var hbX = getInputValue(block, 'X', 0);
            var hbY = getInputValue(block, 'Y', 0);
            return {action: 'draw_health_bar', parameters: {
                x1: hbX, y1: hbY,
                x2: addExpr(hbX, getInputValue(block, 'WIDTH', 100)),
                y2: addExpr(hbY, getInputValue(block, 'HEIGHT', 20))}};
        case 'instance_destroy':
            return {action: 'destroy_instance', parameters: {target: 'self'}};
        case 'instance_destroy_other':
            return {action: 'destroy_instance', parameters: {target: 'other'}};
        case 'instance_destroy_object':
            return {action: 'destroy_instance', parameters: {
                target: 'object', target_object: block.getFieldValue('OBJECT')}};
        case 'instance_create':
            // Bug fix: this case was missing entirely, so every "Create
            // instance of X at x: ... y: ..." block silently produced no
            // action at all (generateBlockCode's switch fell through to
            // default: return null) -- e.g. Tutorial 2's star spawner
            // alarm event re-armed itself every frame but never actually
            // created a star. OBJECT is a plain typed FieldTextInput, not
            // a dropdown (see the block definition in blockly_blocks.js).
            return {action: 'create_instance', parameters: {
                object: block.getFieldValue('OBJECT'),
                x: getInputValue(block, 'X', 0),
                y: getInputValue(block, 'Y', 0)
            }};
        case 'exit_event':
            return {action: 'exit_event', parameters: {}};
        case 'if_condition':
            // Collect nested actions from the DO/ELSE slots (common to every
            // condition_type), then the fields for whichever type is
            // selected -- see blockly_blocks.js for the 8 types and why.
            var ifCondActions = [];
            var ifCondInner = block.getInputTargetBlock('DO');
            while (ifCondInner) {
                var ifCondAction = generateActionCode(ifCondInner);
                if (ifCondAction) {
                    ifCondActions.push(ifCondAction);
                }
                ifCondInner = ifCondInner.getNextBlock();
            }
            var ifCondElseActions = [];
            var ifCondElseInner = block.getInputTargetBlock('ELSE');
            while (ifCondElseInner) {
                var ifCondElseAction = generateActionCode(ifCondElseInner);
                if (ifCondElseAction) {
                    ifCondElseActions.push(ifCondElseAction);
                }
                ifCondElseInner = ifCondElseInner.getNextBlock();
            }
            var ifCondType = block.getFieldValue('CONDITION_TYPE');
            var ifCondParams = {
                condition_type: ifCondType,
                then_actions: ifCondActions,
                else_actions: ifCondElseActions
            };
            if (ifCondType === 'variable_compare') {
                ifCondParams.variable = block.getFieldValue('VAR_NAME');
                ifCondParams.operator = block.getFieldValue('VAR_OPERATOR');
                ifCondParams.value = block.getFieldValue('VAR_VALUE');
            } else if (ifCondType === 'position_check') {
                ifCondParams.check_type = block.getFieldValue('POS_CHECK_TYPE');
                ifCondParams.operator = block.getFieldValue('POS_OPERATOR');
                ifCondParams.value = block.getFieldValue('POS_VALUE');
            } else if (ifCondType === 'collision_check') {
                ifCondParams.object = block.getFieldValue('COLLISION_OBJECT');
                ifCondParams.offset_x = block.getFieldValue('COLLISION_OFFSET_X');
                ifCondParams.offset_y = block.getFieldValue('COLLISION_OFFSET_Y');
            } else if (ifCondType === 'key_pressed') {
                ifCondParams.key = block.getFieldValue('KEY_CHECK');
            } else if (ifCondType === 'mouse_check') {
                ifCondParams.check = block.getFieldValue('MOUSE_CHECK_FIELD');
            } else if (ifCondType === 'random_chance') {
                ifCondParams.chance = block.getFieldValue('CHANCE');
            } else if (ifCondType === 'expression') {
                ifCondParams.expression = block.getFieldValue('EXPRESSION');
            } else {
                // instance_count (and any unrecognized future type)
                ifCondParams.object_name = block.getFieldValue('OBJECT_NAME');
                ifCondParams.operator = block.getFieldValue('OPERATOR');
                ifCondParams.value = block.getFieldValue('VALUE');
            }
            return {action: 'if_condition', parameters: ifCondParams};
        case 'set_variable':
            // Split a leading 'self.' / 'global.' / 'other.' prefix into the
            // separate `scope` parameter the runtime expects. A bare name
            // defaults to instance scope ("sel"), matching the executor's default.
            var sv = parseScopedVariable(block.getFieldValue('VARIABLE'));
            return {action: 'set_variable', parameters: {
                variable: sv.name,
                scope: sv.scope,
                value: getInputValue(block, 'VALUE', 0),
                relative: false
            }};
        case 'test_variable':
            // Same nested-action pattern as if_condition: collect DO/ELSE
            // slot statements and let the runtime branch.
            var tvActions = [];
            var tvInner = block.getInputTargetBlock('DO');
            while (tvInner) {
                var tvAction = generateActionCode(tvInner);
                if (tvAction) {
                    tvActions.push(tvAction);
                }
                tvInner = tvInner.getNextBlock();
            }
            var tvElseActions = [];
            var tvElseInner = block.getInputTargetBlock('ELSE');
            while (tvElseInner) {
                var tvElseAction = generateActionCode(tvElseInner);
                if (tvElseAction) {
                    tvElseActions.push(tvElseAction);
                }
                tvElseInner = tvElseInner.getNextBlock();
            }
            var tv = parseScopedVariable(block.getFieldValue('VARIABLE'));
            return {action: 'test_variable', parameters: {
                variable: tv.name,
                scope: tv.scope,
                operation: block.getFieldValue('OPERATION'),
                value: getInputValue(block, 'VALUE', 0),
                then_actions: tvActions,
                else_actions: tvElseActions
            }};
        case 'test_expression':
            return {action: 'test_expression', parameters: {
                expression: getConditionValue(block, 'CONDITION'),
                then_actions: collectStatementActions(block, 'DO'),
                else_actions: collectStatementActions(block, 'ELSE')
            }};
        case 'room_goto_next':
            return {action: 'next_room', parameters: {}};
        case 'room_goto_previous':
            return {action: 'previous_room', parameters: {}};
        case 'room_restart':
            return {action: 'restart_room', parameters: {}};
        case 'room_goto':
            return {action: 'goto_room', parameters: {room_name: block.getFieldValue('ROOM')}};
        case 'room_if_next_exists':
            var nextExistsActions = [];
            var nextExistsBlock = block.getInputTargetBlock('DO');
            while (nextExistsBlock) {
                var nextExistsAction = generateActionCode(nextExistsBlock);
                if (nextExistsAction) {
                    nextExistsActions.push(nextExistsAction);
                }
                nextExistsBlock = nextExistsBlock.getNextBlock();
            }
            var nextExistsElseActions = [];
            var nextExistsElseBlock = block.getInputTargetBlock('ELSE');
            while (nextExistsElseBlock) {
                var nextExistsElseAction = generateActionCode(nextExistsElseBlock);
                if (nextExistsElseAction) {
                    nextExistsElseActions.push(nextExistsElseAction);
                }
                nextExistsElseBlock = nextExistsElseBlock.getNextBlock();
            }
            return {action: 'if_next_room_exists', parameters: {
                then_actions: nextExistsActions, else_actions: nextExistsElseActions
            }};
        case 'room_if_previous_exists':
            var prevExistsActions = [];
            var prevExistsBlock = block.getInputTargetBlock('DO');
            while (prevExistsBlock) {
                var prevExistsAction = generateActionCode(prevExistsBlock);
                if (prevExistsAction) {
                    prevExistsActions.push(prevExistsAction);
                }
                prevExistsBlock = prevExistsBlock.getNextBlock();
            }
            var prevExistsElseActions = [];
            var prevExistsElseBlock = block.getInputTargetBlock('ELSE');
            while (prevExistsElseBlock) {
                var prevExistsElseAction = generateActionCode(prevExistsElseBlock);
                if (prevExistsElseAction) {
                    prevExistsElseActions.push(prevExistsElseAction);
                }
                prevExistsElseBlock = prevExistsElseBlock.getNextBlock();
            }
            return {action: 'if_previous_room_exists', parameters: {
                then_actions: prevExistsActions, else_actions: prevExistsElseActions
            }};
        case 'sound_play':
            return {action: 'play_sound', parameters: {sound: block.getFieldValue('SOUND')}};
        case 'music_play':
            return {action: 'play_music', parameters: {music: block.getFieldValue('MUSIC')}};
        case 'music_stop':
            return {action: 'stop_music', parameters: {}};
        case 'output_message':
            return {action: 'show_message', parameters: {message: getInputValue(block, 'MESSAGE', '')}};
        case 'set_alarm':
            return {action: 'set_alarm', parameters: {alarm_number: parseInt(block.getFieldValue('ALARM_NUM')), steps: getInputValue(block, 'STEPS', 30)}};
        case 'draw_text':
            return {action: 'draw_text', parameters: {text: getInputValue(block, 'TEXT', ''), x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0)}};
        case 'draw_rectangle':
            return {action: 'draw_rectangle', parameters: {x1: getInputValue(block, 'X', 0), y1: getInputValue(block, 'Y', 0), x2: getInputValue(block, 'X', 0) + getInputValue(block, 'WIDTH', 100), y2: getInputValue(block, 'Y', 0) + getInputValue(block, 'HEIGHT', 100), color: getInputValue(block, 'COLOR', 'white')}};
        case 'draw_circle':
            return {action: 'draw_circle', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0), radius: getInputValue(block, 'RADIUS', 50), color: getInputValue(block, 'COLOR', 'white')}};
        case 'set_sprite':
            var spriteMode = block.getFieldValue('SPRITE_MODE');
            var spriteName = (spriteMode === '<self>') ? '<self>' : block.getFieldValue('SPRITE');
            return {action: 'set_sprite', parameters: {
                sprite: spriteName,
                subimage: getInputValue(block, 'SUBIMAGE', -1),
                speed: getInputValue(block, 'SPEED', -1)
            }};
        case 'set_alpha':
            return {action: 'set_alpha', parameters: {alpha: getInputValue(block, 'ALPHA', 1.0)}};
        case 'set_gravity':
            return {action: 'set_gravity', parameters: {direction: getInputValue(block, 'DIRECTION', 270), gravity: getInputValue(block, 'STRENGTH', 0.5)}};
        case 'set_friction':
            return {action: 'set_friction', parameters: {friction: getInputValue(block, 'FRICTION', 0)}};
        case 'reverse_horizontal':
            return {action: 'reverse_horizontal', parameters: {}};
        case 'reverse_vertical':
            return {action: 'reverse_vertical', parameters: {}};
        case 'wrap_around_room':
            return {action: 'wrap_around_room', parameters: {
                horizontal: block.getFieldValue('HORIZONTAL') === 'TRUE',
                vertical: block.getFieldValue('VERTICAL') === 'TRUE'
            }};
        case 'if_can_push':
            return {action: 'if_can_push', parameters: {
                direction: block.getFieldValue('DIRECTION') || 'facing',
                object_type: block.getFieldValue('OBJECT_TYPE') || 'box',
                then_action: block.getFieldValue('THEN_ACTION') || 'push_and_move',
                else_action: block.getFieldValue('ELSE_ACTION') || 'stop_movement'
            }};
        case 'execute_code':
            return {action: 'execute_code', parameters: {code: block.getFieldValue('CODE') || ''}};

        // ============================================================================
        // THYMIO MOTOR ACTIONS
        // ============================================================================
        case 'thymio_set_motor_speed':
            return {action: 'thymio_set_motor_speed', parameters: {
                left_speed: getInputValue(block, 'LEFT_SPEED', 0),
                right_speed: getInputValue(block, 'RIGHT_SPEED', 0)
            }};
        case 'thymio_move_forward':
            return {action: 'thymio_move_forward', parameters: {speed: getInputValue(block, 'SPEED', 200)}};
        case 'thymio_move_backward':
            return {action: 'thymio_move_backward', parameters: {speed: getInputValue(block, 'SPEED', 200)}};
        case 'thymio_turn_left':
            return {action: 'thymio_turn_left', parameters: {speed: getInputValue(block, 'SPEED', 300)}};
        case 'thymio_turn_right':
            return {action: 'thymio_turn_right', parameters: {speed: getInputValue(block, 'SPEED', 300)}};
        case 'thymio_stop_motors':
            return {action: 'thymio_stop_motors', parameters: {}};

        // ============================================================================
        // THYMIO LED ACTIONS
        // ============================================================================
        case 'thymio_set_led_top':
            return {action: 'thymio_set_led_top', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_bottom_left':
            return {action: 'thymio_set_led_bottom_left', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_bottom_right':
            return {action: 'thymio_set_led_bottom_right', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_circle':
            return {action: 'thymio_set_led_circle', parameters: {
                led_index: parseInt(block.getFieldValue('LED_INDEX')),
                intensity: getInputValue(block, 'INTENSITY', 32)
            }};
        case 'thymio_set_led_circle_all':
            return {action: 'thymio_set_led_circle_all', parameters: {
                led0: getInputValue(block, 'LED0', 0),
                led1: getInputValue(block, 'LED1', 0),
                led2: getInputValue(block, 'LED2', 0),
                led3: getInputValue(block, 'LED3', 0),
                led4: getInputValue(block, 'LED4', 0),
                led5: getInputValue(block, 'LED5', 0),
                led6: getInputValue(block, 'LED6', 0),
                led7: getInputValue(block, 'LED7', 0)
            }};
        case 'thymio_leds_off':
            return {action: 'thymio_leds_off', parameters: {}};

        // ============================================================================
        // THYMIO SOUND ACTIONS
        // ============================================================================
        case 'thymio_play_tone':
            return {action: 'thymio_play_tone', parameters: {
                frequency: getInputValue(block, 'FREQUENCY', 440),
                duration: getInputValue(block, 'DURATION', 60)
            }};
        case 'thymio_play_system_sound':
            return {action: 'thymio_play_system_sound', parameters: {
                sound_id: parseInt(block.getFieldValue('SOUND_ID'))
            }};
        case 'thymio_stop_sound':
            return {action: 'thymio_stop_sound', parameters: {}};

        // ============================================================================
        // THYMIO SENSOR READING ACTIONS
        // ============================================================================
        case 'thymio_read_proximity':
            return {action: 'thymio_read_proximity', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                variable: block.getFieldValue('VARIABLE')
            }};
        case 'thymio_read_ground':
            return {action: 'thymio_read_ground', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                variable: block.getFieldValue('VARIABLE')
            }};
        case 'thymio_read_button':
            return {action: 'thymio_read_button', parameters: {
                button: block.getFieldValue('BUTTON'),
                variable: block.getFieldValue('VARIABLE')
            }};

        // ============================================================================
        // THYMIO CONDITION ACTIONS (with sub_actions)
        // ============================================================================
        case 'thymio_if_proximity':
            var proxSubActions = [];
            var proxSubBlock = block.getInputTargetBlock('DO');
            while (proxSubBlock) {
                var proxAction = generateActionCode(proxSubBlock);
                if (proxAction) {
                    proxSubActions.push(proxAction);
                }
                proxSubBlock = proxSubBlock.getNextBlock();
            }
            return {action: 'thymio_if_proximity', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                comparison: block.getFieldValue('COMPARISON'),
                threshold: getInputValue(block, 'THRESHOLD', 2000)
            }, sub_actions: proxSubActions};

        case 'thymio_if_ground_dark':
            var groundDarkSubActions = [];
            var groundDarkSubBlock = block.getInputTargetBlock('DO');
            while (groundDarkSubBlock) {
                var groundDarkAction = generateActionCode(groundDarkSubBlock);
                if (groundDarkAction) {
                    groundDarkSubActions.push(groundDarkAction);
                }
                groundDarkSubBlock = groundDarkSubBlock.getNextBlock();
            }
            return {action: 'thymio_if_ground_dark', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                threshold: getInputValue(block, 'THRESHOLD', 300)
            }, sub_actions: groundDarkSubActions};

        case 'thymio_if_ground_light':
            var groundLightSubActions = [];
            var groundLightSubBlock = block.getInputTargetBlock('DO');
            while (groundLightSubBlock) {
                var groundLightAction = generateActionCode(groundLightSubBlock);
                if (groundLightAction) {
                    groundLightSubActions.push(groundLightAction);
                }
                groundLightSubBlock = groundLightSubBlock.getNextBlock();
            }
            return {action: 'thymio_if_ground_light', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                threshold: getInputValue(block, 'THRESHOLD', 300)
            }, sub_actions: groundLightSubActions};

        case 'thymio_if_button_pressed':
            var btnPressSubActions = [];
            var btnPressSubBlock = block.getInputTargetBlock('DO');
            while (btnPressSubBlock) {
                var btnPressAction = generateActionCode(btnPressSubBlock);
                if (btnPressAction) {
                    btnPressSubActions.push(btnPressAction);
                }
                btnPressSubBlock = btnPressSubBlock.getNextBlock();
            }
            return {action: 'thymio_if_button_pressed', parameters: {
                button: block.getFieldValue('BUTTON')
            }, sub_actions: btnPressSubActions};

        case 'thymio_if_button_released':
            var btnRelSubActions = [];
            var btnRelSubBlock = block.getInputTargetBlock('DO');
            while (btnRelSubBlock) {
                var btnRelAction = generateActionCode(btnRelSubBlock);
                if (btnRelAction) {
                    btnRelSubActions.push(btnRelAction);
                }
                btnRelSubBlock = btnRelSubBlock.getNextBlock();
            }
            return {action: 'thymio_if_button_released', parameters: {
                button: block.getFieldValue('BUTTON')
            }, sub_actions: btnRelSubActions};

        case 'thymio_if_variable':
            var varSubActions = [];
            var varSubBlock = block.getInputTargetBlock('DO');
            while (varSubBlock) {
                var varAction = generateActionCode(varSubBlock);
                if (varAction) {
                    varSubActions.push(varAction);
                }
                varSubBlock = varSubBlock.getNextBlock();
            }
            return {action: 'thymio_if_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                comparison: block.getFieldValue('COMPARISON'),
                value: getInputValue(block, 'VALUE', 0)
            }, sub_actions: varSubActions};

        // ============================================================================
        // THYMIO TIMING ACTIONS
        // ============================================================================
        case 'thymio_set_timer_period':
            return {action: 'thymio_set_timer_period', parameters: {
                timer_id: parseInt(block.getFieldValue('TIMER_ID')),
                period: getInputValue(block, 'PERIOD', 1000)
            }};

        // ============================================================================
        // THYMIO VARIABLE ACTIONS
        // ============================================================================
        case 'thymio_set_variable':
            return {action: 'thymio_set_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                value: getInputValue(block, 'VALUE', 0)
            }};
        case 'thymio_increase_variable':
            return {action: 'thymio_increase_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                amount: getInputValue(block, 'AMOUNT', 1)
            }};
        case 'thymio_decrease_variable':
            return {action: 'thymio_decrease_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                amount: getInputValue(block, 'AMOUNT', 1)
            }};

        default:
            return null;
    }
}

// Value blocks -> expression text (see getInputValue). Shared with the
// loader (blockly_workspace.html's connectNumberBlock), which turns these
// exact texts back into the same blocks.
var VALUE_BLOCK_EXPRESSIONS = {
    'value_x': 'self.x',
    'value_y': 'self.y',
    'value_hspeed': 'self.hspeed',
    'value_vspeed': 'self.vspeed',
    'value_mouse_x': 'self.mouse_x',
    'value_mouse_y': 'self.mouse_y',
    'value_score': 'score',
    'value_lives': 'lives',
    'value_health': 'health'
};

// Blockly's math_arithmetic OP field -> operator text. "**" (power) is
// valid on all three engines (Python eval on desktop/Kivy, JS on HTML5).
var MATH_ARITHMETIC_OPS = {
    'ADD': '+', 'MINUS': '-', 'MULTIPLY': '*', 'DIVIDE': '/', 'POWER': '**'
};

// The actions stacked in a statement input (DO / ELSE).
function collectStatementActions(block, inputName) {
    var actions = [];
    var inner = block.getInputTargetBlock(inputName);
    while (inner) {
        var action = generateActionCode(inner);
        if (action) actions.push(action);
        inner = inner.getNextBlock();
    }
    return actions;
}

// Blockly logic block -> Python-syntax condition text (audit B6c). Desktop's
// _eval_bool_expression evaluates it, HTML5's gmExpressionValue converts
// and/or/not/True/False, and Kivy emits it as Python. A number/value block
// is used as-is (non-zero = true), a text block verbatim (an authored
// expression), an empty slot is False.
var LOGIC_COMPARE_OPS = {'EQ': '==', 'NEQ': '!=', 'LT': '<', 'LTE': '<=', 'GT': '>', 'GTE': '>='};

function getConditionValue(block, inputName) {
    var input = block.getInputTargetBlock(inputName);
    if (!input) return 'False';
    switch (input.type) {
        case 'logic_boolean':
            return input.getFieldValue('BOOL') === 'TRUE' ? 'True' : 'False';
        case 'logic_negate':
            return '(not ' + getConditionValue(input, 'BOOL') + ')';
        case 'logic_operation':
            var join = input.getFieldValue('OP') === 'OR' ? ' or ' : ' and ';
            return '(' + getConditionValue(input, 'A') + join + getConditionValue(input, 'B') + ')';
        case 'logic_compare':
            var op = LOGIC_COMPARE_OPS[input.getFieldValue('OP')] || '==';
            return '(' + getConditionOperand(input, 'A') + ' ' + op + ' ' + getConditionOperand(input, 'B') + ')';
        case 'text':
            var text = input.getFieldValue('TEXT');
            return (text === null || text === undefined || text.trim() === '') ? 'False' : text;
        default:
            return String(getInputValue(block, inputName, 0));
    }
}

// A comparison side: a nested logic block compares as its truth value,
// anything else as the number/value expression getInputValue gives.
function getConditionOperand(block, inputName) {
    var input = block.getInputTargetBlock(inputName);
    if (input && /^logic_/.test(input.type)) return getConditionValue(block, inputName);
    return String(getInputValue(block, inputName, 0));
}

// Blockly's math_single OP field -> expression template ("%" = argument).
var MATH_SINGLE_TEMPLATES = {
    'ROOT': 'sqrt(%)', 'ABS': 'abs(%)', 'NEG': '(-(%))',
    'LN': 'ln(%)', 'LOG10': 'log10(%)', 'EXP': 'exp(%)', 'POW10': '(10 ** (%))'
};

function getInputValue(block, inputName, defaultValue) {
    var input = block.getInputTargetBlock(inputName);
    if (input) {
        if (input.type === 'math_number') {
            // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B1: `|| defaultValue`
            // treats 0 (and NaN/empty) alike, so typing 0 saved the block's
            // DEFAULT instead -- "set gravity 0" silently saved 0.5 (gravity
            // turned ON), "set sprite subimage 0" saved -1. Only fall back
            // to defaultValue when the field genuinely isn't a number.
            var num = parseFloat(input.getFieldValue('NUM'));
            return isNaN(num) ? defaultValue : num;
        } else if (input.type === 'text') {
            // Same pattern as above, applied to the empty string -- no
            // currently-registered caller passes a non-'' default for a
            // text field, so this has no observable effect yet, but it's
            // the identical bug shape and a future caller would hit it.
            var text = input.getFieldValue('TEXT');
            return (text === null || text === undefined) ? defaultValue : text;
        } else if (VALUE_BLOCK_EXPRESSIONS[input.type]) {
            // docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B6a/B15: spellings every
            // engine evaluates (desktop _parse_value, HTML5 gmExpressionValue
            // via parseNumParam, Kivy _num_code). "game.score" -- the old
            // spelling -- only ever worked nowhere on desktop.
            return VALUE_BLOCK_EXPRESSIONS[input.type];
        } else if (input.type === 'math_arithmetic') {
            var op = MATH_ARITHMETIC_OPS[input.getFieldValue('OP')] || '+';
            return '(' + getInputValue(input, 'A', 0) + ' ' + op + ' ' + getInputValue(input, 'B', 0) + ')';
        } else if (input.type === 'math_single') {
            // B6b: every op maps to a function all three engines provide
            // (runtime/gm_math.py, engine.js gmSafeMath, Kivy GameObject).
            var arg = getInputValue(input, 'NUM', 0);
            var tmpl = MATH_SINGLE_TEMPLATES[input.getFieldValue('OP')] || 'abs(%)';
            return tmpl.replace('%', arg);
        } else if (input.type === 'math_random_int') {
            // Blockly's standard Math category block ("random integer from
            // %1 to %2", FROM/TO value inputs) -- used by Tutorial 2's star
            // spawner to pick a random x. The three runtime engines (desktop
            // Python, HTML5, Kivy) only implement single-argument irandom(n)
            // (0..n inclusive), not a two-argument range function, so this
            // is synthesized from it rather than emitting a call to a
            // two-argument range function no target implements:
            // irandom(b-a)+a covers [a, b] inclusive, matching
            // math_random_int's own semantics exactly.
            var rangeFrom = getInputValue(input, 'FROM', 0);
            var rangeTo = getInputValue(input, 'TO', 0);
            return 'irandom((' + rangeTo + ') - (' + rangeFrom + ')) + (' + rangeFrom + ')';
        }
    }
    return defaultValue;
}
