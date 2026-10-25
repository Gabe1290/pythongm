"""MicrobitSimulator -- the pure board state (docs/MICROBIT_EXTENSION_PLAN.md S2).

No pygame, no GameRunner: these drive the simulator directly. Gesture tests
step one 20 ms sample at a time so the damping counts are exact, rather
than relying on float accumulation of a bigger dt.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.microbit import simulator as simmod  # noqa: E402
from extensions.microbit.font import GLYPHS  # noqa: E402
from extensions.microbit.images import IMAGES  # noqa: E402
from extensions.microbit.simulator import (  # noqa: E402
    GESTURE_DAMPING, MAX_QUEUE, SAMPLE_PERIOD, SCROLL_DELAY, SHAKE_RTX,
    MicrobitSimulator, glyph_image, parse_image, scroll_frames, text_columns,
)

BLANK = [[0] * 5 for _ in range(5)]


def _samples(sim, n):
    """Run n accelerometer samples; return every event they produced."""
    events = []
    for _ in range(n):
        events += sim.update(SAMPLE_PERIOD)
    return events


def _gestures(events):
    return [d for k, d in events if k == "gesture"]


def _settled():
    """A board that has already reported its resting 'face up'."""
    sim = MicrobitSimulator()
    assert _gestures(_samples(sim, GESTURE_DAMPING + 1)) == ["face up"]
    return sim


# ---------------------------------------------------------------------------
# Data tables
# ---------------------------------------------------------------------------

def test_all_64_builtin_images_are_5x5_brightness_grids():
    assert len(IMAGES) == 64
    for name, rows in IMAGES.items():
        assert len(rows) == 5, name
        assert all(len(r) == 5 and set(r) <= {"0", "9"} for r in rows), name
    assert IMAGES["HEART"] == ("09090", "99999", "99999", "09990", "00900")
    assert IMAGES["RABBIT"] and IMAGES["COW"]


def test_font_covers_printable_ascii_with_5_bit_rows():
    assert sorted(GLYPHS) == [chr(c) for c in range(32, 127)]
    assert all(len(rows) == 5 and all(0 <= r < 0x20 for r in rows)
               for rows in GLYPHS.values())


def test_glyph_image_reads_bit_4_as_the_leftmost_column():
    assert glyph_image("A") == [
        [0, 9, 9, 0, 0],
        [9, 0, 0, 9, 0],
        [9, 9, 9, 9, 0],
        [9, 0, 0, 9, 0],
        [9, 0, 0, 9, 0],
    ]
    assert glyph_image(" ") == BLANK


def test_characters_outside_ascii_show_a_question_mark_like_the_device():
    assert glyph_image("é") == glyph_image("?")
    assert glyph_image("\n") == glyph_image("?")


def test_parse_image_accepts_names_in_any_case_and_row_strings():
    heart = [[int(c) for c in r] for r in IMAGES["HEART"]]
    assert parse_image("HEART") == heart
    assert parse_image(" heart ") == heart
    assert parse_image("09090:99999:99999:09990:00900") == heart
    assert parse_image("09090:99999:99999:09990:00900:") == heart
    assert parse_image("12345:00000:00000:00000:00000")[0] == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("bad", [
    "NOT_AN_IMAGE", "", "0909:99999:99999:09990:00900",
    "09090:99999:99999:09990", "0909x:99999:99999:09990:00900", None, 5,
])
def test_parse_image_rejects_anything_else(bad):
    with pytest.raises(ValueError):
        parse_image(bad)


# ---------------------------------------------------------------------------
# Scrolling geometry
# ---------------------------------------------------------------------------

def test_text_columns_are_5_wide_with_a_1_column_gap():
    assert len(text_columns("A")) == 5
    assert len(text_columns("AB")) == 11
    assert text_columns("AB")[5] == [0] * 5
    assert text_columns("") == []


def test_scroll_enters_from_the_right_and_ends_blank():
    frames = scroll_frames("A")
    a = glyph_image("A")
    assert len(frames) == len(text_columns("A")) + 5
    # First frame: only the glyph's first column, on the right edge.
    assert [row[4] for row in frames[0]] == [row[0] for row in a]
    assert all(row[:4] == [0] * 4 for row in frames[0])
    # Fully on screen at frame 4.
    assert frames[4] == a
    assert frames[-1] == BLANK


def test_each_scroll_frame_is_the_previous_shifted_left_by_one():
    frames = scroll_frames("Hi!")
    for prev, cur in zip(frames, frames[1:]):
        assert [row[:4] for row in cur] == [row[1:] for row in prev]


# ---------------------------------------------------------------------------
# Display queue and timing
# ---------------------------------------------------------------------------

def test_set_pixel_clamps_brightness_and_ignores_off_board_coordinates():
    sim = _settled()
    sim.set_pixel(2, 3, 12)
    sim.set_pixel(0, 0, -4)
    sim.set_pixel(5, 0, 9)
    sim.set_pixel(0, -1, 9)
    assert sim.get_pixel(2, 3) == 9 and sim.display[3][2] == 9
    assert sim.get_pixel(0, 0) == 0
    assert sum(map(sum, sim.display)) == 9


def test_brightness_is_clamped_to_0_255():
    sim = _settled()
    assert sim.brightness == 255
    sim.set_brightness(300)
    assert sim.brightness == 255
    sim.set_brightness(-1)
    assert sim.brightness == 0


def test_show_image_appears_at_once_and_reports_done_on_the_next_update():
    sim = _settled()
    sim.show_image("HEART")
    assert sim.display == parse_image("HEART")
    assert sim.update(0) == [("display_done", None)]
    assert sim.display == parse_image("HEART")   # the image stays up
    assert sim.update(1.0) == []                 # done fires only once


def test_scroll_advances_one_column_per_delay():
    sim = _settled()
    frames = scroll_frames("A")
    sim.scroll_text("A")
    assert sim.display == frames[0]
    sim.update(SCROLL_DELAY * 0.99)
    assert sim.display == frames[0]
    sim.update(SCROLL_DELAY * 0.02)
    assert sim.display == frames[1]
    sim.update(SCROLL_DELAY * 3)
    assert sim.display == frames[4]


def test_scroll_finishes_after_one_delay_per_frame_and_leaves_the_display_blank():
    sim = _settled()
    sim.scroll_text("A")
    total = SCROLL_DELAY * len(scroll_frames("A"))
    assert sim.update(total - 0.001) == []
    assert sim.busy
    assert sim.update(0.002) == [("display_done", None)]
    assert not sim.busy and sim.display == BLANK


def test_custom_scroll_delay():
    sim = _settled()
    sim.scroll_text("A", delay=0.5)
    sim.update(0.49)
    assert sim.display == scroll_frames("A")[0]
    sim.update(0.02)
    assert sim.display == scroll_frames("A")[1]


def test_queued_items_play_in_order_like_the_device_waiting_for_the_display():
    sim = _settled()
    sim.show_image("HEART", hold=0.5)
    sim.show_image("SAD")
    assert sim.display == parse_image("HEART")
    assert sim.update(0.4) == []
    assert sim.display == parse_image("HEART")
    assert sim.update(0.2) == [("display_done", None)]
    assert sim.display == parse_image("SAD")


def test_two_scrolls_in_a_row_both_play():
    sim = _settled()
    sim.scroll_text("A")
    sim.scroll_text("B")
    sim.update(SCROLL_DELAY * len(scroll_frames("A")))
    assert sim.busy
    assert sim.display == scroll_frames("B")[0]
    sim.update(SCROLL_DELAY * 4)
    assert sim.display == glyph_image("B")


def test_leftover_time_carries_into_the_next_item():
    sim = _settled()
    sim.show_image("HEART", hold=0.1)
    sim.scroll_text("A")
    sim.update(0.1 + SCROLL_DELAY * 2.5)
    assert sim.display == scroll_frames("A")[2]


def test_an_image_shown_with_no_hold_before_a_scroll_is_replaced_at_once():
    # On the device display.show returns immediately, so the scroll that
    # follows takes over straight away.
    sim = _settled()
    sim.show_image("HEART")
    sim.scroll_text("A")
    assert sim.update(0) == []
    assert sim.display == scroll_frames("A")[0]


def test_showing_what_is_already_up_is_not_a_new_animation():
    # A Step event that shows the same image every frame must not fire
    # display_done every frame.
    sim = _settled()
    sim.show_image("HEART")
    assert sim.update(0) == [("display_done", None)]
    for _ in range(10):
        sim.show_image("HEART")
        assert sim.update(1 / 60) == []


def test_a_repeat_of_the_last_queued_item_is_dropped():
    sim = _settled()
    sim.scroll_text("A")
    sim.scroll_text("B")
    sim.scroll_text("B")
    sim.update(SCROLL_DELAY * (len(scroll_frames("A")) + len(scroll_frames("B"))))
    assert not sim.busy


def test_the_queue_is_bounded():
    sim = _settled()
    results = [sim.scroll_text(str(i % 10) + "x") for i in range(MAX_QUEUE + 3)]
    # Distinct consecutive items, so none were merged as repeats.
    assert results[:MAX_QUEUE] == [True] * MAX_QUEUE
    assert results[MAX_QUEUE:] == [False] * 3


def test_clear_blanks_the_display_and_drops_the_queue_without_a_done_event():
    sim = _settled()
    sim.scroll_text("Hello")
    sim.update(0.3)
    sim.clear()
    assert sim.display == BLANK and not sim.busy
    assert sim.update(5.0) == []


@pytest.mark.parametrize("value,text", [
    (7, "7"), (3.0, "3"), (0, "0"),
])
def test_show_number_shows_a_single_character_still(value, text):
    sim = _settled()
    sim.show_number(value)
    assert sim.display == glyph_image(text)
    assert sim.update(0) == [("display_done", None)]


@pytest.mark.parametrize("value,text", [
    (42, "42"), (-1, "-1"), (2.5, "2.5"), (10.0, "10"),
])
def test_show_number_scrolls_anything_longer(value, text):
    sim = _settled()
    sim.show_number(value)
    assert sim.display == scroll_frames(text)[0]
    sim.update(SCROLL_DELAY * (len(scroll_frames(text)) - 1))
    assert sim.busy


# ---------------------------------------------------------------------------
# Buttons, logo, pins
# ---------------------------------------------------------------------------

def test_button_fires_once_on_press_down():
    sim = _settled()
    sim.set_button("a", True)
    assert sim.update(0) == [("button", "a")]
    sim.set_button("a", True)            # still held
    assert sim.update(0) == []
    sim.set_button("a", False)
    assert sim.update(0) == []
    sim.set_button("A", True)            # any case
    assert sim.update(0) == [("button", "a")]


def test_pressing_the_second_button_while_one_is_held_also_fires_ab():
    sim = _settled()
    sim.set_button("a", True)
    sim.set_button("b", True)
    assert sim.update(0) == [("button", "a"), ("button", "b"), ("button", "ab")]
    assert sim.is_pressed("ab") and sim.is_pressed("a") and sim.is_pressed("b")
    sim.set_button("a", False)
    assert not sim.is_pressed("ab") and sim.is_pressed("b")


def test_unknown_button_or_pin_is_an_error():
    sim = _settled()
    with pytest.raises(ValueError):
        sim.set_button("c", True)
    with pytest.raises(ValueError):
        sim.set_pin_touched(3, True)
    with pytest.raises(ValueError):
        sim.set_pin_analog(5, 10)


def test_logo_and_pins_fire_on_touch_down_only():
    sim = _settled()
    sim.set_logo_touched(True)
    sim.set_logo_touched(True)
    sim.set_pin_touched(1, True)
    assert sim.update(0) == [("logo", "touched"), ("pin", 1)]
    sim.set_logo_touched(False)
    sim.set_pin_touched(1, False)
    assert sim.update(0) == []
    assert not sim.logo_touched and not sim.pins_touched[1]


def test_sensor_setters_clamp_or_wrap():
    sim = _settled()
    sim.set_pin_analog(0, 2000)
    sim.set_light_level(-5)
    sim.set_compass_heading(-10)
    sim.set_temperature(-3)
    assert sim.pins_analog[0] == 1023
    assert sim.light_level == 0
    assert sim.compass_heading == 350
    assert sim.temperature == -3
    sim.set_compass_heading(725)
    assert sim.compass_heading == 5


# ---------------------------------------------------------------------------
# Gestures (codal-core algorithm, 20 ms samples)
# ---------------------------------------------------------------------------

def test_resting_board_reports_face_up_after_the_damping_period():
    sim = MicrobitSimulator()
    # The first sample picks the candidate; GESTURE_DAMPING more confirm it.
    assert _gestures(_samples(sim, GESTURE_DAMPING)) == []
    assert _gestures(_samples(sim, 1)) == ["face up"]
    assert sim.current_gesture == "face up"
    assert _gestures(_samples(sim, 50)) == []


@pytest.mark.parametrize("accel,name", [
    ((-1000, 0, 0), "left"), ((1000, 0, 0), "right"),
    ((0, -1000, 0), "down"), ((0, 1000, 0), "up"),
    ((0, 0, 1000), "face down"), ((0, 0, 0), "freefall"),
])
def test_postures_follow_the_runtime_thresholds(accel, name):
    sim = _settled()
    sim.set_acceleration(*accel)
    assert _gestures(_samples(sim, GESTURE_DAMPING + 1)) == [name]
    assert sim.current_gesture == name


def test_tilt_needs_to_pass_800_mg():
    sim = _settled()
    sim.set_acceleration(-799, 0, -600)
    assert _gestures(_samples(sim, 20)) == []
    sim.set_acceleration(-801, 0, -600)
    assert _gestures(_samples(sim, 20)) == ["left"]


def test_a_brief_tilt_is_filtered_out():
    sim = _settled()
    sim.set_acceleration(-1000, 0, 0)
    assert _gestures(_samples(sim, GESTURE_DAMPING - 1)) == []
    sim.set_acceleration(0, 0, -1024)
    assert _gestures(_samples(sim, 20)) == []


def test_returning_to_rest_reports_face_up_again():
    sim = _settled()
    sim.set_acceleration(1000, 0, 0)
    _samples(sim, 10)
    sim.set_acceleration(0, 0, -1024)
    assert _gestures(_samples(sim, 10)) == ["face up"]


def _shake_per_sample(sim, n):
    """Alternate x between +1000 and -1000 mg; gestures per sample."""
    per_sample = []
    for i in range(n):
        sim.set_acceleration(1000 if i % 2 == 0 else -1000, 0, -1024)
        per_sample.append(_gestures(sim.update(SAMPLE_PERIOD)))
    return per_sample


def _shake(sim, n):
    return [g for sample in _shake_per_sample(sim, n) for g in sample]


def test_four_strong_zero_crossings_make_a_shake():
    sim = _settled()
    assert _shake_per_sample(sim, 4) == [[], [], [], ["shake"]]
    assert sim.current_gesture == "shake"


def test_continued_shaking_only_reports_again_after_the_rearm_time():
    sim = _settled()
    gestures = _shake(sim, 4 + SHAKE_RTX + 4)
    assert gestures.count("shake") == 2


def test_slow_crossings_decay_and_never_make_a_shake():
    sim = _settled()
    events = []
    for i in range(12):
        sim.set_acceleration(1000 if i % 2 == 0 else -1000, 0, -1024)
        events += sim.update(SAMPLE_PERIOD)
        events += _samples(sim, 11)   # longer than the decay period
    assert "shake" not in _gestures(events)


def test_shake_button_fires_once_then_rearms():
    sim = _settled()
    sim.shake()
    sim.shake()
    assert _gestures(sim.update(0)) == ["shake"]
    gestures = _gestures(_samples(sim, SHAKE_RTX - 1))
    sim.shake()
    assert "shake" not in gestures + _gestures(sim.update(0))
    _samples(sim, 2)
    sim.shake()
    assert _gestures(sim.update(0)) == ["shake"]


def test_after_a_shake_the_resting_posture_is_reported_again():
    # codal-core sets the last gesture to SHAKE, so the settled posture
    # differs from it and fires again.
    sim = _settled()
    sim.shake()
    sim.update(0)
    assert _gestures(_samples(sim, 3)) == ["face up"]


def test_impulses_fire_once_per_spike_and_rearm_after_it_subsides():
    sim = _settled()
    sim.set_acceleration(3000, 0, 0)            # between 2g and 3g
    first = _gestures(_samples(sim, 10))
    assert first.count("2g") == 1 and "3g" not in first
    sim.set_acceleration(0, 0, -1024)
    _samples(sim, GESTURE_DAMPING + 2)
    sim.set_acceleration(7000, 0, 0)            # past 6g, below 8g
    second = _gestures(_samples(sim, 1))
    assert [g for g in second if g.endswith("g")] == ["2g", "3g", "6g"]


# ---------------------------------------------------------------------------
# Sound level
# ---------------------------------------------------------------------------

def test_sound_events_cross_the_loud_and_quiet_thresholds_with_hysteresis():
    sim = MicrobitSimulator()
    sim.set_sound_level(50)           # starts quiet: nothing to report
    assert sim.update(0) == []
    sim.set_sound_level(simmod.LOUD_THRESHOLD + 1)
    assert sim.update(0) == [("sound", "loud")]
    sim.set_sound_level(250)
    sim.set_sound_level(150)          # between the thresholds
    assert sim.update(0) == []
    sim.set_sound_level(simmod.QUIET_THRESHOLD - 1)
    assert sim.update(0) == [("sound", "quiet")]
    sim.set_sound_level(0)
    assert sim.update(0) == []
    assert sim.sound_level == 0


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

def test_events_are_returned_once():
    sim = MicrobitSimulator()
    sim.set_button("b", True)
    assert sim.update(0) == [("button", "b")]
    assert sim.update(0) == []


def test_a_long_stall_runs_a_bounded_number_of_samples():
    sim = MicrobitSimulator()
    sim.update(60.0)
    assert sim._sample_clock == 0.0
    assert sim.current_gesture == "face up"
