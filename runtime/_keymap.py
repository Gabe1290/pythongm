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
    return special_keys.get(key)
