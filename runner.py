# runner.py
import pygame
import json
from engine.game_object import GameObject

class GameRunner:
    def __init__(self, project_file):
        with open(project_file, 'r') as f:
            self.project_data = json.load(f)

        self.settings = self.project_data['settings']
        self.resources = self.project_data['resources']
        self.instances = []

        pygame.init()
        self.screen = pygame.display.set_mode((self.settings['screen_width'], self.settings['screen_height']))
        pygame.display.set_caption(self.project_data['project_name'])
        self.clock = pygame.time.Clock()

    def get_resource_path(self, resource_type, name):
        """Finds the path for a given resource name."""
        for resource in self.resources[resource_type]:
            if resource['name'] == name:
                return resource['path']
        return None

    def load_room(self, room_name):
        print(f"Loading room: {room_name}")
        # For simplicity, we'll hardcode the room file for now
        # A real implementation would look up the file in project_data
        with open('rooms/room_main.json', 'r') as f:
            room_data = json.load(f)

        self.background_color = room_data['settings']['background_color']

        # Create instances from the room data
        for inst_data in room_data['instances']:
            obj_name = inst_data['object']

            # Find the object definition file
            obj_def_path = None
            for obj_res in self.resources['objects']:
                if obj_res['name'] == obj_name:
                    obj_def_path = obj_res['definition_file']
                    break

            if not obj_def_path:
                print(f"Warning: Object '{obj_name}' not found in project resources.")
                continue

            # Load the object's definition
            with open(obj_def_path, 'r') as f:
                object_definition = json.load(f)

            # Find the sprite for this object
            sprite_name = object_definition['sprite']
            sprite_path = self.get_resource_path('sprites', sprite_name)

            # Create the GameObject
            new_instance = GameObject(object_definition, sprite_path)
            new_instance.set_position(inst_data['x'], inst_data['y'])
            self.instances.append(new_instance)

    def run(self):
        # Load the starting room
        self.load_room(self.project_data['start_room'])

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # --- Update ---
            # NEW: Get the state of all keyboard keys once per frame
            keys = pygame.key.get_pressed()

            # NEW: Pass the key state to each instance's update method
            for instance in self.instances:
                instance.update(keys, self.instances)

            # --- Draw ---
            self.screen.fill(self.background_color)
            for instance in self.instances:
                instance.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(self.settings['fps'])

        pygame.quit()


if __name__ == '__main__':
    game = GameRunner('my_game.json')
    game.run()
