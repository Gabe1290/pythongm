"""Reference solutions of the Thymio activity sheets (docs/thymio_fiches/), as the action lists a student builds.

Each entry: name -> {"sample": starter project, "events": {event name: [actions]}}. The sheets describe exactly
these programs; tests/test_thymio_fiches.py runs every one of them in the real engine, so a sheet cannot promise a
behaviour the simulator does not have.
"""


def A(action, **params):
    return {"action": action, "parameters": {k: str(v) for k, v in params.items()}}


def IF(condition, *then):
    """A conditional followed by its block, the way the event editor stores it."""
    return [condition, A("start_block"), *then, A("end_block")]


def flat(*parts):
    out = []
    for p in parts:
        out.extend(p if isinstance(p, list) else [p])
    return out


def pressed(button, *then):
    return IF(A("thymio_if_button_pressed", button=button), *then)


def released(button, *then):
    return IF(A("thymio_if_button_released", button=button), *then)


def var_is(name, comparison, value, *then):
    return IF(A("thymio_if_variable", variable=name, comparison=comparison, value=value), *then)


def top(r, g, b):
    return A("thymio_set_led_top", red=r, green=g, blue=b)


FRONT, FRONT_LEFT, FRONT_RIGHT = "2 - Front Center", "1 - Front Left", "3 - Front Right"
LEFT, RIGHT = "0 - Left", "1 - Right"

PROGRAMS = {
    # --- Fiche 1: the four buttons light the top LED ------------------------------------------------------------
    "fiche1_boutons": {
        "sample": "thymio_fiches_1",
        "events": {
            "thymio_button_forward": [top(0, 32, 0)],
            "thymio_button_backward": [top(32, 0, 0)],
            "thymio_button_left": [A("thymio_set_led_bottom_left", red=0, green=0, blue=32)],
            "thymio_button_right": [A("thymio_set_led_bottom_right", red=0, green=0, blue=32)],
            "thymio_button_center": [A("thymio_leds_off")],
        },
    },
    # --- Fiche 2: mixing colours, the circle of eight LEDs ------------------------------------------------------
    "fiche2_couleurs": {
        "sample": "thymio_fiches_1",
        "events": {
            "thymio_button_forward": [top(32, 32, 0)],        # yellow
            "thymio_button_backward": [top(32, 16, 0)],       # orange
            "thymio_button_left": [top(32, 0, 32)],           # magenta
            "thymio_button_right": [top(0, 32, 32)],          # cyan
            "thymio_button_center": [A("thymio_set_led_circle_all", led0=32, led1=0, led2=32, led3=0, led4=32,
                                       led5=0, led6=32, led7=0)],
        },
    },
    # --- Fiche 3: the robot drives while a button is held -------------------------------------------------------
    "fiche3_moteurs": {
        "sample": "thymio_fiches_1",
        "events": {
            "thymio_button_forward": flat(pressed("forward", A("thymio_move_forward", speed=30)),
                                          released("forward", A("thymio_stop_motors"))),
            "thymio_button_backward": flat(pressed("backward", A("thymio_move_backward", speed=30)),
                                           released("backward", A("thymio_stop_motors"))),
            "thymio_button_left": flat(pressed("left", A("thymio_set_motor_speed", left_speed=-30, right_speed=30)),
                                       released("left", A("thymio_stop_motors"))),
            "thymio_button_right": flat(pressed("right", A("thymio_set_motor_speed", left_speed=30, right_speed=-30)),
                                        released("right", A("thymio_stop_motors"))),
        },
    },
    # --- Fiche 4: stop in front of the wall; then go round the boxes --------------------------------------------
    "fiche4_arret_mur": {
        "sample": "thymio_fiches_2",
        "events": {
            "thymio_button_center": pressed("center", A("thymio_move_forward", speed=40)),
            "thymio_proximity_update": flat(
                IF(A("thymio_if_proximity", sensor_index=FRONT, threshold=1000, comparison=">"),
                   A("thymio_stop_motors"), top(32, 0, 0)),
            ),
        },
    },
    "fiche4_evitement": {
        "sample": "thymio_fiches_2",
        "events": {
            "thymio_button_center": pressed("center", A("thymio_move_forward", speed=40)),
            # forward by default, then the sensors take over: the LAST order of the pass wins
            "thymio_proximity_update": flat(
                A("thymio_move_forward", speed=40), top(0, 32, 0),
                IF(A("thymio_if_proximity", sensor_index=FRONT_RIGHT, threshold=250, comparison=">"),
                   A("thymio_set_motor_speed", left_speed=-30, right_speed=30), top(32, 16, 0)),
                IF(A("thymio_if_proximity", sensor_index=FRONT_LEFT, threshold=250, comparison=">"),
                   A("thymio_set_motor_speed", left_speed=30, right_speed=-30), top(32, 16, 0)),
                IF(A("thymio_if_proximity", sensor_index=FRONT, threshold=250, comparison=">"),
                   A("thymio_set_motor_speed", left_speed=30, right_speed=-30), top(32, 16, 0)),
            ),
        },
    },
    # --- Fiche 5: the ground sensors -----------------------------------------------------------------------------
    "fiche5_ruban": {
        "sample": "thymio_fiches_3",
        "events": {
            "thymio_button_center": pressed("center", A("thymio_move_forward", speed=40)),
            "thymio_ground_update": flat(
                IF(A("thymio_if_ground_dark", sensor_index=LEFT, threshold=300),
                   A("thymio_stop_motors"), top(32, 0, 0)),
            ),
        },
    },
    # --- Fiche 6: a counter (variable) shown by a colour --------------------------------------------------------
    "fiche6_compteur": {
        "sample": "thymio_fiches_1",
        "events": {
            "thymio_button_forward": flat(
                pressed("forward", A("thymio_increase_variable", variable="compteur", amount=1)),
                var_is("compteur", ">=", 3, top(0, 32, 0)),
                var_is("compteur", "<", 3, top(32, 0, 0))),
            "thymio_button_backward": flat(
                pressed("backward", A("thymio_decrease_variable", variable="compteur", amount=1)),
                var_is("compteur", ">=", 3, top(0, 32, 0)),
                var_is("compteur", "<", 3, top(32, 0, 0))),
            "thymio_button_center": flat(
                pressed("center", A("thymio_set_variable", variable="compteur", value=0), top(32, 0, 0))),
        },
    },
    # --- Fiche 7: a timer makes the LED blink; then the robot draws a square ------------------------------------
    "fiche7_clignotant": {
        "sample": "thymio_fiches_1",
        "events": {
            "thymio_button_center": pressed("center", A("thymio_set_variable", variable="etat", value=0),
                                      A("thymio_set_timer_period", timer_id=0, period=500)),
            "thymio_timer_0": flat(
                A("thymio_increase_variable", variable="etat", amount=1),
                var_is("etat", "==", 1, top(0, 0, 32)),
                var_is("etat", "==", 2, A("thymio_leds_off"), A("thymio_set_variable", variable="etat", value=0))),
        },
    },
    "fiche7_carre": {
        "sample": "thymio_fiches_1",
        "events": {
            "thymio_button_center": pressed("center", A("thymio_set_variable", variable="etat", value=0),
                                      A("thymio_set_timer_period", timer_id=0, period=1040)),
            "thymio_timer_0": flat(
                A("thymio_increase_variable", variable="etat", amount=1),
                var_is("etat", "==", 1, A("thymio_move_forward", speed=30)),
                var_is("etat", "==", 2, A("thymio_set_motor_speed", left_speed=-30, right_speed=30),
                       A("thymio_set_variable", variable="etat", value=0))),
        },
    },
}

# --- Fiche 8: challenges ---------------------------------------------------------------------------------------------
PROGRAMS["fiche9_feu"] = {                        # traffic light: green, orange, red, every second
    "sample": "thymio_fiches_1",
    "events": {
        "thymio_button_center": pressed("center", A("thymio_set_variable", variable="etat", value=0),
                                      A("thymio_set_timer_period", timer_id=0, period=1000)),
        "thymio_button_backward": pressed("backward", A("thymio_set_timer_period", timer_id=0, period=0),
                                          A("thymio_leds_off")),
        "thymio_timer_0": flat(
            A("thymio_increase_variable", variable="etat", amount=1),
            var_is("etat", "==", 1, top(0, 32, 0)),
            var_is("etat", "==", 2, top(32, 16, 0)),
            var_is("etat", "==", 3, top(32, 0, 0), A("thymio_set_variable", variable="etat", value=0))),
    },
}

_drive = PROGRAMS["fiche3_moteurs"]["events"]
PROGRAMS["fiche9_alarme"] = {                     # drive by hand; the LED says how close the obstacle is
    "sample": "thymio_fiches_2",
    "events": {
        **_drive,
        "thymio_proximity_update": flat(
            top(0, 32, 0),
            IF(A("thymio_if_proximity", sensor_index=FRONT, threshold=250, comparison=">"), top(32, 16, 0)),
            IF(A("thymio_if_proximity", sensor_index=FRONT, threshold=1000, comparison=">"), top(32, 0, 0))),
    },
}

PROGRAMS["fiche9_sablier"] = {                    # an hourglass: one more LED of the circle every second
    "sample": "thymio_fiches_1",
    "events": {
        "thymio_button_center": pressed("center", A("thymio_set_variable", variable="etat", value=0),
                                      A("thymio_set_timer_period", timer_id=0, period=1000)),
        "thymio_timer_0": flat(
            A("thymio_increase_variable", variable="etat", amount=1),
            var_is("etat", "==", 1, A("thymio_set_led_circle", led_index=0, intensity=32)),
            var_is("etat", "==", 2, A("thymio_set_led_circle", led_index=2, intensity=32)),
            var_is("etat", "==", 3, A("thymio_set_led_circle", led_index=4, intensity=32)),
            var_is("etat", "==", 4, A("thymio_set_led_circle", led_index=6, intensity=32)),
            var_is("etat", "==", 5, A("thymio_leds_off"), A("thymio_set_variable", variable="etat", value=0))),
    },
}


# --- Fiche 8: sounds (the computer's speaker plays what the robot's would) -------------------------------------------
def tone(freq, frames):
    return A("thymio_play_tone", frequency=freq, duration=frames)


def system_sound(label):
    return A("thymio_play_system_sound", sound_id=label)


PROGRAMS["fiche8_sons_notes"] = {                 # four buttons, four notes (do, mi, sol, do aigu)
    "sample": "thymio_fiches_1",
    "events": {
        "thymio_button_forward": pressed("forward", tone(262, 30)),
        "thymio_button_left": pressed("left", tone(330, 30)),
        "thymio_button_right": pressed("right", tone(392, 30)),
        "thymio_button_backward": pressed("backward", tone(523, 30)),
    },
}

PROGRAMS["fiche8_sons_tenu"] = {                  # the note lasts while the button is held
    "sample": "thymio_fiches_1",
    "events": {
        "thymio_button_forward": flat(pressed("forward", tone(440, -1)),
                                      released("forward", A("thymio_stop_sound"))),
    },
}

PROGRAMS["fiche8_sons_melodie"] = {               # do, mi, sol, do aigu: each note starts when the previous one ends
    "sample": "thymio_fiches_1",
    "events": {
        "thymio_button_center": pressed("center", A("thymio_set_variable", variable="note", value=0),
                                        tone(262, 20)),
        "thymio_sound_finished": flat(
            A("thymio_increase_variable", variable="note", amount=1),
            var_is("note", "==", 1, tone(330, 20)),
            var_is("note", "==", 2, tone(392, 20)),
            var_is("note", "==", 3, tone(523, 40))),
    },
}

PROGRAMS["fiche8_sons_systeme"] = {               # the factory sounds
    "sample": "thymio_fiches_1",
    "events": {
        "thymio_button_forward": pressed("forward", system_sound("2 - Arrow")),
        "thymio_button_backward": pressed("backward", system_sound("5 - Collision")),
        "thymio_button_left": pressed("left", system_sound("0 - Startup")),
        "thymio_button_right": pressed("right", system_sound("6 - Target Friendly")),
        "thymio_button_center": pressed("center", system_sound("7 - Target Detected")),
    },
}

PROGRAMS["fiche8_sirene"] = {                     # a two-tone siren with a flashing light
    "sample": "thymio_fiches_1",
    "events": {
        "thymio_button_center": pressed("center", A("thymio_set_variable", variable="etat", value=0),
                                        A("thymio_set_timer_period", timer_id=0, period=500)),
        "thymio_timer_0": flat(
            A("thymio_increase_variable", variable="etat", amount=1),
            var_is("etat", "==", 1, tone(440, 30), top(32, 0, 0)),
            var_is("etat", "==", 2, tone(880, 30), top(0, 0, 32), A("thymio_set_variable", variable="etat", value=0))),
    },
}

PROGRAMS["fiche8_radar"] = {                      # parking sensor: faster, higher beeps as the obstacle gets close
    "sample": "thymio_fiches_2",
    "events": {
        **PROGRAMS["fiche3_moteurs"]["events"],
        "thymio_proximity_update": flat(
            IF(A("thymio_if_proximity", sensor_index=FRONT, threshold=250, comparison=">"), tone(800, 4)),
            IF(A("thymio_if_proximity", sensor_index=FRONT, threshold=1000, comparison=">"), tone(1500, 4))),
    },
}
