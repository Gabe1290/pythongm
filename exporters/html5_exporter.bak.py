#!/usr/bin/env python3
"""
HTML5 Game Exporter for PyGameMaker
Exports projects as standalone HTML5 games with keyboard and collision support
"""

import json
import base64
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
        // Embedded game data
        const gameData = {game_data};
        const spritesData = {sprites_data};
        
        // Game engine code
        {engine_code}
    </script>
</body>
</html>"""
        
        self.engine_code = """
// ============================================================================
// PyGameMaker HTML5 Engine
// Full keyboard and collision support
// ============================================================================

class GameObject {
    constructor(name, x, y, data, objectData) {
        this.name = name;
        this.x = x;
        this.y = y;
        this.sprite = null;
        this.visible = data.visible !== false;
        this.solid = false;
        this.speed = 0;
        this.direction = 0;
        this.objectData = objectData;
        this.toDestroy = false;
        
        // Collision tracking
        this.collisionTimes = {};
        
        // Grid movement
        this.targetX = null;
        this.targetY = null;
        this.gridMoveSpeed = 8;
        
        // Event data
        this.events = objectData ? objectData.events || {} : {};
        
        // Extract solid property from object data
        if (objectData) {
            this.solid = objectData.solid || false;
        }
    }
    
    step(game) {
        // Grid movement animation
        if (this.targetX !== null && this.targetY !== null) {
            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.gridMoveSpeed) {
                // Snap to exact position
                this.x = this.targetX;
                this.y = this.targetY;
                this.targetX = null;
                this.targetY = null;
            } else {
                // Move toward target
                this.x += (dx / distance) * this.gridMoveSpeed;
                this.y += (dy / distance) * this.gridMoveSpeed;
            }
        }
        
        // Automatic movement based on speed and direction
        if (this.speed > 0) {
            const dirRad = (this.direction * Math.PI) / 180;
            this.x += Math.cos(dirRad) * this.speed;
            this.y -= Math.sin(dirRad) * this.speed;
        }
        
        // Execute step event
        this.executeEvent('step', game);
    }
    
    executeEvent(eventName, game) {
        if (!this.events || !this.events[eventName]) return;
        
        const eventData = this.events[eventName];
        const actions = eventData.actions || [];
        
        actions.forEach(action => {
            this.executeAction(action, game);
        });
    }
    
    executeAction(action, game) {
        const actionType = action.action;
        const params = action.parameters || {};
        
        switch(actionType) {
            case 'move_fixed':
                this.speed = params.speed || 2;
                this.direction = params.direction || 0;
                break;
                
            case 'grid_move':
                const dir = params.direction;
                const gridSize = params.grid_size || 32;
                
                let newX = this.x;
                let newY = this.y;
                
                switch(dir) {
                    case 'left': newX -= gridSize; break;
                    case 'right': newX += gridSize; break;
                    case 'up': newY -= gridSize; break;
                    case 'down': newY += gridSize; break;
                }
                
                // Check collision before moving
                const canMove = !this.checkCollisionAt(newX, newY, game);
                
                if (canMove) {
                    this.targetX = newX;
                    this.targetY = newY;
                }
                break;
                
            case 'destroy_instance':
                this.toDestroy = true;
                break;
                
            case 'change_room':
                const roomName = params.room_name;
                if (roomName && game.rooms[roomName]) {
                    game.changeRoom(roomName);
                }
                break;
                
            case 'set_variable':
                const varName = params.variable_name;
                const value = params.value;
                if (varName) {
                    this[varName] = value;
                }
                break;
        }
    }
    
    checkCollisionAt(x, y, game) {
        // Create temporary rect at new position
        const testRect = {
            x: x + 2,
            y: y + 2,
            width: 28,
            height: 28
        };
        
        // Check against all instances in current room
        if (!game.currentRoom) return false;
        
        for (const other of game.currentRoom.instances) {
            if (other === this || !other.solid) continue;
            
            const otherRect = {
                x: other.x + 2,
                y: other.y + 2,
                width: 28,
                height: 28
            };
            
            if (this.rectsCollide(testRect, otherRect)) {
                return true;
            }
        }
        
        return false;
    }
    
    getCollisionRect() {
        return {
            x: this.x + 2,
            y: this.y + 2,
            width: 28,
            height: 28
        };
    }
    
    rectsCollide(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    }
    
    checkCollision(other) {
        const rect1 = this.getCollisionRect();
        const rect2 = other.getCollisionRect();
        return this.rectsCollide(rect1, rect2);
    }
    
    render(ctx) {
        if (!this.visible) return;
        
        if (this.sprite && this.sprite.complete) {
            ctx.drawImage(this.sprite, Math.floor(this.x), Math.floor(this.y));
        } else {
            // Draw placeholder
            ctx.fillStyle = '#FF6B6B';
            ctx.fillRect(Math.floor(this.x), Math.floor(this.y), 32, 32);
            ctx.strokeStyle = '#000';
            ctx.strokeRect(Math.floor(this.x), Math.floor(this.y), 32, 32);
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
        // Update all instances
        this.instances.forEach(inst => {
            if (!inst.toDestroy) {
                inst.step(game);
            }
        });
        
        // Remove destroyed instances
        this.instances = this.instances.filter(inst => !inst.toDestroy);
    }
    
    render(ctx) {
        // Clear background
        ctx.fillStyle = this.bgColor;
        ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw background image if available
        if (this.backgroundSprite && this.backgroundSprite.complete) {
            if (this.tileHorizontal || this.tileVertical) {
                // Tiled rendering
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
                // Stretch to fit
                ctx.drawImage(this.backgroundSprite, 0, 0, this.width, this.height);
            }
        }
        
        // Render all instances
        this.instances.forEach(inst => inst.render(ctx));
    }
}

class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.rooms = {};
        this.currentRoom = null;
        this.running = false;
        this.paused = false;
        
        // Keyboard state
        this.keys = {};
        this.keysPressed = {};
        
        // FPS tracking
        this.fps = 0;
        this.frameCount = 0;
        this.lastFpsUpdate = Date.now();
        
        // Key repeat timing
        this.lastKeyTime = {
            'ArrowLeft': 0,
            'ArrowRight': 0,
            'ArrowUp': 0,
            'ArrowDown': 0
        };
        this.keyRepeatDelay = 200; // ms between repeats
        
        this.setupKeyboard();
        this.loadGame();
    }
    
    setupKeyboard() {
        // Keyboard event listeners
        window.addEventListener('keydown', (e) => {
            // Prevent arrow key scrolling
            if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Space'].includes(e.code)) {
                e.preventDefault();
            }
            
            this.keys[e.code] = true;
            
            // Track when key was first pressed
            if (!this.keysPressed[e.code]) {
                this.keysPressed[e.code] = true;
            }
            
            // Special keys
            if (e.code === 'Escape') {
                this.togglePause();
            }
        });
        
        window.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
            this.keysPressed[e.code] = false;
            
            // Reset key timing when released
            if (this.lastKeyTime[e.code] !== undefined) {
                this.lastKeyTime[e.code] = 0;
            }
        });
    }
    
    loadGame() {
        console.log('Loading game...');
        
        // Load sprites
        const sprites = {};
        let loadedCount = 0;
        const totalSprites = Object.keys(spritesData).length;
        
        Object.keys(spritesData).forEach(name => {
            const img = new Image();
            img.onload = () => {
                loadedCount++;
                if (loadedCount === totalSprites) {
                    console.log(`Loaded ${loadedCount} sprites`);
                }
            };
            img.src = spritesData[name];
            sprites[name] = img;
        });
        
        // Load rooms
        const roomsData = gameData.assets.rooms;
        for (const [roomName, roomData] of Object.entries(roomsData)) {
            const room = new GameRoom(roomData);
            
            // Set background sprite if specified
            if (room.bgImage && sprites[room.bgImage]) {
                room.backgroundSprite = sprites[room.bgImage];
            }
            
            // Create instances
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
                
                // Assign sprite
                if (objectData && objectData.sprite && sprites[objectData.sprite]) {
                    inst.sprite = sprites[objectData.sprite];
                }
                
                room.instances.push(inst);
            });
            
            this.rooms[roomName] = room;
            console.log(`Loaded room: ${roomName} (${room.instances.length} instances)`);
        }
        
        // Start with first room
        const firstRoom = Object.keys(this.rooms)[0];
        if (firstRoom) {
            this.currentRoom = this.rooms[firstRoom];
            console.log(`Starting room: ${firstRoom}`);
        }
    }
    
    start() {
        this.running = true;
        this.gameLoop();
    }
    
    gameLoop() {
        if (!this.running) return;
        
        // Update FPS counter
        this.frameCount++;
        const now = Date.now();
        if (now - this.lastFpsUpdate >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastFpsUpdate = now;
            document.getElementById('fps').textContent = `FPS: ${this.fps}`;
        }
        
        if (!this.paused) {
            // Process keyboard input
            this.processKeyboard();
            
            // Update game state
            if (this.currentRoom) {
                this.currentRoom.step(this);
            }
            
            // Check collisions
            this.checkCollisions();
        }
        
        // Render
        if (this.currentRoom) {
            this.currentRoom.render(this.ctx);
        }
        
        // Draw pause overlay
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
        
        this.currentRoom.instances.forEach(inst => {
            if (inst.toDestroy || !inst.events) return;
            
            const keyboardEvents = inst.events.keyboard || inst.events.keyboard_press || {};
            
            // Process arrow keys with timing
            const keyMap = {
                'ArrowLeft': 'left',
                'ArrowRight': 'right',
                'ArrowUp': 'up',
                'ArrowDown': 'down'
            };
            
            for (const [keyCode, direction] of Object.entries(keyMap)) {
                if (this.keys[keyCode] && now - this.lastKeyTime[keyCode] >= this.keyRepeatDelay) {
                    if (keyboardEvents[direction]) {
                        const actions = keyboardEvents[direction].actions || [];
                        actions.forEach(action => inst.executeAction(action, this));
                        this.lastKeyTime[keyCode] = now;
                    }
                }
            }
        });
    }
    
    checkCollisions() {
        if (!this.currentRoom) return;
        
        const instances = this.currentRoom.instances;
        
        for (let i = 0; i < instances.length; i++) {
            const inst1 = instances[i];
            if (inst1.toDestroy || inst1.solid) continue;
            
            // Check if moving
            const isMoving = inst1.speed > 0 || 
                           (inst1.targetX !== null && inst1.targetY !== null);
            
            if (!isMoving) continue;
            
            for (let j = 0; j < instances.length; j++) {
                if (i === j) continue;
                
                const inst2 = instances[j];
                if (inst2.toDestroy) continue;
                
                if (inst1.checkCollision(inst2)) {
                    // Collision detected!
                    const collisionKey = `${inst1.name}_${inst2.name}`;
                    const lastTime = inst1.collisionTimes[collisionKey] || 0;
                    const now = Date.now();
                    
                    if (now - lastTime >= 200) {
                        inst1.collisionTimes[collisionKey] = now;
                        
                        // Execute collision event
                        const eventKey = `collision_with_${inst2.name}`;
                        if (inst1.events[eventKey]) {
                            inst1.executeEvent(eventKey, this);
                        } else if (inst1.events.collision) {
                            inst1.executeEvent('collision', this);
                        }
                    }
                }
            }
        }
    }
    
    changeRoom(roomName) {
        if (this.rooms[roomName]) {
            console.log(`Changing to room: ${roomName}`);
            this.currentRoom = this.rooms[roomName];
            
            // Resize canvas if needed
            this.canvas.width = this.currentRoom.width;
            this.canvas.height = this.currentRoom.height;
        }
    }
    
    togglePause() {
        this.paused = !this.paused;
        const pauseBtn = document.getElementById('pauseBtn');
        pauseBtn.textContent = this.paused ? '▶️ Resume' : '⏸️ Pause';
    }
    
    restart() {
        // Reload the page to restart
        window.location.reload();
    }
}

// Start game when page loads
window.addEventListener('load', () => {
    window.game = new Game();
    window.game.start();
    console.log('Game started!');
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
            
            # Encode sprites as base64
            print(f"  📸 Encoding sprites...")
            sprites_data = self.encode_sprites(project_path, project_data)
            print(f"  ✓ Encoded {len(sprites_data)} sprites")
            
            # Get window size
            settings = project_data.get('settings', {})
            width = settings.get('window_width', 1024)
            height = settings.get('window_height', 768)
            
            # Generate HTML
            print(f"  🎨 Generating HTML...")
            html_content = self.template_html.format(
                game_name=project_data['name'],
                width=width,
                height=height,
                game_data=json.dumps(project_data, indent=2),
                sprites_data=json.dumps(sprites_data),
                engine_code=self.engine_code
            )
            
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