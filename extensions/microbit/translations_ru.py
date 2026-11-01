#!/usr/bin/env python3
"""Russian text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``. Identifiers a student types stay as they are.
"""

ACTIONS = {
    "microbit_show_image": (
        "Показать картинку",
        "Показать картинку на светодиодах: имя (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) или пять строк цифр яркости, например "
        "«09090:99999:99999:09990:00900». Картинки встают в очередь."),
    "microbit_scroll_text": (
        "Прокрутить текст",
        "Прокрутить текст на светодиодном экране. Заключите текст в кавычки "
        "(\"Привет\"); иначе дефис или плюс будет прочитан как вычисление. "
        "Кириллица и буквы с диакритикой показываются как ?, как на настоящей плате."),
    "microbit_show_number": (
        "Показать число",
        "Показать число: одна цифра остаётся на месте, длинное число прокручивается"),
    "microbit_set_pixel": (
        "Включить светодиод",
        "Сразу включить светодиод (x и y от 0 до 4, яркость от 0 до 9)"),
    "microbit_clear_display": (
        "Очистить экран",
        "Погасить все светодиоды и отбросить всё, что ждало в очереди"),
    "microbit_set_brightness": (
        "Яркость экрана",
        "Общая яркость светодиодов: от 0 (выключено) до 255 (максимум)"),
    "microbit_play_tone": (
        "Сыграть ноту",
        "Издать сигнал заданной частоты на заданное число миллисекунд. "
        "Звуки встают в очередь."),
    "microbit_play_melody": (
        "Сыграть мелодию",
        "Сыграть встроенную мелодию (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) или свои ноты вроде «C4:4 E G C5:8 R:4» (нота, "
        "октава, :длительность; R — пауза)."),
    "microbit_stop_sound": (
        "Остановить звук",
        "Выключить динамик и отбросить ожидающие звуки"),
    "microbit_radio_set_group": (
        "Задать радиогруппу",
        "Выбрать радиогруппу (от 0 до 255). Друг друга слышат только micro:bit "
        "одной группы; каждая плата начинает с группы 0."),
    "microbit_radio_send": (
        "Отправить радиосообщение",
        "Отправить число или текст другим micro:bit той же группы (не этой). "
        "Они получат событие «Радиосообщение получено», значение будет в "
        "radio_number и radio_string. Заключите текст в кавычки; он обрезается "
        "до 32 символов."),
    "microbit_read_sensor": (
        "Считать датчик",
        "Считать датчик micro:bit в переменную этого объекта (или в глобальную "
        "переменную, если имя начинается с «global.»)"),
    "microbit_if_button": (
        "Если кнопка нажата",
        "Истинно, пока кнопка удерживается нажатой (A+B = обе)"),
    "microbit_if_gesture": (
        "Если жест",
        "Истинно, пока плата находится в этом жесте или положении"),
    "microbit_if_tilt": (
        "Если наклон",
        "Сравнить ось акселерометра (милли-g, от -2048 до 2048) со значением"),
    "microbit_if_pixel": (
        "Если яркость светодиода",
        "Сравнить яркость светодиода (от 0 до 9) со значением; по умолчанию "
        "вопрос такой: «горит ли он?»"),
}

PARAMS = {
    "Image": "Картинка",
    "Hold (ms)": "Время показа (мс)",
    "Text": "Текст",
    "Delay per column (ms)": "Задержка на столбец (мс)",
    "Number": "Число",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Яркость (0-9)",
    "Brightness (0-255)": "Яркость (0-255)",
    "Frequency (Hz)": "Частота (Гц)",
    "Duration (ms)": "Длительность (мс)",
    "Melody": "Мелодия",
    "Tempo (bpm)": "Темп (уд/мин)",
    "Group (0-255)": "Группа (0-255)",
    "Message": "Сообщение",
    "Sensor": "Датчик",
    "Variable": "Переменная",
    "Button": "Кнопка",
    "Gesture": "Жест",
    "Axis": "Ось",
    "Comparison": "Сравнение",
    "Value": "Значение",
}

EVENTS = {
    "microbit_button_a": "Кнопка A нажата",
    "microbit_button_b": "Кнопка B нажата",
    "microbit_button_ab": "Кнопки A+B нажаты",
    "microbit_logo_touched": "Логотип тронут",
    "microbit_pin_0": "Контакт 0 тронут",
    "microbit_pin_1": "Контакт 1 тронут",
    "microbit_pin_2": "Контакт 2 тронут",
    "microbit_gesture_shake": "Встряхивание",
    "microbit_gesture_logo_up": "Логотип вверх",
    "microbit_gesture_logo_down": "Логотип вниз",
    "microbit_gesture_tilt_left": "Наклон влево",
    "microbit_gesture_tilt_right": "Наклон вправо",
    "microbit_gesture_screen_up": "Экраном вверх",
    "microbit_gesture_screen_down": "Экраном вниз",
    "microbit_gesture_free_fall": "Свободное падение",
    "microbit_gesture_2g": "Удар 2g",
    "microbit_gesture_3g": "Удар 3g",
    "microbit_gesture_6g": "Удар 6g",
    "microbit_gesture_8g": "Удар 8g",
    "microbit_loud_sound": "Громкий звук",
    "microbit_quiet_sound": "Тихий звук",
    "microbit_display_done": "Показ завершён",
    "microbit_radio_received": "Радиосообщение получено",
    "microbit_sound_done": "Звук завершён",
}
