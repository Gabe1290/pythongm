#!/usr/bin/env python3
"""
Mapping tables for converting GameMaker 8.0/8.1 numeric IDs
to pygm2 string identifiers.

Covers: virtual key codes, event types, mouse sub-events,
other sub-events, step sub-events, and standard action library mappings.
"""

# ============================================================================
# VIRTUAL KEY CODE → pygm2 key name (lowercase)
# ============================================================================
# GM8 uses Windows virtual key codes for keyboard events.
# pygm2 uses lowercase key name strings in event data.

GM_VK_TO_KEY_NAME = {
    0: "nokey",
    1: "anykey",
    # Common keys
    8: "backspace",
    9: "tab",
    13: "enter",
    16: "shift",
    17: "control",
    18: "alt",
    19: "pause",
    20: "capslock",
    27: "escape",
    32: "space",
    33: "pageup",
    34: "pagedown",
    35: "end",
    36: "home",
    37: "left",
    38: "up",
    39: "right",
    40: "down",
    44: "print",
    45: "insert",
    46: "delete",
    # Digits 0-9
    **{k: str(k - 48) for k in range(48, 58)},
    # Letters A-Z → lowercase
    **{k: chr(k + 32) for k in range(65, 91)},
    # Numpad 0-9
    96: "numpad_0",
    97: "numpad_1",
    98: "numpad_2",
    99: "numpad_3",
    100: "numpad_4",
    101: "numpad_5",
    102: "numpad_6",
    103: "numpad_7",
    104: "numpad_8",
    105: "numpad_9",
    106: "numpad_multiply",
    107: "numpad_plus",
    109: "numpad_minus",
    110: "numpad_period",
    111: "numpad_divide",
    # Function keys F1-F12
    **{k: f"f{k - 111}" for k in range(112, 124)},
    # Lock keys
    144: "numlock",
    145: "scrolllock",
    # Punctuation (VK_OEM codes)
    186: "semicolon",
    187: "equals",
    188: "comma",
    189: "minus",
    190: "period",
    191: "slash",
    192: "backquote",
    219: "leftbracket",
    220: "backslash",
    221: "rightbracket",
    222: "quote",
}


# ============================================================================
# EVENT TYPE MAPPING
# ============================================================================
# GM8 event type IDs (0-11) and their sub-event resolution.

GM_STEP_SUBEVENT = {
    0: "step",
    1: "begin_step",
    2: "end_step",
}

GM_MOUSE_SUBEVENT = {
    0: "mouse_left_button",
    1: "mouse_right_button",
    2: "mouse_middle_button",
    3: "mouse_no_button",
    4: "mouse_left_press",
    5: "mouse_right_press",
    6: "mouse_middle_press",
    7: "mouse_left_release",
    8: "mouse_right_release",
    9: "mouse_middle_release",
    10: "mouse_enter",
    11: "mouse_leave",
    16: "mouse_global_left_button",
    17: "mouse_global_right_button",
    18: "mouse_global_middle_button",
    19: "mouse_global_left_press",
    20: "mouse_global_right_press",
    21: "mouse_global_middle_press",
    22: "mouse_global_left_release",
    23: "mouse_global_right_release",
    24: "mouse_global_middle_release",
    60: "mouse_wheel_up",
    61: "mouse_wheel_down",
}

GM_OTHER_SUBEVENT = {
    0: "outside_room",
    1: "intersect_boundary",
    2: "game_start",
    3: "game_end",
    4: "room_start",
    5: "room_end",
    6: "no_more_lives",
    7: "animation_end",
    8: "end_of_path",
    9: "no_more_health",
    10: "close_button",
    # User events 0-15 (sub-event codes 10-25 in some GM versions,
    # or 11-26 -- we handle both with a fallback)
}
# Add user events
for _i in range(16):
    GM_OTHER_SUBEVENT[10 + _i] = f"user_event_{_i}"


def resolve_event(event_type: int, event_number: int, object_names: list):
    """
    Convert a GM event type + sub-event number to pygm2 event structure.

    Args:
        event_type: GM event type ID (0-11)
        event_number: Sub-event number (meaning depends on event_type)
        object_names: List of object names indexed by resource ID

    Returns:
        Tuple of (event_key, sub_key_or_None, extra_dict):
          - For simple events: ("create", None, {})
          - For keyboard: ("keyboard", "left", {})
          - For collision: ("collision_with_obj_wall", None, {"target_object": "obj_wall"})
          - For alarm: ("alarm_3", None, {})
    """
    if event_type == 0:  # Create
        return ("create", None, {})
    elif event_type == 1:  # Destroy
        return ("destroy", None, {})
    elif event_type == 2:  # Alarm
        return (f"alarm_{event_number}", None, {})
    elif event_type == 3:  # Step
        name = GM_STEP_SUBEVENT.get(event_number, "step")
        return (name, None, {})
    elif event_type == 4:  # Collision
        obj_name = _resolve_name(object_names, event_number, "object")
        return (f"collision_with_{obj_name}", None, {"target_object": obj_name})
    elif event_type == 5:  # Keyboard (held)
        key = GM_VK_TO_KEY_NAME.get(event_number, f"key_{event_number}")
        return ("keyboard", key, {})
    elif event_type == 6:  # Mouse
        name = GM_MOUSE_SUBEVENT.get(event_number, f"mouse_event_{event_number}")
        return (name, None, {})
    elif event_type == 7:  # Other
        name = GM_OTHER_SUBEVENT.get(event_number, f"other_event_{event_number}")
        return (name, None, {})
    elif event_type == 8:  # Draw
        return ("draw", None, {})
    elif event_type == 9:  # Key Press
        key = GM_VK_TO_KEY_NAME.get(event_number, f"key_{event_number}")
        return ("keyboard_press", key, {})
    elif event_type == 10:  # Key Release
        key = GM_VK_TO_KEY_NAME.get(event_number, f"key_{event_number}")
        return ("keyboard_release", key, {})
    elif event_type == 11:  # Trigger
        return (f"trigger_{event_number}", None, {})
    else:
        return (f"unknown_event_{event_type}_{event_number}", None, {})


def _resolve_name(names_list, index, resource_type):
    """Safely resolve a resource name by index."""
    if 0 <= index < len(names_list) and names_list[index] is not None:
        return names_list[index]
    return f"unknown_{resource_type}_{index}"


# ============================================================================
# ACTION MAPPING: (library_id, action_id) → pygm2 action name
# ============================================================================
# GM8 standard action library uses library_id = 1.
# Action IDs correspond to specific drag-and-drop actions.

GM_ACTION_MAP = {
    # ---- Move tab ----
    (1, 101): "start_moving_direction",
    (1, 102): "set_direction_speed",
    (1, 103): "move_towards_point",
    (1, 104): "set_hspeed",
    (1, 105): "set_vspeed",
    (1, 106): "set_gravity",
    (1, 107): "reverse_horizontal",
    (1, 108): "reverse_vertical",
    (1, 109): "set_friction",
    (1, 110): "jump_to_start",        # GM7 action_move_start
    (1, 111): "jump_to_position",
    (1, 112): "jump_to_start",
    (1, 113): "jump_to_random",
    (1, 114): "snap_to_grid",
    (1, 115): "wrap_around_room",
    (1, 116): "move_to_contact",
    (1, 117): "bounce",
    # ---- Main1 tab (Objects) ----
    (1, 201): "create_instance",
    (1, 202): "create_moving_instance",
    (1, 203): "create_random_instance",
    (1, 206): "change_instance",
    (1, 207): "destroy_instance",
    (1, 208): "destroy_at_position",
    # ---- Main2 tab (Sprite/Sound) ----
    (1, 211): "set_sprite",
    (1, 212): "play_sound",
    (1, 213): "stop_sound",
    (1, 214): "check_sound",
    # GM7 sprite/sound actions
    (1, 541): "set_sprite",           # GM7 action_sprite_set
    (1, 542): "change_sprite",        # GM7 action_sprite_transform
    (1, 543): "set_sprite_color",     # GM7 action_sprite_color
    (1, 551): "play_sound",           # GM7 action_sound
    (1, 552): "stop_sound",           # GM7 action_sound_stop
    (1, 553): "check_sound",          # GM7 action_if_sound
    # ---- Control tab ----
    (1, 301): "if_collision",
    (1, 302): "if_object_exists",
    (1, 303): "test_instance_count",
    (1, 304): "test_chance",
    (1, 305): "test_question",
    (1, 306): "test_expression",
    (1, 309): "if_collision",  # "if collision at position" variant
    (1, 410): "test_alignment",        # GM7 action_if_aligned
    (1, 321): "start_block",
    (1, 322): "end_block",
    (1, 323): "else_block",
    (1, 324): "repeat",
    (1, 325): "exit_event",
    # ---- Score tab ----
    (1, 401): "set_score",
    (1, 402): "test_score",
    (1, 403): "draw_score",
    (1, 404): "show_highscore",
    (1, 405): "clear_highscore",
    (1, 411): "set_lives",
    (1, 412): "test_lives",
    (1, 413): "draw_lives",
    (1, 421): "set_health",
    (1, 422): "test_health",
    (1, 423): "draw_health_bar",
    (1, 424): "start_block",          # GM7 begin-group (kind=2)
    (1, 431): "set_window_caption",
    # GM7 score/lives/health IDs
    (1, 709): "show_highscore",        # GM7 action_highscore_show
    (1, 710): "clear_highscore",       # GM7 action_highscore_clear
    (1, 711): "set_lives",             # GM7 action_set_life
    (1, 712): "test_lives",            # GM7 action_if_life
    (1, 713): "draw_lives",            # GM7 action_draw_life
    (1, 721): "set_health",            # GM7 action_set_health
    (1, 722): "test_health",           # GM7 action_if_health
    (1, 723): "draw_health_bar",       # GM7 action_draw_health
    (1, 731): "set_window_caption",    # GM7 action_set_caption
    # ---- Extra tab ----
    (1, 501): "set_variable",
    (1, 502): "test_variable",
    (1, 503): "draw_variable",
    # GM7 variable/test actions
    (1, 611): "set_variable",          # GM7 action_variable
    (1, 612): "test_variable",         # GM7 action_if_variable
    # ---- Draw tab ----
    (1, 511): "draw_sprite",
    (1, 512): "draw_background",
    (1, 513): "draw_text",
    (1, 514): "draw_scaled_text",
    (1, 515): "draw_rectangle",
    (1, 521): "draw_ellipse",
    (1, 522): "draw_line",
    (1, 523): "draw_arrow",
    (1, 524): "set_draw_color",
    (1, 525): "set_draw_font",
    (1, 526): "fill_color",
    # ---- Code tab ----
    (1, 601): "execute_code",
    (1, 602): "execute_script",
    (1, 603): "comment",
    # ---- Room tab ----
    (1, 222): "next_room",             # GM7 action_next_room
    (1, 224): "goto_room",             # GM7 action_room_goto
    (1, 225): "previous_room",         # GM7 action_room_previous
    (1, 226): "test_next_room",        # GM7 action_if_next_room
    (1, 227): "test_previous_room",    # GM7 action_if_previous_room
    (1, 701): "goto_room",
    (1, 702): "previous_room",
    (1, 703): "next_room",
    (1, 704): "restart_room",
    # ---- Timing tab ----
    (1, 801): "set_alarm",
    (1, 802): "set_timeline",
    (1, 803): "set_timeline_position",
    (1, 804): "set_timeline_speed",
    (1, 805): "start_timeline",
    (1, 806): "pause_timeline",
    (1, 807): "stop_timeline",
    # ---- Info tab ----
    (1, 531): "create_effect",
    (1, 808): "display_message",
    (1, 809): "show_info",
    (1, 810): "open_webpage",
    # ---- Game tab ----
    (1, 331): "restart_game",          # GM7 action_restart_game
    (1, 332): "end_game",              # GM7 action_end_game
    (1, 811): "restart_game",
    (1, 812): "end_game",
    (1, 813): "save_game",
    (1, 814): "load_game",
    # ---- Resources tab ----
    (1, 901): "replace_sprite",
    (1, 902): "replace_sound",
    (1, 903): "replace_background",
}

# Parameter name mapping for known actions.
# Maps (library_id, action_id) → list of pygm2 parameter names
# corresponding to the GM argument order.
GM_ACTION_PARAMS = {
    # Move
    (1, 101): ["directions", "speed"],
    (1, 102): ["direction", "speed"],
    (1, 103): ["x", "y", "speed"],
    (1, 104): ["hspeed"],
    (1, 105): ["vspeed"],
    (1, 106): ["direction", "gravity"],
    (1, 109): ["friction"],
    (1, 111): ["x", "y"],
    (1, 114): ["hsnap", "vsnap"],
    (1, 115): ["direction"],       # horizontal, vertical, both
    (1, 116): ["direction", "max_distance"],
    (1, 117): ["precise", "against"],
    # Main1
    (1, 201): ["object", "x", "y"],
    (1, 202): ["object", "x", "y", "speed", "direction"],
    (1, 203): ["object1", "object2", "object3", "object4", "x", "y"],
    (1, 206): ["object", "perform_events"],
    (1, 207): [],                   # no params (applies to self/other)
    (1, 208): ["x", "y"],
    # Main2 - Sprite/Sound
    (1, 211): ["sprite", "subimage", "speed"],
    (1, 212): ["sound", "loop"],
    (1, 213): ["sound"],
    (1, 214): ["sound"],
    # Control
    (1, 301): ["x", "y", "object"],
    (1, 302): ["object", "count"],
    (1, 303): ["object", "count", "operation"],
    (1, 304): ["sides"],
    (1, 305): ["question"],
    (1, 306): ["expression"],
    (1, 309): ["x", "y", "object"],
    (1, 321): [],  # start_block
    (1, 322): [],  # end_block
    (1, 323): [],  # else
    (1, 324): ["times"],
    (1, 325): [],  # exit
    # Score
    (1, 401): ["value"],            # set_score
    (1, 402): ["value", "operation"],
    (1, 403): ["x", "y", "caption"],
    (1, 411): ["value"],            # set_lives
    (1, 412): ["value", "operation"],
    (1, 413): ["x", "y", "image"],
    (1, 421): ["value"],            # set_health
    (1, 422): ["value", "operation"],
    (1, 423): ["x1", "y1", "x2", "y2", "back_color", "bar_color"],
    (1, 431): ["score", "lives", "health"],
    # Extra
    (1, 501): ["variable", "value"],
    (1, 502): ["variable", "value", "operation"],
    (1, 503): ["variable", "x", "y"],
    # Draw
    (1, 511): ["sprite", "x", "y", "subimage"],
    (1, 512): ["background", "x", "y", "tiled"],
    (1, 513): ["text", "x", "y"],
    (1, 514): ["text", "x", "y", "xscale", "yscale", "angle"],
    (1, 515): ["x1", "y1", "x2", "y2", "filled"],
    (1, 521): ["x1", "y1", "x2", "y2", "filled"],
    (1, 522): ["x1", "y1", "x2", "y2"],
    (1, 523): ["x1", "y1", "x2", "y2", "tip_size"],
    (1, 524): ["color"],
    (1, 525): ["font", "align"],
    (1, 526): ["color"],
    # Code
    (1, 601): ["code"],
    (1, 602): ["script"],
    (1, 603): ["text"],
    # Rooms
    (1, 701): ["room", "transition"],
    (1, 702): ["transition"],
    (1, 703): ["transition"],
    (1, 704): ["transition"],
    # Timing
    (1, 801): ["alarm_number", "steps"],
    (1, 802): ["timeline", "position", "start", "loop"],
    (1, 803): ["position"],
    (1, 804): ["speed"],
    (1, 805): [],
    (1, 806): [],
    (1, 807): [],
    # Info
    (1, 531): ["effect_type", "x", "y", "size", "color", "where"],
    (1, 808): ["message"],
    (1, 809): [],
    (1, 810): ["url"],
    # Game
    (1, 811): [],
    (1, 812): [],
    (1, 813): ["filename"],
    (1, 814): ["filename"],
    # Resources
    (1, 901): ["sprite", "filename", "frame_count"],
    (1, 902): ["sound", "filename"],
    (1, 903): ["background", "filename"],
    # ---- GM7 action param mappings ----
    (1, 110): [],                          # jump_to_start (no params)
    (1, 222): ["transition"],              # next_room
    (1, 224): ["room", "transition"],      # goto_room
    (1, 225): ["transition"],              # previous_room
    (1, 226): [],                          # test_next_room
    (1, 227): [],                          # test_previous_room
    (1, 331): [],                          # restart_game
    (1, 332): [],                          # end_game
    (1, 410): ["hsnap", "vsnap"],          # test_alignment
    (1, 424): [],                          # start_block (begin group)
    (1, 541): ["sprite", "subimage", "speed"],   # set_sprite
    (1, 542): ["xscale", "yscale", "angle", "mirror"],  # change_sprite
    (1, 543): ["color", "alpha"],          # set_sprite_color
    (1, 551): ["sound", "loop"],           # play_sound
    (1, 552): ["sound"],                   # stop_sound
    (1, 553): ["sound"],                   # check_sound
    (1, 611): ["variable", "value"],       # set_variable
    (1, 612): ["variable", "value", "operation"],  # test_variable
    (1, 709): [],                          # show_highscore
    (1, 710): [],                          # clear_highscore
    (1, 711): ["value"],                   # set_lives
    (1, 712): ["value", "operation"],      # test_lives
    (1, 713): ["x", "y", "image"],         # draw_lives
    (1, 721): ["value"],                   # set_health
    (1, 722): ["value", "operation"],      # test_health
    (1, 723): ["x1", "y1", "x2", "y2", "back_color", "bar_color"],  # draw_health_bar
    (1, 731): ["score", "lives", "health"],  # set_window_caption
}

# GM argument kind constants (for resource-reference resolution)
ARG_EXPRESSION = 0
ARG_STRING = 1
ARG_BOTH = 2
ARG_BOOLEAN = 3
ARG_MENU = 4
ARG_SPRITE = 5
ARG_SOUND = 6
ARG_BACKGROUND = 7
ARG_PATH = 8
ARG_SCRIPT = 9
ARG_OBJECT = 10
ARG_ROOM = 11
ARG_FONT = 12
ARG_COLOR = 13
ARG_TIMELINE = 14
ARG_FONT_STRING = 15

# Map argument kind to resource type name (for name resolution)
ARG_KIND_TO_RESOURCE = {
    ARG_SPRITE: "sprites",
    ARG_SOUND: "sounds",
    ARG_BACKGROUND: "backgrounds",
    ARG_PATH: "paths",
    ARG_SCRIPT: "scripts",
    ARG_OBJECT: "objects",
    ARG_ROOM: "rooms",
    ARG_FONT: "fonts",
    ARG_TIMELINE: "timelines",
}


# ============================================================================
# COLOR CONVERSION
# ============================================================================

def gm_color_to_hex(gm_color: int) -> str:
    """
    Convert a GameMaker color integer to a CSS hex string.

    GM stores colors as 0x00BBGGRR (BGR format).
    Returns "#RRGGBB".
    """
    r = gm_color & 0xFF
    g = (gm_color >> 8) & 0xFF
    b = (gm_color >> 16) & 0xFF
    return f"#{r:02x}{g:02x}{b:02x}"
