"""
Project Data Adapter for Kivy Export - ULTIMATE VERSION
Works with your actual project structure where rooms/sprites/etc are in 'assets'
"""

import os
from core.logger import get_logger
from utils.color import to_kivy_rgba

logger = get_logger(__name__)


def parse_color(color_value):
    """Convert a color value to ``[R, G, B, A]`` floats (0.0 to 1.0).

    Delegates to :func:`utils.color.to_kivy_rgba`. Kept as the name the
    Kivy-exported code expects; see ``utils/color.py`` for the runtime
    0-255 counterpart.
    """
    return to_kivy_rgba(color_value)


def adapt_project_for_kivy_export(project_manager):
    """
    Adapt project data from PyGameMaker format to KivyExporter format

    Args:
        project_manager: Your ProjectManager instance with project loaded

    Returns:
        dict: Project data in format expected by KivyExporter
    """
    # Try different possible attribute names for the project data
    project = None
    project_path = None

    # Try to get project data
    for attr_name in ['current_project_data', 'current_project', 'project', 'project_data', 'data']:
        if hasattr(project_manager, attr_name):
            project = getattr(project_manager, attr_name)
            if isinstance(project, dict):
                logger.debug(f"Found project data in attribute: {attr_name}")
                break

    # An empty dict {} is a valid (if empty) project; only None / a
    # non-dict is 'not found' (finding #8 — `not project` rejected {}).
    if project is None or not isinstance(project, dict):
        raise ValueError("Could not find project data in ProjectManager")

    # Try to get project path
    for attr_name in ['project_path', 'path', 'project_dir', 'project_folder']:
        if hasattr(project_manager, attr_name):
            project_path = getattr(project_manager, attr_name)
            if project_path:
                break

    if not project_path:
        import os
        project_path = os.getcwd()

    logger.debug(f"Found project: {project.get('name', 'Unknown')}")
    logger.debug(f"Project path: {project_path}")
    logger.debug(f"Project keys: {list(project.keys())}")

    # Get project name
    project_name = project.get('name', 'MyGame')

    # YOUR STRUCTURE: Everything is in 'assets'!
    assets = project.get('assets', {})
    logger.debug(f"Assets keys: {list(assets.keys()) if assets else 'None'}")

    # Get rooms from assets
    rooms_data = {}
    rooms_source = assets.get('rooms', {})

    if isinstance(rooms_source, dict):
        for room_name, room_info in rooms_source.items():
            if isinstance(room_info, dict):
                rooms_data[room_name] = {
                    'width': room_info.get('width', 640),
                    'height': room_info.get('height', 480),
                    # Pass through verbatim (hex string in saved projects).
                    # KivyExporter normalizes via _bg_color_to_rgb; converting
                    # here to a float list crashed its .startswith() parse
                    # (audit H9).
                    'background_color': room_info.get('background_color', '#808080'),
                    'background_image': (room_info.get('background_image', '')
                                         or room_info.get('background', '')),
                    'tile_horizontal': room_info.get('tile_horizontal', False),
                    'tile_vertical': room_info.get('tile_vertical', False),
                    'instances': room_info.get('instances', [])
                }

    logger.debug(f"Found {len(rooms_data)} room(s)")

    # Get objects from assets
    objects_data = {}
    objects_source = assets.get('objects', {})

    if isinstance(objects_source, dict):
        objects_data = objects_source
        logger.debug(f"Found {len(objects_data)} object(s) in assets")

    # If still no objects, infer from room instances
    if not objects_data and rooms_data:
        logger.debug("Inferring objects from room instances...")
        object_types = set()

        for room_name, room_info in rooms_data.items():
            instances = room_info.get('instances', [])
            logger.debug(f"  Room '{room_name}': {len(instances)} instances")

            for instance in instances:
                obj_type = (instance.get('object_name') or
                           instance.get('object_type') or
                           instance.get('type') or
                           instance.get('object') or
                           instance.get('obj_type'))

                if obj_type:
                    object_types.add(obj_type)

        for obj_type in object_types:
            objects_data[obj_type] = {
                'sprite': '',
                'solid': False,
                'events': {}
            }

        logger.debug(f"Created {len(objects_data)} object definition(s) from instances")

    # Get sprites from assets
    sprites_data = {}
    sprites_source = assets.get('sprites', {})

    for sprite_name, sprite_info in sprites_source.items():
        if isinstance(sprite_info, dict):
            # Try multiple possible field names for the file path
            sprite_path = (sprite_info.get('file_path') or
                        sprite_info.get('path') or
                        sprite_info.get('image_path') or
                        sprite_info.get('source') or
                        '')
        else:
            sprite_path = str(sprite_info)

        # Make path absolute
        if sprite_path and not os.path.isabs(sprite_path):
            import os
            sprite_path = os.path.join(str(project_path), sprite_path)

        sprites_data[sprite_name] = {
            'file_path': sprite_path,  # Changed from 'path' to 'file_path'
            'path': sprite_path         # Keep both for compatibility
        }

    # Get sounds from assets
    sounds_data = {}
    sounds_source = assets.get('sounds', {})

    for sound_name, sound_info in sounds_source.items():
        if isinstance(sound_info, dict):
            sound_path = (sound_info.get('file_path') or
                        sound_info.get('path') or
                        sound_info.get('source') or
                        '')
        else:
            sound_path = str(sound_info)

        if sound_path and not os.path.isabs(sound_path):
            import os
            sound_path = os.path.join(str(project_path), sound_path)

        sounds_data[sound_name] = {
            'file_path': sound_path,
            'path': sound_path
        }

    # Get backgrounds from assets
    backgrounds_data = {}
    backgrounds_source = assets.get('backgrounds', {})

    for bg_name, bg_info in backgrounds_source.items():
        if isinstance(bg_info, dict):
            bg_path = (bg_info.get('file_path') or
                    bg_info.get('path') or
                    bg_info.get('image_path') or
                    bg_info.get('source') or
                    '')
        else:
            bg_path = str(bg_info)

        if bg_path and not os.path.isabs(bg_path):
            import os
            bg_path = os.path.join(str(project_path), bg_path)

        backgrounds_data[bg_name] = {
            'file_path': bg_path,
            'path': bg_path
        }

    # Get settings
    settings = project.get('settings', {})

    # Build adapted project data in the format KivyExporter expects
    adapted_data = {
        'name': project_name,
        'settings': settings,
        'assets': {
            'objects': objects_data,
            'rooms': rooms_data,
            'sprites': sprites_data,
            'sounds': sounds_data,
            'backgrounds': backgrounds_data,
        }
    }

    logger.debug("Adapted Project Data:")
    logger.debug(f"  - Name: {project_name}")
    logger.debug(f"  - Rooms: {len(rooms_data)}")
    logger.debug(f"  - Objects: {len(objects_data)}")
    logger.debug(f"  - Sprites: {len(sprites_data)}")
    logger.debug(f"  - Sounds: {len(sounds_data)}")
    logger.debug(f"  - Backgrounds: {len(backgrounds_data)}")
    logger.debug("Assets structure:")
    logger.debug(f"  - adapted_data['assets'] keys: {list(adapted_data['assets'].keys())}")
    for asset_type, asset_dict in adapted_data['assets'].items():
        if asset_dict:
            logger.debug(f"    - {asset_type}: {list(asset_dict.keys())[:5]}")  # Show first 5

    return adapted_data


def export_with_adapter(project_manager, output_path):
    """
    Complete export function with project adaptation

    Args:
        project_manager: Your ProjectManager instance
        output_path: Where to export the Kivy project

    Returns:
        bool: True if successful
    """
    from export.Kivy.kivy_exporter import KivyExporter
    import inspect

    try:
        # Adapt project data
        logger.info("Adapting project data for Kivy export...")
        adapted_project = adapt_project_for_kivy_export(project_manager)

        # Get project path
        project_path = None
        for attr_name in ['project_path', 'path', 'project_dir', 'project_folder']:
            if hasattr(project_manager, attr_name):
                project_path = getattr(project_manager, attr_name)
                if project_path:
                    break

        if not project_path:
            import os
            project_path = os.getcwd()

        # Check KivyExporter signature to determine which version we have
        sig = inspect.signature(KivyExporter.__init__)
        param_count = len(sig.parameters) - 1  # Subtract 'self'

        logger.info(f"Exporting to: {output_path}")
        logger.debug(f"KivyExporter expects {param_count} arguments")

        # Call with correct number of arguments
        if param_count == 2:
            # My earlier version: __init__(self, project_data, output_path)
            exporter = KivyExporter(adapted_project, str(output_path))
        elif param_count == 3:
            # Your uploaded version: __init__(self, project_data, project_path, output_path)
            exporter = KivyExporter(adapted_project, str(project_path), str(output_path))
        else:
            raise ValueError(f"Unexpected KivyExporter signature with {param_count} parameters")

        success = exporter.export()

        if success:
            logger.info("Export successful!")
            logger.info(f"Output: {output_path}")
            return True
        else:
            logger.error("Export failed")
            return False

    except Exception as e:
        logger.error(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        return False