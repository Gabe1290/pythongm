# Vodič: Ustvari Sokoban Puzzle Igro

> **Izberi svoj jezik / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Uvod

V tem vodiču boš ustvaril **Sokoban** puzzle igro - klasično igro potiskanja skrinj, kjer mora igralec potisniti vse zaboje na ciljne lokacije. Sokoban (kar v japonščini pomeni "skladiščnik") je odličen za učenje gibanja na mreži in logike puzzle iger.

**Kaj se boš naučil:**
- Gibanje na mreži (premikanje v fiksnih korakih)
- Mehaniko potiskanja za premikanje objektov
- Zaznavanje trkov z več vrstami objektov
- Zaznavanje pogoja za zmago
- Oblikovanje nivojev za puzzle igre

**Težavnost:** Začetnik
**Prednastavitev:** Srednja prednastavitev (mehanika potiskanja in
gibanje na mreži, uporabljena tukaj, nista del prednastavitve za
začetnike)

---

## Korak 1: Razumevanje Igre

### Pravila Igre
1. Igralec se lahko premika gor, dol, levo ali desno
2. Igralec lahko potiska zaboje (vendar jih ne more vleči)
3. Naenkrat je mogoče potisniti samo en zaboj
4. Zaboji ne smejo biti potisnjeni skozi stene ali druge zaboje
5. Nivo je dokončan, ko so vsi zaboji na ciljnih lokacijah

### Kaj Potrebujemo

| Element | Namen |
|---------|---------|
| **Igralec** | Skladiščnik, ki ga upravljaš |
| **Zaboj** | Zaboji, ki jih igralec potiska |
| **Stena** | Trdne ovire, ki blokirajo gibanje |
| **Cilj** | Ciljna polja, kamor morajo biti postavljeni zaboji |
| **Tla** | Hodljiva podlaga (opcijsko vizualno) |

---

## Korak 2: Ustvari Sprite-e

Vsi sprite-i naj bodo enake velikosti (32x32 pikslov dobro deluje), da ustvariš pravilno mrežo.

### 2.1 Sprite Igralca

1. V **Drevesu virov** desno klikni na **Sprites** in izberi **Create Sprite**
2. Poimenuj ga `spr_player`
3. Klikni **Edit Sprite**, da odpreš urejevalnik sprite-ov
4. Nariši preprost lik (osebo ali robota)
5. Uporabi značilno barvo, kot je modra ali zelena
6. Velikost: 32x32 pikslov
7. Klikni **OK**, da shraniš

### 2.2 Sprite Zaboja

1. Ustvari nov sprite z imenom `spr_crate`
2. Nariši leseno škatlo ali obliko zaboja
3. Uporabi rjavo ali oranžno barvo
4. Velikost: 32x32 pikslov

### 2.3 Sprite Zaboja na Cilju

1. Ustvari nov sprite z imenom `spr_crate_ok`
2. Nariši isti zaboj, vendar z drugačno barvo (zeleno), da pokažeš, da je pravilno postavljen
3. Velikost: 32x32 pikslov

### 2.4 Sprite Stene

1. Ustvari nov sprite z imenom `spr_wall`
2. Nariši vzorec trdne opeke ali kamna
3. Uporabi sivo ali temno barvo
4. Velikost: 32x32 pikslov

### 2.5 Sprite Cilja

1. Ustvari nov sprite z imenom `spr_target`
2. Nariši oznako X ali kazalnik cilja
3. Uporabi svetlo barvo, kot je rdeča ali rumena
4. Velikost: 32x32 pikslov

### 2.6 Sprite Tal (Opcijsko)

1. Ustvari nov sprite z imenom `spr_floor`
2. Nariši preprost vzorec talne ploščice
3. Uporabi nevtralno barvo
4. Velikost: 32x32 pikslov

---

## Korak 3: Ustvari Objekt Stena

Stena je najpreprostejši objekt - samo blokira gibanje.

1. Desno klikni na **Objects** in izberi **Create Object**
2. Poimenuj ga `obj_wall`
3. Nastavi sprite na `spr_wall`
4. **Označi polje "Solid"**
5. Ni potrebnih dogodkov

---

## Korak 4: Ustvari Objekt Cilj

Cilji označujejo, kamor morajo biti postavljeni zaboji.

1. Ustvari nov objekt z imenom `obj_target`
2. Nastavi sprite na `spr_target`
3. Ni potrebnih dogodkov - to je samo oznaka
4. Pusti "Solid" neoznačeno (igralec in zaboji so lahko na njem)

---

## Korak 5: Ustvari Objekt Zaboj

Zaboj potiska igralec in spremeni videz, ko je na cilju.

1. Ustvari nov objekt z imenom `obj_crate`
2. Nastavi sprite na `spr_crate`
3. **Označi polje "Solid"**

**Dogodek: Step**
1. Add Event → Step → Step
2. Add Action: **Control** → **If Collision**
   - X Offset: `0`
   - Y Offset: `0`
   - Against: `obj_target`
3. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate_ok`
4. Add Action: **Control** → **Else**
5. Add Action: **Instance** → **Set Sprite**
   - Sprite: `spr_crate`

Zaboj tako postane zelen, ko je na ciljnem polju — **If Collision** z
obema odmikoma na `0` preveri, ali se *trenutni* položaj zaboja
prekriva z `obj_target`.

---

## Korak 6: Ustvari Objekt Igralec

Igralec se premakne natanko za eno celico mreže naenkrat in potisne zaboje, ob katere se dotakne.

1. Ustvari nov objekt z imenom `obj_player`
2. Nastavi sprite na `spr_player`

### 6.1 Gibanje na Mreži

Dodaj po en dogodek **Key Press** za vsako smer, vsakega z akcijo **Move** → **Move Grid**:

| Dogodek | Akcija Move Grid |
|---|---|
| Key Press → Right Arrow | Direction: `right`, Grid Size: `32` |
| Key Press → Left Arrow | Direction: `left`, Grid Size: `32` |
| Key Press → Up Arrow | Direction: `up`, Grid Size: `32` |
| Key Press → Down Arrow | Direction: `down`, Grid Size: `32` |

**Move Grid** premakne instanco natanko za eno celico mreže in sama
zaznava trke — igralca ne bo premaknila v trdno steno `obj_wall`,
zato dodatno preverjanje stene tukaj ni potrebno.

### 6.2 Ustavljanje ob Stenah

**Dogodek: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

### 6.3 Potiskanje Zabojev

**Dogodek: Collision with obj_crate**
1. Add Event → Collision → `obj_crate`
2. Add Action: **Control** → **If Can Push**
   - Direction: `facing`
   - Object Type: `obj_crate`
   - Then Action: `push_and_move`

**If Can Push** preveri, ali je prostor za zabojem (v smeri, v katero
se premika igralec) prost, in če je, potisne zaboj za eno celico ter
premakne igralca na njegovo mesto, vse v eni sami akciji. Če je
prostor za zabojem blokiran s steno ali drugim zabojem, se nič ne
premakne.

---

## Korak 7: Ustvari Preverjanje Pogoja za Zmago

Potrebujemo nevidni krmilnik, ki opazuje, ali je vsak zaboj na cilju.

1. Ustvari nov objekt z imenom `obj_game_controller`
2. Sprite ni potreben

**Dogodek: Create** — enkratno nastavi štetje ciljev, z uporabo
**Control** → **Execute Code** (akcija Execute Code v tem projektu
izvede pravi Python, ne GameMaker Language — `self` je trenutna
instanca, `game` je izvajalec igre):

```python
# Prešteje, koliko ciljev obstaja v sobi
self.total_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_target'
)
```

**Dogodek: Step** — vsak sličico preveri, ali so vsi zaboji na cilju:

```python
# Prešteje zaboje, ki se trenutno prekrivajo s ciljem
crates_on_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_crate'
    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')
)

if self.total_targets > 0 and crates_on_targets >= self.total_targets:
    self.restart_room_flag = True
```

`self.restart_room_flag = True` je način, kako surov blok Execute
Code sproži isti ponovni zagon sobe, kot ga izvede akcija **Restart
Room** — glavna zanka to preveri vsak sličico. Če želiš pred ponovnim
zagonom prikazati pojavno okno, takoj za blokom Execute Code dodaj
akcijo **Show Message** (iz **Output**, sporočilo `Level Complete!`).

**Dogodek: Draw**
1. Add Event → Draw
2. Add Action: **Draw** → **Draw Text**
   - Text: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Korak 9: Oblikuj Svoj Nivo

1. Desno klikni na **Rooms** in izberi **Create Room**
2. Poimenuj ga `room_level1`
3. Nastavi velikost sobe na večkratnik 32 (npr. 640x480)
4. Omogoči "Snap to Grid" in nastavi mrežo na 32x32

### Postavljanje Objektov

Zgradi svoj nivo po naslednjih smernicah:

1. **Obdaj nivo s stenami** - Ustvari mejo
2. **Dodaj notranje stene** - Ustvari strukturo uganke
3. **Postavi cilje** - Kamor morajo iti zaboji
4. **Postavi zaboje** - Enako število kot ciljev!
5. **Postavi igralca** - Začetni položaj
6. **Postavi game controller** - Kjerkoli (nevidna je)

### Primer Postavitve Nivoja

```
W W W W W W W W W W
W . . . . . . . . W
W . P . . . C . . W
W . . W W . . . . W
W . . W T . . C . W
W . . . . . W W . W
W . T . . . . . . W
W . . . . . . . . W
W W W W W W W W W W

W = Stena
P = Igralec
C = Zaboj
T = Cilj
. = Prazna tla
```

**Pomembno:** Vedno imej enako število zabojev in ciljev!

---

## Korak 10: Testiraj Svojo Igro!

1. Klikni **Run** ali pritisni **F5** za testiranje
2. Uporabi puščične tipke za premikanje
3. Potisni zaboje na rdeče X cilje
4. Ko so vsi zaboji na ciljih, zmagaš!

---

## Izboljšave (Opcijsko)

### Dodaj Števec Potez

V dogodku **Create** za `obj_game_controller` dodaj **Control** →
**Set Variable** (Variable: `global.moves`, Value: `0`, Scope: `global`).

V vsakem od štirih dogodkov Key Press za `obj_player` dodaj drugo
akcijo takoj za Move Grid: **Control** → **Set Variable** (Variable:
`global.moves`, Value: `1`, Scope: `global`, **Relative** označeno) —
to prišteje 1 k števcu ob vsakem pritisku tipke, ne glede na to, ali je
bil premik dejansko blokiran s steno.

V dogodku **Draw** za `obj_game_controller` dodaj **Draw** →
**Draw Variable** (Variable: `global.moves`, X: `10`, Y: `30`).

### Dodaj Funkcijo Razveljavitve

Shrani prejšnje položaje in omogoči pritisk na Z za razveljavitev zadnje poteze.

### Dodaj Več Nivojev

Ustvari več sob (`room_level2`, `room_level3`, itd.) in v bloku
Execute Code za preverjanje zmage uporabi akcijo **Next Room**
(kategorija Room) namesto **Restart Room** (`self.next_room_flag =
True` namesto `self.restart_room_flag = True`), ko je nivo dokončan.

### Dodaj Zvočne Učinke

Dodaj zvoke za:
- Premikanje igralca
- Potiskanje zaboja
- Zaboj, ki pristane na cilju
- Dokončan nivo

---

## Odpravljanje Napak

| Problem | Rešitev |
|---------|----------|
| Igralec se premika skozi stene | Preveri, da ima `obj_wall` označeno "Solid" |
| Zaboj ne spremeni barve | Preveri, da akcija **If Collision** v dogodku Step cilja na `obj_target` |
| Zaboj lahko potisneš skozi steno | Preveri zaznavanje trkov pred premikanjem zaboja |
| Sporočilo o zmagi se pojavi takoj | Poskrbi, da so cilji postavljeni ločeno od zabojev |
| Igralec se premakne za več polj | Uporabi dogodek Keyboard Press, ne Keyboard |

---

## Kaj Si Se Naučil

Čestitke! Ustvaril si celotno Sokoban puzzle igro! Naučil si se:

- **Gibanje na mreži** - Premikanje v fiksnih korakih po 32 pikslov
- **Mehanika potiskanja** - Zaznavanje in premikanje objektov, ki jih potiska igralec
- **Zapletena logika trkov** - Preverjanje več pogojev pred dovoljenim gibanjem
- **Spremembe stanja** - Spreminjanje sprite-a glede na položaj objekta
- **Pogoji za zmago** - Preverjanje, kdaj so vsi cilji doseženi
- **Oblikovanje nivojev** - Ustvarjanje rešljivih postavitev uganke

---

## Izziv: Oblikuj Svoje Lastne Nivoje!

Prava zabava Sokobana je oblikovanje ugank. Poskusi ustvariti nivoje, ki:
- Se začnejo lahko in postopoma postajajo težji
- Zahtevajo vnaprejšnje načrtovanje
- Imajo samo eno rešitev
- Učinkovito izkoristijo minimalen prostor

Zapomni si: dobra Sokoban uganka naj bo zahtevna, a poštena!

---

## Glej Tudi

- [Vodiči](Tutorials_sl) - Več vodičev za igre
- [Srednja prednastavitev](Intermediate-Preset_sl) - Pregled prednastavitve, potrebne za ta vodič
- [Vodič: Pong](Tutorial-Pong_sl) - Ustvari igro za dva igralca
- [Vodič: Breakout](Tutorial-Breakout_sl) - Ustvari igro razbijanja opek
- [Referenca Dogodkov](Event-Reference_sl) - Popolna dokumentacija dogodkov
