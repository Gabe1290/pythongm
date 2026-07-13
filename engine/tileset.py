# engine/tileset.py
import pygame

class Tileset:
    def __init__(self, tileset_info):
        self.name = tileset_info['name']
        self.tile_width = tileset_info.get('tile_width', 32)
        self.tile_height = tileset_info.get('tile_height', 32)
        self.tiles = []

        try:
            # The path to the tileset image is relative to the project root
            image = pygame.image.load(tileset_info['path']).convert_alpha()
            img_width, img_height = image.get_size()
            
            # Slice the main image into individual tile surfaces
            for y in range(0, img_height, self.tile_height):
                for x in range(0, img_width, self.tile_width):
                    tile_surface = image.subsurface(pygame.Rect(x, y, self.tile_width, self.tile_height))
                    self.tiles.append(tile_surface)
                    
            print(f"Successfully loaded tileset '{self.name}' with {len(self.tiles)} tiles.")

        except pygame.error as e:
            print(f"Error loading tileset '{self.name}': {e}")

    def get_tile(self, tile_id):
        """Safely returns a tile surface by its ID, or None if the ID is invalid."""
        if 0 <= tile_id < len(self.tiles):
            return self.tiles[tile_id]
        return None