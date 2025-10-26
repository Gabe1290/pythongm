#!/usr/bin/env python3
"""
HTML5 Game Exporter for PyGameMaker
Exports projects as standalone HTML5 games with keyboard and collision support
"""

import json
import base64
import gzip
from pathlib import Path
from typing import Dict, Any


class HTML5Exporter:
    """Export PyGameMaker projects to HTML5"""
    
    def __init__(self):
        self.template_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{game_name}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
        }}
        
        #gameContainer {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            padding: 20px;
        }}
        
        #gameCanvas {{
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            background: #000;
        }}
        
        #controls {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px 30px;
            display: flex;
            gap: 15px;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}
        
        button {{
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        button:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        button:active {{
            transform: translateY(0);
        }}
        
        #fps {{
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 600;
        }}
        
        .title {{
            font-size: 32px;
            font-weight: 700;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            margin-bottom: 10px;
        }}
        
        .instructions {{
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
            text-align: center;
            max-width: 600px;
        }}
    </style>
</head>
<body>
    <div id="gameContainer">
        <div class="title">{game_name}</div>
        <canvas id="gameCanvas" width="{width}" height="{height}"></canvas>
        <div class="instructions">
            Use Arrow Keys to move • Press ESC to pause • F5 to restart
        </div>
        <div id="controls">
            <button id="pauseBtn" onclick="game.togglePause()">⏸️ Pause</button>
            <button onclick="game.restart()">🔄 Restart</button>
            <span id="fps">FPS: 60</span>
        </div>
    </div>

    <script>
        // Decompress embedded game data
        function decompressData(base64Data) {
            try {
                const binaryString = atob(base64Data);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                const decompressed = pako.inflate(bytes, { to: 'string' });
                return JSON.parse(decompressed);
            } catch (error) {
                console.error('Failed to decompress data:', error);
                return null;
            }
        }
        
        console.log('📦 Decompressing game data...');
        const gameData = decompressData({game_data});
        const spritesData = decompressData({sprites_data});
        
        if (!gameData || !spritesData) {
            document.body.innerHTML = '<div style="color:white;text-align:center;padding:50px;">❌ Failed to load game data</div>';
            throw new Error('Data decompression failed');
        }
        
        console.log('✅ Game data decompressed');
        console.log('📊 Loaded ' + Object.keys(gameData.assets.rooms).length + ' rooms, ' + 
                    Object.keys(gameData.assets.objects).length + ' objects');
        
        // Game engine code
        {engine_code}
    </script>    
</body>
</html>"""
        
        self.engine_code = """
// ============================================================================
// PyGameMaker HTML5 Engine - FULL DEBUG
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
        this.speed = 0;
        this.direction = 0;
        this.objectData = objectData;
        this.toDestroy = false;
        this.collisionTimes = {};
        this.targetX = null;
        this.targetY = null;
        this.gridMoveSpeed = 8;
        this.events = objectData ? (objectData.events || {}) : {};

        // Assign depth based on object type for proper rendering order
        // Lower depth = behind, higher depth = in front
        this.depth = this.getDepthForObject(name);
        
        // DEBUG: Log events for this object
        if (this.events && Object.keys(this.events).length > 0) {
            console.log(`📋 ${name} events:`, JSON.stringify(this.events, null, 2));
        }

        // Store game reference for later (will be set when added to room)
        this._pendingCreateEvent = true;

        // Load transformation properties from instance data
        this.rotation = data.rotation || 0;
        this.scale_x = data.scale_x || 1.0;
        this.scale_y = data.scale_y || 1.0;

        // DEBUG: Log if instance has transformations
        if (this.rotation !== 0 || this.scale_x !== 1.0 || this.scale_y !== 1.0) {
            console.log(`📐 ${name} transforms: rotation=${this.rotation}°, scale=(${this.scale_x}, ${this.scale_y})`);
        }
    }
    
    triggerCreateEvent(game) {
        if (this._pendingCreateEvent && this.events && this.events.create) {
            console.log(`🎬 Triggering CREATE event for ${this.name}`);
            const createEvent = this.events.create;
            const actions = createEvent.actions || [];
            actions.forEach(action => this.executeAction(action, game));
            this._pendingCreateEvent = false;
        }
    }

    getDepthForObject(name) {
        // Define rendering order layers
        // 0 = Background/floor objects (stores, ground)
        // 10 = Interactive objects (boxes)
        // 20 = Characters/players
        // 100 = UI elements
        
        if (name.includes('store') && !name.includes('box')) {
            return 0;  // Floor/store tiles at the bottom
        } else if (name.includes('ground') || name.includes('floor')) {
            return 0;  // Floor tiles
        } else if (name.includes('wall')) {
            return 5;  // Walls slightly above floor
        } else if (name.includes('box')) {
            return 10;  // Boxes on top of floor
        } else if (name.includes('soko') || name.includes('player')) {
            return 20;  // Player on top of boxes
        } else {
            return 10;  // Default middle layer
        }
    }
    
    step(game) {
        if (this.targetX !== null && this.targetY !== null) {
            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.gridMoveSpeed) {
                this.x = this.targetX;
                this.y = this.targetY;
                this.targetX = null;
                this.targetY = null;
                console.log(`✅ ${this.name} reached target (${this.x}, ${this.y})`);
            } else {
                this.x += (dx / distance) * this.gridMoveSpeed;
                this.y += (dy / distance) * this.gridMoveSpeed;
            }
        }
        
        if (this.speed > 0) {
            const dirRad = (this.direction * Math.PI) / 180;
            this.x += Math.cos(dirRad) * this.speed;
            this.y -= Math.sin(dirRad) * this.speed;
        }
    }
    
    executeAction(action, game) {
        const actionType = action.action;
        const params = action.parameters || {};
        
        console.log(`⚡ Executing ${actionType} on ${this.name}:`, params);
        
        switch(actionType) {
            case 'move_fixed':
                this.speed = params.speed || 2;
                this.direction = params.direction || 0;
                console.log(`  → speed=${this.speed}, dir=${this.direction}`);
                break;
                
            case 'grid_move':
            case 'move_grid':
                const dir = params.direction;
                const gridSize = params.grid_size || 32;
                
                let newX = this.x;
                let newY = this.y;
                let deltaX = 0;
                let deltaY = 0;
                
                switch(dir) {
                    case 'left': 
                        newX -= gridSize; 
                        deltaX = -gridSize;
                        break;
                    case 'right': 
                        newX += gridSize; 
                        deltaX = gridSize;
                        break;
                    case 'up': 
                        newY -= gridSize; 
                        deltaY = -gridSize;
                        break;
                    case 'down': 
                        newY += gridSize; 
                        deltaY = gridSize;
                        break;
                }
                
                console.log(`  → Grid move ${dir}: (${this.x}, ${this.y}) → (${newX}, ${newY})`);
                
                // Check what's at the target position
                const objectAtTarget = this.getObjectAt(newX, newY, game);
                
                if (objectAtTarget && objectAtTarget.name.includes('box')) {
                    // There's a box in the way - try to push it
                    const boxNewX = objectAtTarget.x + deltaX;
                    const boxNewY = objectAtTarget.y + deltaY;
                    
                    console.log(`  → Box detected at target, trying to push to (${boxNewX}, ${boxNewY})`);
                    
                    const canPushBox = !objectAtTarget.checkCollisionAt(boxNewX, boxNewY, game);
                    
                    if (canPushBox) {
                        // Push the box
                        objectAtTarget.targetX = boxNewX;
                        objectAtTarget.targetY = boxNewY;
                        // Move the player
                        this.targetX = newX;
                        this.targetY = newY;
                        console.log(`  → Box pushed! Player and box moving`);
                    } else {
                        console.log(`  → Cannot push box - blocked`);
                    }
                } else {
                    // No box, just check for regular collision
                    const canMove = !this.checkCollisionAt(newX, newY, game);
                    console.log(`  → Can move: ${canMove}`);
                    
                    if (canMove) {
                        this.targetX = newX;
                        this.targetY = newY;
                        console.log(`  → Target set to (${newX}, ${newY})`);
                    } else {
                        console.log(`  → Blocked by collision`);
                    }
                }
                break;

            case 'snap_to_grid':
                // Snap object to nearest grid position
                const snapGridSize = params.grid_size || 32;
                this.x = Math.round(this.x / snapGridSize) * snapGridSize;
                this.y = Math.round(this.y / snapGridSize) * snapGridSize;
                console.log(`  → Snapped to grid: (${this.x}, ${this.y})`);
                break;
            
            case 'if_collision_at':
                // Check for collision at a specific position
                let checkX = this.x;
                let checkY = this.y;
                
                // Evaluate position expressions
                if (params.x) {
                    const xExpr = params.x.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try {
                        checkX = eval(xExpr);
                    } catch(e) {
                        console.warn(`  ⚠️ Invalid x expression: ${params.x}`);
                    }
                }
                
                if (params.y) {
                    const yExpr = params.y.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try {
                        checkY = eval(yExpr);
                    } catch(e) {
                        console.warn(`  ⚠️ Invalid y expression: ${params.y}`);
                    }
                }
                
                console.log(`  → Checking collision at (${checkX}, ${checkY})`);
                
                // Check for object at that position
                const objectType = params.object_type || params.object_types;
                const targetObject = this.getObjectAt(checkX, checkY, game);
                
                console.log(`  → Looking for type: '${objectType}', found object: ${targetObject ? targetObject.name : 'none'}`);
                if (targetObject) {
                    console.log(`  → Object solid: ${targetObject.solid}, at (${targetObject.x}, ${targetObject.y})`);
                }
                
                let collisionFound = false;
                if (targetObject) {
                    // Check if we're looking for 'solid' objects
                    if (objectType === 'solid') {
                        if (targetObject.solid) {
                            collisionFound = true;
                            console.log(`  → Collision found with solid object: ${targetObject.name}`);
                        }
                    } 
                    // Check for specific object type or 'any'
                    else if (objectType === 'any' || targetObject.name === objectType || 
                        (Array.isArray(objectType) && objectType.includes(targetObject.name))) {
                        collisionFound = true;
                        console.log(`  → Collision found with ${targetObject.name}`);
                    }
                }
                
                // Execute then_actions or else_actions
                if (collisionFound && params.then_actions) {
                    console.log(`  → Executing ${params.then_actions.length} THEN actions`);
                    params.then_actions.forEach(action => this.executeAction(action, game));
                } else if (!collisionFound && params.else_actions) {
                    console.log(`  → Executing ${params.else_actions.length} ELSE actions`);
                    params.else_actions.forEach(action => this.executeAction(action, game));
                }
                break;

            case 'move_to_position':
                // Move to a specific position
                let targetX = this.x;
                let targetY = this.y;
                
                // Evaluate position expressions
                if (params.x) {
                    const xExpr = params.x.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try {
                        targetX = eval(xExpr);
                    } catch(e) {
                        console.warn(`  ⚠️ Invalid x expression: ${params.x}`);
                    }
                }
                
                if (params.y) {
                    const yExpr = params.y.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try {
                        targetY = eval(yExpr);
                    } catch(e) {
                        console.warn(`  ⚠️ Invalid y expression: ${params.y}`);
                    }
                }
                
                console.log(`  → Moving to position: (${targetX}, ${targetY})`);
                
                if (params.smooth) {
                    // Smooth movement using target position
                    this.targetX = targetX;
                    this.targetY = targetY;
                    console.log(`  → Smooth movement enabled`);
                } else {
                    // Instant movement
                    this.x = targetX;
                    this.y = targetY;
                    console.log(`  → Instant movement`);
                }
                break;

            case 'push_object':
                // Push another object in a direction
                const pushTarget = params.target || 'other';
                const pushDir = params.direction;
                const pushDist = params.distance || 32;
                const checkColl = params.check_collision !== false;
                
                console.log(`  → Push ${pushTarget} ${pushDir} by ${pushDist}px`);
                
                // Get the object to push (the one we just collided with)
                let pushedObject = null;
                
                if (pushTarget === 'other') {
                    // Find object at current collision position
                    let checkX = this.x;
                    let checkY = this.y;
                    
                    switch(pushDir) {
                        case 'left': checkX -= pushDist; break;
                        case 'right': checkX += pushDist; break;
                        case 'up': checkY -= pushDist; break;
                        case 'down': checkY += pushDist; break;
                    }
                    
                    pushedObject = this.getObjectAt(checkX, checkY, game);
                }
                
                if (pushedObject) {
                    console.log(`  → Found object to push: ${pushedObject.name}`);
                    
                    // Calculate new position for pushed object
                    let newX = pushedObject.x;
                    let newY = pushedObject.y;
                    
                    switch(pushDir) {
                        case 'left': newX -= pushDist; break;
                        case 'right': newX += pushDist; break;
                        case 'up': newY -= pushDist; break;
                        case 'down': newY += pushDist; break;
                    }
                    
                    console.log(`  → New position for pushed object: (${newX}, ${newY})`);
                    
                    // Check if destination is clear
                    let canPush = true;
                    if (checkColl) {
                        canPush = !pushedObject.checkCollisionAt(newX, newY, game);
                        console.log(`  → Can push: ${canPush}`);
                    }
                    
                    if (canPush) {
                        // Push the object
                        pushedObject.targetX = newX;
                        pushedObject.targetY = newY;
                        
                        // ALSO move the player to the box's current position
                        this.targetX = pushedObject.x;
                        this.targetY = pushedObject.y;
                        
                        console.log(`  → Object pushed! Player moving to (${this.targetX}, ${this.targetY})`);
                    } else {
                        console.log(`  → Cannot push - blocked`);
                    }
                } else {
                    console.log(`  → No object found to push`);
                }
                break;

            case 'set_variable':
                const varName = params.variable || params.name;
                let varValue = params.value;
                
                // Handle special values
                if (varValue === 'count_instances') {
                    const countType = params.object_type || params.object_name;
                    varValue = game.currentRoom.instances.filter(inst => 
                        inst.name === countType && !inst.toDestroy
                    ).length;
                    console.log(`  → Counting ${countType}: ${varValue}`);
                }
                
                // Set the variable
                this[varName] = varValue;
                console.log(`  → Set ${varName} = ${varValue}`);
                break;

            case 'count_instances':
                // Count instances of an object type
                const countObjectType = params.object_type || params.object_name;
                let count = 0;
                
                if (game.currentRoom) {
                    count = game.currentRoom.instances.filter(inst => 
                        inst.name === countObjectType && !inst.toDestroy
                    ).length;
                }
                
                console.log(`  → Counted ${count} instances of ${countObjectType}`);
                
                // Store count for comparison (if this is part of an if_variable check)
                if (params.variable) {
                    this[params.variable] = count;
                }
                
                return count;
                break;

            case 'if_condition':
                const conditionType = params.condition_type;
                
                console.log(`  → if_condition type: ${conditionType}`);
                
                if (conditionType === 'instance_count') {
                    // Count instances of an object
                    const targetObjectName = params.object_name || params.object_type;
                    const operator = params.operator || params.operation || '==';
                    const compareValue = params.value || 0;
                    
                    // Count instances
                    let instanceCount = 0;
                    if (game.currentRoom) {
                        instanceCount = game.currentRoom.instances.filter(inst => 
                            inst.name === targetObjectName && !inst.toDestroy
                        ).length;
                    }
                    
                    console.log(`  → Counting ${targetObjectName}: ${instanceCount}`);
                    
                    // Compare
                    let conditionMet = false;
                    switch(operator) {
                        case '==':
                        case 'equal':
                            conditionMet = instanceCount == compareValue;
                            break;
                        case '!=':
                        case 'not_equal':
                            conditionMet = instanceCount != compareValue;
                            break;
                        case '<':
                        case 'less':
                            conditionMet = instanceCount < compareValue;
                            break;
                        case '<=':
                        case 'less_equal':
                            conditionMet = instanceCount <= compareValue;
                            break;
                        case '>':
                        case 'greater':
                            conditionMet = instanceCount > compareValue;
                            break;
                        case '>=':
                        case 'greater_equal':
                            conditionMet = instanceCount >= compareValue;
                            break;
                    }
                    
                    console.log(`  → Instance count check: ${targetObjectName} count=${instanceCount} ${operator} ${compareValue} = ${conditionMet}`);
                    
                    // Execute actions based on result
                    if (conditionMet && params.then_actions) {
                        console.log(`  → Executing ${params.then_actions.length} THEN actions`);
                        params.then_actions.forEach(action => this.executeAction(action, game));
                    } else if (!conditionMet && params.else_actions && params.else_actions.length > 0) {
                        console.log(`  → Executing ${params.else_actions.length} ELSE actions`);
                        params.else_actions.forEach(action => this.executeAction(action, game));
                    }
                } else {
                    console.warn(`  ⚠️ Unknown condition_type: ${conditionType}`);
                }
                break;            

            case 'if_variable':
                // Check a variable condition
                const checkVarName = params.variable;  // ← Changed to checkVarName
                const operation = params.operation || params.operator || 'equal';
                const compareValue = params.value;
                
                let currentValue = this[checkVarName];  // ← Use checkVarName
                
                // If variable starts with 'count_', do a count
                if (checkVarName && checkVarName.startsWith('count_')) {  // ← Use checkVarName
                    const objectType = checkVarName.replace('count_', '');
                    currentValue = game.currentRoom.instances.filter(inst => 
                        inst.name === objectType && !inst.toDestroy
                    ).length;
                    console.log(`  → Counting ${objectType}: ${currentValue}`);
                }
                
                let conditionMet = false;
                
                switch(operation) {
                    case 'equal':
                    case '==':
                    case '===':
                        conditionMet = currentValue == compareValue;
                        break;
                    case 'not_equal':
                    case '!=':
                    case '!==':
                        conditionMet = currentValue != compareValue;
                        break;
                    case 'less':
                    case '<':
                        conditionMet = currentValue < compareValue;
                        break;
                    case 'less_equal':
                    case '<=':
                        conditionMet = currentValue <= compareValue;
                        break;
                    case 'greater':
                    case '>':
                        conditionMet = currentValue > compareValue;
                        break;
                    case 'greater_equal':
                    case '>=':
                        conditionMet = currentValue >= compareValue;
                        break;
                }
                
                console.log(`  → Variable check: ${checkVarName} (${currentValue}) ${operation} ${compareValue} = ${conditionMet}`);  // ← Use checkVarName
                
                if (conditionMet && params.then_actions) {
                    console.log(`  → Executing ${params.then_actions.length} THEN actions`);
                    params.then_actions.forEach(action => this.executeAction(action, game));
                } else if (!conditionMet && params.else_actions) {
                    console.log(`  → Executing ${params.else_actions.length} ELSE actions`);
                    params.else_actions.forEach(action => this.executeAction(action, game));
                }
                break;

            case 'show_message':
                const message = params.message || params.text || '';
                console.log(`  → Showing message: "${message}"`);
                
                // Show browser alert
                if (message) {
                    alert(message);
                }
                break;
            
            case 'delay_action':
                const delayFrames = params.frames || params.delay || 60;
                const delayMs = (delayFrames / 60) * 1000; // Convert frames to milliseconds (60fps)
                
                // Check if there's a then_action (singular) or then_actions (array)
                let delayedAction = null;
                
                if (params.then_action) {
                    // Single action specified as a string
                    delayedAction = {
                        action: params.then_action,
                        parameters: {
                            room_name: params.room_name,
                            room: params.room_name
                        }
                    };
                    console.log(`  → Delaying action '${params.then_action}' by ${delayMs}ms (${delayFrames} frames)`);
                } else if (params.then_actions && params.then_actions.length > 0) {
                    // Array of actions
                    console.log(`  → Delaying ${params.then_actions.length} actions by ${delayMs}ms`);
                }
                
                setTimeout(() => {
                    console.log(`  ⏰ Executing delayed action for ${this.name}`);
                    
                    if (delayedAction) {
                        // Execute single action
                        if (!this.toDestroy && game.currentRoom) {
                            this.executeAction(delayedAction, game);
                        }
                    } else if (params.then_actions) {
                        // Execute array of actions
                        params.then_actions.forEach(action => {
                            if (!this.toDestroy && game.currentRoom) {
                                this.executeAction(action, game);
                            }
                        });
                    }
                }, delayMs);
                break;

            case 'change_room':
            case 'go_to_room':
                let roomName = params.room_name || params.room;
                
                // Handle special room names
                if (roomName === '__next__') {
                    // Go to next room in sequence
                    const roomNames = Object.keys(game.rooms);
                    const currentIndex = roomNames.indexOf(game.currentRoom.name);
                    
                    if (currentIndex >= 0 && currentIndex < roomNames.length - 1) {
                        roomName = roomNames[currentIndex + 1];
                        console.log(`  → '__next__' = ${roomName}`);
                    } else {
                        console.log(`  → No next room available (already at last room)`);
                        return;
                    }
                } else if (roomName === '__previous__') {
                    // Go to previous room
                    const roomNames = Object.keys(game.rooms);
                    const currentIndex = roomNames.indexOf(game.currentRoom.name);
                    
                    if (currentIndex > 0) {
                        roomName = roomNames[currentIndex - 1];
                        console.log(`  → '__previous__' = ${roomName}`);
                    } else {
                        console.log(`  → No previous room available (already at first room)`);
                        return;
                    }
                } else if (roomName === '__restart__') {
                    // Restart current room
                    roomName = game.currentRoom.name;
                    console.log(`  → Restarting current room: ${roomName}`);
                }
                
                if (roomName && game.rooms[roomName]) {
                    console.log(`  → Changing to room: ${roomName}`);
                    game.changeRoom(roomName);
                } else {
                    console.warn(`  ⚠️ Room not found: ${roomName}`);
                }
                break;
                        
            case 'destroy_instance':
                this.toDestroy = true;
                console.log(`  → Marked for destruction`);
                break;
                                
            default:
                console.warn(`  ⚠️ Unknown action type: ${actionType}`);
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
        
        // Find ALL objects at this position
        for (const other of game.currentRoom.instances) {
            if (other === this) continue;
            const otherRect = { x: other.x + 2, y: other.y + 2, width: 28, height: 28 };
            if (this.rectsCollide(testRect, otherRect)) {
                colliding.push(other);
            }
        }
        
        if (colliding.length === 0) return null;
        
        // Prioritize by depth (higher depth = in front)
        // Prioritize solid objects over non-solid
        colliding.sort((a, b) => {
            // First, prioritize solid objects
            if (a.solid && !b.solid) return -1;
            if (!a.solid && b.solid) return 1;
            // Then by depth (higher depth first)
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
        
        // Get transformation properties
        const rotation = this.rotation || 0;
        const scaleX = this.scale_x || 1.0;
        const scaleY = this.scale_y || 1.0;
        
        // Only apply transformations if needed
        if (rotation !== 0 || scaleX !== 1.0 || scaleY !== 1.0) {
            ctx.save();
            
            // Move to center of sprite
            const centerX = Math.floor(this.x) + (width * scaleX) / 2;
            const centerY = Math.floor(this.y) + (height * scaleY) / 2;
            ctx.translate(centerX, centerY);
            
            // Apply rotation (convert degrees to radians)
            if (rotation !== 0) {
                ctx.rotate((rotation * Math.PI) / 180);
            }
            
            // Apply scale
            if (scaleX !== 1.0 || scaleY !== 1.0) {
                ctx.scale(scaleX, scaleY);
            }
            
            // Draw at offset position
            if (this.sprite && this.sprite.complete) {
                ctx.drawImage(this.sprite, -width / 2, -height / 2);
            } else {
                ctx.fillStyle = '#FF6B6B';
                ctx.fillRect(-width / 2, -height / 2, width, height);
                ctx.strokeStyle = '#000';
                ctx.strokeRect(-width / 2, -height / 2, width, height);
            }
            
            ctx.restore();
        } else {
            // No transformation - draw normally
            if (this.sprite && this.sprite.complete) {
                ctx.drawImage(this.sprite, Math.floor(this.x), Math.floor(this.y));
            } else {
                ctx.fillStyle = '#FF6B6B';
                ctx.fillRect(Math.floor(this.x), Math.floor(this.y), 32, 32);
                ctx.strokeStyle = '#000';
                ctx.strokeRect(Math.floor(this.x), Math.floor(this.y), 32, 32);
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
                    
                    console.log(`💥 Collision: ${this.name} with ${other.name} (${actions.length} actions)`);
                    
                    actions.forEach(action => {
                        this.executeCollisionAction(action, other, game);
                    });
                }
            }
        }
    }

    checkNotCollidingEvents(game) {
        if (!game.currentRoom || !this.events) return;
        
        // Look for "NOT colliding" events
        for (const eventName in this.events) {
            if (eventName.startsWith('not_collision_with_')) {
                const targetObjectName = eventName.replace('not_collision_with_', '');
                
                // Check if currently colliding with any instance of target type
                let isColliding = false;
                const myRect = { x: this.x + 2, y: this.y + 2, width: 28, height: 28 };
                
                for (const other of game.currentRoom.instances) {
                    if (other.name === targetObjectName && !other.toDestroy) {
                        const otherRect = { x: other.x + 2, y: other.y + 2, width: 28, height: 28 };
                        if (this.rectsCollide(myRect, otherRect)) {
                            isColliding = true;
                            break;
                        }
                    }
                }
                
                // If NOT colliding, execute the event actions
                if (!isColliding) {
                    const notCollisionEvent = this.events[eventName];
                    const actions = notCollisionEvent.actions || [];
                    
                    if (actions.length > 0) {
                        console.log(`❌ NOT Colliding: ${this.name} NOT with ${targetObjectName} (${actions.length} actions)`);
                        
                        actions.forEach(action => {
                            this.executeCollisionAction(action, null, game);
                        });
                    }
                }
            }
        }
    }
    
    transformTo(newObjectName, game) {
        if (!game.gameData || !game.gameData.assets.objects[newObjectName]) {
            console.warn(`  ⚠️ Cannot transform to ${newObjectName} - object not found`);
            return;
        }
        
        console.log(`  → Transforming ${this.name} to ${newObjectName}`);
        const newObjectData = game.gameData.assets.objects[newObjectName];
        
        this.name = newObjectName;
        this.events = newObjectData.events || {};
        this.solid = newObjectData.solid || false;
        
        // Update depth based on new object type
        this.depth = this.getDepthForObject(newObjectName);
        
        if (newObjectData.sprite && game.sprites[newObjectData.sprite]) {
            this.sprite = game.sprites[newObjectData.sprite];
            console.log(`  → Sprite changed to ${newObjectData.sprite}`);
        }
    }

    executeCollisionAction(action, otherObject, game) {
        const actionType = action.action;
        const params = action.parameters || {};
        
        // Handle null otherObject for NOT colliding events
        const otherName = otherObject ? otherObject.name : 'N/A';
        console.log(`⚡ Collision action ${actionType} on ${this.name} (other: ${otherName}):`, params);

        switch(actionType) {
            case 'transform_to':
                const newObjectName = params.object_name;
                if (newObjectName) {
                    this.transformTo(newObjectName, game);
                }
                console.log(`  → Transformed to ${newObjectName}`);
    
                // Trigger CREATE event for transformed object
                this.triggerCreateEvent(game);
                break;
                
            case 'if_can_push':
                console.log(`  → if_can_push: checking push conditions`);
                // This should be handled in movement logic, not collision
                break;
                
            case 'push_and_move':
                console.log(`  → push_and_move: handled in grid_move`);
                // This is handled in the grid_move action
                break;
                
            case 'stop_movement':
                this.targetX = null;
                this.targetY = null;
                this.speed = 0;
                console.log(`  → Movement stopped due to collision`);
                break;
                
            case 'move':
                // Set movement direction and speed
                if (params.direction !== undefined) {
                    this.direction = params.direction;
                }
                if (params.speed !== undefined) {
                    this.speed = params.speed;
                }
                console.log(`  → Moving: dir=${this.direction}, speed=${this.speed}`);
                break;
                
            case 'bounce':
                // Reverse direction based on bounce type
                if (params.bounce_type === 'horizontal') {
                    this.direction = 180 - this.direction;
                } else if (params.bounce_type === 'vertical') {
                    this.direction = -this.direction;
                }
                console.log(`  → Bounced: new direction=${this.direction}`);
                break;
                
            case 'set_vertical_speed':
                // In a grid-based game, this might not apply
                console.log(`  → set_vertical_speed (not applicable in grid movement)`);
                break;
                
            case 'change_room':
                const roomName = params.room_name;
                if (roomName && game.rooms[roomName]) {
                    game.changeRoom(roomName);
                    console.log(`  → Changed to room ${roomName}`);
                }
                break;
            
            case 'snap_to_grid':
                // Snap object to nearest grid position
                const snapGridSize = params.grid_size || 32;
                this.x = Math.round(this.x / snapGridSize) * snapGridSize;
                this.y = Math.round(this.y / snapGridSize) * snapGridSize;
                console.log(`  → Snapped to grid: (${this.x}, ${this.y})`);
                break;
                    
            case 'destroy_instance':
                if (params.target === 'self') {
                    this.toDestroy = true;
                    console.log(`  → Self marked for destruction`);
                } else if (params.target === 'other' && otherObject) {
                    otherObject.toDestroy = true;
                    console.log(`  → Other object marked for destruction`);
                }
                break;
                
            case 'create_instance':
                const objName = params.object_name;
                const x = params.x !== undefined ? params.x : this.x;
                const y = params.y !== undefined ? params.y : this.y;
                if (objName && game.gameData.assets.objects[objName]) {
                    const objectData = game.gameData.assets.objects[objName];
                    const newInst = new GameObject(objName, x, y, {}, objectData);
                    if (objectData.sprite && game.sprites[objectData.sprite]) {
                        newInst.sprite = game.sprites[objectData.sprite];
                    }
                    game.currentRoom.instances.push(newInst);
                    console.log(`  → Created ${objName} at (${x}, ${y})`);
                }
                break;
                
            case 'play_sound':
                console.log(`  → play_sound (audio not implemented): ${params.sound_name}`);
                break;
                
            case 'set_variable':
                const setVarName = params.variable || params.name;  // ← Changed to setVarName
                let setVarValue = params.value;  // ← Changed to setVarValue
                
                // Handle special values
                if (setVarValue === 'count_instances') {
                    const countType = params.object_type || params.object_name;
                    setVarValue = game.currentRoom.instances.filter(inst => 
                        inst.name === countType && !inst.toDestroy
                    ).length;
                    console.log(`  → Counting ${countType}: ${setVarValue}`);
                }
                
                // Set the variable
                this[setVarName] = setVarValue;
                console.log(`  → Set ${setVarName} = ${setVarValue}`);
                break;
                                
            case 'increment_variable':
                const incVar = params.variable_name;
                const incAmount = params.amount || 1;
                if (incVar) {
                    this[incVar] = (this[incVar] || 0) + incAmount;
                    console.log(`  → Incremented ${incVar} to ${this[incVar]}`);
                }
                break;
                
            default:
                console.warn(`  ⚠️ Unknown collision action type: ${actionType}`);
                // Try to execute as regular action
                this.executeAction(action, game);
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
        // Trigger create events for new instances
        this.instances.forEach(inst => {
            if (inst._pendingCreateEvent) {
                inst.triggerCreateEvent(game);
            }
        });

        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.step(game);
        });
        
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.checkCollisions(game);
        });

        // Check NOT colliding events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.checkNotCollidingEvents(game);
        });
        
        this.instances = this.instances.filter(inst => !inst.toDestroy);
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
        
        // Sort instances by depth before rendering
        // Lower depth = drawn first (behind), higher depth = drawn last (in front)
        const sortedInstances = [...this.instances].sort((a, b) => {
            const depthA = a.depth !== undefined ? a.depth : 0;
            const depthB = b.depth !== undefined ? b.depth : 0;
            return depthA - depthB;  // Ascending order
        });
        
        sortedInstances.forEach(inst => inst.render(ctx));
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
        this.fps = 0;
        this.frameCount = 0;
        this.lastFpsUpdate = Date.now();
        this.lastKeyTime = {
            'ArrowLeft': 0,
            'ArrowRight': 0,
            'ArrowUp': 0,
            'ArrowDown': 0
        };
        this.keyRepeatDelay = 200;
        
        this.setupKeyboard();
        this.loadGame();
    }
    
    setupKeyboard() {
        console.log('⌨️ Setting up keyboard...');
        
        window.addEventListener('keydown', (e) => {
            if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
                e.preventDefault();
            }
            this.keys[e.key] = true;
            if (!this.keysPressed[e.key]) {
                this.keysPressed[e.key] = true;
                console.log(`🔑 Key pressed: ${e.key}`);
            }
            if (e.key === 'Escape') {
                this.togglePause();
            }
        });
        
        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
            this.keysPressed[e.key] = false;
            if (this.lastKeyTime[e.key] !== undefined) {
                this.lastKeyTime[e.key] = 0;
            }
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
        
        const now = Date.now();
        
        // Check if any keys are pressed - early exit if not
        const anyKeyPressed = Object.keys(this.keys).some(key => this.keys[key]);
        if (!anyKeyPressed) return;
        
        this.currentRoom.instances.forEach(inst => {
            if (inst.toDestroy || !inst.events) return;
            
            // Skip objects without keyboard events
            if (!inst.events.keyboard_press && !inst.events.keyboard) return;
            
            const keyboardEvents = inst.events.keyboard_press || inst.events.keyboard || {};
            
            // Skip if keyboard events object is empty
            if (Object.keys(keyboardEvents).length === 0) return;
            
            // DEBUG: On first key press, log the entire events structure
            if (!inst._eventsLogged) {
                console.log(`🔍 Events structure for ${inst.name}:`, inst.events);
                console.log(`🔍 Keyboard events specifically:`, keyboardEvents);
                inst._eventsLogged = true;
            }
            
            const keyMap = {
                'ArrowLeft': ['press_left', 'left'],
                'ArrowRight': ['press_right', 'right'],
                'ArrowUp': ['press_up', 'up'],
                'ArrowDown': ['press_down', 'down']
            };
            
            for (const [keyCode, directions] of Object.entries(keyMap)) {
                if (this.keys[keyCode] && now - this.lastKeyTime[keyCode] >= this.keyRepeatDelay) {
                    let actions = [];
                    let foundDir = null;
                    
                    for (const dir of directions) {
                        if (keyboardEvents[dir] && keyboardEvents[dir].actions && keyboardEvents[dir].actions.length > 0) {
                            actions = keyboardEvents[dir].actions;
                            foundDir = dir;
                            console.log(`🎹 ${inst.name}: ${foundDir} triggered (${actions.length} actions)`);
                            break;
                        }
                    }
                    
                    if (actions.length > 0) {
                        actions.forEach(action => inst.executeAction(action, this));
                        this.lastKeyTime[keyCode] = now;
                    }
                }
            }
        });
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
            // Clear keyboard state to prevent stuck keys
            for (const key in this.keys) {
                this.keys[key] = false;
                this.keysPressed[key] = false;
                this.lastKeyTime[key] = 0;
            }
            
            this.currentRoom = this.rooms[roomName];
            console.log(`📍 Changed to room: ${roomName}`);
            console.log(`⌨️ Keyboard state cleared`);
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
"""
    
    def export(self, project_path: Path, output_path: Path) -> bool:
            """Export project to HTML5"""
            try:
                print(f"📦 Exporting {project_path.name} to HTML5...")
                
                # Load project
                project_file = project_path / "project.json"
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                print(f"  ✓ Loaded project: {project_data['name']}")
                
                # DEBUG: Check keyboard events in objects
                objects = project_data.get('assets', {}).get('objects', {})
                for obj_name, obj_data in objects.items():
                    if 'events' in obj_data:
                        events = obj_data['events']
                        if 'keyboard' in events or 'keyboard_press' in events:
                            print(f"  🎹 {obj_name} has keyboard events")
                            kb_events = events.get('keyboard') or events.get('keyboard_press')
                            if kb_events:
                                for key, key_data in kb_events.items():
                                    actions = key_data.get('actions', [])
                                    print(f"     {key}: {len(actions)} actions")
                
                # Encode sprites as base64
                print(f"  📸 Encoding sprites...")
                sprites_data = self.encode_sprites(project_path, project_data)
                print(f"  ✓ Encoded {len(sprites_data)} sprites")
                
                # Get window size from first room if settings not available
                settings = project_data.get('settings', {})
                width = settings.get('window_width')
                height = settings.get('window_height')
                
                # If no settings, use first room dimensions
                if not width or not height:
                    rooms = project_data.get('assets', {}).get('rooms', {})
                    if rooms:
                        first_room = next(iter(rooms.values()))
                        width = first_room.get('width', 1024)
                        height = first_room.get('height', 768)
                    else:
                        width = 1024
                        height = 768
                
                print(f"  📐 Canvas size: {width}x{height}")
                
                # Generate HTML
                print(f"  🎨 Generating HTML...")
                
                # Serialize the data (no indentation to save space)
                game_data_json = json.dumps(project_data, separators=(',', ':'))
                sprites_data_json = json.dumps(sprites_data, separators=(',', ':'))

                print(f"  📊 Original sizes:")
                print(f"     Game data: {len(game_data_json):,} bytes")
                print(f"     Sprites data: {len(sprites_data_json):,} bytes")

                # Compress the data using gzip
                game_data_compressed = base64.b64encode(
                    gzip.compress(game_data_json.encode('utf-8'), compresslevel=9)
                ).decode('ascii')

                sprites_data_compressed = base64.b64encode(
                    gzip.compress(sprites_data_json.encode('utf-8'), compresslevel=9)
                ).decode('ascii')

                compression_ratio_game = (len(game_data_compressed) * 100) // len(game_data_json)
                compression_ratio_sprites = (len(sprites_data_compressed) * 100) // len(sprites_data_json)

                print(f"  📦 Compressed sizes:")
                print(f"     Game data: {len(game_data_compressed):,} bytes ({compression_ratio_game}%)")
                print(f"     Sprites data: {len(sprites_data_compressed):,} bytes ({compression_ratio_sprites}%)")
                print(f"  💾 Total size reduction: {len(game_data_json) + len(sprites_data_json) - len(game_data_compressed) - len(sprites_data_compressed):,} bytes saved")

                # Replace placeholders manually to avoid format string issues
                html_content = self.template_html.replace('{game_name}', project_data['name'])
                html_content = html_content.replace('{width}', str(width))
                html_content = html_content.replace('{height}', str(height))
                html_content = html_content.replace('{game_data}', f'"{game_data_compressed}"')
                html_content = html_content.replace('{sprites_data}', f'"{sprites_data_compressed}"')
                html_content = html_content.replace('{engine_code}', self.engine_code)
                
                # Write output
                output_file = output_path / f"{project_data['name']}.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                file_size_kb = output_file.stat().st_size / 1024
                
                print(f"  ✅ Export complete!")
                print(f"  📄 File: {output_file.name}")
                print(f"  💾 Size: {file_size_kb:.1f} KB")
                print(f"\n🎮 Open {output_file.name} in a web browser to play!")
                
                return True
                
            except Exception as e:
                print(f"❌ Export failed: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    def encode_sprites(self, project_path: Path, project_data: Dict) -> Dict[str, str]:
        """Encode sprites and backgrounds as base64 data URLs"""
        encoded = {}
        
        # Encode sprites
        sprites_data = project_data.get('assets', {}).get('sprites', {})
        for sprite_name, sprite_info in sprites_data.items():
            file_path = sprite_info.get('file_path', '')
            if file_path:
                full_path = project_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'rb') as f:
                            sprite_bytes = f.read()
                            b64 = base64.b64encode(sprite_bytes).decode('utf-8')
                            
                            # Detect image type
                            ext = full_path.suffix.lower()
                            mime_type = 'image/png'
                            if ext == '.jpg' or ext == '.jpeg':
                                mime_type = 'image/jpeg'
                            elif ext == '.gif':
                                mime_type = 'image/gif'
                            
                            encoded[sprite_name] = f"data:{mime_type};base64,{b64}"
                    except Exception as e:
                        print(f"  ⚠️  Failed to encode {sprite_name}: {e}")
        
        # Encode backgrounds
        backgrounds_data = project_data.get('assets', {}).get('backgrounds', {})
        for bg_name, bg_info in backgrounds_data.items():
            file_path = bg_info.get('file_path', '')
            if file_path:
                full_path = project_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'rb') as f:
                            bg_bytes = f.read()
                            b64 = base64.b64encode(bg_bytes).decode('utf-8')
                            
                            ext = full_path.suffix.lower()
                            mime_type = 'image/png'
                            if ext == '.jpg' or ext == '.jpeg':
                                mime_type = 'image/jpeg'
                            
                            encoded[bg_name] = f"data:{mime_type};base64,{b64}"
                    except Exception as e:
                        print(f"  ⚠️  Failed to encode background {bg_name}: {e}")
        
        return encoded


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python html5_exporter.py <project_path> <output_directory>")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not project_path.exists():
        print(f"❌ Project path not found: {project_path}")
        sys.exit(1)
    
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    
    exporter = HTML5Exporter()
    success = exporter.export(project_path, output_path)
    
    sys.exit(0 if success else 1)