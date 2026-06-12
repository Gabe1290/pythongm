#!/usr/bin/env python3
"""Tests for the shared room/object file-merge kernel.

Regression (audit H12): the GMK converter writes a room's tile layers,
parallax backgrounds, views and creation code only to rooms/<name>.json, but
the merge whitelist copied none of them — so they never reached memory on load
and were erased from the room file on the next save. Every key the runtime
reads must round-trip through merge_room_file.
"""

from utils.project_file_merge import merge_room_file, merge_object_file


HEAVY_KEYS = [
    'tiles', 'backgrounds', 'views_enabled', 'enable_views', 'views',
    'bg_hspeed', 'bg_vspeed', 'bg_stretch', 'persistent', 'creation_code',
]


class TestMergeRoomFile:
    def test_heavy_payload_keys_propagate(self):
        # Metadata-only project.json entry (what the GMK converter returns).
        room_data = {'width': 640, 'height': 480, 'instances': []}
        # The room file carries the real payload.
        file_room_data = {
            'instances': [{'object_name': 'o', 'x': 0, 'y': 0}],
            'width': 640, 'height': 480,
            'tiles': [{'background': 'bg', 'x': 0, 'y': 0}],
            'backgrounds': [{'background_image': 'sky'}] + [{}] * 7,
            'views_enabled': True,
            'views': {'0': {'visible': True}},
            'bg_hspeed': 1.5, 'bg_vspeed': -2.0, 'bg_stretch': False,
            'persistent': True,
            'creation_code': 'self.x = 1',
        }
        count = merge_room_file(room_data, file_room_data)
        assert count == 1
        for key in ['tiles', 'backgrounds', 'views_enabled', 'views',
                    'bg_hspeed', 'bg_vspeed', 'bg_stretch', 'persistent',
                    'creation_code']:
            assert room_data[key] == file_room_data[key], f"{key} not merged"

    def test_save_after_load_preserves_payload(self):
        # Simulate load (merge file -> memory) then save (memory -> file).
        # Before the fix the merged dict lacked tiles, so the rewrite erased it.
        project_entry = {'width': 320, 'height': 240, 'instances': []}
        on_disk = {
            'instances': [], 'width': 320, 'height': 240,
            'tiles': [{'x': 32, 'y': 32}], 'creation_code': 'pass',
        }
        merge_room_file(project_entry, on_disk)  # load
        # project_entry is what _save_rooms_to_files would write back.
        assert project_entry['tiles'] == [{'x': 32, 'y': 32}]
        assert project_entry['creation_code'] == 'pass'

    def test_absent_keys_are_not_invented(self):
        room_data = {'width': 100, 'height': 100}
        merge_room_file(room_data, {'width': 100, 'height': 100})
        for key in HEAVY_KEYS:
            assert key not in room_data

    def test_instances_precedence_unchanged(self):
        room_data = {'instances': [{'a': 1}]}
        count = merge_room_file(room_data, {'instances': [{'b': 2}, {'c': 3}]})
        assert count == 2
        assert room_data['instances'] == [{'b': 2}, {'c': 3}]


class TestMergeObjectFile:
    def test_events_and_props_merge(self):
        obj = {}
        n = merge_object_file(obj, {'events': {'create': {}}, 'sprite': 'spr'})
        assert n == 1
        assert obj['sprite'] == 'spr'
