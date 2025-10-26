#!/usr/bin/env python3
"""
PyGameMaker Runtime Engine
Executes games created in the IDE using Pygame
"""

import pygame
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import math


class GameObject:
    """Represents a game object instance in the runtime"""
    
    def __init__(self, object_name: str, x: float, y: float, object_data: Dict[str, Any]):
        self.name = object_name
        self.x = x
        self.y = y
        self.object_data = object_data
        
        # Object properties
        self.sprite_name = object_data.get('sprite', '')
        self.visible = object_data.get('visible', True)
        self.solid = object_data.get('solid', False)
        self.persistent = object_data.get('persistent', False)
        
        # Runtime properties
        self.speed = 0.0
        self.direction = 0.0
        self.image_angle = 0.0
        self.image_scale_x = 1.0
        self.image_scale_y = 1.0
        
        # Sprite and rendering
        self.sprite_surface = None
        self.sprite_rect = None
        
        # Events
        self.events = object_data.get('events', {})
        
        # State
        self.active = True
        self.to_destroy = False
    
    def load_sprite(self, sprites: Dict[str, pygame.Surface]):
        """Load sprite surface for rendering"""
        if self.sprite_name and self.sprite_name in sprites:
            self.sprite_surface = sprites[self.sprite_name]
            self.sprite_rect = self.sprite_surface.get_rect()
            self.sprite_rect.center = (self.x, self.y)
    
    def update_position(self):
        """Update position based on speed and direction"""
        if self.speed > 0:
            self.x += math.cos(math.radians(self.direction)) * self.speed
            self.y -= math.sin(math.radians(self.direction)) * self.speed
            
            if self.sprite_rect:
                self.sprite_rect.center = (self.x, self.y)
    
    def execute_event(self, event_name: str, game_engine):
        """Execute an event for this object"""
        if event_name in self.events:
            event_data = self.events[event_name]
            actions = event_data.get('actions', [])
            
            for action in actions:
                self.execute_action(action, game_engine)
    
    def execute_action(self, action: str, game_engine):
        """Execute a specific action"""
        # Basic action implementations
        if action == "Move Fixed":
            self.speed = 2.0
            self.direction = 0  # Move right
        elif action == "Play Sound":
            # Sound playing would go here
            pass
        elif action == "Destroy Instance":
            self.to_destroy = True
        # Add more actions as needed
    
    def render(self, screen: pygame.Surface):
        """Render the object to screen"""
        if self.visible and self.sprite_surface and self.sprite_rect:
            screen.blit(self.sprite_surface, self.sprite_rect)


class GameRoom:
    """Represents a game room"""
    
    def __init__(self, room_name: str, room_data: Dict[str, Any]):
        self.name = room_name
        self.width = room_data.get('width', 1024)
        self.height = room_data.get('height', 768)
        self.background_color = room_data.get('background_color', '#87CEEB')
        self.instances = []
        
        # Convert hex color to RGB
        self.bg_color = self.hex_to_rgb(self.background_color)
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def add_instance(self, game_object: GameObject):
        """Add an object instance to the room"""
        self.instances.append(game_object)
    
    def update(self, game_engine):
        """Update all instances in the room"""
        # Execute Step events for all objects
        for instance in self.instances[:]:  # Copy list to avoid modification issues
            if instance.active:
                instance.execute_event('Step', game_engine)
                instance.update_position()
                
                # Remove destroyed instances
                if instance.to_destroy:
                    self.instances.remove(instance)
    
    def render(self, screen: pygame.Surface):
        """Render the room and all instances"""
        # Fill background
        screen.fill(self.bg_color)
        
        # Render all visible instances
        for instance in self.instances:
            if instance.active:
                instance.render(screen)


class GameEngine:
    """Main game engine class"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_data = None
        self.sprites = {}
        self.sounds = {}
        self.objects = {}
        self.rooms = {}
        self.current_room = None
        
        # Pygame initialization with error handling
        try:
            pygame.init()
            # Initialize mixer separately for better error handling
            pygame.mixer.init()
        except Exception as e:
            print(f"Warning: Pygame initialization issue: {e}")
        
        # Game state
        self.running = True
        self.clock = pygame.time.Clock()
        self.screen = None
        self.paused = False  # Add this for message box
        self.message_box_active = False  # Add this for message box
        
        # Load project data
        self.load_project()
    
    def load_project(self):
        """Load project data and assets"""
        project_file = self.project_path / "project.json"
        
        if not project_file.exists():
            raise FileNotFoundError(f"Project file not found: {project_file}")
        
        with open(project_file, 'r') as f:
            self.project_data = json.load(f)
        
        print(f"Loaded project: {self.project_data['name']}")
        
        # Load assets
        self.load_sprites()
        self.load_sounds()
        self.load_objects()
        self.load_rooms()
    
    def load_sprites(self):
        """Load all sprite assets"""
        assets = self.project_data.get('assets', {})
        sprites_data = assets.get('sprites', {})
        
        for sprite_name, sprite_data in sprites_data.items():
            sprite_path = sprite_data.get('project_path', '')
            
            if sprite_path and Path(sprite_path).exists():
                try:
                    surface = pygame.image.load(sprite_path)
                    self.sprites[sprite_name] = surface
                    print(f"Loaded sprite: {sprite_name}")
                except pygame.error as e:
                    print(f"Failed to load sprite {sprite_name}: {e}")
            else:
                print(f"Sprite file not found: {sprite_name} at {sprite_path}")
    
    def load_sounds(self):
        """Load all sound assets"""
        # Sound loading implementation
        pass
    
    def load_objects(self):
        """Load all object definitions"""
        assets = self.project_data.get('assets', {})
        self.objects = assets.get('objects', {})
        print(f"Loaded {len(self.objects)} object definitions")
    
    def load_rooms(self):
        """Load all room definitions"""
        assets = self.project_data.get('assets', {})
        rooms_data = assets.get('rooms', {})
        
        for room_name, room_data in rooms_data.items():
            room = GameRoom(room_name, room_data)
            
            # Create instances from room data
            instances_data = room_data.get('instances', [])
            for instance_data in instances_data:
                object_name = instance_data.get('object_name', '')
                x = instance_data.get('x', 0)
                y = instance_data.get('y', 0)
                
                if object_name in self.objects:
                    game_object = GameObject(object_name, x, y, self.objects[object_name])
                    game_object.load_sprite(self.sprites)
                    room.add_instance(game_object)
            
            self.rooms[room_name] = room
            print(f"Loaded room: {room_name} with {len(instances_data)} instances")
    
    def start_game(self):
        """Start the game with the first room"""
        if not self.rooms:
            print("No rooms found in project")
            return
        
        try:
            # Use first room as starting room
            room_name = list(self.rooms.keys())[0]
            self.current_room = self.rooms[room_name]
            
            # Initialize display with error handling
            screen_size = (self.current_room.width, self.current_room.height)
            self.screen = pygame.display.set_mode(screen_size)
            pygame.display.set_caption(f"PyGameMaker - {self.project_data['name']}")
            
            # Store window dimensions for message box
            self.window_width = self.current_room.width
            self.window_height = self.current_room.height
            
            print(f"Starting game in room: {room_name}")
            print(f"Room size: {screen_size}")
            
            # Execute Create events for all instances
            for instance in self.current_room.instances:
                instance.execute_event('Create', self)
            
            # Start game loop
            self.game_loop()
        
        except Exception as e:
            print(f"Error starting game: {e}")
            import traceback
            traceback.print_exc()
            self.cleanup()
    
    def game_loop(self):
        """Main game loop"""
        try:
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                
                # Update game state
                if self.current_room:
                    self.current_room.update(self)
                
                # Render
                if self.current_room:
                    self.current_room.render(self.screen)
                
                pygame.display.flip()
                self.clock.tick(60)  # 60 FPS
        
        except KeyboardInterrupt:
            print("Game interrupted by user")
        except Exception as e:
            print(f"Error in game loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Safe cleanup
            self.cleanup()

    def cleanup(self):
        """Safe cleanup of pygame resources"""
        print("Stopping game...")
        
        try:
            # Stop mixer first
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except:
            pass
        
        try:
            # Quit pygame display
            if pygame.display.get_init():
                pygame.display.quit()
        except:
            pass
        
        try:
            # Final pygame quit
            pygame.quit()
        except:
            pass
        
        print("Game cleanup complete")

    def show_message_box(self, message: str, title: str = "Message", button_text: str = "OK"):
        """Show a message box overlay that pauses the game"""
        import pygame
        
        # Store the current game state
        self.message_box_active = True
        self.paused = True
        
        # Message box dimensions
        box_width = 400
        box_height = 200
        box_x = (self.window_width - box_width) // 2
        box_y = (self.window_height - box_height) // 2
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        
        # Message box loop
        font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 32)
        
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting_for_input = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        waiting_for_input = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicked on button
                    mouse_x, mouse_y = event.pos
                    button_rect = pygame.Rect(box_x + 150, box_y + 150, 100, 30)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        waiting_for_input = False
            
            # Draw the current game state (frozen)
            # This should show the last rendered frame
            
            # Draw overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw message box
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, (0, 0, 0), 
                            (box_x, box_y, box_width, box_height), 3)
            
            # Draw title
            title_surface = title_font.render(title, True, (0, 0, 0))
            title_rect = title_surface.get_rect(centerx=box_x + box_width//2, y=box_y + 20)
            self.screen.blit(title_surface, title_rect)
            
            # Draw message (word wrap if needed)
            words = message.split(' ')
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] > box_width - 40:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw message lines
            y_offset = 70
            for line in lines[:3]:  # Max 3 lines
                text_surface = font.render(line, True, (0, 0, 0))
                text_rect = text_surface.get_rect(centerx=box_x + box_width//2, y=box_y + y_offset)
                self.screen.blit(text_surface, text_rect)
                y_offset += 30
            
            # Draw button
            button_rect = pygame.Rect(box_x + 150, box_y + 150, 100, 30)
            pygame.draw.rect(self.screen, (200, 200, 200), button_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
            
            button_surface = font.render(button_text, True, (0, 0, 0))
            button_text_rect = button_surface.get_rect(center=button_rect.center)
            self.screen.blit(button_surface, button_text_rect)
            
            pygame.display.flip()
            self.clock.tick(30)  # Lower FPS while paused
        
        # Resume game
        self.paused = False
        self.message_box_active = False


def run_game(project_path: str):
    """Run a game from a project path"""
    engine = None
    try:
        engine = GameEngine(project_path)
        engine.start_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure cleanup even if engine creation failed
        if engine:
            try:
                engine.cleanup()
            except:
                pass
        
        # Double-check pygame is quit
        try:
            pygame.quit()
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python game_engine.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    run_game(project_path)