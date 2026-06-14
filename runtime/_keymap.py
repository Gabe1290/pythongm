#!/usr/bin/env python3
"""
Single-source pygame keycode → key-name mapping.

This table was duplicated verbatim (44 lines, AST-identical) in
`game_runner.GameRunner._get_key_name` and
`input_handler.InputMixin._get_key_name`. Both now delegate here.

pygame is imported defensively (mirroring input_handler) so this module — and
therefore input_handler — stays importable when pygame is absent; game_runner
imports pygame unconditionally anyway, so its behaviour is unchanged.
"""

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    _PYGAME_AVAILABLE = False


def pygame_key_name(key):
    """Map a pygame key code to a key-name string, or None if unrecognized."""
    if not _PYGAME_AVAILABLE:
        return None

    # Arrow keys
    arrow_keys = {
        pygame.K_LEFT: "left",
        pygame.K_RIGHT: "right",
        pygame.K_UP: "up",
        pygame.K_DOWN: "down",
    }
    if key in arrow_keys:
        return arrow_keys[key]

    # Letter keys (a-z)
    if pygame.K_a <= key <= pygame.K_z:
        return chr(key)

    # Number keys (0-9)
    if pygame.K_0 <= key <= pygame.K_9:
        return chr(key)

    # Special keys
    special_keys = {
        pygame.K_SPACE: "space",
        pygame.K_RETURN: "enter",
        pygame.K_ESCAPE: "escape",
        pygame.K_TAB: "tab",
        pygame.K_BACKSPACE: "backspace",
        pygame.K_DELETE: "delete",
        pygame.K_INSERT: "insert",
        pygame.K_HOME: "home",
        pygame.K_END: "end",
        pygame.K_PAGEUP: "pageup",
        pygame.K_PAGEDOWN: "pagedown",
        pygame.K_F1: "f1",
        pygame.K_F2: "f2",
        pygame.K_F3: "f3",
        pygame.K_F4: "f4",
        pygame.K_F5: "f5",
        pygame.K_F6: "f6",
        pygame.K_F7: "f7",
        pygame.K_F8: "f8",
        pygame.K_F9: "f9",
        pygame.K_F10: "f10",
        pygame.K_F11: "f11",
        pygame.K_F12: "f12",
        pygame.K_LSHIFT: "shift",
        pygame.K_RSHIFT: "shift",
        pygame.K_LCTRL: "control",
        pygame.K_RCTRL: "control",
        pygame.K_LALT: "alt",
        pygame.K_RALT: "alt",
    }
    name = special_keys.get(key)
    if name is not None:
        return name
    return _extended_keys().get(key)


_EXTENDED_KEYS_CACHE = None


def _extended_keys():
    """Map numpad / punctuation / lock keys to the names the GMK importer
    emits (importers/gmk_mappings.py). Without these, imported keyboard events
    bound to e.g. the numpad or ';' could never fire (L25). pygame renamed some
    constants across versions, so each is resolved defensively via getattr.
    """
    global _EXTENDED_KEYS_CACHE
    if _EXTENDED_KEYS_CACHE is not None:
        return _EXTENDED_KEYS_CACHE

    mapping = {}

    def add(name, *attr_candidates):
        for attr in attr_candidates:
            code = getattr(pygame, attr, None)
            if code is not None:
                mapping[code] = name
                return

    # Numpad digits (K_KP0.. in older pygame, K_KP_0.. in newer)
    for d in range(10):
        add(f"numpad_{d}", f"K_KP{d}", f"K_KP_{d}")
    add("numpad_multiply", "K_KP_MULTIPLY", "K_KP_MULTIPLY")
    add("numpad_plus", "K_KP_PLUS")
    add("numpad_minus", "K_KP_MINUS")
    add("numpad_period", "K_KP_PERIOD")
    add("numpad_divide", "K_KP_DIVIDE")

    # Lock / system keys
    add("pause", "K_PAUSE")
    add("capslock", "K_CAPSLOCK")
    add("print", "K_PRINTSCREEN", "K_PRINT", "K_SYSREQ")
    add("numlock", "K_NUMLOCKCLEAR", "K_NUMLOCK")
    add("scrolllock", "K_SCROLLLOCK", "K_SCROLLOCK")

    # Punctuation (VK_OEM analogues)
    add("semicolon", "K_SEMICOLON")
    add("equals", "K_EQUALS")
    add("comma", "K_COMMA")
    add("minus", "K_MINUS")
    add("period", "K_PERIOD")
    add("slash", "K_SLASH")
    add("backquote", "K_BACKQUOTE")
    add("leftbracket", "K_LEFTBRACKET")
    add("backslash", "K_BACKSLASH")
    add("rightbracket", "K_RIGHTBRACKET")
    add("quote", "K_QUOTE")

    _EXTENDED_KEYS_CACHE = mapping
    return mapping
