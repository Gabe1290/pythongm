#!/usr/bin/env python3
"""Chinese (Simplified) text for the micro:bit's auto-generated Blockly blocks (follow-up M3).

Same shape as ``translations_de.py``. Identifiers a student types stay as they are.
"""

ACTIONS = {
    "microbit_show_image": (
        "显示图像",
        "在LED上显示图像：可以是名称（HEART, HAPPY, SAD, YES, NO, ARROW_N, "
        "SKULL…），也可以是五行亮度数字，例如“09090:99999:99999:09990:00900”。"
        "显示内容会排队等待。"),
    "microbit_scroll_text": (
        "滚动文字",
        "在LED显示屏上滚动显示文字。请把文字放在引号里（\"你好\"）；"
        "否则连字符或加号会被当作计算。带重音的字母和汉字会像真实开发板一样显示为 ?。"),
    "microbit_show_number": (
        "显示数字",
        "显示一个数字：一位数保持不动，更长的数字会滚动"),
    "microbit_set_pixel": (
        "点亮LED",
        "立即点亮一个LED（x和y为0到4，亮度为0到9）"),
    "microbit_clear_display": (
        "清空显示屏",
        "熄灭所有LED，并丢弃正在排队的显示内容"),
    "microbit_set_brightness": (
        "显示屏亮度",
        "LED的整体亮度，从0（熄灭）到255（最亮）"),
    "microbit_play_tone": (
        "播放音符",
        "以指定频率发出蜂鸣声，持续指定的毫秒数。声音会排队等待。"),
    "microbit_play_melody": (
        "播放旋律",
        "播放内置旋律（DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…），"
        "或你自己的音符，例如“C4:4 E G C5:8 R:4”（音名、八度、:时长；R 表示休止）。"),
    "microbit_stop_sound": (
        "停止声音",
        "关闭扬声器，并丢弃正在排队的声音"),
    "microbit_radio_set_group": (
        "设置无线电组",
        "选择无线电组（0到255）。只有同一组的micro:bit才能互相听到；"
        "每块开发板都从第0组开始。"),
    "microbit_radio_send": (
        "发送无线电消息",
        "向同一组的其他micro:bit（不包括这一块）发送数字或文字。"
        "它们会收到“收到无线电消息”事件，值保存在 radio_number 和 radio_string 中。"
        "请把文字放在引号里；超过32个字符会被截断。"),
    "microbit_read_sensor": (
        "读取传感器",
        "把micro:bit传感器的读数存入此对象的变量（名称以“global.”开头时存入全局变量）"),
    "microbit_if_button": (
        "如果按钮被按下",
        "按钮被按住期间为真（A+B 表示两个都按住）"),
    "microbit_if_gesture": (
        "如果出现手势",
        "开发板处于该手势或姿态期间为真"),
    "microbit_if_tilt": (
        "如果倾斜",
        "把加速度计某个轴的值（毫g，-2048到2048）与一个数值比较"),
    "microbit_if_pixel": (
        "如果LED亮度",
        "把某个LED的亮度（0到9）与一个数值比较；默认的问题是“它亮着吗？”"),
}

PARAMS = {
    "Image": "图像",
    "Hold (ms)": "显示时长（毫秒）",
    "Text": "文字",
    "Delay per column (ms)": "每列延迟（毫秒）",
    "Number": "数字",
    "X (0-4)": "X (0-4)",
    "Y (0-4)": "Y (0-4)",
    "Brightness (0-9)": "亮度 (0-9)",
    "Brightness (0-255)": "亮度 (0-255)",
    "Frequency (Hz)": "频率（Hz）",
    "Duration (ms)": "时长（毫秒）",
    "Melody": "旋律",
    "Tempo (bpm)": "速度（bpm）",
    "Group (0-255)": "组 (0-255)",
    "Message": "消息",
    "Sensor": "传感器",
    "Variable": "变量",
    "Button": "按钮",
    "Gesture": "手势",
    "Axis": "轴",
    "Comparison": "比较",
    "Value": "值",
}

EVENTS = {
    "microbit_button_a": "按钮A被按下",
    "microbit_button_b": "按钮B被按下",
    "microbit_button_ab": "按钮A+B被按下",
    "microbit_logo_touched": "触摸了标志",
    "microbit_pin_0": "触摸了引脚0",
    "microbit_pin_1": "触摸了引脚1",
    "microbit_pin_2": "触摸了引脚2",
    "microbit_gesture_shake": "摇晃",
    "microbit_gesture_logo_up": "标志朝上",
    "microbit_gesture_logo_down": "标志朝下",
    "microbit_gesture_tilt_left": "向左倾斜",
    "microbit_gesture_tilt_right": "向右倾斜",
    "microbit_gesture_screen_up": "屏幕朝上",
    "microbit_gesture_screen_down": "屏幕朝下",
    "microbit_gesture_free_fall": "自由落体",
    "microbit_gesture_2g": "2g冲击",
    "microbit_gesture_3g": "3g冲击",
    "microbit_gesture_6g": "6g冲击",
    "microbit_gesture_8g": "8g冲击",
    "microbit_loud_sound": "大声",
    "microbit_quiet_sound": "小声",
    "microbit_display_done": "显示结束",
    "microbit_radio_received": "收到无线电消息",
    "microbit_sound_done": "声音结束",
}
