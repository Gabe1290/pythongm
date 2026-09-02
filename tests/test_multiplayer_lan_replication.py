"""LAN multiplayer v2 -- snapshot build / apply / interpolation unit tests.

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 4.3: extensions/multiplayer_lan/
replication.py. Pure logic -- no sockets, no pygame.
"""
import sys
from pathlib import Path

from pytest import approx

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_lan.replication import (  # noqa: E402
    NetIdAllocator, SnapshotApplier, SnapshotBuilder,
)


def _inst(nid, o="obj_p", x=0, y=0, r=0, f=0, v=True, vars=None):
    d = {"nid": nid, "o": o, "x": x, "y": y, "r": r, "f": f, "v": v}
    if vars is not None:
        d["vars"] = vars
    return d


# ---------------------------------------------------------------------------
# NetIdAllocator
# ---------------------------------------------------------------------------

class TestNetIdAllocator:
    def test_sequential_from_one(self):
        a = NetIdAllocator()
        assert [a.allocate() for _ in range(4)] == [1, 2, 3, 4]

    def test_never_reused(self):
        a = NetIdAllocator()
        seen = {a.allocate() for _ in range(100)}
        assert len(seen) == 100

    def test_custom_start(self):
        a = NetIdAllocator(start=50)
        assert a.allocate() == 50
        assert a.peek_next == 51


# ---------------------------------------------------------------------------
# SnapshotBuilder -- host-side delta compression
# ---------------------------------------------------------------------------

class TestSnapshotBuilder:
    def test_first_build_is_full(self):
        b = SnapshotBuilder()
        snap = b.build([_inst(1, x=10), _inst(2, x=20)],
                       {"score": 3}, tick=5, time_ms=1234)
        assert snap["t"] == "snap"
        assert snap["tick"] == 5 and snap["time"] == 1234
        assert snap["shared"] == {"score": 3}
        assert {s["nid"] for s in snap["spawn"]} == {1, 2}
        assert snap["spawn"][0]["o"] == "obj_p"
        assert [row["nid"] for row in snap["i"]] == [1, 2]
        assert "despawn" not in snap

    def test_second_build_no_change_has_no_deltas(self):
        b = SnapshotBuilder()
        insts = [_inst(1, x=10)]
        b.build(insts, {"score": 3})
        snap = b.build(insts, {"score": 3})
        assert "shared" not in snap
        assert "spawn" not in snap
        assert "despawn" not in snap
        assert [row["nid"] for row in snap["i"]] == [1]     # positions always sent

    def test_only_changed_shared_key_in_delta(self):
        b = SnapshotBuilder()
        b.build([], {"a": 1, "b": 2, "c": 3})
        snap = b.build([], {"a": 1, "b": 99, "c": 3})
        assert snap["shared"] == {"b": 99}

    def test_removed_shared_key_sent_as_none(self):
        b = SnapshotBuilder()
        b.build([], {"a": 1, "b": 2})
        snap = b.build([], {"a": 1})
        assert snap["shared"] == {"b": None}

    def test_new_instance_produces_spawn(self):
        b = SnapshotBuilder()
        b.build([_inst(1)], {})
        snap = b.build([_inst(1), _inst(2, o="obj_bullet", x=40, y=60)], {})
        assert snap["spawn"] == [{"nid": 2, "o": "obj_bullet", "x": 40, "y": 60}]
        assert "despawn" not in snap

    def test_removed_instance_produces_despawn(self):
        b = SnapshotBuilder()
        b.build([_inst(1), _inst(2)], {})
        snap = b.build([_inst(1)], {})
        assert snap["despawn"] == [2]
        assert [row["nid"] for row in snap["i"]] == [1]

    def test_vars_passed_through_when_present(self):
        b = SnapshotBuilder()
        snap = b.build([_inst(1, vars={"hp": 3})], {})
        assert snap["i"][0]["vars"] == {"hp": 3}

    def test_visible_normalised_to_0_or_1(self):
        b = SnapshotBuilder()
        snap = b.build([_inst(1, v=False), _inst(2, v=True)], {})
        assert snap["i"][0]["v"] == 0
        assert snap["i"][1]["v"] == 1

    def test_reset_forces_a_full_build(self):
        b = SnapshotBuilder()
        b.build([_inst(1)], {"score": 1})
        b.reset()
        snap = b.build([_inst(1)], {"score": 1})
        assert snap["shared"] == {"score": 1}
        assert {s["nid"] for s in snap["spawn"]} == {1}


# ---------------------------------------------------------------------------
# SnapshotApplier -- client-side apply + interpolation
# ---------------------------------------------------------------------------

class TestSnapshotApplierLifecycle:
    def test_spawn_frame_yields_to_create(self):
        a = SnapshotApplier()
        created, destroyed = a.ingest(
            {"t": "snap", "spawn": [{"nid": 1, "o": "obj_p", "x": 5, "y": 6}],
             "i": [{"nid": 1, "x": 5, "y": 6}]}, now=0.0)
        assert created == [(1, "obj_p", 5, 6)]
        assert destroyed == []
        assert a.ghost_ids() == [1]

    def test_despawn_frame_yields_to_destroy(self):
        a = SnapshotApplier()
        a.ingest({"t": "snap", "spawn": [{"nid": 1, "o": "obj_p", "x": 0, "y": 0}],
                  "i": [{"nid": 1, "x": 0, "y": 0}]}, now=0.0)
        created, destroyed = a.ingest({"t": "snap", "despawn": [1], "i": []}, now=0.1)
        assert created == []
        assert destroyed == [1]
        assert a.ghost_ids() == []

    def test_position_row_for_unknown_ghost_is_adopted(self):
        # Joined mid-game and missed the spawn frame.
        a = SnapshotApplier()
        created, _ = a.ingest(
            {"t": "snap", "i": [{"nid": 7, "o": "obj_late", "x": 1, "y": 2}]}, now=0.0)
        assert created == [(7, "obj_late", 1, 2)]
        assert a.ghost_ids() == [7]

    def test_shared_mirror_tracks_deltas(self):
        a = SnapshotApplier()
        a.ingest({"t": "snap", "shared": {"score": 1, "turn": 0}, "i": []}, now=0.0)
        a.ingest({"t": "snap", "shared": {"score": 2}, "i": []}, now=0.1)
        assert a.shared == {"score": 2, "turn": 0}

    def test_vars_accumulate_on_ghost(self):
        a = SnapshotApplier()
        a.ingest({"t": "snap", "spawn": [{"nid": 1, "o": "p", "x": 0, "y": 0}],
                  "i": [{"nid": 1, "x": 0, "y": 0, "vars": {"hp": 3}}]}, now=0.0)
        a.ingest({"t": "snap", "i": [{"nid": 1, "x": 0, "y": 0, "vars": {"ammo": 9}}]}, now=0.1)
        assert a.ghost_vars(1) == {"hp": 3, "ammo": 9}

    def test_tick_and_time_recorded(self):
        a = SnapshotApplier()
        a.ingest({"t": "snap", "tick": 42, "time": 9999, "i": []}, now=0.0)
        assert a.last_tick == 42
        assert a.last_time == 9999


class TestSnapshotApplierInterpolation:
    def _two_samples(self):
        a = SnapshotApplier()
        a.ingest({"t": "snap", "spawn": [{"nid": 1, "o": "p", "x": 0, "y": 0}],
                  "i": [{"nid": 1, "x": 0, "y": 0, "r": 0, "f": 0, "v": 1}]}, now=1.000)
        a.ingest({"t": "snap",
                  "i": [{"nid": 1, "x": 100, "y": 40, "r": 90, "f": 3, "v": 0}]}, now=1.100)
        return a

    def test_midpoint_is_linear(self):
        a = self._two_samples()
        x, y, r, f, v = a.sample(1, render_time=1.050)
        assert x == approx(50.0)
        assert y == approx(20.0)
        assert r == approx(45.0)

    def test_quarter_point(self):
        a = self._two_samples()
        x, y, r, f, v = a.sample(1, render_time=1.025)
        assert x == approx(25.0)
        assert y == approx(10.0)

    def test_discrete_fields_take_earlier_bracket(self):
        a = self._two_samples()
        _, _, _, f, v = a.sample(1, render_time=1.050)
        assert f == 0          # not 3
        assert v is True       # not False

    def test_render_time_before_first_sample_clamps(self):
        a = self._two_samples()
        x, y, r, f, v = a.sample(1, render_time=0.5)
        assert (x, y, r) == (0.0, 0.0, 0.0)

    def test_render_time_after_last_holds_last_no_extrapolation(self):
        a = self._two_samples()
        x, y, r, f, v = a.sample(1, render_time=5.0)
        assert x == 100.0 and y == 40.0 and r == 90.0
        assert f == 3 and v is False

    def test_angle_wraps_the_short_way(self):
        a = SnapshotApplier()
        a.ingest({"t": "snap", "spawn": [{"nid": 1, "o": "p", "x": 0, "y": 0}],
                  "i": [{"nid": 1, "x": 0, "y": 0, "r": 350}]}, now=0.0)
        a.ingest({"t": "snap", "i": [{"nid": 1, "x": 0, "y": 0, "r": 10}]}, now=0.1)
        _, _, r, _, _ = a.sample(1, render_time=0.05)
        # halfway from 350 to 10 the short way is ~0 (360), not 180
        wrapped = r % 360
        assert min(wrapped, 360 - wrapped) < 1.0

    def test_unknown_ghost_samples_none(self):
        a = SnapshotApplier()
        assert a.sample(999, render_time=0.0) is None

    def test_buffer_does_not_grow_without_bound(self):
        a = SnapshotApplier()
        a.ingest({"t": "snap", "spawn": [{"nid": 1, "o": "p", "x": 0, "y": 0}],
                  "i": [{"nid": 1, "x": 0, "y": 0}]}, now=0.0)
        for k in range(200):
            a.ingest({"t": "snap", "i": [{"nid": 1, "x": k, "y": 0}]}, now=1.0 + k * 0.05)
        # deque(maxlen=_BUFFER_LEN) -- bounded regardless of stream length
        assert len(a._ghosts[1].samples) <= 12

    def test_reset_clears_everything(self):
        a = self._two_samples()
        a.reset()
        assert a.ghost_ids() == []
        assert a.shared == {}
        assert a.sample(1, render_time=1.05) is None
