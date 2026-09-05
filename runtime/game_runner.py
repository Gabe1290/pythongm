#!/usr/bin/env python3
"""
Enhanced GameRunner with smooth movement that snaps to grid
"""

import os
import sys
# Force pygame to use software rendering to avoid conflicts with Qt
# Use appropriate video driver based on platform
if sys.platform == 'win32':
    os.environ['SDL_VIDEODRIVER'] = 'windows'
elif sys.platform == 'darwin':
    os.environ['SDL_VIDEODRIVER'] = 'cocoa'
else:  # Linux and other Unix-like systems
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    # Center the window on screen when launched from subprocess
    os.environ['SDL_VIDEO_CENTERED'] = '1'
os.environ['SDL_RENDER_DRIVER'] = 'software'

import pygame
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from runtime.action_executor import ActionExecutor
# pygame_key_name's only caller here, _get_key_name, moved to
# runtime/input_handler.py (File 3, cluster 4) -- no longer needed directly.
# GameSprite moved to runtime/sprite.py (docs/POST_1_0_REFACTOR.md File 3,
# the first cluster) -- re-exported here so the many existing
# `from runtime.game_runner import GameSprite` call sites (tests included)
# keep working unchanged.
from runtime.sprite import GameSprite
from utils.project_file_merge import merge_room_file, merge_object_file
from events.plugin_loader import load_all_plugins
from runtime import extension_hooks
from config.blockly_translations import get_runtime_translation
from runtime.thymio_renderer import ThymioRenderer
from runtime.thymio_action_handlers import register_thymio_actions
from core.logger import get_logger
logger = get_logger(__name__)

# Translation strings for game caption (key: language code)
CAPTION_TRANSLATIONS = {
    'en': {'score': 'Score', 'lives': 'Lives', 'health': 'Health', 'room': 'Room'},
    'de': {'score': 'Punkte', 'lives': 'Leben', 'health': 'Gesundheit', 'room': 'Raum'},
    'es': {'score': 'Puntuación', 'lives': 'Vidas', 'health': 'Salud', 'room': 'Sala'},
    'fr': {'score': 'Score', 'lives': 'Vies', 'health': 'Santé', 'room': 'Niveau'},
    'it': {'score': 'Punteggio', 'lives': 'Vite', 'health': 'Salute', 'room': 'Stanza'},
    'ru': {'score': 'Очки', 'lives': 'Жизни', 'health': 'Здоровье', 'room': 'Комната'},
    'sl': {'score': 'Točke', 'lives': 'Življenja', 'health': 'Zdravje', 'room': 'Soba'},
    'uk': {'score': 'Рахунок', 'lives': 'Життя', 'health': 'Здоров\'я', 'room': 'Кімната'},
}

# Properties that always come from the child's own data, never inherited.
# 'sprite' / 'visible' / 'solid' / 'persistent' / 'remember_destroyed' are
# deliberately child-only: they default to engine values when the child
# doesn't set them, instead of silently picking up a parent's value.
_CHILD_ONLY_OBJECT_PROPS = frozenset({
    'sprite', 'visible', 'solid', 'persistent', 'remember_destroyed',
})

# Keys that aren't user-facing properties (identity / structure / metadata),
# plus 'events' which is merged separately with closest-parent-wins semantics.
_NON_INHERITABLE_OBJECT_KEYS = frozenset({
    'name', 'asset_type', 'parent', 'imported', 'created', 'modified', 'events',
})


def resolve_parent_inheritance(object_data: dict, objects: Dict[str, dict]) -> dict:
    """Resolve a child object's data against its parent chain.

    Events: a child inherits any event type its ancestors define and it doesn't.
    Closest parent wins among ancestors; the child always overrides.

    Properties: a child inherits any property its ancestors define that the
    child itself doesn't set (key missing or value is None), with one exception
    — 'sprite', 'visible', 'solid', 'persistent', and 'remember_destroyed'
    always come from the child's own data (or engine defaults), never from a
    parent.

    Walks up to 10 levels of ancestors so grandparents are reached.
    """
    parent_name = object_data.get('parent', '')
    if not parent_name:
        return object_data

    # Collect ancestor events and properties, closest parent first.
    inherited_events: dict = {}
    inherited_props: dict = {}
    current = parent_name
    for _ in range(10):
        parent_data = objects.get(current, {})
        if not parent_data:
            break
        for event_name, event_data in parent_data.get('events', {}).items():
            if event_name not in inherited_events:
                inherited_events[event_name] = event_data
        for key, value in parent_data.items():
            if key in _CHILD_ONLY_OBJECT_PROPS or key in _NON_INHERITABLE_OBJECT_KEYS:
                continue
            if key not in inherited_props and value is not None:
                inherited_props[key] = value
        current = parent_data.get('parent', '')
        if not current:
            break

    if not inherited_events and not inherited_props:
        return object_data

    merged = dict(object_data)

    if inherited_events:
        child_events = object_data.get('events', {})
        merged_events = dict(inherited_events)
        merged_events.update(child_events)
        merged['events'] = merged_events

    for key, value in inherited_props.items():
        if merged.get(key) is None:
            merged[key] = value

    return merged


def expand_hash_newlines(text: str) -> str:
    r"""Convert GameMaker '#' line breaks in a display string to real newlines.

    In GameMaker display strings (show_message, draw_text, ...) a bare ``#``
    starts a new line, while an escaped ``\#`` is a literal ``#``. So
    ``"CONGRATULATIONS#You won"`` renders as two lines, and ``"3 \# 4"``
    keeps the ``#``.
    """
    if not text or '#' not in text:
        return text
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '\\' and i + 1 < n and text[i + 1] == '#':
            out.append('#')      # escaped literal '#'
            i += 2
        elif ch == '#':
            out.append('\n')     # GM line break
            i += 1
        else:
            out.append(ch)
            i += 1
    return ''.join(out)


# Pre-computed alarm key strings to avoid f-string creation in hot loops
ALARM_KEYS = tuple(f"alarm_{i}" for i in range(12))


# _FLAT_MOUSE_KEY_ALIASES/_mouse_sub_event/_find_key_in_event moved to
# runtime/input_handler.py (docs/POST_1_0_REFACTOR.md File 3, cluster 4) --
# _mouse_sub_event re-exported here so the existing
# `from runtime.game_runner import _mouse_sub_event` call sites (tests
# included) keep working unchanged.
from runtime.input_handler import InputMixin, _mouse_sub_event  # noqa: F401,E402
# CollisionMixin (docs/POST_1_0_REFACTOR.md File 3, cluster 5) -- a fresh
# module, not a revival of the old, deleted `collision_system.CollisionMixin`
# (see ARCHITECTURE.md §6 and runtime/collision.py's own module docstring).
from runtime.collision import CollisionMixin


# GameInstance moved to runtime/instance.py (docs/POST_1_0_REFACTOR.md File 3,
# cluster 3), re-exported here so existing `from runtime.game_runner import
# GameInstance` call sites (tests and the multiplayer extension included)
# keep working unchanged. Unlike GameRoom, this one has no circular
# dependency with this module -- GameInstance never referenced GameRoom or
# any game_runner.py-specific helper -- so this import can live anywhere;
# it's kept here, adjacent to the class it used to be, for readability.
from runtime.instance import GameInstance



# GameRoom moved to runtime/room.py (docs/POST_1_0_REFACTOR.md File 3,
# cluster 2), re-exported here so existing `from runtime.game_runner
# import GameRoom/_sane_room_dimension/ROOM_MIN_DIMENSION/
# ROOM_MAX_DIMENSION` call sites (tests included) keep working unchanged.
#
# MUST stay at this exact position (after resolve_parent_inheritance's
# definition above, before GameRunner below): runtime/room.py imports
# that name from this module at its own top level, so by the time that
# import executes it needs it already defined here. Moving this import
# earlier (e.g. into the top-of-file import block) reintroduces a real
# circular-import failure at process start -- see runtime/room.py's own
# module docstring. (GameInstance no longer factors into this constraint
# -- it moved to runtime/instance.py in cluster 3 and room.py now imports
# it from there directly, with no ordering dependency on game_runner.py.)
from runtime.room import GameRoom, _sane_room_dimension, ROOM_MIN_DIMENSION, ROOM_MAX_DIMENSION  # noqa: E402


class GameRunner(InputMixin, CollisionMixin):
    """Enhanced game runner that properly renders rooms with objects"""

    def __init__(self, project_path: str = None):
        self.running = False
        self.screen = None
        self.clock = None
        self.project_data = None
        self.project_path = None

        # Global game state (Score/Lives/Health system) - must be before ActionExecutor
        self.score = 0
        self.lives = 3
        self.health = 100.0
        self.highscores = []  # List of (name, score) tuples
        self.highscore_max_entries = 10  # Maximum entries in highscore table
        self.highscore_file = None  # Path to highscore file (set when project loads)

        # Global variables storage (user-defined variables accessible from any instance)
        self.global_variables: Dict[str, Any] = {}

        # "Stay destroyed" memory: room name -> set of (object_name, xstart,
        # ystart) identities for instances flagged `remember_destroyed` that
        # were destroyed during play. Consulted whenever a room is rebuilt from
        # its authored layout (room restart / game restart / a non-persistent
        # room's rebuild-on-revisit — see change_room and _visited_rooms below)
        # so those instances are not respawned. Cleared on a full game restart.
        self._destroyed_memory: Dict[str, set] = {}

        # Rooms this playthrough has already entered at least once via
        # change_room. A room not in here yet is still the pristine object
        # GameRoom-built at load, so change_room's rebuild-on-revisit check
        # (only meaningful for an actual REVISIT) can skip it safely. Cleared
        # on a full game restart alongside _destroyed_memory.
        self._visited_rooms: set = set()

        # Cached reference to objects data (set once during project load)
        self._objects_data: Dict[str, dict] = {}

        # Shared action executor for all instances (pass self for global state access)
        self.action_executor = ActionExecutor(game_runner=self)

        # Register Thymio action handlers
        register_thymio_actions(self.action_executor)

        # Load plugins
        logger.debug("🔌 Loading action/event plugins...")
        self.plugin_loader = load_all_plugins(self.action_executor)

        # Game assets
        self.sprites: Dict[str, GameSprite] = {}
        self.backgrounds: Dict[str, pygame.Surface] = {}  # Background surfaces
        self.sounds: Dict[str, Any] = {}  # pygame.mixer.Sound objects
        self.music_files: Dict[str, str] = {}  # music name -> file path
        self.rooms: Dict[str, GameRoom] = {}
        self.current_room = None

        # Thymio robot renderer (shared for all Thymio robots)
        self.thymio_renderer = ThymioRenderer()

        # Tracks Thymio button presses originating from the mouse so that
        # release maps back to the same instance/button: {pygame_button: (instance, button_name)}
        self._thymio_mouse_presses = {}

        # Game settings
        self.fps = 60
        self.window_width = 800
        self.window_height = 600

        # Caption display settings (like GM's "Display score in caption")
        # By default, nothing shows until the value is used in the game
        self.show_score_in_caption = False
        self.show_lives_in_caption = False
        self.show_health_in_caption = False
        self.window_caption = ""  # Custom caption prefix

        # Language for caption translations (default to English)
        self.language = 'en'

        # Caption caching - only update pygame caption when values change
        self._last_caption_state = None  # (score, lives, health, caption, flags)

        # Room transition grace period - skip collision detection for N frames after room change
        # This prevents immediate collision triggers when player spawns on top of a portal/door
        self._room_transition_grace_frames = 0

        # If project path provided, load it
        if project_path:
            self.load_project_data_only(project_path)

    def is_game_running(self):
        """Check if game is currently running"""
        return self.running

    def load_project_data_only(self, project_path: str) -> bool:
        """Load project data without loading sprites (sprites loaded later)"""
        try:
            path = Path(project_path)

            # If it's a directory, look for project.json inside
            if path.is_dir():
                self.project_path = path
                project_file = path / "project.json"
            # If it's a file, use it directly
            elif path.is_file() and path.name == "project.json":
                self.project_path = path.parent
                project_file = path
            else:
                logger.error(f"Invalid project path: {project_path}")
                return False

            if not project_file.exists():
                logger.error(f"Project file not found: {project_file}")
                return False

            # Load project data
            with open(project_file, 'r', encoding='utf-8') as f:
                self.project_data = json.load(f)

            # Cache objects data early so _load_objects_from_files can merge external files
            self._objects_data = self.project_data.get('assets', {}).get('objects', {})

            # Load asset data from separate files if they exist
            self._load_rooms_from_files()
            self._load_objects_from_files()
            self._load_sprites_from_files()

            logger.info(f"Loaded project: {self.project_data.get('name', 'Untitled')}")

            # Cache objects data for fast access during gameplay
            # NOTE: This must be set BEFORE _load_objects_from_files is called above,
            # but we re-set it here to ensure it reflects any file-based merges.
            # The initial set is done before the file loading calls.
            self._objects_data = self.project_data.get('assets', {}).get('objects', {})

            # Load project settings
            self._load_project_settings()

            # Set up highscore file path and load existing scores
            self.highscore_file = self.project_path / "highscores.json"
            self.load_highscores()

            # Only load rooms (without sprites for instances yet)
            self.load_rooms_without_sprites()

            return True

        except Exception as e:
            logger.error(f"Error loading project: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_rooms_from_files(self) -> None:
        """Load room instance data from separate files in rooms/ directory"""
        rooms_dir = self.project_path / "rooms"

        if not rooms_dir.exists():
            logger.debug("DEBUG: No rooms/ directory found, using embedded room data")
            return

        rooms_data = self.project_data.get('assets', {}).get('rooms', {})

        for room_name, room_data in rooms_data.items():
            room_file = rooms_dir / f"{room_name}.json"

            if room_file.exists():
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        file_room_data = json.load(f)

                    # Merge file data into room data (file takes precedence for instances)
                    instance_count = merge_room_file(room_data, file_room_data)
                    if instance_count is not None:
                        logger.debug(f"📂 Loaded room: {room_name} ({instance_count} instances from file)")

                except Exception as e:
                    logger.error(f"⚠️ Failed to load room file {room_file}: {e}")
            else:
                # No external file - use embedded instances (legacy format)
                if room_data.get('instances'):
                    logger.debug(f"📂 Room {room_name}: using embedded instances")

    def _load_objects_from_files(self) -> None:
        """Load object data from separate files in objects/ directory"""
        objects_dir = self.project_path / "objects"

        if not objects_dir.exists():
            logger.error(f"📂 Objects directory not found: {objects_dir}")
            return

        logger.debug(f"📂 Loading objects from: {objects_dir}")
        objects_data = self._objects_data

        for object_name, object_data in objects_data.items():
            object_file = objects_dir / f"{object_name}.json"

            if object_file.exists():
                try:
                    with open(object_file, 'r', encoding='utf-8') as f:
                        file_object_data = json.load(f)

                    # Merge file data into object data (file takes precedence)
                    event_count = merge_object_file(object_data, file_object_data)
                    logger.debug(f"📂 Loaded object: {object_name} ({event_count} events from file)")

                except Exception as e:
                    logger.error(f"⚠️ Failed to load object file {object_file}: {e}")

    def _load_sprites_from_files(self) -> None:
        """Load sprite data from separate files in sprites/ directory"""
        sprites_dir = self.project_path / "sprites"

        if not sprites_dir.exists():
            return

        sprites_data = self.project_data.get('assets', {}).get('sprites', {})

        for sprite_name, sprite_data in sprites_data.items():
            sprite_file = sprites_dir / f"{sprite_name}.json"

            if sprite_file.exists():
                try:
                    with open(sprite_file, 'r', encoding='utf-8') as f:
                        file_sprite_data = json.load(f)

                    # Merge file data into sprite data (file takes precedence).
                    # Single-sourced whitelist so all loaders stay in sync (L6).
                    from utils.project_file_merge import merge_sprite_file
                    merge_sprite_file(sprite_data, file_sprite_data)

                except Exception as e:
                    logger.error(f"⚠️ Failed to load sprite file {sprite_file}: {e}")

    def _load_project_settings(self) -> None:
        """Load game settings from project data"""
        settings = self.project_data.get('settings', {})

        # Load lives/score/health initial values
        self.lives = settings.get('starting_lives', 3)
        self.score = settings.get('starting_score', 0)
        self.health = settings.get('starting_health', 100.0)

        # Load caption display settings
        self.show_lives_in_caption = settings.get('show_lives_in_caption', False)
        self.show_score_in_caption = settings.get('show_score_in_caption', False)
        self.show_health_in_caption = settings.get('show_health_in_caption', False)

        # Honor the authored room/game speed (the GMK importer persists the
        # source game's speed — GM8 defaults to 30 — and templates set it too).
        # Previously this was ignored and fps was hardcoded 60, so imported
        # games ran at double speed (M48). Clamp like execute_set_room_speed.
        room_speed = settings.get('room_speed')
        if room_speed is not None:
            try:
                self.fps = max(1, min(240, int(room_speed)))
            except (ValueError, TypeError):
                pass  # keep the default fps

        logger.debug(f"⚙️ Settings: lives={self.lives}, score={self.score}, "
                     f"health={self.health}, fps={self.fps}")

    def load_sprites(self):
        """Load all sprites from the project (called after pygame.display is initialized)"""
        sprites_data = self.project_data.get('assets', {}).get('sprites', {})

        logger.info(f"Loading {len(sprites_data)} sprites...")

        for sprite_name, sprite_info in sprites_data.items():
            try:
                file_path = sprite_info.get('file_path', '')
                if file_path:
                    full_path = self.project_path / file_path
                    # Pass sprite_info to enable animation support
                    sprite = GameSprite(str(full_path), sprite_info)
                    self.sprites[sprite_name] = sprite
                    logger.debug(f"  âœ… Loaded sprite: {sprite_name} ({sprite.width}x{sprite.height})")
                else:
                    logger.debug(f"  âš ï¸  Sprite {sprite_name} has no file path")
            except Exception as e:
                logger.error(f"  âŒ Error loading sprite {sprite_name}: {e}")

    def load_backgrounds(self):
        """Load all background images from the project (called after pygame.display is initialized)"""
        backgrounds_data = self.project_data.get('assets', {}).get('backgrounds', {})

        if not backgrounds_data:
            return

        logger.info(f"Loading {len(backgrounds_data)} backgrounds...")

        for bg_name, bg_info in backgrounds_data.items():
            try:
                file_path = bg_info.get('file_path', '')
                if file_path:
                    full_path = self.project_path / file_path
                    if full_path.exists():
                        surface = pygame.image.load(str(full_path)).convert_alpha()
                        self.backgrounds[bg_name] = surface
                        logger.debug(f"  âœ… Loaded background: {bg_name} ({surface.get_width()}x{surface.get_height()})")
                    else:
                        logger.debug(f"  âš ï¸  Background file not found: {full_path}")
                else:
                    logger.debug(f"  âš ï¸  Background {bg_name} has no file path")
            except Exception as e:
                logger.error(f"  âŒ Error loading background {bg_name}: {e}")

    def load_sounds(self):
        """Load all sounds from the project (called after pygame.mixer is initialized)"""
        sounds_data = self.project_data.get('assets', {}).get('sounds', {})

        if not sounds_data:
            return

        logger.info(f"Loading {len(sounds_data)} sounds...")

        for sound_name, sound_info in sounds_data.items():
            try:
                file_path = sound_info.get('file_path', '')
                
                # Try to load full sound metadata from individual JSON file
                kind = sound_info.get('kind', None)
                volume = sound_info.get('volume', 1.0)
                
                if kind is None:
                    # Load from individual sound JSON file
                    sound_json_path = self.project_path / 'sounds' / f'{sound_name}.json'
                    if sound_json_path.exists():
                        with open(sound_json_path, 'r', encoding='utf-8') as f:
                            sound_metadata = json.load(f)
                            kind = sound_metadata.get('kind', 'sound')
                            volume = sound_metadata.get('volume', volume)
                            if not file_path:
                                file_path = sound_metadata.get('file_path', '')
                    else:
                        kind = 'sound'  # Default to sound effect

                if file_path:
                    full_path = self.project_path / file_path

                    if not full_path.exists():
                        logger.error(f"  ⚠️  Sound file not found: {full_path}")
                        continue

                    if kind == 'music':
                        # Music is streamed, just store the path
                        self.music_files[sound_name] = str(full_path)
                        logger.debug(f"  🎵 Loaded music: {sound_name}")
                    else:
                        # Sound effects are loaded into memory
                        sound = pygame.mixer.Sound(str(full_path))
                        # Apply default volume from sound definition
                        sound.set_volume(float(volume))
                        self.sounds[sound_name] = sound
                        logger.debug(f"  🔊 Loaded sound: {sound_name}")
                else:
                    logger.debug(f"  ⚠️  Sound {sound_name} has no file path")
            except Exception as e:
                logger.error(f"  ❌ Error loading sound {sound_name}: {e}")

    def load_rooms_without_sprites(self):
        """Load rooms but don't assign sprites to instances yet"""
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        assets = self.project_data.get('assets', {})

        logger.info(f"Loading {len(rooms_data)} rooms...")

        for room_name, room_info in rooms_data.items():
            try:
                room = GameRoom(
                    room_name,
                    room_info,
                    action_executor=self.action_executor,
                    project_path=self.project_path,
                    sprites_data=assets  # Pass all assets so room can find backgrounds/sprites
                )
                # Don't set sprites yet - will do this after pygame.display is ready
                self.rooms[room_name] = room
                logger.debug(f"  Loaded room: {room_name} ({len(room.instances)} instances)")
            except Exception as e:
                logger.error(f"  Error loading room {room_name}: {e}")
                import traceback
                traceback.print_exc()

    def assign_sprites_to_rooms(self):
        """Assign loaded sprites to room instances"""
        objects_data = self._objects_data

        logger.info("Assigning sprites to room instances...")
        for room_name, room in self.rooms.items():
            room.set_sprites_for_instances(self.sprites, objects_data)

            # Count instances with sprites
            sprites_assigned = sum(1 for instance in room.instances if instance.sprite)
            logger.debug(f"  Room {room_name}: {sprites_assigned}/{len(room.instances)} instances have sprites")

    def load_room_backgrounds(self):
        """Load background images for all rooms (called after pygame.display is initialized)"""
        logger.info("Loading room background images...")
        for room_name, room in self.rooms.items():
            # Pass backgrounds reference for tile rendering
            room.set_backgrounds_ref(self.backgrounds)

            if room.background_image_name:
                room.load_background_image()
                if room.background_surface:
                    logger.debug(f"  Room {room_name}: background '{room.background_image_name}' loaded")
                else:
                    logger.error(f"  Room {room_name}: background '{room.background_image_name}' NOT found")

    def find_starting_room(self) -> Optional[str]:
        """Find a room to start the game in - uses room_order if available"""
        if not self.rooms:
            return None

        # Use room_order from project data if available (first room in order)
        if self.project_data:
            room_order = self.project_data.get('room_order', [])
            if room_order:
                # Return first room in the order that actually exists
                for room_name in room_order:
                    if room_name in self.rooms:
                        return room_name

        # Fallback: just use the first room in the dictionary
        return list(self.rooms.keys())[0]

    def test_game(self, project_path: str, language: str = 'en') -> bool:
        """Test run the game from project"""
        logger.info(f"Testing game from project: {project_path}")
        self.language = language

        # Load project data (but not sprites yet)
        if not self.load_project_data_only(project_path):
            logger.error("Failed to load project")
            return False

        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            logger.debug("No rooms found in project")
            return False

        logger.info(f"Starting with room: {starting_room}")
        self.current_room = self.rooms[starting_room]
        self._visited_rooms.add(starting_room)

        self.window_width, self.window_height = self._window_size_for(
            self.current_room)

        # Run the game (sprites will be loaded after pygame.display is ready)
        return self.run_game_loop()

    def _window_size_for(self, room) -> tuple:
        """Window size for a room: the room's own size, UNLESS the room is too
        big to show at once, in which case the size the project declares.

        Sizing the window to the room is right for the ordinary case, and is
        what every sample except views_* relies on. But when a room is LARGER
        than the declared window, sizing to the room shows the entire room at
        once -- which contradicts the author's setting and makes a scrolling
        camera pointless. views_1 rendered its whole 2400x800 room in one
        window, so the camera-scrolling the sample exists to demonstrate was
        invisible; "what is this sample supposed to do?" was the reasonable
        reaction.

        Clamped per axis, and only downwards. A room smaller than or equal to
        the declared window keeps the previous behaviour exactly -- which is
        why raycast_* (640x480 declared, 480x480 rooms) and maze_2/maze_3
        (rooms of differing heights) are unaffected.
        """
        width, height = room.width, room.height
        settings = (self.project_data or {}).get('settings') or {}
        declared_w = settings.get('window_width')
        declared_h = settings.get('window_height')
        if isinstance(declared_w, (int, float)) and 0 < declared_w < width:
            width = int(declared_w)
        if isinstance(declared_h, (int, float)) and 0 < declared_h < height:
            height = int(declared_h)
        return width, height

    @staticmethod
    def _frame_budget() -> int:
        """Frames to render before quitting, from PYGM_MAX_FRAMES. 0 = forever.

        This exists so a built export can be *verified*. A game with no
        budget runs until the player quits, and a headless harness cannot
        press a key, so the only signal available was "it had not crashed
        yet after N seconds" -- which cannot distinguish a game that renders
        from one stuck on a black screen before its first frame. With a
        budget the process renders N real frames and exits 0, printing
        PYGM_FRAMES_COMPLETED=N for the harness to match.

        Absent or unparseable means no budget, so a player's game is never
        affected: the loop below does not even count frames unless asked.
        See tests/test_desktop_export_end_to_end.py and
        docs/EYEBALL_FIXES_2026-08-16.md item A1.5.
        """
        raw = os.environ.get("PYGM_MAX_FRAMES", "")
        try:
            budget = int(raw)
        except (TypeError, ValueError):
            return 0
        return budget if budget > 0 else 0

    @staticmethod
    def _apply_seed() -> bool:
        """Seed the RNG from PYGM_SEED, so a run can be reproduced.

        Several samples build their world with random(): match3 fills its grid,
        treasure scatters its loot, plateforme_3 gives each bonus a random
        frame. Two unseeded runs of those never match, which made comparing an
        exported game against the IDE meaningless -- the first --compare pass
        reported five "failures" that were all just the samples disagreeing
        with themselves (match3_1 differed from its own second run by exactly
        the 33.88% it differed from the export by).

        Seeding both sides identically turns that comparison back into real
        signal. Absent or unparseable means "leave the RNG alone", so a
        player's game is never made repetitive.
        """
        raw = os.environ.get("PYGM_SEED", "")
        if not raw:
            return False
        try:
            seed = int(raw)
        except (TypeError, ValueError):
            return False
        import random
        random.seed(seed)
        logger.info("RNG seeded from PYGM_SEED=%d", seed)
        return True

    def _save_final_frame(self) -> None:
        """Write the last rendered frame to PYGM_SCREENSHOT, if set.

        Pairs with the frame budget above to make "the export runs the same
        engine" a measurable claim rather than an argument: run the source
        engine and the built export for the same number of frames and compare
        the two images (tools/verify_desktop_export.py --compare). Nothing
        happens unless the variable is set.
        """
        destination = os.environ.get("PYGM_SCREENSHOT", "")
        if not destination or not self.screen:
            return
        try:
            pygame.image.save(self.screen, destination)
        except (pygame.error, OSError) as exc:
            logger.warning("Could not save frame to %s: %s", destination, exc)

    def _print_net_status(self) -> None:
        """Print a grep-able one-liner an external harness can check for
        LAN multiplayer verification (tools/smoke_run_multiplayer.py),
        the same "opt-in, observable-from-outside-the-process" pattern
        PYGM_FRAMES_COMPLETED/PYGM_SCREENSHOT already establish. Only
        fires when a v2 multiplayer session actually mirrored
        network_role into globals (extensions/multiplayer_lan/handlers.py
        _apply_session_state) -- an ordinary single-player run's stdout
        is completely unaffected, since global_variables never gets that
        key at all."""
        role = self.global_variables.get("network_role", "")
        if not role:
            return
        print("PYGM_NET_STATUS=role=%s connected=%s player_id=%s" % (
            role,
            self.global_variables.get("network_connected", 0),
            self.global_variables.get("player_id", -1),
        ), flush=True)

    def run_game_loop(self) -> bool:
        """Main game loop"""
        try:
            # Initialize pygame
            pygame.init()

            # Initialize mixer for audio (after pygame.init)
            try:
                pygame.mixer.init()
                logger.debug("🔊 Audio mixer initialized")
            except Exception as e:
                logger.error(f"⚠️  Audio mixer failed to initialize: {e}")

            # Create display
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption(f"PyGameMaker - {self.project_data.get('name', 'Game')}")

            # Initialize clock
            self.clock = pygame.time.Clock()

            logger.info(f"Game window: {self.window_width}x{self.window_height}")

            # NOW load sprites (after pygame.display is initialized)
            logger.debug("\n🎮 Loading sprites after pygame.display initialization...")
            self.load_sprites()

            # Load background images (after pygame.display is initialized)
            self.load_backgrounds()

            # Load sounds (after mixer is initialized)
            self.load_sounds()

            # Load background images for all rooms
            self.load_room_backgrounds()

            # Assign sprites to room instances
            self.assign_sprites_to_rooms()

            logger.debug(f"\nCurrent room: {self.current_room.name}")
            logger.debug(f"Room instances: {len(self.current_room.instances)}")

            # Count instances by type for summary
            instance_counts = {}
            for instance in self.current_room.instances:
                obj_name = instance.object_name
                instance_counts[obj_name] = instance_counts.get(obj_name, 0) + 1

            logger.debug("Instance summary:")
            for obj_name, count in sorted(instance_counts.items()):
                logger.debug(f"  {obj_name}: {count}")

            # Seed before any authored code runs -- create events fire just
            # below and that is where match3 builds its random grid.
            self._apply_seed()

            # IMPORTANT: Execute create events for starting room instances
            logger.debug(f"\n🎬 Triggering create events for starting room: {self.current_room.name}")
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    self.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # Execute the once-per-game game_start event (after Create, before
            # Room Start) so startup setup like score/lives/caption runs.
            logger.debug(f"🎬 Triggering game_start events for starting room: {self.current_room.name}")
            self.trigger_game_start_event()

            # Execute room_start event for all instances (after create events)
            logger.debug(f"🚪 Triggering room_start events for starting room: {self.current_room.name}")
            self.trigger_room_start_event()

            self.running = True
            frame_budget = self._frame_budget()
            frames_rendered = 0

            # Main game loop
            while self.running:
                # Extension frame updates that must run every frame,
                # unconditional on any authored action (e.g. LAN
                # multiplayer applying inbound network state before Step
                # runs against it) -- see runtime/extension_hooks.py.
                extension_hooks.run_frame_updates(self, "before_step")

                # ========== GameMaker 7.0 Event Execution Order ==========
                # Merged loop: begin_step -> alarms -> step (per instance)
                # This reduces 3 separate instance iterations to 1.
                # Iterate a snapshot so instances created mid-frame (e.g. a
                # step event that create_instances) are processed starting next
                # frame — matching GameMaker and preventing a spawn cycle from
                # hanging the whole frame in an unbounded loop (M49).
                for instance in list(self.current_room.instances):
                    obj_data = instance.object_data
                    if obj_data:
                        events = obj_data.get("events")
                        if events:
                            # 1. BEGIN STEP
                            if "begin_step" in events:
                                instance.action_executor.execute_event(instance, "begin_step", events)

                            # 2. ALARMS (countdown and trigger)
                            # Use pre-computed ALARM_KEYS to avoid f-string creation
                            alarm_events = events.get("alarm", {})
                            for alarm_num in range(12):
                                if instance.alarm[alarm_num] > 0:
                                    instance.alarm[alarm_num] -= 1
                                    if instance.alarm[alarm_num] == 0:
                                        instance.alarm[alarm_num] = -1
                                        alarm_key = ALARM_KEYS[alarm_num]
                                        # Check nested first, then flat structure
                                        alarm_event = alarm_events.get(alarm_key) or events.get(alarm_key)
                                        if alarm_event and "actions" in alarm_event:
                                            logger.debug(f"⏰ Alarm {alarm_num} triggered for {instance.object_name}")
                                            instance.action_executor.execute_action_list(instance, alarm_event["actions"])

                    # 2b. DELAYED ACTIONS (countdown and execute)
                    if instance._delayed_actions:
                        completed = []
                        for i, delayed in enumerate(instance._delayed_actions):
                            delayed['frames_remaining'] -= 1
                            if delayed['frames_remaining'] <= 0:
                                completed.append(i)
                                # Execute the delayed action
                                action_name = delayed['action']
                                params = delayed['parameters']
                                logger.debug(f"⏱️ Executing delayed action: {action_name} for {instance.object_name}")

                                # Handle specific delayed actions
                                if action_name == "change_room":
                                    room_name = params.get("room_name", "")
                                    if room_name:
                                        instance.goto_room_target = room_name
                                elif action_name == "next_room":
                                    instance.next_room_flag = True
                                elif action_name == "restart_room":
                                    instance.restart_room_flag = True
                                elif action_name == "game_end":
                                    self.running = False
                                else:
                                    # Try to execute as a generic action
                                    action_data = {"action": action_name, "parameters": params}
                                    instance.action_executor.execute_action(instance, action_data)

                        # Remove completed delayed actions (in reverse order to preserve indices)
                        for i in reversed(completed):
                            instance._delayed_actions.pop(i)

                    # 2c. PARTICLES & TIMELINE (Tier 5.1)
                    instance.update_particle_system()
                    instance.update_timeline()

                    # 3. STEP EVENT (always call - handles nokey internally)
                    instance.step()

                    # 3b. KEYBOARD HELD events (fire every frame while key is down)
                    self._process_held_keys(instance)

                # 4. KEYBOARD/MOUSE EVENTS
                self.handle_events()

                # 5. MOVEMENT (apply physics: gravity, friction, hspeed/vspeed)
                # 6. COLLISION (detect and execute collision events)
                self.update()

                # Update Thymio simulators and trigger events
                self.update_thymio_robots()

                # 7. END STEP and DESTROY events (merged loop)
                has_destroyed = False
                for instance in list(self.current_room.instances):  # snapshot (M49)
                    obj_data = instance.object_data
                    if obj_data:
                        events = obj_data.get("events")
                        if events:
                            if "end_step" in events:
                                instance.action_executor.execute_event(instance, "end_step", events)
                            if instance.to_destroy:
                                has_destroyed = True
                                if "destroy" in events:
                                    logger.debug(f"💥 Triggering destroy event for {instance.object_name}")
                                    instance.action_executor.execute_event(instance, "destroy", events)
                    elif instance.to_destroy:
                        has_destroyed = True

                # Remove destroyed instances only if any were marked
                # Also check ALL instances for to_destroy flag (not just those with events)
                for inst in self.current_room.instances:
                    if inst.to_destroy:
                        has_destroyed = True
                        break

                if has_destroyed:
                    # Incremental grid removal: each destroyed instance only
                    # touches the cells it actually occupied (O(k) per instance
                    # via _instance_cells), avoiding the full O(n) rebuild that
                    # would otherwise walk every surviving instance.
                    room = self.current_room
                    kept = []
                    for inst in room.instances:
                        if inst.to_destroy:
                            # Remember flagged instances so a later room rebuild
                            # (restart) doesn't respawn them.
                            self._remember_destroyed_instance(room, inst)
                            room._remove_from_grid(inst)
                            room._instance_cells.pop(id(inst), None)
                        else:
                            kept.append(inst)
                    room.instances = kept
                    room._depth_dirty = True
                    room.invalidate_collision_listened_types()

                # Extension frame updates that must run every frame after
                # this frame's state has settled (e.g. LAN multiplayer
                # broadcasting the post-update/collision/destroy snapshot)
                # -- see runtime/extension_hooks.py.
                extension_hooks.run_frame_updates(self, "after_update")

                # Clear screen
                self.screen.fill((135, 206, 235))  # Sky blue

                # Render
                self.render()

                # Check for pending messages and display them
                self.process_pending_messages()

                # Control framerate
                self.clock.tick(self.fps)

                # Opt-in frame budget: see _frame_budget().
                if frame_budget:
                    frames_rendered += 1
                    if frames_rendered >= frame_budget:
                        self.running = False
                        self._save_final_frame()
                        print("PYGM_FRAMES_COMPLETED=%d" % frames_rendered,
                              flush=True)
                        self._print_net_status()

            return True

        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_game()
            elif event.type == pygame.KEYDOWN:
                # Check for ESC key to quit game
                if event.key == pygame.K_ESCAPE:
                    self.stop_game()
                # Handle keyboard press events for all instances
                self.handle_keyboard_press(event.key)
            elif event.type == pygame.KEYUP:
                # Handle keyboard release events
                self.handle_keyboard_release(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse button press
                self.handle_mouse_press(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                # Handle mouse button release
                self.handle_mouse_release(event.button, event.pos)
            elif event.type == pygame.MOUSEMOTION:
                # Handle mouse movement
                self.handle_mouse_motion(event.pos)

    # handle_keyboard_press/_process_held_keys/_release_held_key_silent/
    # handle_keyboard_release/handle_mouse_press/_handle_thymio_button_press/
    # handle_mouse_release/handle_mouse_motion/_room_transition_pending/
    # update/_get_key_name moved to runtime/input_handler.py's InputMixin
    # (docs/POST_1_0_REFACTOR.md File 3, cluster 4) -- GameRunner now
    # inherits from InputMixin (`class GameRunner(InputMixin, ...):` above)
    # so all of these remain callable as self.<name>(...) exactly as before.

    # _get_step_grid_size/_get_any_grid_size/_slide_axis_to_contact/
    # check_movement_collision_with_blocker/separate_overlapping_instances/
    # push_back_instance/check_outside_room_events/
    # detect_collisions_for_instance/process_collision_event/
    # check_not_collision_events/_object_matches_target/
    # _resolve_collision_event/instances_overlap/_bbox_in_world/
    # rectangles_overlap/_precise_refine/check_collision_at_position moved
    # to runtime/collision.py's CollisionMixin (docs/POST_1_0_REFACTOR.md
    # File 3, cluster 5) -- GameRunner now inherits from CollisionMixin too
    # (`class GameRunner(InputMixin, CollisionMixin):` above) so all of
    # these remain callable as self.<name>(...) exactly as before.

    @staticmethod
    def _destroyed_identity(inst):
        """Stable identity for a placed instance across a room rebuild.

        Authored room instances carry no id, but they respawn at the same
        (object, position), and `xstart`/`ystart` capture that authored
        position — so this key matches a pre-rebuild instance to its
        post-rebuild twin. Record and consume sides MUST use this helper so
        the two halves can never drift apart."""
        return (inst.object_name, inst.xstart, inst.ystart)

    def _remember_destroyed_instance(self, room, inst):
        """If `inst` opts into `remember_destroyed`, record its identity so a
        future rebuild of `room` (a restart) won't respawn it. No-op for
        instances without the flag."""
        if inst.object_data and inst.object_data.get('remember_destroyed'):
            self._destroyed_memory.setdefault(room.name, set()).add(
                self._destroyed_identity(inst)
            )

    def _apply_destroyed_memory(self, room):
        """Drop instances a player already destroyed that are flagged
        `remember_destroyed`, so rebuilding a room from its layout (restart)
        doesn't bring them back. Identity is (object_name, xstart, ystart),
        which is stable across a rebuild because the room is recreated from the
        same authored instance list. No-op when the room has no remembered
        kills. Cleared on a full game restart."""
        remembered = self._destroyed_memory.get(room.name)
        if not remembered:
            return
        kept = [
            inst for inst in room.instances
            if self._destroyed_identity(inst) not in remembered
        ]
        if len(kept) != len(room.instances):
            room.instances = kept
            room.rebuild_spatial_grid()
            room.invalidate_collision_listened_types()

    def _build_room_from_data(self, room_name, room_data):
        """Construct a fresh GameRoom from authored data (sprites, backgrounds,
        remembered-destroyed pruning applied). Shared by the restart paths."""
        assets = self.project_data.get('assets', {})
        objects_data = assets.get('objects', {})
        room = GameRoom(
            room_name, room_data,
            action_executor=self.action_executor,
            project_path=self.project_path,
            sprites_data=assets,
        )
        room.set_sprites_for_instances(self.sprites, objects_data)
        room.set_backgrounds_ref(self.backgrounds)
        if room.background_image_name:
            room.load_background_image()
        self._apply_destroyed_memory(room)
        return room

    def _readd_persistent_instances(self, room, persistent_instances):
        """Re-add carried persistent instances to a freshly built room.

        Replaces any authored non-persistent instance of the same object,
        refreshes object_data from the project, and resets velocity — the same
        contract change_room uses, shared so restart_current_room matches it.
        """
        if not persistent_instances:
            return
        objects_data = self._objects_data
        for persistent_inst in persistent_instances:
            room.instances = [
                inst for inst in room.instances
                if not (inst.object_name == persistent_inst.object_name and
                        not inst.object_data.get('persistent', False))
            ]
            if persistent_inst.object_name in objects_data:
                merged = resolve_parent_inheritance(
                    objects_data[persistent_inst.object_name], objects_data)
                persistent_inst.set_object_data(merged)
            persistent_inst.hspeed = 0
            persistent_inst.vspeed = 0
            if persistent_inst not in room.instances:
                room.instances.append(persistent_inst)

    def restart_current_room(self):
        """Restart the current room"""
        if not self.current_room:
            return

        room_name = self.current_room.name
        logger.debug(f"🔄 Restarting room: {room_name}")

        # Collect persistent instances before discarding the old room — they
        # must survive a room restart (GameMaker semantics). Without this a
        # persistent player carried in from another room (and absent from this
        # room's authored layout) ceased to exist after restart_room (M51).
        persistent_instances = [
            inst for inst in self.current_room.instances
            if inst.object_data and inst.object_data.get('persistent', False)
        ]

        # Reload room from project data to reset all instances
        room_data = self.project_data.get('assets', {}).get('rooms', {}).get(room_name)
        if room_data:
            # Recreate the room from scratch
            assets = self.project_data.get('assets', {})
            objects_data = assets.get('objects', {})

            new_room = GameRoom(
                room_name,
                room_data,
                action_executor=self.action_executor,
                project_path=self.project_path,
                sprites_data=assets
            )

            # Assign sprites to instances
            new_room.set_sprites_for_instances(self.sprites, objects_data)

            # Wire pre-loaded background surfaces into the new room. Without
            # this, multi-layer / tiled backgrounds lose their surface refs
            # on restart: GameRoom only inspects `background_image_name`
            # (the legacy single-image field) inside load_background_image,
            # while the tiled-layer path lives off `_game_runner_backgrounds`
            # which set_backgrounds_ref populates. Symptom: first room load
            # showed the tiled background; first room_restart left it blank.
            new_room.set_backgrounds_ref(self.backgrounds)

            # Load background if needed
            if new_room.background_image_name:
                new_room.load_background_image()

            # Drop instances that were destroyed earlier and flagged
            # `remember_destroyed` (e.g. collected bonuses) so they don't
            # respawn on restart.
            self._apply_destroyed_memory(new_room)

            # Replace the room in our dictionary
            self.rooms[room_name] = new_room
            self.current_room = new_room

            # Re-add carried persistent instances, replacing any authored
            # non-persistent instance of the same object (mirrors change_room).
            self._readd_persistent_instances(new_room, persistent_instances)

            # Execute create events for the freshly-built instances only;
            # persistent instances already fired create (and the execute_event
            # guard would skip them anyway).
            for instance in self.current_room.instances:
                if instance in persistent_instances:
                    continue
                if instance.object_data and "events" in instance.object_data:
                    instance.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # Execute room_start event for all instances (after create events)
            self.trigger_room_start_event()

            # Set grace period to skip collision detection for 1 frame
            # This prevents immediate collision triggers when player spawns on a portal
            self._room_transition_grace_frames = 1

            logger.debug(f"✅ Room {room_name} restarted with {len(new_room.instances)} instances")

    def restart_game(self):
        """Restart the game from the first room with reset score/lives/health"""
        logger.debug("🔄 Restarting game from first room...")

        # Reset score, lives, and health to starting values
        settings = self.project_data.get('settings', {})
        self.score = settings.get('starting_score', 0)
        self.lives = settings.get('starting_lives', 3)
        self.health = settings.get('starting_health', 100)

        # Full reset: forget every "stay destroyed" instance so bonuses and the
        # like reappear on a fresh playthrough.
        self._destroyed_memory.clear()
        # Also forget which rooms this playthrough has entered, so a room
        # revisited after this restart is correctly treated as a fresh
        # revisit by change_room's rebuild-on-revisit check (harmless
        # either way for the loop below, which force-rebuilds every room
        # unconditionally regardless of _visited_rooms — this only matters
        # for a LATER change_room call after the restart completes).
        self._visited_rooms.clear()

        logger.debug(f"  📊 Reset: Score={self.score}, Lives={self.lives}, Health={self.health}")

        # Get the first room
        room_list = self.get_room_list()
        if not room_list:
            logger.debug("  ⚠️ No rooms found to restart to")
            return

        first_room_name = room_list[0]
        logger.debug(f"  ➡️ Going to first room: {first_room_name}")

        # Recreate the first room from scratch (like restart_current_room does)
        room_data = self.project_data.get('assets', {}).get('rooms', {}).get(first_room_name)
        if room_data:
            assets = self.project_data.get('assets', {})
            objects_data = assets.get('objects', {})

            new_room = GameRoom(
                first_room_name,
                room_data,
                action_executor=self.action_executor,
                project_path=self.project_path,
                sprites_data=assets
            )

            # Assign sprites to instances
            new_room.set_sprites_for_instances(self.sprites, objects_data)

            # Wire pre-loaded background surfaces into the new room (mirror
            # of restart_current_room): without this, multi-layer / tiled
            # backgrounds render blank after game restart because
            # load_background_image only handles the legacy single-image
            # field.
            new_room.set_backgrounds_ref(self.backgrounds)

            # Load background if needed
            if new_room.background_image_name:
                new_room.load_background_image()

            # Resize window if needed
            if self.screen:
                room_width, room_height = self._window_size_for(new_room)
                current_width, current_height = self.screen.get_size()
                if room_width != current_width or room_height != current_height:
                    logger.debug(f"  📐 Resizing window to {room_width}x{room_height}")
                    self.screen = pygame.display.set_mode((room_width, room_height))
                    self.window_width = room_width
                    self.window_height = room_height

            # Replace the room in our dictionary
            self.rooms[first_room_name] = new_room
            self.current_room = new_room
            self._visited_rooms.add(first_room_name)

            # Rebuild every OTHER already-visited room so rooms 2..N don't keep
            # the previous playthrough's mutated state (destroyed/moved/changed
            # instances). Without this, clearing _destroyed_memory only gave a
            # fresh start in room 1 (M52). Create events fire on entry (the
            # instances are fresh, so the create guard lets them run).
            #
            # Deliberately unconditional — every room rebuilds here regardless
            # of GameRoom.persistent (unlike change_room's rebuild-on-revisit
            # check, which honors it). A full game restart is a hard reset;
            # letting a persistent room survive restart_game (as real
            # GameMaker's persistent rooms do) would reopen the exact M52 bug
            # this loop exists to fix, for a case no current sample needs.
            rooms_data = self.project_data.get('assets', {}).get('rooms', {})
            for rname in list(self.rooms.keys()):
                if rname == first_room_name:
                    continue
                rdata = rooms_data.get(rname)
                if rdata:
                    self.rooms[rname] = self._build_room_from_data(rname, rdata)

            # Execute create events for all instances
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    instance.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # A game restart re-fires game_start (after Create, before Room
            # Start), matching GameMaker, so startup setup like the lives/score
            # caption is re-applied on a fresh playthrough.
            self.trigger_game_start_event()

            # Execute room_start event for all instances (after create events)
            self.trigger_room_start_event()

            # Set grace period to skip collision detection for 1 frame
            # This prevents immediate collision triggers when player spawns on a portal
            self._room_transition_grace_frames = 1

            logger.debug(f"  ✅ Game restarted with room '{first_room_name}' ({len(new_room.instances)} instances)")
        else:
            logger.debug(f"  ⚠️ Could not find room data for '{first_room_name}'")

    def goto_next_room(self):
        """Go to the next room"""
        logger.debug("🚪 goto_next_room called")
        if not self.current_room:
            logger.debug("❌ No current room!")
            return

        room_list = self.get_room_list()
        logger.debug(f"🔍 Room list: {room_list}")
        if not room_list:
            logger.debug("❌ Room list is empty!")
            return

        try:
            current_index = room_list.index(self.current_room.name)
            next_index = current_index + 1
            if next_index < len(room_list):
                next_room_name = room_list[next_index]
                logger.debug(f"➡️  Changing from '{self.current_room.name}' (index {current_index}) to '{next_room_name}' (index {next_index})")
                self.change_room(next_room_name)
            else:
                logger.debug(f"⚠️  Already at last room '{self.current_room.name}'")
        except ValueError:
            logger.debug(f"❌ Current room '{self.current_room.name}' not in room list")

    def goto_previous_room(self):
        """Go to the previous room"""
        logger.debug("🚪 goto_previous_room called")
        if not self.current_room:
            logger.debug("❌ No current room!")
            return

        room_list = self.get_room_list()
        logger.debug(f"🔍 Room list: {room_list}")
        if not room_list:
            logger.debug("❌ Room list is empty!")
            return

        try:
            current_index = room_list.index(self.current_room.name)
            if current_index > 0:
                prev_index = current_index - 1
                prev_room_name = room_list[prev_index]
                logger.debug(f"⬅️  Changing from '{self.current_room.name}' (index {current_index}) to '{prev_room_name}' (index {prev_index})")
                self.change_room(prev_room_name)
            else:
                logger.debug(f"⚠️  Already at first room '{self.current_room.name}'")
        except ValueError:
            logger.debug(f"❌ Current room '{self.current_room.name}' not in room list")

    def get_room_list(self) -> List[str]:
        """Get ordered list of room names"""
        if not self.project_data:
            return []

        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        room_order = self.project_data.get('room_order', [])

        if room_order:
            return [r for r in room_order if r in rooms_data]
        else:
            return list(rooms_data.keys())

    def trigger_room_end_event(self):
        """Trigger room_end event on all instances in current room"""
        if not self.current_room:
            return

        for instance in self.current_room.instances:
            if instance.object_data and "events" in instance.object_data:
                instance.action_executor.execute_event(instance, "room_end", instance.object_data["events"])

    def trigger_room_start_event(self):
        """Trigger room_start event on all instances in current room"""
        if not self.current_room:
            return

        for instance in self.current_room.instances:
            if instance.object_data and "events" in instance.object_data:
                instance.action_executor.execute_event(instance, "room_start", instance.object_data["events"])

    def trigger_game_start_event(self):
        """Trigger the once-per-game `game_start` event on all instances in the
        starting room. Fires at launch (and again on game restart), after Create
        and before Room Start, matching GameMaker's Game Start event. Games
        commonly use it to initialise score/lives and the window caption — if it
        never fires, that setup is skipped (e.g. the lives counter stays hidden
        until something else flips it on)."""
        if not self.current_room:
            return

        for instance in self.current_room.instances:
            if instance.object_data and "events" in instance.object_data:
                instance.action_executor.execute_event(instance, "game_start", instance.object_data["events"])

    # Frames spent fading each direction (out then in) — half a second each
    # way at a 30fps room_speed, scaled by the room's actual speed so it
    # reads the same regardless of project fps.
    _FADE_TRANSITION_SECONDS = 0.25

    def _fade_overlay(self, base_frame: "pygame.Surface", fade_in: bool):
        """Blocking sub-loop: replay base_frame under a black overlay whose
        alpha ramps 255->0 (fade_in) or 0->255 (fade out) over
        _FADE_TRANSITION_SECONDS. Mirrors show_message_dialog's existing
        "own local event/render loop" pattern — game logic is frozen for
        these frames (deliberately: a transition is a pause, not extra
        simulated time), only the overlay's alpha advances.

        Safe to call with self.screen is None (headless/test contexts):
        no-ops immediately, matching every other rendering path's guard.
        """
        if not self.screen:
            return
        frame_count = max(1, int(self.fps * self._FADE_TRANSITION_SECONDS))
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        clock = pygame.time.Clock()
        for step in range(frame_count):
            # Let the OS know we're alive; a closed window mid-transition
            # must not hang the process waiting out the fade.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            progress = (step + 1) / frame_count
            # fade_in: 255 (opaque black, hiding the new room) -> 0 (fully
            # visible). fade_out (the old room): the reverse, 0 -> 255.
            alpha = int(255 * ((1 - progress) if fade_in else progress))
            alpha = max(0, min(255, alpha))
            self.screen.blit(base_frame, (0, 0))
            overlay.fill((0, 0, 0, alpha))
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            clock.tick(self.fps)

    def change_room(self, room_name: str, transition: str = 'none'):
        """Change to a different room.

        transition: 'none' (default, instant — unchanged behaviour) or
        'fade' (fade to black, switch, fade back in). Any other value is
        treated as 'none' — matching the runtime's general "unknown ->
        no-op" convention rather than raising. Only 'fade' is implemented;
        see TODO.md's "Room transition effects" entry.
        """
        if room_name in self.rooms:
            do_fade = transition == 'fade' and self.screen is not None
            if do_fade:
                # Snapshot whatever's already on screen from the last
                # rendered frame — no extra render() call needed (and no
                # risk of double-firing draw_gui/update_views the way a
                # full render() pass would — see show_message_dialog's
                # matching one-off self.current_room.render() precedent
                # used below for the fade-in snapshot).
                old_frame = self.screen.copy()
                self._fade_overlay(old_frame, fade_in=False)

            # Collect persistent instances from the current room before leaving
            persistent_instances = []
            if self.current_room:
                for instance in self.current_room.instances:
                    # Check if object is marked as persistent
                    if instance.object_data and instance.object_data.get('persistent', False):
                        persistent_instances.append(instance)
                        logger.debug(f"  💾 Carrying persistent instance: {instance.object_name}")

                # Trigger room_end event in the current room before leaving
                self.trigger_room_end_event()

            logger.debug(f"🚪 Changing to room: {room_name}")

            # A room rebuilds fresh from its authored layout every time it's
            # RE-entered, unless explicitly marked persistent — real
            # GameMaker semantics (see set_room_persistent /
            # GameRoom.persistent). Only fires on an actual revisit
            # (room_name already in _visited_rooms); the room's first-ever
            # entry uses the pristine object GameRoom already built at load,
            # so rebuilding it again would be redundant. _build_room_from_data
            # is the same helper restart_room/restart_game use — it also
            # drops any remember_destroyed instances via _apply_destroyed_memory,
            # so that mechanism keeps working on a non-persistent revisit too.
            target_room = self.rooms[room_name]
            if room_name in self._visited_rooms and not target_room.persistent:
                room_data = self.project_data.get('assets', {}).get('rooms', {}).get(room_name)
                if room_data:
                    target_room = self._build_room_from_data(room_name, room_data)
                    self.rooms[room_name] = target_room
            self._visited_rooms.add(room_name)
            self.current_room = target_room

            # Add persistent instances to the new room
            objects_data = self._objects_data
            for persistent_inst in persistent_instances:
                # Remove any existing instances of the same object type that are NOT persistent
                # This ensures the persistent instance replaces the room's default instance
                self.current_room.instances = [
                    inst for inst in self.current_room.instances
                    if not (inst.object_name == persistent_inst.object_name and
                            not inst.object_data.get('persistent', False))
                ]

                # IMPORTANT: Refresh the persistent instance's object_data from project
                # This ensures any changes to events/properties are picked up
                if persistent_inst.object_name in objects_data:
                    merged = resolve_parent_inheritance(objects_data[persistent_inst.object_name], objects_data)
                    persistent_inst.set_object_data(merged)

                # Reset velocity when entering a new room to prevent momentum carry-over
                # This fixes the bug where player bounces back onto a door due to residual speed
                persistent_inst.hspeed = 0
                persistent_inst.vspeed = 0
                logger.debug(f"  🛑 Reset velocity for persistent instance: {persistent_inst.object_name}")

                # Check if this exact persistent instance is already in the new room
                if persistent_inst not in self.current_room.instances:
                    self.current_room.instances.append(persistent_inst)
                    logger.debug(f"  ➕ Added persistent instance to new room: {persistent_inst.object_name}")

            # Rebuild spatial grid with the new instances
            self.current_room.rebuild_spatial_grid()
            self.current_room.invalidate_collision_listened_types()

            # Resize the window if room size is different
            if self.screen:
                room_width, room_height = self._window_size_for(
                    self.current_room)
                current_width, current_height = self.screen.get_size()

                if room_width != current_width or room_height != current_height:
                    logger.debug(f"📐 Resizing window from {current_width}x{current_height} to {room_width}x{room_height}")
                    self.screen = pygame.display.set_mode((room_width, room_height))
                    self.window_width = room_width
                    self.window_height = room_height
                    logger.debug(f"✅ Window resized to {room_width}x{room_height}")

            # Execute create events for NEW instances only (not persistent ones that carried over)
            for instance in self.current_room.instances:
                if instance not in persistent_instances:
                    if instance.object_data and "events" in instance.object_data:
                        instance.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # Execute room_start event for all instances (after create events)
            self.trigger_room_start_event()

            # Set grace period to skip collision detection for 1 frame
            # This prevents immediate collision triggers when player spawns on a portal
            self._room_transition_grace_frames = 1

            if do_fade:
                # One-off snapshot render of the new room (create/room_start
                # already ran above, so this shows real starting state, not
                # a blank frame) — same "render once outside the main loop
                # to capture a frame" precedent show_message_dialog uses.
                self.current_room.render(self.screen)
                new_frame = self.screen.copy()
                self._fade_overlay(new_frame, fade_in=True)

    def get_caption_text(self, key: str) -> str:
        """Get translated caption text for a key (score, lives, health, room)"""
        translations = CAPTION_TRANSLATIONS.get(self.language, CAPTION_TRANSLATIONS['en'])
        return translations.get(key, key.capitalize())

    def update_caption(self):
        """Update window caption with score/lives/health if enabled.

        Uses caching to avoid rebuilding and setting the caption every frame
        when the values haven't changed.
        """
        # Build current state tuple for comparison
        current_state = (
            self.score,
            self.lives,
            int(self.health),
            self.window_caption,
            self.show_score_in_caption,
            self.show_lives_in_caption,
            self.show_health_in_caption,
        )

        # Skip update if nothing changed
        if current_state == self._last_caption_state:
            return

        self._last_caption_state = current_state

        parts = []

        if self.window_caption:
            parts.append(self.window_caption)

        if self.show_score_in_caption:
            parts.append(f"{self.get_caption_text('score')}: {self.score}")

        if self.show_lives_in_caption:
            parts.append(f"{self.get_caption_text('lives')}: {self.lives}")

        if self.show_health_in_caption:
            parts.append(f"{self.get_caption_text('health')}: {int(self.health)}")

        caption = " | ".join(parts) if parts else "Game"
        pygame.display.set_caption(caption)

    def render(self):
        """Render the game"""
        if not self.screen or not self.current_room:
            return

        # Update window caption with score/lives/health
        self.update_caption()

        # Per-tick view update (follow targets, clamp to room) before rendering.
        self.current_room.update_views()

        # Render current room
        self.current_room.render(self.screen)

        # Render Thymio robots (on top of regular sprites)
        for instance in self.current_room.instances:
            if instance.is_thymio and instance.thymio_simulator:
                render_data = instance.thymio_simulator.get_render_data()
                self.thymio_renderer.render(self.screen, render_data)

        # Draw GUI layer (drawn on top of everything, in screen coordinates)
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue
            events = instance.object_data.get('events', {})
            if 'draw_gui' in events:
                instance._draw_queue = []
                instance.action_executor.execute_event(instance, 'draw_gui', events)
                instance._process_draw_queue(self.screen)

        # Update display
        pygame.display.flip()

    def trigger_no_more_lives_event(self, triggering_instance=None):
        """Trigger the no_more_lives event for all instances that have it defined"""
        if not self.current_room:
            return

        logger.debug("💀 Triggering no_more_lives event for all instances...")

        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})
            if 'no_more_lives' in events:
                logger.debug(f"  📢 Executing no_more_lives for {instance.object_name}")
                instance.action_executor.execute_event(instance, 'no_more_lives', events)

    def trigger_no_more_health_event(self, triggering_instance=None):
        """Trigger the no_more_health event for all instances that have it defined

        Note: This only triggers custom no_more_health events. Any behavior like
        decrementing lives or resetting health must be explicitly programmed
        by the user in their no_more_health event actions.
        """
        if not self.current_room:
            return

        logger.debug("💔 Triggering no_more_health event for all instances...")

        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})
            if 'no_more_health' in events:
                logger.debug(f"  📢 Executing no_more_health for {instance.object_name}")
                instance.action_executor.execute_event(instance, 'no_more_health', events)


    def stop_game(self):
        """Stop the game"""
        logger.debug("Stopping game...")
        self.running = False

    def run(self):
        """Run the game - main entry point called by IDE"""
        if not self.project_data:
            logger.debug("❌ No project loaded. Cannot run game.")
            return False

        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            logger.debug("❌ No rooms found in project")
            return False

        logger.debug(f"🎮 Starting game with room: {starting_room}")
        self.current_room = self.rooms[starting_room]
        self._visited_rooms.add(starting_room)

        self.window_width, self.window_height = self._window_size_for(
            self.current_room)

        # Run the game loop
        return self.run_game_loop()

    def process_pending_messages(self):
        """Check all instances for pending messages and display them"""
        for instance in self.current_room.instances:
            # pending_messages is now always initialized in __init__
            if instance.pending_messages:
                # Get the first pending message
                message = instance.pending_messages.pop(0)
                # Display the message dialog (this pauses the game)
                self.show_message_dialog(message)

    def show_message_dialog(self, message: str):
        """Display a message dialog box that pauses the game

        The dialog shows the message centered on screen with an OK button.
        User can click OK or press Enter/Space/Escape to dismiss.
        """
        logger.debug(f"📢 Showing message dialog: {message}")

        # Make sure we have a screen
        if not self.screen:
            logger.debug("⚠️ Cannot show message dialog - no screen")
            return

        # views_1 is the sample that exposed this: its obj_player shows a
        # message in game_start, so the run hung before its first frame.
        # Under the opt-in frame budget (see _frame_budget()), there is no
        # real input to dismiss this with -- a headless verification run
        # (tools/verify_desktop_export.py) drives SDL's dummy driver, so no
        # KEYDOWN/mouse event can ever arrive and the wait loop below spins
        # forever. Auto-dismiss immediately, matching the frame budget's own
        # "a player's game is never affected" contract: this only ever
        # triggers when PYGM_MAX_FRAMES is explicitly set, never in a normal
        # build. Both the exported binary and the reference source-engine
        # render skip it identically, so --compare stays apples-to-apples.
        if self._frame_budget():
            logger.debug(f"📢 Message dialog auto-dismissed (frame budget mode): {message}")
            return

        # Clear any pending events to prevent accidental dismissal
        pygame.event.clear()

        # Store and pause all instance speeds during dialog
        # This prevents instances from moving while dialog is open, but restores speeds afterward
        saved_speeds = {}
        if self.current_room:
            for instance in self.current_room.instances:
                saved_speeds[id(instance)] = (instance.hspeed, instance.vspeed)
                instance.hspeed = 0
                instance.vspeed = 0

        # Render the current game state first (so dialog appears over the game)
        if self.current_room:
            self.current_room.render(self.screen)
            pygame.display.flip()

        # Use actual screen size for centering (in case window was resized)
        screen_w, screen_h = self.screen.get_size()

        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)

        # Get font
        try:
            font = pygame.font.Font(None, 24)
            title_font = pygame.font.Font(None, 28)
        except Exception:
            font = pygame.font.SysFont('arial', 18)
            title_font = pygame.font.SysFont('arial', 22)

        # Dialog width is fixed; the height grows to fit the message.
        dialog_width = min(400, screen_w - 40)
        max_text_width = dialog_width - 30
        line_height = 22
        text_top = 45  # first message line, below the 30px title bar

        # GameMaker '#' starts a new line. Honour explicit line breaks first,
        # then word-wrap each line to the dialog width. Computed once here
        # rather than every frame inside the dialog loop.
        lines = []
        for paragraph in expand_hash_newlines(message).split('\n'):
            current_line = ""
            for word in paragraph.split():
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] <= max_text_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            lines.append(current_line)  # final (possibly empty) line of paragraph

        # Size the dialog to fit the title, every message line and the button,
        # clamped to the screen.
        button_width = 80
        button_height = 30
        dialog_height = text_top + len(lines) * line_height + 15 + button_height + 15
        dialog_height = min(dialog_height, screen_h - 40)
        dialog_x = (screen_w - dialog_width) // 2
        dialog_y = (screen_h - dialog_height) // 2

        button_x = dialog_x + (dialog_width - button_width) // 2
        button_y = dialog_y + dialog_height - button_height - 15

        # Dialog loop - waits for user to dismiss
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False
                elif event.type == pygame.KEYUP:
                    # Don't let a key released while the dialog is open stay
                    # stuck in keys_pressed (M54).
                    self._release_held_key_silent(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if OK button was clicked
                    mx, my = event.pos
                    if (button_x <= mx <= button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        waiting = False

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw dialog box
            pygame.draw.rect(self.screen, (240, 240, 240),
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, (100, 100, 100),
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)

            # Draw title bar
            pygame.draw.rect(self.screen, (70, 130, 180),
                           (dialog_x, dialog_y, dialog_width, 30))
            title_text = title_font.render("Message", True, (255, 255, 255))
            self.screen.blit(title_text, (dialog_x + 10, dialog_y + 5))

            # Render the pre-wrapped message lines (computed above).
            y_offset = dialog_y + text_top
            for line in lines:
                text_surface = font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (dialog_x + 15, y_offset))
                y_offset += line_height

            # Draw OK button
            mouse_pos = pygame.mouse.get_pos()
            button_hover = (button_x <= mouse_pos[0] <= button_x + button_width and
                          button_y <= mouse_pos[1] <= button_y + button_height)

            button_color = (100, 149, 237) if button_hover else (70, 130, 180)
            pygame.draw.rect(self.screen, button_color,
                           (button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (button_x, button_y, button_width, button_height), 1)

            ok_text = font.render("OK", True, (255, 255, 255))
            ok_text_x = button_x + (button_width - ok_text.get_width()) // 2
            ok_text_y = button_y + (button_height - ok_text.get_height()) // 2
            self.screen.blit(ok_text, (ok_text_x, ok_text_y))

            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)

        # Restore instance speeds after dialog is dismissed
        if self.current_room:
            for instance in self.current_room.instances:
                if id(instance) in saved_speeds:
                    instance.hspeed, instance.vspeed = saved_speeds[id(instance)]

    def show_splash_image(self, surface: pygame.Surface):
        """Show a sprite full-screen, pausing the game until the player
        dismisses it (any key or mouse click) -- the image counterpart of
        show_message_dialog, same blocking-loop shape and speed-pause/
        restore treatment. Scaled to fit the screen while preserving
        aspect ratio, letterboxed in black.
        """
        logger.debug("🖼️ Showing splash image")

        if not self.screen:
            logger.debug("⚠️ Cannot show splash image - no screen")
            return

        pygame.event.clear()

        saved_speeds = {}
        if self.current_room:
            for instance in self.current_room.instances:
                saved_speeds[id(instance)] = (instance.hspeed, instance.vspeed)
                instance.hspeed = 0
                instance.vspeed = 0

        screen_w, screen_h = self.screen.get_size()
        img_w, img_h = surface.get_size()
        if img_w <= 0 or img_h <= 0:
            return

        scale = min(screen_w / img_w, screen_h / img_h)
        if scale <= 0:
            return
        draw_w, draw_h = max(1, round(img_w * scale)), max(1, round(img_h * scale))
        scaled = (surface if (draw_w, draw_h) == (img_w, img_h)
                 else pygame.transform.smoothscale(surface, (draw_w, draw_h)))
        dest_x = (screen_w - draw_w) // 2
        dest_y = (screen_h - draw_h) // 2

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
                elif event.type == pygame.KEYUP:
                    # Mirrors show_message_dialog's own M54 fix -- don't let
                    # a key released while the splash is open stay stuck in
                    # keys_pressed.
                    self._release_held_key_silent(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

            self.screen.fill((0, 0, 0))
            self.screen.blit(scaled, (dest_x, dest_y))
            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)

        # Restore instance speeds after the splash is dismissed
        if self.current_room:
            for instance in self.current_room.instances:
                if id(instance) in saved_speeds:
                    instance.hspeed, instance.vspeed = saved_speeds[id(instance)]

    # ==================== HIGHSCORE SYSTEM ====================

    def load_highscores(self):
        """Load highscores from file"""
        if not self.highscore_file:
            return

        try:
            if self.highscore_file.exists():
                with open(self.highscore_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.highscores = [(entry['name'], entry['score']) for entry in data]
                    logger.debug(f"📊 Loaded {len(self.highscores)} highscores from {self.highscore_file}")
        except Exception as e:
            logger.debug(f"⚠️ Could not load highscores: {e}")
            self.highscores = []

    def save_highscores(self):
        """Save highscores to file"""
        if not self.highscore_file:
            return

        try:
            # Ensure directory exists
            self.highscore_file.parent.mkdir(parents=True, exist_ok=True)

            data = [{'name': name, 'score': score} for name, score in self.highscores]
            with open(self.highscore_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 Saved {len(self.highscores)} highscores to {self.highscore_file}")
        except Exception as e:
            logger.debug(f"⚠️ Could not save highscores: {e}")

    def clear_highscores(self):
        """Clear all highscores"""
        self.highscores = []
        self.save_highscores()
        logger.debug("🧹 Highscore table cleared")

    def is_highscore(self, score: int) -> bool:
        """Check if a score qualifies for the highscore table"""
        if len(self.highscores) < self.highscore_max_entries:
            return True
        # Check if score is higher than the lowest entry
        if self.highscores:
            lowest_score = min(entry[1] for entry in self.highscores)
            return score > lowest_score
        return True

    def add_highscore(self, name: str, score: int):
        """Add a new highscore entry"""
        self.highscores.append((name, score))
        # Sort by score descending
        self.highscores.sort(key=lambda x: x[1], reverse=True)
        # Keep only top entries
        self.highscores = self.highscores[:self.highscore_max_entries]
        self.save_highscores()

    def show_highscore_dialog(self, background_color=(255, 255, 220),
                               new_color=(255, 0, 0), other_color=(0, 0, 0),
                               allow_name_entry: bool = True):
        """Display the highscore table dialog

        Args:
            background_color: Background color for the dialog (R, G, B) - ignored, uses modern dark theme
            new_color: Color for the new highscore entry (R, G, B)
            other_color: Color for other entries (R, G, B) - ignored, uses theme colors
            allow_name_entry: If True and current score qualifies, prompt for name
        """
        logger.debug(f"🏆 Showing highscore dialog (score: {self.score})")

        if not self.screen:
            logger.debug("⚠️ Cannot show highscore dialog - no screen")
            return

        # Clear any pending events
        pygame.event.clear()

        # Check if current score qualifies and we should prompt for name
        player_name = None
        player_rank = -1
        if allow_name_entry and self.is_highscore(self.score) and self.score > 0:
            player_name = self._show_name_entry_dialog()
            if player_name:
                self.add_highscore(player_name, self.score)
                # Find the rank of the new entry
                for i, (name, score) in enumerate(self.highscores):
                    if name == player_name and score == self.score:
                        player_rank = i
                        break

        # Render the current game state first
        if self.current_room:
            self.current_room.render(self.screen)
            pygame.display.flip()

        # Modern dark theme colors (matching IDE)
        bg_dark = (30, 30, 30)           # #1e1e1e - main background
        bg_header = (0, 122, 204)        # #007acc - blue header (like IDE status bar)
        bg_row_odd = (37, 37, 38)        # #252526 - alternating row
        bg_row_even = (45, 45, 48)       # #2d2d30 - alternating row
        bg_highlight = (9, 71, 113)      # #094771 - selected/highlight
        text_primary = (224, 224, 224)   # #e0e0e0 - main text
        text_secondary = (150, 150, 150) # #969696 - secondary text
        _text_gold = (255, 215, 0)        # Gold for rank numbers
        text_new = (100, 200, 100)       # Green for new entry
        border_color = (62, 62, 66)      # #3e3e42 - borders
        button_normal = (0, 122, 204)    # #007acc - blue button
        button_hover = (28, 151, 234)    # #1c97ea - lighter blue

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)

        # Dialog dimensions
        dialog_width = min(420, self.window_width - 40)
        dialog_height = min(420, self.window_height - 40)
        dialog_x = (self.window_width - dialog_width) // 2
        dialog_y = (self.window_height - dialog_height) // 2

        # Button dimensions
        button_width = 100
        button_height = 32
        button_x = dialog_x + (dialog_width - button_width) // 2
        button_y = dialog_y + dialog_height - button_height - 16

        # Fonts - try to use a clean sans-serif font
        try:
            title_font = pygame.font.SysFont('segoeui', 24, bold=True)
            header_font = pygame.font.SysFont('segoeui', 16, bold=True)
            entry_font = pygame.font.SysFont('segoeui', 18)
            button_font = pygame.font.SysFont('segoeui', 16, bold=True)
        except Exception:
            try:
                title_font = pygame.font.SysFont('arial', 24, bold=True)
                header_font = pygame.font.SysFont('arial', 16, bold=True)
                entry_font = pygame.font.SysFont('arial', 18)
                button_font = pygame.font.SysFont('arial', 16, bold=True)
            except Exception:
                title_font = pygame.font.Font(None, 32)
                header_font = pygame.font.Font(None, 22)
                entry_font = pygame.font.Font(None, 24)
                button_font = pygame.font.Font(None, 22)

        # Dialog loop
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False
                elif event.type == pygame.KEYUP:
                    self._release_held_key_silent(event.key)  # M54
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if (button_x <= mx <= button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        waiting = False

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw dialog with rounded corners effect (draw multiple rects)
            # Main background
            pygame.draw.rect(self.screen, bg_dark,
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            # Border
            pygame.draw.rect(self.screen, border_color,
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)

            # Draw header bar
            header_height = 45
            pygame.draw.rect(self.screen, bg_header,
                           (dialog_x + 2, dialog_y + 2, dialog_width - 4, header_height))

            # Title text (translated)
            title_str = get_runtime_translation("HIGH SCORES", self.language)
            title_text = title_font.render(title_str, True, (255, 255, 255))
            title_x = dialog_x + (dialog_width - title_text.get_width()) // 2
            self.screen.blit(title_text, (title_x, dialog_y + 12))

            # Column headers background
            header_y = dialog_y + header_height + 10
            pygame.draw.rect(self.screen, bg_row_odd,
                           (dialog_x + 10, header_y, dialog_width - 20, 28))

            # Column headers (translated)
            rank_str = get_runtime_translation("Rank", self.language)
            name_str = get_runtime_translation("Name", self.language)
            score_str = get_runtime_translation("Score", self.language)
            rank_text = header_font.render(rank_str, True, text_secondary)
            name_text = header_font.render(name_str.upper(), True, text_secondary)
            score_text = header_font.render(score_str.upper(), True, text_secondary)

            self.screen.blit(rank_text, (dialog_x + 25, header_y + 6))
            self.screen.blit(name_text, (dialog_x + 70, header_y + 6))
            self.screen.blit(score_text, (dialog_x + dialog_width - 100, header_y + 6))

            # Draw highscore entries
            entry_start_y = header_y + 35
            entry_height = 30

            if not self.highscores:
                # No scores yet (translated)
                no_scores_str = get_runtime_translation("No scores yet!", self.language)
                no_scores_text = entry_font.render(no_scores_str, True, text_secondary)
                no_scores_x = dialog_x + (dialog_width - no_scores_text.get_width()) // 2
                self.screen.blit(no_scores_text, (no_scores_x, entry_start_y + 60))
            else:
                for i, (name, score) in enumerate(self.highscores[:10]):
                    entry_y = entry_start_y + i * entry_height

                    # Alternating row background
                    if i == player_rank:
                        row_bg = bg_highlight
                    elif i % 2 == 0:
                        row_bg = bg_row_even
                    else:
                        row_bg = bg_row_odd

                    pygame.draw.rect(self.screen, row_bg,
                                   (dialog_x + 10, entry_y, dialog_width - 20, entry_height - 2))

                    # Text color
                    if i == player_rank:
                        text_color = text_new
                        rank_color = text_new
                    else:
                        text_color = text_primary
                        # Gold/silver/bronze for top 3
                        if i == 0:
                            rank_color = (255, 215, 0)   # Gold
                        elif i == 1:
                            rank_color = (192, 192, 192) # Silver
                        elif i == 2:
                            rank_color = (205, 127, 50)  # Bronze
                        else:
                            rank_color = text_secondary

                    # Rank number
                    rank_str = str(i + 1)
                    rank_surface = entry_font.render(rank_str, True, rank_color)
                    self.screen.blit(rank_surface, (dialog_x + 25, entry_y + 5))

                    # Name (truncate if too long)
                    display_name = name[:18] + ".." if len(name) > 18 else name
                    name_surface = entry_font.render(display_name, True, text_color)
                    self.screen.blit(name_surface, (dialog_x + 70, entry_y + 5))

                    # Score (right-aligned)
                    score_str = f"{score:,}"
                    score_surface = entry_font.render(score_str, True, text_color)
                    score_x = dialog_x + dialog_width - 30 - score_surface.get_width()
                    self.screen.blit(score_surface, (score_x, entry_y + 5))

            # Draw OK button
            mouse_pos = pygame.mouse.get_pos()
            button_hover_state = (button_x <= mouse_pos[0] <= button_x + button_width and
                          button_y <= mouse_pos[1] <= button_y + button_height)

            btn_color = button_hover if button_hover_state else button_normal
            pygame.draw.rect(self.screen, btn_color,
                           (button_x, button_y, button_width, button_height))

            ok_str = get_runtime_translation("OK", self.language)
            ok_text = button_font.render(ok_str, True, (255, 255, 255))
            ok_x = button_x + (button_width - ok_text.get_width()) // 2
            ok_y = button_y + (button_height - ok_text.get_height()) // 2
            self.screen.blit(ok_text, (ok_x, ok_y))

            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)

    def _show_name_entry_dialog(self) -> str:
        """Show dialog to enter player name for highscore

        Returns:
            Player name or empty string if cancelled
        """
        logger.debug("📝 Showing name entry dialog")

        if not self.screen:
            return ""

        pygame.event.clear()

        # Render game state
        if self.current_room:
            self.current_room.render(self.screen)
            pygame.display.flip()

        # Modern dark theme colors (matching IDE)
        bg_dark = (30, 30, 30)           # #1e1e1e
        bg_header = (0, 122, 204)        # #007acc
        bg_input = (45, 45, 48)          # #2d2d30
        text_primary = (224, 224, 224)   # #e0e0e0
        text_score = (100, 200, 100)     # Green for score
        border_color = (62, 62, 66)      # #3e3e42
        input_border = (0, 122, 204)     # Blue border for focused input
        button_ok = (0, 122, 204)        # #007acc
        button_ok_hover = (28, 151, 234) # #1c97ea
        _button_cancel = (90, 90, 90)     # Gray
        _button_cancel_hover = (110, 110, 110)

        # Overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)

        # Dialog dimensions
        dialog_width = min(380, self.window_width - 40)
        dialog_height = 200
        dialog_x = (self.window_width - dialog_width) // 2
        dialog_y = (self.window_height - dialog_height) // 2

        # Input field dimensions
        input_width = dialog_width - 50
        input_height = 36
        input_x = dialog_x + 25
        input_y = dialog_y + 110

        # Button dimensions
        button_width = 90
        button_height = 32
        ok_button_x = dialog_x + dialog_width // 2 - button_width - 8
        cancel_button_x = dialog_x + dialog_width // 2 + 8
        button_y = dialog_y + dialog_height - button_height - 16

        # Fonts
        try:
            title_font = pygame.font.SysFont('segoeui', 22, bold=True)
            label_font = pygame.font.SysFont('segoeui', 16)
            score_font = pygame.font.SysFont('segoeui', 20, bold=True)
            input_font = pygame.font.SysFont('segoeui', 18)
            button_font = pygame.font.SysFont('segoeui', 15, bold=True)
        except Exception:
            try:
                title_font = pygame.font.SysFont('arial', 22, bold=True)
                label_font = pygame.font.SysFont('arial', 16)
                score_font = pygame.font.SysFont('arial', 20, bold=True)
                input_font = pygame.font.SysFont('arial', 18)
                button_font = pygame.font.SysFont('arial', 15, bold=True)
            except Exception:
                title_font = pygame.font.Font(None, 28)
                label_font = pygame.font.Font(None, 22)
                score_font = pygame.font.Font(None, 26)
                input_font = pygame.font.Font(None, 24)
                button_font = pygame.font.Font(None, 20)

        player_name = ""
        max_name_length = 20
        cursor_visible = True
        cursor_timer = 0

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    return ""
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip():
                            return player_name.strip()
                    elif event.key == pygame.K_ESCAPE:
                        return ""
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.unicode and len(player_name) < max_name_length:
                        # Only allow printable characters
                        if event.unicode.isprintable():
                            player_name += event.unicode
                elif event.type == pygame.KEYUP:
                    self._release_held_key_silent(event.key)  # M54
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # OK button
                    if (ok_button_x <= mx <= ok_button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        if player_name.strip():
                            return player_name.strip()
                    # Cancel button
                    if (cancel_button_x <= mx <= cancel_button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        return ""

            # Update cursor blink
            cursor_timer += 1
            if cursor_timer >= 30:
                cursor_visible = not cursor_visible
                cursor_timer = 0

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw dialog background
            pygame.draw.rect(self.screen, bg_dark,
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, border_color,
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)

            # Header bar
            header_height = 45
            pygame.draw.rect(self.screen, bg_header,
                           (dialog_x + 2, dialog_y + 2, dialog_width - 4, header_height))

            # Title (translated)
            title_str = get_runtime_translation("NEW HIGH SCORE!", self.language)
            title_text = title_font.render(title_str, True, (255, 255, 255))
            title_x = dialog_x + (dialog_width - title_text.get_width()) // 2
            self.screen.blit(title_text, (title_x, dialog_y + 12))

            # Score display (translated)
            score_label = get_runtime_translation("Score", self.language)
            score_text = score_font.render(f"{score_label}: {self.score:,}", True, text_score)
            score_x = dialog_x + (dialog_width - score_text.get_width()) // 2
            self.screen.blit(score_text, (score_x, dialog_y + 55))

            # Name label (translated)
            label_str = get_runtime_translation("Enter your name:", self.language)
            label_text = label_font.render(label_str, True, text_primary)
            self.screen.blit(label_text, (input_x, input_y - 22))

            # Input field
            pygame.draw.rect(self.screen, bg_input,
                           (input_x, input_y, input_width, input_height))
            pygame.draw.rect(self.screen, input_border,
                           (input_x, input_y, input_width, input_height), 2)

            # Input text with cursor
            display_text = player_name
            if cursor_visible:
                display_text += "|"
            name_surface = input_font.render(display_text, True, text_primary)
            self.screen.blit(name_surface, (input_x + 10, input_y + 8))

            # Buttons
            mouse_pos = pygame.mouse.get_pos()

            # OK button
            ok_hover = (ok_button_x <= mouse_pos[0] <= ok_button_x + button_width and
                       button_y <= mouse_pos[1] <= button_y + button_height)
            ok_color = button_ok_hover if ok_hover else button_ok
            pygame.draw.rect(self.screen, ok_color,
                           (ok_button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (ok_button_x, button_y, button_width, button_height), 1)
            ok_str = get_runtime_translation("OK", self.language)
            ok_text = button_font.render(ok_str, True, (255, 255, 255))
            self.screen.blit(ok_text, (ok_button_x + (button_width - ok_text.get_width()) // 2,
                                       button_y + (button_height - ok_text.get_height()) // 2))

            # Cancel button (translated)
            cancel_hover = (cancel_button_x <= mouse_pos[0] <= cancel_button_x + button_width and
                           button_y <= mouse_pos[1] <= button_y + button_height)
            cancel_color = (180, 100, 100) if cancel_hover else (150, 80, 80)
            pygame.draw.rect(self.screen, cancel_color,
                           (cancel_button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (cancel_button_x, button_y, button_width, button_height), 1)
            cancel_str = get_runtime_translation("Cancel", self.language)
            cancel_text = button_font.render(cancel_str, True, (255, 255, 255))
            self.screen.blit(cancel_text, (cancel_button_x + (button_width - cancel_text.get_width()) // 2,
                                           button_y + (button_height - cancel_text.get_height()) // 2))

            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)

        return ""

    def update_thymio_robots(self):
        """Update all Thymio robot simulators and trigger events"""
        if not self.current_room:
            return

        # Find Thymio instances first. If none, the room is non-Thymio and the
        # obstacle-list scan below would just be wasted work — every frame.
        # (Profiling on a 131-instance maze showed this function consumed ~10%
        # of per-frame work time despite no Thymios being present.)
        thymio_instances = [
            inst for inst in self.current_room.instances
            if inst.is_thymio and inst.thymio_simulator
        ]
        if not thymio_instances:
            return

        # Get obstacles for collision detection (all solid instances that aren't Thymio)
        obstacles = []
        for instance in self.current_room.instances:
            # Check solid from cached object data
            obj_data = instance._cached_object_data
            is_solid = obj_data.get('solid', False) if obj_data else False
            if is_solid and not instance.is_thymio:
                if instance.sprite:
                    rect = pygame.Rect(
                        int(instance.x - instance.sprite.width / 2),
                        int(instance.y - instance.sprite.height / 2),
                        instance.sprite.width,
                        instance.sprite.height
                    )
                    obstacles.append(rect)

        # Update each Thymio robot
        for instance in thymio_instances:

            # Update simulator (returns dict of events that occurred)
            dt = 1/60  # 60 FPS
            thymio_events = instance.thymio_simulator.update(dt, obstacles, self.screen)

            # Sync instance position with simulator
            instance.x = instance.thymio_simulator.x
            instance.y = instance.thymio_simulator.y

            # Trigger Thymio events if they occurred
            if not instance.object_data or "events" not in instance.object_data:
                continue

            events = instance.object_data["events"]

            if thymio_events.get('proximity_update'):
                if 'thymio_proximity_update' in events:
                    instance.action_executor.execute_event(instance, 'thymio_proximity_update', events)

            if thymio_events.get('ground_update'):
                if 'thymio_ground_update' in events:
                    instance.action_executor.execute_event(instance, 'thymio_ground_update', events)

            if thymio_events.get('timer_0'):
                if 'thymio_timer_0' in events:
                    instance.action_executor.execute_event(instance, 'thymio_timer_0', events)

            if thymio_events.get('timer_1'):
                if 'thymio_timer_1' in events:
                    instance.action_executor.execute_event(instance, 'thymio_timer_1', events)

            if thymio_events.get('sound_finished'):
                if 'thymio_sound_finished' in events:
                    instance.action_executor.execute_event(instance, 'thymio_sound_finished', events)

    def cleanup(self):
        """Clean up pygame resources"""
        try:
            if pygame.get_init():
                pygame.quit()
            logger.debug("Game cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Test function
def test_runner():
    """Test the enhanced game runner"""
    runner = GameRunner()

    # Test with a project path - replace with actual path
    test_project = "/path/to/your/project"

    if Path(test_project).exists():
        runner.test_game(test_project)
    else:
        logger.error(f"Test project not found: {test_project}")
        logger.debug("Please update the test_project path")

if __name__ == "__main__":
    test_runner()
