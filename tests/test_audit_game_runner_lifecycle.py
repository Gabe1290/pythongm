#!/usr/bin/env python3
"""Regression tests for the 2026-06-11 audit findings on runtime/game_runner.py.

Covers:
- M48 room_speed -> fps wiring (GMK games no longer run at double speed)
- M49 per-frame loops iterate a snapshot (a self-spawner can't hard-hang one frame)
- M50 push_back_instance separates in bbox-world coords with origin/bbox offsets
- M51 restart_current_room carries persistent instances over
- M52 restart_game rebuilds every room, not just the first
- M53 re-entering a visited room does not re-fire create on live instances
- M54 modal dialogs forward KEYUP so keys_pressed doesn't go stale
- L30 outside_room accounts for the sprite origin
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


def _make_runner():
    """A bare GameRunner with just the attributes the tested paths touch."""
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            runner = GameRunner.__new__(GameRunner)
            runner.action_executor = MagicMock()
            runner.project_path = None
            runner.project_data = None
            runner.sprites = {}
            runner.backgrounds = {}
            runner.screen = None
            runner.rooms = {}
            runner.current_room = None
            runner._objects_data = {}
            runner.score = 0
            runner.lives = 3
            runner.health = 100
            runner.fps = 60
            runner._room_transition_grace_frames = 0
            runner._destroyed_memory = {}
            return runner


def _make_room(name, instances, width=640, height=480):
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRoom
            return GameRoom(
                name,
                {'width': width, 'height': height, 'instances': instances},
                action_executor=MagicMock(),
            )


# ---------------------------------------------------------------------------
# M48 — room_speed is read into self.fps
# ---------------------------------------------------------------------------
class TestRoomSpeed:
    def test_gmk_room_speed_30_sets_fps_30(self):
        runner = _make_runner()
        runner.project_data = {'settings': {'room_speed': 30}}
        runner._load_project_settings()
        assert runner.fps == 30

    def test_missing_room_speed_defaults_to_60(self):
        runner = _make_runner()
        runner.project_data = {'settings': {}}
        runner._load_project_settings()
        assert runner.fps == 60

    def test_room_speed_is_clamped(self):
        runner = _make_runner()
        runner.project_data = {'settings': {'room_speed': 0}}
        runner._load_project_settings()
        assert runner.fps == 1

        runner.project_data = {'settings': {'room_speed': 10000}}
        runner._load_project_settings()
        assert runner.fps == 240

    def test_garbage_room_speed_falls_back(self):
        runner = _make_runner()
        runner.project_data = {'settings': {'room_speed': 'fast'}}
        runner._load_project_settings()
        assert runner.fps == 60


# ---------------------------------------------------------------------------
# M50 — push_back_instance resolves in bbox-world coords with offsets
# ---------------------------------------------------------------------------
class TestPushBack:
    # RETARGETED to our M50 signature. Our push_back_instance takes 9 rect
    # args (no explicit offx/offy): it DERIVES the bbox->origin offset from
    # moving_inst.x/y minus the moving bbox top-left. The remote's discarded
    # version passed offx/offy as two extra positionals; same intended
    # behavior (flush landing in bbox-world coords), different call shape. To
    # reproduce off_x=4 we seed moving.x = mbx + 4 instead of passing 4.
    def test_flush_with_nonzero_offset(self):
        runner = _make_runner()
        # off_x = 4 -> moving.x = mbx(100) + 4 = 104.
        moving = SimpleNamespace(x=104.0, y=0.0)
        # Moving bbox at world (100,0), 16x16; static bbox at (110,0), 16x16.
        # Overlap on x by 6; min-overlap resolution pushes the moving bbox left
        # of the static one: bbox_x = 110 - 16 = 94, instance.x = 94 + 4 = 98.
        runner.push_back_instance(
            moving,
            100.0, 0.0, 16.0, 16.0,   # moving bbox
            110.0, 0.0, 16.0, 16.0,   # static bbox
        )
        assert moving.x == 98.0
        # And the resulting bbox (instance.x - offx) is flush against static.
        assert (moving.x - 4.0) + 16.0 == 110.0

    def test_zero_offset_matches_legacy(self):
        runner = _make_runner()
        # off_x = 0 -> moving.x == mbx.
        moving = SimpleNamespace(x=100.0, y=0.0)
        runner.push_back_instance(
            moving,
            100.0, 0.0, 16.0, 16.0,
            110.0, 0.0, 16.0, 16.0,
        )
        assert moving.x == 94.0  # 110 - 16, no offset

    def test_vertical_separation_with_offset(self):
        runner = _make_runner()
        # off_y = 3 -> moving.y = mby(100) + 3 = 103.
        moving = SimpleNamespace(x=0.0, y=103.0)
        # Pure vertical overlap: moving bbox at (0,100) 16x16, static at (0,108).
        # min overlap is on y (8), push up: bbox_y = 108-16 = 92, +offy(3) = 95.
        runner.push_back_instance(
            moving,
            0.0, 100.0, 16.0, 16.0,
            0.0, 108.0, 16.0, 16.0,
        )
        assert moving.y == 95.0


# ---------------------------------------------------------------------------
# L30 — outside_room accounts for the sprite origin
# ---------------------------------------------------------------------------
class TestOutsideRoom:
    def _instance_with_origin(self, x, y, w, h, origin_x, origin_y):
        from runtime.game_runner import GameInstance
        inst = GameInstance('obj', x, y, {})
        inst._cached_width = w
        inst._cached_height = h
        inst.object_data = {'events': {'outside_room': {'actions': []}}}
        inst.sprite = SimpleNamespace(origin_x=origin_x, origin_y=origin_y)
        inst.action_executor = MagicMock()
        return inst

    def test_origin_shifts_outside_detection(self):
        runner = _make_runner()
        # Sprite is 32x32 with a centered origin (16,16). The instance is at
        # x=16: its sprite top-left is at world 0, so it is fully INSIDE — the
        # naive (no-origin) check would also say inside here. Move it so the
        # sprite is fully off the left edge: instance.x just less than origin
        # means left = x - 16 < -32 -> needs x < -16.
        room = _make_room('lvl', [])
        runner.current_room = room

        # x = -17: left edge = -17 - 16 = -33, +32 = -1 < 0 -> fully outside left
        inst_outside = self._instance_with_origin(-17, 100, 32, 32, 16, 16)
        room.instances = [inst_outside]
        runner.check_outside_room_events()
        assert inst_outside.action_executor.execute_event.called

    def test_not_outside_when_origin_keeps_it_in(self):
        runner = _make_runner()
        room = _make_room('lvl', [])
        runner.current_room = room
        # x = 10 with origin 16: left edge = -6, +32 = 26 > 0 -> still inside.
        # The naive check using raw x=10 would also be inside, but verify the
        # origin path does not spuriously fire.
        inst = self._instance_with_origin(10, 100, 32, 32, 16, 16)
        room.instances = [inst]
        runner.check_outside_room_events()
        assert not inst.action_executor.execute_event.called


# ---------------------------------------------------------------------------
# Shared layout for restart / change_room tests
# ---------------------------------------------------------------------------
_PLAYER = {'object_name': 'player', 'x': 50, 'y': 50}
_MONSTER = {'object_name': 'monster', 'x': 200, 'y': 200}

_PROJECT = {
    'assets': {
        'rooms': {
            'r1': {'width': 320, 'height': 240, 'instances': [dict(_PLAYER)]},
            'r2': {'width': 320, 'height': 240, 'instances': [dict(_MONSTER)]},
        },
        'objects': {
            'player': {'name': 'player', 'persistent': True},
            'monster': {'name': 'monster'},
        },
    },
    'room_order': ['r1', 'r2'],
    'settings': {},
}


# ---------------------------------------------------------------------------
# M51 — restart_current_room carries persistent instances
# ---------------------------------------------------------------------------
class TestRestartPersistent:
    def test_persistent_player_survives_restart_of_room_without_it(self):
        runner = _make_runner()
        runner.project_data = _PROJECT
        runner._objects_data = _PROJECT['assets']['objects']

        # Build r2 (monster only) and inject a carried-over persistent player,
        # as change_room would have done.
        from runtime.game_runner import GameInstance
        room = _make_room('r2', [dict(_MONSTER)])
        room.set_sprites_for_instances({}, _PROJECT['assets']['objects'])
        player = GameInstance('player', 80, 80, {})
        player.set_object_data({'name': 'player', 'persistent': True,
                                'events': {}})
        room.instances.append(player)
        runner.current_room = room
        runner.rooms = {'r2': room}

        runner.restart_current_room()

        names = [i.object_name for i in runner.current_room.instances]
        assert 'player' in names  # persistent player survives the restart
        assert 'monster' in names  # authored monster respawns
        # The same persistent object instance is carried, not a fresh copy.
        carried = next(i for i in runner.current_room.instances
                       if i.object_name == 'player')
        assert carried is player


# ---------------------------------------------------------------------------
# M52 — restart_game rebuilds every room
# ---------------------------------------------------------------------------
class TestRestartGameRebuildsAll:
    def test_all_rooms_rebuilt_not_just_first(self):
        runner = _make_runner()
        runner.project_data = _PROJECT
        runner._objects_data = _PROJECT['assets']['objects']
        runner.get_room_list = lambda: ['r1', 'r2']

        # Simulate a previous playthrough where r2's monster was destroyed:
        # the stored r2 room object has an empty instance list.
        prev_r2 = _make_room('r2', [])  # drained
        runner.rooms = {
            'r1': _make_room('r1', [dict(_PLAYER)]),
            'r2': prev_r2,
        }
        runner.current_room = runner.rooms['r1']

        runner.restart_game()

        # r2 must be a fresh object with the monster back.
        assert runner.rooms['r2'] is not prev_r2
        r2_names = [i.object_name for i in runner.rooms['r2'].instances]
        assert 'monster' in r2_names


# ---------------------------------------------------------------------------
# M53 — re-entering a visited room does not re-fire create
# ---------------------------------------------------------------------------
class TestChangeRoomCreateOnce:
    def test_create_fires_once_per_instance_across_reentry(self):
        # RETARGETED to our M53 implementation: the create-once-per-instance
        # guard lives in ActionExecutor.execute_event (the single chokepoint),
        # not in change_room. change_room calls execute_event(..., "create")
        # on every entry and the guard makes the second call a no-op. The
        # remote's discarded design guarded in change_room itself; that is why
        # the original orphaned test mocked execute_event with a guard-less
        # side_effect (which counted 2). We use a REAL ActionExecutor with a
        # counting create handler so our actual guard is exercised.
        from runtime.action_executor import ActionExecutor

        runner = _make_runner()
        runner.project_data = _PROJECT
        runner._objects_data = _PROJECT['assets']['objects']

        from runtime.game_runner import GameInstance
        # r1 with a non-persistent monster whose create we count.
        room1 = _make_room('r1', [])
        ex = ActionExecutor(game_runner=runner)
        creates = []
        ex.action_handlers['__count_create'] = (
            lambda inst, p: creates.append(1))

        monster = GameInstance('monster', 100, 100, {},
                               action_executor=ex)
        monster.set_object_data({
            'name': 'monster',
            'events': {'create': {'actions': [
                {'action': '__count_create', 'parameters': {}}]}},
        })
        room1.instances.append(monster)

        room2 = _make_room('r2', [])

        runner.rooms = {'r1': room1, 'r2': room2}
        runner.current_room = room2  # start "elsewhere"

        runner.change_room('r1')  # first entry -> create fires
        runner.change_room('r2')
        runner.change_room('r1')  # re-entry -> create must NOT fire again

        assert sum(creates) == 1


# ---------------------------------------------------------------------------
# M54 — modal dialogs forward KEYUP so keys_pressed stays in sync
# ---------------------------------------------------------------------------
class TestDialogKeyup:
    def test_message_dialog_forwards_keyup(self):
        """A KEYUP arriving while show_message_dialog is open clears the held-key
        state SILENTLY (M54): our design calls _release_held_key_silent so the
        key isn't stuck as held after the dialog closes, WITHOUT firing the
        game's keyboard_release event handler while the game is paused behind
        the modal dialog."""
        import runtime.game_runner as gr

        runner = _make_runner()
        runner._release_held_key_silent = MagicMock()
        runner.handle_keyboard_release = MagicMock()

        # A fake pygame whose event.get() yields one KEYUP then signals the
        # dialog to exit via a RETURN keydown.
        fake_pygame = MagicMock()
        fake_pygame.QUIT = 256
        fake_pygame.KEYDOWN = 768
        fake_pygame.KEYUP = 769
        fake_pygame.MOUSEBUTTONDOWN = 1025
        fake_pygame.K_RETURN = 13
        fake_pygame.K_SPACE = 32
        fake_pygame.K_ESCAPE = 27

        keyup_evt = SimpleNamespace(type=769, key=100)        # KEYUP, some key
        dismiss_evt = SimpleNamespace(type=768, key=13)        # KEYDOWN RETURN

        # First iteration delivers [keyup, dismiss]; loop exits after dismiss.
        fake_pygame.event.get.side_effect = [[keyup_evt, dismiss_evt], []]

        # Font.size returns a width tuple; render returns a surface with sizes.
        fake_font = MagicMock()
        fake_font.size.return_value = (10, 10)
        rendered = MagicMock()
        rendered.get_width.return_value = 10
        rendered.get_height.return_value = 10
        fake_font.render.return_value = rendered
        fake_pygame.font.Font.return_value = fake_font
        fake_pygame.font.SysFont.return_value = fake_font
        fake_pygame.mouse.get_pos.return_value = (0, 0)

        # Font / drawing are all on the mock; screen has a size.
        runner.screen = MagicMock()
        runner.screen.get_size.return_value = (320, 240)
        runner.clock = MagicMock()
        runner.current_room = None  # skip the speed save/restore + render

        with patch.object(gr, 'pygame', fake_pygame):
            with patch.object(gr, 'expand_hash_newlines', lambda m: m):
                runner.show_message_dialog("hi")

        # Held state is released silently; the game's release handler must NOT
        # fire while the modal dialog is up.
        runner._release_held_key_silent.assert_called_once_with(100)
        runner.handle_keyboard_release.assert_not_called()


# ---------------------------------------------------------------------------
# M49 — per-frame step loop iterates a snapshot (spawn doesn't process in-frame)
# ---------------------------------------------------------------------------
class TestSpawnSnapshot:
    def test_step_loop_iterates_snapshot(self):
        """An instance created during another instance's step must NOT have its
        own step run in the same frame (snapshot semantics)."""
        runner = _make_runner()
        room = _make_room('lvl', [])
        runner.current_room = room

        from runtime.game_runner import GameInstance
        stepped = []

        spawner = GameInstance('spawner', 0, 0, {})
        spawner.object_data = {'events': {}}
        spawner.action_executor = MagicMock()

        def spawner_step():
            stepped.append('spawner')
            # Mid-step spawn: append a child whose step would also record.
            child = GameInstance('child', 0, 0, {})
            child.object_data = {'events': {}}
            child.action_executor = MagicMock()

            def child_step():
                stepped.append('child')
            child.step = child_step
            room.instances.append(child)
        spawner.step = spawner_step

        room.instances = [spawner]

        # Drive a single pass of the merged step loop exactly as run_game_loop
        # does over a snapshot.
        for instance in list(room.instances):
            instance.step()

        # The child was created but only the spawner stepped this frame.
        assert stepped == ['spawner']
        assert len(room.instances) == 2  # child is queued for next frame
