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

import math
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


class GameRunner(InputMixin):
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
    # inherits from InputMixin (`class GameRunner(InputMixin):` above) so
    # all of these remain callable as self.<name>(...) exactly as before.

    @staticmethod
    def _get_step_grid_size(instance) -> int:
        """Detect grid size from an instance's step event (if_on_grid parameter).

        Returns the grid_size if the instance has an if_on_grid action in its
        step event, or 0 if not found.
        """
        obj_data = instance._cached_object_data if instance._cached_object_data else {}
        step_event = obj_data.get('events', {}).get('step', {})
        for action in step_event.get('actions', []):
            if action.get('action') == 'if_on_grid':
                grid = action.get('parameters', {}).get('grid_size')
                if grid:
                    try:
                        return int(grid)
                    except (ValueError, TypeError):
                        pass
        return 0

    @staticmethod
    def _get_any_grid_size(instance) -> int:
        """Detect grid size from any event on an instance (if_on_grid parameter).

        Searches all events (step, keyboard nokey, etc.) for if_on_grid.
        Returns the grid_size or 0 if not found.
        """
        obj_data = instance._cached_object_data if instance._cached_object_data else {}
        events = obj_data.get('events', {})
        for event_name, event_data in events.items():
            # Handle nested keyboard events (keyboard -> nokey -> actions)
            if isinstance(event_data, dict):
                actions = event_data.get('actions', [])
                if not actions and isinstance(event_data, dict):
                    # Check nested events (e.g., keyboard -> nokey)
                    for sub_name, sub_data in event_data.items():
                        if isinstance(sub_data, dict):
                            for action in sub_data.get('actions', []):
                                if action.get('action') == 'if_on_grid':
                                    grid = action.get('parameters', {}).get('grid_size')
                                    if grid:
                                        try:
                                            return int(grid)
                                        except (ValueError, TypeError):
                                            pass
                for action in actions:
                    if action.get('action') == 'if_on_grid':
                        grid = action.get('parameters', {}).get('grid_size')
                        if grid:
                            try:
                                return int(grid)
                            except (ValueError, TypeError):
                                pass
        return 0


    def _slide_axis_to_contact(self, instance, axis: str, objects_data: dict):
        """Advance a blocked instance pixel-by-pixel along one axis until it
        rests flush against the blocker, instead of cancelling the whole move.

        Called from the blocked branch of the hspeed/vspeed movement step, so
        the full move has already been found to collide. ``axis`` is 'x' or
        'y'. Steps at most ``floor(|speed|)`` whole pixels toward the intended
        position, stopping one pixel before the first colliding cell; this
        leaves at most a sub-pixel residual gap, well within the 1px ground
        probe platformer logic relies on. Leaves intended_x/intended_y equal to
        the resting position so the post-move bookkeeping (and
        _process_held_keys) sees no pending move.

        O(|speed|) collision checks per blocked instance per frame — negligible
        for the handful of fast movers in a typical scene; revisit with a
        binary search if a stress scene ever makes it hot.
        """
        speed = instance.hspeed if axis == 'x' else instance.vspeed
        step = 1.0 if speed > 0 else -1.0
        remaining = abs(speed)
        moved = 0.0
        while moved + 1.0 <= remaining:
            if axis == 'x':
                instance.intended_x = instance.x + step
                instance.intended_y = instance.y
            else:
                instance.intended_x = instance.x
                instance.intended_y = instance.y + step
            sub_can, _ = self.check_movement_collision_with_blocker(instance, objects_data)
            if not sub_can:
                break
            if axis == 'x':
                instance.x = instance.intended_x
            else:
                instance.y = instance.intended_y
            moved += 1.0
        instance.intended_x = instance.x
        instance.intended_y = instance.y

    def check_movement_collision_with_blocker(self, moving_instance, objects_data: dict):
        """Check if intended movement would be blocked by another instance.

        Blocking rule (matches GameMaker 7.0):
        1. There must be a collision event defined between the two object
           types (in either direction — walks parent chains).
        2. At least ONE of the two objects must be marked `solid`. Pairs
           of two non-solid objects fire their collision events through
           the post-movement overlap detection path
           (`detect_collisions_for_instance`) but never physically block
           each other. This is why e.g. a maze monster can run THROUGH the
           player and trigger the death animation without getting stuck
           on top of the player's sprite — both are non-solid.

        Solid + collision-event is the Sokoban shape: the player blocks
        on the box, the box's `collision_with_player` handler runs
        if_can_push to move the box one cell, and the blocked-then-pushed
        loop in `update()` re-tries the player's move.

        Returns:
            (can_move: bool, blocking_instance: GameInstance or None)
        """
        intended_x = moving_instance.intended_x
        intended_y = moving_instance.intended_y

        # Use cached dimensions
        w1 = moving_instance._cached_width
        h1 = moving_instance._cached_height

        # Pre-parsed collision targets for the moving instance
        collision_targets = moving_instance._collision_targets

        # Fast-path: if neither this instance nor any other in the room would
        # ever block this movement (no collision targets either way), the
        # nearby-instance scan below would always return should_block=False.
        # Skip it entirely. This is the dominant cost in scenes with many
        # moving instances that don't collide (profiled at ~75% of CPU on a
        # 1000-instance bouncing-drifters scene).
        if (not collision_targets
                and moving_instance.object_name not in self.current_room.get_collision_listened_types()):
            return (True, None)

        # Use spatial grid for faster collision detection
        nearby_instances = self.current_room.get_nearby_instances(intended_x, intended_y, w1, h1)

        for other_instance in nearby_instances:
            if other_instance == moving_instance:
                continue

            # Use cached object data if available
            other_obj_data = other_instance._cached_object_data
            if not other_obj_data:
                other_obj_data = objects_data.get(other_instance.object_name, {})

            # Step 1: is there a collision event in either direction?
            # Parent-chain match (via _object_matches_target) is load-bearing:
            # the event-firing path resolves collision_with_<parent> to child
            # instances, so the blocking path must too — otherwise movement
            # passes through, the post-movement event snaps the mover back,
            # and intended_x is left stale (it never gets reset on the "no
            # collision detected" branch). _process_held_keys then sees
            # intended_x != x and skips keyboard events forever.
            has_collision_event = False

            if collision_targets:
                # Check both current name and original name (before change_instance)
                names_to_check = {other_instance.object_name}
                original = getattr(other_instance, '_original_object_name', None)
                if original and original != other_instance.object_name:
                    names_to_check.add(original)

                for target_name in collision_targets:
                    for name in names_to_check:
                        if self._object_matches_target(name, target_name):
                            has_collision_event = True
                            break
                    if has_collision_event:
                        break

            if not has_collision_event:
                # Check if the other instance has a collision event with the mover
                other_collision_targets = other_instance._collision_targets
                if other_collision_targets:
                    for target_name in other_collision_targets:
                        if self._object_matches_target(moving_instance.object_name, target_name):
                            has_collision_event = True
                            break

            if not has_collision_event:
                continue

            # Step 2: also require at least one side to be `solid`. Two
            # non-solid objects with a collision event fire the event via
            # the post-movement overlap path (detect_collisions_for_instance)
            # but never physically block each other — that's why maze_3's
            # monster_all can run THROUGH obj_person and trigger the death
            # animation without getting wedged on top of the player sprite.
            # Sokoban-style pushable boxes work because the box itself is
            # marked solid; the player blocks on it, the box's collision
            # event runs if_can_push, and update()'s blocked-then-pushed
            # loop re-tries the move.
            moving_solid = bool(
                (moving_instance._cached_object_data or {}).get('solid', False)
            )
            other_solid = bool(other_obj_data.get('solid', False))
            if not (moving_solid or other_solid):
                continue

            # Use collision bboxes (smaller than full sprite for sprites
            # with transparent borders or explicit bbox_* metadata).
            # AABB-only here (no pixel-perfect refine): movement-blocking is
            # what the player feels as "the wall stops me here", and grid-maze
            # sprites with a few transparent edge pixels would otherwise let
            # the mover slip 1–N pixels into the wall's cell every frame
            # before being snapped back by the post-movement collision event,
            # producing a visible jitter. Pixel-perfect (sprite.precise) still
            # refines collision-event firing via instances_overlap, so damage
            # zones and pickup triggers keep their pixel accuracy. Phase 2a
            # originally wired precise into all three AABB call sites — this
            # narrows it to the two firing paths where it actually helps.
            s1 = moving_instance.sprite
            s2 = other_instance.sprite
            if s1 is None or s2 is None:
                continue
            bw1 = s1.bbox_right - s1.bbox_left
            bh1 = s1.bbox_bottom - s1.bbox_top
            bw2 = s2.bbox_right - s2.bbox_left
            bh2 = s2.bbox_bottom - s2.bbox_top
            # Move-target world position uses intended_*; offsets shift by the
            # sprite origin and bbox_left/top so we compare collision-bbox
            # corners, not whole-sprite corners.
            mx = intended_x - s1.origin_x + s1.bbox_left
            my = intended_y - s1.origin_y + s1.bbox_top
            ox = other_instance.x - s2.origin_x + s2.bbox_left
            oy = other_instance.y - s2.origin_y + s2.bbox_top

            if self.rectangles_overlap(mx, my, bw1, bh1, ox, oy, bw2, bh2):
                # If the mover already overlaps the blocker at its current
                # position, let it escape: blocking every direction would
                # trap it in an oscillation freeze on the next bounce.
                cur_mx = moving_instance.x - s1.origin_x + s1.bbox_left
                cur_my = moving_instance.y - s1.origin_y + s1.bbox_top
                if self.rectangles_overlap(cur_mx, cur_my, bw1, bh1, ox, oy, bw2, bh2):
                    continue
                return (False, other_instance)

        return (True, None)

    def separate_overlapping_instances(self, objects_data: dict):
        """Separate instances that are overlapping after collision events.

        When object A pushes object B but B can't move (hits solid), A should be pushed back.
        This only applies to instances that have collision events defined between them,
        and only when at least one of the objects is solid.
        """
        processed_pairs = set()

        for instance in self.current_room.instances:
            # Use pre-parsed collision targets for faster lookup
            collision_targets = instance._collision_targets
            if not collision_targets:
                continue

            # Use cached dimensions
            w1 = instance._cached_width
            h1 = instance._cached_height

            # Use spatial grid for faster collision detection
            nearby_instances = self.current_room.get_nearby_instances(instance.x, instance.y, w1, h1)

            for other_instance in nearby_instances:
                if other_instance == instance:
                    continue

                # Skip if we already processed this pair
                pair_key = (min(id(instance), id(other_instance)), max(id(instance), id(other_instance)))
                if pair_key in processed_pairs:
                    continue

                # Check if there's a collision event between these objects using pre-parsed targets
                if other_instance.object_name not in collision_targets:
                    continue

                # Only separate when at least one object is solid.
                # Non-solid collisions (e.g. ball/paddle bounce, death zone triggers)
                # should not cause physical separation.
                inst_obj_data = objects_data.get(instance.object_name, {})
                other_obj_data = objects_data.get(other_instance.object_name, {})
                if not inst_obj_data.get('solid', False) and not other_obj_data.get('solid', False):
                    continue

                # Check if collision bboxes overlap (smaller than full sprite
                # when sprite has transparent borders / explicit bbox_* meta).
                s1 = instance.sprite
                s2 = other_instance.sprite
                if s1 is None or s2 is None:
                    continue
                bw1 = s1.bbox_right - s1.bbox_left
                bh1 = s1.bbox_bottom - s1.bbox_top
                bw2 = s2.bbox_right - s2.bbox_left
                bh2 = s2.bbox_bottom - s2.bbox_top
                ix = instance.x - s1.origin_x + s1.bbox_left
                iy = instance.y - s1.origin_y + s1.bbox_top
                ox = other_instance.x - s2.origin_x + s2.bbox_left
                oy = other_instance.y - s2.origin_y + s2.bbox_top

                if self.rectangles_overlap(ix, iy, bw1, bh1, ox, oy, bw2, bh2):
                    # They're overlapping - push the moving instance back
                    # Determine which one was moving based on hspeed/vspeed
                    inst_moving = instance.hspeed != 0 or instance.vspeed != 0
                    other_moving = other_instance.hspeed != 0 or other_instance.vspeed != 0

                    # Pass bbox-world rects so separation is computed in the same
                    # coordinate space the overlap was detected in (M50). Mixing
                    # raw instance coords with bbox dims shifted the landing
                    # position by the sprite origin / bbox offsets.
                    if inst_moving and not other_moving:
                        self.push_back_instance(instance, ix, iy, bw1, bh1,
                                                ox, oy, bw2, bh2)
                    elif other_moving and not inst_moving:
                        self.push_back_instance(other_instance, ox, oy, bw2, bh2,
                                                ix, iy, bw1, bh1)

                    processed_pairs.add(pair_key)

    def push_back_instance(self, moving_inst, mbx, mby, mbw, mbh,
                           sbx, sby, sbw, sbh):
        """Push moving instance out of overlap with a static one.

        All rects are bbox-world coordinates (top-left + size). The instance's
        raw position is recovered by adding back its bbox-to-origin offset, so
        sprites with nonzero origin or auto-bbox margins land flush instead of
        a few pixels off (which broke grid alignment / re-triggered every frame).
        """
        # Offset from the moving instance's bbox-world top-left to its raw x/y.
        off_x = moving_inst.x - mbx
        off_y = moving_inst.y - mby

        overlap_left = (mbx + mbw) - sbx
        overlap_right = (sbx + sbw) - mbx
        overlap_top = (mby + mbh) - sby
        overlap_bottom = (sby + sbh) - mby

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_left and overlap_left > 0:
            moving_inst.x = (sbx - mbw) + off_x
        elif min_overlap == overlap_right and overlap_right > 0:
            moving_inst.x = (sbx + sbw) + off_x
        elif min_overlap == overlap_top and overlap_top > 0:
            moving_inst.y = (sby - mbh) + off_y
        elif min_overlap == overlap_bottom and overlap_bottom > 0:
            moving_inst.y = (sby + sbh) + off_y

    def check_outside_room_events(self):
        """Check for instances that have moved outside the room boundaries.

        Triggers outside_room event when an instance is completely outside the room.
        GameMaker convention: triggers when the instance's sprite is fully outside.
        """
        if not self.current_room:
            return

        room_width = self.current_room.width
        room_height = self.current_room.height

        for instance in self.current_room.instances:
            # Skip if no object data or events
            if not instance.object_data or "events" not in instance.object_data:
                continue

            events = instance.object_data["events"]
            if "outside_room" not in events:
                continue

            # Get instance bounds
            w = instance._cached_width
            h = instance._cached_height

            # The sprite's actual screen extent is x-origin_x .. x-origin_x+w
            # (rendering uses x - origin_x). Account for the origin so the event
            # fires exactly when the sprite is fully off-screen, not origin_x px
            # late/early for nonzero-origin sprites (L30).
            sprite = getattr(instance, 'sprite', None)
            origin_x = getattr(sprite, 'origin_x', 0) if sprite else 0
            origin_y = getattr(sprite, 'origin_y', 0) if sprite else 0
            left = instance.x - origin_x
            top = instance.y - origin_y

            # Check if completely outside room (not just partially)
            outside = (
                left + w < 0 or          # Completely off left
                left > room_width or     # Completely off right
                top + h < 0 or           # Completely off top
                top > room_height        # Completely off bottom
            )

            if outside:
                logger.debug(f"📤 outside_room event for {instance.object_name} at ({instance.x}, {instance.y})")
                instance.action_executor.execute_event(instance, "outside_room", events)

    def detect_collisions_for_instance(self, instance, objects_data: dict) -> list:
        """Detect collisions for an instance and capture speeds

        Returns a list of collision data dicts with speeds captured at detection time.
        Does NOT process the events - that's done separately.

        Optimized to use pre-parsed collision targets and cached dimensions.
        """
        collisions = []

        # Use pre-parsed collision targets (much faster than iterating all events)
        collision_targets = instance._collision_targets
        if not collision_targets:
            return collisions

        # _active_collisions and _collision_cooldowns are now initialized in __init__

        # Track which collisions are currently active this frame
        current_collisions = set()

        # Decrement cooldowns in single pass (avoid multiple iterations)
        cooldowns = instance._collision_cooldowns
        if cooldowns:
            keys_to_delete = []
            for key, frames in cooldowns.items():
                if frames <= 1:
                    keys_to_delete.append(key)
                else:
                    cooldowns[key] = frames - 1
            for key in keys_to_delete:
                del cooldowns[key]

        # Get nearby instances using spatial grid for faster detection
        # Use cached dimensions instead of sprite lookup
        w1 = instance._cached_width
        h1 = instance._cached_height
        nearby_instances = self.current_room.get_nearby_instances(instance.x, instance.y, w1, h1)

        # Cache instance speeds (avoid repeated getattr)
        inst_hspeed = instance.hspeed
        inst_vspeed = instance.vspeed

        # For each nearby instance, find the MOST-SPECIFIC collision target it
        # matches and fire only that event. Inverting the iteration (other-first
        # instead of target-first) prevents double-firing: when an object like
        # obj_marqueur (parent=obj_brique) is matched by BOTH
        # collision_with_obj_marqueur (direct) and collision_with_obj_brique
        # (parent), the previous target-first loop appended both, so the parent
        # brique-snap-and-stop behavior also fired on a no-op marker pickup.
        # Concretely: Pingus would freeze in mid-air when his sprite brushed a
        # marqueur during a jump, because the brique collision zeroed his
        # vspeed even though the marqueur-specific event was just `comment`.
        objects_data = self._objects_data
        for other_instance in nearby_instances:
            if other_instance == instance:
                continue

            # Walk other's name + parent chain; first match in collision_targets wins.
            matched_target = None
            current = other_instance.object_name
            for _ in range(10):  # depth cap matches _resolve_collision_event
                if current in collision_targets:
                    matched_target = current
                    break
                parent = objects_data.get(current, {}).get('parent', '')
                if not parent:
                    break
                current = parent

            if matched_target is None:
                continue

            if not self.instances_overlap(instance, other_instance):
                continue

            event_name = f"collision_with_{matched_target}"
            collision_key = (id(other_instance), event_name)
            current_collisions.add(collision_key)

            # Cache other instance speeds for collision data
            other_hspeed = other_instance.hspeed
            other_vspeed = other_instance.vspeed

            # Only fire event if this is a NEW collision AND not in cooldown
            in_cooldown = collision_key in instance._collision_cooldowns
            is_new_collision = collision_key not in instance._active_collisions
            should_fire = is_new_collision and not in_cooldown

            if should_fire:
                collisions.append({
                    'instance': instance,
                    'event_name': event_name,
                    'events': instance._cached_object_data.get('events', {}),
                    'other_instance': other_instance,
                    # Capture object names so we can detect change_instance
                    'object_name': instance.object_name,
                    'other_object_name': other_instance.object_name,
                    # Capture speeds at moment of collision detection
                    'self_hspeed': inst_hspeed,
                    'self_vspeed': inst_vspeed,
                    'other_hspeed': other_hspeed,
                    'other_vspeed': other_vspeed,
                })
                # Short cooldown (5 frames) prevents double-trigger in same collision
                # This is short enough to allow continuous pushing at normal speeds
                instance._collision_cooldowns[collision_key] = 5

        # Update active collisions for next frame
        instance._active_collisions = current_collisions

        return collisions

    def process_collision_event(self, collision_data: dict):
        """Process a single collision event with stored speeds"""
        instance = collision_data['instance']
        event_name = collision_data['event_name']
        events = collision_data['events']
        other_instance = collision_data['other_instance']

        # Skip if either instance changed type since detection (e.g., change_instance
        # transformed box into box_stored — remaining box events are stale)
        detected_name = collision_data.get('object_name')
        if detected_name and instance.object_name != detected_name:
            logger.debug(f"  ⏭️ Skipping stale collision {event_name}: {detected_name} changed to {instance.object_name}")
            return
        detected_other_name = collision_data.get('other_object_name')
        if detected_other_name and other_instance.object_name != detected_other_name:
            logger.debug(f"  ⏭️ Skipping stale collision {event_name}: other {detected_other_name} changed to {other_instance.object_name}")
            return

        # If the colliding instance is moving and has a grid-based step event,
        # snap it to the next grid position in its movement direction before
        # processing the event. Overlap collisions fire as soon as sprite edges
        # touch, but the instance should be on-grid when actions like
        # change_instance execute (e.g. Box landing on Store).
        # This is safe because the collision-checked push in the blocked
        # collision handler prevents moving instances from overlapping blockers.
        self_hspeed = collision_data.get('self_hspeed', 0)
        self_vspeed = collision_data.get('self_vspeed', 0)
        if self_hspeed != 0 or self_vspeed != 0:
            grid_size = self._get_step_grid_size(instance)
            if grid_size:
                if self_hspeed > 0:
                    instance.x = math.ceil(instance.x / grid_size) * grid_size
                elif self_hspeed < 0:
                    instance.x = math.floor(instance.x / grid_size) * grid_size
                if self_vspeed > 0:
                    instance.y = math.ceil(instance.y / grid_size) * grid_size
                elif self_vspeed < 0:
                    instance.y = math.floor(instance.y / grid_size) * grid_size
                # Stop since we snapped to destination
                instance.hspeed = 0
                instance.vspeed = 0
                logger.debug(f"  📐 Snapped moving instance to grid: {instance.object_name} → ({instance.x}, {instance.y})")

        # Use INFO level for important collisions (box with store)
        if 'obj_box' in instance.object_name and 'obj_store' in other_instance.object_name:
            logger.debug(f"🎯 BOX-STORE COLLISION: {instance.object_name} with {other_instance.object_name} at ({instance.x}, {instance.y})")
        else:
            logger.debug(f"🎯 COLLISION DETECTED: {instance.object_name} with {other_instance.object_name}")
        logger.debug(f"   Stored speeds - self: ({collision_data['self_hspeed']}, {collision_data['self_vspeed']}), other: ({collision_data['other_hspeed']}, {collision_data['other_vspeed']})")

        # Pass other_instance and collision speeds as context for collision actions
        instance.action_executor.execute_collision_event(
            instance,
            event_name,
            events,
            other_instance,
            collision_speeds={
                'self_hspeed': collision_data['self_hspeed'],
                'self_vspeed': collision_data['self_vspeed'],
                'other_hspeed': collision_data['other_hspeed'],
                'other_vspeed': collision_data['other_vspeed'],
            }
        )

    def check_not_collision_events(self, objects_data: dict):
        """Check for 'not_collision' events - these fire when instance is NOT colliding with target.

        Used for Sokoban-style mechanics where obj_box_store transforms back to obj_box
        when pushed off an obj_store.
        """
        # Iterate over a copy since we may destroy instances
        for instance in list(self.current_room.instances):
            if not instance._cached_object_data:
                continue

            events = instance._cached_object_data.get('events', {})

            # Look for not_collision_with_* events
            for event_name, event_data in events.items():
                if not event_name.startswith('not_collision_with_'):
                    continue

                target_object = event_name[19:]  # Remove 'not_collision_with_' prefix

                # Check if instance is colliding (bbox-level) with ANY instance
                # of target object. Bbox here matches the other firing paths
                # (instances_overlap, check_collision_at_position) so a
                # not_collision_with_X event has the same "what counts as
                # touching" semantics as collision_with_X.
                is_colliding = False
                s1 = instance.sprite
                if s1 is None:
                    continue
                bw1 = s1.bbox_right - s1.bbox_left
                bh1 = s1.bbox_bottom - s1.bbox_top
                ix = instance.x - s1.origin_x + s1.bbox_left
                iy = instance.y - s1.origin_y + s1.bbox_top

                for other_instance in self.current_room.instances:
                    if other_instance == instance:
                        continue
                    if other_instance.object_name != target_object:
                        continue

                    s2 = other_instance.sprite
                    if s2 is None:
                        continue
                    bw2 = s2.bbox_right - s2.bbox_left
                    bh2 = s2.bbox_bottom - s2.bbox_top
                    ox = other_instance.x - s2.origin_x + s2.bbox_left
                    oy = other_instance.y - s2.origin_y + s2.bbox_top

                    if self.rectangles_overlap(ix, iy, bw1, bh1, ox, oy, bw2, bh2):
                        is_colliding = True
                        break

                # If NOT colliding, fire the event
                if not is_colliding:
                    actions = event_data.get('actions', [])
                    if actions:
                        logger.debug(f"🚫 NOT_COLLISION: {instance.object_name} not colliding with {target_object}")
                        instance.action_executor.execute_action_list(instance, actions)

    def _object_matches_target(self, object_name: str, target: str) -> bool:
        """Check if object_name matches target, considering parent inheritance."""
        if object_name == target:
            return True
        # Walk up the parent chain (max 10 levels to prevent cycles)
        objects_data = self._objects_data
        current = object_name
        for _ in range(10):
            obj_data = objects_data.get(current, {})
            parent = obj_data.get('parent', '')
            if not parent:
                return False
            if parent == target:
                return True
            current = parent
        return False

    def _resolve_collision_event(self, events: dict, other_instance) -> str:
        """Find the collision event in `events` that matches `other_instance`.

        Tries the other's current name, then walks its parent chain, then
        falls back to _original_object_name (set by change_instance). Returns
        the matching event name, or None if no event applies.
        """
        if not events:
            return None
        direct = f"collision_with_{other_instance.object_name}"
        if direct in events:
            return direct
        objects_data = self._objects_data
        current = other_instance.object_name
        for _ in range(10):
            parent = objects_data.get(current, {}).get('parent', '')
            if not parent:
                break
            candidate = f"collision_with_{parent}"
            if candidate in events:
                return candidate
            current = parent
        original = getattr(other_instance, '_original_object_name', None)
        if original and original != other_instance.object_name:
            alt = f"collision_with_{original}"
            if alt in events:
                return alt
        return None

    def instances_overlap(self, inst1, inst2) -> bool:
        """Check if two instances overlap using their sprite collision bboxes.

        The AABB step uses each sprite's collision bbox (sprite.bbox_left etc),
        not the full sprite size — so a 32x32 sprite of a character with
        transparent borders won't trigger collision while two grid cells apart.
        Precise refinement still uses the full sprite mask aligned at the
        AABB top-left, matching the previous semantics.
        """
        # Bbox dimensions and world top-left (origin- and bbox-adjusted)
        b1 = self._bbox_in_world(inst1)
        b2 = self._bbox_in_world(inst2)
        if b1 is None or b2 is None:
            return False
        bx1, by1, bw1, bh1 = b1
        bx2, by2, bw2, bh2 = b2

        if not self.rectangles_overlap(bx1, by1, bw1, bh1, bx2, by2, bw2, bh2):
            return False
        return self._precise_refine(inst1, bx1, by1, inst2, bx2, by2)

    @staticmethod
    def _bbox_in_world(instance):
        """Return (x, y, w, h) of the instance's collision bbox in world coords,
        or None if it has no sprite. World x/y is the bbox top-left after
        applying sprite origin and the sprite's bbox_left/top offsets."""
        s = instance.sprite
        if s is None:
            return None
        x = instance.x - s.origin_x + s.bbox_left
        y = instance.y - s.origin_y + s.bbox_top
        w = s.bbox_right - s.bbox_left
        h = s.bbox_bottom - s.bbox_top
        return (x, y, w, h)

    def rectangles_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        """Check if two rectangles overlap"""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    def _precise_refine(self, inst1, ax1, ay1, inst2, ax2, ay2) -> bool:
        """Post-AABB refinement for pixel-perfect collision.

        Returns True to keep an AABB-positive hit, False to reject it.
        Pixel-perfect is opt-in per sprite (sprite.precise). Static-only:
        rotated or scaled instances bypass the mask check, so the AABB
        result stands.

        ax1, ay1, ax2, ay2 are the AABB top-left positions actually used
        at the call site (already origin-adjusted). Identical coordinates
        to the rectangles_overlap that just returned True.
        """
        s1 = inst1.sprite if inst1 else None
        s2 = inst2.sprite if inst2 else None
        if not (s1 and s2):
            return True
        if not (getattr(s1, 'precise', False) or getattr(s2, 'precise', False)):
            return True
        if (getattr(inst1, 'rotation', 0) or getattr(inst2, 'rotation', 0)
                or getattr(inst1, 'image_angle', 0) or getattr(inst2, 'image_angle', 0)
                or getattr(inst1, 'scale_x', 1) != 1 or getattr(inst1, 'scale_y', 1) != 1
                or getattr(inst2, 'scale_x', 1) != 1 or getattr(inst2, 'scale_y', 1) != 1):
            return True
        m1 = s1.get_mask(inst1.image_index) if hasattr(s1, 'get_mask') else None
        m2 = s2.get_mask(inst2.image_index) if hasattr(s2, 'get_mask') else None
        if m1 is None or m2 is None:
            return True
        # The masks are FULL-FRAME (mask (0,0) == sprite frame top-left), but
        # ax/ay are the bbox top-left in world coords (origin + bbox offset).
        # Back out each sprite's bbox offset to align the masks at their frame
        # origins; using the bbox positions directly left the overlap offset
        # wrong by (bbox_left2 - bbox_left1, bbox_top2 - bbox_top1), producing
        # false hits/misses whenever two precise sprites had different bbox
        # offsets (it self-cancelled only when they happened to match).
        fx1 = ax1 - getattr(s1, 'bbox_left', 0)
        fy1 = ay1 - getattr(s1, 'bbox_top', 0)
        fx2 = ax2 - getattr(s2, 'bbox_left', 0)
        fy2 = ay2 - getattr(s2, 'bbox_top', 0)
        return m1.overlap(m2, (int(fx2 - fx1), int(fy2 - fy1))) is not None

    def check_collision_at_position(self, instance, check_x: float, check_y: float,
                                    object_type: str = "any", exclude_instance=None) -> bool:
        """Check if there's a collision at a given position

        Args:
            instance: The instance doing the check
            check_x: X position to check
            check_y: Y position to check
            object_type: Type of object to check for:
                - 'any': Only solid objects (non-solid don't block, collision events fire after move)
                - 'all': ANY overlapping instance, solid or not (GM place_empty /
                         "all objects"); used by check_empty's "all" option
                - 'solid': Only solid objects
                - specific name: Only that specific object type
            exclude_instance: Additional instance to exclude (e.g., collision other)

        Returns:
            True if collision found, False otherwise
        """
        if not self.current_room:
            logger.debug("⚠️ check_collision_at_position: No current room!")
            return False

        # Use cached dimensions
        w1 = instance._cached_width
        h1 = instance._cached_height

        # Use spatial grid for faster collision detection
        nearby_instances = self.current_room.get_nearby_instances(check_x, check_y, w1, h1)

        # Cache instance's collision targets for checking stop_movement
        instance_collision_targets = instance._collision_targets

        for other_instance in nearby_instances:
            if other_instance == instance:
                continue
            # Also exclude the collision "other" instance (e.g., explorer pushing rock)
            if exclude_instance and other_instance == exclude_instance:
                continue

            # Use sprite collision bboxes (smaller than full sprite when the
            # sprite has transparent borders or explicit bbox_* metadata)
            s1 = instance.sprite
            s2 = other_instance.sprite
            if s1 is None or s2 is None:
                continue
            bw1 = s1.bbox_right - s1.bbox_left
            bh1 = s1.bbox_bottom - s1.bbox_top
            bw2 = s2.bbox_right - s2.bbox_left
            bh2 = s2.bbox_bottom - s2.bbox_top
            # check_x/y is the candidate top-left of `instance`; the bbox
            # is offset within the sprite by origin + bbox_left/top.
            ix = check_x - s1.origin_x + s1.bbox_left
            iy = check_y - s1.origin_y + s1.bbox_top
            ox = other_instance.x - s2.origin_x + s2.bbox_left
            oy = other_instance.y - s2.origin_y + s2.bbox_top

            # Check if collision bboxes overlap
            if self.rectangles_overlap(ix, iy, bw1, bh1, ox, oy, bw2, bh2):
                # Pixel-perfect refinement (no-op unless either sprite opts in).
                if not self._precise_refine(
                        instance, ix, iy,
                        other_instance, ox, oy):
                    continue
                # "all": every overlapping instance occupies the position,
                # solid or not (GM "all objects" / place_empty). Solid-only
                # "any" ignores non-solid monsters, which let a pushed block
                # teleport over a monster in maze_3.
                if object_type == "all":
                    return True
                # Use cached object data for properties
                other_obj_data = other_instance._cached_object_data
                if not other_obj_data:
                    objects_data = self._objects_data
                    other_obj_data = objects_data.get(other_instance.object_name, {})

                is_solid = other_obj_data.get('solid', False)

                # Collision detected - check if it matches the filter
                if object_type == "any":
                    # Solid objects always block
                    if is_solid:
                        return True

                    # For non-solid objects, check if there's a collision event
                    # that has a "stop_movement" action using pre-parsed collision targets
                    target_name = other_instance.object_name
                    if target_name in instance_collision_targets:
                        # Check if the collision event has a stop_movement action
                        event_data = instance_collision_targets[target_name]
                        actions = event_data.get('actions', [])
                        for action in actions:
                            if action.get('action') == 'stop_movement':
                                return True
                        # Collision event exists but no stop_movement - continue checking other objects
                        continue
                    else:
                        # Also check if the OTHER object has a collision event with stop_movement
                        # using its pre-parsed collision targets
                        other_collision_targets = other_instance._collision_targets
                        if instance.object_name in other_collision_targets:
                            reverse_event_data = other_collision_targets[instance.object_name]
                            reverse_actions = reverse_event_data.get('actions', [])
                            for action in reverse_actions:
                                if action.get('action') == 'stop_movement':
                                    return True

                        # No blocking event for THIS object - continue checking other objects
                        continue

                elif object_type == "solid":
                    # "solid" means only solid objects
                    if is_solid:
                        return True
                else:
                    # Check for specific object type
                    if other_instance.object_name == object_type:
                        return True

        return False

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
