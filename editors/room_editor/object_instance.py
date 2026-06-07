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
        # Carry only an explicitly-provided id. This used to fall back to
        # id(self) — a Python memory address — which got baked into the saved
        # room JSON as a huge, non-deterministic number, churning the diff on
        # every re-save. The persisted instance_id is never read for any logic
        # (the runtime keys its spatial grid off the live id(instance), and
        # runtime-created instances synthesise their own), so leaving it unset
        # and omitting it from to_dict is safe and keeps room files clean.
        self.instance_id = instance_id
        self.rotation = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.visible = True

    def to_dict(self):
        """Convert instance to dictionary for saving"""
        data = {
            'object_name': self.object_name,
            'x': self.x,
            'y': self.y,
        }
        # Only persist a real, explicitly-provided id — never an auto memory
        # address. Kept in its historical position (after y) when present.
        if self.instance_id is not None:
            data['instance_id'] = self.instance_id
        data['rotation'] = self.rotation
        data['scale_x'] = self.scale_x
        data['scale_y'] = self.scale_y
        data['visible'] = self.visible
        return data

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
