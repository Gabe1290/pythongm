#!/usr/bin/env python3
"""
Action Parameters Formatter
Formats action parameters for display in the events tree
"""


class ActionParametersFormatter:
    """Formats action parameters for display"""

    @staticmethod
    def format_action_parameters(action_name: str, params: dict) -> str:
        """Format action parameters for display with smart prioritization"""

        # Special formatting for if_collision_at
        if action_name == "if_collision_at":
            parts = []

            # Show object type FIRST (most important)
            object_type = params.get("object_type", params.get("object_types", "any"))
            if isinstance(object_type, list):
                object_type = ", ".join(object_type)
            parts.append(f"with: {object_type}")

            # Show position (x, y)
            x = params.get("x", "")
            y = params.get("y", "")
            if x or y:
                # Simplify common expressions
                x_simple = x.replace("self.x + 32", "→").replace("self.x - 32", "←").replace("self.x", "•")
                y_simple = y.replace("self.y + 32", "↓").replace("self.y - 32", "↑").replace("self.y", "•")
                parts.append(f"at: ({x_simple}, {y_simple})")

            # Show action counts
            then_actions = params.get("then_actions", [])
            else_actions = params.get("else_actions", [])
            if then_actions or else_actions:
                parts.append(f"then: {len(then_actions)}, else: {len(else_actions)}")

            return " | ".join(parts)

        # Special formatting for push_object
        elif action_name == "push_object":
            parts = []

            target = params.get("target", "other")
            if target != "self":
                parts.append(f"target: {target}")

            direction = params.get("direction", "")
            if direction:
                direction_icons = {"right": "→", "left": "←", "up": "↑", "down": "↓"}
                parts.append(direction_icons.get(direction, direction))

            distance = params.get("distance", "")
            if distance:
                parts.append(f"{distance}px")

            check_collision = params.get("check_collision", True)
            if not check_collision:
                parts.append("no check")

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
                parts.append(f"to: ({x_simple}, {y_simple})")

            smooth = params.get("smooth", False)
            if smooth:
                parts.append("smooth")

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
            for k, v in params.items():
                # Skip verbose parameters
                if k in ["then_actions", "else_actions", "then_action_params", "else_action_params"]:
                    continue

                # Shorten long values
                if isinstance(v, str) and len(v) > 20:
                    v = v[:17] + "..."

                param_list.append(f"{k}={v}")

            summary = ", ".join(param_list)

            # Allow up to 80 characters instead of 30
            max_length = 80
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."

            return summary
