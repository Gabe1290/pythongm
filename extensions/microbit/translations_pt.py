#!/usr/bin/env python3
"""Portuguese text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``. Brazilian Portuguese, matching the IDE's own pt UI translation (arquivo, clique, tela). Identifiers a student types stay as they are.
Accents and cedillas are not optional.
"""

ACTIONS = {
    "microbit_show_image": (
        "Mostrar uma imagem",
        "Mostrar uma imagem nos LEDs: um nome (HEART, HAPPY, SAD, YES, NO, "
        "ARROW_N, SKULL…) ou cinco linhas de dígitos de brilho como "
        "«09090:99999:99999:09990:00900». As imagens ficam em fila."),
    "microbit_scroll_text": (
        "Rolar um texto",
        "Rolar um texto na tela de LEDs. Coloque o texto entre aspas "
        "(\"Olá\"); caso contrário, um hífen ou um sinal de mais é lido como um cálculo. "
        "As letras acentuadas aparecem como ? tal como na placa verdadeira."),
    "microbit_show_number": (
        "Mostrar um número",
        "Mostrar um número: um dígito fica fixo, um número mais longo rola"),
    "microbit_set_pixel": (
        "Acender um LED",
        "Acender um LED de imediato (x e y de 0 a 4, brilho de 0 a 9)"),
    "microbit_clear_display": (
        "Limpar a tela",
        "Apagar todos os LED e descartar o que estava em espera"),
    "microbit_set_brightness": (
        "Brilho da tela",
        "Brilho geral dos LED, de 0 (apagado) a 255 (máximo)"),
    "microbit_play_tone": (
        "Tocar uma nota",
        "Emitir um bipe a uma frequência durante um número de milissegundos. "
        "Os sons ficam em fila."),
    "microbit_play_melody": (
        "Tocar uma melodia",
        "Tocar uma melodia incorporada (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, "
        "POWER_UP…) ou suas próprias notas como «C4:4 E G C5:8 R:4» (nota, "
        "oitava, :duração; R é uma pausa)."),
    "microbit_stop_sound": (
        "Parar o som",
        "Desligar o alto-falante e descartar os sons em espera"),
    "microbit_radio_set_group": (
        "Definir o grupo de rádio",
        "Escolher o grupo de rádio (0 a 255). Só as micro:bit do mesmo grupo "
        "se escutam; cada placa começa no grupo 0."),
    "microbit_radio_send": (
        "Enviar uma mensagem por rádio",
        "Enviar um número ou um texto para as outras micro:bit do mesmo grupo (não a "
        "esta). Recebem o evento «Mensagem de rádio recebida», com o valor em "
        "radio_number e radio_string. Coloque o texto entre aspas; é cortado "
        "em 32 caracteres."),
    "microbit_read_sensor": (
        "Ler um sensor",
        "Ler um sensor da micro:bit para uma variável deste objeto (ou para uma "
        "variável global se o nome começar por «global.»)"),
    "microbit_if_button": (
        "Se o botão estiver pressionado",
        "Verdadeiro enquanto o botão se mantiver pressionado (A+B = os dois)"),
    "microbit_if_gesture": (
        "Se houver um gesto",
        "Verdadeiro enquanto a placa estiver neste gesto ou posição"),
    "microbit_if_tilt": (
        "Se houver inclinação",
        "Comparar um eixo do acelerômetro (mili-g, de -2048 a 2048) com um valor"),
    "microbit_if_pixel": (
        "Se o brilho do LED",
        "Comparar o brilho de um LED (0 a 9) com um valor; por padrão, "
        "a pergunta é «está aceso?»"),
}

PARAMS = {
    "Image": "Imagem",
    "Hold (ms)": "Duração (ms)",
    "Text": "Texto",
    "Delay per column (ms)": "Atraso por coluna (ms)",
    "Number": "Número",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "Brilho (0-9)",
    "Brightness (0-255)": "Brilho (0-255)",
    "Frequency (Hz)": "Frequência (Hz)",
    "Duration (ms)": "Duração (ms)",
    "Melody": "Melodia",
    "Tempo (bpm)": "Tempo (bpm)",
    "Group (0-255)": "Grupo (0-255)",
    "Message": "Mensagem",
    "Sensor": "Sensor",
    "Variable": "Variável",
    "Button": "Botão",
    "Gesture": "Gesto",
    "Axis": "Eixo",
    "Comparison": "Comparação",
    "Value": "Valor",
}

EVENTS = {
    "microbit_button_a": "Botão A pressionado",
    "microbit_button_b": "Botão B pressionado",
    "microbit_button_ab": "Botões A+B pressionados",
    "microbit_logo_touched": "Logotipo tocado",
    "microbit_pin_0": "Pino 0 tocado",
    "microbit_pin_1": "Pino 1 tocado",
    "microbit_pin_2": "Pino 2 tocado",
    "microbit_gesture_shake": "Sacudida",
    "microbit_gesture_logo_up": "Logotipo para cima",
    "microbit_gesture_logo_down": "Logotipo para baixo",
    "microbit_gesture_tilt_left": "Inclinada para a esquerda",
    "microbit_gesture_tilt_right": "Inclinada para a direita",
    "microbit_gesture_screen_up": "Tela para cima",
    "microbit_gesture_screen_down": "Tela para baixo",
    "microbit_gesture_free_fall": "Queda livre",
    "microbit_gesture_2g": "Impacto de 2g",
    "microbit_gesture_3g": "Impacto de 3g",
    "microbit_gesture_6g": "Impacto de 6g",
    "microbit_gesture_8g": "Impacto de 8g",
    "microbit_loud_sound": "Som alto",
    "microbit_quiet_sound": "Som baixo",
    "microbit_display_done": "Exibição concluída",
    "microbit_radio_received": "Mensagem de rádio recebida",
    "microbit_sound_done": "Som concluído",
}
