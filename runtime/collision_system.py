#!/usr/bin/env python3
"""
Collision Detection System

This module provides collision detection functionality for the game runtime.
It's designed as a mixin class that GameRunner can inherit from to keep
collision-related code organized separately.
"""

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from core.logger import get_logger

if TYPE_CHECKING:
    from runtime.game_runner import GameInstance, GameRoom

logger = get_logger(__name__)

# Type aliases
Instance = Any
ObjectsData = Dict[str, Dict[str, Any]]


class CollisionMixin:
    """Mixin providing collision detection methods for GameRunner.

    This class should be inherited by GameRunner to provide collision
    detection functionality. It expects the following attributes:
    - current_room: GameRoom with instances and spatial grid
    - action_executor: ActionExecutor instance
    """

    # These will be set by the inheriting class
    current_room: Optional['GameRoom']
    action_executor: Any

    def check_movement_collision(self, moving_instance: Instance, objects_data: ObjectsData) -> bool:
        """Check if intended movement would be blocked by solid objects.

        Only solid objects block movement. Non-solid objects don't block -
        they rely on collision events to handle interactions.

        Args:
            moving_instance: Instance attempting to move
            objects_data: Dictionary of object definitions

        Returns:
            True if movement is allowed, False if blocked
        """
        can_move, _ = self.check_movement_collision_with_blocker(moving_instance, objects_data)
        return can_move

    def check_movement_collision_with_blocker(
        self, moving_instance: Instance, objects_data: ObjectsData
    ) -> Tuple[bool, Optional[Instance]]:
        """Check if intended movement would be blocked by solid objects.

        Args:
            moving_instance: Instance attempting to move
            objects_data: Dictionary of object definitions

        Returns:
            Tuple of (can_move, blocking_instance or None)
        """
        intended_x = moving_instance.intended_x
        intended_y = moving_instance.intended_y

        w1 = moving_instance._cached_width
        h1 = moving_instance._cached_height

        nearby_instances = self.current_room.get_nearby_instances(intended_x, intended_y, w1, h1)

        for other_instance in nearby_instances:
            if other_instance == moving_instance:
                continue

            other_obj_data = other_instance._cached_object_data
            if not other_obj_data:
                other_obj_data = objects_data.get(other_instance.object_name, {})

            is_solid = other_obj_data.get('solid', False)
            if not is_solid:
                continue

            w2 = other_instance._cached_width
            h2 = other_instance._cached_height

            if self.rectangles_overlap(intended_x, intended_y, w1, h1,
                                       other_instance.x, other_instance.y, w2, h2):
                return (False, other_instance)

        return (True, None)

    def instances_overlap(self, inst1: Instance, inst2: Instance) -> bool:
        """Check if two instances overlap using their bounding boxes.

        Args:
            inst1: First instance
            inst2: Second instance

        Returns:
            True if the instances overlap
        """
        w1 = inst1._cached_width
        h1 = inst1._cached_height
        w2 = inst2._cached_width
        h2 = inst2._cached_height

        return self.rectangles_overlap(inst1.x, inst1.y, w1, h1, inst2.x, inst2.y, w2, h2)

    def rectangles_overlap(
        self, x1: float, y1: float, w1: int, h1: int,
        x2: float, y2: float, w2: int, h2: int
    ) -> bool:
        """Check if two rectangles overlap.

        Args:
            x1, y1, w1, h1: First rectangle (position and size)
            x2, y2, w2, h2: Second rectangle (position and size)

        Returns:
            True if rectangles overlap
        """
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    def check_collision_at_position(
        self, instance: Instance, check_x: float, check_y: float,
        object_type: str = "any", exclude_instance: Optional[Instance] = None
    ) -> bool:
        """Check if there would be a collision at a given position.

        Used by conditional actions like if_collision.

        Args:
            instance: The instance to check collision for
            check_x: X position to check
            check_y: Y position to check
            object_type: Type of object to check against ("any", "solid", or object name)
            exclude_instance: Instance to exclude from collision check

        Returns:
            True if collision detected
        """
        if not self.current_room:
            return False

        w1 = instance._cached_width
        h1 = instance._cached_height

        nearby_instances = self.current_room.get_nearby_instances(check_x, check_y, w1, h1)

        for other_instance in nearby_instances:
            if other_instance == instance:
                continue
            if exclude_instance and other_instance == exclude_instance:
                continue

            w2 = other_instance._cached_width
            h2 = other_instance._cached_height

            if not self.rectangles_overlap(check_x, check_y, w1, h1,
                                          other_instance.x, other_instance.y, w2, h2):
                continue

            # Check object type filter
            if object_type == "any":
                return True
            elif object_type == "solid":
                other_obj_data = other_instance._cached_object_data or {}
                if other_obj_data.get('solid', False):
                    return True
            elif other_instance.object_name == object_type:
                return True

        return False

    def detect_collisions_for_instance(
        self, instance: Instance, objects_data: ObjectsData
    ) -> List[Dict[str, Any]]:
        """Detect all collision events for a single instance.

        Args:
            instance: Instance to check collisions for
            objects_data: Dictionary of object definitions

        Returns:
            List of collision data dictionaries
        """
        collisions = []

        collision_targets = instance._collision_targets
        if not collision_targets:
            return collisions

        w1 = instance._cached_width
        h1 = instance._cached_height

        nearby_instances = self.current_room.get_nearby_instances(instance.x, instance.y, w1, h1)

        for other_instance in nearby_instances:
            if other_instance == instance:
                continue

            if other_instance.object_name not in collision_targets:
                continue

            w2 = other_instance._cached_width
            h2 = other_instance._cached_height

            if self.rectangles_overlap(instance.x, instance.y, w1, h1,
                                       other_instance.x, other_instance.y, w2, h2):
                event_name = f"collision_with_{other_instance.object_name}"
                collisions.append({
                    'instance': instance,
                    'other': other_instance,
                    'event_name': event_name,
                    'self_hspeed': instance.hspeed,
                    'self_vspeed': instance.vspeed,
                    'other_hspeed': other_instance.hspeed,
                    'other_vspeed': other_instance.vspeed,
                })

        return collisions

    def process_collision_event(self, collision_data: Dict[str, Any]) -> None:
        """Process a single collision event.

        Args:
            collision_data: Dictionary with collision information
        """
        instance = collision_data['instance']
        other = collision_data['other']
        event_name = collision_data['event_name']

        if not instance.object_data or "events" not in instance.object_data:
            return

        collision_speeds = {
            'self_hspeed': collision_data['self_hspeed'],
            'self_vspeed': collision_data['self_vspeed'],
            'other_hspeed': collision_data['other_hspeed'],
            'other_vspeed': collision_data['other_vspeed'],
        }

        self.action_executor.execute_collision_event(
            instance, event_name, instance.object_data["events"],
            other, collision_speeds
        )


def get_bounding_box(instance: Instance) -> Tuple[float, float, int, int]:
    """Get the bounding box for an instance.

    Args:
        instance: Game instance

    Returns:
        Tuple of (x, y, width, height)
    """
    return (
        instance.x,
        instance.y,
        instance._cached_width,
        instance._cached_height
    )


def boxes_overlap(box1: Tuple[float, float, int, int],
                  box2: Tuple[float, float, int, int]) -> bool:
    """Check if two bounding boxes overlap.

    Args:
        box1: First bounding box (x, y, width, height)
        box2: Second bounding box (x, y, width, height)

    Returns:
        True if boxes overlap
    """
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
