#!/usr/bin/env python3
"""
Fixtures-specific configuration and helpers
"""

import pytest
import json
from pathlib import Path
from PIL import Image


@pytest.fixture
def complete_sample_project(temp_dir, sample_sprite_file, sample_sound_file):
    """
    Create a complete sample project with assets and project file.
    """
    project_path = temp_dir / "complete_project"
    project_path.mkdir()

    # Create directories
    for dirname in ["sprites", "sounds", "backgrounds", "objects",
                    "rooms", "scripts", "fonts", "data", "thumbnails"]:
        (project_path / dirname).mkdir()

    # Copy test assets
    import shutil
    sprite_dest = project_path / "sprites" / "player.png"
    sound_dest = project_path / "sounds" / "jump.wav"
    shutil.copy(sample_sprite_file, sprite_dest)
    shutil.copy(sample_sound_file, sound_dest)

    # Create project.json
    project_data = {
        "version": "1.0.0",
        "name": "CompleteProject",
        "created": "2024-01-01T00:00:00",
        "modified": "2024-01-01T00:00:00",
        "settings": {
            "width": 800,
            "height": 600,
            "fps": 60
        },
        "sprites": {
            "player": {
                "name": "player",
                "path": "sprites/player.png",
                "width": 64,
                "height": 64
            }
        },
        "sounds": {
            "jump": {
                "name": "jump",
                "path": "sounds/jump.wav"
            }
        },
        "backgrounds": {},
        "objects": {
            "obj_player": {
                "name": "obj_player",
                "sprite": "player",
                "events": {
                    "create": {
                        "actions": []
                    }
                }
            }
        },
        "rooms": {
            "room_main": {
                "name": "room_main",
                "width": 800,
                "height": 600,
                "instances": []
            }
        },
        "scripts": {},
        "fonts": {},
        "data": {}
    }

    project_file = project_path / "project.json"
    with open(project_file, 'w') as f:
        json.dump(project_data, f, indent=2)

    return project_path


@pytest.fixture
def multiple_test_images(temp_dir):
    """
    Create multiple test images in different formats.
    Returns a dict of format -> path.
    """
    images = {}

    # PNG
    png_path = temp_dir / "test.png"
    Image.new('RGB', (50, 50), color='red').save(png_path)
    images['png'] = png_path

    # JPEG
    jpg_path = temp_dir / "test.jpg"
    Image.new('RGB', (50, 50), color='green').save(jpg_path)
    images['jpg'] = jpg_path

    # BMP
    bmp_path = temp_dir / "test.bmp"
    Image.new('RGB', (50, 50), color='blue').save(bmp_path)
    images['bmp'] = bmp_path

    return images
