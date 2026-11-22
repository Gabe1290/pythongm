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
        "Control": "Steuerung",
        "Movement": "Bewegung",
        "Timing": "Zeitsteuerung",
        "Drawing": "Zeichnen",
        "Score/Lives/Health": "Punkte/Leben/Gesundheit",
        "Instance": "Instanz",
        "Room": "Raum",
        "Values": "Werte",
        "Sound": "Klang",
        "Game": "Spiel",
        "Particles": "Partikel",
        "Views": "Ansichten",
    },
    "es": {
        "Events": "Eventos",
        "Control": "Control",
        "Movement": "Movimiento",
        "Timing": "Temporizador",
        "Drawing": "Dibujo",
        "Score/Lives/Health": "Puntuación/Vidas/Salud",
        "Instance": "Instancia",
        "Room": "Sala",
        "Values": "Valores",
        "Sound": "Sonido",
        "Game": "Juego",
        "Particles": "Partículas",
        "Views": "Vistas",
    },
    "fr": {
        "Events": "Événements",
        "Control": "Contrôle",
        "Movement": "Mouvement",
        "Timing": "Minuterie",
        "Drawing": "Dessin",
        "Score/Lives/Health": "Score/Vies/Santé",
        "Instance": "Instance",
        "Room": "Salle",
        "Values": "Valeurs",
        "Sound": "Son",
        "Game": "Jeu",
        "Particles": "Particules",
        "Views": "Vues",
    },
    "it": {
        "Events": "Eventi",
        "Control": "Controllo",
        "Movement": "Movimento",
        "Timing": "Temporizzazione",
        "Drawing": "Disegno",
        "Score/Lives/Health": "Punteggio/Vite/Salute",
        "Instance": "Istanza",
        "Room": "Stanza",
        "Values": "Valori",
        "Sound": "Suono",
        "Game": "Gioco",
        "Particles": "Particelle",
        "Views": "Viste",
    },
    "ru": {
        "Events": "События",
        "Control": "Управление",
        "Movement": "Движение",
        "Timing": "Таймер",
        "Drawing": "Рисование",
        "Score/Lives/Health": "Очки/Жизни/Здоровье",
        "Instance": "Экземпляр",
        "Room": "Комната",
        "Values": "Значения",
        "Sound": "Звук",
        "Game": "Игра",
        "Particles": "Частицы",
        "Views": "Виды",
    },
    "sl": {
        "Events": "Dogodki",
        "Control": "Nadzor",
        "Movement": "Gibanje",
        "Timing": "Časovnik",
        "Drawing": "Risanje",
        "Score/Lives/Health": "Točke/Življenja/Zdravje",
        "Instance": "Primerek",
        "Room": "Soba",
        "Values": "Vrednosti",
        "Sound": "Zvok",
        "Game": "Igra",
        "Particles": "Delci",
        "Views": "Pogledi",
    },
    "uk": {
        "Events": "Події",
        "Control": "Керування",
        "Movement": "Рух",
        "Timing": "Таймер",
        "Drawing": "Малювання",
        "Score/Lives/Health": "Очки/Життя/Здоров'я",
        "Instance": "Екземпляр",
        "Room": "Кімната",
        "Values": "Значення",
        "Sound": "Звук",
        "Game": "Гра",
        "Particles": "Частинки",
        "Views": "Перегляди",
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

    # Control
    "if_condition": {
        "name": {"de": "Falls-Bedingung", "es": "Condición Si", "fr": "Condition Si", "it": "Condizione Se", "ru": "Условие Если", "sl": "Pogoj Če", "uk": "Умова Якщо"},
        "description": {"de": "Führt Aktionen nur aus, wenn eine Bedingung erfüllt ist (z. B. instance_count == 0)", "es": "Ejecuta acciones solo cuando se cumple una condición (p. ej. instance_count == 0)", "fr": "Exécute des actions seulement si une condition est vraie (ex. instance_count == 0)", "it": "Esegue le azioni solo quando una condizione è vera (es. instance_count == 0)", "ru": "Выполняет действия только при выполнении условия (например, instance_count == 0)", "sl": "Izvede dejanja samo, če je pogoj izpolnjen (npr. instance_count == 0)", "uk": "Виконує дії лише тоді, коли умова виконується (напр. instance_count == 0)"}
    },
    "set_variable": {
        "name": {"de": "Variable setzen", "es": "Definir Variable", "fr": "Définir Variable", "it": "Imposta Variabile", "ru": "Задать переменную", "sl": "Nastavi spremenljivko", "uk": "Встановити змінну"},
        "description": {"de": "Weist einer eigenen Variable der Instanz oder global einen Wert zu", "es": "Asigna un valor a una variable personalizada de la instancia o global", "fr": "Attribue une valeur à une variable personnalisée de l'instance ou globale", "it": "Assegna un valore a una variabile personalizzata dell'istanza o globale", "ru": "Присваивает значение собственной переменной экземпляра или глобальной", "sl": "Dodeli vrednost lastni spremenljivki primerka ali globalni spremenljivki", "uk": "Присвоює значення власній змінній екземпляра або глобальній змінній"}
    },
    "test_variable": {
        "name": {"de": "Variable prüfen", "es": "Comprobar Variable", "fr": "Tester Variable", "it": "Verifica Variabile", "ru": "Проверить переменную", "sl": "Preveri spremenljivko", "uk": "Перевірити змінну"},
        "description": {"de": "Vergleicht eine Variable mit einem Wert und führt verschachtelte Aktionen aus, wenn wahr", "es": "Compara una variable con un valor y ejecuta acciones anidadas si es verdadero", "fr": "Compare une variable à une valeur et exécute les actions imbriquées si vrai", "it": "Confronta una variabile con un valore ed esegue le azioni annidate se vero", "ru": "Сравнивает переменную со значением и выполняет вложенные действия при истине", "sl": "Primerja spremenljivko z vrednostjo in izvede vgnezdena dejanja, če je resnično", "uk": "Порівнює змінну зі значенням і виконує вкладені дії, якщо істина"}
    },
    "test_expression": {
        "name": {"de": "Falls-Bedingung (Logik)", "es": "Condición Si (Lógica)", "fr": "Condition Si (Logique)", "it": "Condizione Se (Logica)", "ru": "Условие Если (Логика)", "sl": "Pogoj Če (Logika)", "uk": "Умова Якщо (Логіка)"},
        "description": {"de": "Führt verschachtelte Aktionen aus, wenn eine aus Logik-Blöcken (Vergleich, Und/Oder, Nicht) gebaute Bedingung wahr ist", "es": "Ejecuta acciones anidadas cuando una condición construida con bloques de Lógica (comparar, y/o, no) es verdadera", "fr": "Exécute les actions imbriquées quand une condition construite avec des blocs Logique (comparaison, et/ou, non) est vraie", "it": "Esegue le azioni annidate quando una condizione costruita con blocchi Logica (confronto, e/o, non) è vera", "ru": "Выполняет вложенные действия, когда условие, построенное из блоков Логики (сравнение, и/или, не), истинно", "sl": "Izvede vgnezdena dejanja, ko je pogoj, sestavljen iz blokov Logika (primerjava, in/ali, ne), resničen", "uk": "Виконує вкладені дії, коли умова, побудована з блоків Логіки (порівняння, і/або, ні), є істинною"}
    },
    "check_empty": {
        "name": {"de": "Leerplatz prüfen", "es": "Comprobar Vacío", "fr": "Vérifier Vide", "it": "Verifica Vuoto", "ru": "Проверить пустоту", "sl": "Preveri prazno", "uk": "Перевірити порожнечу"},
        "description": {"de": "Wahr, wenn (x, y) keine Kollision hat — steuert nachfolgende Aktion(en) bei Gitterbewegung", "es": "Verdadero cuando (x, y) no tiene colisión — condiciona la(s) acción(es) siguiente(s) en movimiento de cuadrícula", "fr": "Vrai quand (x, y) n'a aucune collision — conditionne la/les action(s) suivante(s) en déplacement sur grille", "it": "Vero quando (x, y) non ha collisioni — condiziona le azioni successive nel movimento a griglia", "ru": "Истина, если (x, y) не имеет столкновения — управляет следующими действиями при движении по сетке", "sl": "Resnično, ko (x, y) nima trka — pogojuje naslednja dejanja pri premikanju po mreži", "uk": "Істина, якщо (x, y) не має зіткнення — керує наступними діями при русі по сітці"}
    },
    "exit_event": {
        "name": {"de": "Ereignis beenden", "es": "Salir del Evento", "fr": "Quitter l'Événement", "it": "Esci dall'Evento", "ru": "Выйти из события", "sl": "Zapusti dogodek", "uk": "Вийти з події"},
        "description": {"de": "Stoppt die Ausführung der restlichen Aktionen dieses Ereignisses — meist mit einem Test kombiniert, um beim ersten erfolgreichen Zweig abzubrechen", "es": "Detiene la ejecución del resto de las acciones de este evento — normalmente combinado con una prueba para detenerse en la primera rama exitosa", "fr": "Arrête l'exécution des actions restantes de cet événement — généralement associé à un test pour s'arrêter à la première branche réussie", "it": "Interrompe l'esecuzione delle azioni rimanenti di questo evento — di solito abbinato a un test per fermarsi al primo ramo riuscito", "ru": "Останавливает выполнение оставшихся действий этого события — обычно сочетается с проверкой для остановки на первой успешной ветке", "sl": "Ustavi izvajanje preostalih dejanj tega dogodka — običajno v paru s testom za ustavitev pri prvi uspešni veji", "uk": "Зупиняє виконання решти дій цієї події — зазвичай поєднується з перевіркою, щоб зупинитися на першій успішній гілці"}
    },
    "else_action": {
        "name": {"de": "Sonst", "es": "Si no", "fr": "Sinon", "it": "Altrimenti", "ru": "Иначе", "sl": "Sicer", "uk": "Інакше"},
        "description": {"de": "Führt die nächste Aktion nur aus, wenn der vorherige Test falsch war — mit Block-Start/-Ende kombinieren, um mehr als eine Aktion auf die Sonst-Seite zu legen", "es": "Ejecuta la siguiente acción solo cuando la prueba anterior fue falsa — combínalo con Iniciar/Finalizar Bloque para poner más de una acción en el lado 'si no'", "fr": "Exécute l'action suivante seulement si le test précédent était faux — associer à Début/Fin de Bloc pour mettre plus d'une action du côté sinon", "it": "Esegue l'azione successiva solo se il test precedente era falso — abbinare a Inizio/Fine Blocco per mettere più di un'azione sul lato altrimenti", "ru": "Выполняет следующее действие, только если предыдущая проверка была ложной — сочетайте с началом/концом блока, чтобы добавить более одного действия в ветку «иначе»", "sl": "Izvede naslednje dejanje samo, če je bil prejšnji test neresničen — združi z začetkom/koncem bloka, da postaviš več kot eno dejanje na stran sicer", "uk": "Виконує наступну дію лише тоді, коли попередня перевірка була хибною — поєднуйте з початком/кінцем блоку, щоб додати більше однієї дії в гілку «інакше»"}
    },
    "start_block": {
        "name": {"de": "Block-Start", "es": "Iniciar Bloque", "fr": "Début de Bloc", "it": "Inizio Blocco", "ru": "Начало блока", "sl": "Začetek bloka", "uk": "Початок блоку"},
        "description": {"de": "Gruppiert mehrere Aktionen, sodass eine vorherige Bedingung für alle gilt, nicht nur für die nächste", "es": "Agrupa varias acciones para que una condición anterior se aplique a todas ellas, no solo a la siguiente", "fr": "Regroupe plusieurs actions pour qu'une condition précédente s'applique à toutes, pas seulement à la suivante", "it": "Raggruppa più azioni in modo che una condizione precedente si applichi a tutte, non solo alla successiva", "ru": "Группирует несколько действий, чтобы предыдущее условие применялось ко всем им, а не только к следующему", "sl": "Združi več dejanj, tako da prejšnji pogoj velja za vsa, ne le za naslednje", "uk": "Групує кілька дій, щоб попередня умова застосовувалася до всіх них, а не лише до наступної"}
    },
    "end_block": {
        "name": {"de": "Block-Ende", "es": "Finalizar Bloque", "fr": "Fin de Bloc", "it": "Fine Blocco", "ru": "Конец блока", "sl": "Konec bloka", "uk": "Кінець блоку"},
        "description": {"de": "Schließt eine Block-Start-Gruppe", "es": "Cierra un grupo de Iniciar Bloque", "fr": "Ferme un groupe Début de Bloc", "it": "Chiude un gruppo Inizio Blocco", "ru": "Закрывает группу «Начало блока»", "sl": "Zapre skupino Začetek bloka", "uk": "Закриває групу «Початок блоку»"}
    },

    # Game
    "restart_game": {
        "name": {"de": "Spiel neu starten", "es": "Reiniciar Juego", "fr": "Redémarrer le Jeu", "it": "Riavvia Gioco", "ru": "Перезапустить игру", "sl": "Znova zaženi igro", "uk": "Перезапустити гру"},
        "description": {"de": "Startet im ersten Raum neu", "es": "Reinicia desde la primera sala", "fr": "Redémarre depuis la première salle", "it": "Riavvia dalla prima stanza", "ru": "Перезапускает с первой комнаты", "sl": "Znova zažene od prve sobe", "uk": "Перезапускає з першої кімнати"}
    },
    "load_game": {
        "name": {"de": "Spiel laden", "es": "Cargar Juego", "fr": "Charger la Partie", "it": "Carica Partita", "ru": "Загрузить игру", "sl": "Naloži igro", "uk": "Завантажити гру"},
        "description": {"de": "Stellt Raum, Punkte/Leben/Gesundheit, globale Variablen und Instanzzustände aus einer Spielstanddatei wieder her", "es": "Restaura la sala, puntuación/vidas/salud, variables globales y estados de instancia desde un archivo guardado", "fr": "Restaure la salle, le score/vies/santé, les variables globales et les états d'instance depuis un fichier de sauvegarde", "it": "Ripristina stanza, punteggio/vite/salute, variabili globali e stati delle istanze da un file di salvataggio", "ru": "Восстанавливает комнату, очки/жизни/здоровье, глобальные переменные и состояния экземпляров из файла сохранения", "sl": "Obnovi sobo, točke/življenja/zdravje, globalne spremenljivke in stanja primerkov iz datoteke shranjevanja", "uk": "Відновлює кімнату, рахунок/життя/здоров'я, глобальні змінні та стани екземплярів із файлу збереження"}
    },
    "save_game": {
        "name": {"de": "Spiel speichern", "es": "Guardar Juego", "fr": "Sauvegarder la Partie", "it": "Salva Partita", "ru": "Сохранить игру", "sl": "Shrani igro", "uk": "Зберегти гру"},
        "description": {"de": "Speichert den aktuellen Raum, Punkte/Leben/Gesundheit, globale Variablen und Instanzzustände in einer Datei", "es": "Guarda la sala actual, puntuación/vidas/salud, variables globales y estados de instancia en un archivo", "fr": "Enregistre la salle actuelle, le score/vies/santé, les variables globales et les états d'instance dans un fichier", "it": "Salva la stanza attuale, punteggio/vite/salute, variabili globali e stati delle istanze in un file", "ru": "Сохраняет текущую комнату, очки/жизни/здоровье, глобальные переменные и состояния экземпляров в файл", "sl": "Shrani trenutno sobo, točke/življenja/zdravje, globalne spremenljivke in stanja primerkov v datoteko", "uk": "Зберігає поточну кімнату, рахунок/життя/здоров'я, глобальні змінні та стани екземплярів у файл"}
    },
    "open_webpage": {
        "name": {"de": "Webseite öffnen", "es": "Abrir Página Web", "fr": "Ouvrir une Page Web", "it": "Apri Pagina Web", "ru": "Открыть веб-страницу", "sl": "Odpri spletno stran", "uk": "Відкрити вебсторінку"},
        "description": {"de": "Öffnet eine URL im Standardbrowser", "es": "Abre una URL en el navegador predeterminado", "fr": "Ouvre une URL dans le navigateur par défaut", "it": "Apre un URL nel browser predefinito", "ru": "Открывает URL в браузере по умолчанию", "sl": "Odpre URL v privzetem brskalniku", "uk": "Відкриває URL у браузері за замовчуванням"}
    },
    "set_window_caption": {
        "name": {"de": "Fenstertitel festlegen", "es": "Definir Título de Ventana", "fr": "Définir le Titre de Fenêtre", "it": "Imposta Titolo Finestra", "ru": "Задать заголовок окна", "sl": "Nastavi naslov okna", "uk": "Встановити заголовок вікна"},
        "description": {"de": "Konfiguriert die Anzeige von Punkte/Leben/Gesundheit im Fenstertitel", "es": "Configura la visualización de puntuación/vidas/salud en el título de la ventana", "fr": "Configure l'affichage du score/vies/santé dans le titre de la fenêtre", "it": "Configura la visualizzazione di punteggio/vite/salute nel titolo della finestra", "ru": "Настраивает отображение очков/жизней/здоровья в заголовке окна", "sl": "Nastavi prikaz točk/življenj/zdravja v naslovu okna", "uk": "Налаштовує відображення рахунку/життів/здоров'я в заголовку вікна"}
    },
    "show_info": {
        "name": {"de": "Spielinfo anzeigen", "es": "Mostrar Info del Juego", "fr": "Afficher Infos du Jeu", "it": "Mostra Info Gioco", "ru": "Показать информацию об игре", "sl": "Prikaži info igre", "uk": "Показати інформацію про гру"},
        "description": {"de": "Zeigt den Spielinformationsbildschirm an", "es": "Muestra la pantalla de información del juego", "fr": "Affiche l'écran d'informations du jeu", "it": "Mostra la schermata informazioni del gioco", "ru": "Отображает экран информации об игре", "sl": "Prikaže zaslon z informacijami o igri", "uk": "Відображає екран інформації про гру"}
    },
    "show_video": {
        "name": {"de": "Video abspielen", "es": "Mostrar Vídeo", "fr": "Afficher une Vidéo", "it": "Mostra Video", "ru": "Показать видео", "sl": "Prikaži video", "uk": "Показати відео"},
        "description": {"de": "Spielt eine Videodatei im Standard-Videoplayer deines Systems ab", "es": "Reproduce un archivo de vídeo en el reproductor predeterminado de tu sistema", "fr": "Lit un fichier vidéo dans le lecteur vidéo par défaut du système", "it": "Riproduce un file video nel lettore video predefinito del sistema", "ru": "Воспроизводит видеофайл в видеопроигрывателе системы по умолчанию", "sl": "Predvaja video datoteko v privzetem video predvajalniku sistema", "uk": "Відтворює відеофайл у стандартному відеоплеєрі системи"}
    },
    "splash_show_image": {
        "name": {"de": "Startbild: Bild anzeigen", "es": "Splash: Mostrar Imagen", "fr": "Splash : Afficher une Image", "it": "Splash: Mostra Immagine", "ru": "Заставка: показать изображение", "sl": "Uvodna slika: prikaži sliko", "uk": "Заставка: показати зображення"},
        "description": {"de": "Zeigt einen Sprite im Vollbild und pausiert das Spiel, bis der Spieler es schließt", "es": "Muestra un sprite a pantalla completa y pausa el juego hasta que el jugador lo cierre", "fr": "Affiche un sprite en plein écran et met le jeu en pause jusqu'à ce que le joueur le ferme", "it": "Mostra uno sprite a schermo intero e mette in pausa il gioco finché il giocatore non lo chiude", "ru": "Показывает спрайт на весь экран и приостанавливает игру, пока игрок его не закроет", "sl": "Prikaže sprite čez cel zaslon in zaustavi igro, dokler je igralec ne zapre", "uk": "Показує спрайт на весь екран і призупиняє гру, доки гравець її не закриє"}
    },
    "splash_show_text": {
        "name": {"de": "Startbild: Text anzeigen", "es": "Splash: Mostrar Texto", "fr": "Splash : Afficher un Texte", "it": "Splash: Mostra Testo", "ru": "Заставка: показать текст", "sl": "Uvodna slika: prikaži besedilo", "uk": "Заставка: показати текст"},
        "description": {"de": "Zeigt eine Nachricht an und pausiert das Spiel, bis der Spieler sie schließt", "es": "Muestra un mensaje y pausa el juego hasta que el jugador lo cierre", "fr": "Affiche un message et met le jeu en pause jusqu'à ce que le joueur le ferme", "it": "Mostra un messaggio e mette in pausa il gioco finché il giocatore non lo chiude", "ru": "Показывает сообщение и приостанавливает игру, пока игрок его не закроет", "sl": "Prikaže sporočilo in zaustavi igro, dokler je igralec ne zapre", "uk": "Показує повідомлення і призупиняє гру, доки гравець її не закриє"}
    },

    # Views
    "enable_views": {
        "name": {"de": "Ansichten aktivieren", "es": "Activar Vistas", "fr": "Activer les Vues", "it": "Attiva Viste", "ru": "Включить виды", "sl": "Omogoči poglede", "uk": "Увімкнути перегляди"},
        "description": {"de": "Schaltet das Kamera-/Ansichtssystem des Raums ein oder aus (lässt ein Level scrollen, wenn es größer als das Fenster ist)", "es": "Activa o desactiva el sistema de cámara/vista de la sala (permite desplazar un nivel más grande que la ventana)", "fr": "Active ou désactive le système de caméra/vue de la salle (permet à un niveau de défiler s'il est plus grand que la fenêtre)", "it": "Attiva o disattiva il sistema di telecamera/vista della stanza (consente lo scorrimento di un livello più grande della finestra)", "ru": "Включает или выключает систему камеры/вида комнаты (позволяет прокручивать уровень, если он больше окна)", "sl": "Vklopi ali izklopi sistem kamere/pogleda sobe (omogoči drsenje nivoja, ki je večji od okna)", "uk": "Вмикає або вимикає систему камери/перегляду кімнати (дозволяє прокручувати рівень, якщо він більший за вікно)"}
    },
    "set_view": {
        "name": {"de": "Ansicht festlegen", "es": "Definir Vista", "fr": "Définir une Vue", "it": "Imposta Vista", "ru": "Задать вид", "sl": "Nastavi pogled", "uk": "Встановити перегляд"},
        "description": {"de": "Konfiguriert eine Kameraansicht: welcher Teil des Raums gezeigt wird, wo sie auf dem Bildschirm zeichnet, und ein zu verfolgendes Objekt", "es": "Configura una vista de cámara: qué parte de la sala muestra, dónde se dibuja en pantalla y un objeto a seguir", "fr": "Configure une vue de caméra : quelle partie de la salle elle montre, où elle s'affiche à l'écran, et un objet à suivre", "it": "Configura una vista della telecamera: quale parte della stanza mostra, dove disegna sullo schermo e un oggetto da seguire", "ru": "Настраивает вид камеры: какую часть комнаты показывает, где рисует на экране и объект для слежения", "sl": "Nastavi pogled kamere: kateri del sobe prikazuje, kje na zaslonu riše, in predmet, ki naj mu sledi", "uk": "Налаштовує вид камери: яку частину кімнати показує, де малює на екрані та об'єкт для стеження"}
    },
}


# The 32 blocks the Configure Blocks dialog still showed in English inside
# translated categories (TODO.md, closed 2026-11-21). Order: de, es, fr, it, ru, sl, uk.
_BLOCK_LANGS = ("de", "es", "fr", "it", "ru", "sl", "uk")
_MORE_BLOCKS = {
    "event_other": (
        ("Weitere Ereignisse", "Otros eventos", "Autres événements", "Altri eventi", "Другие события", "Drugi dogodki", "Інші події"),
        ("Keine Leben mehr, keine Gesundheit mehr, Raum-Ereignisse", "Sin vidas, sin salud, eventos de sala", "Plus de vies, plus de santé, événements de salle",
         "Vite esaurite, salute esaurita, eventi della stanza", "Нет жизней, нет здоровья, события комнаты", "Ni več življenj, ni več zdravja, dogodki sobe",
         "Немає життів, немає здоров'я, події кімнати")),
    "move_free": (
        ("Frei bewegen", "Mover libremente", "Déplacement libre", "Movimento libero", "Свободное движение", "Prosto gibanje", "Вільний рух"),
        ("In beliebigem Richtungswinkel und Tempo bewegen", "Moverse con cualquier ángulo de dirección y velocidad", "Se déplacer selon un angle de direction et une vitesse quelconques",
         "Muoversi con un angolo di direzione e una velocità qualsiasi", "Двигаться под любым углом направления и с любой скоростью",
         "Premikanje pod poljubnim kotom smeri in hitrostjo", "Рухатися під будь-яким кутом напрямку та з будь-якою швидкістю")),
    "set_speed": (
        ("Geschwindigkeit setzen", "Establecer velocidad", "Définir la vitesse", "Imposta velocità", "Задать скорость", "Nastavi hitrost", "Встановити швидкість"),
        ("Betrag der Geschwindigkeit setzen (Richtung bleibt)", "Establecer la magnitud de la velocidad (mantiene la dirección)", "Définir la valeur de la vitesse (garde la direction)",
         "Imposta l'intensità della velocità (mantiene la direzione)", "Задать величину скорости (направление сохраняется)",
         "Nastavi velikost hitrosti (smer ostane)", "Встановити величину швидкості (напрямок зберігається)")),
    "set_direction": (
        ("Richtung setzen", "Establecer dirección", "Définir la direction", "Imposta direzione", "Задать направление", "Nastavi smer", "Встановити напрямок"),
        ("Richtungswinkel setzen (Geschwindigkeit bleibt)", "Establecer el ángulo de dirección (mantiene la velocidad)", "Définir l'angle de direction (garde la vitesse)",
         "Imposta l'angolo di direzione (mantiene la velocità)", "Задать угол направления (скорость сохраняется)", "Nastavi kot smeri (hitrost ostane)",
         "Встановити кут напрямку (швидкість зберігається)")),
    "grid_move": (
        ("Im Raster bewegen", "Mover en cuadrícula", "Déplacement sur la grille", "Movimento a griglia", "Движение по сетке", "Premik po mreži", "Рух по сітці"),
        ("Eine Rastereinheit in eine Richtung bewegen", "Moverse una unidad de cuadrícula en una dirección", "Se déplacer d'une case de la grille dans une direction",
         "Muoversi di una casella della griglia in una direzione", "Сдвинуться на одну клетку сетки в заданном направлении", "Premik za eno polje mreže v izbrani smeri",
         "Зсунутися на одну клітинку сітки в заданому напрямку")),
    "bounce": (
        ("Abprallen", "Rebotar", "Rebondir", "Rimbalza", "Отскочить", "Odbij se", "Відскочити"),
        ("An festen Objekten abprallen", "Rebotar contra objetos sólidos", "Rebondir sur les objets solides", "Rimbalza sugli oggetti solidi",
         "Отскакивать от твёрдых объектов", "Odbij se od trdnih objektov", "Відскакувати від твердих об'єктів")),
    "wrap_around_room": (
        ("Um den Raum herumführen", "Dar la vuelta a la sala", "Traverser les bords de la salle", "Attraversa i bordi della stanza", "Переход через край комнаты",
         "Prehod čez rob sobe", "Перехід через край кімнати"),
        ("Auf der gegenüberliegenden Seite wieder erscheinen", "Aparecer por el lado opuesto", "Réapparaître du côté opposé", "Riapparire dal lato opposto",
         "Появиться с противоположной стороны", "Pojavi se na nasprotni strani", "З'явитися з протилежного боку")),
    "move_to_contact": (
        ("Bis zum Kontakt bewegen", "Mover hasta el contacto", "Avancer jusqu'au contact", "Muovi fino al contatto", "Двигаться до касания", "Premakni do stika", "Рухатися до дотику"),
        ("Bewegen, bis eine Berührung stattfindet", "Moverse hasta tocar algo", "Avancer jusqu'à toucher quelque chose", "Muoversi finché non tocca qualcosa",
         "Двигаться, пока не коснётся препятствия", "Premikaj se, dokler se česa ne dotakne", "Рухатися, доки не торкнеться перешкоди")),
    "test_alignment": (
        ("Rasterausrichtung prüfen", "Comprobar alineación con la cuadrícula", "Tester l'alignement sur la grille", "Verifica allineamento alla griglia",
         "Проверить выравнивание по сетке", "Preveri poravnavo z mrežo", "Перевірити вирівнювання за сіткою"),
        ("Bedingung: wahr, wenn die Instanz am Raster ausgerichtet ist", "Condición: verdadera si la instancia está alineada con la cuadrícula",
         "Condition : vraie si l'instance est alignée sur la grille", "Condizione: vera se l'istanza è allineata alla griglia",
         "Условие: истинно, если экземпляр выровнен по сетке", "Pogoj: resničen, če je primerek poravnan z mrežo", "Умова: істинна, якщо екземпляр вирівняно за сіткою")),
    "execute_code": (
        ("Code ausführen", "Ejecutar código", "Exécuter du code", "Esegui codice", "Выполнить код", "Izvedi kodo", "Виконати код"),
        ("Eigenen Python-Code ausführen", "Ejecutar código Python propio", "Exécuter du code Python personnalisé", "Esegui codice Python personalizzato",
         "Выполнить собственный код на Python", "Izvedi lastno kodo Python", "Виконати власний код Python")),
    "draw_arrow": (
        ("Pfeil zeichnen", "Dibujar flecha", "Dessiner une flèche", "Disegna freccia", "Нарисовать стрелку", "Nariši puščico", "Намалювати стрілку"),
        ("Einen Pfeil von einem Punkt zu einem anderen zeichnen", "Dibujar una flecha de un punto a otro", "Dessiner une flèche d'un point à un autre",
         "Disegna una freccia da un punto a un altro", "Нарисовать стрелку от одной точки к другой", "Nariši puščico od ene točke do druge",
         "Намалювати стрілку від однієї точки до іншої")),
    "draw_background": (
        ("Hintergrund zeichnen", "Dibujar fondo", "Dessiner un arrière-plan", "Disegna sfondo", "Нарисовать фон", "Nariši ozadje", "Намалювати тло"),
        ("Ein Hintergrundbild zeichnen, wahlweise über den Bildschirm gekachelt", "Dibujar una imagen de fondo, opcionalmente repetida en toda la pantalla",
         "Dessiner une image d'arrière-plan, éventuellement répétée sur tout l'écran", "Disegna un'immagine di sfondo, eventualmente ripetuta su tutto lo schermo",
         "Нарисовать фоновое изображение, при желании повторяя его по всему экрану", "Nariši sliko ozadja, po želji ponovljeno čez ves zaslon",
         "Намалювати зображення тла, за бажанням повторюючи його по всьому екрану")),
    "draw_ellipse": (
        ("Ellipse zeichnen", "Dibujar elipse", "Dessiner une ellipse", "Disegna ellisse", "Нарисовать эллипс", "Nariši elipso", "Намалювати еліпс"),
        ("Eine gefüllte oder umrandete Ellipse in einem Rahmen zeichnen", "Dibujar una elipse rellena o con contorno dentro de un rectángulo",
         "Dessiner une ellipse pleine ou en contour dans un rectangle", "Disegna un'ellisse piena o solo contorno all'interno di un rettangolo",
         "Нарисовать заполненный или контурный эллипс внутри прямоугольника", "Nariši polno ali obrobljeno elipso znotraj pravokotnika",
         "Намалювати заповнений або контурний еліпс усередині прямокутника")),
    "draw_line": (
        ("Linie zeichnen", "Dibujar línea", "Dessiner une ligne", "Disegna linea", "Нарисовать линию", "Nariši črto", "Намалювати лінію"),
        ("Eine Linie zwischen zwei Punkten zeichnen", "Dibujar una línea entre dos puntos", "Dessiner une ligne entre deux points", "Disegna una linea tra due punti",
         "Нарисовать линию между двумя точками", "Nariši črto med dvema točkama", "Намалювати лінію між двома точками")),
    "draw_scaled_text": (
        ("Skalierten Text zeichnen", "Dibujar texto escalado", "Dessiner du texte mis à l'échelle", "Disegna testo in scala", "Нарисовать масштабированный текст",
         "Nariši povečano besedilo", "Намалювати масштабований текст"),
        ("Text in beliebiger Größe zeichnen", "Dibujar texto a cualquier escala", "Dessiner du texte à n'importe quelle échelle", "Disegna testo a qualsiasi scala",
         "Нарисовать текст в любом масштабе", "Nariši besedilo v poljubnem merilu", "Намалювати текст у будь-якому масштабі")),
    "draw_sprite": (
        ("Sprite zeichnen", "Dibujar sprite", "Dessiner un sprite", "Disegna sprite", "Нарисовать спрайт", "Nariši sprite", "Намалювати спрайт"),
        ("Ein Sprite-Bild an einer Position zeichnen", "Dibujar un fotograma de sprite en una posición", "Dessiner une image d'un sprite à une position",
         "Disegna un fotogramma di uno sprite in una posizione", "Нарисовать кадр спрайта в заданной позиции", "Nariši sličico spritea na izbranem mestu",
         "Намалювати кадр спрайта в заданій позиції")),
    "fill_color": (
        ("Bildschirm mit Farbe füllen", "Rellenar pantalla con color", "Remplir l'écran d'une couleur", "Riempi lo schermo di colore", "Залить экран цветом",
         "Zapolni zaslon z barvo", "Залити екран кольором"),
        ("Den ganzen Sichtbereich mit einer Farbe füllen", "Rellenar toda la vista con un color sólido", "Remplir toute la vue d'une couleur unie",
         "Riempi l'intera vista con un colore pieno", "Залить всю видимую область сплошным цветом", "Zapolni celoten vidni del z enobarvno barvo",
         "Залити всю видиму область суцільним кольором")),
    "set_color": (
        ("Farbe setzen", "Establecer color", "Définir la couleur", "Imposta colore", "Задать цвет", "Nastavi barvo", "Встановити колір"),
        ("Zeichenfarbe und Deckkraft für die folgenden Zeichnungen setzen", "Establecer el color y la opacidad de dibujo para los siguientes dibujos",
         "Définir la couleur et l'opacité des dessins suivants", "Imposta colore e opacità per i disegni successivi",
         "Задать цвет и прозрачность для следующих рисунков", "Nastavi barvo in prosojnost za naslednja risanja", "Встановити колір і прозорість для наступних малюнків")),
    "set_draw_color": (
        ("Zeichenfarbe setzen", "Establecer color de dibujo", "Définir la couleur de dessin", "Imposta colore di disegno", "Задать цвет рисования",
         "Nastavi barvo risanja", "Встановити колір малювання"),
        ("Die Farbe für die folgenden Zeichenaktionen setzen", "Establecer el color de las siguientes acciones de dibujo",
         "Définir la couleur utilisée par les actions de dessin suivantes", "Imposta il colore usato dalle azioni di disegno successive",
         "Задать цвет для следующих действий рисования", "Nastavi barvo za naslednja dejanja risanja", "Встановити колір для наступних дій малювання")),
    "set_draw_font": (
        ("Schriftart setzen", "Establecer fuente de dibujo", "Définir la police de dessin", "Imposta carattere di disegno", "Задать шрифт рисования",
         "Nastavi pisavo risanja", "Встановити шрифт малювання"),
        ("Schriftart und Ausrichtung für den folgenden Text setzen", "Establecer la fuente y la alineación para el texto siguiente",
         "Définir la police et l'alignement du texte dessiné ensuite", "Imposta carattere e allineamento per il testo successivo",
         "Задать шрифт и выравнивание для следующего текста", "Nastavi pisavo in poravnavo za naslednje besedilo", "Встановити шрифт і вирівнювання для наступного тексту")),
    "test_health": (
        ("Gesundheit prüfen", "Comprobar salud", "Tester la santé", "Verifica salute", "Проверить здоровье", "Preveri zdravje", "Перевірити здоров'я"),
        ("Bedingung: aktuelle Gesundheit mit einem Wert vergleichen", "Condición: comparar la salud actual con un valor", "Condition : comparer la santé actuelle à une valeur",
         "Condizione: confronta la salute attuale con un valore", "Условие: сравнить текущее здоровье со значением", "Pogoj: primerjaj trenutno zdravje z vrednostjo",
         "Умова: порівняти поточне здоров'я зі значенням")),
    "test_score": (
        ("Punktzahl prüfen", "Comprobar puntuación", "Tester le score", "Verifica punteggio", "Проверить счёт", "Preveri točke", "Перевірити рахунок"),
        ("Bedingung: Punktzahl mit einem Wert vergleichen", "Condición: comparar la puntuación con un valor", "Condition : comparer le score à une valeur",
         "Condizione: confronta il punteggio con un valore", "Условие: сравнить счёт со значением", "Pogoj: primerjaj točke z vrednostjo", "Умова: порівняти рахунок зі значенням")),
    "test_lives": (
        ("Leben prüfen", "Comprobar vidas", "Tester les vies", "Verifica vite", "Проверить жизни", "Preveri življenja", "Перевірити життя"),
        ("Bedingung: Anzahl der Leben mit einem Wert vergleichen", "Condición: comparar el número de vidas con un valor", "Condition : comparer le nombre de vies à une valeur",
         "Condizione: confronta il numero di vite con un valore", "Условие: сравнить число жизней со значением", "Pogoj: primerjaj število življenj z vrednostjo",
         "Умова: порівняти кількість життів зі значенням")),
    "show_highscore": (
        ("Bestenliste anzeigen", "Mostrar puntuaciones altas", "Afficher les meilleurs scores", "Mostra punteggi migliori", "Показать рекорды", "Prikaži najboljše rezultate",
         "Показати рекорди"),
        ("Die Bestenliste anzeigen", "Mostrar la tabla de puntuaciones altas", "Afficher le tableau des meilleurs scores", "Mostra la tabella dei punteggi migliori",
         "Показать таблицу рекордов", "Prikaži lestvico najboljših rezultatov", "Показати таблицю рекордів")),
    "clear_highscore": (
        ("Bestenliste löschen", "Borrar puntuaciones altas", "Effacer les meilleurs scores", "Cancella punteggi migliori", "Очистить рекорды", "Počisti najboljše rezultate",
         "Очистити рекорди"),
        ("Die Bestenliste zurücksetzen", "Reiniciar la tabla de puntuaciones altas", "Réinitialiser le tableau des meilleurs scores", "Azzera la tabella dei punteggi migliori",
         "Сбросить таблицу рекордов", "Ponastavi lestvico najboljših rezultatov", "Скинути таблицю рекордів")),
    "instance_destroy_object": (
        ("Alle eines Objekts zerstören", "Destruir todas las de un objeto", "Détruire toutes les instances d'un objet", "Distruggi tutte le istanze di un oggetto",
         "Уничтожить все экземпляры объекта", "Uniči vse primerke objekta", "Знищити всі екземпляри об'єкта"),
        ("Jede Instanz eines Objekts zerstören", "Destruir cada instancia de un objeto", "Détruire chaque instance d'un objet", "Distruggi ogni istanza di un oggetto",
         "Уничтожить каждый экземпляр объекта", "Uniči vsak primerek objekta", "Знищити кожен екземпляр об'єкта")),
    "instance_change": (
        ("Instanz ändern", "Cambiar instancia", "Changer d'instance", "Cambia istanza", "Сменить экземпляр", "Spremeni primerek", "Змінити екземпляр"),
        ("In einen anderen Objekttyp verwandeln", "Transformarse en otro tipo de objeto", "Se transformer en un autre type d'objet", "Trasformarsi in un altro tipo di oggetto",
         "Превратиться в объект другого типа", "Preobrazi se v drugo vrsto objekta", "Перетворитися на об'єкт іншого типу")),
    "if_can_push": (
        ("Wenn schieben möglich", "Si se puede empujar", "Si on peut pousser", "Se si può spingere", "Если можно толкнуть", "Če je mogoče potisniti", "Якщо можна штовхнути"),
        ("Schiebeprüfung wie bei Sokoban", "Comprobación de empuje al estilo Sokoban", "Vérification de poussée à la manière de Sokoban",
         "Controllo di spinta in stile Sokoban", "Проверка толкания в стиле Сокобана", "Preverjanje potiska kot v igri Sokoban", "Перевірка штовхання в стилі Сокобана")),
    "room_goto_previous": (
        ("Vorheriger Raum", "Sala anterior", "Salle précédente", "Stanza precedente", "Предыдущая комната", "Prejšnja soba", "Попередня кімната"),
        ("Zum vorherigen Raum gehen", "Ir a la sala anterior", "Aller à la salle précédente", "Vai alla stanza precedente", "Перейти в предыдущую комнату",
         "Pojdi v prejšnjo sobo", "Перейти до попередньої кімнати")),
    "room_if_next_exists": (
        ("Wenn nächster Raum existiert", "Si existe la siguiente sala", "Si la salle suivante existe", "Se esiste la stanza successiva", "Если есть следующая комната",
         "Če obstaja naslednja soba", "Якщо є наступна кімната"),
        ("Prüfen, ob ein nächster Raum existiert", "Comprobar si existe la siguiente sala", "Vérifier si la salle suivante existe", "Verifica se esiste la stanza successiva",
         "Проверить, есть ли следующая комната", "Preveri, ali obstaja naslednja soba", "Перевірити, чи є наступна кімната")),
    "room_if_previous_exists": (
        ("Wenn vorheriger Raum existiert", "Si existe la sala anterior", "Si la salle précédente existe", "Se esiste la stanza precedente", "Если есть предыдущая комната",
         "Če obstaja prejšnja soba", "Якщо є попередня кімната"),
        ("Prüfen, ob ein vorheriger Raum existiert", "Comprobar si existe la sala anterior", "Vérifier si la salle précédente existe", "Verifica se esiste la stanza precedente",
         "Проверить, есть ли предыдущая комната", "Preveri, ali obstaja prejšnja soba", "Перевірити, чи є попередня кімната")),
    "game_end": (
        ("Spiel beenden", "Terminar juego", "Terminer le jeu", "Termina il gioco", "Завершить игру", "Končaj igro", "Завершити гру"),
        ("Das Spiel schließen", "Cerrar el juego", "Fermer le jeu", "Chiudi il gioco", "Закрыть игру", "Zapri igro", "Закрити гру")),
}
for _type, (_names, _descs) in _MORE_BLOCKS.items():
    BLOCK_TRANSLATIONS.setdefault(_type, {
        "name": dict(zip(_BLOCK_LANGS, _names)),
        "description": dict(zip(_BLOCK_LANGS, _descs)),
    })


# Languages kept in their own modules (config/blockly_block_i18n_<lang>.py):
# CATEGORIES = {category: text}, BLOCKS = {block_type: (name, description)}.
# docs/BLOCKLY_DIALOG_I18N_2026-11-22.md.
MODULE_LANGUAGES = ("pl",)


def _merge_language_modules():
    import importlib
    for _lang in MODULE_LANGUAGES:
        _mod = importlib.import_module(f"config.blockly_block_i18n_{_lang}")
        CATEGORY_TRANSLATIONS.setdefault(_lang, {}).update(_mod.CATEGORIES)
        for _type, (_name, _desc) in _mod.BLOCKS.items():
            _entry = BLOCK_TRANSLATIONS.setdefault(_type, {"name": {}, "description": {}})
            _entry["name"][_lang] = _name
            _entry["description"][_lang] = _desc


_merge_language_modules()

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


def register_category_translations(mapping) -> None:
    """Merge ``{lang: {category: translated}}`` from an extension
    (PLUGIN_BLOCK_CATEGORY_TRANSLATIONS). Existing entries are kept."""
    for language, categories in (mapping or {}).items():
        table = CATEGORY_TRANSLATIONS.setdefault(language, {})
        for category, text in categories.items():
            table.setdefault(category, text)


def register_block_translations(mapping) -> None:
    """Merge ``{block_type: {"name": {lang: ..}, "description": {lang: ..}}}``
    from an extension (PLUGIN_BLOCK_TRANSLATIONS). Existing entries are kept."""
    for block_type, entry in (mapping or {}).items():
        BLOCK_TRANSLATIONS.setdefault(block_type, entry)


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
