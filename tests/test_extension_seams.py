"""The generic core seams extensions plug into (docs/THYMIO_EXTENSION_PLAN.md
Stage 0).

Each Stage-0 unit adds one seam to core and one section here proving it with
a DUMMY registrant — no Thymio code involved — so a seam bug can never be
confused with a bug in the code that later moves onto it.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# 0.1 — Instance.extension_state
# ---------------------------------------------------------------------------

def _instance(name="obj_a"):
    from runtime.instance import GameInstance
    return GameInstance(name, 0, 0, {}, action_executor=None)


def test_instance_has_empty_extension_state_by_default():
    inst = _instance()
    assert inst.extension_state == {}


def test_instance_extension_state_is_per_instance():
    """A shared class-level dict would leak one robot's state into every
    instance; each instance must own its own mapping."""
    a, b = _instance("obj_a"), _instance("obj_b")
    a.extension_state["dummy"] = {"hp": 3}
    assert b.extension_state == {}
    assert a.extension_state is not b.extension_state


def test_instance_extension_state_mirrors_room_pattern():
    """Same shape as GameRoom.extension_state so an extension namespaces the
    two identically (room.extension_state['x'] / inst.extension_state['x'])."""
    from runtime.game_runner import GameRoom
    room = GameRoom("r", {"width": 64, "height": 64}, action_executor=None)
    inst = _instance()
    assert type(inst.extension_state) is type(room.extension_state) is dict


# ---------------------------------------------------------------------------
# 0.2 — PLUGIN_INSTANCE_OVERLAYS
# ---------------------------------------------------------------------------

import pytest


@pytest.fixture
def clean_overlays():
    from runtime import extension_hooks
    saved = extension_hooks.get_instance_overlays()
    extension_hooks.clear_instance_overlays()
    yield extension_hooks
    extension_hooks.clear_instance_overlays()
    for f in saved:
        extension_hooks.register_instance_overlay(f)


def test_instance_overlay_registry_is_idempotent_and_skips_bad_input(clean_overlays):
    hooks = clean_overlays

    def ov(instance, screen):
        pass

    hooks.register_instance_overlay(ov)
    hooks.register_instance_overlay(ov)          # loader may re-run
    hooks.register_instance_overlay("nope")      # logged, not registered
    assert hooks.get_instance_overlays() == [ov]


def test_run_instance_overlays_offers_to_all_and_survives_a_raise(clean_overlays):
    hooks = clean_overlays
    seen = []

    def broken(instance, screen):
        raise RuntimeError("boom")

    def good(instance, screen):
        seen.append(instance)

    hooks.register_instance_overlay(broken)
    hooks.register_instance_overlay(good)
    inst = _instance()
    hooks.run_instance_overlays(inst, object())
    assert seen == [inst], "a raising overlay must not stop the next one"


def test_loader_registers_plugin_instance_overlays(clean_overlays):
    from events.plugin_loader import PluginLoader

    def ov(instance, screen):
        pass

    assert PluginLoader._load_instance_overlays(object.__new__(PluginLoader), [ov]) == 1
    assert ov in clean_overlays.get_instance_overlays()


def test_game_runner_render_offers_every_instance_to_overlays(clean_overlays):
    """Drive the real GameRunner.render on a minimal stand-in: every instance
    of the current room reaches the overlay, after the room is drawn and
    with the real screen surface."""
    import pygame
    from types import SimpleNamespace
    from runtime.game_runner import GameRunner

    # Init but never quit the display: other tests (the pygame name-entry
    # dialog) rely on the session-wide display staying up.
    pygame.display.init()
    screen = pygame.display.set_mode((32, 32))
    order = []
    a, b = _instance("obj_a"), _instance("obj_b")
    room = SimpleNamespace(
        instances=[a, b],
        update_views=lambda: order.append("views"),
        render=lambda s: order.append("room"),
    )
    fake = SimpleNamespace(screen=screen, current_room=room,
                           update_caption=lambda: None)

    got = []
    clean_overlays.register_instance_overlay(
        lambda inst, s: got.append((inst, s)))
    GameRunner.render(fake)

    assert order == ["views", "room"]
    assert [i for i, _ in got] == [a, b]
    assert all(s is screen for _, s in got)


def test_instance_created_hook_runs_per_room_instance_and_survives_a_raise():
    """Stage B3 seam: a room offers each instance it builds to the hooks."""
    from runtime import extension_hooks
    from runtime.game_runner import GameRoom
    saved = extension_hooks.get_instance_created_hooks()
    extension_hooks.clear_instance_created_hooks()
    try:
        seen = []
        extension_hooks.register_instance_created_hook(lambda i, d, r: 1 / 0)
        extension_hooks.register_instance_created_hook(
            lambda i, d, r: seen.append((i.object_name, d.get("x"), r)))
        extension_hooks.register_instance_created_hook("nope")
        assert len(extension_hooks.get_instance_created_hooks()) == 2
        room = GameRoom("r", {"width": 64, "height": 64, "instances": [
            {"object": "a", "x": 1, "y": 2}, {"object": "b", "x": 3, "y": 4}]},
            action_executor=None)
        assert seen == [("a", 1, room), ("b", 3, room)]
    finally:
        extension_hooks.clear_instance_created_hooks()
        for f in saved:
            extension_hooks.register_instance_created_hook(f)


def test_custom_rendered_instance_skips_sprite_and_draw_event():
    """The engine leaves a custom_rendered instance to the overlay pass."""
    from types import SimpleNamespace
    from runtime.game_runner import GameRoom
    import pygame
    pygame.display.init()
    screen = pygame.display.set_mode((32, 32))
    room = GameRoom("r", {"width": 32, "height": 32}, action_executor=None)
    calls = []
    for name, custom in (("plain", False), ("robot", True)):
        inst = SimpleNamespace(
            depth=0, visible=True, custom_rendered=custom,
            render=lambda s, view_offset=(0, 0), n=name: calls.append(("render", n)),
            run_draw_event=lambda s, n=name: calls.append(("draw", n)))
        room.instances.append(inst)
    room._depth_dirty = True
    room._render_room(screen, (0, 0))
    room._render_draw_events(screen)
    assert calls == [("render", "plain"), ("draw", "plain")]


def test_after_collision_is_a_valid_frame_update_phase():
    """Stage A5 added the third phase (between collision and end-step)."""
    from runtime import extension_hooks
    saved = extension_hooks.get_frame_updates()
    extension_hooks.clear_frame_updates()
    try:
        calls = []
        extension_hooks.register_frame_update(lambda r: calls.append(r), "after_collision")
        extension_hooks.register_frame_update(lambda r: calls.append("bad"), "nope")
        assert len(extension_hooks.get_frame_updates()) == 1
        extension_hooks.run_frame_updates("R", "after_collision")
        extension_hooks.run_frame_updates("R", "after_update")
        assert calls == ["R"]
    finally:
        extension_hooks.clear_frame_updates()
        for f, p in saved:
            extension_hooks.register_frame_update(f, p)


# ---------------------------------------------------------------------------
# 0.3 — PLUGIN_INPUT_HANDLERS
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_input():
    from runtime import extension_hooks
    saved = extension_hooks.get_input_handlers()
    extension_hooks.clear_input_handlers()
    yield extension_hooks
    extension_hooks.clear_input_handlers()
    for h in saved:
        extension_hooks.register_input_handler(h)


def test_input_registry_validates_and_is_idempotent(clean_input):
    hooks = clean_input
    good = {"key_down": lambda i, k: False}
    hooks.register_input_handler(good)
    hooks.register_input_handler(good)
    hooks.register_input_handler({"bogus": lambda: None})      # unknown kind
    hooks.register_input_handler({"key_up": "not callable"})
    hooks.register_input_handler(["not", "a", "dict"])
    assert hooks.get_input_handlers() == [good]


def test_run_input_aggregates_and_survives_a_raise(clean_input):
    hooks = clean_input
    hooks.register_input_handler({"mouse_down": lambda r, b, x, y: 1 / 0})
    hooks.register_input_handler({"mouse_down": lambda r, b, x, y: True})
    hooks.register_input_handler({"key_up": lambda i, k: None})   # no mouse_down
    assert hooks.run_mouse_down(object(), 1, 0, 0) is True
    assert hooks.run_mouse_up(object(), 1, 0, 0) is False           # nobody handles
    assert hooks.run_key_down(object(), "up") is False


def test_loader_registers_plugin_input_handlers(clean_input):
    from events.plugin_loader import PluginLoader
    h = {"key_down": lambda i, k: True}
    assert PluginLoader._load_input_handlers(object.__new__(PluginLoader), [h]) == 1
    assert h in clean_input.get_input_handlers()


def _runner_with(instances):
    """Minimal stand-in for the InputMixin's `self`, with a room whose
    screen_to_room is the identity."""
    from types import SimpleNamespace
    import pygame
    room = SimpleNamespace(instances=instances,
                           screen_to_room=lambda x, y: (x, y))
    return SimpleNamespace(current_room=room,
                           _get_key_name=lambda key: "up" if key == pygame.K_UP else None)


def _instance_with_events(name, events):
    inst = _instance(name)
    inst.object_data = {"events": events}
    inst.keys_pressed = set()
    inst.action_executor = None
    return inst


def test_keyboard_hooks_run_per_instance_in_loop_order(clean_input):
    """key_down/key_up see each instance, interleaved with the engine's own
    per-instance dispatch — so the extension's ordering matches authored
    keyboard events exactly. Orphan instances (no object_data) are skipped
    like everywhere else."""
    import pygame
    from runtime.game_runner import GameRunner
    a = _instance_with_events("obj_a", {})
    b = _instance_with_events("obj_b", {})
    orphan = _instance("obj_gone")
    orphan.keys_pressed = set()
    runner = _runner_with([a, orphan, b])

    seen = []
    clean_input.register_input_handler({
        "key_down": lambda inst, key: seen.append(("down", inst, key)) or True,
        "key_up": lambda inst, key: seen.append(("up", inst, key)),
    })
    GameRunner.handle_keyboard_press(runner, pygame.K_UP)
    GameRunner.handle_keyboard_release(runner, pygame.K_UP)
    assert seen == [("down", a, "up"), ("down", b, "up"),
                    ("up", a, "up"), ("up", b, "up")]


def test_mouse_hooks_swallow_the_click_before_mouse_events(clean_input):
    """A handler returning True on mouse_down/mouse_up stops the engine's
    per-instance mouse dispatch, with raw screen coordinates; returning
    False lets it through untouched."""
    import pygame
    from runtime.game_runner import GameRunner

    fired = []

    class _Exec:
        def execute_action_list(self, inst, actions):
            fired.append(actions)

    inst = _instance_with_events("obj_a", {
        "mouse": {"left_button": {"actions": ["press"]},
                  "left_button_released": {"actions": ["release"]}},
    })
    inst.action_executor = _Exec()
    runner = _runner_with([inst])

    calls = []
    swallow = {"v": True}
    clean_input.register_input_handler({
        "mouse_down": lambda r, b, x, y: calls.append(("down", b, x, y)) or swallow["v"],
        "mouse_up": lambda r, b, x, y: calls.append(("up", b, x, y)) or swallow["v"],
    })
    GameRunner.handle_mouse_press(runner, 1, (12, 34))
    GameRunner.handle_mouse_release(runner, 1, (12, 34))
    assert calls == [("down", 1, 12, 34), ("up", 1, 12, 34)]
    assert fired == [], "swallowed click must not reach mouse events"

    swallow["v"] = False
    GameRunner.handle_mouse_press(runner, 1, (12, 34))
    GameRunner.handle_mouse_release(runner, 1, (12, 34))
    assert fired == [["press"], ["release"]]


# ---------------------------------------------------------------------------
# 0.4 — PLUGIN_ASSET_TYPES (core/asset_types)
# ---------------------------------------------------------------------------

import json


@pytest.fixture
def clean_asset_types():
    from core import asset_types
    saved = asset_types.get_registered_asset_types()
    asset_types.clear_registered_asset_types()
    yield asset_types
    asset_types.clear_registered_asset_types()
    for spec in saved:
        asset_types.register_side_file_asset_type(spec)


def _arena_spec():
    from core.asset_types import SideFileAssetType
    return SideFileAssetType(
        plural="arenas", singular="arena", description="Dummy arenas",
        file_keys=("size", "walls"), strip_keys=("walls",))


def test_asset_type_registry_validates_and_is_idempotent(clean_asset_types):
    at = clean_asset_types
    from core.asset_types import SideFileAssetType
    spec = _arena_spec()
    at.register_side_file_asset_type(spec)
    at.register_side_file_asset_type(spec)                       # re-run
    at.register_side_file_asset_type("nope")                     # not a spec
    at.register_side_file_asset_type(SideFileAssetType(          # core type
        "rooms", "room", "", (), ()))
    at.register_side_file_asset_type(SideFileAssetType(          # conflict
        "arenas", "arena", "other", ("x",), ()))
    assert at.get_registered_asset_types() == [spec]
    assert at.side_file_type_names() == ("rooms", "objects", "sprites", "arenas")
    assert at.plural_to_singular() == {"arenas": "arena"}


def test_core_asset_types_registers_nothing_by_default(clean_asset_types):
    """Since Stage C5, core/asset_types.py registers nothing at import time
    -- "playgrounds" is the Thymio extension's own PLUGIN_ASSET_TYPES entry,
    registered through the loader like any other extension asset type (see
    test_thymio_extension.py's Stage C5 coverage for that)."""
    from core.asset_types import get_registered_asset_types
    assert get_registered_asset_types() == []


def test_loader_registers_plugin_asset_types(clean_asset_types):
    from events.plugin_loader import PluginLoader
    spec = _arena_spec()
    assert PluginLoader._load_asset_types(object.__new__(PluginLoader), [spec]) == 1
    assert spec in clean_asset_types.get_registered_asset_types()


def test_project_structure_slots_registered_types_after_rooms(clean_asset_types):
    from core.project_manager import ProjectManager
    clean_asset_types.register_side_file_asset_type(_arena_spec())
    keys = list(ProjectManager._project_structure())
    assert keys == ["sprites", "sounds", "backgrounds", "objects", "rooms",
                    "arenas", "scripts", "fonts", "data"]
    assert "playgrounds" not in ProjectManager.DEFAULT_PROJECT_STRUCTURE


def test_registered_type_round_trips_through_project_manager(clean_asset_types, tmp_path):
    """A dummy 'arenas' type saves to arenas/<name>.json with strip_keys
    removed from project.json, and loads back merged — including a legacy
    string entry and one whose payload lives only in the side file."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from core.project_manager import ProjectManager

    clean_asset_types.register_side_file_asset_type(_arena_spec())
    proj = tmp_path / "p"
    (proj / "arenas").mkdir(parents=True)
    (proj / "arenas" / "b.json").write_text(json.dumps(
        {"size": [3, 4], "walls": [1], "ignored": True}), encoding="utf-8")
    (proj / "project.json").write_text(json.dumps({
        "name": "p", "version": "1.0.0", "created": "x", "modified": "x",
        "settings": {}, "assets": {
            "rooms": {"room0": {"name": "room0", "asset_type": "room",
                                "width": 64, "height": 64}},
            "arenas": {
                "a": {"name": "a", "asset_type": "arena", "size": [1, 2], "walls": [9]},
                "b": "b",
            }}}), encoding="utf-8")

    pm = ProjectManager()
    assert pm.load_project(proj)
    arenas = pm.current_project_data["assets"]["arenas"]
    assert arenas["b"] == {"name": "b", "asset_type": "arena",
                           "size": [3, 4], "walls": [1]}      # file_keys only
    assert arenas["a"]["walls"] == [9]
    assert pm.get_project_info()["arenas_count"] == 2
    assert pm.save_project()

    on_disk = json.loads((proj / "project.json").read_text(encoding="utf-8"))
    assert on_disk["assets"]["arenas"]["a"] == {
        "name": "a", "asset_type": "arena", "size": [1, 2],
        "_external_file": "arenas/a.json"}                     # walls stripped
    side = json.loads((proj / "arenas" / "a.json").read_text(encoding="utf-8"))
    assert side["walls"] == [9] and side["size"] == [1, 2]
    assert (proj / "arenas" / "b.json").exists()
    # Rollback bookkeeping covers the new directory too.
    assert "arenas" in pm._SAVE_MANAGED_NAMES


def test_unregistered_type_is_left_alone_on_disk(clean_asset_types, tmp_path):
    """With no extension registering it, an unknown asset dict in a shared
    project is preserved verbatim in project.json (no side file, no strip)."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from core.project_manager import ProjectManager

    proj = tmp_path / "q"
    proj.mkdir()
    entry = {"name": "z", "asset_type": "arena", "size": [1], "walls": [2]}
    (proj / "project.json").write_text(json.dumps({
        "name": "q", "version": "1.0.0", "created": "x", "modified": "x",
        "settings": {}, "assets": {"rooms": {}, "arenas": {"z": entry}}}),
        encoding="utf-8")
    pm = ProjectManager()
    assert pm.load_project(proj) and pm.save_project()
    on_disk = json.loads((proj / "project.json").read_text(encoding="utf-8"))
    assert on_disk["assets"]["arenas"]["z"] == entry
    assert not (proj / "arenas").exists()


# ---------------------------------------------------------------------------
# 0.6 — PLUGIN_BLOCK_CATEGORIES (config/blockly_config + blockly_translations)
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_blocks():
    from config import blockly_config as bc, blockly_translations as bt
    before_cats = set(bc.BLOCK_REGISTRY)
    before_presets = set(bc.PRESETS)
    saved_cat_tr = {lang: dict(t) for lang, t in bt.CATEGORY_TRANSLATIONS.items()}
    saved_block_tr = set(bt.BLOCK_TRANSLATIONS)
    yield bc, bt
    bc.unregister_block_categories(set(bc.BLOCK_REGISTRY) - before_cats)
    for name in set(bc.PRESETS) - before_presets:
        del bc.PRESETS[name]
    bt.CATEGORY_TRANSLATIONS.clear()
    bt.CATEGORY_TRANSLATIONS.update(saved_cat_tr)
    for name in set(bt.BLOCK_TRANSLATIONS) - saved_block_tr:
        del bt.BLOCK_TRANSLATIONS[name]


_DUMMY_CATS = {"Dummy Robot": [
    {"type": "dummy_beep", "name": "Beep", "description": "Beep once", "implemented": True},
    {"type": "dummy_fly", "name": "Fly", "description": "Not yet", "implemented": False},
]}


def test_block_categories_merge_and_refresh_full_presets(clean_blocks):
    bc, _bt = clean_blocks
    assert bc.register_block_categories(_DUMMY_CATS) == 1
    assert bc.register_block_categories(_DUMMY_CATS) == 0          # idempotent
    assert bc.register_block_categories({"Events": []}) == 0        # core wins
    assert "Dummy Robot" in bc.BLOCK_REGISTRY
    assert {"dummy_beep", "dummy_fly"} <= bc.get_all_block_types()
    assert bc.is_block_implemented("dummy_beep") and not bc.is_block_implemented("dummy_fly")
    assert "dummy_beep" in bc.PRESETS["full"].enabled_blocks
    assert "Dummy Robot" in bc.PRESETS["full"].enabled_categories
    assert "dummy_beep" in bc.PRESETS["implemented_only"].enabled_blocks
    assert "dummy_fly" not in bc.PRESETS["implemented_only"].enabled_blocks
    cfg = bc.BlocklyConfig(preset_name="x")
    cfg.enable_category("Dummy Robot")
    assert cfg.enabled_blocks == {"dummy_beep", "dummy_fly"}


def test_blockly_presets_and_translations_merge(clean_blocks):
    bc, bt = clean_blocks
    bc.register_block_categories(_DUMMY_CATS)
    preset = bc.BlocklyConfig(preset_name="dummy")
    preset.enable_category("Dummy Robot")
    assert bc.register_blockly_presets({"dummy": preset, "full": preset, "bad": 3}) == 1
    assert bc.PRESETS["dummy"] is preset
    assert bc.PRESETS["full"] is not preset

    bt.register_category_translations({"fr": {"Dummy Robot": "Robot factice", "Events": "NOPE"}})
    assert bt.get_translated_category("Dummy Robot", "fr") == "Robot factice"
    assert bt.get_translated_category("Events", "fr") != "NOPE"      # existing kept
    bt.register_block_translations({"dummy_beep": {
        "name": {"fr": "Bip"}, "description": {"fr": "Un bip"}}})
    assert bt.get_translated_block_name("dummy_beep", "fr") == "Bip"
    assert bt.get_translated_block_description("dummy_beep", "fr") == "Un bip"


def test_loader_registers_block_categories(clean_blocks):
    from types import SimpleNamespace
    from events.plugin_loader import PluginLoader
    bc, bt = clean_blocks
    preset = bc.BlocklyConfig(preset_name="dummy")
    module = SimpleNamespace(
        PLUGIN_BLOCK_CATEGORIES=_DUMMY_CATS,
        PLUGIN_BLOCKLY_PRESETS={"dummy": preset},
        PLUGIN_BLOCK_CATEGORY_TRANSLATIONS={"de": {"Dummy Robot": "Attrappe"}},
        PLUGIN_BLOCK_TRANSLATIONS={"dummy_beep": {"name": {"de": "Piep"}, "description": {}}},
    )
    loader = object.__new__(PluginLoader)
    assert PluginLoader._load_block_categories(loader, module) == 2
    assert "Dummy Robot" in bc.BLOCK_REGISTRY and "dummy" in bc.PRESETS
    assert bt.get_translated_category("Dummy Robot", "de") == "Attrappe"
    assert bt.get_translated_block_name("dummy_beep", "de") == "Piep"
    assert PluginLoader._load_block_categories(loader, SimpleNamespace()) == 0
