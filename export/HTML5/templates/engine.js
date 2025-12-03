
// ============================================================================
// PyGameMaker HTML5 Engine - GAMEMAKER 7.0 COMPATIBLE
// ============================================================================

console.log('🎮 Game engine loading...');

class GameObject {
    constructor(name, x, y, data, objectData) {
        this.name = name;
        this.x = x;
        this.y = y;
        this.sprite = null;
        this.visible = data.visible !== false;
        this.solid = objectData ? (objectData.solid || false) : false;
        this.objectData = objectData;
        this.toDestroy = false;
        this.events = objectData ? (objectData.events || {}) : {};

        // GAMEMAKER 7.0: Movement properties with bidirectional sync
        this._hspeed = 0.0;
        this._vspeed = 0.0;
        this._speed = 0.0;
        this._direction = 0;
        this._friction = 0;
        this._gravity = 0;
        this._gravity_direction = 270;

        // GAMEMAKER 7.0: 12 alarm clocks per instance
        this.alarms = new Array(12).fill(-1);  // -1 = inactive, >= 0 = countdown

        // Depth-based rendering (lower = back, higher = front)
        this.depth = this.getDepthForObject(name);

        // Grid movement helpers
        this.targetX = null;
        this.targetY = null;
        this.gridMoveSpeed = 8;

        // Collision tracking
        this._collision_other = null;

        // Store game reference for later
        this._pendingCreateEvent = true;

        // Transformation properties
        this.rotation = data.rotation || 0;
        this.scale_x = data.scale_x || 1.0;
        this.scale_y = data.scale_y || 1.0;
    }

    // GAMEMAKER 7.0: Bidirectional speed/direction property synchronization
    get hspeed() { return this._hspeed; }
    set hspeed(value) {
        this._hspeed = value;
        this.syncSpeedDirectionFromComponents();
    }

    get vspeed() { return this._vspeed; }
    set vspeed(value) {
        this._vspeed = value;
        this.syncSpeedDirectionFromComponents();
    }

    get speed() { return this._speed; }
    set speed(value) {
        this._speed = value;
        this.syncComponentsFromSpeedDirection();
    }

    get direction() { return this._direction; }
    set direction(value) {
        this._direction = value;
        this.syncComponentsFromSpeedDirection();
    }

    get friction() { return this._friction; }
    set friction(value) { this._friction = value; }

    get gravity() { return this._gravity; }
    set gravity(value) { this._gravity = value; }

    get gravity_direction() { return this._gravity_direction; }
    set gravity_direction(value) { this._gravity_direction = value; }

    syncSpeedDirectionFromComponents() {
        // Update speed/direction when hspeed/vspeed change (GM 7.0 behavior)
        if (this._hspeed !== 0 || this._vspeed !== 0) {
            this._speed = Math.sqrt(this._hspeed**2 + this._vspeed**2);
            this._direction = Math.atan2(-this._vspeed, this._hspeed) * 180 / Math.PI;
        } else {
            this._speed = 0;
        }
    }

    syncComponentsFromSpeedDirection() {
        // Update hspeed/vspeed when speed/direction change (GM 7.0 behavior)
        if (this._speed !== 0) {
            const rad = this._direction * Math.PI / 180;
            this._hspeed = this._speed * Math.cos(rad);
            this._vspeed = -this._speed * Math.sin(rad);
        } else {
            this._hspeed = 0;
            this._vspeed = 0;
        }
    }

    getDepthForObject(name) {
        // Define rendering order layers
        if (name.includes('store') && !name.includes('box')) {
            return 0;  // Floor/store tiles at the bottom
        } else if (name.includes('ground') || name.includes('floor')) {
            return 0;
        } else if (name.includes('wall')) {
            return 5;
        } else if (name.includes('box')) {
            return 10;
        } else if (name.includes('soko') || name.includes('player')) {
            return 20;
        } else {
            return 10;
        }
    }

    // GAMEMAKER 7.0: Alarm processing
    processAlarms() {
        for (let i = 0; i < 12; i++) {
            if (this.alarms[i] > 0) {
                this.alarms[i]--;
                if (this.alarms[i] === 0) {
                    this.alarms[i] = -1;
                    this.triggerEvent(`alarm_${i}`);
                }
            }
        }
    }

    triggerEvent(eventName) {
        if (this.events && this.events[eventName]) {
            const event = this.events[eventName];
            const actions = event.actions || [];
            this.executeActions(actions, this._gameRef);
        }
    }

    // GAMEMAKER 7.0: Event handlers
    onBeginStep(game) {
        if (this.events && this.events.begin_step) {
            const event = this.events.begin_step;
            const actions = event.actions || [];
            this.executeActions(actions, game);
        }
    }

    onStep(game) {
        if (this.events && this.events.step) {
            const event = this.events.step;
            const actions = event.actions || [];
            this.executeActions(actions, game);
        }
    }

    onEndStep(game) {
        if (this.events && this.events.end_step) {
            const event = this.events.end_step;
            const actions = event.actions || [];
            this.executeActions(actions, game);
        }
    }

    onDraw(ctx) {
        if (this.events && this.events.draw) {
            const event = this.events.draw;
            const actions = event.actions || [];
            // Draw events would need special handling for graphics context
            // For now, just do normal rendering
        }
        this.render(ctx);
    }

    onKeyboardPress(key, game) {
        if (!this.events) return;

        // NEW: Handle keyboard_press events (fires once when key first pressed)
        if (this.events.keyboard_press) {
            this.handleKeyboardEvent(key, this.events.keyboard_press, game);
        }

        // OLD: Support legacy keyboard events
        if (this.events.keyboard) {
            const keyboardEvents = this.events.keyboard;
            const keyMap = {
                'ArrowLeft': ['left'],
                'ArrowRight': ['right'],
                'ArrowUp': ['up'],
                'ArrowDown': ['down']
            };

            const directions = keyMap[key];
            if (directions) {
                for (const dirName of directions) {
                    if (keyboardEvents[dirName] && keyboardEvents[dirName].actions) {
                        const actions = keyboardEvents[dirName].actions;
                        this.executeActions(actions, game);
                        break;
                    }
                }
            }
        }
    }

    onKeyboardHeld(key, game) {
        if (!this.events || !this.events.keyboard) return;

        // NEW: Handle keyboard events (fires continuously while key is held)
        this.handleKeyboardEvent(key, this.events.keyboard, game);
    }

    onKeyboardRelease(key, game) {
        if (!this.events || !this.events.keyboard_release) return;

        // NEW: Handle keyboard_release events (fires once when key is released)
        this.handleKeyboardEvent(key, this.events.keyboard_release, game);
    }

    onNoKey(game) {
        // Handle nokey event (fires when no arrow keys are pressed)
        if (!this.events || !this.events.keyboard || !this.events.keyboard.nokey) return;

        const nokeyEvent = this.events.keyboard.nokey;
        const actions = nokeyEvent.actions || [];
        this.executeActions(actions, game);
    }

    handleKeyboardEvent(key, eventData, game) {
        // Map browser keys to event key names
        const keyMap = {
            'ArrowLeft': 'LEFT',
            'ArrowRight': 'RIGHT',
            'ArrowUp': 'UP',
            'ArrowDown': 'DOWN',
            ' ': 'SPACE',
            'Enter': 'ENTER',
            'Escape': 'ESCAPE',
            'Backspace': 'BACKSPACE',
            'Tab': 'TAB',
            'Delete': 'DELETE'
        };

        // Handle letter keys (a-z)
        if (key.length === 1 && /[a-zA-Z]/.test(key)) {
            const upperKey = key.toUpperCase();
            if (eventData[upperKey] && eventData[upperKey].actions) {
                this.executeActions(eventData[upperKey].actions, game);
            }
            return;
        }

        // Handle number keys (0-9)
        if (key.length === 1 && /[0-9]/.test(key)) {
            if (eventData[key] && eventData[key].actions) {
                this.executeActions(eventData[key].actions, game);
            }
            return;
        }

        // Handle special keys
        const mappedKey = keyMap[key] || key;
        if (eventData[mappedKey] && eventData[mappedKey].actions) {
            this.executeActions(eventData[mappedKey].actions, game);
        }

        // Also try legacy lowercase format for arrow keys
        const legacyKey = mappedKey.toLowerCase();
        if (eventData[legacyKey] && eventData[legacyKey].actions) {
            this.executeActions(eventData[legacyKey].actions, game);
        }
    }

    triggerCreateEvent(game) {
        if (this._pendingCreateEvent && this.events && this.events.create) {
            const createEvent = this.events.create;
            const actions = createEvent.actions || [];
            this.executeActions(actions, game);
            this._pendingCreateEvent = false;
        }
    }

    // GAMEMAKER 7.0: Movement processing
    processMovement(game) {
        // Apply gravity (GM 7.0: adds to speed each step)
        if (this._gravity !== 0) {
            const gravRad = this._gravity_direction * Math.PI / 180;
            this._hspeed += this._gravity * Math.cos(gravRad);
            this._vspeed += -this._gravity * Math.sin(gravRad);
            this.syncSpeedDirectionFromComponents();
        }

        // Apply friction (GM 7.0: reduces speed towards zero)
        if (this._friction !== 0) {
            if (Math.abs(this._hspeed) > this._friction) {
                this._hspeed -= this._friction * Math.sign(this._hspeed);
            } else {
                this._hspeed = 0;
            }

            if (Math.abs(this._vspeed) > this._friction) {
                this._vspeed -= this._friction * Math.sign(this._vspeed);
            } else {
                this._vspeed = 0;
            }
            this.syncSpeedDirectionFromComponents();
        }

        // Handle grid-based movement
        if (this.targetX !== null && this.targetY !== null) {
            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < this.gridMoveSpeed) {
                this.x = this.targetX;
                this.y = this.targetY;
                this.targetX = null;
                this.targetY = null;
            } else {
                this.x += (dx / distance) * this.gridMoveSpeed;
                this.y += (dy / distance) * this.gridMoveSpeed;
            }
        }

        // Apply hspeed/vspeed
        if (this._hspeed !== 0 || this._vspeed !== 0) {
            let newX = this.x + this._hspeed;
            let newY = this.y + this._vspeed;

            // Check solid collision
            if (this.solid) {
                const canMove = !this.checkCollisionAt(newX, newY, game);
                if (canMove) {
                    this.x = newX;
                    this.y = newY;
                }
            } else {
                this.x = newX;
                this.y = newY;
            }
        }
    }

    /**
     * Execute an array of actions with block-based conditional support.
     * Handles if_xxx/else_block patterns where actions are sequential siblings.
     */
    executeActions(actions, game) {
        let i = 0;
        while (i < actions.length) {
            const action = actions[i];
            const actionType = action.action;
            const params = action.parameters || {};

            // Check if this is a conditional action
            if (actionType && actionType.startsWith('if_')) {
                // Check if this conditional uses NESTED then_actions/else_actions (legacy format)
                // If so, delegate to executeAction which handles nested format
                if (params.then_actions || params.else_actions) {
                    this.executeAction(action, game);
                    i++;
                    continue;
                }

                // Otherwise, use SEQUENTIAL block-based format (if_xxx, actions, else_block, actions)
                // Evaluate the condition
                const conditionResult = this.evaluateCondition(action, game);

                // Find the else_block position (if any) and end of block
                let elseIndex = -1;
                let endIndex = actions.length;

                for (let j = i + 1; j < actions.length; j++) {
                    const nextAction = actions[j].action;
                    if (nextAction === 'else_block' || nextAction === 'else_action') {
                        elseIndex = j;
                        break;
                    }
                    // If we hit another if_* at the same level, that's the end
                    if (nextAction && nextAction.startsWith('if_')) {
                        endIndex = j;
                        break;
                    }
                }

                if (conditionResult) {
                    // Condition is TRUE: execute actions from i+1 to elseIndex (or endIndex)
                    const trueEndIndex = elseIndex >= 0 ? elseIndex : endIndex;
                    for (let j = i + 1; j < trueEndIndex; j++) {
                        this.executeAction(actions[j], game);
                    }
                    // Skip past the else block content
                    if (elseIndex >= 0) {
                        i = endIndex;  // Jump to end
                    } else {
                        i = trueEndIndex;
                    }
                } else {
                    // Condition is FALSE: skip to else_block and execute from there
                    if (elseIndex >= 0) {
                        for (let j = elseIndex + 1; j < endIndex; j++) {
                            this.executeAction(actions[j], game);
                        }
                        i = endIndex;
                    } else {
                        // No else block, skip the whole if block
                        i = endIndex;
                    }
                }
            } else if (actionType === 'else_block' || actionType === 'else_action') {
                // Else blocks handled by if_* processing, skip if encountered standalone
                i++;
            } else {
                // Regular action, execute normally
                this.executeAction(action, game);
                i++;
            }
        }
    }

    /**
     * Evaluate a conditional action and return true/false.
     */
    evaluateCondition(action, game) {
        const actionType = action.action;
        const params = action.parameters || {};

        switch (actionType) {
            case 'if_next_room_exists':
                const roomNamesNext = Object.keys(game.rooms);
                const currentIdxNext = roomNamesNext.indexOf(game.currentRoom.name);
                return currentIdxNext >= 0 && currentIdxNext < roomNamesNext.length - 1;

            case 'if_previous_room_exists':
                const roomNamesPrev = Object.keys(game.rooms);
                const currentIdxPrev = roomNamesPrev.indexOf(game.currentRoom.name);
                return currentIdxPrev > 0;

            case 'if_on_grid':
                const checkGridSize = params.grid_size || 32;
                const nearestGridX = Math.round(this.x / checkGridSize) * checkGridSize;
                const nearestGridY = Math.round(this.y / checkGridSize) * checkGridSize;
                const gridTolerance = Math.max(Math.abs(this._hspeed), Math.abs(this._vspeed), 4) + 1;
                return Math.abs(this.x - nearestGridX) <= gridTolerance &&
                       Math.abs(this.y - nearestGridY) <= gridTolerance;

            case 'if_collision':
            case 'if_collision_at':
                // Check collision at specified position
                const checkX = params.x !== undefined ? params.x : this.x;
                const checkY = params.y !== undefined ? params.y : this.y;
                const targetObject = params.object;
                // Would need to check collisions at this position
                return false;  // Default to false for now

            case 'if_variable':
                // Compare a variable to a value
                const varName = params.variable;
                const compareValue = params.value;
                const op = params.operation || '==';
                const currentValue = this[varName];
                switch (op) {
                    case '==': return currentValue == compareValue;
                    case '!=': return currentValue != compareValue;
                    case '<': return currentValue < compareValue;
                    case '>': return currentValue > compareValue;
                    case '<=': return currentValue <= compareValue;
                    case '>=': return currentValue >= compareValue;
                    default: return currentValue == compareValue;
                }

            case 'if_question':
                // Show a yes/no dialog and return result
                const question = params.message || params.question || 'Yes or No?';
                return confirm(question);

            default:
                console.warn(`Unknown conditional action: ${actionType}`);
                return false;
        }
    }

    executeAction(action, game) {
        const actionType = action.action;
        const params = action.parameters || {};

        switch(actionType) {
            // GAMEMAKER 7.0: Movement actions
            case 'set_hspeed':
                this.hspeed = params.speed || params.value || 0;
                break;

            case 'set_vspeed':
                this.vspeed = params.speed || params.value || 0;
                break;

            case 'set_speed':
                this.speed = params.speed || params.value || 0;
                break;

            case 'set_direction':
                this.direction = params.direction || params.value || 0;
                break;

            case 'move_fixed':
                // GameMaker's 8-way movement
                const directions = params.directions || ['right'];
                const speed = params.speed || 4;
                const dirMap = {
                    'right': 0, 'up-right': 45, 'up': 90, 'up-left': 135,
                    'left': 180, 'down-left': 225, 'down': 270, 'down-right': 315,
                    'stop': -1
                };
                if (directions.includes('stop')) {
                    this.speed = 0;
                } else if (directions.length === 1) {
                    this.direction = dirMap[directions[0]] || 0;
                    this.speed = speed;
                } else {
                    // Random direction from multiple choices
                    const validDirs = directions.filter(d => d !== 'stop').map(d => dirMap[d] || 0);
                    this.direction = validDirs[Math.floor(Math.random() * validDirs.length)];
                    this.speed = speed;
                }
                break;

            case 'move_free':
                this.direction = params.direction || 0;
                this.speed = params.speed || 4;
                break;

            case 'move_towards':
                const targetX = params.x || 0;
                const targetY = params.y || 0;
                const moveSpeed = params.speed || 4;
                this.direction = Math.atan2(-(targetY - this.y), targetX - this.x) * 180 / Math.PI;
                this.speed = moveSpeed;
                break;

            case 'set_gravity':
                this.gravity_direction = params.direction || 270;
                this.gravity = params.gravity || 0.5;
                break;

            case 'set_friction':
                this.friction = params.friction || 0.1;
                break;

            case 'reverse_horizontal':
                this.hspeed = -this.hspeed;
                break;

            case 'reverse_vertical':
                this.vspeed = -this.vspeed;
                break;

            case 'stop_movement':
                this.hspeed = 0;
                this.vspeed = 0;
                this.speed = 0;
                this.targetX = null;
                this.targetY = null;
                // Snap to nearest grid position when stopping
                const stopGridSize = 32;
                this.x = Math.round(this.x / stopGridSize) * stopGridSize;
                this.y = Math.round(this.y / stopGridSize) * stopGridSize;
                break;

            // GAMEMAKER 7.0: Alarm actions
            case 'set_alarm':
                const alarmNum = params.alarm_number || 0;
                const steps = params.steps || 30;
                if (alarmNum >= 0 && alarmNum < 12) {
                    this.alarms[alarmNum] = steps;
                }
                break;

            // GAMEMAKER 7.0: Control actions
            case 'test_expression':
                const expr = params.expression || 'false';
                // Would need safe evaluation
                break;

            case 'check_empty':
            case 'check_collision':
                // Collision checking logic
                break;

            case 'repeat':
                const times = params.times || 1;
                const repeatActions = params.actions || [];
                for (let i = 0; i < times; i++) {
                    this.executeActions(repeatActions, game);
                }
                break;

            case 'exit_event':
                return; // Exit current event

            // Grid movement (existing)
            case 'grid_move':
            case 'move_grid':
                const dir = params.direction;
                const gridSize = params.grid_size || 32;

                let newX = this.x;
                let newY = this.y;
                let deltaX = 0;
                let deltaY = 0;

                switch(dir) {
                    case 'left': newX -= gridSize; deltaX = -gridSize; break;
                    case 'right': newX += gridSize; deltaX = gridSize; break;
                    case 'up': newY -= gridSize; deltaY = -gridSize; break;
                    case 'down': newY += gridSize; deltaY = gridSize; break;
                }

                const objectAtTarget = this.getObjectAt(newX, newY, game);

                if (objectAtTarget && objectAtTarget.name.includes('box')) {
                    const boxNewX = objectAtTarget.x + deltaX;
                    const boxNewY = objectAtTarget.y + deltaY;
                    const canPushBox = !objectAtTarget.checkCollisionAt(boxNewX, boxNewY, game);

                    if (canPushBox) {
                        objectAtTarget.targetX = boxNewX;
                        objectAtTarget.targetY = boxNewY;
                        this.targetX = newX;
                        this.targetY = newY;
                    }
                } else {
                    const canMove = !this.checkCollisionAt(newX, newY, game);
                    if (canMove) {
                        this.targetX = newX;
                        this.targetY = newY;
                    }
                }
                break;

            case 'snap_to_grid':
                const snapGridSize = params.grid_size || 32;
                this.x = Math.round(this.x / snapGridSize) * snapGridSize;
                this.y = Math.round(this.y / snapGridSize) * snapGridSize;
                break;

            case 'if_on_grid':
                const checkGridSize = params.grid_size || 32;
                // Use tolerance-based grid check (handles floating point positions)
                const nearestGridX = Math.round(this.x / checkGridSize) * checkGridSize;
                const nearestGridY = Math.round(this.y / checkGridSize) * checkGridSize;
                const gridTolerance = Math.max(Math.abs(this._hspeed), Math.abs(this._vspeed), 4) + 1;
                const isOnGrid = Math.abs(this.x - nearestGridX) <= gridTolerance &&
                                 Math.abs(this.y - nearestGridY) <= gridTolerance;

                if (isOnGrid) {
                    if (params.then_actions) {
                        this.executeActions(params.then_actions, game);
                    }
                } else if (params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'stop_if_no_keys':
                // Check if any arrow keys are currently pressed
                const arrowKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
                const anyArrowKeyPressed = arrowKeys.some(key => game.keys[key]);

                if (!anyArrowKeyPressed) {
                    // No arrow keys pressed - stop movement
                    this.hspeed = 0;
                    this.vspeed = 0;
                    this.speed = 0;
                    this.targetX = null;
                    this.targetY = null;
                }
                // If keys ARE pressed, do nothing (keep moving)
                break;

            case 'if_collision_at':
                let checkX = this.x;
                let checkY = this.y;

                if (params.x) {
                    const xExpr = params.x.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try { checkX = eval(xExpr); } catch(e) {}
                }

                if (params.y) {
                    const yExpr = params.y.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try { checkY = eval(yExpr); } catch(e) {}
                }

                const objectType = params.object_type || params.object_types;
                const targetObject = this.getObjectAt(checkX, checkY, game);

                let collisionFound = false;
                if (targetObject) {
                    if (objectType === 'solid' && targetObject.solid) {
                        collisionFound = true;
                    } else if (objectType === 'any' || targetObject.name === objectType ||
                        (Array.isArray(objectType) && objectType.includes(targetObject.name))) {
                        collisionFound = true;
                    }
                }

                if (collisionFound && params.then_actions) {
                    this.executeActions(params.then_actions, game);
                } else if (!collisionFound && params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'if_condition':
            case 'if_variable':
                // Variable checking logic (existing code)
                break;

            case 'destroy_instance':
                const target = params.target || 'self';
                if (target === 'other' && this._collision_other) {
                    this._collision_other.toDestroy = true;
                } else {
                    this.toDestroy = true;
                }
                break;

            case 'next_room':
                // Go to next room in the room order
                const roomNamesNext = Object.keys(game.rooms);
                const currentIndexNext = roomNamesNext.indexOf(game.currentRoom.name);
                if (currentIndexNext >= 0 && currentIndexNext < roomNamesNext.length - 1) {
                    const nextRoomName = roomNamesNext[currentIndexNext + 1];
                    game.changeRoom(nextRoomName);
                } else {
                    console.log('Already at last room');
                }
                break;

            case 'previous_room':
                // Go to previous room in the room order
                const roomNamesPrev = Object.keys(game.rooms);
                const currentIndexPrev = roomNamesPrev.indexOf(game.currentRoom.name);
                if (currentIndexPrev > 0) {
                    const prevRoomName = roomNamesPrev[currentIndexPrev - 1];
                    game.changeRoom(prevRoomName);
                } else {
                    console.log('Already at first room');
                }
                break;

            case 'restart_room':
                // Restart current room
                game.changeRoom(game.currentRoom.name);
                break;

            case 'change_room':
            case 'go_to_room':
                let roomName = params.room_name || params.room;

                if (roomName === '__next__') {
                    const roomNames = Object.keys(game.rooms);
                    const currentIndex = roomNames.indexOf(game.currentRoom.name);
                    if (currentIndex >= 0 && currentIndex < roomNames.length - 1) {
                        roomName = roomNames[currentIndex + 1];
                    } else {
                        return;
                    }
                } else if (roomName === '__previous__') {
                    const roomNames = Object.keys(game.rooms);
                    const currentIndex = roomNames.indexOf(game.currentRoom.name);
                    if (currentIndex > 0) {
                        roomName = roomNames[currentIndex - 1];
                    } else {
                        return;
                    }
                } else if (roomName === '__restart__') {
                    roomName = game.currentRoom.name;
                }

                if (roomName && game.rooms[roomName]) {
                    game.changeRoom(roomName);
                }
                break;

            case 'if_next_room_exists':
                // Note: Block-based if/else handling is done in executeActions()
                // This case handles legacy nested then_actions/else_actions format
                const roomNamesForNext = Object.keys(game.rooms);
                const currentIdxForNext = roomNamesForNext.indexOf(game.currentRoom.name);
                const nextRoomExists = currentIdxForNext >= 0 && currentIdxForNext < roomNamesForNext.length - 1;

                if (nextRoomExists && params.then_actions) {
                    this.executeActions(params.then_actions, game);
                } else if (!nextRoomExists && params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'if_previous_room_exists':
                // Note: Block-based if/else handling is done in executeActions()
                // This case handles legacy nested then_actions/else_actions format
                const roomNamesForPrev = Object.keys(game.rooms);
                const currentIdxForPrev = roomNamesForPrev.indexOf(game.currentRoom.name);
                const prevRoomExists = currentIdxForPrev > 0;

                if (prevRoomExists && params.then_actions) {
                    this.executeActions(params.then_actions, game);
                } else if (!prevRoomExists && params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'else_block':
            case 'else_action':
                // Else blocks are handled by their parent if_* actions
                // They should not be executed directly
                break;

            case 'display_message':
            case 'show_message':
                // Display a message dialog
                const message = params.message || params.text || '';
                if (message) {
                    // Stop movement and snap to grid before showing message
                    // This prevents the player from drifting off-grid during collision events
                    this.hspeed = 0;
                    this.vspeed = 0;
                    this.speed = 0;
                    const msgGridSize = 32;
                    this.x = Math.round(this.x / msgGridSize) * msgGridSize;
                    this.y = Math.round(this.y / msgGridSize) * msgGridSize;

                    // Also stop and snap the collision "other" object if applicable
                    if (this._collision_other) {
                        this._collision_other.hspeed = 0;
                        this._collision_other.vspeed = 0;
                        this._collision_other.speed = 0;
                        this._collision_other.x = Math.round(this._collision_other.x / msgGridSize) * msgGridSize;
                        this._collision_other.y = Math.round(this._collision_other.y / msgGridSize) * msgGridSize;
                    }

                    alert(message);
                }
                break;

            default:
                console.warn(`Unknown action: ${actionType}`);
        }
    }

    checkCollisionAt(x, y, game) {
        const testRect = { x: x + 2, y: y + 2, width: 28, height: 28 };
        if (!game.currentRoom) return false;

        for (const other of game.currentRoom.instances) {
            if (other === this || !other.solid) continue;
            const otherRect = { x: other.x + 2, y: other.y + 2, width: 28, height: 28 };
            if (this.rectsCollide(testRect, otherRect)) {
                return true;
            }
        }
        return false;
    }

    getObjectAt(x, y, game) {
        if (!game.currentRoom) return null;

        const testRect = { x: x + 2, y: y + 2, width: 28, height: 28 };
        const colliding = [];

        for (const other of game.currentRoom.instances) {
            if (other === this) continue;
            const otherRect = { x: other.x + 2, y: other.y + 2, width: 28, height: 28 };
            if (this.rectsCollide(testRect, otherRect)) {
                colliding.push(other);
            }
        }

        if (colliding.length === 0) return null;

        colliding.sort((a, b) => {
            if (a.solid && !b.solid) return -1;
            if (!a.solid && b.solid) return 1;
            return b.depth - a.depth;
        });

        return colliding[0];
    }

    rectsCollide(r1, r2) {
        return r1.x < r2.x + r2.width && r1.x + r1.width > r2.x &&
               r1.y < r2.y + r2.height && r1.y + r1.height > r2.y;
    }

    render(ctx) {
        if (!this.visible) return;

        const width = this.sprite && this.sprite.complete ? this.sprite.width : 32;
        const height = this.sprite && this.sprite.complete ? this.sprite.height : 32;

        if (this.rotation !== 0 || this.scale_x !== 1.0 || this.scale_y !== 1.0) {
            ctx.save();
            const centerX = Math.floor(this.x) + (width * this.scale_x) / 2;
            const centerY = Math.floor(this.y) + (height * this.scale_y) / 2;
            ctx.translate(centerX, centerY);

            if (this.rotation !== 0) {
                ctx.rotate((this.rotation * Math.PI) / 180);
            }

            if (this.scale_x !== 1.0 || this.scale_y !== 1.0) {
                ctx.scale(this.scale_x, this.scale_y);
            }

            if (this.sprite && this.sprite.complete) {
                ctx.drawImage(this.sprite, -width / 2, -height / 2);
            } else {
                ctx.fillStyle = '#FF6B6B';
                ctx.fillRect(-width / 2, -height / 2, width, height);
            }

            ctx.restore();
        } else {
            if (this.sprite && this.sprite.complete) {
                ctx.drawImage(this.sprite, Math.floor(this.x), Math.floor(this.y));
            } else {
                ctx.fillStyle = '#FF6B6B';
                ctx.fillRect(Math.floor(this.x), Math.floor(this.y), 32, 32);
            }
        }
    }

    checkCollisions(game) {
        if (!game.currentRoom || !this.events) return;

        const myRect = { x: this.x + 2, y: this.y + 2, width: 28, height: 28 };

        for (const other of game.currentRoom.instances) {
            if (other === this || other.toDestroy) continue;

            const otherRect = { x: other.x + 2, y: other.y + 2, width: 28, height: 28 };

            if (this.rectsCollide(myRect, otherRect)) {
                const collisionKey = `collision_with_${other.name}`;

                if (this.events[collisionKey]) {
                    const collisionEvent = this.events[collisionKey];
                    const actions = collisionEvent.actions || [];
                    this._collision_other = other;
                    this.executeActions(actions, game);
                }
            }
        }
    }
}

class GameRoom {
    constructor(data) {
        this.name = data.name;
        this.width = data.width || 1024;
        this.height = data.height || 768;
        this.bgColor = data.background_color || '#87CEEB';
        this.bgImage = data.background_image || '';
        this.tileHorizontal = data.tile_horizontal || false;
        this.tileVertical = data.tile_vertical || false;
        this.instances = [];
        this.backgroundSprite = null;
    }

    step(game) {
        // GAMEMAKER 7.0 EVENT ORDER:
        // 1. Begin Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onBeginStep(game);
        });

        // 2. Alarm events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.processAlarms();
        });

        // 3. Keyboard events (handled separately in game.processKeyboard)
        // 3b. NoKey events - only fire when no arrow keys pressed AND object is moving
        // This prevents constant stop_movement calls when already stationary
        const arrowKeysForNoKey = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
        const anyArrowKeyHeld = arrowKeysForNoKey.some(key => game.keys[key]);
        if (!anyArrowKeyHeld) {
            this.instances.forEach(inst => {
                // Only trigger nokey if the instance is actually moving
                if (!inst.toDestroy && (inst._hspeed !== 0 || inst._vspeed !== 0)) {
                    inst.onNoKey(game);
                }
            });
        }

        // 4. Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onStep(game);
        });

        // 5. Movement
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.processMovement(game);
        });

        // 6. Collision events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.checkCollisions(game);
        });

        // 7. End Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onEndStep(game);
        });

        // 8. Cleanup destroyed instances
        this.instances = this.instances.filter(inst => !inst.toDestroy);

        // Trigger create events for new instances
        this.instances.forEach(inst => {
            if (inst._pendingCreateEvent) {
                inst.triggerCreateEvent(game);
            }
        });
    }

    render(ctx) {
        ctx.fillStyle = this.bgColor;
        ctx.fillRect(0, 0, this.width, this.height);

        if (this.backgroundSprite && this.backgroundSprite.complete) {
            if (this.tileHorizontal || this.tileVertical) {
                const imgWidth = this.backgroundSprite.width;
                const imgHeight = this.backgroundSprite.height;
                const xCount = this.tileHorizontal ? Math.ceil(this.width / imgWidth) + 1 : 1;
                const yCount = this.tileVertical ? Math.ceil(this.height / imgHeight) + 1 : 1;

                for (let x = 0; x < xCount; x++) {
                    for (let y = 0; y < yCount; y++) {
                        const xPos = this.tileHorizontal ? x * imgWidth : 0;
                        const yPos = this.tileVertical ? y * imgHeight : 0;
                        if (xPos < this.width && yPos < this.height) {
                            ctx.drawImage(this.backgroundSprite, xPos, yPos);
                        }
                    }
                }
            } else {
                ctx.drawImage(this.backgroundSprite, 0, 0, this.width, this.height);
            }
        }

        // GAMEMAKER 7.0: Draw events (sort by depth first)
        const sortedInstances = [...this.instances].sort((a, b) => a.depth - b.depth);
        sortedInstances.forEach(inst => inst.onDraw(ctx));
    }
}

class Game {
    constructor() {
        console.log('🎮 Initializing game...');
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.rooms = {};
        this.currentRoom = null;
        this.running = false;
        this.paused = false;
        this.keys = {};
        this.keysPressed = {};
        this.keysReleased = {};
        this.fps = 0;
        this.frameCount = 0;
        this.lastFpsUpdate = Date.now();

        this.setupKeyboard();
        this.loadGame();
    }

    setupKeyboard() {
        console.log('⌨️ Setting up keyboard...');

        window.addEventListener('keydown', (e) => {
            if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
                e.preventDefault();
            }

            if (!this.keys[e.key]) {
                this.keysPressed[e.key] = true;
            }
            this.keys[e.key] = true;

            if (e.key === 'Escape') {
                this.togglePause();
            }
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
            this.keysReleased[e.key] = true;
        });
    }

    loadGame() {
        console.log('📦 Loading game data...');

        if (typeof gameData === 'undefined') {
            console.error('❌ gameData is undefined!');
            return;
        }

        this.sprites = {};
        this.gameData = gameData;
        const sprites = this.sprites;
        const spriteNames = Object.keys(spritesData);
        console.log(`Loading ${spriteNames.length} sprites...`);

        spriteNames.forEach(name => {
            const img = new Image();
            img.onload = () => console.log(`✓ Loaded sprite: ${name}`);
            img.onerror = () => console.error(`❌ Failed sprite: ${name}`);
            img.src = spritesData[name];
            sprites[name] = img;
        });

        const roomsData = gameData.assets.rooms;
        console.log(`Loading ${Object.keys(roomsData).length} rooms...`);

        for (const [roomName, roomData] of Object.entries(roomsData)) {
            const room = new GameRoom(roomData);

            if (room.bgImage && sprites[room.bgImage]) {
                room.backgroundSprite = sprites[room.bgImage];
            }

            const instancesData = roomData.instances || [];
            instancesData.forEach(instData => {
                const objectData = gameData.assets.objects[instData.object_name];
                const inst = new GameObject(
                    instData.object_name,
                    instData.x,
                    instData.y,
                    instData,
                    objectData
                );

                inst._gameRef = this;

                if (objectData && objectData.sprite && sprites[objectData.sprite]) {
                    inst.sprite = sprites[objectData.sprite];
                }

                room.instances.push(inst);
            });

            this.rooms[roomName] = room;
            console.log(`✓ Loaded room: ${roomName} (${room.instances.length} instances)`);
        }

        const firstRoom = Object.keys(this.rooms)[0];
        if (firstRoom) {
            this.currentRoom = this.rooms[firstRoom];
            console.log(`🚀 Starting with room: ${firstRoom}`);
        }
    }

    start() {
        console.log('▶️ Starting game loop...');
        this.running = true;

        if (this.currentRoom) {
            this.canvas.width = this.currentRoom.width;
            this.canvas.height = this.currentRoom.height;
            console.log(`📐 Canvas initialized to: ${this.currentRoom.width}x${this.currentRoom.height}`);
        }

        this.gameLoop();
    }

    gameLoop() {
        if (!this.running) return;

        this.frameCount++;
        const now = Date.now();
        if (now - this.lastFpsUpdate >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastFpsUpdate = now;
            document.getElementById('fps').textContent = `FPS: ${this.fps}`;
        }

        if (!this.paused) {
            this.processKeyboard();
            this.processKeyboardRelease();
            if (this.currentRoom) {
                this.currentRoom.step(this);
            }
        }

        if (this.currentRoom) {
            this.currentRoom.render(this.ctx);
        }

        if (this.paused) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillStyle = 'white';
            this.ctx.font = 'bold 48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('PAUSED', this.canvas.width / 2, this.canvas.height / 2);
        }

        requestAnimationFrame(() => this.gameLoop());
    }

    processKeyboard() {
        if (!this.currentRoom) return;

        // Process keyboard press events (fires once when key first pressed)
        for (const key in this.keysPressed) {
            if (this.keysPressed[key]) {
                this.currentRoom.instances.forEach(inst => {
                    if (!inst.toDestroy && inst.events) {
                        inst.onKeyboardPress(key, this);
                    }
                });
            }
        }

        // Clear pressed keys for next frame
        this.keysPressed = {};

        // Process keyboard held events (fires continuously while key is held)
        for (const key in this.keys) {
            if (this.keys[key]) {
                this.currentRoom.instances.forEach(inst => {
                    if (!inst.toDestroy && inst.events) {
                        inst.onKeyboardHeld(key, this);
                    }
                });
            }
        }
    }

    processKeyboardRelease() {
        if (!this.currentRoom) return;

        // Process keyboard release events
        for (const key in this.keysReleased) {
            if (this.keysReleased[key]) {
                this.currentRoom.instances.forEach(inst => {
                    if (!inst.toDestroy && inst.events) {
                        inst.onKeyboardRelease(key, this);
                    }
                });
            }
        }

        // Clear released keys for next frame
        this.keysReleased = {};
    }

    togglePause() {
        this.paused = !this.paused;
        document.getElementById('pauseBtn').textContent = this.paused ? '▶️ Resume' : '⏸️ Pause';
        console.log(this.paused ? '⏸️ Paused' : '▶️ Resumed');
    }

    restart() {
        window.location.reload();
    }

    changeRoom(roomName) {
        if (this.rooms[roomName]) {
            // Clear keyboard state
            for (const key in this.keys) {
                this.keys[key] = false;
            }
            this.keysPressed = {};
            this.keysReleased = {};

            this.currentRoom = this.rooms[roomName];

            // Resize canvas
            this.canvas.width = this.currentRoom.width;
            this.canvas.height = this.currentRoom.height;

            console.log(`📍 Changed to room: ${roomName}`);
        } else {
            console.warn(`⚠️ Room not found: ${roomName}`);
        }
    }
}

window.addEventListener('load', () => {
    try {
        window.game = new Game();
        window.game.start();
        console.log('✅ Game started!');
    } catch (error) {
        console.error('❌ Failed to start:', error);
    }
});
