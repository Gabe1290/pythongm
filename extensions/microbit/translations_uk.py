#!/usr/bin/env python3
"""Ukrainian text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``. Identifiers a student types stay as they are.
"""

ACTIONS = {
    "microbit_show_image": (
        "Показати зображення",
        "Показати зображення на світлодіодах: назва (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) або п'ять рядків цифр яскравості, наприклад "
        "«09090:99999:99999:09990:00900». Зображення стають у чергу."),
    "microbit_scroll_text": (
        "Прокрутити текст",
        "Прокрутити текст на світлодіодному екрані. Візьміть текст у лапки "
        "(\"Привіт\"); інакше дефіс або плюс буде прочитано як обчислення. "
        "Літери з діакритикою показуються як ?, як і на справжній платі."),
    "microbit_show_number": (
        "Показати число",
        "Показати число: одна цифра залишається на місці, довге число прокручується"),
    "microbit_set_pixel": (
        "Увімкнути світлодіод",
        "Одразу ввімкнути світлодіод (x та y від 0 до 4, яскравість від 0 до 9)"),
    "microbit_clear_display": (
        "Очистити екран",
        "Погасити всі світлодіоди та відкинути все, що чекало в черзі"),
    "microbit_set_brightness": (
        "Яскравість екрана",
        "Загальна яскравість світлодіодів: від 0 (вимкнено) до 255 (максимум)"),
    "microbit_play_tone": (
        "Зіграти ноту",
        "Видати сигнал заданої частоти на задану кількість мілісекунд. "
        "Звуки стають у чергу."),
    "microbit_play_melody": (
        "Зіграти мелодію",
        "Зіграти вбудовану мелодію (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) або власні ноти на кшталт «C4:4 E G C5:8 R:4» (нота, "
        "октава, :тривалість; R — пауза)."),
    "microbit_stop_sound": (
        "Зупинити звук",
        "Вимкнути динамік і відкинути звуки, що чекають"),
    "microbit_radio_set_group": (
        "Задати радіогрупу",
        "Вибрати радіогрупу (від 0 до 255). Одна одну чують лише micro:bit "
        "однієї групи; кожна плата починає з групи 0."),
    "microbit_radio_send": (
        "Надіслати радіоповідомлення",
        "Надіслати число або текст іншим micro:bit тієї самої групи (не цій). "
        "Вони отримають подію «Радіоповідомлення отримано», значення буде в "
        "radio_number і radio_string. Візьміть текст у лапки; його обрізають "
        "до 32 символів."),
    "microbit_read_sensor": (
        "Зчитати датчик",
        "Зчитати датчик micro:bit у змінну цього об'єкта (або в глобальну "
        "змінну, якщо назва починається з «global.»)"),
    "microbit_if_button": (
        "Якщо кнопку натиснуто",
        "Істинно, поки кнопку утримують натиснутою (A+B = обидві)"),
    "microbit_if_gesture": (
        "Якщо жест",
        "Істинно, поки плата перебуває в цьому жесті або положенні"),
    "microbit_if_tilt": (
        "Якщо нахил",
        "Порівняти вісь акселерометра (мілі-g, від -2048 до 2048) зі значенням"),
    "microbit_if_pixel": (
        "Якщо яскравість світлодіода",
        "Порівняти яскравість світлодіода (від 0 до 9) зі значенням; за "
        "замовчуванням питання таке: «чи він світиться?»"),
}

PARAMS = {
    "Image": "Зображення",
    "Hold (ms)": "Час показу (мс)",
    "Text": "Текст",
    "Delay per column (ms)": "Затримка на стовпчик (мс)",
    "Number": "Число",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Яскравість (0-9)",
    "Brightness (0-255)": "Яскравість (0-255)",
    "Frequency (Hz)": "Частота (Гц)",
    "Duration (ms)": "Тривалість (мс)",
    "Melody": "Мелодія",
    "Tempo (bpm)": "Темп (уд/хв)",
    "Group (0-255)": "Група (0-255)",
    "Message": "Повідомлення",
    "Sensor": "Датчик",
    "Variable": "Змінна",
    "Button": "Кнопка",
    "Gesture": "Жест",
    "Axis": "Вісь",
    "Comparison": "Порівняння",
    "Value": "Значення",
}

EVENTS = {
    "microbit_button_a": "Кнопку A натиснуто",
    "microbit_button_b": "Кнопку B натиснуто",
    "microbit_button_ab": "Кнопки A+B натиснуто",
    "microbit_logo_touched": "Логотип торкнули",
    "microbit_pin_0": "Контакт 0 торкнули",
    "microbit_pin_1": "Контакт 1 торкнули",
    "microbit_pin_2": "Контакт 2 торкнули",
    "microbit_gesture_shake": "Струс",
    "microbit_gesture_logo_up": "Логотип угору",
    "microbit_gesture_logo_down": "Логотип донизу",
    "microbit_gesture_tilt_left": "Нахил ліворуч",
    "microbit_gesture_tilt_right": "Нахил праворуч",
    "microbit_gesture_screen_up": "Екраном угору",
    "microbit_gesture_screen_down": "Екраном донизу",
    "microbit_gesture_free_fall": "Вільне падіння",
    "microbit_gesture_2g": "Удар 2g",
    "microbit_gesture_3g": "Удар 3g",
    "microbit_gesture_6g": "Удар 6g",
    "microbit_gesture_8g": "Удар 8g",
    "microbit_loud_sound": "Гучний звук",
    "microbit_quiet_sound": "Тихий звук",
    "microbit_display_done": "Показ завершено",
    "microbit_radio_received": "Радіоповідомлення отримано",
    "microbit_sound_done": "Звук завершено",
}
