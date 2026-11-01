#!/usr/bin/env python3
"""Slovenian text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``. Identifiers a student types stay as they are.
The háček letters (č, š, ž) are not optional.
"""

ACTIONS = {
    "microbit_show_image": (
        "Prikaži sliko",
        "Prikaži sliko na LED diodah: ime (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) ali pet vrstic številk svetilnosti, na primer "
        "»09090:99999:99999:09990:00900«. Slike se uvrstijo v čakalno vrsto."),
    "microbit_scroll_text": (
        "Drsi besedilo",
        "Besedilo drsi po zaslonu z LED diodami. Besedilo daj v narekovaje "
        "(\"Živjo\"); sicer se vezaj ali plus prebere kot izračun. Črke s strešico "
        "se prikažejo kot ?, tako kot na pravi ploščici."),
    "microbit_show_number": (
        "Prikaži število",
        "Prikaži število: ena števka ostane pri miru, daljše število drsi"),
    "microbit_set_pixel": (
        "Prižgi LED diodo",
        "Takoj prižgi LED diodo (x in y od 0 do 4, svetilnost od 0 do 9)"),
    "microbit_clear_display": (
        "Počisti zaslon",
        "Ugasni vse LED diode in zavrzi vse, kar je čakalo"),
    "microbit_set_brightness": (
        "Svetilnost zaslona",
        "Splošna svetilnost LED diod, od 0 (ugasnjeno) do 255 (največ)"),
    "microbit_play_tone": (
        "Zaigraj ton",
        "Oddaj pisk z dano frekvenco za dano število milisekund. "
        "Zvoki se uvrstijo v čakalno vrsto."),
    "microbit_play_melody": (
        "Zaigraj melodijo",
        "Zaigraj vgrajeno melodijo (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) ali svoje note, na primer »C4:4 E G C5:8 R:4« (nota, "
        "oktava, :trajanje; R je premor)."),
    "microbit_stop_sound": (
        "Ustavi zvok",
        "Izklopi zvočnik in zavrzi zvoke, ki čakajo"),
    "microbit_radio_set_group": (
        "Nastavi radijsko skupino",
        "Izberi radijsko skupino (od 0 do 255). Slišijo se le micro:biti "
        "iz iste skupine; vsaka ploščica začne v skupini 0."),
    "microbit_radio_send": (
        "Pošlji radijsko sporočilo",
        "Pošlji število ali besedilo drugim micro:bitom iz iste skupine (ne temu). "
        "Prejmejo dogodek »Radijsko sporočilo prejeto«, vrednost je v "
        "radio_number in radio_string. Besedilo daj v narekovaje; skrajša se "
        "na 32 znakov."),
    "microbit_read_sensor": (
        "Preberi tipalo",
        "Preberi tipalo micro:bita v spremenljivko tega predmeta (ali v globalno "
        "spremenljivko, če se ime začne z »global.«)"),
    "microbit_if_button": (
        "Če je tipka pritisnjena",
        "Res, dokler je tipka pridržana (A+B = obe)"),
    "microbit_if_gesture": (
        "Če je poteza",
        "Res, dokler je ploščica v tej potezi ali legi"),
    "microbit_if_tilt": (
        "Če je nagib",
        "Primerjaj os pospeškomera (mili-g, od -2048 do 2048) z vrednostjo"),
    "microbit_if_pixel": (
        "Če je svetilnost LED diode",
        "Primerjaj svetilnost LED diode (od 0 do 9) z vrednostjo; privzeto "
        "je vprašanje »ali sveti?«"),
}

PARAMS = {
    "Image": "Slika",
    "Hold (ms)": "Čas prikaza (ms)",
    "Text": "Besedilo",
    "Delay per column (ms)": "Zakasnitev na stolpec (ms)",
    "Number": "Število",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Svetilnost (0-9)",
    "Brightness (0-255)": "Svetilnost (0-255)",
    "Frequency (Hz)": "Frekvenca (Hz)",
    "Duration (ms)": "Trajanje (ms)",
    "Melody": "Melodija",
    "Tempo (bpm)": "Tempo (udarcev/min)",
    "Group (0-255)": "Skupina (0-255)",
    "Message": "Sporočilo",
    "Sensor": "Tipalo",
    "Variable": "Spremenljivka",
    "Button": "Tipka",
    "Gesture": "Poteza",
    "Axis": "Os",
    "Comparison": "Primerjava",
    "Value": "Vrednost",
}

EVENTS = {
    "microbit_button_a": "Tipka A pritisnjena",
    "microbit_button_b": "Tipka B pritisnjena",
    "microbit_button_ab": "Tipki A+B pritisnjeni",
    "microbit_logo_touched": "Logotip dotaknjen",
    "microbit_pin_0": "Pin 0 dotaknjen",
    "microbit_pin_1": "Pin 1 dotaknjen",
    "microbit_pin_2": "Pin 2 dotaknjen",
    "microbit_gesture_shake": "Stresanje",
    "microbit_gesture_logo_up": "Logotip navzgor",
    "microbit_gesture_logo_down": "Logotip navzdol",
    "microbit_gesture_tilt_left": "Nagib v levo",
    "microbit_gesture_tilt_right": "Nagib v desno",
    "microbit_gesture_screen_up": "Zaslon navzgor",
    "microbit_gesture_screen_down": "Zaslon navzdol",
    "microbit_gesture_free_fall": "Prosti pad",
    "microbit_gesture_2g": "Sunek 2g",
    "microbit_gesture_3g": "Sunek 3g",
    "microbit_gesture_6g": "Sunek 6g",
    "microbit_gesture_8g": "Sunek 8g",
    "microbit_loud_sound": "Glasen zvok",
    "microbit_quiet_sound": "Tih zvok",
    "microbit_display_done": "Prikaz končan",
    "microbit_radio_received": "Radijsko sporočilo prejeto",
    "microbit_sound_done": "Zvok končan",
}
