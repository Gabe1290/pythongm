"""Thymio entries of the Configure dialog in every shipped language
(docs/THYMIO_BLOCKS_I18N_2026-11-22.md U1).

The extension's toolbox entries (blockly_categories.PLUGIN_BLOCK_CATEGORIES) are shown by
ThymioConfigDialog, which names them through config.blockly_translations; the plugin loader merges
PLUGIN_BLOCK_TRANSLATIONS into that table. The names in the Thymio events panel and action list are
NOT these (they stay English; the French activity sheets rely on them).
"""

LANGS = ("fr", "de", "es", "it", "pl", "pt", "ru", "sl", "uk", "ja", "zh")

# block type -> (names in LANGS order, descriptions in LANGS order)
_T = {
    # ---- events
    "thymio_button_forward": (
        ("Bouton avant", "Vorwärts-Taste", "Botón adelante", "Pulsante avanti", "Przycisk do przodu", "Botão para frente",
         "Кнопка вперёд", "Gumb naprej", "Кнопка вперед", "前ボタン", "前进按钮"),
        ("Bouton avant appuyé", "Vorwärts-Taste gedrückt", "Botón adelante pulsado", "Pulsante avanti premuto",
         "Naciśnięto przycisk do przodu", "Botão para frente pressionado", "Нажата кнопка вперёд", "Pritisnjen gumb naprej",
         "Натиснуто кнопку вперед", "前ボタンが押された", "按下前进按钮")),
    "thymio_button_backward": (
        ("Bouton arrière", "Rückwärts-Taste", "Botón atrás", "Pulsante indietro", "Przycisk do tyłu", "Botão para trás",
         "Кнопка назад", "Gumb nazaj", "Кнопка назад", "後ボタン", "后退按钮"),
        ("Bouton arrière appuyé", "Rückwärts-Taste gedrückt", "Botón atrás pulsado", "Pulsante indietro premuto",
         "Naciśnięto przycisk do tyłu", "Botão para trás pressionado", "Нажата кнопка назад", "Pritisnjen gumb nazaj",
         "Натиснуто кнопку назад", "後ボタンが押された", "按下后退按钮")),
    "thymio_button_left": (
        ("Bouton gauche", "Linke Taste", "Botón izquierdo", "Pulsante sinistro", "Lewy przycisk", "Botão esquerdo",
         "Левая кнопка", "Levi gumb", "Ліва кнопка", "左ボタン", "左按钮"),
        ("Bouton gauche appuyé", "Linke Taste gedrückt", "Botón izquierdo pulsado", "Pulsante sinistro premuto",
         "Naciśnięto lewy przycisk", "Botão esquerdo pressionado", "Нажата левая кнопка", "Pritisnjen levi gumb",
         "Натиснуто ліву кнопку", "左ボタンが押された", "按下左按钮")),
    "thymio_button_right": (
        ("Bouton droit", "Rechte Taste", "Botón derecho", "Pulsante destro", "Prawy przycisk", "Botão direito",
         "Правая кнопка", "Desni gumb", "Права кнопка", "右ボタン", "右按钮"),
        ("Bouton droit appuyé", "Rechte Taste gedrückt", "Botón derecho pulsado", "Pulsante destro premuto",
         "Naciśnięto prawy przycisk", "Botão direito pressionado", "Нажата правая кнопка", "Pritisnjen desni gumb",
         "Натиснуто праву кнопку", "右ボタンが押された", "按下右按钮")),
    "thymio_button_center": (
        ("Bouton central", "Mittlere Taste", "Botón central", "Pulsante centrale", "Środkowy przycisk", "Botão central",
         "Центральная кнопка", "Srednji gumb", "Центральна кнопка", "中央ボタン", "中间按钮"),
        ("Bouton central appuyé", "Mittlere Taste gedrückt", "Botón central pulsado", "Pulsante centrale premuto",
         "Naciśnięto środkowy przycisk", "Botão central pressionado", "Нажата центральная кнопка", "Pritisnjen srednji gumb",
         "Натиснуто центральну кнопку", "中央ボタンが押された", "按下中间按钮")),
    "thymio_any_button": (
        ("N'importe quel bouton", "Beliebige Taste", "Cualquier botón", "Qualsiasi pulsante", "Dowolny przycisk",
         "Qualquer botão", "Любая кнопка", "Kateri koli gumb", "Будь-яка кнопка", "いずれかのボタン", "任意按钮"),
        ("L'état d'un bouton a changé", "Der Zustand einer Taste hat sich geändert", "Cambió el estado de un botón",
         "Lo stato di un pulsante è cambiato", "Zmienił się stan przycisku", "O estado de um botão mudou",
         "Изменилось состояние кнопки", "Stanje gumba se je spremenilo", "Змінився стан кнопки",
         "ボタンの状態が変わった", "按钮状态发生变化")),
    "thymio_proximity_update": (
        ("Mise à jour de proximité", "Näherungs-Aktualisierung", "Actualización de proximidad", "Aggiornamento prossimità",
         "Aktualizacja zbliżenia", "Atualização de proximidade", "Обновление датчиков близости",
         "Posodobitev bližine", "Оновлення датчиків близькості", "近接センサー更新", "接近传感器更新"),
        ("Capteurs de proximité mis à jour (10 Hz)", "Näherungssensoren aktualisiert (10 Hz)",
         "Sensores de proximidad actualizados (10 Hz)", "Sensori di prossimità aggiornati (10 Hz)",
         "Czujniki zbliżenia zaktualizowane (10 Hz)", "Sensores de proximidade atualizados (10 Hz)",
         "Датчики близости обновлены (10 Гц)", "Senzorji bližine posodobljeni (10 Hz)",
         "Датчики близькості оновлено (10 Гц)", "近接センサーを更新（10 Hz）", "接近传感器已更新（10 Hz）")),
    "thymio_ground_update": (
        ("Mise à jour du sol", "Boden-Aktualisierung", "Actualización del suelo", "Aggiornamento suolo",
         "Aktualizacja podłoża", "Atualização do chão", "Обновление датчиков пола", "Posodobitev tal",
         "Оновлення датчиків підлоги", "床センサー更新", "地面传感器更新"),
        ("Capteurs de sol mis à jour (10 Hz)", "Bodensensoren aktualisiert (10 Hz)", "Sensores de suelo actualizados (10 Hz)",
         "Sensori del suolo aggiornati (10 Hz)", "Czujniki podłoża zaktualizowane (10 Hz)", "Sensores de chão atualizados (10 Hz)",
         "Датчики пола обновлены (10 Гц)", "Senzorji tal posodobljeni (10 Hz)", "Датчики підлоги оновлено (10 Гц)",
         "床センサーを更新（10 Hz）", "地面传感器已更新（10 Hz）")),
    "thymio_timer_0": (
        ("Minuterie 0", "Timer 0", "Temporizador 0", "Timer 0", "Licznik czasu 0", "Temporizador 0", "Таймер 0",
         "Časovnik 0", "Таймер 0", "タイマー 0", "计时器 0"),
        ("La minuterie 0 s'est déclenchée", "Timer 0 ausgelöst", "Se activó el temporizador 0", "Timer 0 scattato",
         "Licznik czasu 0 zadziałał", "Temporizador 0 disparado", "Сработал таймер 0", "Časovnik 0 se je sprožil",
         "Спрацював таймер 0", "タイマー 0 が作動した", "计时器 0 触发")),
    "thymio_timer_1": (
        ("Minuterie 1", "Timer 1", "Temporizador 1", "Timer 1", "Licznik czasu 1", "Temporizador 1", "Таймер 1",
         "Časovnik 1", "Таймер 1", "タイマー 1", "计时器 1"),
        ("La minuterie 1 s'est déclenchée", "Timer 1 ausgelöst", "Se activó el temporizador 1", "Timer 1 scattato",
         "Licznik czasu 1 zadziałał", "Temporizador 1 disparado", "Сработал таймер 1", "Časovnik 1 se je sprožil",
         "Спрацював таймер 1", "タイマー 1 が作動した", "计时器 1 触发")),
    "thymio_tap": (
        ("Tapotement détecté", "Antippen erkannt", "Toque detectado", "Tocco rilevato", "Wykryto stuknięcie",
         "Toque detectado", "Обнаружено касание", "Zaznan dotik", "Виявлено дотик", "タップを検知", "检测到敲击"),
        ("Le robot a été tapoté ou secoué", "Roboter angetippt oder geschüttelt", "Se tocó o sacudió el robot",
         "Il robot è stato toccato o scosso", "Robot został stuknięty lub potrząśnięty", "O robô foi tocado ou sacudido",
         "Робота коснулись или встряхнули", "Robota so potrkali ali stresli", "Робота торкнулися або струснули",
         "ロボットがたたかれたか振られた", "机器人被敲击或晃动")),
    "thymio_sound_detected": (
        ("Son détecté", "Geräusch erkannt", "Sonido detectado", "Suono rilevato", "Wykryto dźwięk", "Som detectado",
         "Обнаружен звук", "Zaznan zvok", "Виявлено звук", "音を検知", "检测到声音"),
        ("Seuil du microphone dépassé", "Mikrofon-Schwelle überschritten", "Se superó el umbral del micrófono",
         "Soglia del microfono superata", "Przekroczono próg mikrofonu", "Limite do microfone ultrapassado",
         "Превышен порог микрофона", "Presežen prag mikrofona", "Перевищено поріг мікрофона",
         "マイクのしきい値を超えた", "超过麦克风阈值")),
    "thymio_sound_finished": (
        ("Son terminé", "Ton beendet", "Sonido terminado", "Suono terminato", "Dźwięk zakończony", "Som terminado",
         "Звук закончился", "Zvok končan", "Звук закінчився", "サウンド終了", "声音结束"),
        ("La lecture du son est terminée", "Wiedergabe des Tons beendet", "Terminó la reproducción del sonido",
         "Riproduzione del suono terminata", "Odtwarzanie dźwięku zakończone", "A reprodução do som terminou",
         "Воспроизведение звука завершено", "Predvajanje zvoka je končano", "Відтворення звуку завершено",
         "サウンドの再生が終わった", "声音播放完毕")),
    "thymio_message_received": (
        ("Message reçu", "Nachricht empfangen", "Mensaje recibido", "Messaggio ricevuto", "Odebrano wiadomość",
         "Mensagem recebida", "Получено сообщение", "Prejeto sporočilo", "Отримано повідомлення", "メッセージ受信",
         "收到消息"),
        ("Message infrarouge reçu", "Infrarot-Nachricht empfangen", "Mensaje infrarrojo recibido", "Messaggio infrarosso ricevuto",
         "Odebrano wiadomość w podczerwieni", "Mensagem infravermelha recebida", "Получено ИК-сообщение",
         "Prejeto infrardeče sporočilo", "Отримано ІЧ-повідомлення", "赤外線メッセージを受信", "收到红外消息")),
    # ---- motors
    "thymio_set_motor_speed": (
        ("Vitesse des moteurs", "Motorgeschwindigkeiten setzen", "Velocidad de los motores", "Velocità dei motori",
         "Ustaw prędkość silników", "Definir velocidade dos motores", "Задать скорость моторов", "Nastavi hitrost motorjev",
         "Задати швидкість моторів", "モーターの速さを設定", "设置电机速度"),
        ("Régler la vitesse des moteurs gauche et droit", "Geschwindigkeit des linken und rechten Motors setzen",
         "Fijar la velocidad de los motores izquierdo y derecho", "Imposta la velocità dei motori sinistro e destro",
         "Ustaw prędkość lewego i prawego silnika", "Define a velocidade dos motores esquerdo e direito",
         "Задать скорость левого и правого моторов", "Nastavi hitrost levega in desnega motorja",
         "Задати швидкість лівого й правого моторів", "左右のモーターの速さを設定", "设置左右电机的速度")),
    "thymio_move_forward": (
        ("Avancer", "Vorwärts fahren", "Avanzar", "Vai avanti", "Jedź do przodu", "Mover para frente", "Ехать вперёд",
         "Pelji naprej", "Їхати вперед", "前進", "前进"),
        ("Avancer à la vitesse donnée", "Mit der angegebenen Geschwindigkeit vorwärts fahren", "Avanzar a la velocidad indicada",
         "Avanza alla velocità indicata", "Jedź do przodu z podaną prędkością", "Move para frente na velocidade indicada",
         "Ехать вперёд с заданной скоростью", "Pelji naprej z dano hitrostjo", "Їхати вперед із заданою швидкістю",
         "指定した速さで前進", "以指定速度前进")),
    "thymio_move_backward": (
        ("Reculer", "Rückwärts fahren", "Retroceder", "Vai indietro", "Jedź do tyłu", "Mover para trás", "Ехать назад",
         "Pelji nazaj", "Їхати назад", "後退", "后退"),
        ("Reculer à la vitesse donnée", "Mit der angegebenen Geschwindigkeit rückwärts fahren", "Retroceder a la velocidad indicada",
         "Va indietro alla velocità indicata", "Jedź do tyłu z podaną prędkością", "Move para trás na velocidade indicada",
         "Ехать назад с заданной скоростью", "Pelji nazaj z dano hitrostjo", "Їхати назад із заданою швидкістю",
         "指定した速さで後退", "以指定速度后退")),
    "thymio_turn_left": (
        ("Tourner à gauche", "Links drehen", "Girar a la izquierda", "Gira a sinistra", "Skręć w lewo", "Virar à esquerda",
         "Повернуть налево", "Zavij levo", "Повернути ліворуч", "左に回る", "左转"),
        ("Tourner à gauche à la vitesse donnée", "Mit der angegebenen Geschwindigkeit nach links drehen",
         "Girar a la izquierda a la velocidad indicada", "Gira a sinistra alla velocità indicata",
         "Skręć w lewo z podaną prędkością", "Vira à esquerda na velocidade indicada", "Повернуть налево с заданной скоростью",
         "Zavij levo z dano hitrostjo", "Повернути ліворуч із заданою швидкістю", "指定した速さで左に回る", "以指定速度左转")),
    "thymio_turn_right": (
        ("Tourner à droite", "Rechts drehen", "Girar a la derecha", "Gira a destra", "Skręć w prawo", "Virar à direita",
         "Повернуть направо", "Zavij desno", "Повернути праворуч", "右に回る", "右转"),
        ("Tourner à droite à la vitesse donnée", "Mit der angegebenen Geschwindigkeit nach rechts drehen",
         "Girar a la derecha a la velocidad indicada", "Gira a destra alla velocità indicata",
         "Skręć w prawo z podaną prędkością", "Vira à direita na velocidade indicada", "Повернуть направо с заданной скоростью",
         "Zavij desno z dano hitrostjo", "Повернути праворуч із заданою швидкістю", "指定した速さで右に回る", "以指定速度右转")),
    "thymio_stop_motors": (
        ("Arrêter les moteurs", "Motoren anhalten", "Detener los motores", "Ferma i motori", "Zatrzymaj silniki",
         "Parar os motores", "Остановить моторы", "Ustavi motorja", "Зупинити мотори", "モーターを止める", "停止电机"),
        ("Arrêter les deux moteurs", "Beide Motoren anhalten", "Detener los dos motores", "Ferma entrambi i motori",
         "Zatrzymaj oba silniki", "Para os dois motores", "Остановить оба мотора", "Ustavi oba motorja", "Зупинити обидва мотори",
         "両方のモーターを止める", "停止两个电机")),
    # ---- LEDs
    "thymio_set_led_top": (
        ("LED du dessus", "Obere LED setzen", "LED superior", "LED superiore", "Ustaw górną diodę LED", "LED de cima",
         "Задать верхний светодиод", "Nastavi zgornjo LED", "Задати верхній світлодіод", "上の LED を設定", "设置顶部 LED"),
        ("Régler la couleur de la LED RVB du dessus", "Farbe der oberen RGB-LED setzen", "Fijar el color del LED RGB superior",
         "Imposta il colore del LED RGB superiore", "Ustaw kolor górnej diody RGB", "Define a cor do LED RGB de cima",
         "Задать цвет верхнего RGB-светодиода", "Nastavi barvo zgornje RGB LED", "Задати колір верхнього RGB-світлодіода",
         "上の RGB LED の色を設定", "设置顶部 RGB LED 的颜色")),
    "thymio_set_led_bottom_left": (
        ("LED en bas à gauche", "LED unten links setzen", "LED inferior izquierdo", "LED in basso a sinistra",
         "Ustaw lewą dolną diodę LED", "LED de baixo à esquerda", "Задать нижний левый светодиод", "Nastavi spodnjo levo LED",
         "Задати нижній лівий світлодіод", "左下の LED を設定", "设置左下 LED"),
        ("Régler la LED RVB en bas à gauche", "Untere linke RGB-LED setzen", "Fijar el LED RGB inferior izquierdo",
         "Imposta il LED RGB in basso a sinistra", "Ustaw lewą dolną diodę RGB", "Define o LED RGB de baixo à esquerda",
         "Задать нижний левый RGB-светодиод", "Nastavi spodnjo levo RGB LED", "Задати нижній лівий RGB-світлодіод",
         "左下の RGB LED を設定", "设置左下 RGB LED")),
    "thymio_set_led_bottom_right": (
        ("LED en bas à droite", "LED unten rechts setzen", "LED inferior derecho", "LED in basso a destra",
         "Ustaw prawą dolną diodę LED", "LED de baixo à direita", "Задать нижний правый светодиод", "Nastavi spodnjo desno LED",
         "Задати нижній правий світлодіод", "右下の LED を設定", "设置右下 LED"),
        ("Régler la LED RVB en bas à droite", "Untere rechte RGB-LED setzen", "Fijar el LED RGB inferior derecho",
         "Imposta il LED RGB in basso a destra", "Ustaw prawą dolną diodę RGB", "Define o LED RGB de baixo à direita",
         "Задать нижний правый RGB-светодиод", "Nastavi spodnjo desno RGB LED", "Задати нижній правий RGB-світлодіод",
         "右下の RGB LED を設定", "设置右下 RGB LED")),
    "thymio_set_led_circle": (
        ("LED du cercle", "Kreis-LED setzen", "LED del círculo", "LED del cerchio", "Ustaw diodę LED okręgu",
         "LED do círculo", "Задать светодиод круга", "Nastavi LED kroga", "Задати світлодіод кола", "円の LED を設定",
         "设置圆环 LED"),
        ("Régler une LED du cercle", "Eine LED des Kreises setzen", "Fijar un LED del círculo", "Imposta un LED del cerchio",
         "Ustaw jedną diodę LED okręgu", "Define um LED do círculo", "Задать один светодиод круга", "Nastavi eno LED kroga",
         "Задати один світлодіод кола", "円の LED を 1 つ設定", "设置圆环上的一个 LED")),
    "thymio_set_led_circle_all": (
        ("Toutes les LED du cercle", "Alle Kreis-LEDs setzen", "Todos los LED del círculo", "Tutti i LED del cerchio",
         "Ustaw wszystkie diody LED okręgu", "Todos os LEDs do círculo", "Задать все светодиоды круга",
         "Nastavi vse LED kroga", "Задати всі світлодіоди кола", "円の LED をすべて設定", "设置圆环所有 LED"),
        ("Régler les 8 LED du cercle", "Alle 8 Kreis-LEDs setzen", "Fijar los 8 LED del círculo", "Imposta gli 8 LED del cerchio",
         "Ustaw 8 diod LED okręgu", "Define os 8 LEDs do círculo", "Задать 8 светодиодов круга", "Nastavi 8 LED kroga",
         "Задати 8 світлодіодів кола", "円の 8 個の LED を設定", "设置圆环的 8 个 LED")),
    "thymio_leds_off": (
        ("Éteindre les LED", "LEDs ausschalten", "Apagar los LED", "Spegni i LED", "Wyłącz diody LED", "Apagar os LEDs",
         "Выключить светодиоды", "Ugasni LED", "Вимкнути світлодіоди", "LED を消す", "关闭 LED"),
        ("Éteindre toutes les LED", "Alle LEDs ausschalten", "Apagar todos los LED", "Spegni tutti i LED",
         "Wyłącz wszystkie diody LED", "Apaga todos os LEDs", "Выключить все светодиоды", "Ugasni vse LED",
         "Вимкнути всі світлодіоди", "すべての LED を消す", "关闭所有 LED")),
    # ---- sound
    "thymio_play_tone": (
        ("Jouer une note", "Ton abspielen", "Tocar un tono", "Suona un tono", "Zagraj ton", "Tocar um tom",
         "Сыграть тон", "Predvajaj ton", "Відтворити тон", "音を鳴らす", "播放音调"),
        ("Jouer un son à une fréquence donnée", "Einen Ton mit gegebener Frequenz abspielen",
         "Tocar un tono de frecuencia dada", "Suona un tono alla frequenza indicata", "Zagraj ton o podanej częstotliwości",
         "Toca um tom na frequência indicada", "Сыграть тон заданной частоты", "Predvajaj ton z dano frekvenco",
         "Відтворити тон заданої частоти", "指定した周波数の音を鳴らす", "播放指定频率的音调")),
    "thymio_play_system_sound": (
        ("Jouer un son système", "Systemton abspielen", "Tocar sonido del sistema", "Suona un suono di sistema",
         "Odtwórz dźwięk systemowy", "Tocar som do sistema", "Воспроизвести системный звук", "Predvajaj sistemski zvok",
         "Відтворити системний звук", "システム音を鳴らす", "播放系统声音"),
        ("Jouer un son intégré", "Einen eingebauten Ton abspielen", "Tocar un sonido integrado", "Suona un suono integrato",
         "Odtwórz wbudowany dźwięk", "Toca um som embutido", "Воспроизвести встроенный звук", "Predvajaj vgrajeni zvok",
         "Відтворити вбудований звук", "内蔵の音を鳴らす", "播放内置声音")),
    "thymio_stop_sound": (
        ("Arrêter le son", "Ton anhalten", "Detener el sonido", "Ferma il suono", "Zatrzymaj dźwięk", "Parar o som",
         "Остановить звук", "Ustavi zvok", "Зупинити звук", "音を止める", "停止声音"),
        ("Arrêter le son en cours", "Laufenden Ton anhalten", "Detener el sonido en curso", "Ferma il suono in corso",
         "Zatrzymaj odtwarzany dźwięk", "Para o som em reprodução", "Остановить текущий звук", "Ustavi trenutni zvok",
         "Зупинити поточний звук", "再生中の音を止める", "停止正在播放的声音")),
    # ---- sensors
    "thymio_read_proximity": (
        ("Lire la proximité", "Nähe auslesen", "Leer proximidad", "Leggi prossimità", "Odczytaj zbliżenie", "Ler proximidade",
         "Прочитать близость", "Preberi bližino", "Прочитати близькість", "近接を読む", "读取接近值"),
        ("Lire la valeur d'un capteur de proximité", "Wert eines Näherungssensors auslesen", "Leer el valor de un sensor de proximidad",
         "Leggi il valore di un sensore di prossimità", "Odczytaj wartość czujnika zbliżenia", "Lê o valor de um sensor de proximidade",
         "Прочитать значение датчика близости", "Preberi vrednost senzorja bližine", "Прочитати значення датчика близькості",
         "近接センサーの値を読む", "读取接近传感器的值")),
    "thymio_read_ground": (
        ("Lire le sol", "Boden auslesen", "Leer suelo", "Leggi suolo", "Odczytaj podłoże", "Ler o chão", "Прочитать пол",
         "Preberi tla", "Прочитати підлогу", "床を読む", "读取地面值"),
        ("Lire la valeur d'un capteur de sol", "Wert eines Bodensensors auslesen", "Leer el valor de un sensor de suelo",
         "Leggi il valore di un sensore del suolo", "Odczytaj wartość czujnika podłoża", "Lê o valor de um sensor de chão",
         "Прочитать значение датчика пола", "Preberi vrednost senzorja tal", "Прочитати значення датчика підлоги",
         "床センサーの値を読む", "读取地面传感器的值")),
    "thymio_read_button": (
        ("Lire un bouton", "Taste auslesen", "Leer botón", "Leggi pulsante", "Odczytaj przycisk", "Ler botão",
         "Прочитать кнопку", "Preberi gumb", "Прочитати кнопку", "ボタンを読む", "读取按钮"),
        ("Lire l'état d'un bouton", "Zustand einer Taste auslesen", "Leer el estado de un botón", "Leggi lo stato di un pulsante",
         "Odczytaj stan przycisku", "Lê o estado de um botão", "Прочитать состояние кнопки", "Preberi stanje gumba",
         "Прочитати стан кнопки", "ボタンの状態を読む", "读取按钮状态")),
    # ---- conditions
    "thymio_if_proximity": (
        ("Si proximité", "Wenn Nähe", "Si proximidad", "Se prossimità", "Jeśli zbliżenie", "Se proximidade", "Если близость",
         "Če bližina", "Якщо близькість", "もし近接", "如果接近"),
        ("Tester un capteur de proximité", "Einen Näherungssensor prüfen", "Comprobar un sensor de proximidad",
         "Controlla un sensore di prossimità", "Sprawdź czujnik zbliżenia", "Verifica um sensor de proximidade",
         "Проверить датчик близости", "Preveri senzor bližine", "Перевірити датчик близькості", "近接センサーを調べる",
         "检查接近传感器")),
    "thymio_if_ground_dark": (
        ("Si le sol est sombre", "Wenn Boden dunkel", "Si el suelo está oscuro", "Se il suolo è scuro", "Jeśli podłoże ciemne",
         "Se o chão está escuro", "Если пол тёмный", "Če so tla temna", "Якщо підлога темна", "もし床が暗い", "如果地面是暗的"),
        ("Tester si le sol est sombre", "Prüfen, ob der Boden dunkel ist", "Comprobar si el suelo está oscuro",
         "Controlla se il suolo è scuro", "Sprawdź, czy podłoże jest ciemne", "Verifica se o chão está escuro",
         "Проверить, тёмный ли пол", "Preveri, ali so tla temna", "Перевірити, чи темна підлога", "床が暗いか調べる",
         "检查地面是否是暗的")),
    "thymio_if_ground_light": (
        ("Si le sol est clair", "Wenn Boden hell", "Si el suelo está claro", "Se il suolo è chiaro", "Jeśli podłoże jasne",
         "Se o chão está claro", "Если пол светлый", "Če so tla svetla", "Якщо підлога світла", "もし床が明るい",
         "如果地面是亮的"),
        ("Tester si le sol est clair", "Prüfen, ob der Boden hell ist", "Comprobar si el suelo está claro",
         "Controlla se il suolo è chiaro", "Sprawdź, czy podłoże jest jasne", "Verifica se o chão está claro",
         "Проверить, светлый ли пол", "Preveri, ali so tla svetla", "Перевірити, чи світла підлога", "床が明るいか調べる",
         "检查地面是否是亮的")),
    "thymio_if_button_pressed": (
        ("Si bouton appuyé", "Wenn Taste gedrückt", "Si botón pulsado", "Se pulsante premuto", "Jeśli przycisk naciśnięty",
         "Se botão pressionado", "Если кнопка нажата", "Če je gumb pritisnjen", "Якщо кнопку натиснуто", "もしボタンが押されている",
         "如果按钮被按下"),
        ("Tester si un bouton est appuyé", "Prüfen, ob eine Taste gedrückt ist", "Comprobar si un botón está pulsado",
         "Controlla se un pulsante è premuto", "Sprawdź, czy przycisk jest naciśnięty", "Verifica se um botão está pressionado",
         "Проверить, нажата ли кнопка", "Preveri, ali je gumb pritisnjen", "Перевірити, чи натиснуто кнопку",
         "ボタンが押されているか調べる", "检查按钮是否被按下")),
    "thymio_if_button_released": (
        ("Si bouton relâché", "Wenn Taste losgelassen", "Si botón soltado", "Se pulsante rilasciato", "Jeśli przycisk puszczony",
         "Se botão solto", "Если кнопка отпущена", "Če je gumb spuščen", "Якщо кнопку відпущено", "もしボタンが離されている",
         "如果按钮被松开"),
        ("Tester si un bouton est relâché", "Prüfen, ob eine Taste losgelassen ist", "Comprobar si un botón está soltado",
         "Controlla se un pulsante è rilasciato", "Sprawdź, czy przycisk jest puszczony", "Verifica se um botão está solto",
         "Проверить, отпущена ли кнопка", "Preveri, ali je gumb spuščen", "Перевірити, чи відпущено кнопку",
         "ボタンが離されているか調べる", "检查按钮是否被松开")),
    "thymio_if_variable": (
        ("Si variable", "Wenn Variable", "Si variable", "Se variabile", "Jeśli zmienna", "Se variável", "Если переменная",
         "Če spremenljivka", "Якщо змінна", "もし変数", "如果变量"),
        ("Tester une condition sur une variable", "Eine Bedingung für eine Variable prüfen", "Comprobar una condición sobre una variable",
         "Controlla una condizione su una variabile", "Sprawdź warunek zmiennej", "Verifica uma condição de variável",
         "Проверить условие для переменной", "Preveri pogoj za spremenljivko", "Перевірити умову для змінної",
         "変数の条件を調べる", "检查变量条件")),
    # ---- timers
    "thymio_set_timer_period": (
        ("Période de la minuterie", "Timer-Periode setzen", "Periodo del temporizador", "Periodo del timer",
         "Ustaw okres licznika czasu", "Período do temporizador", "Задать период таймера", "Nastavi periodo časovnika",
         "Задати період таймера", "タイマーの周期を設定", "设置计时器周期"),
        ("Régler la période de la minuterie (ms)", "Timer-Periode setzen (ms)", "Fijar el periodo del temporizador (ms)",
         "Imposta il periodo del timer (ms)", "Ustaw okres licznika czasu (ms)", "Define o período do temporizador (ms)",
         "Задать период таймера (мс)", "Nastavi periodo časovnika (ms)", "Задати період таймера (мс)",
         "タイマーの周期を設定（ms）", "设置计时器周期（毫秒）")),
    # ---- variables
    "thymio_set_variable": (
        ("Définir une variable", "Variable setzen", "Establecer variable", "Imposta variabile", "Ustaw zmienną",
         "Definir variável", "Задать переменную", "Nastavi spremenljivko", "Задати змінну", "変数を設定", "设置变量"),
        ("Donner une valeur à une variable", "Einer Variablen einen Wert geben", "Dar un valor a una variable",
         "Assegna un valore a una variabile", "Nadaj wartość zmiennej", "Dá um valor a uma variável",
         "Задать значение переменной", "Spremenljivki nastavi vrednost", "Задати значення змінної", "変数に値を入れる",
         "给变量赋值")),
    "thymio_increase_variable": (
        ("Augmenter une variable", "Variable erhöhen", "Aumentar variable", "Aumenta variabile", "Zwiększ zmienną",
         "Aumentar variável", "Увеличить переменную", "Povečaj spremenljivko", "Збільшити змінну", "変数を増やす", "增加变量"),
        ("Ajouter 1 à une variable", "Eine Variable um 1 erhöhen", "Sumar 1 a una variable", "Aggiungi 1 a una variabile",
         "Dodaj 1 do zmiennej", "Soma 1 a uma variável", "Прибавить 1 к переменной", "Spremenljivki prištej 1",
         "Додати 1 до змінної", "変数に 1 を足す", "变量加 1")),
    "thymio_decrease_variable": (
        ("Diminuer une variable", "Variable verringern", "Disminuir variable", "Diminuisci variabile", "Zmniejsz zmienną",
         "Diminuir variável", "Уменьшить переменную", "Zmanjšaj spremenljivko", "Зменшити змінну", "変数を減らす", "减少变量"),
        ("Retirer 1 à une variable", "Eine Variable um 1 verringern", "Restar 1 a una variable", "Togli 1 a una variabile",
         "Odejmij 1 od zmiennej", "Subtrai 1 de uma variável", "Вычесть 1 из переменной", "Spremenljivki odštej 1",
         "Відняти 1 від змінної", "変数から 1 を引く", "变量减 1")),
}

PLUGIN_BLOCK_TRANSLATIONS = {
    block: {"name": dict(zip(LANGS, names)), "description": dict(zip(LANGS, descs))}
    for block, (names, descs) in _T.items()
}
