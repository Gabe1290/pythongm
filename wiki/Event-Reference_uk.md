# Довідник Подій

*[Головна](Home_uk) | [Посібник з Пресетів](Preset-Guide_uk) | [Повний довідник дій](Full-Action-Reference_uk)*

Ця сторінка документує всі доступні події в PyGameMaker. Події — це тригери, які виконують дії, коли в грі виникають певні умови.

## Категорії Подій

- [Події Об'єкта](Event-Reference-Object_uk) - Create, Step, Destroy
- [Події Введення](Event-Reference-Input_uk) - Клавіатура, Миша
- [Події Зіткнення](Event-Reference-Collision_uk) - Зіткнення об'єктів
- [Часові Події](Event-Reference-Timing_uk) - Будильники, Варіанти Step
- [Події Малювання](Event-Reference-Drawing_uk) - Користувацький рендеринг
- [Події Кімнати](Event-Reference-Room_uk) - Переходи між кімнатами
- [Події Гри](Event-Reference-Game_uk) - Початок/Кінець гри
- [Інші Події](Event-Reference-Other_uk) - Межі, Життя, Здоров'я

---

## Порядок Виконання Подій

Розуміння, коли спрацьовують події, допомагає створювати передбачувану
поведінку гри (перевірено проти головного циклу в
`runtime/game_runner.py`):

1. **Begin Step** — Початок кадру
2. **Alarm** — Усі будильники, що спрацювали, відраховують і активуються
3. **Step** (та **Keyboard (утримання)**) — Основна ігрова логіка, потім
   безперервні перевірки утримуваних клавіш для того самого екземпляра
4. **Keyboard Press/Release, Mouse** — Накопичені події введення для
   цього кадру обробляються (це відбувається *після* Step, а не до
   нього — код у Step реагує на клавіші, натиснуті вже *на початку*
   кадру, а не на ті, що натиснуті протягом нього)
5. **Рух, потім Collision** — Застосовується фізика (гравітація/тертя/
   hspeed/vspeed), потім виявляються зіткнення й запускаються їхні події
6. **End Step** (та **Destroy**) — Після зіткнень
7. **Draw** — Фаза рендерингу

---

## Події за Пресетом

Перевірено проти `events.event_types.get_available_events()`,
наповненого кожним реальним пресетом з `config/blockly_config.py` —
про те, що саме обмежує "пресет" (і в селекторі Blockly, і в
структурованій панелі Events/Actions), і як визначається пресет
проєкту, див. [Посібник з Пресетів](Preset-Guide_uk).

| Пресет | Включені Події |
|--------|----------------|
| **Початківець** (19 подій) | Create, Step, Keyboard (утримання), Keyboard \<No Key\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Середній** (21 подія) | + Destroy, Keyboard Press |
| **Повний** (лише редакція Development, 23 події) | + Keyboard Release, Mouse |

---

## Дивіться Також

- [Повний Довідник Дій](Full-Action-Reference_uk) — Повний список дій
- [Пресет для Початківців](Beginner-Preset_uk) — Основні події для початківців
- [Середній Пресет](Intermediate-Preset_uk) — Додаткові події
- [Події та Дії](Podii_ta_Dii_uk) — Огляд основних концепцій
