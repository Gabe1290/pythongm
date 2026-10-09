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
    "Control": [
        {"type": "if_condition", "name": "If Condition", "description": "Run actions only when a condition holds (e.g. instance_count == 0)", "implemented": True},
        {"type": "set_variable", "name": "Set Variable", "description": "Assign a value to a custom variable on the instance or globally", "implemented": True},
        {"type": "test_variable", "name": "Test Variable", "description": "Compare a variable against a value and run nested actions when true", "implemented": True},
        {"type": "test_expression", "name": "If Condition (Logic)", "description": "Run nested actions when a condition built from Logic blocks (compare, and/or, not) is true", "implemented": True},
        {"type": "check_empty", "name": "Check Empty", "description": "True when (x, y) has no collision — gate following action(s) on grid movement", "implemented": True},
        {"type": "exit_event", "name": "Exit Event", "description": "Stop running the rest of this event's actions — typically paired with a test to commit on the first branch that succeeds", "implemented": True},
        {"type": "else_action", "name": "Else", "description": "Runs the next action only when the preceding test was false — pair with start_block/end_block to put more than one action on the else side", "implemented": True},
        {"type": "start_block", "name": "Start Block", "description": "Group multiple actions so a preceding conditional applies to all of them, not just the next one", "implemented": True},
        {"type": "end_block", "name": "End Block", "description": "Closes a Start Block group", "implemented": True},
    ],
    "Movement": [
        {"type": "move_set_hspeed", "name": "Set Horizontal Speed", "description": "Set X velocity", "implemented": True},
        {"type": "move_set_vspeed", "name": "Set Vertical Speed", "description": "Set Y velocity", "implemented": True},
        {"type": "move_stop", "name": "Stop Movement", "description": "Stop all movement", "implemented": True},
        {"type": "move_direction", "name": "Move Direction", "description": "Move in 4 directions", "implemented": True},
        {"type": "move_free", "name": "Move Free", "description": "Move at an arbitrary direction angle and speed", "implemented": True},
        {"type": "set_speed", "name": "Set Speed", "description": "Set speed magnitude (preserves direction)", "implemented": True},
        {"type": "set_direction", "name": "Set Direction", "description": "Set direction angle (preserves speed)", "implemented": True},
        {"type": "move_towards", "name": "Move Towards", "description": "Move to point", "implemented": True},
        {"type": "move_snap_to_grid", "name": "Snap to Grid", "description": "Align to grid", "implemented": True},
        {"type": "move_jump_to", "name": "Jump to Position", "description": "Instant teleport", "implemented": True},
        {"type": "grid_move", "name": "Move Grid", "description": "Move one grid unit in a direction", "implemented": True},
        {"type": "grid_stop_if_no_keys", "name": "Stop if No Keys", "description": "Grid movement helper", "implemented": True},
        {"type": "grid_check_keys_and_move", "name": "Check Keys and Move", "description": "Grid movement helper", "implemented": True},
        {"type": "grid_if_on_grid", "name": "If On Grid", "description": "Grid-aligned check", "implemented": True},
        {"type": "set_gravity", "name": "Set Gravity", "description": "Apply gravity force", "implemented": True},
        {"type": "set_friction", "name": "Set Friction", "description": "Apply friction", "implemented": True},
        {"type": "reverse_horizontal", "name": "Reverse Horizontal", "description": "Flip X direction", "implemented": True},
        {"type": "reverse_vertical", "name": "Reverse Vertical", "description": "Flip Y direction", "implemented": True},
        {"type": "bounce", "name": "Bounce", "description": "Bounce off solid objects", "implemented": True},
        {"type": "wrap_around_room", "name": "Wrap Around Room", "description": "Wrap to opposite side", "implemented": True},
        {"type": "move_to_contact", "name": "Move to Contact", "description": "Move until touching", "implemented": True},
    ],
    "Timing": [
        {"type": "set_alarm", "name": "Set Alarm", "description": "Set timer (0-11)", "implemented": True},
    ],
    "Drawing": [
        {"type": "draw_text", "name": "Draw Text", "description": "Display text", "implemented": True},
        {"type": "draw_rectangle", "name": "Draw Rectangle", "description": "Draw filled rectangle", "implemented": True},
        {"type": "draw_circle", "name": "Draw Circle", "description": "Draw filled circle", "implemented": True},
        {"type": "set_sprite", "name": "Set Sprite", "description": "Change sprite image", "implemented": True},
        {"type": "set_alpha", "name": "Set Transparency", "description": "Set alpha (0-1)", "implemented": True},
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
        {"type": "instance_change", "name": "Change Instance", "description": "Transform into different object type", "implemented": True},
        {"type": "if_can_push", "name": "If Can Push", "description": "Sokoban-style push check", "implemented": True},
    ],
    "Room": [
        {"type": "room_goto_next", "name": "Next Room", "description": "Go to next room", "implemented": True},
        {"type": "room_goto_previous", "name": "Previous Room", "description": "Go to previous room", "implemented": True},
        {"type": "room_restart", "name": "Restart Room", "description": "Restart current room", "implemented": True},
        {"type": "room_goto", "name": "Go to Room", "description": "Go to specific room", "implemented": True},
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
        {"type": "execute_code", "name": "Execute Code", "description": "Execute custom Python code", "implemented": True},
    ],
    "Game": [
        {"type": "game_end", "name": "End Game", "description": "Close the game", "implemented": True},
        {"type": "game_restart", "name": "Restart Game", "description": "Restart from first room", "implemented": True},
        {"type": "show_highscore", "name": "Show Highscore", "description": "Display highscore table", "implemented": True},
        {"type": "clear_highscore", "name": "Clear Highscore", "description": "Reset highscore table", "implemented": True},
    ],
}
# The 8 "Thymio *" categories moved to extensions/thymio/blockly_categories.py
# (docs/THYMIO_EXTENSION_PLAN.md, Stage F) -- merged back into BLOCK_REGISTRY
# at extension-load time via register_block_categories().


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
# GENERATED ACTION NAMES (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2)
# ============================================================================
# Every core (non-extension, non-Audio) action that has no hand-written
# Blockly block -- editors/object_editor/blockly/blockly_workspace.html's
# `registerCustomBlocks` builds its Blockly block for these automatically,
# instead of the literal <block type="..."> XML every BLOCK_REGISTRY entry
# above corresponds to. Until this unit, these names appeared in NO preset's
# enabled_blocks at all (the bug docs/BLOCKLY_TOOLBOX_GATING_PLAN.md fixes),
# so every preset effectively showed every one of them regardless of what it
# actually declared. Grouped by ActionType.category for readability; the
# grouping has no functional meaning (every preset below that wants "all of
# them" just takes the whole set).
#
# Keep this in sync with the JS hardcoded block types in
# blockly_workspace.html's `categories` object --
# tests/test_toolbox_visibility.py's drift-detection test re-extracts that
# set and fails loudly if this list and the JS disagree.
GENERATED_ACTION_NAMES: frozenset = frozenset({
    # Control
    "check_empty", "comment", "else_action", "end_block", "execute_code",
    "execute_script", "if_collision", "if_collision_at", "if_object_exists",
    "repeat", "start_block", "test_chance", "test_question",
    # Game
    "draw_arrow", "draw_background", "draw_ellipse", "draw_line",
    "draw_scaled_text", "draw_sprite", "draw_variable", "fill_color",
    "load_game", "open_webpage", "restart_game", "save_game", "set_color",
    "set_draw_color", "set_draw_font", "set_window_caption", "show_info",
    "show_video", "splash_show_image", "splash_show_text",
    # Grid
    "test_alignment",
    # Instance
    "change_instance", "create_moving_instance", "create_random_instance",
    "destroy_at_position", "set_image_index", "set_image_speed",
    "start_animation", "stop_animation", "test_instance_count",
    # Movement
    "bounce", "jump_to_random", "jump_to_start", "move_grid",
    "move_to_contact", "move_towards_point", "set_direction_speed",
    "start_moving_direction",
    # Particles
    "burst_particles", "clear_particles", "create_emitter",
    "create_particle_system", "create_particle_type", "destroy_emitter",
    "destroy_particle_system", "stream_particles",
    # Room
    "check_room", "game_end", "set_background", "set_background_color",
    "set_room_caption", "set_room_persistent", "set_room_speed",
    # Score
    "clear_highscore", "show_highscore", "test_health", "test_lives",
    "test_score",
    # Timing
    "pause_timeline", "set_timeline", "set_timeline_position",
    "set_timeline_speed", "sleep", "start_timeline", "stop_timeline",
    # Views
    "enable_views", "set_view",
})


# ============================================================================
# CONFIGURATION DATA CLASS
# ============================================================================


# Actions that used to be in GENERATED_ACTION_NAMES and now have a
# hand-written block (listed in BLOCK_REGISTRY instead). Every place that
# enables "all generated actions" also enables these, so a preset or migrated
# config keeps showing them exactly as before the block was written.
# test_expression: docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B6c.
PROMOTED_TO_HAND_WRITTEN_BLOCKS: frozenset = frozenset({"test_expression"})

@dataclass
class BlocklyConfig:
    """Configuration for which blocks are enabled in Blockly"""

    enabled_blocks: Set[str] = field(default_factory=set)
    enabled_categories: Set[str] = field(default_factory=set)
    preset_name: str = "full"
    # Bumped to 2 when GENERATED_ACTION_NAMES (Unit 2) was added, so
    # load_config() can tell a config saved before that change apart from
    # one built fresh by current code (which already includes them) and
    # migrate it exactly once. A config built directly by this module's own
    # code (every get_*() preset, any fresh custom config) is current by
    # construction, hence the default of 2, not 1.
    config_version: int = 2

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "enabled_blocks": list(self.enabled_blocks),
            "enabled_categories": list(self.enabled_categories),
            "preset_name": self.preset_name,
            "config_version": self.config_version,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BlocklyConfig':
        """Create from dictionary"""
        return cls(
            enabled_blocks=set(data.get("enabled_blocks", [])),
            enabled_categories=set(data.get("enabled_categories", [])),
            preset_name=data.get("preset_name", "full"),
            # A file saved before config_version existed has no such key --
            # that absence IS the "needs migrating" signal (see load_config).
            config_version=data.get("config_version", 1),
        )

    def is_block_enabled(self, block_type: str) -> bool:
        """Check if a block is enabled"""
        return block_type in self.enabled_blocks


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
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)
        return config

    @classmethod
    def get_beginner(cls) -> 'BlocklyConfig':
        """Beginner preset — covers Getting Started, First Game, Pong, Breakout tutorials"""
        config = cls(preset_name="beginner")

        # Events needed by beginner tutorials
        config.enable_block("event_create")       # First Game, Pong, Breakout
        config.enable_block("event_step")          # First Game
        config.enable_block("event_draw")          # First Game, Pong, Breakout (score/lives display)
        config.enable_block("event_keyboard_held") # First Game, Pong, Breakout (continuous movement)
        config.enable_block("event_keyboard_nokey")# First Game, Pong, Breakout (stop when no key)
        config.enable_block("event_collision")     # First Game, Pong, Breakout
        config.enable_block("event_alarm")         # First Game (star spawning timer)
        config.enable_block("event_other")         # Breakout (no_more_lives game-over hook)

        # Movement
        config.enable_block("move_set_hspeed")     # First Game, Pong, Breakout
        config.enable_block("move_set_vspeed")     # First Game, Pong, Breakout
        config.enable_block("move_stop")           # First Game, Pong, Breakout
        config.enable_block("move_jump_to")        # Pong (ball reset), Breakout
        config.enable_block("move_direction")      # Pong (ball start direction)
        config.enable_block("bounce")              # Pong (ball bouncing)
        config.enable_block("reverse_horizontal")  # Breakout (ball direction)
        config.enable_block("reverse_vertical")    # Breakout (ball direction)
        config.enable_block("set_gravity")         # beginner sample game (falling/physics)

        # Timing
        config.enable_block("set_alarm")           # First Game (star spawn interval)

        # Drawing
        config.enable_block("draw_text")           # First Game, Pong (score display)
        config.enable_block("draw_score")          # First Game, Breakout

        # Score and Lives
        config.enable_block("score_set")           # First Game, Pong, Breakout
        config.enable_block("score_add")           # First Game, Breakout
        config.enable_block("lives_set")           # Breakout
        config.enable_block("lives_add")           # Breakout
        config.enable_block("draw_lives")          # Breakout

        # Instance
        config.enable_block("instance_destroy")       # First Game, Breakout
        config.enable_block("instance_destroy_other") # First Game (star), Breakout (bricks)
        config.enable_block("instance_create")        # First Game (star spawning)
        config.enable_block("instance_change")         # beginner sample game (transform object type)

        # Room
        config.enable_block("room_restart")        # Breakout (game over)
        # Room-existence checks — needed so beginners can fix the
        # maze samples' multi-room navigation events (and write their
        # own; the pair is common when guarding goto_next_room /
        # goto_previous_room on the first / last room). The "if next
        # room doesn't exist" case (e.g. end the game on the goal in
        # the last level) is expressed via else_actions on
        # `room_if_next_exists` rather than a separate inverted block.
        config.enable_block("room_if_next_exists")
        config.enable_block("room_if_previous_exists")

        # Game control — game-over flow and highscore
        config.enable_block("game_end")            # Breakout (end game on no_more_lives)
        config.enable_block("show_highscore")      # Breakout (display highscore table)

        # Control flow — exit_event lets beginners write GameMaker-style
        # "try a direction, commit if it fits, otherwise try the next"
        # patterns (e.g. maze_3's monster bounce on wall collision).
        # test_variable is enabled so a beginner sample game can branch on
        # a variable's value. The remaining Control blocks (if_condition /
        # set_variable) stay out of beginner to keep the picker simple.
        # start_block/end_block pair with else_action when a branch needs
        # more than one action (e.g. platformer step: on ground →
        # zero gravity AND snap to contact).
        config.enable_block("exit_event")
        config.enable_block("else_action")
        config.enable_block("start_block")
        config.enable_block("end_block")
        config.enable_block("test_variable")

        # Output
        config.enable_block("output_message")      # Game over messages

        # Generated (no hand-written block) actions the fix in
        # docs/BLOCKLY_TOOLBOX_GATING_PLAN.md newly gates. First decided with
        # the user 2026-10-01 from a partial audit (3 actions); a full
        # per-sample audit (every beginner-edition sample's project.json,
        # tests/test_blockly_preset_generated_actions.py) found 17 more
        # actually in use, several more widely used than those 3 --
        # decided with the user the same day to include all of them.
        # set_draw_font and draw_sprite are the only two left out
        # (sky_strike_1 only, each): a sample using a block that's not in
        # the toolbox still loads and runs, it just can't be added again
        # from the picker.
        config.enable_block("restart_game")          # maze_1/3/4, plateforme_3, treasure, sky_strike_1
        config.enable_block("set_window_caption")    # maze_2/3/4, plateforme_3, treasure
        config.enable_block("set_draw_color")        # maze_3/4
        config.enable_block("start_moving_direction")  # maze_1/2/3/4, plateforme_3, treasure
        config.enable_block("comment")                  # maze_3/4, plateforme_1/2/3
        config.enable_block("if_collision")             # maze_3/4, plateforme_1/2/3
        config.enable_block("test_instance_count")      # maze_3/4, treasure
        config.enable_block("sleep")                    # maze_4, plateforme_3, treasure
        config.enable_block("move_to_contact")          # plateforme_1/2/3
        config.enable_block("execute_code")             # match3_1/2/3
        config.enable_block("if_object_exists")         # maze_2, plateforme_3
        config.enable_block("set_direction_speed")      # maze_3/4
        config.enable_block("destroy_at_position")      # maze_3/4
        config.enable_block("check_empty")              # maze_3/4
        config.enable_block("jump_to_start")            # maze_4, treasure
        config.enable_block("test_alignment")           # maze_4, treasure
        config.enable_block("test_chance")              # maze_4, treasure
        config.enable_block("test_expression")          # plateforme_3
        config.enable_block("execute_script")           # treasure
        config.enable_block("set_background")           # sky_strike_1

        # Enable categories that have blocks
        config.enabled_categories = {
            "Events", "Movement", "Timing", "Drawing",
            "Score/Lives/Health", "Instance", "Room", "Output", "Game",
            "Control",
        }

        return config

    @classmethod
    def get_intermediate(cls) -> 'BlocklyConfig':
        """Intermediate preset — adds Sokoban, Maze, Platformer, Lunar Lander tutorials"""
        config = cls.get_beginner()
        config.preset_name = "intermediate"

        # Additional events
        config.enable_block("event_keyboard_press")  # Sokoban (one move per press)
        config.enable_block("event_destroy")         # General cleanup

        # Grid movement for Sokoban and Maze
        config.enable_block("move_snap_to_grid")
        config.enable_block("grid_move")
        config.enable_block("grid_if_on_grid")

        # Physics for Platformer and Lunar Lander
        config.enable_block("set_gravity")
        config.enable_block("set_friction")

        # Instance management
        config.enable_block("instance_change")       # Sokoban (crate on target)
        config.enable_block("if_can_push")           # Sokoban (push mechanic)
        config.enable_block("check_empty")           # Sokoban/Maze (can-I-move-here?)

        # Drawing
        config.enable_block("set_sprite")            # Sokoban (crate appearance)

        # Health system
        config.enable_block("health_set")
        config.enable_block("health_add")
        config.enable_block("draw_health_bar")

        # Room navigation
        config.enable_block("room_goto_next")
        config.enable_block("room_goto_previous")
        config.enable_block("room_goto")
        config.enable_block("room_if_next_exists")
        config.enable_block("room_if_previous_exists")

        # Sound
        config.enable_block("sound_play")
        config.enable_block("music_play")
        config.enable_block("music_stop")

        # Output
        config.enable_block("execute_code")

        config.enabled_categories.update({"Sound"})

        # Behaviour-preserving (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2):
        # every generated action already showed here, ungated, before this
        # fix. Trimming this preset to a smaller set is a separate decision.
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)

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
        config.enable_block("instance_change")
        config.enable_block("check_empty")           # platform/wall checks

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

        # Behaviour-preserving (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2).
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)

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
        config.enable_block("grid_move")
        config.enable_block("grid_stop_if_no_keys")
        config.enable_block("grid_check_keys_and_move")
        config.enable_block("grid_if_on_grid")
        config.enable_block("check_empty")           # "can I move into this cell?"

        # Instance
        config.enable_block("instance_destroy")
        config.enable_block("instance_create")
        config.enable_block("instance_change")

        # Health system
        config.enable_block("health_set")
        config.enable_block("health_add")
        config.enable_block("draw_health_bar")

        # Room
        config.enable_block("room_goto_next")
        config.enable_block("room_goto")

        # Output
        config.enable_block("output_message")
        config.enable_block("execute_code")

        # Sound
        config.enable_block("sound_play")
        config.enable_block("music_play")

        config.enabled_categories = {"Events", "Movement", "Score/Lives/Health", "Instance", "Room", "Output", "Sound"}

        # Behaviour-preserving (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2).
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)

        return config

    @classmethod
    def get_sokoban(cls) -> 'BlocklyConfig':
        """Sokoban/box-pushing puzzle game preset"""
        config = cls(preset_name="sokoban")

        # Events - essential for Sokoban
        config.enable_block("event_create")
        config.enable_block("event_keyboard_press")  # Arrow keys for grid movement (one move per press)
        config.enable_block("event_keyboard_nokey")  # Stop when no key pressed
        config.enable_block("event_collision")  # Push boxes, hit walls

        # Movement - grid-based movement is essential
        config.enable_block("move_set_hspeed")
        config.enable_block("move_set_vspeed")
        config.enable_block("move_stop")
        config.enable_block("move_snap_to_grid")
        config.enable_block("move_jump_to")  # For pushing boxes
        config.enable_block("grid_move")  # Grid-based movement
        config.enable_block("grid_if_on_grid")  # Only move when aligned

        # Instance - for changing box types
        config.enable_block("instance_destroy")
        config.enable_block("instance_create")
        config.enable_block("instance_change")
        config.enable_block("if_can_push")  # Sokoban push mechanic

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
        config.enable_block("execute_code")

        config.enabled_categories = {"Events", "Movement", "Instance", "Room", "Score/Lives/Health", "Output"}

        # Behaviour-preserving (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2).
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)

        return config

    # get_thymio() moved to extensions/thymio/blockly_categories.py's
    # _build_thymio_preset() (docs/THYMIO_EXTENSION_PLAN.md, Stage F) --
    # it can't reuse enable_category() the way this class's own presets do;
    # see that module's docstring for why.

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
        See docs/RELEASE_QA_CHECKLIST.md for the full testing plan.
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
        config.enable_block("instance_change")

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
        config.enable_block("execute_code")

        config.enabled_categories = {"Events", "Movement", "Instance", "Room", "Output"}

        # Behaviour-preserving (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2).
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)

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

    @classmethod
    def get_code_editor(cls) -> 'BlocklyConfig':
        """Code Editor preset - only includes events and actions that the
        Python Code Editor can display and parse bidirectionally.

        All events and actions in this preset can be:
        1. Generated from Blockly/Events Panel to Python code
        2. Parsed from Python code back to Blockly/Events Panel

        Supported actions (from python_code_parser.py ACTION_TO_PYTHON):
        - Movement: set_hspeed, set_vspeed, stop_movement, reverse_horizontal,
                   reverse_vertical, set_gravity, set_friction, jump_to_position,
                   snap_to_grid, set_direction_speed
        - Instance: destroy_instance, create_instance
        - Room: next_room, previous_room, restart_room, goto_room
        - Game: end_game, restart_game
        - Score/Lives/Health: set_score, set_lives, set_health
        - Drawing: draw_score, draw_lives, draw_health_bar, set_sprite, set_alpha
        - Alarm: set_alarm
        - Sound: play_sound, play_music, stop_music
        - Output: display_message, execute_code

        Supported events:
        - create, destroy, step, begin_step, end_step, draw
        - alarm_0 through alarm_11
        - keyboard_<key>, keyboard_pressed_<key>, keyboard_released_<key>
        - collision_with_<object>
        """
        config = cls(preset_name="code_editor")

        # =====================================================================
        # EVENTS - All events supported by the code editor
        # =====================================================================
        config.enable_block("event_create")
        config.enable_block("event_destroy")
        config.enable_block("event_step")
        config.enable_block("event_draw")
        config.enable_block("event_alarm")
        config.enable_block("event_keyboard_held")
        config.enable_block("event_keyboard_press")
        config.enable_block("event_keyboard_release")
        config.enable_block("event_collision")

        # =====================================================================
        # MOVEMENT - Actions with Python code templates
        # =====================================================================
        config.enable_block("move_set_hspeed")      # set_hspeed
        config.enable_block("move_set_vspeed")      # set_vspeed
        config.enable_block("move_stop")            # stop_movement
        config.enable_block("reverse_horizontal")   # reverse_horizontal
        config.enable_block("reverse_vertical")     # reverse_vertical
        config.enable_block("set_gravity")          # set_gravity
        config.enable_block("set_friction")         # set_friction
        config.enable_block("move_jump_to")         # jump_to_position
        config.enable_block("move_snap_to_grid")    # snap_to_grid
        config.enable_block("move_direction")       # set_direction_speed

        # =====================================================================
        # INSTANCE - Create/destroy actions
        # =====================================================================
        config.enable_block("instance_destroy")     # destroy_instance
        config.enable_block("instance_create")      # create_instance
        config.enable_block("instance_change")      # change_instance

        # =====================================================================
        # ROOM - Navigation actions
        # =====================================================================
        config.enable_block("room_goto_next")       # next_room
        config.enable_block("room_goto_previous")   # previous_room
        config.enable_block("room_restart")         # restart_room
        config.enable_block("room_goto")            # goto_room

        # =====================================================================
        # GAME CONTROL
        # =====================================================================
        config.enable_block("game_end")             # end_game
        config.enable_block("game_restart")         # restart_game

        # =====================================================================
        # SCORE/LIVES/HEALTH
        # =====================================================================
        config.enable_block("score_set")            # set_score
        config.enable_block("score_add")            # set_score (relative)
        config.enable_block("lives_set")            # set_lives
        config.enable_block("lives_add")            # set_lives (relative)
        config.enable_block("health_set")           # set_health
        config.enable_block("health_add")           # set_health (relative)
        config.enable_block("draw_score")           # draw_score
        config.enable_block("draw_lives")           # draw_lives
        config.enable_block("draw_health_bar")      # draw_health_bar

        # =====================================================================
        # SPRITE/APPEARANCE
        # =====================================================================
        config.enable_block("set_sprite")           # set_sprite
        config.enable_block("set_alpha")            # set_alpha (image_alpha)

        # =====================================================================
        # TIMING
        # =====================================================================
        config.enable_block("set_alarm")            # set_alarm

        # =====================================================================
        # SOUND
        # =====================================================================
        config.enable_block("sound_play")           # play_sound
        config.enable_block("music_play")           # play_music
        config.enable_block("music_stop")           # stop_music

        # =====================================================================
        # OUTPUT
        # =====================================================================
        config.enable_block("output_message")       # display_message
        config.enable_block("execute_code")         # execute_code (passthrough)

        # Enable all categories that have blocks
        config.enabled_categories = {
            "Events", "Movement", "Instance", "Room", "Game",
            "Score/Lives/Health", "Drawing", "Timing", "Sound", "Output"
        }

        # Behaviour-preserving (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2) --
        # this preset's own docstring claims a narrower, Python-code-parser-
        # matched scope, but the pre-fix bug showed every generated action
        # regardless; trimming to the documented scope is a separate,
        # later decision (not made here).
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)

        return config

    @classmethod
    def get_blockly_editor(cls) -> 'BlocklyConfig':
        """Blockly Editor preset - includes all events and actions that work
        in the Blockly visual programming editor.

        This preset includes all implemented blocks that can be used in Blockly.
        Some blocks may not have Python code equivalents (use Code Editor preset
        for bidirectional Python sync).

        Includes:
        - All implemented events (create, step, draw, destroy, keyboard, mouse,
          collision, alarm, other)
        - All implemented movement actions (including grid movement helpers)
        - All implemented instance actions
        - All implemented room actions (including conditional checks)
        - All implemented score/lives/health actions
        - All implemented sprite/appearance actions
        - All implemented timing actions
        - All implemented sound actions
        - All implemented output actions
        - All implemented game control actions
        - All value blocks for reading game state
        """
        config = cls(preset_name="blockly_editor")

        # =====================================================================
        # EVENTS - All implemented events
        # =====================================================================
        config.enable_block("event_create")
        config.enable_block("event_step")
        config.enable_block("event_draw")
        config.enable_block("event_destroy")
        config.enable_block("event_keyboard_nokey")
        config.enable_block("event_keyboard_anykey")
        config.enable_block("event_keyboard_held")
        config.enable_block("event_keyboard_press")
        config.enable_block("event_keyboard_release")
        config.enable_block("event_mouse")
        config.enable_block("event_collision")
        config.enable_block("event_alarm")
        config.enable_block("event_other")

        # =====================================================================
        # MOVEMENT - All implemented movement actions
        # =====================================================================
        config.enable_block("move_set_hspeed")
        config.enable_block("move_set_vspeed")
        config.enable_block("move_stop")
        config.enable_block("move_direction")
        config.enable_block("move_snap_to_grid")
        config.enable_block("move_jump_to")
        config.enable_block("grid_move")
        config.enable_block("grid_stop_if_no_keys")
        config.enable_block("grid_check_keys_and_move")
        config.enable_block("grid_if_on_grid")
        config.enable_block("set_gravity")
        config.enable_block("set_friction")
        config.enable_block("reverse_horizontal")
        config.enable_block("reverse_vertical")
        config.enable_block("bounce")
        config.enable_block("wrap_around_room")

        # =====================================================================
        # TIMING
        # =====================================================================
        config.enable_block("set_alarm")

        # =====================================================================
        # DRAWING/SPRITE
        # =====================================================================
        config.enable_block("set_sprite")

        # =====================================================================
        # SCORE/LIVES/HEALTH
        # =====================================================================
        config.enable_block("score_set")
        config.enable_block("score_add")
        config.enable_block("lives_set")
        config.enable_block("lives_add")
        config.enable_block("health_set")
        config.enable_block("health_add")
        config.enable_block("draw_score")
        config.enable_block("draw_lives")
        config.enable_block("draw_health_bar")

        # =====================================================================
        # INSTANCE
        # =====================================================================
        config.enable_block("instance_destroy")
        config.enable_block("instance_destroy_other")
        config.enable_block("instance_create")
        config.enable_block("instance_change")
        config.enable_block("if_can_push")

        # =====================================================================
        # ROOM
        # =====================================================================
        config.enable_block("room_goto_next")
        config.enable_block("room_goto_previous")
        config.enable_block("room_restart")
        config.enable_block("room_if_next_exists")
        config.enable_block("room_if_previous_exists")

        # =====================================================================
        # VALUES - For reading game state
        # =====================================================================
        config.enable_block("value_x")
        config.enable_block("value_y")
        config.enable_block("value_hspeed")
        config.enable_block("value_vspeed")
        config.enable_block("value_score")
        config.enable_block("value_lives")
        config.enable_block("value_health")
        config.enable_block("value_mouse_x")
        config.enable_block("value_mouse_y")

        # =====================================================================
        # SOUND
        # =====================================================================
        config.enable_block("sound_play")
        config.enable_block("music_play")
        config.enable_block("music_stop")

        # =====================================================================
        # OUTPUT
        # =====================================================================
        config.enable_block("output_message")
        config.enable_block("execute_code")

        # =====================================================================
        # GAME CONTROL
        # =====================================================================
        config.enable_block("game_end")
        config.enable_block("game_restart")
        config.enable_block("show_highscore")
        config.enable_block("clear_highscore")

        # Enable all categories that have blocks
        config.enabled_categories = {
            "Events", "Movement", "Timing", "Drawing", "Score/Lives/Health",
            "Instance", "Room", "Values", "Sound", "Output", "Game"
        }

        # Behaviour-preserving (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 2).
        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)

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
    # "thymio" is registered by extensions/thymio/blockly_categories.py via
    # register_blockly_presets() once the extension loads (Stage F).
    "testing": BlocklyConfig.get_testing(),
    "implemented_only": BlocklyConfig.get_implemented_only(),
    "code_editor": BlocklyConfig.get_code_editor(),
    "blockly_editor": BlocklyConfig.get_blockly_editor(),
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
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)


def load_config() -> BlocklyConfig:
    """Load configuration from file, or return default"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, encoding='utf-8') as f:
                data = json.load(f)
                config = BlocklyConfig.from_dict(data)
                needs_save = False

                # Migrate (Unit 2, docs/BLOCKLY_TOOLBOX_GATING_PLAN.md): a
                # config saved before GENERATED_ACTION_NAMES existed has none
                # of them, which would newly hide every one of those actions
                # for a custom (non-"full") config that previously saw them
                # all, same as every preset's own migration below. Runs once
                # per file -- config_version going to 2 is what stops it
                # re-running on the next load.
                if config.config_version < 2:
                    added = GENERATED_ACTION_NAMES - config.enabled_blocks
                    if added:
                        print(f"Blockly config migration: Adding {len(added)} generated action names: {added}")
                        config.enabled_blocks.update(GENERATED_ACTION_NAMES | PROMOTED_TO_HAND_WRITTEN_BLOCKS)
                    config.config_version = 2
                    needs_save = True

                # Migrate: If using "full" preset, ensure all new blocks and categories are enabled
                # This handles the case where new blocks/categories were added after config was saved
                if config.preset_name == "full":
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

                # Save the migrated config so it persists (either migration
                # above may have set this, independent of preset_name).
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


# ============================================================================
# EXTENSION MERGE POINT (docs/THYMIO_EXTENSION_PLAN.md, Stage 0.6)
# ============================================================================
# An extension contributes hand-curated toolbox categories (the same shape
# as the entries above) via PLUGIN_BLOCK_CATEGORIES, and presets via
# PLUGIN_BLOCKLY_PRESETS; events/plugin_loader calls these at startup.

def register_block_categories(categories: Dict[str, List[Dict]]) -> int:
    """Merge extension categories into BLOCK_REGISTRY (first name wins, so a
    re-run is a no-op). Presets that mean "everything" are rebuilt so they
    include the new blocks. Returns how many categories were added."""
    added = 0
    for name, blocks in (categories or {}).items():
        if name in BLOCK_REGISTRY:
            continue
        BLOCK_REGISTRY[name] = [dict(block) for block in blocks]
        added += 1
    if added:
        PRESETS["full"] = BlocklyConfig.get_full()
        PRESETS["implemented_only"] = BlocklyConfig.get_implemented_only()
    return added


def unregister_block_categories(names) -> None:
    """Drop categories added by register_block_categories. For tests."""
    for name in names:
        BLOCK_REGISTRY.pop(name, None)
    PRESETS["full"] = BlocklyConfig.get_full()
    PRESETS["implemented_only"] = BlocklyConfig.get_implemented_only()


def register_blockly_presets(presets: Dict[str, BlocklyConfig]) -> int:
    """Add extension presets to PRESETS (first name wins)."""
    added = 0
    for name, config in (presets or {}).items():
        if name in PRESETS or not isinstance(config, BlocklyConfig):
            continue
        PRESETS[name] = config
        added += 1
    return added
