#!/usr/bin/env python3
"""Spanish text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``: block label + tooltip per action, the parameter
labels, and the drop-down labels of its events. Identifiers a student types stay as they
are. Accents and ñ are not optional.
"""

ACTIONS = {
    "microbit_show_image": (
        "Mostrar una imagen",
        "Mostrar una imagen en los LED: un nombre (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) o cinco filas de cifras de brillo como "
        "«09090:99999:99999:09990:00900». Las imágenes se ponen en cola."),
    "microbit_scroll_text": (
        "Desplazar un texto",
        "Desplazar un texto por la pantalla de LED. Pon el texto entre comillas "
        "(\"Hola\"); si no, un guion o un signo más se lee como un cálculo. Las "
        "letras con acento se muestran como ? igual que en la placa real."),
    "microbit_show_number": (
        "Mostrar un número",
        "Mostrar un número: una cifra se queda fija, un número más largo se desplaza"),
    "microbit_set_pixel": (
        "Encender un LED",
        "Encender un LED al instante (x e y de 0 a 4, brillo de 0 a 9)"),
    "microbit_clear_display": (
        "Borrar la pantalla",
        "Apagar todos los LED y descartar lo que estaba en espera"),
    "microbit_set_brightness": (
        "Brillo de la pantalla",
        "Brillo general de los LED, de 0 (apagado) a 255 (máximo)"),
    "microbit_play_tone": (
        "Tocar una nota",
        "Emitir un pitido a una frecuencia durante un número de milisegundos. "
        "Los sonidos se ponen en cola."),
    "microbit_play_melody": (
        "Tocar una melodía",
        "Tocar una melodía incorporada (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) o tus propias notas como «C4:4 E G C5:8 R:4» (nota, "
        "octava, :duración; R es un silencio)."),
    "microbit_stop_sound": (
        "Detener el sonido",
        "Apagar el altavoz y descartar los sonidos en espera"),
    "microbit_radio_set_group": (
        "Elegir el grupo de radio",
        "Elegir el grupo de radio (0 a 255). Solo las micro:bit del mismo grupo "
        "se oyen entre sí; cada placa empieza en el grupo 0."),
    "microbit_radio_send": (
        "Enviar un mensaje por radio",
        "Enviar un número o un texto a las demás micro:bit del mismo grupo (no a "
        "esta). Reciben el evento «Mensaje de radio recibido», con el valor en "
        "radio_number y radio_string. Pon el texto entre comillas; se corta a "
        "32 caracteres."),
    "microbit_read_sensor": (
        "Leer un sensor",
        "Leer un sensor de la micro:bit en una variable de este objeto (o en una "
        "variable global si el nombre empieza por «global.»)"),
    "microbit_if_button": (
        "Si el botón está pulsado",
        "Verdadero mientras se mantiene pulsado el botón (A+B = los dos)"),
    "microbit_if_gesture": (
        "Si hay un gesto",
        "Verdadero mientras la placa está en ese gesto o posición"),
    "microbit_if_tilt": (
        "Si hay inclinación",
        "Comparar un eje del acelerómetro (mili-g, de -2048 a 2048) con un valor"),
    "microbit_if_pixel": (
        "Si el brillo del LED",
        "Comparar el brillo de un LED (0 a 9) con un valor; por defecto, "
        "la pregunta es «¿está encendido?»"),
}

PARAMS = {
    "Image": "Imagen",
    "Hold (ms)": "Duración (ms)",
    "Text": "Texto",
    "Delay per column (ms)": "Retardo por columna (ms)",
    "Number": "Número",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Brillo (0-9)",
    "Brightness (0-255)": "Brillo (0-255)",
    "Frequency (Hz)": "Frecuencia (Hz)",
    "Duration (ms)": "Duración (ms)",
    "Melody": "Melodía",
    "Tempo (bpm)": "Tempo (bpm)",
    "Group (0-255)": "Grupo (0-255)",
    "Message": "Mensaje",
    "Sensor": "Sensor",
    "Variable": "Variable",
    "Button": "Botón",
    "Gesture": "Gesto",
    "Axis": "Eje",
    "Comparison": "Comparación",
    "Value": "Valor",
}

EVENTS = {
    "microbit_button_a": "Botón A pulsado",
    "microbit_button_b": "Botón B pulsado",
    "microbit_button_ab": "Botones A+B pulsados",
    "microbit_logo_touched": "Logotipo tocado",
    "microbit_pin_0": "Pin 0 tocado",
    "microbit_pin_1": "Pin 1 tocado",
    "microbit_pin_2": "Pin 2 tocado",
    "microbit_gesture_shake": "Sacudida",
    "microbit_gesture_logo_up": "Logotipo hacia arriba",
    "microbit_gesture_logo_down": "Logotipo hacia abajo",
    "microbit_gesture_tilt_left": "Inclinada a la izquierda",
    "microbit_gesture_tilt_right": "Inclinada a la derecha",
    "microbit_gesture_screen_up": "Pantalla hacia arriba",
    "microbit_gesture_screen_down": "Pantalla hacia abajo",
    "microbit_gesture_free_fall": "Caída libre",
    "microbit_gesture_2g": "Golpe de 2g",
    "microbit_gesture_3g": "Golpe de 3g",
    "microbit_gesture_6g": "Golpe de 6g",
    "microbit_gesture_8g": "Golpe de 8g",
    "microbit_loud_sound": "Sonido fuerte",
    "microbit_quiet_sound": "Sonido débil",
    "microbit_display_done": "Pantalla terminada",
    "microbit_radio_received": "Mensaje de radio recibido",
    "microbit_sound_done": "Sonido terminado",
}
