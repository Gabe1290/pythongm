#!/usr/bin/env python3
"""
Action Parameters Formatter
Formats action parameters for display in the events tree
"""


try:
    from PySide6.QtCore import QCoreApplication as _Qt
except Exception:                                       # no Qt: the English text as is
    class _Qt:
        @staticmethod
        def translate(_context, text):
            return text
# Fixed summary words go through _Qt.translate("ActionParametersFormatter", "...") with literal
# arguments, the shape scripts/i18n_catchup.py collects into the catalogues.


def _language():
    try:
        from core.language_manager import get_language_manager
        return get_language_manager().get_current_language() or "en"
    except Exception:
        return "en"


def _labels(action_name, lang):
    """{param key: label in the IDE language}, for a non-English IDE (docs/OPEN_WORK_2026-11-22.md U1).
    English keeps the parameter keys, exactly as before."""
    if lang == "en":
        return {}
    try:
        from events.action_types import get_action_type
        from core.ui_names import param_label
        action = get_action_type(action_name)
        return {p.name: param_label(p, lang=lang) for p in (action.parameters if action else [])}
    except Exception:
        return {}


def _value(value, lang):
    """A drop-down word ("right", "solid") in the IDE language; anything else unchanged."""
    if lang == "en" or not isinstance(value, str):
        return value
    from core.ui_names import choice_label
    return choice_label(value, lang=lang)


class ActionParametersFormatter:
    """Formats action parameters for display"""

    @staticmethod
    def format_action_parameters(action_name: str, params: dict) -> str:
        """Format action parameters for display with smart prioritization"""
        lang = _language()

        # Special formatting for if_collision_at
        if action_name == "if_collision_at":
            parts = []

            # Show object type FIRST (most important)
            object_type = params.get("object_type", params.get("object_types", "any"))
            if isinstance(object_type, list):
                object_type = ", ".join(object_type)
            parts.append(_Qt.translate("ActionParametersFormatter", "with: {0}").format(_value(object_type, lang)))

            # Show position (x, y)
            x = params.get("x", "")
            y = params.get("y", "")
            if x or y:
                # Simplify common expressions
                x_simple = x.replace("self.x + 32", "→").replace("self.x - 32", "←").replace("self.x", "•")
                y_simple = y.replace("self.y + 32", "↓").replace("self.y - 32", "↑").replace("self.y", "•")
                parts.append(_Qt.translate("ActionParametersFormatter", "at: ({0}, {1})").format(x_simple, y_simple))

            # Show action counts
            then_actions = params.get("then_actions", [])
            else_actions = params.get("else_actions", [])
            if then_actions or else_actions:
                parts.append(_Qt.translate("ActionParametersFormatter", "then: {0}, else: {1}").format(len(then_actions), len(else_actions)))

            return " | ".join(parts)

        # Special formatting for if_can_push (Sokoban-style)
        elif action_name == "if_can_push":
            obj_type = params.get("object_type", "box")
            then_act = params.get("then_action", "push_and_move")
            else_act = params.get("else_action", "stop_movement")
            return _Qt.translate("ActionParametersFormatter", "push {0}? then: {1}, else: {2}").format(_value(obj_type, lang), _value(then_act, lang),
                                                               _value(else_act, lang))

        # Special formatting for push_object
        elif action_name == "push_object":
            parts = []

            target = params.get("target", "other")
            if target != "self":
                parts.append(_Qt.translate("ActionParametersFormatter", "target: {0}").format(_value(target, lang)))

            direction = params.get("direction", "")
            if direction:
                direction_icons = {"right": "→", "left": "←", "up": "↑", "down": "↓"}
                parts.append(direction_icons.get(direction, direction))

            distance = params.get("distance", "")
            if distance:
                parts.append(f"{distance}px")

            check_collision = params.get("check_collision", True)
            if not check_collision:
                parts.append(_Qt.translate("ActionParametersFormatter", "no check"))

            return " ".join(parts)

        # Special formatting for move_to_position
        elif action_name == "move_to_position":
            parts = []

            x = params.get("x", "")
            y = params.get("y", "")
            if x or y:
                # Simplify expressions
                x_simple = x.replace("self.x + 32", "→").replace("self.x - 32", "←").replace("self.x", "•")
                y_simple = y.replace("self.y + 32", "↓").replace("self.y - 32", "↑").replace("self.y", "•")
                parts.append(_Qt.translate("ActionParametersFormatter", "to: ({0}, {1})").format(x_simple, y_simple))

            smooth = params.get("smooth", False)
            if smooth:
                parts.append(_Qt.translate("ActionParametersFormatter", "smooth"))

            return " ".join(parts)

        # Special formatting for move_grid
        elif action_name == "move_grid":
            direction = params.get("direction", "")
            grid_size = params.get("grid_size", 32)

            direction_icons = {"right": "→", "left": "←", "up": "↑", "down": "↓"}
            icon = direction_icons.get(direction, direction)

            return f"{icon} {grid_size}px"

        # Special formatting for transform_to
        elif action_name == "transform_to":
            object_name = params.get("object_name", "")
            return f"→ {object_name}"

        # Default: show all parameters (but with more space)
        else:
            param_list = []
            labels = _labels(action_name, lang)
            for k, v in params.items():
                # Skip verbose parameters
                if k in ["then_actions", "else_actions", "then_action_params", "else_action_params"]:
                    continue
                # Skip translation dicts (shown as indicator instead)
                if k.endswith("_translations") and isinstance(v, dict):
                    continue

                # Shorten long values
                if isinstance(v, str) and len(v) > 20:
                    v = v[:17] + "..."

                param_list.append(f"{labels.get(k, k)}={_value(v, lang)}")

            # Show a compact indicator if translations exist
            translations = params.get("message_translations")
            if translations and isinstance(translations, dict):
                n = len(translations)
                param_list.append((_Qt.translate("ActionParametersFormatter", "[{0} translation]") if n == 1 else _Qt.translate("ActionParametersFormatter", "[{0} translations]")).format(n))

            summary = ", ".join(param_list)

            # Allow up to 80 characters instead of 30
            max_length = 80
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."

            return summary
