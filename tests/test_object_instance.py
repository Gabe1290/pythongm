#!/usr/bin/env python3
"""Tests for room-editor ObjectInstance serialization.

Regression: a placed instance with no stored id used to fall back to id(self)
(a memory address), which got baked into the saved room JSON as a huge,
non-deterministic number — churning the diff on every re-save. The id is dead
metadata (read nowhere for logic), so it's now simply omitted when absent.
"""

from editors.room_editor.object_instance import ObjectInstance


class TestObjectInstanceSerialization:
    def test_new_instance_omits_instance_id(self):
        inst = ObjectInstance('obj_wall', 32, 64)
        assert inst.instance_id is None
        data = inst.to_dict()
        assert 'instance_id' not in data  # no ephemeral memory-address id
        assert data['object_name'] == 'obj_wall'
        assert (data['x'], data['y']) == (32, 64)
        # The rest of the schema is unchanged.
        assert data['rotation'] == 0
        assert data['scale_x'] == 1.0 and data['scale_y'] == 1.0
        assert data['visible'] is True

    def test_explicit_instance_id_round_trips(self):
        inst = ObjectInstance.from_dict(
            {'object_name': 'obj_x', 'x': 1, 'y': 2, 'instance_id': 5})
        assert inst.instance_id == 5
        out = inst.to_dict()
        assert out['instance_id'] == 5
        # Position in the dict is preserved (after y, before rotation).
        keys = list(out.keys())
        assert keys.index('instance_id') == keys.index('y') + 1
        assert keys.index('instance_id') == keys.index('rotation') - 1

    def test_shorthand_object_key_without_id_stays_clean(self):
        # Legacy rooms store instances as {"object": ..., "x": .., "y": ..}.
        inst = ObjectInstance.from_dict({'object': 'obj_wall', 'x': 0, 'y': 0})
        data = inst.to_dict()
        assert data['object_name'] == 'obj_wall'
        assert 'instance_id' not in data

    def test_two_new_instances_are_both_id_free(self):
        # Two distinct instances no longer carry distinct memory-address ids.
        a = ObjectInstance('obj_wall', 0, 0).to_dict()
        b = ObjectInstance('obj_wall', 32, 0).to_dict()
        assert 'instance_id' not in a and 'instance_id' not in b
