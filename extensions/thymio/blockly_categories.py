#!/usr/bin/env python3
"""Thymio's Blockly toolbox categories, preset and category translations
(docs/THYMIO_EXTENSION_PLAN.md, Stage F).

Moved verbatim out of ``config/blockly_config.py``'s ``BLOCK_REGISTRY`` /
``BlocklyConfig.get_thymio()`` / ``PRESETS`` and ``config/blockly_translations.py``'s
``CATEGORY_TRANSLATIONS``.

The preset can't be built the way ``get_thymio()`` built it -- with
``BlocklyConfig().enable_category("Thymio Motors")`` etc. -- because
``enable_category()`` only populates ``enabled_blocks`` when the category is
already a key in the *global* ``BLOCK_REGISTRY``, and this module (so
``PLUGIN_BLOCKLY_PRESETS``) is evaluated at extension *import* time, which
happens before ``events/plugin_loader.py``'s ``_load_block_categories`` calls
``register_block_categories(PLUGIN_BLOCK_CATEGORIES)`` to merge these
categories into ``BLOCK_REGISTRY``. Built eagerly the old way, the preset
would end up with the right ``enabled_categories`` but an empty
``enabled_blocks`` for every Thymio category -- silently broken. Building it
directly from the local ``PLUGIN_BLOCK_CATEGORIES`` dict below sidesteps the
ordering hazard entirely.
"""

from config.blockly_config import BlocklyConfig

PLUGIN_BLOCK_CATEGORIES = {
    "Thymio Events": [
        {"type": "thymio_button_forward", "name": "Forward Button", "description": "Forward button pressed", "implemented": True},
        {"type": "thymio_button_backward", "name": "Backward Button", "description": "Backward button pressed", "implemented": True},
        {"type": "thymio_button_left", "name": "Left Button", "description": "Left button pressed", "implemented": True},
        {"type": "thymio_button_right", "name": "Right Button", "description": "Right button pressed", "implemented": True},
        {"type": "thymio_button_center", "name": "Center Button", "description": "Center button pressed", "implemented": True},
        {"type": "thymio_any_button", "name": "Any Button", "description": "Any button state changed", "implemented": True},
        {"type": "thymio_proximity_update", "name": "Proximity Update", "description": "Proximity sensors updated (10 Hz)", "implemented": True},
        {"type": "thymio_ground_update", "name": "Ground Update", "description": "Ground sensors updated (10 Hz)", "implemented": True},
        {"type": "thymio_timer_0", "name": "Timer 0", "description": "Timer 0 triggered", "implemented": True},
        {"type": "thymio_timer_1", "name": "Timer 1", "description": "Timer 1 triggered", "implemented": True},
        {"type": "thymio_tap", "name": "Tap Detected", "description": "Robot tapped/shaken", "implemented": True},
        {"type": "thymio_sound_detected", "name": "Sound Detected", "description": "Microphone threshold exceeded", "implemented": True},
        {"type": "thymio_sound_finished", "name": "Sound Finished", "description": "Sound playback completed", "implemented": True},
        {"type": "thymio_message_received", "name": "Message Received", "description": "IR message received", "implemented": True},
    ],
    "Thymio Motors": [
        {"type": "thymio_set_motor_speed", "name": "Set Motor Speeds", "description": "Set left and right motor speeds", "implemented": True},
        {"type": "thymio_move_forward", "name": "Move Forward", "description": "Move forward at speed", "implemented": True},
        {"type": "thymio_move_backward", "name": "Move Backward", "description": "Move backward at speed", "implemented": True},
        {"type": "thymio_turn_left", "name": "Turn Left", "description": "Turn left at speed", "implemented": True},
        {"type": "thymio_turn_right", "name": "Turn Right", "description": "Turn right at speed", "implemented": True},
        {"type": "thymio_stop_motors", "name": "Stop Motors", "description": "Stop both motors", "implemented": True},
    ],
    "Thymio LEDs": [
        {"type": "thymio_set_led_top", "name": "Set Top LED", "description": "Set top RGB LED color", "implemented": True},
        {"type": "thymio_set_led_bottom_left", "name": "Set Bottom Left LED", "description": "Set bottom left RGB LED", "implemented": True},
        {"type": "thymio_set_led_bottom_right", "name": "Set Bottom Right LED", "description": "Set bottom right RGB LED", "implemented": True},
        {"type": "thymio_set_led_circle", "name": "Set Circle LED", "description": "Set one circle LED", "implemented": True},
        {"type": "thymio_set_led_circle_all", "name": "Set All Circle LEDs", "description": "Set all 8 circle LEDs", "implemented": True},
        {"type": "thymio_leds_off", "name": "Turn Off LEDs", "description": "Turn off all LEDs", "implemented": True},
    ],
    "Thymio Sound": [
        {"type": "thymio_play_tone", "name": "Play Tone", "description": "Play frequency tone", "implemented": True},
        {"type": "thymio_play_system_sound", "name": "Play System Sound", "description": "Play built-in sound", "implemented": True},
        {"type": "thymio_stop_sound", "name": "Stop Sound", "description": "Stop sound playback", "implemented": True},
    ],
    "Thymio Sensors": [
        {"type": "thymio_read_proximity", "name": "Read Proximity", "description": "Read proximity sensor value", "implemented": True},
        {"type": "thymio_read_ground", "name": "Read Ground", "description": "Read ground sensor value", "implemented": True},
        {"type": "thymio_read_button", "name": "Read Button", "description": "Read button state", "implemented": True},
    ],
    "Thymio Conditions": [
        {"type": "thymio_if_proximity", "name": "If Proximity", "description": "Check proximity sensor", "implemented": True},
        {"type": "thymio_if_ground_dark", "name": "If Ground Dark", "description": "Check if ground is dark", "implemented": True},
        {"type": "thymio_if_ground_light", "name": "If Ground Light", "description": "Check if ground is light", "implemented": True},
        {"type": "thymio_if_button_pressed", "name": "If Button Pressed", "description": "Check if button pressed", "implemented": True},
        {"type": "thymio_if_button_released", "name": "If Button Released", "description": "Check if button released", "implemented": True},
        {"type": "thymio_if_variable", "name": "If Variable", "description": "Check variable condition", "implemented": True},
    ],
    "Thymio Timers": [
        {"type": "thymio_set_timer_period", "name": "Set Timer Period", "description": "Set timer period (ms)", "implemented": True},
    ],
    "Thymio Variables": [
        {"type": "thymio_set_variable", "name": "Set Variable", "description": "Set variable value", "implemented": True},
        {"type": "thymio_increase_variable", "name": "Increase Variable", "description": "Increment variable", "implemented": True},
        {"type": "thymio_decrease_variable", "name": "Decrease Variable", "description": "Decrement variable", "implemented": True},
    ],
}


def _build_thymio_preset() -> BlocklyConfig:
    """Same shape as the old ``BlocklyConfig.get_thymio()`` classmethod, built
    without going through ``enable_category()`` / the global ``BLOCK_REGISTRY``
    (see module docstring)."""
    config = BlocklyConfig(preset_name="thymio")
    config.enabled_blocks.add("event_create")
    for category, blocks in PLUGIN_BLOCK_CATEGORIES.items():
        config.enabled_categories.add(category)
        for block in blocks:
            config.enabled_blocks.add(block["type"])
    config.enabled_blocks.update({"start_block", "end_block", "else_action"})
    return config


PLUGIN_BLOCKLY_PRESETS = {"thymio": _build_thymio_preset()}

PLUGIN_BLOCK_CATEGORY_TRANSLATIONS = {
    "de": {
        "Thymio Events": "Thymio Ereignisse",
        "Thymio Motors": "Thymio Motoren",
        "Thymio LEDs": "Thymio LEDs",
        "Thymio Sound": "Thymio Klang",
        "Thymio Sensors": "Thymio Sensoren",
        "Thymio Conditions": "Thymio Bedingungen",
        "Thymio Timers": "Thymio Timer",
        "Thymio Variables": "Thymio Variablen",
    },
    "es": {
        "Thymio Events": "Eventos Thymio",
        "Thymio Motors": "Motores Thymio",
        "Thymio LEDs": "LEDs Thymio",
        "Thymio Sound": "Sonido Thymio",
        "Thymio Sensors": "Sensores Thymio",
        "Thymio Conditions": "Condiciones Thymio",
        "Thymio Timers": "Temporizadores Thymio",
        "Thymio Variables": "Variables Thymio",
    },
    "fr": {
        "Thymio Events": "Événements Thymio",
        "Thymio Motors": "Moteurs Thymio",
        "Thymio LEDs": "LEDs Thymio",
        "Thymio Sound": "Son Thymio",
        "Thymio Sensors": "Capteurs Thymio",
        "Thymio Conditions": "Conditions Thymio",
        "Thymio Timers": "Minuteries Thymio",
        "Thymio Variables": "Variables Thymio",
    },
    "it": {
        "Thymio Events": "Eventi Thymio",
        "Thymio Motors": "Motori Thymio",
        "Thymio LEDs": "LED Thymio",
        "Thymio Sound": "Suono Thymio",
        "Thymio Sensors": "Sensori Thymio",
        "Thymio Conditions": "Condizioni Thymio",
        "Thymio Timers": "Timer Thymio",
        "Thymio Variables": "Variabili Thymio",
    },
    "ru": {
        "Thymio Events": "События Thymio",
        "Thymio Motors": "Моторы Thymio",
        "Thymio LEDs": "Светодиоды Thymio",
        "Thymio Sound": "Звук Thymio",
        "Thymio Sensors": "Датчики Thymio",
        "Thymio Conditions": "Условия Thymio",
        "Thymio Timers": "Таймеры Thymio",
        "Thymio Variables": "Переменные Thymio",
    },
    "sl": {
        "Thymio Events": "Dogodki Thymio",
        "Thymio Motors": "Motorji Thymio",
        "Thymio LEDs": "LED diode Thymio",
        "Thymio Sound": "Zvok Thymio",
        "Thymio Sensors": "Senzorji Thymio",
        "Thymio Conditions": "Pogoji Thymio",
        "Thymio Timers": "Časovniki Thymio",
        "Thymio Variables": "Spremenljivke Thymio",
    },
    "uk": {
        "Thymio Events": "Події Thymio",
        "Thymio Motors": "Мотори Thymio",
        "Thymio LEDs": "Світлодіоди Thymio",
        "Thymio Sound": "Звук Thymio",
        "Thymio Sensors": "Датчики Thymio",
        "Thymio Conditions": "Умови Thymio",
        "Thymio Timers": "Таймери Thymio",
        "Thymio Variables": "Змінні Thymio",
    },
}
