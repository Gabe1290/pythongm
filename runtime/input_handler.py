#!/usr/bin/env python3
"""
Input Handling System

This module provides keyboard and mouse input handling for the game runtime.
It's designed as a mixin class that GameRunner can inherit from.
"""

from typing import Any, Dict, Optional, Set, Tuple, TYPE_CHECKING

from core.logger import get_logger

# Import pygame only when needed to avoid import errors in tests
try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    _PYGAME_AVAILABLE = False

if TYPE_CHECKING:
    from runtime.game_runner import GameRoom

logger = get_logger(__name__)


class InputMixin:
    """Mixin providing input handling methods for GameRunner.

    This class should be inherited by GameRunner to provide keyboard
    and mouse input handling. It expects the following attributes:
    - current_room: GameRoom with instances
    - keys_pressed: Set of currently pressed keys
    - mouse_buttons: Set of currently pressed mouse buttons
    - mouse_x, mouse_y: Current mouse position
    """

    # These will be set by the inheriting class
    current_room: Optional['GameRoom']
    keys_pressed: Set[str]
    mouse_buttons: Set[int]
    mouse_x: int
    mouse_y: int

    def handle_keyboard_press(self, key: int) -> None:
        """Handle keyboard press event.

        Args:
            key: Pygame key code
        """
        if not self.current_room:
            return

        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        # Add to pressed keys set
        self.keys_pressed.add(sub_key)

        logger.debug(f"⌨️ Key pressed: {sub_key}")

        # Execute keyboard events for all instances
        for instance in self.current_room.instances:
            self._execute_keyboard_event(instance, sub_key, "keyboard_press")
            self._execute_keyboard_event(instance, sub_key, "keyboard")

    def handle_keyboard_release(self, key: int) -> None:
        """Handle keyboard release event.

        Args:
            key: Pygame key code
        """
        if not self.current_room:
            return

        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        # Remove from pressed keys set
        self.keys_pressed.discard(sub_key)

        logger.debug(f"⌨️ Key released: {sub_key}")

        # Execute keyboard_release events for all instances
        for instance in self.current_room.instances:
            self._execute_keyboard_event(instance, sub_key, "keyboard_release")

    def _execute_keyboard_event(self, instance: Any, key: str, event_type: str) -> None:
        """Execute keyboard event actions for an instance.

        Args:
            instance: Game instance
            key: Key name (e.g., "left", "space", "a")
            event_type: Event type ("keyboard", "keyboard_press", "keyboard_release")
        """
        if not instance.object_data:
            return

        events = instance.object_data.get('events', {})
        if event_type not in events:
            return

        keyboard_event = events[event_type]
        if not isinstance(keyboard_event, dict):
            return

        # Find key in event dict (case-insensitive)
        found_key = self._find_key_in_event(keyboard_event, key)
        if not found_key:
            return

        sub_event_data = keyboard_event[found_key]
        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
            actions = sub_event_data["actions"]
            logger.debug(f"  ✅ Executing {event_type}.{found_key} for {instance.object_name}")
            for action_data in actions:
                instance.action_executor.execute_action(instance, action_data)

    def _find_key_in_event(self, event_dict: Dict[str, Any], key: str) -> Optional[str]:
        """Find a key in event dictionary (case-insensitive).

        Args:
            event_dict: Dictionary of key events
            key: Key to find

        Returns:
            Matching key name from dict, or None
        """
        if key in event_dict:
            return key
        upper_key = key.upper()
        if upper_key in event_dict:
            return upper_key
        return None

    def handle_mouse_press(self, button: int, pos: Tuple[int, int]) -> None:
        """Handle mouse button press event.

        Args:
            button: Mouse button (1=left, 2=middle, 3=right)
            pos: Mouse position (x, y)
        """
        if not self.current_room:
            return

        self.mouse_buttons.add(button)
        self.mouse_x, self.mouse_y = pos

        button_names = {1: "left", 2: "middle", 3: "right"}
        button_name = button_names.get(button, f"button{button}")

        logger.debug(f"🖱️ Mouse {button_name} pressed at {pos}")

        # Execute mouse events for all instances
        for instance in self.current_room.instances:
            self._execute_mouse_event(instance, button_name, pos, "mouse_button")
            self._execute_mouse_event(instance, button_name, pos, "mouse_press")
            self._check_mouse_global_event(instance, button_name, "global_press")

    def handle_mouse_release(self, button: int, pos: Tuple[int, int]) -> None:
        """Handle mouse button release event.

        Args:
            button: Mouse button (1=left, 2=middle, 3=right)
            pos: Mouse position (x, y)
        """
        if not self.current_room:
            return

        self.mouse_buttons.discard(button)
        self.mouse_x, self.mouse_y = pos

        button_names = {1: "left", 2: "middle", 3: "right"}
        button_name = button_names.get(button, f"button{button}")

        logger.debug(f"🖱️ Mouse {button_name} released at {pos}")

        # Execute mouse release events for all instances
        for instance in self.current_room.instances:
            self._execute_mouse_event(instance, button_name, pos, "mouse_release")
            self._check_mouse_global_event(instance, button_name, "global_release")

    def _execute_mouse_event(
        self, instance: Any, button: str, pos: Tuple[int, int], event_type: str
    ) -> None:
        """Execute mouse event actions for an instance.

        Only triggers if mouse is over the instance.

        Args:
            instance: Game instance
            button: Button name ("left", "right", "middle")
            pos: Mouse position
            event_type: Event type ("mouse_button", "mouse_press", "mouse_release")
        """
        if not instance.object_data:
            return

        # Check if mouse is over instance
        if not self._mouse_over_instance(pos, instance):
            return

        events = instance.object_data.get('events', {})
        if event_type not in events:
            return

        mouse_event = events[event_type]
        if not isinstance(mouse_event, dict):
            return

        if button in mouse_event:
            sub_event_data = mouse_event[button]
            if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                logger.debug(f"  ✅ Executing {event_type}.{button} for {instance.object_name}")
                for action_data in sub_event_data["actions"]:
                    instance.action_executor.execute_action(instance, action_data)

    def _check_mouse_global_event(self, instance: Any, button: str, event_type: str) -> None:
        """Execute global mouse event (doesn't require mouse over instance).

        Args:
            instance: Game instance
            button: Button name
            event_type: Event type ("global_press", "global_release")
        """
        if not instance.object_data:
            return

        events = instance.object_data.get('events', {})
        if event_type not in events:
            return

        global_event = events[event_type]
        if not isinstance(global_event, dict):
            return

        if button in global_event:
            sub_event_data = global_event[button]
            if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                logger.debug(f"  ✅ Executing {event_type}.{button} for {instance.object_name}")
                for action_data in sub_event_data["actions"]:
                    instance.action_executor.execute_action(instance, action_data)

    def _mouse_over_instance(self, pos: Tuple[int, int], instance: Any) -> bool:
        """Check if mouse position is over an instance.

        Args:
            pos: Mouse position (x, y)
            instance: Game instance

        Returns:
            True if mouse is over the instance
        """
        mx, my = pos
        x, y = instance.x, instance.y
        w = instance._cached_width
        h = instance._cached_height
        return x <= mx < x + w and y <= my < y + h

    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion event.

        Args:
            pos: Mouse position (x, y)
        """
        self.mouse_x, self.mouse_y = pos

    def _get_key_name(self, key: int) -> Optional[str]:
        """Map pygame key code to key name string.

        Args:
            key: Pygame key code

        Returns:
            Key name string or None if not recognized
        """
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
