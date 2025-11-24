#!/usr/bin/env python3
"""
Blockly Configuration System
Allows users to customize which blocks are available in the visual editor
"""

from dataclasses import dataclass, field, asdict
from typing import Set, Dict, List, Optional
from pathlib import Path
import json


# ============================================================================
# BLOCK REGISTRY
# ============================================================================

# All available block types organized by category
BLOCK_REGISTRY: Dict[str, List[Dict[str, str]]] = {
    "Events": [
        {"type": "event_create", "name": "Create Event", "description": "When object is created"},
        {"type": "event_step", "name": "Step Event", "description": "Every frame"},
        {"type": "event_draw", "name": "Draw Event", "description": "During drawing phase"},
        {"type": "event_destroy", "name": "Destroy Event", "description": "When object is destroyed"},
        {"type": "event_keyboard_nokey", "name": "No Key", "description": "No key pressed"},
        {"type": "event_keyboard_anykey", "name": "Any Key", "description": "Any key pressed"},
        {"type": "event_keyboard_held", "name": "Keyboard (held)", "description": "Key held down"},
        {"type": "event_keyboard_press", "name": "Key Press", "description": "Key pressed once"},
        {"type": "event_keyboard_release", "name": "Key Release", "description": "Key released"},
        {"type": "event_mouse", "name": "Mouse Events", "description": "Mouse clicks and movement"},
        {"type": "event_collision", "name": "Collision", "description": "Collision with object"},
        {"type": "event_alarm", "name": "Alarm Events", "description": "Alarm triggers (0-11)"},
    ],
    "Movement": [
        {"type": "move_set_hspeed", "name": "Set Horizontal Speed", "description": "Set X velocity"},
        {"type": "move_set_vspeed", "name": "Set Vertical Speed", "description": "Set Y velocity"},
        {"type": "move_stop", "name": "Stop Movement", "description": "Stop all movement"},
        {"type": "move_direction", "name": "Move Direction", "description": "Move in 4 directions"},
        {"type": "move_towards", "name": "Move Towards", "description": "Move to point"},
        {"type": "move_snap_to_grid", "name": "Snap to Grid", "description": "Align to grid"},
        {"type": "move_jump_to", "name": "Jump to Position", "description": "Instant teleport"},
        {"type": "grid_stop_if_no_keys", "name": "Stop if No Keys", "description": "Grid movement helper"},
        {"type": "grid_check_keys_and_move", "name": "Check Keys and Move", "description": "Grid movement helper"},
        {"type": "grid_if_on_grid", "name": "If On Grid", "description": "Grid-aligned check"},
        {"type": "set_gravity", "name": "Set Gravity", "description": "Apply gravity force"},
        {"type": "set_friction", "name": "Set Friction", "description": "Apply friction"},
        {"type": "reverse_horizontal", "name": "Reverse Horizontal", "description": "Flip X direction"},
        {"type": "reverse_vertical", "name": "Reverse Vertical", "description": "Flip Y direction"},
    ],
    "Timing": [
        {"type": "set_alarm", "name": "Set Alarm", "description": "Set timer (0-11)"},
    ],
    "Drawing": [
        {"type": "draw_text", "name": "Draw Text", "description": "Display text"},
        {"type": "draw_rectangle", "name": "Draw Rectangle", "description": "Draw filled rectangle"},
        {"type": "draw_circle", "name": "Draw Circle", "description": "Draw filled circle"},
        {"type": "set_sprite", "name": "Set Sprite", "description": "Change sprite image"},
        {"type": "set_alpha", "name": "Set Transparency", "description": "Set alpha (0-1)"},
    ],
    "Score/Lives/Health": [
        {"type": "score_set", "name": "Set Score", "description": "Set score value"},
        {"type": "score_add", "name": "Add to Score", "description": "Change score"},
        {"type": "lives_set", "name": "Set Lives", "description": "Set lives value"},
        {"type": "lives_add", "name": "Add to Lives", "description": "Change lives"},
        {"type": "health_set", "name": "Set Health", "description": "Set health value"},
        {"type": "health_add", "name": "Add to Health", "description": "Change health"},
        {"type": "draw_score", "name": "Draw Score", "description": "Display score text"},
        {"type": "draw_lives", "name": "Draw Lives", "description": "Display lives icons"},
        {"type": "draw_health_bar", "name": "Draw Health Bar", "description": "Display health bar"},
    ],
    "Instance": [
        {"type": "instance_destroy", "name": "Destroy Instance", "description": "Destroy this object"},
        {"type": "instance_destroy_other", "name": "Destroy Other", "description": "Destroy colliding object"},
        {"type": "instance_create", "name": "Create Instance", "description": "Spawn new object"},
    ],
    "Room": [
        {"type": "room_goto_next", "name": "Next Room", "description": "Go to next room"},
        {"type": "room_restart", "name": "Restart Room", "description": "Restart current room"},
        {"type": "room_goto", "name": "Go to Room", "description": "Go to specific room"},
    ],
    "Values": [
        {"type": "value_x", "name": "X Position", "description": "Get X coordinate"},
        {"type": "value_y", "name": "Y Position", "description": "Get Y coordinate"},
        {"type": "value_hspeed", "name": "Horizontal Speed", "description": "Get X velocity"},
        {"type": "value_vspeed", "name": "Vertical Speed", "description": "Get Y velocity"},
        {"type": "value_score", "name": "Score", "description": "Get score value"},
        {"type": "value_lives", "name": "Lives", "description": "Get lives value"},
        {"type": "value_health", "name": "Health", "description": "Get health value"},
        {"type": "value_mouse_x", "name": "Mouse X", "description": "Get mouse X"},
        {"type": "value_mouse_y", "name": "Mouse Y", "description": "Get mouse Y"},
    ],
    "Sound": [
        {"type": "sound_play", "name": "Play Sound", "description": "Play sound effect"},
        {"type": "music_play", "name": "Play Music", "description": "Play background music"},
        {"type": "music_stop", "name": "Stop Music", "description": "Stop music"},
    ],
    "Output": [
        {"type": "output_message", "name": "Show Message", "description": "Display message dialog"},
    ],
}

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

        # Output
        config.enable_block("output_message")

        # Enable categories that have blocks
        config.enabled_categories = {"Events", "Movement", "Score/Lives/Health", "Instance", "Output"}

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


# ============================================================================
# PRESET REGISTRY
# ============================================================================

PRESETS: Dict[str, BlocklyConfig] = {
    "full": BlocklyConfig.get_full(),
    "beginner": BlocklyConfig.get_beginner(),
    "intermediate": BlocklyConfig.get_intermediate(),
    "platformer": BlocklyConfig.get_platformer(),
    "grid_rpg": BlocklyConfig.get_grid_rpg(),
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
                return BlocklyConfig.from_dict(data)
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
