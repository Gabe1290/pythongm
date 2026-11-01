#!/usr/bin/env python3
"""Japanese text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``. Identifiers a student types stay as they are.
"""

ACTIONS = {
    "microbit_show_image": (
        "画像を表示",
        "LEDに画像を表示します。名前（HEART, HAPPY, SAD, YES, NO, ARROW_N, "
        "SKULL…）か、明るさの数字5行（例：「09090:99999:99999:09990:00900」）を指定します。"
        "表示は順番待ちになります。"),
    "microbit_scroll_text": (
        "文字をスクロール",
        "LEDディスプレイに文字をスクロール表示します。文字は引用符で囲んでください"
        "（\"こんにちは\"）。囲まないと、ハイフンやプラスが計算として読まれます。"
        "アクセント付きの文字や日本語は、実機と同じく ? と表示されます。"),
    "microbit_show_number": (
        "数を表示",
        "数を表示します。1桁はそのまま表示され、それより長い数はスクロールします"),
    "microbit_set_pixel": (
        "LEDを点灯",
        "LEDをすぐに点灯します（xとyは0〜4、明るさは0〜9）"),
    "microbit_clear_display": (
        "ディスプレイを消去",
        "すべてのLEDを消し、順番待ちの表示を取り消します"),
    "microbit_set_brightness": (
        "ディスプレイの明るさ",
        "LED全体の明るさ。0（消灯）から255（最大）まで"),
    "microbit_play_tone": (
        "音を鳴らす",
        "指定した周波数のビープ音を、指定したミリ秒だけ鳴らします。"
        "音は順番待ちになります。"),
    "microbit_play_melody": (
        "メロディを演奏",
        "内蔵のメロディ（DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…）か、"
        "自分の音符（例：「C4:4 E G C5:8 R:4」。音名、オクターブ、:長さ。R は休符）を演奏します。"),
    "microbit_stop_sound": (
        "音を止める",
        "スピーカーを止め、順番待ちの音を取り消します"),
    "microbit_radio_set_group": (
        "無線グループを設定",
        "無線グループ（0〜255）を選びます。同じグループのmicro:bitだけが互いに聞こえます。"
        "どのボードもグループ0から始まります。"),
    "microbit_radio_send": (
        "無線メッセージを送信",
        "同じグループのほかのmicro:bit（このボードは除く）に、数か文字を送ります。"
        "受け取った側では「無線メッセージを受信」イベントが起き、値は radio_number と "
        "radio_string に入ります。文字は引用符で囲んでください。32文字で切り詰められます。"),
    "microbit_read_sensor": (
        "センサーを読む",
        "micro:bitのセンサーの値を、このオブジェクトの変数に読み込みます"
        "（名前が「global.」で始まるときはグローバル変数）"),
    "microbit_if_button": (
        "もしボタンが押されていたら",
        "ボタンが押され続けている間は真です（A+B は両方）"),
    "microbit_if_gesture": (
        "もしジェスチャーなら",
        "ボードがこのジェスチャーまたは向きの間は真です"),
    "microbit_if_tilt": (
        "もし傾きが",
        "加速度センサーの軸の値（ミリg、-2048〜2048）を、ある値と比べます"),
    "microbit_if_pixel": (
        "もしLEDの明るさが",
        "LEDの明るさ（0〜9）を、ある値と比べます。初期設定では「点いていますか？」という問いです"),
}

PARAMS = {
    "Image": "画像",
    "Hold (ms)": "表示時間（ミリ秒）",
    "Text": "文字",
    "Delay per column (ms)": "1列ごとの待ち時間（ミリ秒）",
    "Number": "数",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "明るさ (0-9)",
    "Brightness (0-255)": "明るさ (0-255)",
    "Frequency (Hz)": "周波数（Hz）",
    "Duration (ms)": "長さ（ミリ秒）",
    "Melody": "メロディ",
    "Tempo (bpm)": "テンポ（bpm）",
    "Group (0-255)": "グループ (0-255)",
    "Message": "メッセージ",
    "Sensor": "センサー",
    "Variable": "変数",
    "Button": "ボタン",
    "Gesture": "ジェスチャー",
    "Axis": "軸",
    "Comparison": "比較",
    "Value": "値",
}

EVENTS = {
    "microbit_button_a": "ボタンAが押された",
    "microbit_button_b": "ボタンBが押された",
    "microbit_button_ab": "ボタンA+Bが押された",
    "microbit_logo_touched": "ロゴにさわった",
    "microbit_pin_0": "ピン0にさわった",
    "microbit_pin_1": "ピン1にさわった",
    "microbit_pin_2": "ピン2にさわった",
    "microbit_gesture_shake": "振った",
    "microbit_gesture_logo_up": "ロゴが上",
    "microbit_gesture_logo_down": "ロゴが下",
    "microbit_gesture_tilt_left": "左に傾けた",
    "microbit_gesture_tilt_right": "右に傾けた",
    "microbit_gesture_screen_up": "画面が上",
    "microbit_gesture_screen_down": "画面が下",
    "microbit_gesture_free_fall": "自由落下",
    "microbit_gesture_2g": "2gの衝撃",
    "microbit_gesture_3g": "3gの衝撃",
    "microbit_gesture_6g": "6gの衝撃",
    "microbit_gesture_8g": "8gの衝撃",
    "microbit_loud_sound": "大きな音",
    "microbit_quiet_sound": "小さな音",
    "microbit_display_done": "表示が終わった",
    "microbit_radio_received": "無線メッセージを受信",
    "microbit_sound_done": "音が終わった",
}
