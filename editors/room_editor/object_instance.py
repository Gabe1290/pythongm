#!/usr/bin/env python3
"""
Object Instance class for Room Editor
Represents an instance of an object placed in a room
"""


class ObjectInstance:
    """Represents an instance of an object placed in a room"""

    def __init__(self, object_name, x=0, y=0, instance_id=None):
        self.object_name = object_name
        self.x = x
        self.y = y
        self.instance_id = instance_id or id(self)
        self.rotation = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.visible = True

    def to_dict(self):
        """Convert instance to dictionary for saving"""
        return {
            'object_name': self.object_name,
            'x': self.x,
            'y': self.y,
            'instance_id': self.instance_id,
            'rotation': self.rotation,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y,
            'visible': self.visible
        }

    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        # Support both 'object' and 'object_name' keys for compatibility
        object_name = data.get('object') or data.get('object_name')
        instance = cls(
            object_name,
            data['x'],
            data['y'],
            data.get('instance_id')
        )
        instance.rotation = data.get('rotation', 0)
        instance.scale_x = data.get('scale_x', 1.0)
        instance.scale_y = data.get('scale_y', 1.0)
        instance.visible = data.get('visible', True)
        return instance
