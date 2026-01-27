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

            // Handle keyboard events with nested format
            // Output: {"keyboard": {"right": {"actions": [...]}}}
            if (eventType.subtype && (eventType.event === 'keyboard' || eventType.event === 'keyboard_press' || eventType.event === 'keyboard_release')) {
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
        case 'event_alarm': return {event: 'alarm_' + block.getFieldValue('ALARM_NUM')};
        case 'event_keyboard_nokey': return {event: 'keyboard', subtype: 'nokey'};
        case 'event_keyboard_anykey': return {event: 'keyboard', subtype: 'anykey'};
        case 'event_keyboard_held': return {event: 'keyboard', subtype: block.getFieldValue('KEY')};
        case 'event_keyboard_press': return {event: 'keyboard_press', subtype: block.getFieldValue('KEY')};
        case 'event_keyboard_release': return {event: 'keyboard_release', subtype: block.getFieldValue('KEY')};
        case 'event_mouse': return {event: 'mouse_' + block.getFieldValue('BUTTON')};
        case 'event_collision': return {event: 'collision_with_' + block.getFieldValue('OBJECT')};
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

function generateActionCode(block) {
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
        case 'move_snap_to_grid':
            return {action: 'snap_to_grid', parameters: {grid_size: getInputValue(block, 'GRID_SIZE', 32)}};
        case 'move_jump_to':
            return {action: 'jump_to_position', parameters: {x: getInputValue(block, 'X', 0), y: getInputValue(block, 'Y', 0)}};
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
            return {action: 'draw_health_bar', parameters: {x1: getInputValue(block, 'X', 0), y1: getInputValue(block, 'Y', 0), x2: getInputValue(block, 'X', 0) + getInputValue(block, 'WIDTH', 100), y2: getInputValue(block, 'Y', 0) + 20}};
        case 'instance_destroy':
            return {action: 'destroy_instance', parameters: {target: 'self'}};
        case 'instance_destroy_other':
            return {action: 'destroy_instance', parameters: {target: 'other'}};
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
            return {action: 'if_next_room_exists', parameters: {then_actions: nextExistsActions}};
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
            return {action: 'if_previous_room_exists', parameters: {then_actions: prevExistsActions}};
        case 'sound_play':
            return {action: 'play_sound', parameters: {sound: block.getFieldValue('SOUND')}};
        case 'music_play':
            return {action: 'play_music', parameters: {music: block.getFieldValue('MUSIC')}};
        case 'music_stop':
            return {action: 'stop_music', parameters: {}};
        case 'output_message':
            return {action: 'show_message', parameters: {message: getInputValue(block, 'MESSAGE', '')}};
        case 'set_alarm':
            return {action: 'set_alarm', parameters: {alarm_num: parseInt(block.getFieldValue('ALARM_NUM')), steps: getInputValue(block, 'STEPS', 30)}};
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
            return {action: 'set_gravity', parameters: {direction: getInputValue(block, 'DIRECTION', 270), strength: getInputValue(block, 'STRENGTH', 0.5)}};
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
        case 'execute_code':
            return {action: 'execute_code', parameters: {code: block.getFieldValue('CODE') || ''}};

        // ============================================================================
        // THYMIO MOTOR ACTIONS
        // ============================================================================
        case 'thymio_set_motor_speed':
            return {type: 'thymio_set_motor_speed', parameters: {
                left_speed: getInputValue(block, 'LEFT_SPEED', 0),
                right_speed: getInputValue(block, 'RIGHT_SPEED', 0)
            }};
        case 'thymio_move_forward':
            return {type: 'thymio_move_forward', parameters: {speed: getInputValue(block, 'SPEED', 200)}};
        case 'thymio_move_backward':
            return {type: 'thymio_move_backward', parameters: {speed: getInputValue(block, 'SPEED', 200)}};
        case 'thymio_turn_left':
            return {type: 'thymio_turn_left', parameters: {speed: getInputValue(block, 'SPEED', 300)}};
        case 'thymio_turn_right':
            return {type: 'thymio_turn_right', parameters: {speed: getInputValue(block, 'SPEED', 300)}};
        case 'thymio_stop_motors':
            return {type: 'thymio_stop_motors', parameters: {}};

        // ============================================================================
        // THYMIO LED ACTIONS
        // ============================================================================
        case 'thymio_set_led_top':
            return {type: 'thymio_set_led_top', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_bottom_left':
            return {type: 'thymio_set_led_bottom_left', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_bottom_right':
            return {type: 'thymio_set_led_bottom_right', parameters: {
                red: getInputValue(block, 'RED', 0),
                green: getInputValue(block, 'GREEN', 0),
                blue: getInputValue(block, 'BLUE', 0)
            }};
        case 'thymio_set_led_circle':
            return {type: 'thymio_set_led_circle', parameters: {
                led_index: parseInt(block.getFieldValue('LED_INDEX')),
                intensity: getInputValue(block, 'INTENSITY', 32)
            }};
        case 'thymio_set_led_circle_all':
            return {type: 'thymio_set_led_circle_all', parameters: {
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
            return {type: 'thymio_leds_off', parameters: {}};

        // ============================================================================
        // THYMIO SOUND ACTIONS
        // ============================================================================
        case 'thymio_play_tone':
            return {type: 'thymio_play_tone', parameters: {
                frequency: getInputValue(block, 'FREQUENCY', 440),
                duration: getInputValue(block, 'DURATION', 60)
            }};
        case 'thymio_play_system_sound':
            return {type: 'thymio_play_system_sound', parameters: {
                sound_id: parseInt(block.getFieldValue('SOUND_ID'))
            }};
        case 'thymio_stop_sound':
            return {type: 'thymio_stop_sound', parameters: {}};

        // ============================================================================
        // THYMIO SENSOR READING ACTIONS
        // ============================================================================
        case 'thymio_read_proximity':
            return {type: 'thymio_read_proximity', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                variable: block.getFieldValue('VARIABLE')
            }};
        case 'thymio_read_ground':
            return {type: 'thymio_read_ground', parameters: {
                sensor_index: parseInt(block.getFieldValue('SENSOR_INDEX')),
                variable: block.getFieldValue('VARIABLE')
            }};
        case 'thymio_read_button':
            return {type: 'thymio_read_button', parameters: {
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
            return {type: 'thymio_if_proximity', parameters: {
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
            return {type: 'thymio_if_ground_dark', parameters: {
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
            return {type: 'thymio_if_ground_light', parameters: {
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
            return {type: 'thymio_if_button_pressed', parameters: {
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
            return {type: 'thymio_if_button_released', parameters: {
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
            return {type: 'thymio_if_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                comparison: block.getFieldValue('COMPARISON'),
                value: getInputValue(block, 'VALUE', 0)
            }, sub_actions: varSubActions};

        // ============================================================================
        // THYMIO TIMING ACTIONS
        // ============================================================================
        case 'thymio_set_timer_period':
            return {type: 'thymio_set_timer_period', parameters: {
                timer_id: parseInt(block.getFieldValue('TIMER_ID')),
                period: getInputValue(block, 'PERIOD', 1000)
            }};

        // ============================================================================
        // THYMIO VARIABLE ACTIONS
        // ============================================================================
        case 'thymio_set_variable':
            return {type: 'thymio_set_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                value: getInputValue(block, 'VALUE', 0)
            }};
        case 'thymio_increase_variable':
            return {type: 'thymio_increase_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                amount: getInputValue(block, 'AMOUNT', 1)
            }};
        case 'thymio_decrease_variable':
            return {type: 'thymio_decrease_variable', parameters: {
                variable: block.getFieldValue('VARIABLE'),
                amount: getInputValue(block, 'AMOUNT', 1)
            }};

        default:
            return null;
    }
}

function getInputValue(block, inputName, defaultValue) {
    var input = block.getInputTargetBlock(inputName);
    if (input) {
        if (input.type === 'math_number') {
            return parseFloat(input.getFieldValue('NUM')) || defaultValue;
        } else if (input.type === 'text') {
            return input.getFieldValue('TEXT') || defaultValue;
        } else if (input.type === 'value_x') {
            return 'self.x';
        } else if (input.type === 'value_y') {
            return 'self.y';
        } else if (input.type === 'value_score') {
            return 'game.score';
        } else if (input.type === 'value_lives') {
            return 'game.lives';
        } else if (input.type === 'value_health') {
            return 'game.health';
        }
    }
    return defaultValue;
}
