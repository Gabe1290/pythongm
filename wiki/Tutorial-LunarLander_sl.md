# Vodič: Ustvari Igro Lunarnega Pristanka

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Uvod

V tem vodiču boš ustvaril **Igro Lunarnega Pristanka** - klasično arkadno igro, kjer nadziraš vesoljsko plovilo, ki se spušča na pristajalno ploščad. Upravljati moraš potisk, da uravnotežiš gravitacijo in pristaneš nežno, brez trka. Ta igra je odlična za učenje fizikalnih konceptov, kot so gravitacija, potisk, hitrost in upravljanje goriva.

**Kaj se boš naučil:**
- Fiziko gravitacije in potiska
- Zaznavanje pristanka na podlagi hitrosti
- Sistem upravljanja goriva
- Rotacijski ali smerni nadzor
- Varne pristajalne cone

**Težavnost:** Začetnik
**Prednastavitev:** Srednja prednastavitev (fizika potiska/goriva v
celoti temelji na Execute Code, ki ni del prednastavitve za začetnike)

---

## Korak 1: Razumevanje Igre

### Mehanike Igre
1. Pristajalnik gravitacija vleče navzdol
2. Pritisk GOR uporabi potisk navzgor (porabi gorivo)
3. LEVO/DESNO nadzira rotacijo ali gibanje
4. Pristani nežno na ploščadi za zmago
5. Zaletiš se, če pristaneš prehitro ali zgrešiš ploščad
6. Brez goriva ne moreš upočasniti!

### Kaj Potrebujemo

| Element | Namen |
|---------|-------|
| **Pristajalnik** | Plovilo, ki ga nadziraš |
| **Ploščad** | Varna cona za pristanek |
| **Tla** | Teren, ki povzroči trk |
| **Prikaz Goriva** | Prikazuje preostalo gorivo |
| **Prikaz Hitrosti** | Prikazuje trenutno hitrost |

---

## Korak 2: Ustvari Sprite-e

### Sprite-i
- `spr_lander` (32x32 pikslov) - preprosto plovilo
- `spr_pad` (64x16 pikslov) - pristajalna ploščad
- `spr_ground` (32x32 pikslov) - skalnati teren
- `spr_flame` (16x16 pikslov) - potisni plamen (opcijsko)

---

## Korak 3-4: Ustvari Objekte Tla in Ploščad

**obj_ground** in **obj_pad**: Nastavi sprite, označi "Solid"

---

## Korak 5: Ustvari Objekt Pristajalnik

Pristajalnik je glavni objekt, ki ga upravlja igralec. Za razliko od
drugih gibalnih vodičev tega wikija morajo njegovi kontrolniki
postopoma zbirati hitrost in slediti viru goriva, zato ta objekt bolj
temelji na **Control** → **Execute Code** (pravi Python — `self` je
trenutna instanca, `game` je izvajalec igre, `keyboard.check(name)`
sporoči, ali je tipka pridržana) kot prejšnji gibalni vodiči, a še
vedno uporablja strukturirano akcijo, kjer je to mogoče.

### 5.1 Gravitacija in Začetne Spremenljivke

**Dogodek: Create**
1. Akcija: **Move** → **Set Gravity** (Direction: `270`, Gravity:
   `0.05`) — rahel vlek navzdol; pogon ga samodejno prišteje k
   navpični hitrosti pristajalnika vsako sličico, enako kot v vodiču
   za platforme, le šibkeje.
2. Akcija: **Control** → **Execute Code**:

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Gibalni sistem tega pogona že sledi hitrosti prek `self.hspeed`/
`self.vspeed` in premakne instanco za ta znesek vsako sličico (z
vgrajenim trdim trkom) — ni treba ustvarjati ločenih spremenljivk
`hsp`/`vsp`, kot bi to počela ročna fizikalna simulacija.

### 5.2 Dogodek Step — Potisk in Kontrole

**Dogodek: Step** — Akcija: **Control** → **Execute Code**:

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

    # Omeji najvišjo hitrost
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Prepreči, da bi pristajalnik zdrsnil ven ob straneh ali nad sobo
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

Celoten blok je znotraj `if not self.landed and not self.crashed:`,
tako da se potisk in krmiljenje ustavita v trenutku, ko se igra konča
— objekt nima načina, da bi prekinil dogodek na sredini (ni `exit`
kot v GML); `if` okrog preostale kode opravi enako nalogo.

### 5.3 Trk s Ploščadjo

**Dogodek: Collision with obj_pad**
1. Akcija: **Control** → **Test Expression**
   - Expression: `(self.hspeed**2 + self.vspeed**2)**0.5 <=
     self.safe_speed` — hitrost pristanka je dolžina vektorja hitrosti
     (Pitagorov izrek), ne spremenljivka `speed` (v tem pogonu je
     `speed` *hitrost animacije* sprite-a, ne velikost gibanja — prava
     past za tiste, ki prihajajo iz GameMakerja).
   - Then Actions:
     1. **Control** → **Set Variable** (Variable: `landed`, Value: `true`, Scope: `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction: `270`, Gravity: `0`) —
        prepreči, da bi gravitacija tiho spet nabirala navpično
        hitrost na že pristalem pristajalniku
     4. **Output** → **Show Message** (Message: `Popoln Pristanek! Zmagal si!`)
   - Else Actions:
     1. **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
     2. **Output** → **Show Message** (Message: `Trk! Prehitro!`)
     3. **Room** → **Restart Room**

Besedilo Show Message je fiksen niz — ne more prikazati dejanske
hitrosti pristanka. HUD (Korak 7) že prikazuje živo hitrost vse do
trenutka dotika, zato je igralec številko že videl.

### 5.4 Trk s Tlemi

**Dogodek: Collision with obj_ground**
1. Akcija: **Control** → **Set Variable** (Variable: `crashed`, Value: `true`, Scope: `self`)
2. Akcija: **Output** → **Show Message** (Message: `Trk v teren!`)
3. Akcija: **Room** → **Restart Room**

---

## Korak 6-7: Game Controller

**obj_game_controller** — Dogodek Draw: najde pristajalnik s zanko
skozi `game.current_room.instances` (enak vzorec kot pri števcu
kovancev v vodiču za labirint), izračuna zaokroženo gorivo/hitrost v
**Execute Code**, nato pa ju prikaže z **Draw Text**/**Draw
Variable**; za popolne podrobnosti po akcijah glej [angleško
različico](Tutorial-LunarLander).

---

## Korak 8: Oblikuj Svojo Raven

1. Ustvari `room_game` (640x480)
2. Črno ozadje (vesolje)
3. Postavi tla spodaj z odprtino
4. Postavi ploščad v odprtino
5. Postavi pristajalnik zgoraj
6. Postavi game controller

---

## Kaj Si Se Naučil

- **Fizika potiska** - Prilagajanje `self.vspeed` proti nenehnemu vleku Set Gravity
- **Upravljanje hitrosti** - Izračun hitrosti iz `hspeed`/`vspeed` s Pitagorovim izrekom
- **Sistem goriva** - Upravljanje virov s preprosto spremenljivko instance
- **Zaznavanje trkov** - Različni izidi za ploščad in tla, izbrani s Test Expression

---

## Glej Tudi

- [Vodiči](Tutorials_sl) - Več vodičev
- [Vodič: Platformer](Tutorial-Platformer_sl) - Ustvari platformsko igro
