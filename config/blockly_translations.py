#!/usr/bin/env python3
"""
Blockly Block Translations
Translations for block categories, names, and descriptions
Based on Scratch and Blockly standard French translations
"""

# Category name translations
CATEGORY_TRANSLATIONS = {
    "de": {
        "Events": "Ereignisse",
        "Movement": "Bewegung",
        "Timing": "Zeitsteuerung",
        "Drawing": "Zeichnen",
        "Score/Lives/Health": "Punkte/Leben/Gesundheit",
        "Instance": "Instanz",
        "Room": "Raum",
        "Values": "Werte",
        "Sound": "Klang",
        "Output": "Ausgabe",
        "Particles": "Partikel",
    },
    "es": {
        "Events": "Eventos",
        "Movement": "Movimiento",
        "Timing": "Temporizador",
        "Drawing": "Dibujo",
        "Score/Lives/Health": "Puntuación/Vidas/Salud",
        "Instance": "Instancia",
        "Room": "Sala",
        "Values": "Valores",
        "Sound": "Sonido",
        "Output": "Salida",
        "Particles": "Partículas",
    },
    "fr": {
        "Events": "Événements",
        "Movement": "Mouvement",
        "Timing": "Minuterie",
        "Drawing": "Dessin",
        "Score/Lives/Health": "Score/Vies/Santé",
        "Instance": "Instance",
        "Room": "Salle",
        "Values": "Valeurs",
        "Sound": "Son",
        "Output": "Sortie",
        "Particles": "Particules",
    },
    "it": {
        "Events": "Eventi",
        "Movement": "Movimento",
        "Timing": "Temporizzazione",
        "Drawing": "Disegno",
        "Score/Lives/Health": "Punteggio/Vite/Salute",
        "Instance": "Istanza",
        "Room": "Stanza",
        "Values": "Valori",
        "Sound": "Suono",
        "Output": "Output",
        "Particles": "Particelle",
    },
    "ru": {
        "Events": "События",
        "Movement": "Движение",
        "Timing": "Таймер",
        "Drawing": "Рисование",
        "Score/Lives/Health": "Очки/Жизни/Здоровье",
        "Instance": "Экземпляр",
        "Room": "Комната",
        "Values": "Значения",
        "Sound": "Звук",
        "Output": "Вывод",
        "Particles": "Частицы",
    },
    "sl": {
        "Events": "Dogodki",
        "Movement": "Gibanje",
        "Timing": "Časovnik",
        "Drawing": "Risanje",
        "Score/Lives/Health": "Točke/Življenja/Zdravje",
        "Instance": "Primerek",
        "Room": "Soba",
        "Values": "Vrednosti",
        "Sound": "Zvok",
        "Output": "Izhod",
        "Particles": "Delci",
    },
    "uk": {
        "Events": "Події",
        "Movement": "Рух",
        "Timing": "Таймер",
        "Drawing": "Малювання",
        "Score/Lives/Health": "Очки/Життя/Здоров'я",
        "Instance": "Екземпляр",
        "Room": "Кімната",
        "Values": "Значення",
        "Sound": "Звук",
        "Output": "Вивід",
        "Particles": "Частинки",
    },
}

# Block name and description translations
# Format: "block_type": {"name": {...}, "description": {...}}
BLOCK_TRANSLATIONS = {
    # Events
    "event_create": {
        "name": {"de": "Erstellen-Ereignis", "es": "Evento de creación", "fr": "Événement de création", "it": "Evento di creazione", "ru": "Событие создания", "sl": "Dogodek ustvarjanja", "uk": "Подія створення"},
        "description": {"de": "Wenn Objekt erstellt wird", "es": "Cuando se crea el objeto", "fr": "Quand l'objet est créé", "it": "Quando l'oggetto viene creato", "ru": "Когда объект создан", "sl": "Ko je objekt ustvarjen", "uk": "Коли об'єкт створено"}
    },
    "event_step": {
        "name": {"de": "Schritt-Ereignis", "es": "Evento de paso", "fr": "Événement étape", "it": "Evento passo", "ru": "Событие шага", "sl": "Dogodek koraka", "uk": "Подія кроку"},
        "description": {"de": "Jeden Frame", "es": "Cada fotograma", "fr": "Chaque image", "it": "Ogni frame", "ru": "Каждый кадр", "sl": "Vsak okvir", "uk": "Кожен кадр"}
    },
    "event_draw": {
        "name": {"de": "Zeichnen-Ereignis", "es": "Evento de dibujo", "fr": "Événement de dessin", "it": "Evento di disegno", "ru": "Событие рисования", "sl": "Dogodek risanja", "uk": "Подія малювання"},
        "description": {"de": "Während der Zeichenphase", "es": "Durante la fase de dibujo", "fr": "Pendant la phase de dessin", "it": "Durante la fase di disegno", "ru": "Во время фазы рисования", "sl": "Med fazo risanja", "uk": "Під час фази малювання"}
    },
    "event_destroy": {
        "name": {"de": "Zerstören-Ereignis", "es": "Evento de destrucción", "fr": "Événement de destruction", "it": "Evento di distruzione", "ru": "Событие уничтожения", "sl": "Dogodek uničenja", "uk": "Подія знищення"},
        "description": {"de": "Wenn Objekt zerstört wird", "es": "Cuando se destruye el objeto", "fr": "Quand l'objet est détruit", "it": "Quando l'oggetto viene distrutto", "ru": "Когда объект уничтожен", "sl": "Ko je objekt uničen", "uk": "Коли об'єкт знищено"}
    },
    "event_keyboard_nokey": {
        "name": {"de": "Keine Taste", "es": "Sin tecla", "fr": "Aucune touche", "it": "Nessun tasto", "ru": "Нет клавиши", "sl": "Brez tipke", "uk": "Без клавіші"},
        "description": {"de": "Keine Taste gedrückt", "es": "Ninguna tecla presionada", "fr": "Aucune touche pressée", "it": "Nessun tasto premuto", "ru": "Клавиша не нажата", "sl": "Tipka ni pritisnjena", "uk": "Клавішу не натиснуто"}
    },
    "event_keyboard_anykey": {
        "name": {"de": "Beliebige Taste", "es": "Cualquier tecla", "fr": "N'importe quelle touche", "it": "Qualsiasi tasto", "ru": "Любая клавиша", "sl": "Katerakoli tipka", "uk": "Будь-яка клавіша"},
        "description": {"de": "Beliebige Taste gedrückt", "es": "Cualquier tecla presionada", "fr": "N'importe quelle touche pressée", "it": "Qualsiasi tasto premuto", "ru": "Любая клавиша нажата", "sl": "Katerakoli tipka pritisnjena", "uk": "Будь-яку клавішу натиснуто"}
    },
    "event_keyboard_held": {
        "name": {"de": "Tastatur (gehalten)", "es": "Teclado (mantenido)", "fr": "Clavier (maintenu)", "it": "Tastiera (tenuto)", "ru": "Клавиатура (удержание)", "sl": "Tipkovnica (držanje)", "uk": "Клавіатура (утримання)"},
        "description": {"de": "Taste gedrückt halten", "es": "Tecla mantenida", "fr": "Touche maintenue", "it": "Tasto tenuto premuto", "ru": "Клавиша удерживается", "sl": "Tipka držana", "uk": "Клавіша утримується"}
    },
    "event_keyboard_press": {
        "name": {"de": "Taste drücken", "es": "Tecla presionada", "fr": "Touche pressée", "it": "Tasto premuto", "ru": "Нажатие клавиши", "sl": "Pritisk tipke", "uk": "Натискання клавіші"},
        "description": {"de": "Taste einmal gedrückt", "es": "Tecla presionada una vez", "fr": "Touche pressée une fois", "it": "Tasto premuto una volta", "ru": "Клавиша нажата один раз", "sl": "Tipka pritisnjena enkrat", "uk": "Клавішу натиснуто один раз"}
    },
    "event_keyboard_release": {
        "name": {"de": "Taste loslassen", "es": "Tecla liberada", "fr": "Touche relâchée", "it": "Tasto rilasciato", "ru": "Отпускание клавиши", "sl": "Spust tipke", "uk": "Відпускання клавіші"},
        "description": {"de": "Taste losgelassen", "es": "Tecla liberada", "fr": "Touche relâchée", "it": "Tasto rilasciato", "ru": "Клавиша отпущена", "sl": "Tipka spuščena", "uk": "Клавішу відпущено"}
    },
    "event_mouse": {
        "name": {"de": "Mausereignisse", "es": "Eventos de ratón", "fr": "Événements souris", "it": "Eventi mouse", "ru": "События мыши", "sl": "Dogodki miške", "uk": "Події миші"},
        "description": {"de": "Mausklicks und Bewegung", "es": "Clics y movimiento del ratón", "fr": "Clics et mouvement de la souris", "it": "Clic e movimento del mouse", "ru": "Клики и движение мыши", "sl": "Kliki in premiki miške", "uk": "Кліки та рух миші"}
    },
    "event_collision": {
        "name": {"de": "Kollision", "es": "Colisión", "fr": "Collision", "it": "Collisione", "ru": "Столкновение", "sl": "Trk", "uk": "Зіткнення"},
        "description": {"de": "Kollision mit Objekt", "es": "Colisión con objeto", "fr": "Collision avec un objet", "it": "Collisione con oggetto", "ru": "Столкновение с объектом", "sl": "Trk z objektom", "uk": "Зіткнення з об'єктом"}
    },
    "event_alarm": {
        "name": {"de": "Alarm-Ereignisse", "es": "Eventos de alarma", "fr": "Événements alarme", "it": "Eventi allarme", "ru": "События будильника", "sl": "Dogodki alarma", "uk": "Події будильника"},
        "description": {"de": "Alarm-Auslöser (0-11)", "es": "Disparador de alarma (0-11)", "fr": "Déclencheur d'alarme (0-11)", "it": "Trigger allarme (0-11)", "ru": "Срабатывание будильника (0-11)", "sl": "Sprožilec alarma (0-11)", "uk": "Тригер будильника (0-11)"}
    },

    # Movement
    "move_set_hspeed": {
        "name": {"de": "Horizontale Geschwindigkeit setzen", "es": "Establecer velocidad horizontal", "fr": "Définir vitesse horizontale", "it": "Imposta velocità orizzontale", "ru": "Задать горизонтальную скорость", "sl": "Nastavi vodoravno hitrost", "uk": "Встановити горизонтальну швидкість"},
        "description": {"de": "X-Geschwindigkeit setzen", "es": "Establecer velocidad X", "fr": "Définir la vélocité X", "it": "Imposta velocità X", "ru": "Задать скорость по X", "sl": "Nastavi hitrost X", "uk": "Встановити швидкість X"}
    },
    "move_set_vspeed": {
        "name": {"de": "Vertikale Geschwindigkeit setzen", "es": "Establecer velocidad vertical", "fr": "Définir vitesse verticale", "it": "Imposta velocità verticale", "ru": "Задать вертикальную скорость", "sl": "Nastavi navpično hitrost", "uk": "Встановити вертикальну швидкість"},
        "description": {"de": "Y-Geschwindigkeit setzen", "es": "Establecer velocidad Y", "fr": "Définir la vélocité Y", "it": "Imposta velocità Y", "ru": "Задать скорость по Y", "sl": "Nastavi hitrost Y", "uk": "Встановити швидкість Y"}
    },
    "move_stop": {
        "name": {"de": "Bewegung stoppen", "es": "Detener movimiento", "fr": "Arrêter le mouvement", "it": "Ferma movimento", "ru": "Остановить движение", "sl": "Ustavi gibanje", "uk": "Зупинити рух"},
        "description": {"de": "Alle Bewegung stoppen", "es": "Detener todo movimiento", "fr": "Arrêter tout mouvement", "it": "Ferma tutti i movimenti", "ru": "Остановить всё движение", "sl": "Ustavi vse gibanje", "uk": "Зупинити весь рух"}
    },
    "move_direction": {
        "name": {"de": "Richtung bewegen", "es": "Mover en dirección", "fr": "Déplacer direction", "it": "Muovi direzione", "ru": "Двигаться в направлении", "sl": "Premakni v smeri", "uk": "Рухатися в напрямку"},
        "description": {"de": "In 4 Richtungen bewegen", "es": "Mover en 4 direcciones", "fr": "Déplacer en 4 directions", "it": "Muovi in 4 direzioni", "ru": "Двигаться в 4 направлениях", "sl": "Premakni v 4 smereh", "uk": "Рухатися в 4 напрямках"}
    },
    "move_towards": {
        "name": {"de": "Bewegen zu", "es": "Mover hacia", "fr": "Déplacer vers", "it": "Muovi verso", "ru": "Двигаться к", "sl": "Premakni proti", "uk": "Рухатися до"},
        "description": {"de": "Zu einem Punkt bewegen", "es": "Mover hacia un punto", "fr": "Déplacer vers un point", "it": "Muovi verso un punto", "ru": "Двигаться к точке", "sl": "Premakni do točke", "uk": "Рухатися до точки"}
    },
    "move_snap_to_grid": {
        "name": {"de": "An Raster ausrichten", "es": "Ajustar a cuadrícula", "fr": "Aligner à la grille", "it": "Allinea alla griglia", "ru": "Выровнять по сетке", "sl": "Poravnaj na mrežo", "uk": "Вирівняти по сітці"},
        "description": {"de": "An Raster ausrichten", "es": "Alinear a cuadrícula", "fr": "Aligner à la grille", "it": "Allinea alla griglia", "ru": "Выровнять по сетке", "sl": "Poravnaj na mrežo", "uk": "Вирівняти по сітці"}
    },
    "move_jump_to": {
        "name": {"de": "Zu Position springen", "es": "Saltar a posición", "fr": "Sauter à la position", "it": "Salta alla posizione", "ru": "Прыгнуть к позиции", "sl": "Skoči na položaj", "uk": "Стрибнути до позиції"},
        "description": {"de": "Sofortiger Teleport", "es": "Teletransporte instantáneo", "fr": "Téléportation instantanée", "it": "Teletrasporto istantaneo", "ru": "Мгновенная телепортация", "sl": "Takojšnja teleportacija", "uk": "Миттєва телепортація"}
    },
    "grid_stop_if_no_keys": {
        "name": {"de": "Stoppen wenn keine Taste", "es": "Detener si no hay teclas", "fr": "Arrêter si aucune touche", "it": "Ferma se nessun tasto", "ru": "Остановить если нет клавиш", "sl": "Ustavi če ni tipk", "uk": "Зупинити якщо немає клавіш"},
        "description": {"de": "Raster-Bewegungshilfe", "es": "Ayuda de movimiento en cuadrícula", "fr": "Aide pour mouvement grille", "it": "Aiuto movimento griglia", "ru": "Помощь движения по сетке", "sl": "Pomoč pri gibanju po mreži", "uk": "Допомога руху по сітці"}
    },
    "grid_check_keys_and_move": {
        "name": {"de": "Tasten prüfen und bewegen", "es": "Verificar teclas y mover", "fr": "Vérifier touches et déplacer", "it": "Controlla tasti e muovi", "ru": "Проверить клавиши и двигаться", "sl": "Preveri tipke in premakni", "uk": "Перевірити клавіші та рухатися"},
        "description": {"de": "Raster-Bewegungshilfe", "es": "Ayuda de movimiento en cuadrícula", "fr": "Aide pour mouvement grille", "it": "Aiuto movimento griglia", "ru": "Помощь движения по сетке", "sl": "Pomoč pri gibanju po mreži", "uk": "Допомога руху по сітці"}
    },
    "grid_if_on_grid": {
        "name": {"de": "Wenn auf Raster", "es": "Si en cuadrícula", "fr": "Si sur la grille", "it": "Se sulla griglia", "ru": "Если на сетке", "sl": "Če na mreži", "uk": "Якщо на сітці"},
        "description": {"de": "Rasterausrichtungsprüfung", "es": "Verificación de alineación", "fr": "Vérification alignement grille", "it": "Controllo allineamento griglia", "ru": "Проверка выравнивания", "sl": "Preverjanje poravnave", "uk": "Перевірка вирівнювання"}
    },
    "set_gravity": {
        "name": {"de": "Schwerkraft setzen", "es": "Establecer gravedad", "fr": "Définir gravité", "it": "Imposta gravità", "ru": "Задать гравитацию", "sl": "Nastavi gravitacijo", "uk": "Встановити гравітацію"},
        "description": {"de": "Schwerkraft anwenden", "es": "Aplicar fuerza de gravedad", "fr": "Appliquer force de gravité", "it": "Applica forza di gravità", "ru": "Применить силу гравитации", "sl": "Uporabi gravitacijsko silo", "uk": "Застосувати силу гравітації"}
    },
    "set_friction": {
        "name": {"de": "Reibung setzen", "es": "Establecer fricción", "fr": "Définir friction", "it": "Imposta attrito", "ru": "Задать трение", "sl": "Nastavi trenje", "uk": "Встановити тертя"},
        "description": {"de": "Reibung anwenden", "es": "Aplicar fricción", "fr": "Appliquer friction", "it": "Applica attrito", "ru": "Применить трение", "sl": "Uporabi trenje", "uk": "Застосувати тертя"}
    },
    "reverse_horizontal": {
        "name": {"de": "Horizontal umkehren", "es": "Invertir horizontal", "fr": "Inverser horizontal", "it": "Inverti orizzontale", "ru": "Обратить горизонтально", "sl": "Obrni vodoravno", "uk": "Обернути горизонтально"},
        "description": {"de": "X-Richtung umkehren", "es": "Invertir dirección X", "fr": "Inverser direction X", "it": "Inverti direzione X", "ru": "Обратить направление X", "sl": "Obrni smer X", "uk": "Обернути напрямок X"}
    },
    "reverse_vertical": {
        "name": {"de": "Vertikal umkehren", "es": "Invertir vertical", "fr": "Inverser vertical", "it": "Inverti verticale", "ru": "Обратить вертикально", "sl": "Obrni navpično", "uk": "Обернути вертикально"},
        "description": {"de": "Y-Richtung umkehren", "es": "Invertir dirección Y", "fr": "Inverser direction Y", "it": "Inverti direzione Y", "ru": "Обратить направление Y", "sl": "Obrni smer Y", "uk": "Обернути напрямок Y"}
    },

    # Timing
    "set_alarm": {
        "name": {"de": "Alarm setzen", "es": "Establecer alarma", "fr": "Définir alarme", "it": "Imposta allarme", "ru": "Установить будильник", "sl": "Nastavi alarm", "uk": "Встановити будильник"},
        "description": {"de": "Timer setzen (0-11)", "es": "Establecer temporizador (0-11)", "fr": "Définir minuteur (0-11)", "it": "Imposta timer (0-11)", "ru": "Установить таймер (0-11)", "sl": "Nastavi časovnik (0-11)", "uk": "Встановити таймер (0-11)"}
    },

    # Drawing
    "draw_text": {
        "name": {"de": "Text zeichnen", "es": "Dibujar texto", "fr": "Dessiner texte", "it": "Disegna testo", "ru": "Нарисовать текст", "sl": "Nariši besedilo", "uk": "Намалювати текст"},
        "description": {"de": "Text anzeigen", "es": "Mostrar texto", "fr": "Afficher du texte", "it": "Visualizza testo", "ru": "Показать текст", "sl": "Prikaži besedilo", "uk": "Показати текст"}
    },
    "draw_rectangle": {
        "name": {"de": "Rechteck zeichnen", "es": "Dibujar rectángulo", "fr": "Dessiner rectangle", "it": "Disegna rettangolo", "ru": "Нарисовать прямоугольник", "sl": "Nariši pravokotnik", "uk": "Намалювати прямокутник"},
        "description": {"de": "Gefülltes Rechteck zeichnen", "es": "Dibujar rectángulo relleno", "fr": "Dessiner rectangle plein", "it": "Disegna rettangolo pieno", "ru": "Нарисовать заполненный прямоугольник", "sl": "Nariši poln pravokotnik", "uk": "Намалювати заповнений прямокутник"}
    },
    "draw_circle": {
        "name": {"de": "Kreis zeichnen", "es": "Dibujar círculo", "fr": "Dessiner cercle", "it": "Disegna cerchio", "ru": "Нарисовать круг", "sl": "Nariši krog", "uk": "Намалювати коло"},
        "description": {"de": "Gefüllten Kreis zeichnen", "es": "Dibujar círculo relleno", "fr": "Dessiner cercle plein", "it": "Disegna cerchio pieno", "ru": "Нарисовать заполненный круг", "sl": "Nariši poln krog", "uk": "Намалювати заповнене коло"}
    },
    "set_sprite": {
        "name": {"de": "Sprite setzen", "es": "Establecer sprite", "fr": "Définir sprite", "it": "Imposta sprite", "ru": "Установить спрайт", "sl": "Nastavi sprite", "uk": "Встановити спрайт"},
        "description": {"de": "Sprite-Bild ändern", "es": "Cambiar imagen del sprite", "fr": "Changer l'image du sprite", "it": "Cambia immagine sprite", "ru": "Изменить изображение спрайта", "sl": "Spremeni sliko sprajtа", "uk": "Змінити зображення спрайту"}
    },
    "set_alpha": {
        "name": {"de": "Transparenz setzen", "es": "Establecer transparencia", "fr": "Définir transparence", "it": "Imposta trasparenza", "ru": "Установить прозрачность", "sl": "Nastavi prosojnost", "uk": "Встановити прозорість"},
        "description": {"de": "Alpha setzen (0-1)", "es": "Establecer alfa (0-1)", "fr": "Définir alpha (0-1)", "it": "Imposta alpha (0-1)", "ru": "Установить альфа (0-1)", "sl": "Nastavi alfo (0-1)", "uk": "Встановити альфа (0-1)"}
    },

    # Score/Lives/Health
    "score_set": {
        "name": {"de": "Punkte setzen", "es": "Establecer puntuación", "fr": "Définir score", "it": "Imposta punteggio", "ru": "Установить очки", "sl": "Nastavi točke", "uk": "Встановити очки"},
        "description": {"de": "Punktewert setzen", "es": "Establecer valor de puntuación", "fr": "Définir valeur du score", "it": "Imposta valore punteggio", "ru": "Установить значение очков", "sl": "Nastavi vrednost točk", "uk": "Встановити значення очок"}
    },
    "score_add": {
        "name": {"de": "Punkte hinzufügen", "es": "Añadir puntuación", "fr": "Ajouter au score", "it": "Aggiungi al punteggio", "ru": "Добавить очки", "sl": "Dodaj točke", "uk": "Додати очки"},
        "description": {"de": "Punkte ändern", "es": "Modificar puntuación", "fr": "Modifier le score", "it": "Modifica punteggio", "ru": "Изменить очки", "sl": "Spremeni točke", "uk": "Змінити очки"}
    },
    "lives_set": {
        "name": {"de": "Leben setzen", "es": "Establecer vidas", "fr": "Définir vies", "it": "Imposta vite", "ru": "Установить жизни", "sl": "Nastavi življenja", "uk": "Встановити життя"},
        "description": {"de": "Lebenanzahl setzen", "es": "Establecer número de vidas", "fr": "Définir nombre de vies", "it": "Imposta numero di vite", "ru": "Установить количество жизней", "sl": "Nastavi število življenj", "uk": "Встановити кількість життів"}
    },
    "lives_add": {
        "name": {"de": "Leben hinzufügen", "es": "Añadir vidas", "fr": "Ajouter aux vies", "it": "Aggiungi alle vite", "ru": "Добавить жизни", "sl": "Dodaj življenja", "uk": "Додати життя"},
        "description": {"de": "Leben ändern", "es": "Modificar vidas", "fr": "Modifier les vies", "it": "Modifica vite", "ru": "Изменить жизни", "sl": "Spremeni življenja", "uk": "Змінити життя"}
    },
    "health_set": {
        "name": {"de": "Gesundheit setzen", "es": "Establecer salud", "fr": "Définir santé", "it": "Imposta salute", "ru": "Установить здоровье", "sl": "Nastavi zdravje", "uk": "Встановити здоров'я"},
        "description": {"de": "Gesundheitswert setzen", "es": "Establecer valor de salud", "fr": "Définir valeur de santé", "it": "Imposta valore salute", "ru": "Установить значение здоровья", "sl": "Nastavi vrednost zdravja", "uk": "Встановити значення здоров'я"}
    },
    "health_add": {
        "name": {"de": "Gesundheit hinzufügen", "es": "Añadir salud", "fr": "Ajouter à la santé", "it": "Aggiungi alla salute", "ru": "Добавить здоровье", "sl": "Dodaj zdravje", "uk": "Додати здоров'я"},
        "description": {"de": "Gesundheit ändern", "es": "Modificar salud", "fr": "Modifier la santé", "it": "Modifica salute", "ru": "Изменить здоровье", "sl": "Spremeni zdravje", "uk": "Змінити здоров'я"}
    },
    "draw_score": {
        "name": {"de": "Punkte anzeigen", "es": "Mostrar puntuación", "fr": "Afficher score", "it": "Visualizza punteggio", "ru": "Показать очки", "sl": "Prikaži točke", "uk": "Показати очки"},
        "description": {"de": "Punktetext anzeigen", "es": "Mostrar texto de puntuación", "fr": "Afficher texte du score", "it": "Visualizza testo punteggio", "ru": "Показать текст очков", "sl": "Prikaži besedilo točk", "uk": "Показати текст очок"}
    },
    "draw_lives": {
        "name": {"de": "Leben anzeigen", "es": "Mostrar vidas", "fr": "Afficher vies", "it": "Visualizza vite", "ru": "Показать жизни", "sl": "Prikaži življenja", "uk": "Показати життя"},
        "description": {"de": "Leben-Icons anzeigen", "es": "Mostrar iconos de vidas", "fr": "Afficher icônes des vies", "it": "Visualizza icone vite", "ru": "Показать иконки жизней", "sl": "Prikaži ikone življenj", "uk": "Показати іконки життів"}
    },
    "draw_health_bar": {
        "name": {"de": "Gesundheitsleiste anzeigen", "es": "Mostrar barra de salud", "fr": "Afficher barre de santé", "it": "Visualizza barra salute", "ru": "Показать полосу здоровья", "sl": "Prikaži vrstico zdravja", "uk": "Показати смужку здоров'я"},
        "description": {"de": "Gesundheitsleiste anzeigen", "es": "Mostrar barra de salud", "fr": "Afficher barre de santé", "it": "Visualizza barra salute", "ru": "Показать полосу здоровья", "sl": "Prikaži vrstico zdravja", "uk": "Показати смужку здоров'я"}
    },

    # Instance
    "instance_destroy": {
        "name": {"de": "Instanz zerstören", "es": "Destruir instancia", "fr": "Détruire instance", "it": "Distruggi istanza", "ru": "Уничтожить экземпляр", "sl": "Uniči primerek", "uk": "Знищити екземпляр"},
        "description": {"de": "Dieses Objekt zerstören", "es": "Destruir este objeto", "fr": "Détruire cet objet", "it": "Distruggi questo oggetto", "ru": "Уничтожить этот объект", "sl": "Uniči ta objekt", "uk": "Знищити цей об'єкт"}
    },
    "instance_destroy_other": {
        "name": {"de": "Anderes zerstören", "es": "Destruir otro", "fr": "Détruire autre", "it": "Distruggi altro", "ru": "Уничтожить другой", "sl": "Uniči drugo", "uk": "Знищити інший"},
        "description": {"de": "Kollidierendes Objekt zerstören", "es": "Destruir objeto en colisión", "fr": "Détruire objet en collision", "it": "Distruggi oggetto in collisione", "ru": "Уничтожить столкнувшийся объект", "sl": "Uniči trčen objekt", "uk": "Знищити об'єкт зіткнення"}
    },
    "instance_create": {
        "name": {"de": "Instanz erstellen", "es": "Crear instancia", "fr": "Créer instance", "it": "Crea istanza", "ru": "Создать экземпляр", "sl": "Ustvari primerek", "uk": "Створити екземпляр"},
        "description": {"de": "Neues Objekt erstellen", "es": "Crear nuevo objeto", "fr": "Créer nouvel objet", "it": "Crea nuovo oggetto", "ru": "Создать новый объект", "sl": "Ustvari nov objekt", "uk": "Створити новий об'єкт"}
    },

    # Room
    "room_goto_next": {
        "name": {"de": "Nächster Raum", "es": "Siguiente sala", "fr": "Salle suivante", "it": "Stanza successiva", "ru": "Следующая комната", "sl": "Naslednja soba", "uk": "Наступна кімната"},
        "description": {"de": "Zum nächsten Raum gehen", "es": "Ir a la siguiente sala", "fr": "Aller à la salle suivante", "it": "Vai alla stanza successiva", "ru": "Перейти в следующую комнату", "sl": "Pojdi v naslednjo sobo", "uk": "Перейти до наступної кімнати"}
    },
    "room_restart": {
        "name": {"de": "Raum neustarten", "es": "Reiniciar sala", "fr": "Redémarrer salle", "it": "Riavvia stanza", "ru": "Перезапустить комнату", "sl": "Ponovno zaženi sobo", "uk": "Перезапустити кімнату"},
        "description": {"de": "Aktuellen Raum neustarten", "es": "Reiniciar sala actual", "fr": "Redémarrer la salle actuelle", "it": "Riavvia stanza corrente", "ru": "Перезапустить текущую комнату", "sl": "Ponovno zaženi trenutno sobo", "uk": "Перезапустити поточну кімнату"}
    },
    "room_goto": {
        "name": {"de": "Zu Raum gehen", "es": "Ir a sala", "fr": "Aller à la salle", "it": "Vai alla stanza", "ru": "Перейти в комнату", "sl": "Pojdi v sobo", "uk": "Перейти до кімнати"},
        "description": {"de": "Zu bestimmtem Raum gehen", "es": "Ir a una sala específica", "fr": "Aller à une salle spécifique", "it": "Vai a una stanza specifica", "ru": "Перейти в определённую комнату", "sl": "Pojdi v določeno sobo", "uk": "Перейти до певної кімнати"}
    },

    # Values
    "value_x": {
        "name": {"de": "X-Position", "es": "Posición X", "fr": "Position X", "it": "Posizione X", "ru": "Позиция X", "sl": "Položaj X", "uk": "Позиція X"},
        "description": {"de": "X-Koordinate abrufen", "es": "Obtener coordenada X", "fr": "Obtenir coordonnée X", "it": "Ottieni coordinata X", "ru": "Получить координату X", "sl": "Pridobi koordinato X", "uk": "Отримати координату X"}
    },
    "value_y": {
        "name": {"de": "Y-Position", "es": "Posición Y", "fr": "Position Y", "it": "Posizione Y", "ru": "Позиция Y", "sl": "Položaj Y", "uk": "Позиція Y"},
        "description": {"de": "Y-Koordinate abrufen", "es": "Obtener coordenada Y", "fr": "Obtenir coordonnée Y", "it": "Ottieni coordinata Y", "ru": "Получить координату Y", "sl": "Pridobi koordinato Y", "uk": "Отримати координату Y"}
    },
    "value_hspeed": {
        "name": {"de": "Horizontale Geschwindigkeit", "es": "Velocidad horizontal", "fr": "Vitesse horizontale", "it": "Velocità orizzontale", "ru": "Горизонтальная скорость", "sl": "Vodoravna hitrost", "uk": "Горизонтальна швидкість"},
        "description": {"de": "X-Geschwindigkeit abrufen", "es": "Obtener velocidad X", "fr": "Obtenir vélocité X", "it": "Ottieni velocità X", "ru": "Получить скорость X", "sl": "Pridobi hitrost X", "uk": "Отримати швидкість X"}
    },
    "value_vspeed": {
        "name": {"de": "Vertikale Geschwindigkeit", "es": "Velocidad vertical", "fr": "Vitesse verticale", "it": "Velocità verticale", "ru": "Вертикальная скорость", "sl": "Navpična hitrost", "uk": "Вертикальна швидкість"},
        "description": {"de": "Y-Geschwindigkeit abrufen", "es": "Obtener velocidad Y", "fr": "Obtenir vélocité Y", "it": "Ottieni velocità Y", "ru": "Получить скорость Y", "sl": "Pridobi hitrost Y", "uk": "Отримати швидкість Y"}
    },
    "value_score": {
        "name": {"de": "Punkte", "es": "Puntuación", "fr": "Score", "it": "Punteggio", "ru": "Очки", "sl": "Točke", "uk": "Очки"},
        "description": {"de": "Punktewert abrufen", "es": "Obtener valor de puntuación", "fr": "Obtenir valeur du score", "it": "Ottieni valore punteggio", "ru": "Получить значение очков", "sl": "Pridobi vrednost točk", "uk": "Отримати значення очок"}
    },
    "value_lives": {
        "name": {"de": "Leben", "es": "Vidas", "fr": "Vies", "it": "Vite", "ru": "Жизни", "sl": "Življenja", "uk": "Життя"},
        "description": {"de": "Lebenanzahl abrufen", "es": "Obtener número de vidas", "fr": "Obtenir nombre de vies", "it": "Ottieni numero di vite", "ru": "Получить количество жизней", "sl": "Pridobi število življenj", "uk": "Отримати кількість життів"}
    },
    "value_health": {
        "name": {"de": "Gesundheit", "es": "Salud", "fr": "Santé", "it": "Salute", "ru": "Здоровье", "sl": "Zdravje", "uk": "Здоров'я"},
        "description": {"de": "Gesundheitswert abrufen", "es": "Obtener valor de salud", "fr": "Obtenir valeur de santé", "it": "Ottieni valore salute", "ru": "Получить значение здоровья", "sl": "Pridobi vrednost zdravja", "uk": "Отримати значення здоров'я"}
    },
    "value_mouse_x": {
        "name": {"de": "Maus X", "es": "Ratón X", "fr": "Souris X", "it": "Mouse X", "ru": "Мышь X", "sl": "Miška X", "uk": "Миша X"},
        "description": {"de": "Maus-X abrufen", "es": "Obtener X del ratón", "fr": "Obtenir X de la souris", "it": "Ottieni X del mouse", "ru": "Получить X мыши", "sl": "Pridobi X miške", "uk": "Отримати X миші"}
    },
    "value_mouse_y": {
        "name": {"de": "Maus Y", "es": "Ratón Y", "fr": "Souris Y", "it": "Mouse Y", "ru": "Мышь Y", "sl": "Miška Y", "uk": "Миша Y"},
        "description": {"de": "Maus-Y abrufen", "es": "Obtener Y del ratón", "fr": "Obtenir Y de la souris", "it": "Ottieni Y del mouse", "ru": "Получить Y мыши", "sl": "Pridobi Y miške", "uk": "Отримати Y миші"}
    },

    # Sound
    "sound_play": {
        "name": {"de": "Sound abspielen", "es": "Reproducir sonido", "fr": "Jouer son", "it": "Riproduci suono", "ru": "Воспроизвести звук", "sl": "Predvajaj zvok", "uk": "Відтворити звук"},
        "description": {"de": "Soundeffekt abspielen", "es": "Reproducir efecto de sonido", "fr": "Jouer effet sonore", "it": "Riproduci effetto sonoro", "ru": "Воспроизвести звуковой эффект", "sl": "Predvajaj zvočni učinek", "uk": "Відтворити звуковий ефект"}
    },
    "music_play": {
        "name": {"de": "Musik abspielen", "es": "Reproducir música", "fr": "Jouer musique", "it": "Riproduci musica", "ru": "Воспроизвести музыку", "sl": "Predvajaj glasbo", "uk": "Відтворити музику"},
        "description": {"de": "Hintergrundmusik abspielen", "es": "Reproducir música de fondo", "fr": "Jouer musique de fond", "it": "Riproduci musica di sottofondo", "ru": "Воспроизвести фоновую музыку", "sl": "Predvajaj glasbo v ozadju", "uk": "Відтворити фонову музику"}
    },
    "music_stop": {
        "name": {"de": "Musik stoppen", "es": "Detener música", "fr": "Arrêter musique", "it": "Ferma musica", "ru": "Остановить музыку", "sl": "Ustavi glasbo", "uk": "Зупинити музику"},
        "description": {"de": "Musik stoppen", "es": "Detener la música", "fr": "Arrêter la musique", "it": "Ferma musica", "ru": "Остановить музыку", "sl": "Ustavi glasbo", "uk": "Зупинити музику"}
    },

    # Output
    "output_message": {
        "name": {"de": "Nachricht anzeigen", "es": "Mostrar mensaje", "fr": "Afficher message", "it": "Mostra messaggio", "ru": "Показать сообщение", "sl": "Prikaži sporočilo", "uk": "Показати повідомлення"},
        "description": {"de": "Nachrichtendialog anzeigen", "es": "Mostrar diálogo de mensaje", "fr": "Afficher dialogue de message", "it": "Visualizza dialogo messaggio", "ru": "Показать диалог сообщения", "sl": "Prikaži pogovorno okno", "uk": "Показати діалог повідомлення"}
    },

    # Extra Tab - Variables
    "draw_variable": {
        "name": {"de": "Variable anzeigen", "es": "Dibujar variable", "fr": "Afficher variable", "it": "Visualizza variabile", "ru": "Показать переменную", "sl": "Nariši spremenljivko", "uk": "Показати змінну"},
        "description": {"de": "Variable auf Bildschirm anzeigen", "es": "Dibujar valor de variable", "fr": "Afficher valeur de variable", "it": "Visualizza valore variabile", "ru": "Показать значение переменной", "sl": "Nariši vrednost spremenljivke", "uk": "Показати значення змінної"}
    },
    "goto_room": {
        "name": {"de": "Zu Raum wechseln", "es": "Ir a sala", "fr": "Aller à la salle", "it": "Vai alla stanza", "ru": "Перейти в комнату", "sl": "Pojdi v sobo", "uk": "Перейти до кімнати"},
        "description": {"de": "Zu bestimmtem Raum wechseln", "es": "Ir a una sala específica", "fr": "Aller à une salle spécifique", "it": "Vai a una stanza specifica", "ru": "Перейти в указанную комнату", "sl": "Pojdi v določeno sobo", "uk": "Перейти до певної кімнати"}
    },
    "check_room": {
        "name": {"de": "Raum prüfen", "es": "Comprobar sala", "fr": "Vérifier salle", "it": "Controlla stanza", "ru": "Проверить комнату", "sl": "Preveri sobo", "uk": "Перевірити кімнату"},
        "description": {"de": "Prüfen ob in bestimmtem Raum", "es": "Comprobar si en sala específica", "fr": "Vérifier si dans la salle", "it": "Controlla se in stanza specifica", "ru": "Проверить нахождение в комнате", "sl": "Preveri če v določeni sobi", "uk": "Перевірити чи в певній кімнаті"}
    },
    "if_next_room_exists": {
        "name": {"de": "Wenn nächster Raum existiert", "es": "Si existe sala siguiente", "fr": "Si salle suivante existe", "it": "Se stanza successiva esiste", "ru": "Если есть следующая комната", "sl": "Če naslednja soba obstaja", "uk": "Якщо наступна кімната існує"},
        "description": {"de": "Prüfen ob nächster Raum existiert", "es": "Comprobar si hay sala siguiente", "fr": "Vérifier si salle suivante existe", "it": "Controlla se esiste stanza successiva", "ru": "Проверить существование следующей комнаты", "sl": "Preveri če obstaja naslednja soba", "uk": "Перевірити чи існує наступна кімната"}
    },
    "if_previous_room_exists": {
        "name": {"de": "Wenn vorheriger Raum existiert", "es": "Si existe sala anterior", "fr": "Si salle précédente existe", "it": "Se stanza precedente esiste", "ru": "Если есть предыдущая комната", "sl": "Če prejšnja soba obstaja", "uk": "Якщо попередня кімната існує"},
        "description": {"de": "Prüfen ob vorheriger Raum existiert", "es": "Comprobar si hay sala anterior", "fr": "Vérifier si salle précédente existe", "it": "Controlla se esiste stanza precedente", "ru": "Проверить существование предыдущей комнаты", "sl": "Preveri če obstaja prejšnja soba", "uk": "Перевірити чи існує попередня кімната"}
    },

    # Particles Tab
    "create_particle_system": {
        "name": {"de": "Partikelsystem erstellen", "es": "Crear sistema de partículas", "fr": "Créer système de particules", "it": "Crea sistema particelle", "ru": "Создать систему частиц", "sl": "Ustvari sistem delcev", "uk": "Створити систему частинок"},
        "description": {"de": "Neues Partikelsystem erstellen", "es": "Crear nuevo sistema de partículas", "fr": "Créer nouveau système de particules", "it": "Crea nuovo sistema di particelle", "ru": "Создать новую систему частиц", "sl": "Ustvari nov sistem delcev", "uk": "Створити нову систему частинок"}
    },
    "destroy_particle_system": {
        "name": {"de": "Partikelsystem zerstören", "es": "Destruir sistema de partículas", "fr": "Détruire système de particules", "it": "Distruggi sistema particelle", "ru": "Уничтожить систему частиц", "sl": "Uniči sistem delcev", "uk": "Знищити систему частинок"},
        "description": {"de": "Partikelsystem entfernen", "es": "Eliminar sistema de partículas", "fr": "Supprimer système de particules", "it": "Rimuovi sistema particelle", "ru": "Удалить систему частиц", "sl": "Odstrani sistem delcev", "uk": "Видалити систему частинок"}
    },
    "clear_particles": {
        "name": {"de": "Alle Partikel löschen", "es": "Borrar todas las partículas", "fr": "Effacer toutes les particules", "it": "Cancella tutte le particelle", "ru": "Очистить все частицы", "sl": "Počisti vse delce", "uk": "Очистити всі частинки"},
        "description": {"de": "Alle aktiven Partikel entfernen", "es": "Eliminar todas las partículas activas", "fr": "Supprimer toutes les particules actives", "it": "Rimuovi tutte le particelle attive", "ru": "Удалить все активные частицы", "sl": "Odstrani vse aktivne delce", "uk": "Видалити всі активні частинки"}
    },
    "create_particle_type": {
        "name": {"de": "Partikeltyp erstellen", "es": "Crear tipo de partícula", "fr": "Créer type de particule", "it": "Crea tipo particella", "ru": "Создать тип частицы", "sl": "Ustvari vrsto delca", "uk": "Створити тип частинки"},
        "description": {"de": "Neuen Partikeltyp definieren", "es": "Definir nuevo tipo de partícula", "fr": "Définir nouveau type de particule", "it": "Definisci nuovo tipo di particella", "ru": "Определить новый тип частицы", "sl": "Določi novo vrsto delca", "uk": "Визначити новий тип частинки"}
    },
    "create_emitter": {
        "name": {"de": "Emitter erstellen", "es": "Crear emisor", "fr": "Créer émetteur", "it": "Crea emettitore", "ru": "Создать эмиттер", "sl": "Ustvari oddajnik", "uk": "Створити емітер"},
        "description": {"de": "Partikelemitter erstellen", "es": "Crear emisor de partículas", "fr": "Créer émetteur de particules", "it": "Crea emettitore particelle", "ru": "Создать эмиттер частиц", "sl": "Ustvari oddajnik delcev", "uk": "Створити емітер частинок"}
    },
    "destroy_emitter": {
        "name": {"de": "Emitter zerstören", "es": "Destruir emisor", "fr": "Détruire émetteur", "it": "Distruggi emettitore", "ru": "Уничтожить эмиттер", "sl": "Uniči oddajnik", "uk": "Знищити емітер"},
        "description": {"de": "Partikelemitter entfernen", "es": "Eliminar emisor de partículas", "fr": "Supprimer émetteur de particules", "it": "Rimuovi emettitore particelle", "ru": "Удалить эмиттер частиц", "sl": "Odstrani oddajnik delcev", "uk": "Видалити емітер частинок"}
    },
    "burst_particles": {
        "name": {"de": "Partikelexplosion", "es": "Explosión de partículas", "fr": "Explosion de particules", "it": "Esplosione particelle", "ru": "Взрыв частиц", "sl": "Eksplozija delcev", "uk": "Вибух частинок"},
        "description": {"de": "Einmalige Partikelemission", "es": "Emitir partículas una vez", "fr": "Émettre particules une fois", "it": "Emetti particelle una volta", "ru": "Одноразовый выброс частиц", "sl": "Enkratna emisija delcev", "uk": "Одноразовий викид частинок"}
    },
    "stream_particles": {
        "name": {"de": "Partikelstrom", "es": "Flujo de partículas", "fr": "Flux de particules", "it": "Flusso particelle", "ru": "Поток частиц", "sl": "Tok delcev", "uk": "Потік частинок"},
        "description": {"de": "Kontinuierliche Partikelemission", "es": "Emitir partículas continuamente", "fr": "Émettre particules en continu", "it": "Emetti particelle continuamente", "ru": "Непрерывный поток частиц", "sl": "Neprekinjeno oddajanje delcev", "uk": "Безперервний потік частинок"}
    },

    # Timing Tab - Timelines
    "set_timeline": {
        "name": {"de": "Timeline setzen", "es": "Establecer línea de tiempo", "fr": "Définir timeline", "it": "Imposta timeline", "ru": "Установить таймлайн", "sl": "Nastavi časovnico", "uk": "Встановити таймлайн"},
        "description": {"de": "Timeline für Instanz setzen", "es": "Establecer línea de tiempo de instancia", "fr": "Définir la timeline de l'instance", "it": "Imposta timeline dell'istanza", "ru": "Установить таймлайн экземпляра", "sl": "Nastavi časovnico primerka", "uk": "Встановити таймлайн екземпляра"}
    },
    "set_timeline_position": {
        "name": {"de": "Timeline-Position setzen", "es": "Establecer posición de línea de tiempo", "fr": "Définir position timeline", "it": "Imposta posizione timeline", "ru": "Установить позицию таймлайна", "sl": "Nastavi položaj časovnice", "uk": "Встановити позицію таймлайну"},
        "description": {"de": "Aktuelle Position in Timeline setzen", "es": "Establecer posición actual en línea de tiempo", "fr": "Définir position actuelle dans timeline", "it": "Imposta posizione corrente nella timeline", "ru": "Установить текущую позицию таймлайна", "sl": "Nastavi trenutni položaj v časovnici", "uk": "Встановити поточну позицію таймлайну"}
    },
    "set_timeline_speed": {
        "name": {"de": "Timeline-Geschwindigkeit setzen", "es": "Establecer velocidad de línea de tiempo", "fr": "Définir vitesse timeline", "it": "Imposta velocità timeline", "ru": "Установить скорость таймлайна", "sl": "Nastavi hitrost časovnice", "uk": "Встановити швидкість таймлайну"},
        "description": {"de": "Abspielgeschwindigkeit der Timeline", "es": "Velocidad de reproducción de línea de tiempo", "fr": "Vitesse de lecture de la timeline", "it": "Velocità di riproduzione timeline", "ru": "Скорость воспроизведения таймлайна", "sl": "Hitrost predvajanja časovnice", "uk": "Швидкість відтворення таймлайну"}
    },
    "start_timeline": {
        "name": {"de": "Timeline starten", "es": "Iniciar línea de tiempo", "fr": "Démarrer timeline", "it": "Avvia timeline", "ru": "Запустить таймлайн", "sl": "Zaženi časovnico", "uk": "Запустити таймлайн"},
        "description": {"de": "Timeline-Wiedergabe starten", "es": "Iniciar reproducción de línea de tiempo", "fr": "Démarrer lecture de timeline", "it": "Avvia riproduzione timeline", "ru": "Запустить воспроизведение таймлайна", "sl": "Zaženi predvajanje časovnice", "uk": "Запустити відтворення таймлайну"}
    },
    "pause_timeline": {
        "name": {"de": "Timeline pausieren", "es": "Pausar línea de tiempo", "fr": "Mettre en pause timeline", "it": "Pausa timeline", "ru": "Приостановить таймлайн", "sl": "Zaustavi časovnico", "uk": "Призупинити таймлайн"},
        "description": {"de": "Timeline-Wiedergabe pausieren", "es": "Pausar reproducción de línea de tiempo", "fr": "Mettre en pause lecture de timeline", "it": "Metti in pausa riproduzione timeline", "ru": "Приостановить воспроизведение таймлайна", "sl": "Zaustavi predvajanje časovnice", "uk": "Призупинити відтворення таймлайну"}
    },
    "stop_timeline": {
        "name": {"de": "Timeline stoppen", "es": "Detener línea de tiempo", "fr": "Arrêter timeline", "it": "Ferma timeline", "ru": "Остановить таймлайн", "sl": "Ustavi časovnico", "uk": "Зупинити таймлайн"},
        "description": {"de": "Timeline stoppen und zurücksetzen", "es": "Detener y reiniciar línea de tiempo", "fr": "Arrêter et réinitialiser timeline", "it": "Ferma e reimposta timeline", "ru": "Остановить и сбросить таймлайн", "sl": "Ustavi in ponastavi časovnico", "uk": "Зупинити та скинути таймлайн"}
    },
}


def get_translated_category(category: str, language: str = "en") -> str:
    """Get translated category name"""
    if language == "en" or language not in CATEGORY_TRANSLATIONS:
        return category
    return CATEGORY_TRANSLATIONS[language].get(category, category)


def get_translated_block_name(block_type: str, language: str = "en") -> str:
    """Get translated block name"""
    if language == "en" or block_type not in BLOCK_TRANSLATIONS:
        return None
    return BLOCK_TRANSLATIONS[block_type]["name"].get(language)


def get_translated_block_description(block_type: str, language: str = "en") -> str:
    """Get translated block description"""
    if language == "en" or block_type not in BLOCK_TRANSLATIONS:
        return None
    return BLOCK_TRANSLATIONS[block_type]["description"].get(language)


# Runtime translations for Pygame dialogs (highscore, etc.)
# These are used by game_runner.py since it can't use Qt's translation system
# Languages: de, es, fr, it, ru, sl, uk (active IDE languages)
#            + ja, ko, nl, pl, pt, tr, zh (additional)
RUNTIME_TRANSLATIONS = {
    # Highscore dialog
    "HIGH SCORES": {
        "de": "BESTENLISTE",
        "es": "PUNTUACIONES ALTAS",
        "fr": "MEILLEURS SCORES",
        "it": "PUNTEGGI MIGLIORI",
        "ja": "ハイスコア",
        "ko": "최고 점수",
        "nl": "HOOGSTE SCORES",
        "pl": "NAJLEPSZE WYNIKI",
        "pt": "RECORDES",
        "ru": "РЕКОРДЫ",
        "sl": "NAJBOLJŠI REZULTATI",
        "tr": "EN YÜKSEK SKORLAR",
        "uk": "НАЙКРАЩІ РЕЗУЛЬТАТИ",
        "zh": "最高分",
    },
    "Rank": {
        "de": "Rang",
        "es": "Pos.",
        "fr": "Rang",
        "it": "Pos.",
        "ja": "順位",
        "ko": "순위",
        "nl": "Rang",
        "pl": "Poz.",
        "pt": "Pos.",
        "ru": "Место",
        "sl": "Mesto",
        "tr": "Sıra",
        "uk": "Місце",
        "zh": "排名",
    },
    "Name": {
        "de": "Name",
        "es": "Nombre",
        "fr": "Nom",
        "it": "Nome",
        "ja": "名前",
        "ko": "이름",
        "nl": "Naam",
        "pl": "Nazwa",
        "pt": "Nome",
        "ru": "Имя",
        "sl": "Ime",
        "tr": "İsim",
        "uk": "Ім'я",
        "zh": "姓名",
    },
    "Score": {
        "de": "Punkte",
        "es": "Puntos",
        "fr": "Score",
        "it": "Punti",
        "ja": "スコア",
        "ko": "점수",
        "nl": "Score",
        "pl": "Wynik",
        "pt": "Pontos",
        "ru": "Очки",
        "sl": "Točke",
        "tr": "Skor",
        "uk": "Очки",
        "zh": "分数",
    },
    "No scores yet!": {
        "de": "Noch keine Punkte!",
        "es": "¡Sin puntuaciones!",
        "fr": "Aucun score !",
        "it": "Nessun punteggio!",
        "ja": "スコアなし！",
        "ko": "점수 없음!",
        "nl": "Nog geen scores!",
        "pl": "Brak wyników!",
        "pt": "Sem pontuações!",
        "ru": "Нет рекордов!",
        "sl": "Še ni rezultatov!",
        "tr": "Henüz skor yok!",
        "uk": "Ще немає результатів!",
        "zh": "暂无分数！",
    },
    "Press any key or click to continue": {
        "de": "Beliebige Taste drücken oder klicken zum Fortfahren",
        "es": "Presiona una tecla o haz clic para continuar",
        "fr": "Appuyez sur une touche ou cliquez pour continuer",
        "it": "Premi un tasto o clicca per continuare",
        "ja": "続行するにはキーを押すかクリックしてください",
        "ko": "계속하려면 아무 키나 누르거나 클릭하세요",
        "nl": "Druk op een toets of klik om door te gaan",
        "pl": "Naciśnij dowolny klawisz lub kliknij, aby kontynuować",
        "pt": "Pressione uma tecla ou clique para continuar",
        "ru": "Нажмите любую клавишу или щёлкните для продолжения",
        "sl": "Pritisnite tipko ali kliknite za nadaljevanje",
        "tr": "Devam etmek için bir tuşa basın veya tıklayın",
        "uk": "Натисніть будь-яку клавішу або клацніть для продовження",
        "zh": "按任意键或点击继续",
    },
    # Name entry dialog
    "NEW HIGH SCORE!": {
        "de": "NEUER REKORD!",
        "es": "¡NUEVO RÉCORD!",
        "fr": "NOUVEAU RECORD !",
        "it": "NUOVO RECORD!",
        "ja": "新記録！",
        "ko": "새 기록!",
        "nl": "NIEUW RECORD!",
        "pl": "NOWY REKORD!",
        "pt": "NOVO RECORDE!",
        "ru": "НОВЫЙ РЕКОРД!",
        "sl": "NOV REKORD!",
        "tr": "YENİ REKOR!",
        "uk": "НОВИЙ РЕКОРД!",
        "zh": "新纪录！",
    },
    "Enter your name:": {
        "de": "Geben Sie Ihren Namen ein:",
        "es": "Ingresa tu nombre:",
        "fr": "Entrez votre nom :",
        "it": "Inserisci il tuo nome:",
        "ja": "名前を入力：",
        "ko": "이름을 입력하세요:",
        "nl": "Voer uw naam in:",
        "pl": "Wpisz swoje imię:",
        "pt": "Digite seu nome:",
        "ru": "Введите ваше имя:",
        "sl": "Vnesite svoje ime:",
        "tr": "Adınızı girin:",
        "uk": "Введіть своє ім'я:",
        "zh": "请输入姓名：",
    },
    "OK": {
        "de": "OK",
        "es": "OK",
        "fr": "OK",
        "it": "OK",
        "ja": "OK",
        "ko": "확인",
        "nl": "OK",
        "pl": "OK",
        "pt": "OK",
        "ru": "ОК",
        "sl": "V redu",
        "tr": "Tamam",
        "uk": "OK",
        "zh": "确定",
    },
    "Cancel": {
        "de": "Abbrechen",
        "es": "Cancelar",
        "fr": "Annuler",
        "it": "Annulla",
        "ja": "キャンセル",
        "ko": "취소",
        "nl": "Annuleren",
        "pl": "Anuluj",
        "pt": "Cancelar",
        "ru": "Отмена",
        "sl": "Prekliči",
        "tr": "İptal",
        "uk": "Скасувати",
        "zh": "取消",
    },
}


def get_runtime_translation(text: str, language: str = "en") -> str:
    """Get translated runtime text for Pygame dialogs

    Args:
        text: The English text to translate
        language: Target language code (e.g., 'fr', 'de')

    Returns:
        Translated text, or original text if translation not available
    """
    if language == "en" or text not in RUNTIME_TRANSLATIONS:
        return text
    return RUNTIME_TRANSLATIONS[text].get(language, text)
