import sys
import os
import traceback

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import pygame
import json
from engine.game_object import GameObject
from engine.tileset import Tileset
from engine.camera import Camera

class GameRunner:
    def __init__(self, project_file):
        with open(project_file, 'r') as f:
            self.project_data = json.load(f)
        
        self.settings = self.project_data['settings']
        self.resources = self.project_data['resources']
        self.instances = []
        
        self.loaded_tilesets = {}
        self.tile_layers_to_draw = []
        
        self.room_bg_color = (0,0,0)
        self.room_bg_image = None
        self.room_bg_mode = "Tiled"
        self.room_bg_scroll_x = 1.0
        self.room_bg_scroll_y = 1.0
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.settings['screen_width'], self.settings['screen_height']))
        pygame.display.set_caption(self.project_data['project_name'])
        self.clock = pygame.time.Clock()

        self.camera = Camera(self.settings['screen_width'], self.settings['screen_height'])
        self.player_instance = None

    def get_resource_info(self, resource_type, name):
        for resource in self.resources.get(resource_type, []):
            if resource.get('name') == name:
                return resource
        return None

    def load_tilesets(self):
        for ts_info in self.resources.get('tilesets', []):
            self.loaded_tilesets[ts_info['name']] = Tileset(ts_info)

    def load_room(self, room_name):
        print(f"--- Loading room: {room_name} ---")
        if not self.loaded_tilesets: self.load_tilesets()

        room_info = self.get_resource_info('rooms', room_name)
        if not room_info: print(f"FATAL: Room '{room_name}' not found."); return False

        with open(room_info['definition_file'], 'r') as f:
            room_data = json.load(f)

        room_settings = room_data.get('settings', {})
        
        # --- UPDATED: Load all background properties from settings ---
        self.room_bg_color = room_settings.get('background_color', (0,0,0))
        self.room_bg_mode = room_settings.get('background_mode', 'Tiled')
        self.room_bg_scroll_x = room_settings.get('background_scroll_x', 1.0)
        self.room_bg_scroll_y = room_settings.get('background_scroll_y', 1.0)
        
        bg_image_name = room_settings.get('background_image')
        if bg_image_name and bg_image_name != "None":
            print(f"  - Loading background image: {bg_image_name}")
            bg_info = self.get_resource_info('backgrounds', bg_image_name)
            if bg_info:
                try:
                    self.room_bg_image = pygame.image.load(bg_info['path']).convert_alpha()
                except pygame.error as e:
                    print(f"  - ERROR loading background image '{bg_image_name}': {e}")
                    self.room_bg_image = None
        else:
            self.room_bg_image = None
            print("  - No background image specified for this room.")

        # --- World size and other loading logic is unchanged ---
        world_w = room_settings.get('width', self.settings['screen_width'])
        world_h = room_settings.get('height', self.settings['screen_height'])
        self.camera.set_world_size(world_w, world_h)
        print(f"DEBUG: World size set to {world_w}x{world_h}")
        
        self.tile_layers_to_draw = []
        for layer_data in room_data.get('tile_layers', []):
            tileset_name = layer_data.get('tileset')
            tileset = self.loaded_tilesets.get(tileset_name)
            if tileset: self.tile_layers_to_draw.append({"tileset": tileset, "tiles": layer_data.get('tiles', []), "depth": layer_data.get('depth', 10000)})
        self.tile_layers_to_draw.sort(key=lambda layer: layer['depth'], reverse=True)

        self.instances = []
        for inst_data in room_data.get('instances', []):
            obj_name = inst_data['object']
            obj_info = self.get_resource_info('objects', obj_name)
            if not obj_info: continue
            with open(obj_info['definition_file'], 'r') as f: object_definition = json.load(f)
            sprite_name = object_definition.get('sprite'); sprite_info = self.get_resource_info('sprites', sprite_name)
            if not sprite_info: continue
            new_instance = GameObject(object_definition, sprite_info['path']); new_instance.set_position(inst_data['x'], inst_data['y']); self.instances.append(new_instance)
            if obj_name == 'obj_player': self.player_instance = new_instance; self.camera.follow(self.player_instance.rect)
        print("--- Room Load Complete ---")
        return True

    def run(self):
        if not self.load_room(self.project_data['start_room']):
            print("Halting due to room load failure."); return

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
            
            keys = pygame.key.get_pressed()
            for instance in self.instances: instance.update(keys, self.instances)
            self.camera.update()

            # --- UPDATED DRAWING LOGIC ---
            self.screen.fill(self.room_bg_color)
            if self.room_bg_image:
                if self.room_bg_mode == "Stretched":
                    stretched_bg = pygame.transform.scale(self.room_bg_image, (self.settings['screen_width'], self.settings['screen_height']))
                    self.screen.blit(stretched_bg, (0, 0))
                else: # Tiled or Fixed
                    bg_width, bg_height = self.room_bg_image.get_size()
                    if bg_width > 0 and bg_height > 0:
                        start_x = (-self.camera.rect.x * self.room_bg_scroll_x)
                        start_y = (-self.camera.rect.y * self.room_bg_scroll_y)
                        if self.room_bg_mode == "Tiled":
                            start_x %= bg_width; start_y %= bg_height
                            x = start_x - bg_width
                            while x < self.settings['screen_width']:
                                y = start_y - bg_height
                                while y < self.settings['screen_height']: self.screen.blit(self.room_bg_image, (x, y)); y += bg_height
                                x += bg_width
                        else: # "Fixed" mode (but with parallax)
                            self.screen.blit(self.room_bg_image, (start_x, start_y))

            for layer in self.tile_layers_to_draw:
                tileset = layer['tileset']
                for row_index, row in enumerate(layer['tiles']):
                    for col_index, tile_id in enumerate(row):
                        if tile_id != -1:
                            if tile_surface := tileset.get_tile(tile_id):
                                pos = (col_index * tileset.tile_width, row_index * tileset.tile_height)
                                self.screen.blit(tile_surface, self.camera.apply_offset_to_pos(pos))
            for instance in self.instances:
                offset_rect = self.camera.apply_offset(instance.rect)
                self.screen.blit(instance.sprite_image, offset_rect)
            
            pygame.display.flip()
            self.clock.tick(self.settings['fps'])
        pygame.quit()

if __name__ == '__main__':
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        game = GameRunner('my_game.json')
        game.run()
    except Exception as e:
        print("!!! A FATAL ERROR OCCURRED !!!"); print(f"ERROR: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")