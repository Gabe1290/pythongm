#!/usr/bin/env python3
"""
Resource Packager for PyGameMaker IDE
Exports/imports individual resources (rooms, objects) with all dependencies
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import shutil


class ResourcePackager:
    """Package and unpackage individual resources with dependencies"""
    
    PACKAGE_VERSION = "1.0.0"
    
    @staticmethod
    def export_object(project_path: Path, object_name: str, output_path: Path) -> bool:
        """
        Export an object with all its sprite dependencies
        
        Args:
            project_path: Path to current project
            object_name: Name of object to export
            output_path: Path to output .gmobj file
            
        Returns:
            True if successful
        """
        try:
            # Load project data
            project_file = project_path / "project.json"
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Get object data
            objects = project_data.get('assets', {}).get('objects', {})
            if object_name not in objects:
                print(f"Object '{object_name}' not found")
                return False
            
            object_data = objects[object_name]
            
            # Collect dependencies (sprites)
            dependencies = ResourcePackager._collect_object_dependencies(
                object_data, project_data, project_path
            )
            
            # Create package
            package_data = {
                "version": ResourcePackager.PACKAGE_VERSION,
                "type": "object",
                "created": datetime.now().isoformat(),
                "object": object_data,
                "dependencies": dependencies
            }
            
            # Ensure output has correct extension
            if not output_path.suffix == '.gmobj':
                output_path = output_path.with_suffix('.gmobj')
            
            # Create zip package
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add package metadata
                zipf.writestr('package.json', json.dumps(package_data, indent=2))
                
                # Add sprite files if they exist
                sprite_name = object_data.get('sprite', '')
                if sprite_name and sprite_name in dependencies.get('sprites', {}):
                    sprite_path = project_path / 'sprites' / f"{sprite_name}.png"
                    if sprite_path.exists():
                        zipf.write(sprite_path, f'sprites/{sprite_name}.png')
                        print(f"  Added sprite: {sprite_name}.png")
            
            print(f"✅ Object exported to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting object: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def export_room(project_path: Path, room_name: str, output_path: Path) -> bool:
        """
        Export a room with all its dependencies (objects, sprites, backgrounds)

        Args:
            project_path: Path to current project
            room_name: Name of room to export
            output_path: Path to output .gmroom file

        Returns:
            True if successful
        """
        try:
            # Load project data
            project_file = project_path / "project.json"
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # Get room data
            rooms = project_data.get('assets', {}).get('rooms', {})
            if room_name not in rooms:
                print(f"Room '{room_name}' not found")
                return False

            room_data = rooms[room_name].copy()  # Make a copy to avoid modifying original

            # Load instances from separate room file if it exists
            # (instances are stored in rooms/<room_name>.json, not in project.json)
            room_file = project_path / "rooms" / f"{room_name}.json"
            if room_file.exists():
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        file_room_data = json.load(f)
                    if 'instances' in file_room_data:
                        room_data['instances'] = file_room_data['instances']
                        print(f"  Loaded {len(room_data['instances'])} instances from room file")
                except Exception as e:
                    print(f"  ⚠️ Failed to load room file: {e}")
            
            # Collect dependencies (objects, sprites, backgrounds)
            dependencies = ResourcePackager._collect_room_dependencies(
                room_data, project_data, project_path
            )
            
            # Create package
            package_data = {
                "version": ResourcePackager.PACKAGE_VERSION,
                "type": "room",
                "created": datetime.now().isoformat(),
                "room": room_data,
                "dependencies": dependencies
            }
            
            # Ensure output has correct extension
            if not output_path.suffix == '.gmroom':
                output_path = output_path.with_suffix('.gmroom')
            
            # Create zip package
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add package metadata
                zipf.writestr('package.json', json.dumps(package_data, indent=2))
                
                # Add background if it exists
                background = room_data.get('background_image', '')
                if background and background in dependencies.get('backgrounds', {}):
                    bg_path = project_path / 'backgrounds' / f"{background}.png"
                    if bg_path.exists():
                        zipf.write(bg_path, f'backgrounds/{background}.png')
                        print(f"  Added background: {background}.png")
                
                # Add sprites for all objects
                for sprite_name in dependencies.get('sprites', {}).keys():
                    sprite_path = project_path / 'sprites' / f"{sprite_name}.png"
                    if sprite_path.exists():
                        zipf.write(sprite_path, f'sprites/{sprite_name}.png')
                        print(f"  Added sprite: {sprite_name}.png")
            
            print(f"✅ Room exported to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting room: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def import_object(package_path: Path, project_path: Path) -> Optional[str]:
        """
        Import an object package into a project
        
        Args:
            package_path: Path to .gmobj file
            project_path: Path to target project
            
        Returns:
            Name of imported object, or None on failure
        """
        try:
            # Validate package
            if not zipfile.is_zipfile(package_path):
                print("Not a valid package file")
                return None
            
            # Extract package data
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Read package metadata
                with zipf.open('package.json') as f:
                    package_data = json.load(f)
                
                # Validate package type
                if package_data.get('type') != 'object':
                    print("Package is not an object")
                    return None
                
                object_data = package_data['object']
                object_name = object_data['name']
                dependencies = package_data.get('dependencies', {})
                
                print(f"📦 Importing object: {object_name}")
                
                # Load target project data
                project_file = project_path / "project.json"
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                # Check for name conflicts
                objects = project_data.get('assets', {}).get('objects', {})
                if object_name in objects:
                    # Generate unique name
                    base_name = object_name
                    counter = 1
                    while object_name in objects:
                        object_name = f"{base_name}_{counter}"
                        counter += 1
                    object_data['name'] = object_name
                    print(f"  ⚠️  Renamed to: {object_name} (name conflict)")
                
                # Import sprite dependencies
                for sprite_name, sprite_data in dependencies.get('sprites', {}).items():
                    # Check if sprite already exists
                    sprites = project_data.get('assets', {}).get('sprites', {})
                    if sprite_name not in sprites:
                        # Extract sprite file
                        sprite_file = f'sprites/{sprite_name}.png'
                        if sprite_file in zipf.namelist():
                            sprite_dest = project_path / 'sprites' / f"{sprite_name}.png"
                            sprite_dest.parent.mkdir(exist_ok=True)
                            
                            with zipf.open(sprite_file) as src:
                                with open(sprite_dest, 'wb') as dst:
                                    dst.write(src.read())
                            
                            # Add sprite to project
                            sprites[sprite_name] = sprite_data
                            print(f"  ✅ Imported sprite: {sprite_name}")
                        else:
                            print(f"  ⚠️  Sprite file not found: {sprite_name}")
                    else:
                        print(f"  ℹ️  Sprite already exists: {sprite_name}")
                
                # Add object to project
                objects[object_name] = object_data
                
                # Save updated project
                with open(project_file, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Object imported successfully: {object_name}")
                return object_name
                
        except Exception as e:
            print(f"❌ Error importing object: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def import_room(package_path: Path, project_path: Path) -> Optional[str]:
        """
        Import a room package into a project
        
        Args:
            package_path: Path to .gmroom file
            project_path: Path to target project
            
        Returns:
            Name of imported room, or None on failure
        """
        try:
            # Validate package
            if not zipfile.is_zipfile(package_path):
                print("Not a valid package file")
                return None
            
            # Extract package data
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Read package metadata
                with zipf.open('package.json') as f:
                    package_data = json.load(f)
                
                # Validate package type
                if package_data.get('type') != 'room':
                    print("Package is not a room")
                    return None
                
                room_data = package_data['room']
                room_name = room_data['name']
                dependencies = package_data.get('dependencies', {})
                
                print(f"📦 Importing room: {room_name}")
                
                # Load target project data
                project_file = project_path / "project.json"
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                # Check for name conflicts
                rooms = project_data.get('assets', {}).get('rooms', {})
                if room_name in rooms:
                    # Generate unique name
                    base_name = room_name
                    counter = 1
                    while room_name in rooms:
                        room_name = f"{base_name}_{counter}"
                        counter += 1
                    room_data['name'] = room_name
                    print(f"  ⚠️  Renamed to: {room_name} (name conflict)")
                
                # Import background dependencies
                for bg_name, bg_data in dependencies.get('backgrounds', {}).items():
                    backgrounds = project_data.get('assets', {}).get('backgrounds', {})
                    if bg_name not in backgrounds:
                        # Extract background file
                        bg_file = f'backgrounds/{bg_name}.png'
                        if bg_file in zipf.namelist():
                            bg_dest = project_path / 'backgrounds' / f"{bg_name}.png"
                            bg_dest.parent.mkdir(exist_ok=True)
                            
                            with zipf.open(bg_file) as src:
                                with open(bg_dest, 'wb') as dst:
                                    dst.write(src.read())
                            
                            backgrounds[bg_name] = bg_data
                            print(f"  ✅ Imported background: {bg_name}")
                
                # Import object dependencies
                for obj_name, obj_data in dependencies.get('objects', {}).items():
                    objects = project_data.get('assets', {}).get('objects', {})
                    if obj_name not in objects:
                        objects[obj_name] = obj_data
                        print(f"  ✅ Imported object: {obj_name}")
                
                # Import sprite dependencies
                for sprite_name, sprite_data in dependencies.get('sprites', {}).items():
                    sprites = project_data.get('assets', {}).get('sprites', {})
                    if sprite_name not in sprites:
                        # Extract sprite file
                        sprite_file = f'sprites/{sprite_name}.png'
                        if sprite_file in zipf.namelist():
                            sprite_dest = project_path / 'sprites' / f"{sprite_name}.png"
                            sprite_dest.parent.mkdir(exist_ok=True)
                            
                            with zipf.open(sprite_file) as src:
                                with open(sprite_dest, 'wb') as dst:
                                    dst.write(src.read())
                            
                            sprites[sprite_name] = sprite_data
                            print(f"  ✅ Imported sprite: {sprite_name}")
                
                # Add room to project
                rooms[room_name] = room_data
                
                # Save updated project
                with open(project_file, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Room imported successfully: {room_name}")
                return room_name
                
        except Exception as e:
            print(f"❌ Error importing room: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _collect_object_dependencies(object_data: Dict, project_data: Dict, project_path: Path) -> Dict:
        """Collect all dependencies for an object"""
        dependencies = {
            'sprites': {}
        }
        
        # Get sprite
        sprite_name = object_data.get('sprite', '')
        if sprite_name:
            sprites = project_data.get('assets', {}).get('sprites', {})
            if sprite_name in sprites:
                dependencies['sprites'][sprite_name] = sprites[sprite_name]
        
        return dependencies
    
    @staticmethod
    def _collect_room_dependencies(room_data: Dict, project_data: Dict, project_path: Path) -> Dict:
        """Collect all dependencies for a room"""
        dependencies = {
            'objects': {},
            'sprites': {},
            'backgrounds': {}
        }
        
        # Get background
        background = room_data.get('background_image', '')
        if background:
            backgrounds = project_data.get('assets', {}).get('backgrounds', {})
            if background in backgrounds:
                dependencies['backgrounds'][background] = backgrounds[background]
        
        # Get objects from instances
        instances = room_data.get('instances', [])
        objects = project_data.get('assets', {}).get('objects', {})
        sprites = project_data.get('assets', {}).get('sprites', {})
        
        for instance in instances:
            obj_name = instance.get('object_type', '')
            if obj_name and obj_name in objects:
                # Add object
                if obj_name not in dependencies['objects']:
                    obj_data = objects[obj_name]
                    dependencies['objects'][obj_name] = obj_data
                    
                    # Add object's sprite
                    sprite_name = obj_data.get('sprite', '')
                    if sprite_name and sprite_name in sprites:
                        dependencies['sprites'][sprite_name] = sprites[sprite_name]
        
        return dependencies