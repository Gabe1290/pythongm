# Посібник: Створення Гри про Посадку на Місяць

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Вступ

У цьому посібнику ви створите **Гру про Посадку на Місяць** — класичну аркадну гру, де ви керуєте космічним кораблем, що опускається на посадковий майданчик. Ви маєте керувати тягою, щоб протидіяти гравітації, і м'яко приземлитися без аварії. Ця гра ідеально підходить для вивчення фізичних понять: гравітації, тяги, швидкості та керування пальним.

**Що ви навчитесь:**
- Фізика гравітації та тяги
- Виявлення посадки за швидкістю
- Система керування пальним
- Керування обертанням або напрямком
- Безпечні зони посадки

**Складність:** Початківець
**Пресет:** Середній Пресет (фізика тяги/пального всюди спирається на Execute Code, якого немає в Пресеті для Початківців)

---

## Крок 1: Зрозуміти Гру

### Механіки Гри
1. Модуль тягне вниз гравітація
2. Натискання ВГОРУ створює тягу вгору (витрачає пальне)
3. ВЛІВО/ВПРАВО керують обертанням або рухом модуля
4. М'яко приземліться на майданчик, щоб перемогти
5. Аварія, якщо приземлитеся надто швидко або промахнетеся повз майданчик
6. Скінчиться пальне — не зможете загальмувати!

### Що Нам Потрібно

| Елемент | Призначення |
|---------|-------------|
| **Модуль** | Космічний корабель, яким ви керуєте |
| **Посадковий майданчик** | Безпечна зона для посадки |
| **Земля** | Рельєф, що спричиняє аварію |
| **Індикатор пального** | Показує залишок пального |
| **Індикатор швидкості** | Показує поточну швидкість |

---

## Крок 2: Створити Спрайти

### 2.1 Спрайт Модуля

1. У **Дереві Ресурсів** клацніть правою кнопкою на **Sprites** та виберіть **Create Sprite**
2. Назвіть його `spr_lander`
3. Натисніть **Edit Sprite**, щоб відкрити редактор спрайтів
4. Намалюйте простий космічний корабель (трикутник або класичну форму посадкового модуля)
5. Розмір: 32x32 пікселі
6. **Важливо:** встановіть початок координат по центру знизу для правильної посадки

### 2.2 Спрайт Посадкового Майданчика

1. Створіть новий спрайт з назвою `spr_pad`
2. Намалюйте плоску платформу з розміткою (як літера "H")
3. Використайте яскраві кольори (жовтий/зелений)
4. Розмір: 64x16 пікселів

### 2.3 Спрайт Землі

1. Створіть новий спрайт з назвою `spr_ground`
2. Намалюйте кам'янистий/нерівний рельєф
3. Використайте сірий/коричневий колір
4. Розмір: 32x32 пікселі

### 2.4 Спрайт Полум'я (Необов'язково)

1. Створіть новий спрайт з назвою `spr_flame`
2. Намалюйте невелике полум'я/вихлоп
3. Використайте помаранчевий/жовтий колір
4. Розмір: 16x16 пікселів

![The Sprite Editor with spr_lander open, Origin set to Center-Bottom (X 16, Y 32); spr_lander, spr_pad, spr_ground and spr_flame in the resource tree](images/tutorial-lunarlander-02-sprites.png)

---

## Крок 3: Створити Об'єкт Землі

Земля — це небезпечний рельєф, що спричиняє аварію.

1. Клацніть правою кнопкою на **Objects** та виберіть **Create Object**
2. Назвіть його `obj_ground`
3. Встановіть спрайт `spr_ground`
4. **Позначте прапорець "Solid"**
5. Події не потрібні

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-lunarlander-03-ground-object.png)

---

## Крок 4: Створити Об'єкт Посадкового Майданчика

Посадковий майданчик — це місце, де гравець має безпечно приземлитися.

1. Створіть новий об'єкт з назвою `obj_pad`
2. Встановіть спрайт `spr_pad`
3. **Позначте прапорець "Solid"**
4. Події не потрібні (зіткнення обробляє модуль)

![obj_pad's Object Events panel: empty, with Solid checked](images/tutorial-lunarlander-04-pad-object.png)

---

## Крок 5: Створити Об'єкт Модуля

Модуль — головний об'єкт, яким керує гравець, з фізикою. На відміну від
інших посібників про рух у цьому вікі, його керування має поступово
накопичувати швидкість і стежити за ресурсом пального, тож цей об'єкт
більше спирається на **Control** → **Execute Code** (справжній Python —
`self` це поточний екземпляр, `game` це рушій гри, `keyboard.check(ім'я)`
повідомляє про утримувану клавішу), ніж лише на структуровані дії. Скрізь,
де структурована дія справляється, цей посібник усе одно використовує її.

1. Створіть новий об'єкт з назвою `obj_lander`
2. Встановіть спрайт `spr_lander`

### 5.1 Гравітація та Початкові Змінні

**Подія: Create**
1. Додайте дію **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — легке притягання вниз; рушій на кожному кроці автоматично додає його
   до вертикальної швидкості модуля, так само як гравітація в посібнику
   Платформер, лише слабше.
2. Додайте дію **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Система руху цього проєкту вже стежить за швидкістю через
`self.hspeed`/`self.vspeed` і переміщує екземпляр на цю величину на
кожному кадрі (з вбудованим зіткненням з твердими об'єктами) — не потрібно
створювати окремі змінні `hsp`/`vsp`, як це робила б ручна фізична
симуляція.

### 5.2 Подія Step — Тяга та Керування

**Подія: Step** — Додайте дію **Control** → **Execute Code**:

```python
if not self.landed and not self.crashed:
    if keyboard.check('up') and self.fuel > 0:
        self.vspeed -= self.thrust_force
        self.fuel -= self.fuel_use
        if self.fuel < 0:
            self.fuel = 0

    if keyboard.check('left'):
        self.hspeed -= 0.05
    if keyboard.check('right'):
        self.hspeed += 0.05

    # Обмежити максимальну швидкість
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Не дає модулю зісковзнути за краї або вище room
    room = game.current_room
    if self.x < 16:
        self.x = 16
        self.hspeed = 0
    if self.x > room.width - 16:
        self.x = room.width - 16
        self.hspeed = 0
    if self.y < 16:
        self.y = 16
        self.vspeed = 0
```

Увесь блок обгорнуто в `if not self.landed and not self.crashed:`, щоб
тяга й кермування зупинялися в мить, коли гра завершується — об'єкт `self`
не має способу вийти з події на півдорозі (немає `exit` у стилі GML), тож
`if` навколо решти коду робить те саме.

### 5.3 Зіткнення з Посадковим Майданчиком

**Подія: Collision with obj_pad**
1. Додайте дію **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — швидкість посадки це довжина вектора швидкості; Піфагор, а не
     змінна `speed` (у цьому рушії `speed` це *швидкість анімації
     спрайта*, а не величина руху — справжня пастка для тих, хто прийшов
     з GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        не дає гравітації знову тихо накопичувати вертикальну швидкість у
        вже приземленого модуля
     4. **Output** → **Show Message** (Message: `Perfect Landing! You Win!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

Текст Show Message — це фіксований рядок, у нього не можна вбудувати
реальну швидкість посадки. HUD (Крок 7) уже показує живу швидкість аж до
моменту дотику, тож гравець уже бачив це число.

### 5.4 Зіткнення із Землею

**Подія: Collision with obj_ground**
1. Додайте дію **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Додайте дію **Output** → **Show Message** (Message: `Crashed into terrain!`)
3. Додайте дію **Room** → **Restart Room**

![obj_lander's Object Events panel: Create (Set Gravity + Execute Code), Step (Execute Code), Collision with obj_pad (the Test Expression landing check), Collision with obj_ground (Set Variable + Show Message + Restart Room)](images/tutorial-lunarlander-05-lander-object.png)

---

## Крок 6: Створити Об'єкт Полум'я (Необов'язково)

Візуальний відгук під час тяги.

1. Створіть новий об'єкт з назвою `obj_flame`
2. Встановіть спрайт `spr_flame`

Його створюватиме модуль під час тяги (просунута функція). Для простішого
підходу можна малювати полум'я в події Draw модуля.

![obj_flame's Object Events panel: empty -- it just needs the spr_flame sprite](images/tutorial-lunarlander-06-flame-object.png)

---

## Крок 7: Створити Ігровий Контролер

Ігровий контролер відображає пальне, швидкість та інструкції, зчитуючи їх
з екземпляра модуля на кожному кадрі.

1. Створіть новий об'єкт з назвою `obj_game_controller`
2. Спрайт не потрібен

**Подія: Draw**
1. Додайте дію **Control** → **Execute Code** — знаходить модуль та
   обчислює значення, які покажуть дії Draw нижче:

```python
lander = None
for inst in game.current_room.instances:
    if inst.object_name == 'obj_lander':
        lander = inst
        break

if lander is not None:
    self.fuel_display = round(lander.fuel)
    self.speed_display = round((lander.hspeed ** 2 + lander.vspeed ** 2) ** 0.5, 2)
    self.too_fast = self.speed_display > lander.safe_speed
    self.no_fuel = lander.fuel <= 0
else:
    self.fuel_display = 0
    self.speed_display = 0.0
    self.too_fast = False
    self.no_fuel = False
```

2. Додайте дію **Game** → **Set Draw Color** (Color: `#FFFFFF`)
3. Додайте дію **Game** → **Draw Text** (Text: `LUNAR LANDER`, X: `10`, Y: `10`)
4. Додайте дію **Game** → **Draw Text** (Text: `Fuel:`, X: `10`, Y: `30`)
5. Додайте дію **Game** → **Draw Variable** (Variable: `self.fuel_display`, X: `70`, Y: `30`)
6. Додайте дію **Game** → **Draw Text** (Text: `Speed:`, X: `10`, Y: `50`)
7. Додайте дію **Game** → **Draw Variable** (Variable: `self.speed_display`, X: `70`, Y: `50`)
8. Додайте дію **Game** → **Draw Text** (Text: `Safe Speed: < 2`, X: `10`, Y: `70`)

Потім два рядки попереджень, кожен під керуванням **Control** → **Test
Expression** (Else не потрібен — нічого не малюється, коли умова хибна):

9. **Control** → **Test Expression** (Expression: `self.too_fast`)
   - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions: **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression: `self.no_fuel`)
    - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Додайте дію **Game** → **Set Draw Color** (Color: `#808080`)
12. Додайте дію **Game** → **Draw Text** (Text: `UP: Thrust | LEFT/RIGHT: Move`,
    X: `10`, Y: `440`) — виберіть Y ближче до низу того розміру room,
    який ви використовуєте на Кроці 8.

![obj_game_controller's Object Events panel: a Draw event with 12 actions -- the Execute Code HUD-value calculation, then the Set Draw Color / Draw Text / Draw Variable chain and the two Test Expression warning blocks -- with no sprite set](images/tutorial-lunarlander-07-controller-object.png)

---

## Крок 8: Спроектувати Свій Рівень

1. Клацніть правою кнопкою на **Rooms** та виберіть **Create Room**
2. Назвіть її `room_game`
3. Задайте розмір room (наприклад, 640x480)
4. Встановіть колір фону чорним (космос)

### Розміщення Об'єктів

Будуйте рівень за цими рекомендаціями:

1. **Земля** — Розмістіть `obj_ground` уздовж низу, щоб створити рельєф
2. **Посадковий майданчик** — Розмістіть `obj_pad` у прогалині рельєфу
3. **Модуль** — Розмістіть `obj_lander` угорі room
4. **Ігровий контролер** — Розмістіть `obj_game_controller` будь-де

### Приклад Компонування Рівня

```
    L                          <- Модуль починає тут




GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Земля    L = Модуль    P = Посадковий майданчик
```

![The Room Editor for room_game: a solid terrain row along the bottom with rocky chunks above it, a yellow landing pad in a clear gap, the white lander near the top-left, and the obj_game_controller marker near the top-right, all on a black space background](images/tutorial-lunarlander-08-room.png)

---

## Крок 9: Протестуйте Свою Гру!

1. Натисніть **Запустити** або клавішу **F5** для перевірки
2. Використовуйте стрілку **ВГОРУ** для тяги (стежте за пальним!)
3. Використовуйте стрілки **ВЛІВО/ВПРАВО** для кермування
4. М'яко приземліться на майданчик (швидкість має бути менше 2)
5. Уникайте кам'янистого рельєфу!

---

## Покращення (Необов'язково)

### Додати Керування Обертанням

Замість руху вліво/вправо обертайте модуль і давайте тягу в напрямку,
куди він дивиться. Екземпляри цього рушія мають справжній атрибут
`rotation` (градуси, 0 = праворуч, зростає проти годинникової стрілки),
що використовується для обертання спрайта — не потрібні
`image_angle`/`lengthdir_x`/`lengthdir_y`, оскільки `math` уже доступний у
Execute Code:

Замініть код події Create з 5.1 на:
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # спрямований угору
self.rotation_speed = 3
```

Замініть рядки кермування з 5.2 (блок `left`/`right` → `hspeed`) на:
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

І замініть рядки тяги на:
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(`-=` у `vspeed` відповідає коду гравітації самого рушія — вісь Y екрана
зростає вниз, тож «вгору» це від'ємна вертикальна швидкість).

### Додати Кілька Посадкових Майданчиків

Створіть майданчики різного розміру з різною цінністю в очках:
- Малий майданчик = 100 очок (складніше)
- Великий майданчик = 50 очок (легше)

### Додати Підбори Пального

1. Створіть `obj_fuel`, що ширяє в повітрі
2. Під час зіткнення з модулем додайте пальне та знищіть об'єкт

### Додати Рівні

Створіть кілька room із дедалі складнішим рельєфом і меншими посадковими
майданчиками.

### Додати Вітер

Додайте невеликий сталий горизонтальний поштовх. У коді події Create
об'єкта `obj_lander` додайте `self.wind_force = 0.02`; потім на початку
блоку `if not self.landed and not self.crashed:` події Step додайте:
```python
self.hspeed += self.wind_force
```

---

## Усунення Несправностей

| Проблема | Рішення |
|----------|---------|
| Модуль падає надто швидко | Зменште значення `Gravity` в Set Gravity або збільште `thrust_force` у коді події Create |
| Не вдається достатньо загальмувати | Збільште `thrust_force` або збільште `safe_speed` |
| Пальне закінчується надто швидко | Зменште `fuel_use` або збільште початкове `fuel` |
| Модуль виходить за екран | Перевірте блок меж у кінці коду події Step |
| Посадка не зараховується | Переконайтеся, що в `obj_pad` позначено "Solid" |

---

## Що Ви Навчились

Вітаємо! Ви створили гру про посадку на Місяць! Ви навчились:

- **Фізика тяги** — Підштовхування `self.vspeed` проти неперервного притягання Set Gravity
- **Керування швидкістю** — Обчислення швидкості з `hspeed`/`vspeed` за теоремою Піфагора
- **Система пального** — Ігровий процес керування ресурсом із простою змінною екземпляра
- **Виявлення зіткнень** — Різні результати для майданчика та землі, обрані за допомогою Test Expression
- **Відображення HUD** — Обчислення значень для показу в Execute Code, потім показ їх за допомогою Draw Text/Draw Variable

---

## Ідеї для Випробувань

1. **Реалістичне Обертання** — Обертатися та давати тягу в напрямку погляду
2. **Кілька Рівнів** — Дедалі складніший рельєф
3. **Система Очок** — Очки залежно від залишку пального та точності посадки
4. **Астероїди** — Додати рухомі перешкоди для ухилення
5. **Режим на Двох Гравців** — Перегони, хто приземлиться першим

---

## Дивіться Також

- [Посібники](Tutorials_uk) - Більше посібників з ігор
- [Середній Пресет](Intermediate-Preset_uk) - Огляд пресета, який потрібен цьому посібнику
- [Посібник: Платформер](Tutorial-Platformer_uk) - Створити гру з стрибками по платформах
- [Посібник: Лабіринт](Tutorial-Maze_uk) - Створити гру навігації лабіринтом
- [Довідник Подій](Event-Reference_uk) - Повна документація подій
