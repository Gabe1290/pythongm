"""Regression tests: Kivy codegen for the long-tail actions previously
missing from export/Kivy/code_generator.py (docs/DEFERRED_GAPS_2026_PLAN.md
Tier 3) -- move_free, move_towards_point, bounce, stop_sound, check_sound,
draw_scaled_text, fill_color, set_alpha, set_color, set_image_index,
set_image_speed, start_animation, stop_animation, set_room_caption,
check_room, show_info, show_video, open_webpage, splash_show_text,
splash_show_image, save_game, load_game, test_question.

Each of these used to hit the generator's "Unknown action type" default and
export as a silent `pass # TODO`. Mirrors tests/test_kivy_more_actions_export.py's
own `_gen`/`_valid` pattern (compile-gated, no real Kivy needed).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _gen(action_type, params, sprite_paths=None, sound_paths=None, event_type="step"):
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=2, sprite_paths=sprite_paths or {},
                            sound_paths=sound_paths or {})
    g.process_action({"action_type": action_type, "parameters": params}, event_type)
    return g.get_code()


def _valid(src):
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    try:
        compile(wrapper, "<gen>", "exec")
        return True
    except SyntaxError:
        return False


def test_move_free_matches_set_direction_speed():
    out = _gen("move_free", {"direction": "90", "speed": "3"})
    assert "self.direction = 90; self.speed = 3" in out
    assert _valid(out)


def test_move_towards_point_uses_direct_kivy_space_no_flip():
    out = _gen("move_towards_point", {"x": "10", "y": "20", "speed": "4"})
    assert "(10) - self.x" in out
    assert "(20) - self.y" in out
    assert "self.hspeed" in out and "self.vspeed" in out
    assert _valid(out)


def test_move_towards_point_at_target_gives_zero_speed_ternary():
    out = _gen("move_towards_point", {"x": "0", "y": "0", "speed": "4"})
    assert "0 if _mtp_dist == 0 else" in out
    assert _valid(out)


def test_bounce_reverses_larger_component():
    out = _gen("bounce", {})
    assert "abs(self.hspeed) >= abs(self.vspeed)" in out
    assert "-self.hspeed" in out and "-self.vspeed" in out
    assert _valid(out)


def test_stop_sound_resolves_path():
    out = _gen("stop_sound", {"sound": "snd_a"}, sound_paths={"snd_a": "assets/sounds/snd_a.wav"})
    assert "stop_sound('assets/sounds/snd_a.wav')" in out
    assert _valid(out)


def test_stop_sound_unknown_is_honest_noop():
    out = _gen("stop_sound", {"sound": "snd_missing"})
    assert "not found in export" in out
    assert _valid(out)


def test_check_sound_guards_on_is_sound_playing():
    out = _gen("check_sound", {"sound": "snd_a"}, sound_paths={"snd_a": "assets/sounds/snd_a.wav"})
    assert "is_sound_playing" in out
    assert "assets/sounds/snd_a.wav" in out
    assert _valid(out)


def test_check_sound_not_flag_inverts():
    out = _gen("check_sound", {"sound": "snd_a", "not_flag": True},
               sound_paths={"snd_a": "assets/sounds/snd_a.wav"})
    assert "if not _cs_playing(" in out
    assert _valid(out)


def test_draw_scaled_text_queues_scaled_text_command():
    out = _gen("draw_scaled_text", {"text": "hi", "x": "1", "y": "2", "xscale": "2", "yscale": "3"})
    assert "type='scaled_text'" in out
    assert "xscale=2" in out and "yscale=3" in out
    assert _valid(out)


def test_fill_color_queues_fill_command():
    out = _gen("fill_color", {"color": "#112233"})
    assert "type='fill'" in out
    assert "#112233" in out
    assert _valid(out)


def test_set_alpha_clamps():
    out = _gen("set_alpha", {"alpha": "0.5"})
    assert "self.image_alpha" in out
    assert _valid(out)


def test_set_color_sets_blend_and_alpha():
    out = _gen("set_color", {"color": "#ff0000", "alpha": "0.8"})
    assert "self.image_blend = (255, 0, 0)" in out
    assert "self.image_alpha" in out
    assert _valid(out)


def test_set_image_index_and_speed():
    out = _gen("set_image_index", {"frame": "3"})
    assert "self.image_index = float(3)" in out
    assert _valid(out)
    out2 = _gen("set_image_speed", {"speed": "0.5"})
    assert "self.image_speed = float(0.5)" in out2
    assert _valid(out2)


def test_start_and_stop_animation():
    assert "self.image_speed = 1.0" in _gen("start_animation", {})
    assert "self.image_speed = 0.0" in _gen("stop_animation", {})


def test_set_room_caption_reuses_set_window_caption():
    out = _gen("set_room_caption", {"caption": "Hello"})
    assert "set_window_caption(caption='Hello')" in out
    assert _valid(out)


def test_check_room_literal_name():
    out = _gen("check_room", {"room": "room0"})
    assert "ROOM_ORDER" in out
    assert "'room0'" in out
    assert _valid(out)


def test_check_room_sentinels_handled():
    for sentinel in ("__current__", "__next__", "__prev__"):
        out = _gen("check_room", {"room": sentinel})
        assert sentinel in out
        assert _valid(out)


def test_show_info_builds_message_from_project_meta():
    out = _gen("show_info", {})
    assert "PROJECT_META" in out
    assert "show_message" in out
    assert _valid(out)


def test_show_video_calls_system_player_helper():
    out = _gen("show_video", {"filename": "clip.mp4"})
    assert "show_video_file" in out
    assert "clip.mp4" in out
    assert _valid(out)


def test_open_webpage_calls_helper():
    out = _gen("open_webpage", {"url": "https://example.com"})
    assert "open_webpage" in out
    assert "https://example.com" in out
    assert _valid(out)


def test_splash_show_text_reuses_show_message():
    out = _gen("splash_show_text", {"text": "hello"})
    assert "show_message('hello')" in out
    assert _valid(out)


def test_splash_show_image_resolves_sprite_path():
    out = _gen("splash_show_image", {"image": "spr_a"}, sprite_paths={"spr_a": "assets/images/spr_a.png"})
    assert "show_splash_image('assets/images/spr_a.png')" in out
    assert _valid(out)


def test_splash_show_image_unknown_sprite_is_honest_noop():
    out = _gen("splash_show_image", {"image": "spr_missing"})
    assert "not found in export" in out
    assert _valid(out)


def test_save_game_and_load_game():
    out = _gen("save_game", {"filename": "s.sav"})
    assert "from savegame import save_game" in out
    assert _valid(out)
    out2 = _gen("load_game", {"filename": "s.sav"})
    assert "from savegame import load_game" in out2
    assert _valid(out2)


def test_test_question_defaults_true_and_is_documented():
    out = _gen("test_question", {"question": "Continue?"})
    assert "if True:" in out
    assert "Kivy" in out
    assert _valid(out)


def test_all_23_actions_no_longer_hit_the_unsupported_default():
    """End-to-end sanity: none of these fall through to the generic
    'pass # TODO' branch that get_unsupported_actions() tracks."""
    from export.Kivy.code_generator import ActionCodeGenerator, reset_unsupported_actions, get_unsupported_actions
    reset_unsupported_actions()
    actions = [
        "move_free", "move_towards_point", "bounce", "stop_sound", "check_sound",
        "draw_scaled_text", "fill_color", "set_alpha", "set_color",
        "set_image_index", "set_image_speed", "start_animation", "stop_animation",
        "set_room_caption", "check_room", "show_info", "show_video",
        "open_webpage", "splash_show_text", "splash_show_image",
        "save_game", "load_game", "test_question",
    ]
    g = ActionCodeGenerator(base_indent=2)
    for action_type in actions:
        g.process_action({"action_type": action_type, "parameters": {}}, "step")
    assert get_unsupported_actions() == []


def test_real_export_with_all_23_actions_compiles_end_to_end():
    """Not just isolated codegen strings: a full KivyExporter().export() run
    (savegame.py generation, PROJECT_META baking, the image_alpha/
    image_blend base_object.py wiring, the fill draw-queue case) with every
    action present in one object's step event, every generated file
    compiling cleanly."""
    import tempfile
    from export.Kivy.kivy_exporter import KivyExporter

    project_data = {
        "name": "Test Game", "version": "2.1", "author": "Tester",
        "description": "A test.",
        "settings": {"window_width": 320, "window_height": 240},
        "assets": {
            "sprites": {"spr_a": {"file_path": "spr_a.png", "width": 16, "height": 16}},
            "sounds": {"snd_a": {"file_path": "snd_a.wav"}},
            "backgrounds": {},
            "objects": {
                "obj_test": {
                    "name": "obj_test", "sprite": "spr_a",
                    "events": {"step": {"actions": [
                        {"action": "move_free", "parameters": {"direction": "90", "speed": "3"}},
                        {"action": "move_towards_point", "parameters": {"x": "10", "y": "20", "speed": "4"}},
                        {"action": "bounce", "parameters": {}},
                        {"action": "stop_sound", "parameters": {"sound": "snd_a"}},
                        {"action": "check_sound", "parameters": {"sound": "snd_a", "then_actions": [], "else_actions": []}},
                        {"action": "draw_scaled_text", "parameters": {"text": "hi", "x": "1", "y": "2", "xscale": "2", "yscale": "2"}},
                        {"action": "fill_color", "parameters": {"color": "#112233"}},
                        {"action": "set_alpha", "parameters": {"alpha": "0.5"}},
                        {"action": "set_color", "parameters": {"color": "#ff0000", "alpha": "0.8"}},
                        {"action": "set_image_index", "parameters": {"frame": "2"}},
                        {"action": "set_image_speed", "parameters": {"speed": "0.5"}},
                        {"action": "start_animation", "parameters": {}},
                        {"action": "stop_animation", "parameters": {}},
                        {"action": "set_room_caption", "parameters": {"caption": "Hello"}},
                        {"action": "check_room", "parameters": {"room": "room0", "then_actions": [], "else_actions": []}},
                        {"action": "show_info", "parameters": {}},
                        {"action": "show_video", "parameters": {"filename": "clip.mp4"}},
                        {"action": "open_webpage", "parameters": {"url": "https://example.com"}},
                        {"action": "splash_show_text", "parameters": {"text": "splash"}},
                        {"action": "splash_show_image", "parameters": {"image": "spr_a"}},
                        {"action": "save_game", "parameters": {"filename": "s.sav"}},
                        {"action": "load_game", "parameters": {"filename": "s.sav"}},
                        {"action": "test_question", "parameters": {"question": "OK?", "then_actions": [], "else_actions": []}},
                    ]}},
                },
            },
            "rooms": {
                "room0": {"name": "room0", "width": 320, "height": 240,
                          "instances": [{"object_type": "obj_test", "x": 10, "y": 10}]},
            },
        },
        "room_order": ["room0"],
    }

    out = Path(tempfile.mkdtemp(prefix="kivy_tier3_full_")) / "export"
    assert KivyExporter(project_data, Path("."), out).export()

    for rel in ("game/objects/obj_test.py", "game/main.py",
                "game/savegame.py", "game/objects/base_object.py"):
        src = (out / rel).read_text(encoding="utf-8")
        compile(src, rel, "exec")

    main_src = (out / "game" / "main.py").read_text(encoding="utf-8")
    assert "PROJECT_META = " in main_src
    assert "'name': 'Test Game'" in main_src
    assert "def stop_sound(path):" in main_src
    assert "def is_sound_playing(path):" in main_src
    assert "def show_splash_image(sprite_path):" in main_src

    base_src = (out / "game" / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "self.image_alpha = 1.0" in base_src
    assert "self.image_blend = (255, 255, 255)" in base_src
