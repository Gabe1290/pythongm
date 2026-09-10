# Руководство: Создание Игры про Посадку на Луну

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Введение

В этом руководстве вы создадите **Игру про Посадку на Луну** — классическую аркадную игру, где вы управляете космическим кораблём, спускающимся на посадочную площадку. Вы должны управлять тягой, чтобы противодействовать гравитации, и мягко приземлиться, не разбившись. Эта игра идеально подходит для изучения физических понятий: гравитации, тяги, скорости и управления топливом.

**Что вы узнаете:**
- Физика гравитации и тяги
- Определение посадки по скорости
- Система управления топливом
- Управление вращением или направлением
- Безопасные зоны посадки

**Сложность:** Начинающий
**Пресет:** Пресет для Среднего Уровня (физика тяги/топлива повсюду опирается на Execute Code, которого нет в Пресете для Начинающих)

---

## Шаг 1: Понять Игру

### Механики Игры
1. Модуль притягивается вниз гравитацией
2. Нажатие ВВЕРХ создаёт тягу вверх (расходует топливо)
3. ВЛЕВО/ВПРАВО управляют вращением или движением модуля
4. Мягко приземлитесь на площадку, чтобы победить
5. Крушение, если приземлитесь слишком быстро или промахнётесь мимо площадки
6. Кончится топливо — не сможете затормозить!

### Что Нам Нужно

| Элемент | Назначение |
|---------|------------|
| **Модуль** | Космический корабль, которым вы управляете |
| **Посадочная площадка** | Безопасная зона для посадки |
| **Земля** | Рельеф, вызывающий крушение |
| **Индикатор топлива** | Показывает оставшееся топливо |
| **Индикатор скорости** | Показывает текущую скорость |

---

## Шаг 2: Создать Спрайты

### 2.1 Спрайт Модуля

1. В **Дереве Ресурсов** щёлкните правой кнопкой на **Sprites** и выберите **Create Sprite**
2. Назовите его `spr_lander`
3. Нажмите **Edit Sprite**, чтобы открыть редактор спрайтов
4. Нарисуйте простой космический корабль (треугольник или классическую форму посадочного модуля)
5. Размер: 32x32 пикселя
6. **Важно:** установите начало координат по центру снизу для правильной посадки

### 2.2 Спрайт Посадочной Площадки

1. Создайте новый спрайт с именем `spr_pad`
2. Нарисуйте плоскую платформу с разметкой (как буква «H»)
3. Используйте яркие цвета (жёлтый/зелёный)
4. Размер: 64x16 пикселей

### 2.3 Спрайт Земли

1. Создайте новый спрайт с именем `spr_ground`
2. Нарисуйте каменистый/неровный рельеф
3. Используйте серый/коричневый цвет
4. Размер: 32x32 пикселя

### 2.4 Спрайт Пламени (Необязательно)

1. Создайте новый спрайт с именем `spr_flame`
2. Нарисуйте небольшое пламя/выхлоп
3. Используйте оранжевый/жёлтый цвет
4. Размер: 16x16 пикселей

![The Sprite Editor with spr_lander open, Origin set to Center-Bottom (X 16, Y 32); spr_lander, spr_pad, spr_ground and spr_flame in the resource tree](images/tutorial-lunarlander-02-sprites.png)

---

## Шаг 3: Создать Объект Земли

Земля — это опасный рельеф, вызывающий крушение.

1. Щёлкните правой кнопкой на **Objects** и выберите **Create Object**
2. Назовите его `obj_ground`
3. Установите спрайт `spr_ground`
4. **Поставьте галочку "Solid"**
5. События не нужны

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-lunarlander-03-ground-object.png)

---

## Шаг 4: Создать Объект Посадочной Площадки

Посадочная площадка — это место, где игрок должен безопасно приземлиться.

1. Создайте новый объект с именем `obj_pad`
2. Установите спрайт `spr_pad`
3. **Поставьте галочку "Solid"**
4. События не нужны (столкновение обрабатывает модуль)

![obj_pad's Object Events panel: empty, with Solid checked](images/tutorial-lunarlander-04-pad-object.png)

---

## Шаг 5: Создать Объект Модуля

Модуль — главный объект, которым управляет игрок, с физикой. В отличие от
других руководств по движению в этом вики, его управление должно
постепенно накапливать скорость и отслеживать ресурс топлива, поэтому
этот объект больше опирается на **Control** → **Execute Code** (настоящий
Python — `self` это текущий экземпляр, `game` это движок игры,
`keyboard.check(имя)` сообщает об удерживаемой клавише), чем только на
структурированные действия. Везде, где структурированное действие
справляется, это руководство по-прежнему использует его.

1. Создайте новый объект с именем `obj_lander`
2. Установите спрайт `spr_lander`

### 5.1 Гравитация и Начальные Переменные

**Событие: Create**
1. Добавьте действие **Move** → **Set Gravity** (Direction: `270`, Gravity: `0.05`)
   — лёгкое притяжение вниз; движок автоматически добавляет его к
   вертикальной скорости модуля на каждом шаге, так же как гравитация в
   руководстве Платформер, только слабее.
2. Добавьте действие **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Система движения этого проекта уже отслеживает скорость через
`self.hspeed`/`self.vspeed` и перемещает экземпляр на эту величину на
каждом кадре (со встроенным твёрдым столкновением) — не нужно создавать
отдельные переменные `hsp`/`vsp`, как это делала бы ручная физическая
симуляция.

### 5.2 Событие Step — Тяга и Управление

**Событие: Step** — Добавьте действие **Control** → **Execute Code**:

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

    # Ограничить максимальную скорость
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Не даёт модулю уйти за края или выше room
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

Весь блок обёрнут в `if not self.landed and not self.crashed:`, чтобы тяга
и рулёжка останавливались в тот момент, когда игра заканчивается — у
объекта `self` нет способа выйти из события на полпути (нет `exit` в стиле
GML), поэтому `if` вокруг остального кода делает то же самое.

### 5.3 Столкновение с Посадочной Площадкой

**Событие: Collision with obj_pad**
1. Добавьте действие **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — скорость посадки это длина вектора скорости; Пифагор, а не
     переменная `speed` (в этом движке `speed` это *скорость анимации
     спрайта*, а не величина движения — настоящая ловушка для тех, кто
     пришёл из GameMaker).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        не даёт гравитации снова незаметно накапливать вертикальную
        скорость у уже приземлившегося модуля
     4. **Output** → **Show Message** (Message: `Perfect Landing! You Win!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

Текст Show Message — это фиксированная строка, в неё нельзя встроить
реальную скорость посадки. HUD (Шаг 7) уже показывает живую скорость
вплоть до момента касания, так что игрок уже видел это число.

### 5.4 Столкновение с Землёй

**Событие: Collision with obj_ground**
1. Добавьте действие **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Добавьте действие **Output** → **Show Message** (Message: `Crashed into terrain!`)
3. Добавьте действие **Room** → **Restart Room**

![obj_lander's Object Events panel: Create (Set Gravity + Execute Code), Step (Execute Code), Collision with obj_pad (the Test Expression landing check), Collision with obj_ground (Set Variable + Show Message + Restart Room)](images/tutorial-lunarlander-05-lander-object.png)

---

## Шаг 6: Создать Объект Пламени (Необязательно)

Визуальная обратная связь при тяге.

1. Создайте новый объект с именем `obj_flame`
2. Установите спрайт `spr_flame`

Он будет создаваться модулем при тяге (продвинутая функция). Для более
простого подхода можно рисовать пламя в событии Draw модуля.

![obj_flame's Object Events panel: empty -- it just needs the spr_flame sprite](images/tutorial-lunarlander-06-flame-object.png)

---

## Шаг 7: Создать Игровой Контроллер

Игровой контроллер отображает топливо, скорость и инструкции, считывая их
с экземпляра модуля на каждом кадре.

1. Создайте новый объект с именем `obj_game_controller`
2. Спрайт не нужен

**Событие: Draw**
1. Добавьте действие **Control** → **Execute Code** — находит модуль и
   вычисляет значения, которые покажут действия Draw ниже:

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

2. Добавьте действие **Game** → **Set Draw Color** (Color: `#FFFFFF`)
3. Добавьте действие **Game** → **Draw Text** (Text: `LUNAR LANDER`, X: `10`, Y: `10`)
4. Добавьте действие **Game** → **Draw Text** (Text: `Fuel:`, X: `10`, Y: `30`)
5. Добавьте действие **Game** → **Draw Variable** (Variable: `self.fuel_display`, X: `70`, Y: `30`)
6. Добавьте действие **Game** → **Draw Text** (Text: `Speed:`, X: `10`, Y: `50`)
7. Добавьте действие **Game** → **Draw Variable** (Variable: `self.speed_display`, X: `70`, Y: `50`)
8. Добавьте действие **Game** → **Draw Text** (Text: `Safe Speed: < 2`, X: `10`, Y: `70`)

Затем две строки предупреждений, каждая под управлением **Control** →
**Test Expression** (Else не нужен — ничего не рисуется, когда условие
ложно):

9. **Control** → **Test Expression** (Expression: `self.too_fast`)
   - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions: **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression: `self.no_fuel`)
    - Then Actions: **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Добавьте действие **Game** → **Set Draw Color** (Color: `#808080`)
12. Добавьте действие **Game** → **Draw Text** (Text: `UP: Thrust | LEFT/RIGHT: Move`,
    X: `10`, Y: `440`) — выберите Y ближе к низу того размера room,
    который вы используете на Шаге 8.

![obj_game_controller's Object Events panel: a Draw event with 12 actions -- the Execute Code HUD-value calculation, then the Set Draw Color / Draw Text / Draw Variable chain and the two Test Expression warning blocks -- with no sprite set](images/tutorial-lunarlander-07-controller-object.png)

---

## Шаг 8: Спроектировать Свой Уровень

1. Щёлкните правой кнопкой на **Rooms** и выберите **Create Room**
2. Назовите её `room_game`
3. Задайте размер room (например, 640x480)
4. Установите цвет фона чёрным (космос)

### Размещение Объектов

Стройте уровень по этим рекомендациям:

1. **Земля** — Разместите `obj_ground` вдоль низа, чтобы создать рельеф
2. **Посадочная площадка** — Разместите `obj_pad` в промежутке рельефа
3. **Модуль** — Разместите `obj_lander` вверху room
4. **Игровой контроллер** — Разместите `obj_game_controller` где угодно

### Пример Раскладки Уровня

```
    L                          <- Модуль начинает здесь




GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Земля    L = Модуль    P = Посадочная площадка
```

![The Room Editor for room_game: a solid terrain row along the bottom with rocky chunks above it, a yellow landing pad in a clear gap, the white lander near the top-left, and the obj_game_controller marker near the top-right, all on a black space background](images/tutorial-lunarlander-08-room.png)

---

## Шаг 9: Протестируйте Свою Игру!

1. Нажмите **Запустить** или клавишу **F5** для проверки
2. Используйте стрелку **ВВЕРХ** для тяги (следите за топливом!)
3. Используйте стрелки **ВЛЕВО/ВПРАВО** для рулёжки
4. Мягко приземлитесь на площадку (скорость должна быть меньше 2)
5. Избегайте каменистого рельефа!

---

## Улучшения (Необязательно)

### Добавить Управление Вращением

Вместо движения влево/вправо вращайте модуль и создавайте тягу в
направлении, куда он смотрит. У экземпляров этого движка есть настоящий
атрибут `rotation` (градусы, 0 = вправо, растёт против часовой стрелки),
используемый для поворота спрайта — не нужны
`image_angle`/`lengthdir_x`/`lengthdir_y`, поскольку `math` уже доступен в
Execute Code:

Замените код события Create из 5.1 на:
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # направлен вверх
self.rotation_speed = 3
```

Замените строки рулёжки из 5.2 (блок `left`/`right` → `hspeed`) на:
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

И замените строки тяги на:
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(`-=` у `vspeed` соответствует коду гравитации самого движка — ось Y
экрана растёт вниз, поэтому «вверх» это отрицательная вертикальная
скорость).

### Добавить Несколько Посадочных Площадок

Создайте площадки разного размера с разной ценностью в очках:
- Маленькая площадка = 100 очков (сложнее)
- Большая площадка = 50 очков (легче)

### Добавить Подборы Топлива

1. Создайте `obj_fuel`, который парит в воздухе
2. При столкновении с модулем добавьте топливо и уничтожьте объект

### Добавить Уровни

Создайте несколько room со всё более сложным рельефом и меньшими
посадочными площадками.

### Добавить Ветер

Добавьте небольшой постоянный горизонтальный толчок. В коде события Create
объекта `obj_lander` добавьте `self.wind_force = 0.02`; затем в начале
блока `if not self.landed and not self.crashed:` события Step добавьте:
```python
self.hspeed += self.wind_force
```

---

## Устранение Неполадок

| Проблема | Решение |
|----------|---------|
| Модуль падает слишком быстро | Уменьшите значение `Gravity` в Set Gravity или увеличьте `thrust_force` в коде события Create |
| Не получается достаточно затормозить | Увеличьте `thrust_force` или увеличьте `safe_speed` |
| Топливо кончается слишком быстро | Уменьшите `fuel_use` или увеличьте начальный `fuel` |
| Модуль уходит за экран | Проверьте блок границ в конце кода события Step |
| Посадка не засчитывается | Убедитесь, что у `obj_pad` отмечено "Solid" |

---

## Что Вы Узнали

Поздравляем! Вы создали игру про посадку на Луну! Вы узнали:

- **Физика тяги** — Подталкивание `self.vspeed` против непрерывного притяжения Set Gravity
- **Управление скоростью** — Вычисление скорости из `hspeed`/`vspeed` по теореме Пифагора
- **Топливная система** — Геймплей управления ресурсом с простой переменной экземпляра
- **Определение столкновений** — Разные исходы для площадки и земли, выбираемые с помощью Test Expression
- **Отображение HUD** — Вычисление отображаемых значений в Execute Code, затем показ их с помощью Draw Text/Draw Variable

---

## Идеи для Испытаний

1. **Реалистичное Вращение** — Вращаться и создавать тягу в направлении взгляда
2. **Несколько Уровней** — Всё более сложный рельеф
3. **Система Очков** — Очки в зависимости от оставшегося топлива и точности посадки
4. **Астероиды** — Добавить движущиеся препятствия для уклонения
5. **Режим на Двух Игроков** — Гонка, кто приземлится первым

---

## Смотрите Также

- [Руководства](Tutorials_ru) - Больше руководств по играм
- [Пресет для Среднего Уровня](Intermediate-Preset_ru) - Обзор пресета, который нужен этому руководству
- [Руководство: Платформер](Tutorial-Platformer_ru) - Создать игру с прыжками по платформам
- [Руководство: Лабиринт](Tutorial-Maze_ru) - Создать игру с навигацией по лабиринту
- [Справочник Событий](Event-Reference_ru) - Полная документация по событиям
