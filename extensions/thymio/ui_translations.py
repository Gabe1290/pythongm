"""Thymio names in the events panel, the action list and the action configure dialog, in every shipped
language (docs/THYMIO_PANEL_I18N_PLAN.md U2). Registered as PLUGIN_UI_TRANSLATIONS and read through
core.ui_names.ui_name(kind, english).

Action and event NAMES reuse the Configure dialog's wording (block_translations.py, same keys), so the
dialog, the Blockly blocks and the panel name each thing the same way. Choice labels are DISPLAY only:
a project keeps storing the English label (U0).
"""
from .actions import THYMIO_ACTIONS
from .block_translations import LANGS, PLUGIN_BLOCK_TRANSLATIONS
from .events import THYMIO_EVENT_TYPES


def _t(*texts):
    assert len(texts) == len(LANGS), texts
    return dict(zip(LANGS, texts))


ACTION_DESCRIPTIONS = {
    "Set left and right motor speeds independently (-500 to 500)": _t(
        "Régler séparément la vitesse des moteurs gauche et droit (-500 à 500)",
        "Geschwindigkeit des linken und rechten Motors einzeln setzen (-500 bis 500)",
        "Fijar por separado la velocidad de los motores izquierdo y derecho (-500 a 500)",
        "Imposta separatamente la velocità dei motori sinistro e destro (da -500 a 500)",
        "Ustaw osobno prędkość lewego i prawego silnika (od -500 do 500)",
        "Define separadamente a velocidade dos motores esquerdo e direito (-500 a 500)",
        "Задать скорость левого и правого моторов по отдельности (от -500 до 500)",
        "Ločeno nastavi hitrost levega in desnega motorja (od -500 do 500)",
        "Задати швидкість лівого й правого моторів окремо (від -500 до 500)",
        "左右のモーターの速さを別々に設定（-500〜500）", "分别设置左右电机的速度（-500 到 500）"),
    "Move forward at specified speed (both motors same speed)": _t(
        "Avancer à la vitesse donnée (les deux moteurs à la même vitesse)",
        "Mit der angegebenen Geschwindigkeit vorwärts fahren (beide Motoren gleich schnell)",
        "Avanzar a la velocidad indicada (los dos motores a la misma velocidad)",
        "Vai avanti alla velocità indicata (entrambi i motori alla stessa velocità)",
        "Jedź do przodu z podaną prędkością (oba silniki tak samo)",
        "Move para frente na velocidade indicada (os dois motores na mesma velocidade)",
        "Ехать вперёд с заданной скоростью (оба мотора одинаково)",
        "Pelji naprej z dano hitrostjo (oba motorja enako hitro)",
        "Їхати вперед із заданою швидкістю (обидва мотори однаково)",
        "指定した速さで前進（両方のモーターが同じ速さ）", "以指定速度前进（两个电机速度相同）"),
    "Move backward at specified speed": _t(
        "Reculer à la vitesse donnée", "Mit der angegebenen Geschwindigkeit rückwärts fahren",
        "Retroceder a la velocidad indicada", "Vai indietro alla velocità indicata", "Jedź do tyłu z podaną prędkością",
        "Move para trás na velocidade indicada", "Ехать назад с заданной скоростью", "Pelji nazaj z dano hitrostjo",
        "Їхати назад із заданою швидкістю", "指定した速さで後退", "以指定速度后退"),
    "Turn left in place (left motor stops, right motor moves)": _t(
        "Tourner à gauche sur place (le moteur gauche s'arrête, le droit tourne)",
        "Auf der Stelle nach links drehen (linker Motor steht, rechter läuft)",
        "Girar a la izquierda en el sitio (el motor izquierdo se para, el derecho gira)",
        "Gira a sinistra sul posto (il motore sinistro si ferma, il destro gira)",
        "Obróć się w lewo w miejscu (lewy silnik stoi, prawy pracuje)",
        "Vira à esquerda no lugar (o motor esquerdo para, o direito gira)",
        "Повернуть налево на месте (левый мотор стоит, правый работает)",
        "Zavij levo na mestu (levi motor stoji, desni se vrti)",
        "Повернути ліворуч на місці (лівий мотор стоїть, правий працює)",
        "その場で左に回る（左のモーターは止まり、右が動く）", "原地左转（左电机停止，右电机转动）"),
    "Turn right in place (right motor stops, left motor moves)": _t(
        "Tourner à droite sur place (le moteur droit s'arrête, le gauche tourne)",
        "Auf der Stelle nach rechts drehen (rechter Motor steht, linker läuft)",
        "Girar a la derecha en el sitio (el motor derecho se para, el izquierdo gira)",
        "Gira a destra sul posto (il motore destro si ferma, il sinistro gira)",
        "Obróć się w prawo w miejscu (prawy silnik stoi, lewy pracuje)",
        "Vira à direita no lugar (o motor direito para, o esquerdo gira)",
        "Повернуть направо на месте (правый мотор стоит, левый работает)",
        "Zavij desno na mestu (desni motor stoji, levi se vrti)",
        "Повернути праворуч на місці (правий мотор стоїть, лівий працює)",
        "その場で右に回る（右のモーターは止まり、左が動く）", "原地右转（右电机停止，左电机转动）"),
    "Stop both motors (set speeds to 0)": _t(
        "Arrêter les deux moteurs (vitesses à 0)", "Beide Motoren anhalten (Geschwindigkeiten auf 0)",
        "Detener los dos motores (velocidades a 0)", "Ferma entrambi i motori (velocità a 0)",
        "Zatrzymaj oba silniki (prędkości na 0)", "Para os dois motores (velocidades em 0)",
        "Остановить оба мотора (скорости 0)", "Ustavi oba motorja (hitrosti na 0)", "Зупинити обидва мотори (швидкості 0)",
        "両方のモーターを止める（速さを 0 に）", "停止两个电机（速度设为 0）"),
    "Set the top RGB LED color (0-32 for each channel)": _t(
        "Régler la couleur de la LED RVB du dessus (0-32 par canal)", "Farbe der oberen RGB-LED setzen (0-32 je Kanal)",
        "Fijar el color del LED RGB superior (0-32 por canal)", "Imposta il colore del LED RGB superiore (0-32 per canale)",
        "Ustaw kolor górnej diody RGB (0-32 na kanał)", "Define a cor do LED RGB de cima (0-32 por canal)",
        "Задать цвет верхнего RGB-светодиода (0-32 на канал)", "Nastavi barvo zgornje RGB LED (0-32 na kanal)",
        "Задати колір верхнього RGB-світлодіода (0-32 на канал)", "上の RGB LED の色を設定（各チャンネル 0〜32）",
        "设置顶部 RGB LED 的颜色（每个通道 0-32）"),
    "Set the bottom left RGB LED color": _t(
        "Régler la couleur de la LED RVB en bas à gauche", "Farbe der unteren linken RGB-LED setzen",
        "Fijar el color del LED RGB inferior izquierdo", "Imposta il colore del LED RGB in basso a sinistra",
        "Ustaw kolor lewej dolnej diody RGB", "Define a cor do LED RGB de baixo à esquerda",
        "Задать цвет нижнего левого RGB-светодиода", "Nastavi barvo spodnje leve RGB LED",
        "Задати колір нижнього лівого RGB-світлодіода", "左下の RGB LED の色を設定", "设置左下 RGB LED 的颜色"),
    "Set the bottom right RGB LED color": _t(
        "Régler la couleur de la LED RVB en bas à droite", "Farbe der unteren rechten RGB-LED setzen",
        "Fijar el color del LED RGB inferior derecho", "Imposta il colore del LED RGB in basso a destra",
        "Ustaw kolor prawej dolnej diody RGB", "Define a cor do LED RGB de baixo à direita",
        "Задать цвет нижнего правого RGB-светодиода", "Nastavi barvo spodnje desne RGB LED",
        "Задати колір нижнього правого RGB-світлодіода", "右下の RGB LED の色を設定", "设置右下 RGB LED 的颜色"),
    "Set one of the 8 circle LEDs (yellow/orange)": _t(
        "Régler une des 8 LED du cercle (jaune/orange)", "Eine der 8 Kreis-LEDs setzen (gelb/orange)",
        "Fijar uno de los 8 LED del círculo (amarillo/naranja)", "Imposta uno degli 8 LED del cerchio (giallo/arancione)",
        "Ustaw jedną z 8 diod LED okręgu (żółta/pomarańczowa)", "Define um dos 8 LEDs do círculo (amarelo/laranja)",
        "Задать один из 8 светодиодов круга (жёлтый/оранжевый)", "Nastavi eno od 8 LED kroga (rumena/oranžna)",
        "Задати один із 8 світлодіодів кола (жовтий/помаранчевий)", "円の 8 個の LED の 1 つを設定（黄/オレンジ）",
        "设置圆环 8 个 LED 中的一个（黄/橙色）"),
    "Set all 8 circle LEDs at once (comma-separated values)": _t(
        "Régler les 8 LED du cercle d'un coup (valeurs séparées par des virgules)",
        "Alle 8 Kreis-LEDs auf einmal setzen (Werte durch Kommas getrennt)",
        "Fijar los 8 LED del círculo a la vez (valores separados por comas)",
        "Imposta gli 8 LED del cerchio insieme (valori separati da virgole)",
        "Ustaw naraz 8 diod LED okręgu (wartości rozdzielone przecinkami)",
        "Define os 8 LEDs do círculo de uma vez (valores separados por vírgulas)",
        "Задать все 8 светодиодов круга сразу (значения через запятую)",
        "Nastavi vseh 8 LED kroga hkrati (vrednosti, ločene z vejicami)",
        "Задати всі 8 світлодіодів кола одразу (значення через кому)",
        "円の 8 個の LED をまとめて設定（値はカンマ区切り）", "一次设置圆环的 8 个 LED（用逗号分隔的值）"),
    "Turn off all LEDs (top, bottom, and circle)": _t(
        "Éteindre toutes les LED (dessus, dessous et cercle)", "Alle LEDs ausschalten (oben, unten und Kreis)",
        "Apagar todos los LED (superior, inferiores y círculo)", "Spegni tutti i LED (sopra, sotto e cerchio)",
        "Wyłącz wszystkie diody LED (górną, dolne i okręgu)", "Apaga todos os LEDs (cima, baixo e círculo)",
        "Выключить все светодиоды (верхний, нижние и круг)", "Ugasni vse LED (zgornjo, spodnji in krog)",
        "Вимкнути всі світлодіоди (верхній, нижні й коло)", "すべての LED を消す（上、下、円）", "关闭所有 LED（顶部、底部和圆环）"),
    "Play a tone at specified frequency and duration": _t(
        "Jouer une note à la fréquence et pour la durée données", "Einen Ton mit gegebener Frequenz und Dauer abspielen",
        "Tocar un tono de frecuencia y duración dadas", "Suona un tono con frequenza e durata indicate",
        "Zagraj ton o podanej częstotliwości i czasie", "Toca um tom com a frequência e a duração indicadas",
        "Сыграть тон заданной частоты и длительности", "Predvajaj ton z dano frekvenco in trajanjem",
        "Відтворити тон заданої частоти й тривалості", "指定した周波数と長さで音を鳴らす", "按指定频率和时长播放音调"),
    "Play one of the robot's built-in system sounds. On real hardware this plays the robot's own melody for that sound; the in-app simulator only approximates it as a single tone, so it won't sound the same as the real robot.": _t(
        "Jouer un des sons système intégrés du robot. Sur le vrai robot, c'est sa propre mélodie ; le simulateur ne l'imite que par une seule note, donc le son n'est pas le même.",
        "Einen der eingebauten Systemtöne des Roboters abspielen. Auf dem echten Roboter ist das seine eigene Melodie; der Simulator ahmt sie nur mit einem einzelnen Ton nach, sie klingt also anders.",
        "Tocar uno de los sonidos del sistema del robot. En el robot real es su propia melodía; el simulador solo la imita con un único tono, así que no suena igual.",
        "Suona uno dei suoni di sistema del robot. Sul robot vero è la sua melodia; il simulatore la imita solo con un singolo tono, quindi non suona uguale.",
        "Odtwórz jeden z wbudowanych dźwięków robota. Na prawdziwym robocie to jego własna melodia; symulator naśladuje ją tylko jednym tonem, więc brzmi inaczej.",
        "Toca um dos sons do sistema do robô. No robô real é a própria melodia dele; o simulador só a imita com um único tom, então não soa igual.",
        "Воспроизвести один из встроенных звуков робота. На настоящем роботе это его собственная мелодия; симулятор лишь изображает её одним тоном, поэтому звучит иначе.",
        "Predvajaj enega od vgrajenih zvokov robota. Na pravem robotu je to njegova melodija; simulator jo le posnema z enim tonom, zato ne zveni enako.",
        "Відтворити один із вбудованих звуків робота. На справжньому роботі це його власна мелодія; симулятор лише імітує її одним тоном, тому звучить інакше.",
        "ロボット内蔵のシステム音を鳴らす。実機ではロボット独自のメロディですが、シミュレーターは 1 つの音でまねるだけなので、同じ音にはなりません。",
        "播放机器人内置的系统声音之一。真实机器人上是它自己的旋律；模拟器只用一个音调近似，所以听起来不一样。"),
    "Stop currently playing sound": _t(
        "Arrêter le son en cours", "Laufenden Ton anhalten", "Detener el sonido en curso", "Ferma il suono in corso",
        "Zatrzymaj odtwarzany dźwięk", "Para o som em reprodução", "Остановить текущий звук", "Ustavi trenutni zvok",
        "Зупинити поточний звук", "再生中の音を止める", "停止正在播放的声音"),
    "Read a proximity sensor value and store in variable": _t(
        "Lire la valeur d'un capteur de proximité et la ranger dans une variable",
        "Wert eines Näherungssensors lesen und in einer Variablen speichern",
        "Leer el valor de un sensor de proximidad y guardarlo en una variable",
        "Leggi il valore di un sensore di prossimità e salvalo in una variabile",
        "Odczytaj wartość czujnika zbliżenia i zapisz ją w zmiennej",
        "Lê o valor de um sensor de proximidade e guarda numa variável",
        "Прочитать значение датчика близости и сохранить в переменной",
        "Preberi vrednost senzorja bližine in jo shrani v spremenljivko",
        "Прочитати значення датчика близькості й зберегти у змінній",
        "近接センサーの値を読んで変数に入れる", "读取接近传感器的值并存入变量"),
    "Read a ground sensor value and store in variable": _t(
        "Lire la valeur d'un capteur de sol et la ranger dans une variable",
        "Wert eines Bodensensors lesen und in einer Variablen speichern",
        "Leer el valor de un sensor de suelo y guardarlo en una variable",
        "Leggi il valore di un sensore del suolo e salvalo in una variabile",
        "Odczytaj wartość czujnika podłoża i zapisz ją w zmiennej",
        "Lê o valor de um sensor de chão e guarda numa variável",
        "Прочитать значение датчика пола и сохранить в переменной",
        "Preberi vrednost senzorja tal in jo shrani v spremenljivko",
        "Прочитати значення датчика підлоги й зберегти у змінній",
        "床センサーの値を読んで変数に入れる", "读取地面传感器的值并存入变量"),
    "Read button state and store in variable (0=released, 1=pressed)": _t(
        "Lire l'état d'un bouton et le ranger dans une variable (0 = relâché, 1 = appuyé)",
        "Tastenzustand lesen und in einer Variablen speichern (0 = losgelassen, 1 = gedrückt)",
        "Leer el estado de un botón y guardarlo en una variable (0 = soltado, 1 = pulsado)",
        "Leggi lo stato di un pulsante e salvalo in una variabile (0 = rilasciato, 1 = premuto)",
        "Odczytaj stan przycisku i zapisz w zmiennej (0 = puszczony, 1 = naciśnięty)",
        "Lê o estado de um botão e guarda numa variável (0 = solto, 1 = pressionado)",
        "Прочитать состояние кнопки и сохранить в переменной (0 = отпущена, 1 = нажата)",
        "Preberi stanje gumba in ga shrani v spremenljivko (0 = spuščen, 1 = pritisnjen)",
        "Прочитати стан кнопки й зберегти у змінній (0 = відпущено, 1 = натиснуто)",
        "ボタンの状態を読んで変数に入れる（0 = 離されている、1 = 押されている）",
        "读取按钮状态并存入变量（0 = 松开，1 = 按下）"),
    "Check if proximity sensor detects obstacle above threshold": _t(
        "Tester si un capteur de proximité détecte un obstacle au-dessus du seuil",
        "Prüfen, ob ein Näherungssensor ein Hindernis über der Schwelle erkennt",
        "Comprobar si un sensor de proximidad detecta un obstáculo por encima del umbral",
        "Controlla se un sensore di prossimità rileva un ostacolo sopra la soglia",
        "Sprawdź, czy czujnik zbliżenia wykrywa przeszkodę powyżej progu",
        "Verifica se um sensor de proximidade detecta um obstáculo acima do limite",
        "Проверить, видит ли датчик близости препятствие выше порога",
        "Preveri, ali senzor bližine zazna oviro nad pragom",
        "Перевірити, чи бачить датчик близькості перешкоду вище порога",
        "近接センサーがしきい値より強く障害物を検知しているか調べる", "检查接近传感器是否检测到超过阈值的障碍物"),
    "Check if ground sensor detects dark surface (line following)": _t(
        "Tester si un capteur de sol voit une surface sombre (suivi de ligne)",
        "Prüfen, ob ein Bodensensor eine dunkle Fläche erkennt (Linienfolgen)",
        "Comprobar si un sensor de suelo detecta una superficie oscura (seguir líneas)",
        "Controlla se un sensore del suolo rileva una superficie scura (seguilinea)",
        "Sprawdź, czy czujnik podłoża wykrywa ciemną powierzchnię (jazda po linii)",
        "Verifica se um sensor de chão detecta uma superfície escura (seguir linha)",
        "Проверить, видит ли датчик пола тёмную поверхность (следование по линии)",
        "Preveri, ali senzor tal zazna temno površino (sledenje črti)",
        "Перевірити, чи бачить датчик підлоги темну поверхню (рух по лінії)",
        "床センサーが暗い面を検知しているか調べる（ライントレース）", "检查地面传感器是否检测到暗色表面（巡线）"),
    "Check if ground sensor detects light surface": _t(
        "Tester si un capteur de sol voit une surface claire", "Prüfen, ob ein Bodensensor eine helle Fläche erkennt",
        "Comprobar si un sensor de suelo detecta una superficie clara", "Controlla se un sensore del suolo rileva una superficie chiara",
        "Sprawdź, czy czujnik podłoża wykrywa jasną powierzchnię", "Verifica se um sensor de chão detecta uma superfície clara",
        "Проверить, видит ли датчик пола светлую поверхность", "Preveri, ali senzor tal zazna svetlo površino",
        "Перевірити, чи бачить датчик підлоги світлу поверхню", "床センサーが明るい面を検知しているか調べる",
        "检查地面传感器是否检测到亮色表面"),
    "Check if a button is currently pressed": _t(
        "Tester si un bouton est appuyé", "Prüfen, ob eine Taste gerade gedrückt ist", "Comprobar si un botón está pulsado",
        "Controlla se un pulsante è premuto", "Sprawdź, czy przycisk jest teraz naciśnięty", "Verifica se um botão está pressionado",
        "Проверить, нажата ли сейчас кнопка", "Preveri, ali je gumb pritisnjen", "Перевірити, чи натиснуто зараз кнопку",
        "ボタンが今押されているか調べる", "检查按钮当前是否被按下"),
    "Check if a button is currently released": _t(
        "Tester si un bouton est relâché", "Prüfen, ob eine Taste gerade losgelassen ist", "Comprobar si un botón está soltado",
        "Controlla se un pulsante è rilasciato", "Sprawdź, czy przycisk jest teraz puszczony", "Verifica se um botão está solto",
        "Проверить, отпущена ли сейчас кнопка", "Preveri, ali je gumb spuščen", "Перевірити, чи відпущено зараз кнопку",
        "ボタンが今離されているか調べる", "检查按钮当前是否松开"),
    "Set timer period in milliseconds (triggers on_timer event)": _t(
        "Régler la période de la minuterie en millisecondes (déclenche l'événement de minuterie)",
        "Timer-Periode in Millisekunden setzen (löst das Timer-Ereignis aus)",
        "Fijar el periodo del temporizador en milisegundos (dispara el evento del temporizador)",
        "Imposta il periodo del timer in millisecondi (attiva l'evento del timer)",
        "Ustaw okres licznika czasu w milisekundach (wywołuje zdarzenie licznika)",
        "Define o período do temporizador em milissegundos (dispara o evento do temporizador)",
        "Задать период таймера в миллисекундах (вызывает событие таймера)",
        "Nastavi periodo časovnika v milisekundah (sproži dogodek časovnika)",
        "Задати період таймера в мілісекундах (викликає подію таймера)",
        "タイマーの周期をミリ秒で設定（タイマーイベントが起きる）", "以毫秒设置计时器周期（触发计时器事件）"),
    "Set a variable to a value (16-bit integer: -32768 to 32767)": _t(
        "Donner une valeur à une variable (entier 16 bits : -32768 à 32767)",
        "Einer Variablen einen Wert geben (16-Bit-Ganzzahl: -32768 bis 32767)",
        "Dar un valor a una variable (entero de 16 bits: -32768 a 32767)",
        "Assegna un valore a una variabile (intero a 16 bit: da -32768 a 32767)",
        "Nadaj zmiennej wartość (liczba całkowita 16-bitowa: od -32768 do 32767)",
        "Dá um valor a uma variável (inteiro de 16 bits: -32768 a 32767)",
        "Задать значение переменной (16-битное целое: от -32768 до 32767)",
        "Spremenljivki nastavi vrednost (16-bitno celo število: od -32768 do 32767)",
        "Задати значення змінної (16-бітне ціле: від -32768 до 32767)",
        "変数に値を入れる（16 ビット整数: -32768〜32767）", "给变量赋值（16 位整数：-32768 到 32767）"),
    "Increase variable by specified amount": _t(
        "Augmenter une variable de la quantité donnée", "Variable um den angegebenen Betrag erhöhen",
        "Aumentar una variable en la cantidad indicada", "Aumenta una variabile della quantità indicata",
        "Zwiększ zmienną o podaną wartość", "Aumenta uma variável na quantidade indicada",
        "Увеличить переменную на заданную величину", "Povečaj spremenljivko za dano vrednost",
        "Збільшити змінну на задану величину", "変数を指定した量だけ増やす", "将变量增加指定的量"),
    "Decrease variable by specified amount": _t(
        "Diminuer une variable de la quantité donnée", "Variable um den angegebenen Betrag verringern",
        "Disminuir una variable en la cantidad indicada", "Diminuisci una variabile della quantità indicata",
        "Zmniejsz zmienną o podaną wartość", "Diminui uma variável na quantidade indicada",
        "Уменьшить переменную на заданную величину", "Zmanjšaj spremenljivko za dano vrednost",
        "Зменшити змінну на задану величину", "変数を指定した量だけ減らす", "将变量减少指定的量"),
    "Check variable value against a condition": _t(
        "Tester la valeur d'une variable avec une condition", "Wert einer Variablen mit einer Bedingung prüfen",
        "Comprobar el valor de una variable con una condición", "Controlla il valore di una variabile con una condizione",
        "Sprawdź wartość zmiennej względem warunku", "Verifica o valor de uma variável com uma condição",
        "Проверить значение переменной по условию", "Preveri vrednost spremenljivke s pogojem",
        "Перевірити значення змінної за умовою", "変数の値を条件と比べる", "按条件检查变量的值"),
}

_BUTTON_EVENT = {
    "forward": ("avant", "Vorwärts", "adelante", "avanti", "do przodu", "para frente", "вперёд", "naprej", "вперед", "前", "前进"),
    "backward": ("arrière", "Rückwärts", "atrás", "indietro", "do tyłu", "para trás", "назад", "nazaj", "назад", "後", "后退"),
    "left": ("gauche", "linke", "izquierdo", "sinistro", "lewy", "esquerdo", "левая", "levi", "ліва", "左", "左"),
    "right": ("droit", "rechte", "derecho", "destro", "prawy", "direito", "правая", "desni", "права", "右", "右"),
    "center": ("central", "mittlere", "central", "centrale", "środkowy", "central", "центральная", "srednji", "центральна",
               "中央", "中间"),
}


def _button_event(which):
    w = _BUTTON_EVENT[which]
    return _t(
        f"S'exécute quand le bouton {w[0]} est appuyé ou relâché (comme sur le vrai robot ; tester l'état du bouton pour savoir lequel)",
        f"Wird ausgeführt, wenn die Taste {w[1]} gedrückt oder losgelassen wird (wie beim echten Roboter; den Tastenzustand prüfen, um es zu unterscheiden)",
        f"Se ejecuta cuando el botón {w[2]} se pulsa o se suelta (como en el robot real; comprueba el estado del botón para saber cuál)",
        f"Eseguito quando il pulsante {w[3]} viene premuto o rilasciato (come sul robot vero; controlla lo stato del pulsante per capire quale)",
        f"Wykonywane, gdy przycisk {w[4]} zostanie naciśnięty lub puszczony (jak w prawdziwym robocie; sprawdź stan przycisku, by to rozróżnić)",
        f"Executado quando o botão {w[5]} é pressionado ou solto (como no robô real; verifique o estado do botão para saber qual)",
        f"Выполняется, когда кнопку «{w[6]}» нажимают или отпускают (как на настоящем роботе; проверьте состояние кнопки, чтобы различить)",
        f"Izvede se, ko je gumb {w[7]} pritisnjen ali spuščen (kot na pravem robotu; preveri stanje gumba, da ločiš)",
        f"Виконується, коли кнопку «{w[8]}» натискають або відпускають (як на справжньому роботі; перевірте стан кнопки, щоб розрізнити)",
        f"{w[9]}ボタンが押されたとき、または離されたときに実行（実機と同じ。どちらかはボタンの状態で調べる）",
        f"{w[10]}按钮被按下或松开时执行（与真实机器人一样；检查按钮状态来区分）")


EVENT_DESCRIPTIONS = {
    f"Executed when the {w} button is pressed or released (like the real robot; test the button state to tell which)": _button_event(w)
    for w in _BUTTON_EVENT
}
EVENT_DESCRIPTIONS.update({
    "Executed when any button state changes (use button conditions to check which)": _t(
        "S'exécute quand l'état d'un bouton change (utiliser les conditions de bouton pour savoir lequel)",
        "Wird ausgeführt, wenn sich der Zustand einer Taste ändert (mit Tastenbedingungen prüfen, welche)",
        "Se ejecuta cuando cambia el estado de un botón (usa las condiciones de botón para saber cuál)",
        "Eseguito quando cambia lo stato di un pulsante (usa le condizioni sui pulsanti per capire quale)",
        "Wykonywane, gdy zmieni się stan przycisku (użyj warunków przycisków, by sprawdzić który)",
        "Executado quando o estado de um botão muda (use as condições de botão para saber qual)",
        "Выполняется при изменении состояния кнопки (проверьте, какой, условиями кнопок)",
        "Izvede se, ko se stanje gumba spremeni (s pogoji za gumbe preveri, katerega)",
        "Виконується, коли змінюється стан кнопки (перевірте, якої, умовами кнопок)",
        "ボタンの状態が変わったときに実行（どのボタンかはボタンの条件で調べる）", "任一按钮状态变化时执行（用按钮条件检查是哪一个）"),
    "Executed when proximity sensors update (10 Hz / every 100ms)": _t(
        "S'exécute quand les capteurs de proximité sont mis à jour (10 Hz, toutes les 100 ms)",
        "Wird ausgeführt, wenn die Näherungssensoren aktualisiert werden (10 Hz, alle 100 ms)",
        "Se ejecuta cuando se actualizan los sensores de proximidad (10 Hz, cada 100 ms)",
        "Eseguito quando si aggiornano i sensori di prossimità (10 Hz, ogni 100 ms)",
        "Wykonywane przy aktualizacji czujników zbliżenia (10 Hz, co 100 ms)",
        "Executado quando os sensores de proximidade atualizam (10 Hz, a cada 100 ms)",
        "Выполняется при обновлении датчиков близости (10 Гц, каждые 100 мс)",
        "Izvede se ob posodobitvi senzorjev bližine (10 Hz, vsakih 100 ms)",
        "Виконується під час оновлення датчиків близькості (10 Гц, кожні 100 мс)",
        "近接センサーが更新されたときに実行（10 Hz、100 ms ごと）", "接近传感器更新时执行（10 Hz，每 100 毫秒）"),
    "Executed when ground sensors update (10 Hz / every 100ms)": _t(
        "S'exécute quand les capteurs de sol sont mis à jour (10 Hz, toutes les 100 ms)",
        "Wird ausgeführt, wenn die Bodensensoren aktualisiert werden (10 Hz, alle 100 ms)",
        "Se ejecuta cuando se actualizan los sensores de suelo (10 Hz, cada 100 ms)",
        "Eseguito quando si aggiornano i sensori del suolo (10 Hz, ogni 100 ms)",
        "Wykonywane przy aktualizacji czujników podłoża (10 Hz, co 100 ms)",
        "Executado quando os sensores de chão atualizam (10 Hz, a cada 100 ms)",
        "Выполняется при обновлении датчиков пола (10 Гц, каждые 100 мс)",
        "Izvede se ob posodobitvi senzorjev tal (10 Hz, vsakih 100 ms)",
        "Виконується під час оновлення датчиків підлоги (10 Гц, кожні 100 мс)",
        "床センサーが更新されたときに実行（10 Hz、100 ms ごと）", "地面传感器更新时执行（10 Hz，每 100 毫秒）"),
})
for _n in ("0", "1"):
    EVENT_DESCRIPTIONS[f"Executed when timer {_n} period expires (configure with Set Timer Period action)"] = _t(
        f"S'exécute quand la période de la minuterie {_n} est écoulée (à régler avec l'action Période de la minuterie)",
        f"Wird ausgeführt, wenn die Periode von Timer {_n} abläuft (mit der Aktion „Timer-Periode setzen“ einstellen)",
        f"Se ejecuta cuando termina el periodo del temporizador {_n} (se fija con la acción Periodo del temporizador)",
        f"Eseguito quando scade il periodo del timer {_n} (si imposta con l'azione Periodo del timer)",
        f"Wykonywane, gdy upłynie okres licznika czasu {_n} (ustaw akcją Ustaw okres licznika czasu)",
        f"Executado quando o período do temporizador {_n} termina (definido com a ação Período do temporizador)",
        f"Выполняется, когда истекает период таймера {_n} (задаётся действием «Задать период таймера»)",
        f"Izvede se, ko poteče perioda časovnika {_n} (nastaviš jo z dejanjem Nastavi periodo časovnika)",
        f"Виконується, коли минає період таймера {_n} (задається дією «Задати період таймера»)",
        f"タイマー {_n} の周期が来たときに実行（「タイマーの周期を設定」アクションで設定）",
        f"计时器 {_n} 周期到时执行（用“设置计时器周期”动作配置）")
EVENT_DESCRIPTIONS.update({
    "Executed when accelerometer detects a tap or shock": _t(
        "S'exécute quand l'accéléromètre détecte un tapotement ou un choc",
        "Wird ausgeführt, wenn der Beschleunigungssensor ein Antippen oder einen Stoß erkennt",
        "Se ejecuta cuando el acelerómetro detecta un toque o un golpe",
        "Eseguito quando l'accelerometro rileva un tocco o un urto",
        "Wykonywane, gdy akcelerometr wykryje stuknięcie lub wstrząs",
        "Executado quando o acelerômetro detecta um toque ou um choque",
        "Выполняется, когда акселерометр обнаруживает касание или удар",
        "Izvede se, ko pospeškometer zazna dotik ali sunek",
        "Виконується, коли акселерометр виявляє дотик або удар",
        "加速度センサーがタップや衝撃を検知したときに実行", "加速度计检测到敲击或撞击时执行"),
    "Executed when microphone detects sound above threshold": _t(
        "S'exécute quand le microphone détecte un son au-dessus du seuil",
        "Wird ausgeführt, wenn das Mikrofon ein Geräusch über der Schwelle erkennt",
        "Se ejecuta cuando el micrófono detecta un sonido por encima del umbral",
        "Eseguito quando il microfono rileva un suono sopra la soglia",
        "Wykonywane, gdy mikrofon wykryje dźwięk powyżej progu",
        "Executado quando o microfone detecta um som acima do limite",
        "Выполняется, когда микрофон слышит звук выше порога",
        "Izvede se, ko mikrofon zazna zvok nad pragom",
        "Виконується, коли мікрофон чує звук вище порога",
        "マイクがしきい値を超える音を検知したときに実行", "麦克风检测到超过阈值的声音时执行"),
    "Executed when sound playback completes": _t(
        "S'exécute quand la lecture d'un son est terminée", "Wird ausgeführt, wenn die Wiedergabe eines Tons endet",
        "Se ejecuta cuando termina la reproducción de un sonido", "Eseguito quando termina la riproduzione di un suono",
        "Wykonywane po zakończeniu odtwarzania dźwięku", "Executado quando a reprodução de um som termina",
        "Выполняется по окончании воспроизведения звука", "Izvede se, ko se predvajanje zvoka konča",
        "Виконується після завершення відтворення звуку", "音の再生が終わったときに実行", "声音播放完毕时执行"),
    "Executed when IR communication receives message from another Thymio": _t(
        "S'exécute quand la communication infrarouge reçoit un message d'un autre Thymio",
        "Wird ausgeführt, wenn per Infrarot eine Nachricht von einem anderen Thymio eintrifft",
        "Se ejecuta cuando la comunicación infrarroja recibe un mensaje de otro Thymio",
        "Eseguito quando la comunicazione infrarossa riceve un messaggio da un altro Thymio",
        "Wykonywane, gdy komunikacja w podczerwieni odbierze wiadomość od innego Thymio",
        "Executado quando a comunicação infravermelha recebe uma mensagem de outro Thymio",
        "Выполняется, когда по ИК-связи приходит сообщение от другого Thymio",
        "Izvede se, ko infrardeča povezava prejme sporočilo drugega Thymia",
        "Виконується, коли через ІЧ-зв'язок надходить повідомлення від іншого Thymio",
        "赤外線通信でほかの Thymio からメッセージを受け取ったときに実行", "红外通信收到另一台 Thymio 的消息时执行"),
})


PARAMS = {
    "Left Motor Speed": _t("Vitesse du moteur gauche", "Geschwindigkeit linker Motor", "Velocidad del motor izquierdo", "Velocità motore sinistro",
                           "Prędkość lewego silnika", "Velocidade do motor esquerdo", "Скорость левого мотора", "Hitrost levega motorja",
                           "Швидкість лівого мотора", "左モーターの速さ", "左电机速度"),
    "Right Motor Speed": _t("Vitesse du moteur droit", "Geschwindigkeit rechter Motor", "Velocidad del motor derecho", "Velocità motore destro",
                            "Prędkość prawego silnika", "Velocidade do motor direito", "Скорость правого мотора", "Hitrost desnega motorja",
                            "Швидкість правого мотора", "右モーターの速さ", "右电机速度"),
    "Speed": _t("Vitesse", "Geschwindigkeit", "Velocidad", "Velocità", "Prędkość", "Velocidade", "Скорость", "Hitrost", "Швидкість", "速さ", "速度"),
    "Turn Speed": _t("Vitesse de rotation", "Drehgeschwindigkeit", "Velocidad de giro", "Velocità di rotazione", "Prędkość obrotu",
                     "Velocidade de giro", "Скорость поворота", "Hitrost obračanja", "Швидкість повороту", "回る速さ", "转向速度"),
    "Red": _t("Rouge", "Rot", "Rojo", "Rosso", "Czerwony", "Vermelho", "Красный", "Rdeča", "Червоний", "赤", "红"),
    "Green": _t("Vert", "Grün", "Verde", "Verde", "Zielony", "Verde", "Зелёный", "Zelena", "Зелений", "緑", "绿"),
    "Blue": _t("Bleu", "Blau", "Azul", "Blu", "Niebieski", "Azul", "Синий", "Modra", "Синій", "青", "蓝"),
    "LED Position": _t("Position de la LED", "LED-Position", "Posición del LED", "Posizione del LED", "Pozycja diody LED", "Posição do LED",
                       "Положение светодиода", "Položaj LED", "Положення світлодіода", "LED の位置", "LED 位置"),
    "Intensity": _t("Intensité", "Helligkeit", "Intensidad", "Intensità", "Jasność", "Intensidade", "Яркость", "Jakost", "Яскравість", "明るさ", "亮度"),
    "Frequency (Hz)": _t("Fréquence (Hz)", "Frequenz (Hz)", "Frecuencia (Hz)", "Frequenza (Hz)", "Częstotliwość (Hz)", "Frequência (Hz)",
                         "Частота (Гц)", "Frekvenca (Hz)", "Частота (Гц)", "周波数（Hz）", "频率（Hz）"),
    "Duration": _t("Durée", "Dauer", "Duración", "Durata", "Czas trwania", "Duração", "Длительность", "Trajanje", "Тривалість", "長さ", "时长"),
    "System Sound": _t("Son système", "Systemton", "Sonido del sistema", "Suono di sistema", "Dźwięk systemowy", "Som do sistema",
                       "Системный звук", "Sistemski zvok", "Системний звук", "システム音", "系统声音"),
    "Sensor": _t("Capteur", "Sensor", "Sensor", "Sensore", "Czujnik", "Sensor", "Датчик", "Senzor", "Датчик", "センサー", "传感器"),
    "Store in Variable": _t("Ranger dans la variable", "In Variable speichern", "Guardar en la variable", "Salva nella variabile",
                            "Zapisz w zmiennej", "Guardar na variável", "Сохранить в переменной", "Shrani v spremenljivko",
                            "Зберегти у змінній", "入れる変数", "存入变量"),
    "Button": _t("Bouton", "Taste", "Botón", "Pulsante", "Przycisk", "Botão", "Кнопка", "Gumb", "Кнопка", "ボタン", "按钮"),
    "Threshold": _t("Seuil", "Schwelle", "Umbral", "Soglia", "Próg", "Limite", "Порог", "Prag", "Поріг", "しきい値", "阈值"),
    "Comparison": _t("Comparaison", "Vergleich", "Comparación", "Confronto", "Porównanie", "Comparação", "Сравнение", "Primerjava",
                     "Порівняння", "比較", "比较"),
    "Timer": _t("Minuterie", "Timer", "Temporizador", "Timer", "Licznik czasu", "Temporizador", "Таймер", "Časovnik", "Таймер",
                "タイマー", "计时器"),
    "Period (ms)": _t("Période (ms)", "Periode (ms)", "Periodo (ms)", "Periodo (ms)", "Okres (ms)", "Período (ms)", "Период (мс)",
                      "Perioda (ms)", "Період (мс)", "周期（ms）", "周期（毫秒）"),
    "Variable Name": _t("Nom de la variable", "Variablenname", "Nombre de la variable", "Nome della variabile", "Nazwa zmiennej",
                        "Nome da variável", "Имя переменной", "Ime spremenljivke", "Назва змінної", "変数名", "变量名"),
    "Value": _t("Valeur", "Wert", "Valor", "Valore", "Wartość", "Valor", "Значение", "Vrednost", "Значення", "値", "值"),
    "Amount": _t("Quantité", "Betrag", "Cantidad", "Quantità", "Wartość", "Quantidade", "Величина", "Količina", "Величина", "量", "数量"),
}
_LED = ("LED", "LED", "LED", "LED", "Dioda", "LED", "Светодиод", "LED", "Світлодіод", "LED", "LED")
_SIDE = {"Front": ("avant", "vorne", "delante", "davanti", "przód", "frente", "перед", "spredaj", "перед", "前", "前"),
         "Right": ("droite", "rechts", "derecha", "destra", "prawo", "direita", "справа", "desno", "праворуч", "右", "右"),
         "Back": ("arrière", "hinten", "detrás", "dietro", "tył", "trás", "сзади", "zadaj", "ззаду", "後", "后"),
         "Left": ("gauche", "links", "izquierda", "sinistra", "lewo", "esquerda", "слева", "levo", "ліворуч", "左", "左")}
for _i in range(8):
    PARAMS[f"LED {_i}"] = dict(zip(LANGS, (f"{w} {_i}" for w in _LED)))
for _i, _side in ((0, "Front"), (3, "Right"), (4, "Back"), (7, "Left")):
    PARAMS[f"LED {_i} ({_side})"] = dict(zip(LANGS, (f"{w} {_i} ({s})" for w, s in zip(_LED, _SIDE[_side]))))

PARAM_DESCRIPTIONS = {
    "Left motor speed (-500 to 500, or variable)": _t(
        "Vitesse du moteur gauche (-500 à 500, ou une variable)", "Geschwindigkeit linker Motor (-500 bis 500 oder Variable)",
        "Velocidad del motor izquierdo (-500 a 500, o una variable)", "Velocità del motore sinistro (da -500 a 500, o variabile)",
        "Prędkość lewego silnika (od -500 do 500 lub zmienna)", "Velocidade do motor esquerdo (-500 a 500, ou variável)",
        "Скорость левого мотора (от -500 до 500 или переменная)", "Hitrost levega motorja (od -500 do 500 ali spremenljivka)",
        "Швидкість лівого мотора (від -500 до 500 або змінна)", "左モーターの速さ（-500〜500 か変数）", "左电机速度（-500 到 500，或变量）"),
    "Right motor speed (-500 to 500, or variable)": _t(
        "Vitesse du moteur droit (-500 à 500, ou une variable)", "Geschwindigkeit rechter Motor (-500 bis 500 oder Variable)",
        "Velocidad del motor derecho (-500 a 500, o una variable)", "Velocità del motore destro (da -500 a 500, o variabile)",
        "Prędkość prawego silnika (od -500 do 500 lub zmienna)", "Velocidade do motor direito (-500 a 500, ou variável)",
        "Скорость правого мотора (от -500 до 500 или переменная)", "Hitrost desnega motorja (od -500 do 500 ali spremenljivka)",
        "Швидкість правого мотора (від -500 до 500 або змінна)", "右モーターの速さ（-500〜500 か変数）", "右电机速度（-500 到 500，或变量）"),
    "Backward speed (0 to 500, or variable)": _t(
        "Vitesse de recul (0 à 500, ou une variable)", "Rückwärtsgeschwindigkeit (0 bis 500 oder Variable)",
        "Velocidad hacia atrás (0 a 500, o una variable)", "Velocità all'indietro (da 0 a 500, o variabile)",
        "Prędkość do tyłu (od 0 do 500 lub zmienna)", "Velocidade para trás (0 a 500, ou variável)",
        "Скорость назад (от 0 до 500 или переменная)", "Hitrost nazaj (od 0 do 500 ali spremenljivka)",
        "Швидкість назад (від 0 до 500 або змінна)", "後退の速さ（0〜500 か変数）", "后退速度（0 到 500，或变量）"),
    "Forward speed (0 to 500, or variable)": _t(
        "Vitesse d'avance (0 à 500, ou une variable)", "Vorwärtsgeschwindigkeit (0 bis 500 oder Variable)",
        "Velocidad hacia delante (0 a 500, o una variable)", "Velocità in avanti (da 0 a 500, o variabile)",
        "Prędkość do przodu (od 0 do 500 lub zmienna)", "Velocidade para frente (0 a 500, ou variável)",
        "Скорость вперёд (от 0 до 500 или переменная)", "Hitrost naprej (od 0 do 500 ali spremenljivka)",
        "Швидкість уперед (від 0 до 500 або змінна)", "前進の速さ（0〜500 か変数）", "前进速度（0 到 500，或变量）"),
    "Rotation speed (0 to 500, or variable)": _t(
        "Vitesse de rotation (0 à 500, ou une variable)", "Drehgeschwindigkeit (0 bis 500 oder Variable)",
        "Velocidad de giro (0 a 500, o una variable)", "Velocità di rotazione (da 0 a 500, o variabile)",
        "Prędkość obrotu (od 0 do 500 lub zmienna)", "Velocidade de giro (0 a 500, ou variável)",
        "Скорость поворота (от 0 до 500 или переменная)", "Hitrost obračanja (od 0 do 500 ali spremenljivka)",
        "Швидкість повороту (від 0 до 500 або змінна)", "回る速さ（0〜500 か変数）", "转向速度（0 到 500，或变量）"),
    "Which circle LED to control (0-7, clockwise from front)": _t(
        "Quelle LED du cercle (0-7, dans le sens des aiguilles d'une montre depuis l'avant)",
        "Welche Kreis-LED (0-7, im Uhrzeigersinn von vorne)", "Qué LED del círculo (0-7, en sentido horario desde delante)",
        "Quale LED del cerchio (0-7, in senso orario dal davanti)", "Która dioda LED okręgu (0-7, zgodnie z ruchem wskazówek zegara od przodu)",
        "Qual LED do círculo (0-7, no sentido horário a partir da frente)", "Какой светодиод круга (0-7, по часовой стрелке от переда)",
        "Katera LED kroga (0-7, v smeri urinega kazalca od spredaj)", "Який світлодіод кола (0-7, за годинниковою стрілкою від переду)",
        "円のどの LED か（0〜7、前から時計回り）", "圆环上的哪个 LED（0-7，从前方顺时针）"),
    "LED intensity (0-32, or variable)": _t(
        "Intensité de la LED (0-32, ou une variable)", "LED-Helligkeit (0-32 oder Variable)", "Intensidad del LED (0-32, o una variable)",
        "Intensità del LED (0-32, o variabile)", "Jasność diody LED (0-32 lub zmienna)", "Intensidade do LED (0-32, ou variável)",
        "Яркость светодиода (0-32 или переменная)", "Jakost LED (0-32 ali spremenljivka)", "Яскравість світлодіода (0-32 або змінна)",
        "LED の明るさ（0〜32 か変数）", "LED 亮度（0-32，或变量）"),
    "Intensity 0-32": _t("Intensité 0-32", "Helligkeit 0-32", "Intensidad 0-32", "Intensità 0-32", "Jasność 0-32", "Intensidade 0-32",
                         "Яркость 0-32", "Jakost 0-32", "Яскравість 0-32", "明るさ 0〜32", "亮度 0-32"),
    "Tone frequency in Hertz (e.g., 440 for A4, or variable)": _t(
        "Fréquence de la note en hertz (p. ex. 440 pour le la, ou une variable)", "Tonfrequenz in Hertz (z. B. 440 für a', oder Variable)",
        "Frecuencia del tono en hercios (p. ej., 440 para el la, o una variable)", "Frequenza del tono in hertz (es. 440 per il la, o variabile)",
        "Częstotliwość tonu w hercach (np. 440 dla a1, lub zmienna)", "Frequência do tom em hertz (ex.: 440 para o lá, ou variável)",
        "Частота тона в герцах (например, 440 — ля, или переменная)", "Frekvenca tona v hercih (npr. 440 za a1, ali spremenljivka)",
        "Частота тону в герцах (наприклад, 440 — ля, або змінна)", "音の周波数（Hz、例: ラは 440、または変数）", "音调频率，单位赫兹（例如 440 为 A4，或变量）"),
    "Duration in 1/60 second units (e.g., 60 = 1 second, -1 = continuous, or variable)": _t(
        "Durée en 1/60 de seconde (p. ex. 60 = 1 seconde, -1 = continu, ou une variable)",
        "Dauer in 1/60 Sekunde (z. B. 60 = 1 Sekunde, -1 = dauerhaft, oder Variable)",
        "Duración en 1/60 de segundo (p. ej., 60 = 1 segundo, -1 = continuo, o una variable)",
        "Durata in 1/60 di secondo (es. 60 = 1 secondo, -1 = continuo, o variabile)",
        "Czas w 1/60 sekundy (np. 60 = 1 sekunda, -1 = bez końca, lub zmienna)",
        "Duração em 1/60 de segundo (ex.: 60 = 1 segundo, -1 = contínuo, ou variável)",
        "Длительность в 1/60 секунды (например, 60 = 1 секунда, -1 = непрерывно, или переменная)",
        "Trajanje v 1/60 sekunde (npr. 60 = 1 sekunda, -1 = neprekinjeno, ali spremenljivka)",
        "Тривалість у 1/60 секунди (наприклад, 60 = 1 секунда, -1 = безперервно, або змінна)",
        "長さ（1/60 秒単位、例: 60 = 1 秒、-1 = 鳴らし続ける、または変数）", "时长，单位 1/60 秒（例如 60 = 1 秒，-1 = 持续，或变量）"),
    "Which system sound to play": _t(
        "Quel son système jouer", "Welcher Systemton abgespielt wird", "Qué sonido del sistema tocar", "Quale suono di sistema suonare",
        "Który dźwięk systemowy odtworzyć", "Qual som do sistema tocar", "Какой системный звук воспроизвести",
        "Kateri sistemski zvok predvajati", "Який системний звук відтворити", "鳴らすシステム音", "要播放的系统声音"),
    "Which ground sensor to check": _t(
        "Quel capteur de sol tester", "Welcher Bodensensor geprüft wird", "Qué sensor de suelo comprobar", "Quale sensore del suolo controllare",
        "Który czujnik podłoża sprawdzić", "Qual sensor de chão verificar", "Какой датчик пола проверить", "Kateri senzor tal preveriti",
        "Який датчик підлоги перевірити", "調べる床センサー", "要检查的地面传感器"),
    "Which ground sensor to read": _t(
        "Quel capteur de sol lire", "Welcher Bodensensor gelesen wird", "Qué sensor de suelo leer", "Quale sensore del suolo leggere",
        "Który czujnik podłoża odczytać", "Qual sensor de chão ler", "Какой датчик пола прочитать", "Kateri senzor tal prebrati",
        "Який датчик підлоги прочитати", "読む床センサー", "要读取的地面传感器"),
    "Which proximity sensor to check": _t(
        "Quel capteur de proximité tester", "Welcher Näherungssensor geprüft wird", "Qué sensor de proximidad comprobar",
        "Quale sensore di prossimità controllare", "Który czujnik zbliżenia sprawdzić", "Qual sensor de proximidade verificar",
        "Какой датчик близости проверить", "Kateri senzor bližine preveriti", "Який датчик близькості перевірити",
        "調べる近接センサー", "要检查的接近传感器"),
    "Which proximity sensor to read": _t(
        "Quel capteur de proximité lire", "Welcher Näherungssensor gelesen wird", "Qué sensor de proximidad leer",
        "Quale sensore di prossimità leggere", "Który czujnik zbliżenia odczytać", "Qual sensor de proximidade ler",
        "Какой датчик близости прочитать", "Kateri senzor bližine prebrati", "Який датчик близькості прочитати",
        "読む近接センサー", "要读取的接近传感器"),
    "Variable name to store button state (0 or 1)": _t(
        "Nom de la variable où ranger l'état du bouton (0 ou 1)", "Name der Variablen für den Tastenzustand (0 oder 1)",
        "Nombre de la variable donde guardar el estado del botón (0 o 1)", "Nome della variabile in cui salvare lo stato del pulsante (0 o 1)",
        "Nazwa zmiennej na stan przycisku (0 lub 1)", "Nome da variável onde guardar o estado do botão (0 ou 1)",
        "Имя переменной для состояния кнопки (0 или 1)", "Ime spremenljivke za stanje gumba (0 ali 1)",
        "Назва змінної для стану кнопки (0 або 1)", "ボタンの状態を入れる変数の名前（0 か 1）", "存放按钮状态的变量名（0 或 1）"),
    "Variable name to store the sensor value": _t(
        "Nom de la variable où ranger la valeur du capteur", "Name der Variablen für den Sensorwert",
        "Nombre de la variable donde guardar el valor del sensor", "Nome della variabile in cui salvare il valore del sensore",
        "Nazwa zmiennej na wartość czujnika", "Nome da variável onde guardar o valor do sensor", "Имя переменной для значения датчика",
        "Ime spremenljivke za vrednost senzorja", "Назва змінної для значення датчика", "センサーの値を入れる変数の名前",
        "存放传感器值的变量名"),
    "Variable name to store the sensor value (0-4000)": _t(
        "Nom de la variable où ranger la valeur du capteur (0-4000)", "Name der Variablen für den Sensorwert (0-4000)",
        "Nombre de la variable donde guardar el valor del sensor (0-4000)", "Nome della variabile in cui salvare il valore del sensore (0-4000)",
        "Nazwa zmiennej na wartość czujnika (0-4000)", "Nome da variável onde guardar o valor do sensor (0-4000)",
        "Имя переменной для значения датчика (0-4000)", "Ime spremenljivke za vrednost senzorja (0-4000)",
        "Назва змінної для значення датчика (0-4000)", "センサーの値（0〜4000）を入れる変数の名前", "存放传感器值（0-4000）的变量名"),
    "Which button to check": _t(
        "Quel bouton tester", "Welche Taste geprüft wird", "Qué botón comprobar", "Quale pulsante controllare", "Który przycisk sprawdzić",
        "Qual botão verificar", "Какую кнопку проверить", "Kateri gumb preveriti", "Яку кнопку перевірити", "調べるボタン", "要检查的按钮"),
    "Which button to read": _t(
        "Quel bouton lire", "Welche Taste gelesen wird", "Qué botón leer", "Quale pulsante leggere", "Który przycisk odczytać",
        "Qual botão ler", "Какую кнопку прочитать", "Kateri gumb prebrati", "Яку кнопку прочитати", "読むボタン", "要读取的按钮"),
    "Dark detection threshold (typically 300, or variable)": _t(
        "Seuil de détection du sombre (souvent 300, ou une variable)", "Schwelle für dunkel (meist 300, oder Variable)",
        "Umbral de oscuridad (normalmente 300, o una variable)", "Soglia per lo scuro (di solito 300, o variabile)",
        "Próg ciemności (zwykle 300 lub zmienna)", "Limite de escuro (geralmente 300, ou variável)",
        "Порог тёмного (обычно 300 или переменная)", "Prag za temno (običajno 300 ali spremenljivka)",
        "Поріг темного (зазвичай 300 або змінна)", "暗いと判断するしきい値（ふつう 300、または変数）", "判定为暗的阈值（通常 300，或变量）"),
    "Detection threshold (0-4000, typically 2000 for ~5cm, or variable)": _t(
        "Seuil de détection (0-4000, souvent 2000 pour environ 5 cm, ou une variable)",
        "Erkennungsschwelle (0-4000, meist 2000 für ca. 5 cm, oder Variable)",
        "Umbral de detección (0-4000, normalmente 2000 para unos 5 cm, o una variable)",
        "Soglia di rilevamento (0-4000, di solito 2000 per circa 5 cm, o variabile)",
        "Próg wykrywania (0-4000, zwykle 2000 dla ok. 5 cm, lub zmienna)",
        "Limite de detecção (0-4000, geralmente 2000 para cerca de 5 cm, ou variável)",
        "Порог обнаружения (0-4000, обычно 2000 — около 5 см, или переменная)",
        "Prag zaznave (0-4000, običajno 2000 za približno 5 cm, ali spremenljivka)",
        "Поріг виявлення (0-4000, зазвичай 2000 — близько 5 см, або змінна)",
        "検知のしきい値（0〜4000、約 5 cm ならふつう 2000、または変数）", "检测阈值（0-4000，约 5 厘米通常为 2000，或变量）"),
    "Light detection threshold (typically 300, or variable)": _t(
        "Seuil de détection du clair (souvent 300, ou une variable)", "Schwelle für hell (meist 300, oder Variable)",
        "Umbral de claridad (normalmente 300, o una variable)", "Soglia per il chiaro (di solito 300, o variabile)",
        "Próg jasności (zwykle 300 lub zmienna)", "Limite de claro (geralmente 300, ou variável)",
        "Порог светлого (обычно 300 или переменная)", "Prag za svetlo (običajno 300 ali spremenljivka)",
        "Поріг світлого (зазвичай 300 або змінна)", "明るいと判断するしきい値（ふつう 300、または変数）", "判定为亮的阈值（通常 300，或变量）"),
    "Comparison operator": _t("Opérateur de comparaison", "Vergleichsoperator", "Operador de comparación", "Operatore di confronto",
                              "Operator porównania", "Operador de comparação", "Оператор сравнения", "Primerjalni operator",
                              "Оператор порівняння", "比較の演算子", "比较运算符"),
    "How to compare sensor value to threshold": _t(
        "Comment comparer la valeur du capteur au seuil", "Wie der Sensorwert mit der Schwelle verglichen wird",
        "Cómo comparar el valor del sensor con el umbral", "Come confrontare il valore del sensore con la soglia",
        "Jak porównać wartość czujnika z progiem", "Como comparar o valor do sensor com o limite",
        "Как сравнивать значение датчика с порогом", "Kako primerjati vrednost senzorja s pragom",
        "Як порівнювати значення датчика з порогом", "センサーの値としきい値の比べ方", "如何将传感器值与阈值比较"),
    "Which timer to configure (0 or 1)": _t(
        "Quelle minuterie régler (0 ou 1)", "Welcher Timer eingestellt wird (0 oder 1)", "Qué temporizador configurar (0 o 1)",
        "Quale timer configurare (0 o 1)", "Który licznik czasu ustawić (0 lub 1)", "Qual temporizador configurar (0 ou 1)",
        "Какой таймер настроить (0 или 1)", "Kateri časovnik nastaviti (0 ali 1)", "Який таймер налаштувати (0 або 1)",
        "設定するタイマー（0 か 1）", "要配置的计时器（0 或 1）"),
    "Timer period in milliseconds (e.g., 1000 = 1 second, or variable)": _t(
        "Période en millisecondes (p. ex. 1000 = 1 seconde, ou une variable)", "Periode in Millisekunden (z. B. 1000 = 1 Sekunde, oder Variable)",
        "Periodo en milisegundos (p. ej., 1000 = 1 segundo, o una variable)", "Periodo in millisecondi (es. 1000 = 1 secondo, o variabile)",
        "Okres w milisekundach (np. 1000 = 1 sekunda, lub zmienna)", "Período em milissegundos (ex.: 1000 = 1 segundo, ou variável)",
        "Период в миллисекундах (например, 1000 = 1 секунда, или переменная)", "Perioda v milisekundah (npr. 1000 = 1 sekunda, ali spremenljivka)",
        "Період у мілісекундах (наприклад, 1000 = 1 секунда, або змінна)", "周期（ミリ秒、例: 1000 = 1 秒、または変数）",
        "周期，单位毫秒（例如 1000 = 1 秒，或变量）"),
    "Variable name (will be declared in Aseba)": _t(
        "Nom de la variable (déclarée dans Aseba)", "Variablenname (wird in Aseba deklariert)", "Nombre de la variable (se declara en Aseba)",
        "Nome della variabile (dichiarata in Aseba)", "Nazwa zmiennej (zostanie zadeklarowana w Aseba)", "Nome da variável (declarada no Aseba)",
        "Имя переменной (объявляется в Aseba)", "Ime spremenljivke (deklarirana v Asebi)", "Назва змінної (оголошується в Aseba)",
        "変数名（Aseba で宣言されます）", "变量名（将在 Aseba 中声明）"),
    "Variable name to decrease": _t("Nom de la variable à diminuer", "Name der zu verringernden Variablen", "Nombre de la variable que disminuir",
                                    "Nome della variabile da diminuire", "Nazwa zmiennej do zmniejszenia", "Nome da variável a diminuir",
                                    "Имя уменьшаемой переменной", "Ime spremenljivke za zmanjšanje", "Назва змінної для зменшення",
                                    "減らす変数の名前", "要减少的变量名"),
    "Variable name to increase": _t("Nom de la variable à augmenter", "Name der zu erhöhenden Variablen", "Nombre de la variable que aumentar",
                                    "Nome della variabile da aumentare", "Nazwa zmiennej do zwiększenia", "Nome da variável a aumentar",
                                    "Имя увеличиваемой переменной", "Ime spremenljivke za povečanje", "Назва змінної для збільшення",
                                    "増やす変数の名前", "要增加的变量名"),
    "Variable to check": _t("Variable à tester", "Zu prüfende Variable", "Variable que comprobar", "Variabile da controllare",
                            "Zmienna do sprawdzenia", "Variável a verificar", "Проверяемая переменная", "Spremenljivka za preverjanje",
                            "Змінна для перевірки", "調べる変数", "要检查的变量"),
    "Value to assign (integer, or expression)": _t(
        "Valeur à donner (nombre entier ou expression)", "Zuzuweisender Wert (Ganzzahl oder Ausdruck)", "Valor que asignar (entero o expresión)",
        "Valore da assegnare (intero o espressione)", "Wartość do przypisania (liczba całkowita lub wyrażenie)",
        "Valor a atribuir (inteiro ou expressão)", "Присваиваемое значение (целое или выражение)",
        "Vrednost za nastavitev (celo število ali izraz)", "Значення для присвоєння (ціле або вираз)", "入れる値（整数か式）",
        "要赋的值（整数或表达式）"),
    "Value to compare against": _t("Valeur de comparaison", "Vergleichswert", "Valor con el que comparar", "Valore con cui confrontare",
                                   "Wartość do porównania", "Valor de comparação", "Значение для сравнения", "Vrednost za primerjavo",
                                   "Значення для порівняння", "比べる値", "用于比较的值"),
    "Amount to add (default 1)": _t("Quantité à ajouter (1 par défaut)", "Hinzuzufügender Betrag (Standard 1)", "Cantidad que sumar (1 por defecto)",
                                    "Quantità da aggiungere (predefinita 1)", "Wartość do dodania (domyślnie 1)", "Quantidade a somar (padrão 1)",
                                    "Сколько прибавить (по умолчанию 1)", "Koliko prišteti (privzeto 1)", "Скільки додати (типово 1)",
                                    "足す量（既定は 1）", "要加的数量（默认 1）"),
    "Amount to subtract (default 1)": _t("Quantité à retirer (1 par défaut)", "Abzuziehender Betrag (Standard 1)", "Cantidad que restar (1 por defecto)",
                                         "Quantità da togliere (predefinita 1)", "Wartość do odjęcia (domyślnie 1)", "Quantidade a subtrair (padrão 1)",
                                         "Сколько вычесть (по умолчанию 1)", "Koliko odšteti (privzeto 1)", "Скільки відняти (типово 1)",
                                         "引く量（既定は 1）", "要减的数量（默认 1）"),
}
for _c, _w in (("Red", 0), ("Green", 1), ("Blue", 2)):
    _names = [t for t in PARAMS[_c].values()]
    PARAM_DESCRIPTIONS[f"{_c} intensity (0-32, or variable)"] = dict(zip(LANGS, (
        f"Intensité du {_names[0].lower()} (0-32, ou une variable)", f"{_names[1]}-Anteil (0-32 oder Variable)",
        f"Intensidad del {_names[2].lower()} (0-32, o una variable)", f"Intensità del {_names[3].lower()} (0-32, o variabile)",
        f"{_names[4]} (0-32 lub zmienna)", f"Intensidade do {_names[5].lower()} (0-32, ou variável)",
        f"{_names[6]} (0-32 или переменная)", f"{_names[7]} (0-32 ali spremenljivka)", f"{_names[8]} (0-32 або змінна)",
        f"{_names[9]}の明るさ（0〜32 か変数）", f"{_names[10]}色亮度（0-32，或变量）")))

CHOICES = {}
_SOUND = {
    "Startup": ("Démarrage", "Start", "Inicio", "Avvio", "Uruchomienie", "Início", "Запуск", "Zagon", "Запуск", "起動", "启动"),
    "Shutdown": ("Extinction", "Ausschalten", "Apagado", "Spegnimento", "Wyłączenie", "Desligamento", "Выключение", "Izklop", "Вимкнення",
                 "終了", "关机"),
    "Arrow": ("Flèche", "Pfeil", "Flecha", "Freccia", "Strzałka", "Seta", "Стрелка", "Puščica", "Стрілка", "矢印", "箭头"),
    "Central": ("Central", "Mitte", "Central", "Centrale", "Środkowy", "Central", "Центральный", "Sredinski", "Центральний", "中央", "中间"),
    "Free Fall": ("Chute libre", "Freier Fall", "Caída libre", "Caduta libera", "Swobodny spadek", "Queda livre", "Свободное падение",
                  "Prosti pad", "Вільне падіння", "自由落下", "自由落体"),
    "Collision": ("Collision", "Kollision", "Colisión", "Collisione", "Zderzenie", "Colisão", "Столкновение", "Trk", "Зіткнення",
                  "衝突", "碰撞"),
    "Target Friendly": ("Cible amie", "Freundliches Ziel", "Objetivo amigo", "Bersaglio amico", "Cel przyjazny", "Alvo amigo",
                        "Дружественная цель", "Prijazna tarča", "Дружня ціль", "味方の目標", "友方目标"),
    "Target Detected": ("Cible détectée", "Ziel erkannt", "Objetivo detectado", "Bersaglio rilevato", "Wykryto cel", "Alvo detectado",
                        "Цель обнаружена", "Tarča zaznana", "Ціль виявлено", "目標を検知", "检测到目标"),
    "Front Left Far": ("Avant gauche loin", "Vorne links außen", "Delante izquierda lejos", "Davanti sinistra esterno", "Przód lewy skrajny",
                       "Frente esquerda longe", "Перед слева крайний", "Spredaj levo zunaj", "Перед ліворуч крайній", "前左外", "前左外侧"),
    "Front Left": ("Avant gauche", "Vorne links", "Delante izquierda", "Davanti sinistra", "Przód lewy", "Frente esquerda", "Перед слева",
                   "Spredaj levo", "Перед ліворуч", "前左", "前左"),
    "Front Center": ("Avant centre", "Vorne Mitte", "Delante centro", "Davanti centro", "Przód środek", "Frente centro", "Перед по центру",
                     "Spredaj sredina", "Перед по центру", "前中央", "前中"),
    "Front Right": ("Avant droit", "Vorne rechts", "Delante derecha", "Davanti destra", "Przód prawy", "Frente direita", "Перед справа",
                    "Spredaj desno", "Перед праворуч", "前右", "前右"),
    "Front Right Far": ("Avant droit loin", "Vorne rechts außen", "Delante derecha lejos", "Davanti destra esterno", "Przód prawy skrajny",
                        "Frente direita longe", "Перед справа крайний", "Spredaj desno zunaj", "Перед праворуч крайній", "前右外", "前右外侧"),
    "Back Left": ("Arrière gauche", "Hinten links", "Detrás izquierda", "Dietro sinistra", "Tył lewy", "Trás esquerda", "Сзади слева",
                  "Zadaj levo", "Ззаду ліворуч", "後左", "后左"),
    "Back Right": ("Arrière droit", "Hinten rechts", "Detrás derecha", "Dietro destra", "Tył prawy", "Trás direita", "Сзади справа",
                   "Zadaj desno", "Ззаду праворуч", "後右", "后右"),
    "Left": ("Gauche", "Links", "Izquierda", "Sinistra", "Lewy", "Esquerda", "Левый", "Levi", "Лівий", "左", "左"),
    "Right": ("Droit", "Rechts", "Derecha", "Destra", "Prawy", "Direita", "Правый", "Desni", "Правий", "右", "右"),
}
_NUMBERED = [("0", "Startup"), ("1", "Shutdown"), ("2", "Arrow"), ("3", "Central"), ("4", "Free Fall"), ("5", "Collision"),
             ("6", "Target Friendly"), ("7", "Target Detected"), ("0", "Front Left Far"), ("1", "Front Left"), ("2", "Front Center"),
             ("3", "Front Right"), ("4", "Front Right Far"), ("5", "Back Left"), ("6", "Back Right"), ("0", "Left"), ("1", "Right")]
for _n, _w in _NUMBERED:
    CHOICES[f"{_n} - {_w}"] = dict(zip(LANGS, (f"{_n} - {t}" for t in _SOUND[_w])))
CHOICES.update({
    "forward": _t("avant", "vorwärts", "adelante", "avanti", "do przodu", "para frente", "вперёд", "naprej", "вперед", "前", "前进"),
    "backward": _t("arrière", "rückwärts", "atrás", "indietro", "do tyłu", "para trás", "назад", "nazaj", "назад", "後", "后退"),
    "left": _t("gauche", "links", "izquierda", "sinistra", "lewy", "esquerda", "левая", "levi", "ліва", "左", "左"),
    "right": _t("droite", "rechts", "derecha", "destra", "prawy", "direita", "правая", "desni", "права", "右", "右"),
    "center": _t("centre", "Mitte", "centro", "centro", "środkowy", "centro", "центральная", "srednji", "центральна", "中央", "中间"),
})

CATEGORIES = {
    "Thymio Buttons": _t("Boutons Thymio", "Thymio-Tasten", "Botones de Thymio", "Pulsanti Thymio", "Przyciski Thymio", "Botões do Thymio",
                         "Кнопки Thymio", "Gumbi Thymio", "Кнопки Thymio", "Thymio ボタン", "Thymio 按钮"),
    "Thymio Sensors": _t("Capteurs Thymio", "Thymio-Sensoren", "Sensores de Thymio", "Sensori Thymio", "Czujniki Thymio", "Sensores do Thymio",
                         "Датчики Thymio", "Senzorji Thymio", "Датчики Thymio", "Thymio センサー", "Thymio 传感器"),
    "Thymio Timing": _t("Minuteries Thymio", "Thymio-Zeitsteuerung", "Temporización de Thymio", "Temporizzazione Thymio", "Czas Thymio",
                        "Tempo do Thymio", "Время Thymio", "Časovniki Thymio", "Час Thymio", "Thymio タイマー", "Thymio 计时"),
    "Thymio Sound": _t("Son Thymio", "Thymio-Klang", "Sonido de Thymio", "Suono Thymio", "Dźwięk Thymio", "Som do Thymio", "Звук Thymio",
                       "Zvok Thymio", "Звук Thymio", "Thymio サウンド", "Thymio 声音"),
    "Thymio Communication": _t("Communication Thymio", "Thymio-Kommunikation", "Comunicación de Thymio", "Comunicazione Thymio",
                               "Komunikacja Thymio", "Comunicação do Thymio", "Связь Thymio", "Komunikacija Thymio", "Зв'язок Thymio",
                               "Thymio 通信", "Thymio 通信"),
    "Motors": _t("Moteurs", "Motoren", "Motores", "Motori", "Silniki", "Motores", "Моторы", "Motorji", "Мотори", "モーター", "电机"),
    "LEDs": _t("LED", "LEDs", "LED", "LED", "Diody LED", "LEDs", "Светодиоды", "LED", "Світлодіоди", "LED", "LED 灯"),
    "Sound": _t("Son", "Klang", "Sonido", "Suono", "Dźwięk", "Som", "Звук", "Zvok", "Звук", "サウンド", "声音"),
    "Sensors": _t("Capteurs", "Sensoren", "Sensores", "Sensori", "Czujniki", "Sensores", "Датчики", "Senzorji", "Датчики", "センサー", "传感器"),
    "Conditions": _t("Conditions", "Bedingungen", "Condiciones", "Condizioni", "Warunki", "Condições", "Условия", "Pogoji", "Умови", "条件", "条件"),
    "Timing": _t("Minuteries", "Zeitsteuerung", "Temporización", "Temporizzazione", "Czas", "Tempo", "Время", "Časovniki", "Час", "タイマー", "计时"),
    "Variables": _t("Variables", "Variablen", "Variables", "Variabili", "Zmienne", "Variáveis", "Переменные", "Spremenljivke", "Змінні", "変数", "变量"),
}


def _names(registry):
    """English display name -> the Configure dialog's translation of the same key."""
    out = {}
    for key, item in registry.items():
        entry = PLUGIN_BLOCK_TRANSLATIONS.get(key)
        if entry is not None:
            out[item.display_name] = dict(entry["name"])
    return out


PLUGIN_UI_TRANSLATIONS = {
    "action": _names(THYMIO_ACTIONS),
    "event": _names(THYMIO_EVENT_TYPES),
    "action_description": ACTION_DESCRIPTIONS,
    "event_description": EVENT_DESCRIPTIONS,
    "param": PARAMS,
    "param_description": PARAM_DESCRIPTIONS,
    "choice": CHOICES,
    "category": CATEGORIES,
}
