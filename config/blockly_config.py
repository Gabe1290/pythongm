#!/usr/bin/env python3
"""
Blockly Configuration System
Allows users to customize which blocks are available in the visual editor
"""

from dataclasses import dataclass, field
from typing import Set, Dict, List
from pathlib import Path
import json


# ============================================================================
# BLOCK REGISTRY
# ============================================================================

# All available block types organized by category
# Each block has: type, name, description, and implemented (True/False)
BLOCK_REGISTRY: Dict[str, List[Dict]] = {
    "Events": [
        {"type": "event_create", "name": "Create Event", "description": "When object is created", "implemented": True},
        {"type": "event_step", "name": "Step Event", "description": "Every frame", "implemented": True},
        {"type": "event_draw", "name": "Draw Event", "description": "During drawing phase", "implemented": True},
        {"type": "event_destroy", "name": "Destroy Event", "description": "When object is destroyed", "implemented": True},
        {"type": "event_keyboard_nokey", "name": "No Key", "description": "No key pressed", "implemented": True},
        {"type": "event_keyboard_anykey", "name": "Any Key", "description": "Any key pressed", "implemented": True},
        {"type": "event_keyboard_held", "name": "Keyboard (held)", "description": "Key held down", "implemented": True},
        {"type": "event_keyboard_press", "name": "Key Press", "description": "Key pressed once", "implemented": True},
        {"type": "event_keyboard_release", "name": "Key Release", "description": "Key released", "implemented": True},
        {"type": "event_mouse", "name": "Mouse Events", "description": "Mouse clicks and movement", "implemented": True},
        {"type": "event_collision", "name": "Collision", "description": "Collision with object", "implemented": True},
        {"type": "event_alarm", "name": "Alarm Events", "description": "Alarm triggers (0-11)", "implemented": True},
        {"type": "event_other", "name": "Other Events", "description": "No more lives, health, room events", "implemented": True},
    ],
    "Movement": [
        {"type": "move_set_hspeed", "name": "Set Horizontal Speed", "description": "Set X velocity", "implemented": True},
        {"type": "move_set_vspeed", "name": "Set Vertical Speed", "description": "Set Y velocity", "implemented": True},
        {"type": "move_stop", "name": "Stop Movement", "description": "Stop all movement", "implemented": True},
        {"type": "move_direction", "name": "Move Direction", "description": "Move in 4 directions", "implemented": True},
        {"type": "move_towards", "name": "Move Towards", "description": "Move to point", "implemented": False},
        {"type": "move_snap_to_grid", "name": "Snap to Grid", "description": "Align to grid", "implemented": True},
        {"type": "move_jump_to", "name": "Jump to Position", "description": "Instant teleport", "implemented": True},
        {"type": "grid_stop_if_no_keys", "name": "Stop if No Keys", "description": "Grid movement helper", "implemented": True},
        {"type": "grid_check_keys_and_move", "name": "Check Keys and Move", "description": "Grid movement helper", "implemented": True},
        {"type": "grid_if_on_grid", "name": "If On Grid", "description": "Grid-aligned check", "implemented": True},
        {"type": "set_gravity", "name": "Set Gravity", "description": "Apply gravity force", "implemented": True},
        {"type": "set_friction", "name": "Set Friction", "description": "Apply friction", "implemented": True},
        {"type": "reverse_horizontal", "name": "Reverse Horizontal", "description": "Flip X direction", "implemented": True},
        {"type": "reverse_vertical", "name": "Reverse Vertical", "description": "Flip Y direction", "implemented": True},
        {"type": "bounce", "name": "Bounce", "description": "Bounce off solid objects", "implemented": True},
        {"type": "wrap_around_room", "name": "Wrap Around Room", "description": "Wrap to opposite side", "implemented": True},
        {"type": "move_to_contact", "name": "Move to Contact", "description": "Move until touching", "implemented": False},
    ],
    "Timing": [
        {"type": "set_alarm", "name": "Set Alarm", "description": "Set timer (0-11)", "implemented": True},
    ],
    "Drawing": [
        {"type": "draw_text", "name": "Draw Text", "description": "Display text", "implemented": False},
        {"type": "draw_rectangle", "name": "Draw Rectangle", "description": "Draw filled rectangle", "implemented": False},
        {"type": "draw_circle", "name": "Draw Circle", "description": "Draw filled circle", "implemented": False},
        {"type": "set_sprite", "name": "Set Sprite", "description": "Change sprite image", "implemented": True},
        {"type": "set_alpha", "name": "Set Transparency", "description": "Set alpha (0-1)", "implemented": False},
    ],
    "Score/Lives/Health": [
        {"type": "score_set", "name": "Set Score", "description": "Set score value", "implemented": True},
        {"type": "score_add", "name": "Add to Score", "description": "Change score", "implemented": True},
        {"type": "lives_set", "name": "Set Lives", "description": "Set lives value", "implemented": True},
        {"type": "lives_add", "name": "Add to Lives", "description": "Change lives", "implemented": True},
        {"type": "health_set", "name": "Set Health", "description": "Set health value", "implemented": True},
        {"type": "health_add", "name": "Add to Health", "description": "Change health", "implemented": True},
        {"type": "draw_score", "name": "Draw Score", "description": "Display score text", "implemented": True},
        {"type": "draw_lives", "name": "Draw Lives", "description": "Display lives icons", "implemented": True},
        {"type": "draw_health_bar", "name": "Draw Health Bar", "description": "Display health bar", "implemented": True},
    ],
    "Instance": [
        {"type": "instance_destroy", "name": "Destroy Instance", "description": "Destroy this object", "implemented": True},
        {"type": "instance_destroy_other", "name": "Destroy Other", "description": "Destroy colliding object", "implemented": True},
        {"type": "instance_create", "name": "Create Instance", "description": "Spawn new object", "implemented": True},
    ],
    "Room": [
        {"type": "room_goto_next", "name": "Next Room", "description": "Go to next room", "implemented": True},
        {"type": "room_goto_previous", "name": "Previous Room", "description": "Go to previous room", "implemented": True},
        {"type": "room_restart", "name": "Restart Room", "description": "Restart current room", "implemented": True},
        {"type": "room_goto", "name": "Go to Room", "description": "Go to specific room", "implemented": False},
        {"type": "room_if_next_exists", "name": "If Next Room Exists", "description": "Check if next room exists", "implemented": True},
        {"type": "room_if_previous_exists", "name": "If Previous Room Exists", "description": "Check if previous room exists", "implemented": True},
    ],
    "Values": [
        {"type": "value_x", "name": "X Position", "description": "Get X coordinate", "implemented": True},
        {"type": "value_y", "name": "Y Position", "description": "Get Y coordinate", "implemented": True},
        {"type": "value_hspeed", "name": "Horizontal Speed", "description": "Get X velocity", "implemented": True},
        {"type": "value_vspeed", "name": "Vertical Speed", "description": "Get Y velocity", "implemented": True},
        {"type": "value_score", "name": "Score", "description": "Get score value", "implemented": True},
        {"type": "value_lives", "name": "Lives", "description": "Get lives value", "implemented": True},
        {"type": "value_health", "name": "Health", "description": "Get health value", "implemented": True},
        {"type": "value_mouse_x", "name": "Mouse X", "description": "Get mouse X", "implemented": True},
        {"type": "value_mouse_y", "name": "Mouse Y", "description": "Get mouse Y", "implemented": True},
    ],
    "Sound": [
        {"type": "sound_play", "name": "Play Sound", "description": "Play sound effect", "implemented": True},
        {"type": "music_play", "name": "Play Music", "description": "Play background music", "implemented": True},
        {"type": "music_stop", "name": "Stop Music", "description": "Stop music", "implemented": True},
    ],
    "Output": [
        {"type": "output_message", "name": "Show Message", "description": "Display message dialog", "implemented": True},
    ],
    "Game": [
        {"type": "game_end", "name": "End Game", "description": "Close the game", "implemented": True},
        {"type": "game_restart", "name": "Restart Game", "description": "Restart from first room", "implemented": True},
        {"type": "show_highscore", "name": "Show Highscore", "description": "Display highscore table", "implemented": True},
        {"type": "clear_highscore", "name": "Clear Highscore", "description": "Reset highscore table", "implemented": True},
    ],
}


def get_implemented_blocks() -> Set[str]:
    """Get set of all implemented block types"""
    implemented = set()
    for blocks in BLOCK_REGISTRY.values():
        for block in blocks:
            if block.get("implemented", True):
                implemented.add(block["type"])
    return implemented


def is_block_implemented(block_type: str) -> bool:
    """Check if a specific block is implemented"""
    for blocks in BLOCK_REGISTRY.values():
        for block in blocks:
            if block["type"] == block_type:
                return block.get("implemented", True)
    return True  # Default to True if not found

# Block dependencies - some blocks require others
BLOCK_DEPENDENCIES: Dict[str, List[str]] = {
    "event_alarm": ["set_alarm"],
    "draw_score": ["score_set", "score_add"],
    "draw_lives": ["lives_set", "lives_add"],
    "draw_health_bar": ["health_set", "health_add"],
    "grid_stop_if_no_keys": ["grid_check_keys_and_move", "grid_if_on_grid"],
    "grid_check_keys_and_move": ["grid_stop_if_no_keys", "grid_if_on_grid"],
}


# ============================================================================
# CONFIGURATION DATA CLASS
# ============================================================================

@dataclass
class BlocklyConfig:
    """Configuration for which blocks are enabled in Blockly"""

    enabled_blocks: Set[str] = field(default_factory=set)
    enabled_categories: Set[str] = field(default_factory=set)
    preset_name: str = "full"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "enabled_blocks": list(self.enabled_blocks),
            "enabled_categories": list(self.enabled_categories),
            "preset_name": self.preset_name
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BlocklyConfig':
        """Create from dictionary"""
        return cls(
            enabled_blocks=set(data.get("enabled_blocks", [])),
            enabled_categories=set(data.get("enabled_categories", [])),
            preset_name=data.get("preset_name", "full")
        )

    def is_block_enabled(self, block_type: str) -> bool:
        """Check if a block is enabled"""
        return block_type in self.enabled_blocks

    def is_category_enabled(self, category: str) -> bool:
        """Check if a category is enabled"""
        return category in self.enabled_categories

    def enable_block(self, block_type: str):
        """Enable a specific block"""
        self.enabled_blocks.add(block_type)

    def disable_block(self, block_type: str):
        """Disable a specific block"""
        self.enabled_blocks.discard(block_type)

    def enable_category(self, category: str):
        """Enable all blocks in a category"""
        self.enabled_categories.add(category)
        if category in BLOCK_REGISTRY:
            for block in BLOCK_REGISTRY[category]:
                self.enabled_blocks.add(block["type"])

    def disable_category(self, category: str):
        """Disable all blocks in a category"""
        self.enabled_categories.discard(category)
        if category in BLOCK_REGISTRY:
            for block in BLOCK_REGISTRY[category]:
                self.enabled_blocks.discard(block["type"])

    def get_missing_dependencies(self) -> Dict[str, List[str]]:
        """Find blocks with missing dependencies"""
        missing = {}
        for block_type in self.enabled_blocks:
            if block_type in BLOCK_DEPENDENCIES:
                deps = BLOCK_DEPENDENCIES[block_type]
                missing_deps = [dep for dep in deps if dep not in self.enabled_blocks]
                if missing_deps:
                    missing[block_type] = missing_deps
        return missing

    # ========================================================================
    # PRESETS
    # ========================================================================

    @classmethod
    def get_full(cls) -> 'BlocklyConfig':
        """Full feature set - all blocks enabled"""
        config = cls(preset_name="full")
        for category, blocks in BLOCK_REGISTRY.items():
            config.enable_category(category)
        return config

    @classmethod
    def get_beginner(cls) -> 'BlocklyConfig':
        """Simplified for beginners - basic blocks only"""
        config = cls(preset_name="beginner")

        # Essential events
        config.enable_block("event_create")
        config.enable_block("event_step")
        config.enable_block("event_keyboard_press")
        config.enable_block("event_collision")

        # Basic movement
        config.enable_block("move_set_hspeed")
        config.enable_block("move_set_vspeed")
        config.enable_block("move_stop")
        config.enable_block("move_jump_to")

        # Basic instance
        config.enable_block("instance_destroy")
        config.enable_block("instance_create")

        # Score
        config.enable_block("score_set")
        config.enable_block("score_add")
        config.enable_block("draw_score")

        # Room
        config.enable_block("room_goto_next")
        config.enable_block("room_goto_previous")
        config.enable_block("room_restart")
        config.enable_block("room_goto")
        config.enable_block("room_if_next_exists")
        config.enable_block("room_if_previous_exists")

        # Output
        config.enable_block("output_message")

        # Enable categories that have blocks
        config.enabled_categories = {"Events", "Movement", "Score/Lives/Health", "Instance", "Room", "Output"}

        return config

    @classmethod
    def get_intermediate(cls) -> 'BlocklyConfig':
        """Intermediate - adds more features"""
        config = cls.get_beginner()
        config.preset_name = "intermediate"

        # More events
        config.enable_block("event_draw")
        config.enable_block("event_destroy")
        config.enable_block("event_mouse")
        config.enable_block("event_alarm")

        # More movement
        config.enable_block("move_direction")
        config.enable_block("move_towards")

        # Timing
        config.enable_block("set_alarm")

        # Score
        config.enable_block("score_set")

        # Lives and health
        config.enable_block("lives_set")
        config.enable_block("lives_add")
        config.enable_block("draw_lives")
        config.enable_block("health_set")
        config.enable_block("health_add")
        config.enable_block("draw_health_bar")

        # Sound
        config.enable_block("sound_play")
        config.enable_block("music_play")
        config.enable_block("music_stop")

        # Room
        config.enable_block("room_goto_next")
        config.enable_block("room_restart")

        config.enabled_categories.update({"Timing", "Sound", "Room"})

        return config

    @classmethod
    def get_platformer(cls) -> 'BlocklyConfig':
        """Platformer game preset"""
        config = cls(preset_name="platformer")

        # Events
        config.enable_block("event_create")
        config.enable_block("event_step")
        config.enable_block("event_keyboard_press")
        config.enable_block("event_keyboard_held")
        config.enable_block("event_collision")
        config.enable_block("event_destroy")

        # Movement with physics
        config.enable_block("move_set_hspeed")
        config.enable_block("move_set_vspeed")
        config.enable_block("move_stop")
        config.enable_block("set_gravity")
        config.enable_block("set_friction")
        config.enable_block("reverse_horizontal")

        # Instance
        config.enable_block("instance_destroy")
        config.enable_block("instance_create")

        # Score/Lives
        config.enable_block("score_set")
        config.enable_block("score_add")
        config.enable_block("draw_score")
        config.enable_block("lives_set")
        config.enable_block("lives_add")
        config.enable_block("draw_lives")

        # Room
        config.enable_block("room_goto_next")
        config.enable_block("room_restart")

        # Sound
        config.enable_block("sound_play")
        config.enable_block("music_play")

        config.enabled_categories = {"Events", "Movement", "Score/Lives/Health", "Instance", "Room", "Sound"}

        return config

    @classmethod
    def get_grid_rpg(cls) -> 'BlocklyConfig':
        """Grid-based RPG/puzzle game preset"""
        config = cls(preset_name="grid_rpg")

        # Events
        config.enable_block("event_create")
        config.enable_block("event_step")
        config.enable_block("event_keyboard_press")
        config.enable_block("event_collision")

        # Grid movement
        config.enable_block("move_snap_to_grid")
        config.enable_block("move_jump_to")
        config.enable_block("grid_stop_if_no_keys")
        config.enable_block("grid_check_keys_and_move")
        config.enable_block("grid_if_on_grid")

        # Instance
        config.enable_block("instance_destroy")
        config.enable_block("instance_create")

        # Health system
        config.enable_block("health_set")
        config.enable_block("health_add")
        config.enable_block("draw_health_bar")

        # Room
        config.enable_block("room_goto_next")
        config.enable_block("room_goto")

        # Output
        config.enable_block("output_message")

        # Sound
        config.enable_block("sound_play")
        config.enable_block("music_play")

        config.enabled_categories = {"Events", "Movement", "Score/Lives/Health", "Instance", "Room", "Output", "Sound"}

        return config

    @classmethod
    def get_sokoban(cls) -> 'BlocklyConfig':
        """Sokoban/box-pushing puzzle game preset"""
        config = cls(preset_name="sokoban")

        # Events - essential for Sokoban
        config.enable_block("event_create")
        config.enable_block("event_keyboard_held")  # Arrow keys for movement
        config.enable_block("event_keyboard_nokey")  # Stop when no key pressed
        config.enable_block("event_collision")  # Push boxes, hit walls

        # Movement - grid-based movement is essential
        config.enable_block("move_set_hspeed")
        config.enable_block("move_set_vspeed")
        config.enable_block("move_stop")
        config.enable_block("move_snap_to_grid")
        config.enable_block("move_jump_to")  # For pushing boxes
        config.enable_block("grid_if_on_grid")  # Only move when aligned

        # Instance - for changing box types
        config.enable_block("instance_destroy")
        config.enable_block("instance_create")

        # Room - level progression
        config.enable_block("room_goto_next")
        config.enable_block("room_goto_previous")
        config.enable_block("room_restart")
        config.enable_block("room_if_next_exists")

        # Lives - optional but useful for Sokoban
        config.enable_block("lives_set")
        config.enable_block("lives_add")

        # Output - for win messages
        config.enable_block("output_message")

        config.enabled_categories = {"Events", "Movement", "Instance", "Room", "Score/Lives/Health", "Output"}

        return config

    @classmethod
    def get_testing(cls) -> 'BlocklyConfig':
        """Testing preset - only includes validated events and actions.

        This preset is organized by game type phases:
        - Phase 1: Sokoban-like (grid puzzles)
        - Phase 2: Labyrinth/Rogue-like (maze exploration)
        - Phase 3: Platform (side-scrolling)
        - Phase 4: Scrolling shooter
        - Phase 5: Racing
        - Phase 6: Zelda-like RPG

        Enable blocks here only after they pass testing.
        See docs/TESTING_CHECKLIST.md for the full testing plan.
        """
        config = cls(preset_name="testing")

        # =====================================================================
        # PHASE 1: Sokoban-like Games (Grid-based puzzles)
        # =====================================================================

        # Phase 1 Events
        config.enable_block("event_create")
        config.enable_block("event_keyboard_held")
        config.enable_block("event_keyboard_nokey")
        config.enable_block("event_collision")
        config.enable_block("event_step")

        # Phase 1 Movement
        config.enable_block("move_set_hspeed")
        config.enable_block("move_set_vspeed")
        config.enable_block("move_stop")
        config.enable_block("move_snap_to_grid")
        config.enable_block("move_jump_to")
        config.enable_block("grid_if_on_grid")

        # Phase 1 Instance
        config.enable_block("instance_destroy")
        config.enable_block("instance_create")

        # Phase 1 Room
        config.enable_block("room_goto_next")
        config.enable_block("room_goto_previous")
        config.enable_block("room_restart")
        config.enable_block("room_if_next_exists")
        config.enable_block("room_if_previous_exists")

        # =====================================================================
        # PHASE 2: Labyrinth/Rogue-like Games
        # Uncomment blocks below after Phase 1 testing is complete
        # =====================================================================

        # Phase 2 Events
        # config.enable_block("event_keyboard_press")
        # config.enable_block("event_destroy")
        # config.enable_block("event_alarm")

        # Phase 2 Movement
        # config.enable_block("move_direction")
        # config.enable_block("move_towards")
        # config.enable_block("grid_stop_if_no_keys")
        # config.enable_block("grid_check_keys_and_move")

        # Phase 2 Timing
        # config.enable_block("set_alarm")

        # Phase 2 Score/Lives/Health
        # config.enable_block("health_set")
        # config.enable_block("health_add")
        # config.enable_block("draw_health_bar")
        # config.enable_block("lives_set")
        # config.enable_block("lives_add")

        # Phase 2 Sound
        # config.enable_block("sound_play")
        # config.enable_block("music_play")
        # config.enable_block("music_stop")

        # =====================================================================
        # PHASE 3: Platform Games
        # Uncomment blocks below after Phase 2 testing is complete
        # =====================================================================

        # Phase 3 Events
        # config.enable_block("event_keyboard_release")

        # Phase 3 Movement
        # config.enable_block("set_gravity")
        # config.enable_block("set_friction")
        # config.enable_block("reverse_horizontal")
        # config.enable_block("reverse_vertical")

        # Phase 3 Score
        # config.enable_block("score_set")
        # config.enable_block("score_add")
        # config.enable_block("draw_score")
        # config.enable_block("draw_lives")

        # Phase 3 Appearance
        # config.enable_block("set_sprite")
        # config.enable_block("set_alpha")

        # =====================================================================
        # PHASE 4: Scrolling Shooter Games
        # Uncomment blocks below after Phase 3 testing is complete
        # =====================================================================

        # (Additional blocks for Phase 4+)

        # =====================================================================
        # PHASE 5: Racing Games
        # Uncomment blocks below after Phase 4 testing is complete
        # =====================================================================

        # (Additional blocks for Phase 5+)

        # =====================================================================
        # PHASE 6: Zelda-like RPG
        # Uncomment blocks below after Phase 5 testing is complete
        # =====================================================================

        # Phase 6 Events
        # config.enable_block("event_draw")
        # config.enable_block("event_mouse")

        # Output (useful for testing)
        config.enable_block("output_message")

        config.enabled_categories = {"Events", "Movement", "Instance", "Room", "Output"}

        return config

    @classmethod
    def get_implemented_only(cls) -> 'BlocklyConfig':
        """Implemented Only preset - only includes blocks that are fully implemented.

        This preset automatically enables all blocks marked as implemented=True
        and excludes any blocks marked as implemented=False in the BLOCK_REGISTRY.
        """
        config = cls(preset_name="implemented_only")

        implemented_blocks = get_implemented_blocks()

        # Enable all implemented blocks and track categories
        for category, blocks in BLOCK_REGISTRY.items():
            category_has_blocks = False
            for block in blocks:
                if block["type"] in implemented_blocks:
                    config.enable_block(block["type"])
                    category_has_blocks = True
            if category_has_blocks:
                config.enabled_categories.add(category)

        return config


# ============================================================================
# PRESET REGISTRY
# ============================================================================

PRESETS: Dict[str, BlocklyConfig] = {
    "full": BlocklyConfig.get_full(),
    "beginner": BlocklyConfig.get_beginner(),
    "intermediate": BlocklyConfig.get_intermediate(),
    "platformer": BlocklyConfig.get_platformer(),
    "grid_rpg": BlocklyConfig.get_grid_rpg(),
    "sokoban": BlocklyConfig.get_sokoban(),
    "testing": BlocklyConfig.get_testing(),
    "implemented_only": BlocklyConfig.get_implemented_only(),
}


# ============================================================================
# PERSISTENCE
# ============================================================================

def get_config_path() -> Path:
    """Get path to configuration file"""
    config_dir = Path.home() / ".config" / "pygamemaker"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "blockly_config.json"


def save_config(config: BlocklyConfig):
    """Save configuration to file"""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)


def load_config() -> BlocklyConfig:
    """Load configuration from file, or return default"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path) as f:
                data = json.load(f)
                config = BlocklyConfig.from_dict(data)

                # Migrate: If using "full" preset, ensure all new blocks and categories are enabled
                # This handles the case where new blocks/categories were added after config was saved
                if config.preset_name == "full":
                    needs_save = False

                    all_blocks = get_all_block_types()
                    new_blocks = all_blocks - config.enabled_blocks
                    if new_blocks:
                        print(f"Blockly config migration: Adding {len(new_blocks)} new blocks to full preset: {new_blocks}")
                        for block in new_blocks:
                            config.enabled_blocks.add(block)
                        needs_save = True

                    # Also ensure all categories are enabled
                    all_categories = set(BLOCK_REGISTRY.keys())
                    new_categories = all_categories - config.enabled_categories
                    if new_categories:
                        print(f"Blockly config migration: Adding {len(new_categories)} new categories: {new_categories}")
                        for category in new_categories:
                            config.enabled_categories.add(category)
                        needs_save = True

                    # Save the migrated config so it persists
                    if needs_save:
                        save_config(config)
                        print("Blockly config migration: Saved updated configuration")

                return config
        except Exception as e:
            print(f"Error loading Blockly config: {e}")

    # Return full config by default
    return BlocklyConfig.get_full()


def get_all_block_types() -> Set[str]:
    """Get set of all available block types"""
    all_blocks = set()
    for blocks in BLOCK_REGISTRY.values():
        for block in blocks:
            all_blocks.add(block["type"])
    return all_blocks
