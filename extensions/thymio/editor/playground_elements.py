#!/usr/bin/env python3
"""
Playground element classes for the Playground Editor.
Represents walls and robots placed in an Aseba playground.
"""

import uuid


class PlaygroundWall:
    """Represents a wall in an Aseba playground"""

    def __init__(self, x=0, y=0, l1=50, l2=5, h=10,
                 color="wall", angle=0.0, mass=None, element_id=None):
        self.element_id = element_id or uuid.uuid4().hex[:8]
        self.x = x          # Center x position
        self.y = y          # Center y position
        self.l1 = l1         # Length (along main axis)
        self.l2 = l2         # Thickness (perpendicular)
        self.h = h           # Height (3D, for simulator)
        self.color = color   # Named color reference
        self.angle = angle   # Rotation in radians
        self.mass = mass     # None = static, float = pushable

    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'id': self.element_id,
            'x': self.x,
            'y': self.y,
            'l1': self.l1,
            'l2': self.l2,
            'h': self.h,
            'color': self.color,
            'angle': self.angle,
            'mass': self.mass,
        }

    @classmethod
    def from_dict(cls, data):
        """Create wall from dictionary"""
        return cls(
            x=data.get('x', 0),
            y=data.get('y', 0),
            l1=data.get('l1', 50),
            l2=data.get('l2', 5),
            h=data.get('h', 10),
            color=data.get('color', 'wall'),
            angle=data.get('angle', 0.0),
            mass=data.get('mass'),
            element_id=data.get('id'),
        )


class PlaygroundRobot:
    """Represents a robot in an Aseba playground"""

    VALID_TYPES = ('thymio2', 'e-puck')

    def __init__(self, robot_type="thymio2", x=0, y=0,
                 port=33333, angle=0.0, name="Thymio",
                 linked_object="", element_id=None):
        self.element_id = element_id or uuid.uuid4().hex[:8]
        self.robot_type = robot_type  # "thymio2" or "e-puck"
        self.x = x
        self.y = y
        self.port = port
        self.angle = angle    # Rotation in radians
        self.name = name
        self.linked_object = linked_object  # Name of the pygm2 Thymio object to run

    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'id': self.element_id,
            'type': self.robot_type,
            'x': self.x,
            'y': self.y,
            'port': self.port,
            'angle': self.angle,
            'name': self.name,
            'linked_object': self.linked_object,
        }

    @classmethod
    def from_dict(cls, data):
        """Create robot from dictionary"""
        return cls(
            robot_type=data.get('type', 'thymio2'),
            x=data.get('x', 0),
            y=data.get('y', 0),
            port=data.get('port', 33333),
            angle=data.get('angle', 0.0),
            name=data.get('name', 'Thymio'),
            linked_object=data.get('linked_object', ''),
            element_id=data.get('id'),
        )
