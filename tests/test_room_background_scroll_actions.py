"""Finishing the room-background/scrolling actions (TODO.md's "UI metadata
coverage" entry: set_background*/set_room_speed/set_room_persistent).

Four runtime/action_executor.py handlers existed but were either dead,
partial, or simply unregistered in events/action_types.py:

- set_room_speed: already fully functional (self.game_runner.fps is read
  fresh every frame). Only needed UI registration — pinned here structurally.
- set_background_color: `show_color` was accepted and discarded. Now wired
  onto GameRoom.show_background_color; render() fills black instead of the
  configured color when False (not skipping the fill — that would smear the
  previous frame's pixels across this continuously-redrawing pygame loop).
- set_background: `foreground` was accepted and discarded. Now wired onto
  GameRoom.background_foreground; the legacy single-background draw moves
  from before to after the instance-render pass, mirroring the multi-layer
  bg_layers format's existing foreground pass.
- set_room_persistent: set GameRoom.persistent, but nothing ever read it.
  Root cause: GameRunner.change_room reused self.rooms[room_name] forever,
  so every room behaved as persistent by accident. Now real GameMaker
  semantics: a room rebuilds fresh from its authored layout on every
  REVISIT unless explicitly marked persistent=True (see change_room and
  self._visited_rooms). Deliberately NOT applied to restart_game, which
  already unconditionally rebuilds every room (a prior fix, M52) — a full
  restart stays a hard reset regardless of any room's persistent flag.

This change surfaced a real regression in the maze_3/maze_4 samples (real
backtracking via previous_room/next_room; both have obj_diamond collectibles
with no remember_destroyed flag) — fixed by marking every room in those two
samples persistent: true in both project.json and rooms/*.json. The class
at the bottom of this file is the end-to-end proof that fix holds, driving
a real GameRunner through the actual sample.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame


# ---------------------------------------------------------------------------
# UI registration
# ---------------------------------------------------------------------------

class TestActionRegistration:
    def test_all_four_actions_resolve(self):
        from events.action_types import get_action_type
        for name in ("set_room_speed", "set_room_persistent",
                     "set_background_color", "set_background"):
            action_type = get_action_type(name)
            assert action_type is not None, f"{name} not registered"
            assert action_type.category == "Room"

    def test_set_room_speed_params(self):
        from events.action_types import get_action_type
        params = {p.name for p in get_action_type("set_room_speed").parameters}
        assert params == {"speed"}

    def test_set_room_persistent_params(self):
        from events.action_types import get_action_type
        params = {p.name for p in get_action_type("set_room_persistent").parameters}
        assert params == {"persistent"}

    def test_set_background_color_params(self):
        from events.action_types import get_action_type
        params = {p.name for p in get_action_type("set_background_color").parameters}
        assert params == {"color", "show_color"}

    def test_set_background_params(self):
        from events.action_types import get_action_type
        params = {p.name for p in get_action_type("set_background").parameters}
        assert params == {"background", "visible", "foreground",
                           "tiled_h", "tiled_v", "hspeed", "vspeed"}


# ---------------------------------------------------------------------------
# change_room rebuild-vs-reuse semantics
# ---------------------------------------------------------------------------

def _make_runner():
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            runner = GameRunner.__new__(GameRunner)
            runner.action_executor = MagicMock()
            runner.project_path = None
            runner.project_data = None
            runner._objects_data = {}
            runner.sprites = {}
            runner.backgrounds = {}
            runner.screen = None
            runner.rooms = {}
            runner.current_room = None
            runner.score = 0
            runner.lives = 3
            runner.health = 100
            runner._room_transition_grace_frames = 0
            runner._destroyed_memory = {}
            runner._visited_rooms = set()
            return runner


def _make_room(name, instances, persistent=False):
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRoom
            return GameRoom(
                name,
                {'width': 320, 'height': 240, 'instances': instances,
                 'persistent': persistent},
                action_executor=MagicMock(),
            )


class TestRoomPersistenceSemantics:
    def test_non_persistent_room_rebuilds_on_revisit(self):
        project_data = {
            'assets': {
                'rooms': {'r1': {'width': 320, 'height': 240, 'instances': [
                    {'object_name': 'box', 'x': 5, 'y': 5}]}},
                'objects': {'box': {'name': 'box'}},
            },
            'settings': {},
        }
        runner = _make_runner()
        runner.project_data = project_data
        runner._objects_data = project_data['assets']['objects']

        room1 = _make_room('r1', [{'object_name': 'box', 'x': 5, 'y': 5}])
        room2 = _make_room('r2', [])
        runner.rooms = {'r1': room1, 'r2': room2}
        runner.current_room = room2

        runner.change_room('r1')
        first = runner.rooms['r1']
        assert first is room1  # first entry: pristine object, no rebuild

        runner.change_room('r2')
        runner.change_room('r1')
        second = runner.rooms['r1']

        assert second is not first, "non-persistent room was not rebuilt on revisit"

    def test_persistent_room_keeps_live_state_on_revisit(self):
        project_data = {
            'assets': {
                'rooms': {'r1': {'width': 320, 'height': 240, 'instances': [
                    {'object_name': 'box', 'x': 5, 'y': 5}]}},
                'objects': {'box': {'name': 'box'}},
            },
            'settings': {},
        }
        runner = _make_runner()
        runner.project_data = project_data
        runner._objects_data = project_data['assets']['objects']

        room1 = _make_room('r1', [{'object_name': 'box', 'x': 5, 'y': 5}], persistent=True)
        room2 = _make_room('r2', [])
        runner.rooms = {'r1': room1, 'r2': room2}
        runner.current_room = room2

        runner.change_room('r1')
        # Mutate live state the way real gameplay would (move an instance).
        runner.current_room.instances[0].x = 999

        runner.change_room('r2')
        runner.change_room('r1')

        assert runner.rooms['r1'] is room1, "persistent room was rebuilt on revisit"
        assert runner.current_room.instances[0].x == 999, "live state was lost"

    def test_first_visit_never_rebuilds(self):
        """A room's first-ever entry must use the pristine object GameRoom
        already built — rebuilding it again would be redundant (not wrong,
        but wasted work the _visited_rooms check exists to skip)."""
        project_data = {
            'assets': {
                'rooms': {'r1': {'width': 320, 'height': 240, 'instances': []}},
                'objects': {},
            },
            'settings': {},
        }
        runner = _make_runner()
        runner.project_data = project_data
        room1 = _make_room('r1', [])
        runner.rooms = {'r1': room1}
        runner.current_room = None

        runner.change_room('r1')

        assert runner.rooms['r1'] is room1

    def test_remember_destroyed_instance_stays_gone_after_non_persistent_rebuild(self):
        project_data = {
            'assets': {
                'rooms': {'r1': {'width': 320, 'height': 240, 'instances': [
                    {'object_name': 'bonus', 'x': 10, 'y': 10}]}},
                'objects': {'bonus': {'name': 'bonus', 'remember_destroyed': True}},
            },
            'settings': {},
        }
        runner = _make_runner()
        runner.project_data = project_data
        runner._objects_data = project_data['assets']['objects']

        room1 = _make_room('r1', [{'object_name': 'bonus', 'x': 10, 'y': 10}])
        room1.set_sprites_for_instances({}, project_data['assets']['objects'])
        room2 = _make_room('r2', [])
        runner.rooms = {'r1': room1, 'r2': room2}
        runner.current_room = room2

        runner.change_room('r1')
        bonus = runner.current_room.instances[0]
        bonus.to_destroy = True
        runner._remember_destroyed_instance(runner.current_room, bonus)
        runner.current_room.instances.remove(bonus)

        runner.change_room('r2')
        runner.change_room('r1')  # non-persistent rebuild

        names = [i.object_name for i in runner.current_room.instances]
        assert 'bonus' not in names, "remember_destroyed instance respawned after rebuild"

    def test_restart_game_still_rebuilds_a_persistent_room(self):
        """The deliberate deviation from real GameMaker: restart_game
        unconditionally rebuilds every room (M52), even one marked
        persistent — a full restart is a hard reset."""
        project_data = {
            'assets': {
                'rooms': {
                    'r1': {'width': 320, 'height': 240, 'instances': [
                        {'object_name': 'box', 'x': 1, 'y': 1}], 'persistent': True},
                    'r2': {'width': 320, 'height': 240, 'instances': [], 'persistent': True},
                },
                'objects': {'box': {'name': 'box'}},
            },
            'settings': {},
        }
        runner = _make_runner()
        runner.project_data = project_data
        runner._objects_data = project_data['assets']['objects']
        runner.window_width = 320
        runner.window_height = 240

        room1 = _make_room('r1', [{'object_name': 'box', 'x': 1, 'y': 1}], persistent=True)
        room2 = _make_room('r2', [], persistent=True)
        runner.rooms = {'r1': room1, 'r2': room2}
        runner.current_room = room1
        runner._visited_rooms.update({'r1', 'r2'})
        runner.current_room.instances[0].x = 999  # mutate live state

        runner.restart_game()

        assert runner.rooms['r1'] is not room1, "persistent room survived restart_game"
        assert runner.rooms['r1'].instances[0].x == 1, "restart did not use the authored layout"
        # restart_game marks the first room visited again (matching run()/
        # test_game()'s own convention), but 'r2' was never re-entered post-
        # restart, so it must NOT still be considered visited.
        assert runner._visited_rooms == {'r1'}, \
            f"_visited_rooms not correctly reset by restart_game: {runner._visited_rooms}"


# ---------------------------------------------------------------------------
# show_background_color / background_foreground rendering
# ---------------------------------------------------------------------------

class TestBackgroundColorVisibility:
    def _room(self, show_color=True):
        from runtime.game_runner import GameRoom
        room = GameRoom('r', {'width': 64, 'height': 64,
                               'background_color': '#ff0000',
                               'show_background_color': show_color},
                         action_executor=MagicMock())
        return room

    def test_default_shows_configured_color(self):
        room = self._room(show_color=True)
        screen = pygame.Surface((64, 64))
        room.render(screen)
        assert screen.get_at((0, 0))[:3] == (255, 0, 0)

    def test_hidden_fills_black_not_the_configured_color(self):
        room = self._room(show_color=False)
        screen = pygame.Surface((64, 64))
        # Pre-fill with a marker color to prove the fill actually ran
        # (not skipped, which would leave stale pixels / smear frames).
        screen.fill((0, 255, 0))
        room.render(screen)
        assert screen.get_at((0, 0))[:3] == (0, 0, 0)


class TestBackgroundForeground:
    def _room_with_bg_and_instance(self, foreground):
        from runtime.game_runner import GameRoom, GameInstance
        room = GameRoom('r', {'width': 64, 'height': 64,
                               'background_foreground': foreground},
                         action_executor=MagicMock())
        bg = pygame.Surface((64, 64))
        bg.fill((0, 0, 255))
        room.background_surface = bg
        room.background_image_name = 'bg'

        inst = GameInstance('obj', 0, 0, {'x': 0, 'y': 0}, action_executor=MagicMock())
        sprite_surface = pygame.Surface((16, 16))
        sprite_surface.fill((255, 0, 0))
        inst.sprite = MagicMock()
        inst.sprite.get_frame = MagicMock(return_value=sprite_surface)
        inst.sprite.origin_x = 0
        inst.sprite.origin_y = 0
        inst.scale_x = 1.0
        inst.scale_y = 1.0
        inst.visible = True
        inst.is_thymio = False
        inst.object_data = None
        room.instances.append(inst)
        room._depth_dirty = True
        return room

    def test_background_behind_instances_by_default(self):
        room = self._room_with_bg_and_instance(foreground=False)
        screen = pygame.Surface((64, 64))
        room._render_room(screen, (0, 0))
        # The instance's sprite pixel must be on top (red), not overdrawn
        # by the background (blue).
        px = screen.get_at((4, 4))[:3]
        assert px == (255, 0, 0), f"instance was not drawn on top, got {px}"

    def test_background_in_front_of_instances_when_foreground(self):
        room = self._room_with_bg_and_instance(foreground=True)
        screen = pygame.Surface((64, 64))
        room._render_room(screen, (0, 0))
        # The background now draws AFTER instances, so it must cover the
        # sprite: the sampled pixel is blue, not red.
        px = screen.get_at((4, 4))[:3]
        assert px == (0, 0, 255), f"background did not draw in front, got {px}"

    def test_foreground_still_tiles_across_the_whole_room(self):
        """foreground and tiled_h/tiled_v are independent params on the
        same action — _render_legacy_background handles tiling entirely
        internally and is called from exactly one of the two call sites
        per frame (never both), so moving WHICH slot invokes it doesn't
        touch the tiling logic itself. Verify the combination directly
        rather than just reasoning about it: a small tile must repeat
        across the full room AND still draw over instances when
        foreground=True."""
        from runtime.game_runner import GameRoom, GameInstance

        room = GameRoom('r', {'width': 64, 'height': 64,
                               'tile_horizontal': True, 'tile_vertical': True,
                               'background_foreground': True},
                         action_executor=MagicMock())
        bg = pygame.Surface((16, 16))
        bg.fill((0, 0, 255))
        room.background_surface = bg
        room.background_image_name = 'bg'

        inst = GameInstance('obj', 0, 0, {'x': 0, 'y': 0}, action_executor=MagicMock())
        sprite_surface = pygame.Surface((16, 16))
        sprite_surface.fill((255, 0, 0))
        inst.sprite = MagicMock()
        inst.sprite.get_frame = MagicMock(return_value=sprite_surface)
        inst.sprite.origin_x = 0
        inst.sprite.origin_y = 0
        inst.scale_x = 1.0
        inst.scale_y = 1.0
        inst.visible = True
        inst.is_thymio = False
        inst.object_data = None
        room.instances.append(inst)
        room._depth_dirty = True

        screen = pygame.Surface((64, 64))
        room._render_room(screen, (0, 0))

        for point in ((0, 0), (40, 40), (60, 60)):
            assert screen.get_at(point)[:3] == (0, 0, 255), \
                f"tile did not repeat across the room at {point}"
        # foreground=True: the tiled background must also cover the instance.
        assert screen.get_at((4, 4))[:3] == (0, 0, 255), \
            "tiled foreground background did not draw over the instance"

    def test_scroll_speed_is_not_doubled_by_the_foreground_reorder(self):
        """The background/foreground branches are mutually exclusive per
        frame (exactly one _render_legacy_background call either way), so
        bg_scroll_x/y — accumulated inside that one call — must advance by
        exactly hspeed/vspeed per frame in EITHER mode, not twice."""
        from runtime.game_runner import GameRoom

        for foreground in (False, True):
            room = GameRoom('r', {'width': 64, 'height': 64, 'bg_hspeed': 5,
                                   'background_foreground': foreground},
                             action_executor=MagicMock())
            bg = pygame.Surface((16, 16))
            bg.fill((0, 200, 0))
            room.background_surface = bg
            room.background_image_name = 'bg'

            screen = pygame.Surface((64, 64))
            room._render_room(screen, (0, 0))
            room._render_room(screen, (0, 0))

            assert room.bg_scroll_x == 10.0, (
                f"foreground={foreground}: expected 2 frames * 5px = 10, "
                f"got {room.bg_scroll_x}")


# ---------------------------------------------------------------------------
# End-to-end regression proof: maze_3's real sample data, real GameRunner
# ---------------------------------------------------------------------------

class TestMaze3PersistenceRegression:
    """Proves the semantics flip + the maze_3 sample fix (persistent: true
    on every room) together preserve real gameplay: a collected diamond
    must not respawn after the player backtracks away from and back to
    its room via the real previous_room/next_room actions."""

    def test_collected_diamond_stays_gone_after_backtrack(self):
        from runtime.game_runner import GameRunner

        project_json = str(REPO_ROOT / "samples" / "maze_3" / "project.json")
        runner = GameRunner(project_json)
        runner.language = "en"
        runner.show_message_dialog = lambda *a, **k: None
        runner.show_highscore_dialog = lambda *a, **k: None
        runner._show_name_entry_dialog = lambda *a, **k: ""
        runner.process_pending_messages = lambda *a, **k: None

        state = {"frames": 0}
        MAX_FRAMES = 20

        class _FakeClock:
            def tick(self, fps=0):
                f = state["frames"] = state["frames"] + 1
                if f == 2:
                    runner.change_room("room1")
                if f == 4:
                    player = next(i for i in runner.current_room.instances
                                  if i.object_name == "obj_person")
                    # Teleport exactly onto a real authored diamond position
                    # (samples/maze_3/rooms/room1.json) so the real collision
                    # pipeline destroys it deterministically, without needing
                    # to simulate multi-frame maze navigation.
                    player.x, player.y = 160.0, 96.0
                if f == 8:
                    # room1 -> room2 (controller_main's N binding). Not
                    # room_start -- its own controller_start binds next_room
                    # to SPACE, not N, so bouncing off room_start would need
                    # a different key than the P/N pair below.
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n))
                if f == 12:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))  # room2 -> room1 (backtrack)
                if f >= MAX_FRAMES:
                    runner.running = False
                return 0

            def get_fps(self):
                return 60.0

        real_clock = pygame.time.Clock
        pygame.time.Clock = _FakeClock
        try:
            result = runner.run()
        finally:
            pygame.time.Clock = real_clock

        assert result is not False, "game loop reported a fatal crash"
        assert runner.current_room.name == "room1", \
            f"expected to be back in room1, got {runner.current_room.name}"

        diamonds = [i for i in runner.current_room.instances
                    if i.object_name == "obj_diamond"]
        assert len(diamonds) == 3, (
            f"expected 3 diamonds (1 collected, stays gone after backtrack), "
            f"found {len(diamonds)}")
