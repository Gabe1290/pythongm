# Vodič: Ustvari Igro Labirinta

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Uvod

V tem vodiču boš ustvaril **Igro Labirinta**, kjer igralec navigira skozi hodnike do izhoda, medtem ko se izogiba oviram in zbira kovance. Ta klasična vrsta igre je odlična za učenje gladkega gibanja, zaznavanja trkov in oblikovanja ravni.

**Kaj se boš naučil:**
- Gladko gibanje igralca s tipkovnico
- Obravnavanje trkov s stenami
- Zaznavanje cilja (doseganje izhoda)
- Zbirateljske predmete
- Preprost sistem časovnika

**Težavnost:** Začetnik
**Prednastavitev:** Srednja prednastavitev (akcija Execute Code,
uporabljena za časovnik, ni del prednastavitve za začetnike)

---

## Korak 1: Razumevanje Igre

### Pravila Igre
1. Igralec se premika skozi labirint s puščičnimi tipkami
2. Stene blokirajo gibanje igralca
3. Zberi kovance za točke
4. Doseži izhod za dokončanje ravni
5. Dokončaj labirint čim hitreje!

### Kaj Potrebujemo

| Element | Namen |
|---------|-------|
| **Igralec** | Lik, ki ga nadziraš |
| **Stena** | Trdne ovire, ki blokirajo gibanje |
| **Izhod** | Cilj, ki konča raven |
| **Kovanec** | Zbirateljski predmeti za točke |
| **Tla** | Vizualno ozadje (neobvezno) |

---

## Korak 2: Ustvari Sprite-e

Vsi sprite-i za stene in tla naj bodo 32x32 pikslov za pravilno mrežo.

### 2.1 Sprite Igralca

1. V **Drevesu Virov** desno klikni na **Sprites** in izberi **Create Sprite**
2. Poimenuj ga `spr_player`
3. Klikni **Edit Sprite** za odpiranje urejevalnika
4. Nariši majhen lik (krog, osebo ali obliko puščice)
5. Uporabi živo barvo, kot je modra ali zelena
6. Velikost: 24x24 pikslov (manjši od sten za lažjo navigacijo)
7. Klikni **OK** za shranjevanje

### 2.2 Sprite Stene

1. Ustvari nov sprite z imenom `spr_wall`
2. Nariši trden vzorec opeke ali kamna
3. Uporabi sivo ali temno barvo
4. Velikost: 32x32 pikslov

### 2.3 Sprite Izhoda

1. Ustvari nov sprite z imenom `spr_exit`
2. Nariši vrata, zastavo ali svetel označevalec cilja
3. Uporabi zeleno ali zlato barvo
4. Velikost: 32x32 pikslov

### 2.4 Sprite Kovanca

1. Ustvari nov sprite z imenom `spr_coin`
2. Nariši majhen rumen/zlat krog
3. Velikost: 16x16 pikslov

### 2.5 Sprite Tal (Neobvezno)

1. Ustvari nov sprite z imenom `spr_floor`
2. Nariši preprost vzorec talnih ploščic
3. Uporabi svetlo nevtralno barvo
4. Velikost: 32x32 pikslov

---

## Korak 3: Ustvari Objekt Stena

Stena blokira gibanje igralca.

1. Desno klikni na **Objects** in izberi **Create Object**
2. Poimenuj ga `obj_wall`
3. Nastavi sprite na `spr_wall`
4. **Označi polje "Solid"**
5. Dogodki niso potrebni

---

## Korak 4: Ustvari Objekt Izhod

Izhod konča raven, ko ga igralec doseže.

1. Ustvari nov objekt z imenom `obj_exit`
2. Nastavi sprite na `spr_exit`

**Dogodek: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Output** → **Show Message**
   - Message: `You Win!`
3. Add Action: **Room** → **Next Room** (ali **Restart Room** za eno raven)

Besedilo Show Message je fiksen niz — ne more vsebovati žive vrednosti,
kot je pretečen čas. Časovnik ostane viden v HUD-u (Korak 7) vse do
zmage, zato je igralec svoj čas že videl.

---

## Korak 5: Ustvari Objekt Kovanec

Kovanci dodajajo k rezultatu, ko so pobrani.

1. Ustvari nov objekt z imenom `obj_coin`
2. Nastavi sprite na `spr_coin`

**Dogodek: Collision with obj_player**
1. Add Event → Collision → obj_player
2. Add Action: **Score** → **Set Score**
   - New Score: `10`
   - Označi "Relative" za dodajanje 10 točk
3. Add Action: **Instance** → **Destroy Instance**
   - Applies to: Self

---

## Korak 6: Ustvari Objekt Igralec

Igralec se gladko premika s puščičnimi tipkami.

1. Ustvari nov objekt z imenom `obj_player`
2. Nastavi sprite na `spr_player`

### 6.1 Gibanje

Dodaj štiri dogodke **Keyboard (held)** in en dogodek **No Key**,
vsakega z akcijo **Move** → **Set Horizontal/Vertical Speed**:

| Dogodek | Akcija |
|---|---|
| Keyboard (held) → Right Arrow | Set Horizontal Speed na `4` |
| Keyboard (held) → Left Arrow | Set Horizontal Speed na `-4` |
| Keyboard (held) → Down Arrow | Set Vertical Speed na `4` |
| Keyboard (held) → Up Arrow | Set Vertical Speed na `-4` |
| Keyboard: No Key | Set Horizontal Speed na `0` **in** Set Vertical Speed na `0` |

### 6.2 Ustavljanje ob Stenah

**Dogodek: Collision with obj_wall**
1. Add Event → Collision → `obj_wall`
2. Add Action: **Move** → **Stop Movement**

Tukaj ni potrebne ročne kode za preverjanje položaja. Gibalna zanka
tega pogona že prepreči, da bi se instanca premaknila v trden objekt,
preden je sličica narisana (`obj_wall` je Solid), zato se igralec
nikoli dejansko ne prekriva s steno — dogodek trka zgoraj samo
izniči morebitno preostalo hitrost, tako da igralec ne "pritiska"
naprej vanjo.

---

## Korak 7: Ustvari Game Controller

Game controller upravlja časovnik in prikazuje informacije.

1. Ustvari nov objekt z imenom `obj_game_controller`
2. Sprite ni potreben

**Dogodek: Create** — zažene časovnik z uporabo **Control** →
**Execute Code** (akcija Execute Code v tem projektu izvede pravi
Python, ne GameMaker Language):

```python
self.timer = 0.0
```

**Dogodek: Step** — poveča ga vsako sličico:

```python
self.timer += 1.0 / game.fps
```

**Dogodek: Draw** — zgradi HUD z resničnimi ukazi vrste za risanje.
Dodaj tri akcije **Draw** → **Draw Text**:

| Akcija Draw Text | Besedilo | Položaj |
|---|---|---|
| 1. | `Score:` | X `10`, Y `10` |
| 2. | `Time:` | X `10`, Y `30` |
| 3. | `Coins:` | X `10`, Y `50` |

nato takoj za njimi tri akcije **Draw** → **Draw Variable**, da
prikažeš žive vrednosti ob vsaki oznaki:

| Akcija Draw Variable | Spremenljivka | Položaj |
|---|---|---|
| 1. | `score` | X `70`, Y `10` |
| 2. | `self.timer` | X `70`, Y `30` |
| 3. | *(glej spodaj)* | X `70`, Y `50` |

Ni vgrajenega števca "preostalih kovancev", na katerega bi kazal Draw
Variable — tik pred akcijami Draw Variable dodaj še eno akcijo
**Control** → **Execute Code**, da ga izračunaš v spremenljivko
instance, ki jo Draw Variable nato lahko prebere:

```python
self.coins_left = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_coin'
)
```

(nato nastavi polje Variable 3. akcije Draw Variable na `self.coins_left`).

---

## Korak 8: Oblikuj Svoj Labirint

1. Desno klikni na **Rooms** in izberi **Create Room**
2. Poimenuj jo `room_maze`
3. Nastavi velikost sobe (npr. 640x480)
4. Omogoči "Snap to Grid" in nastavi mrežo na 32x32

### Postavljanje Objektov

Zgradi svoj labirint po teh smernicah:

1. **Ustvari rob** - Obkroži sobo s stenami
2. **Zgradi hodnike** - Ustvari poti skozi labirint
3. **Postavi izhod** - Postavi ga na konec labirinta
4. **Razporedi kovance** - Postavi jih vzdolž poti
5. **Postavi igralca** - Blizu vhoda
6. **Dodaj game controller** - Kjerkoli (neviden je)

### Primer Postavitve Labirinta

```
W W W W W W W W W W W W W W W W W W W W
W P . . . . W . . . . . . . W . . . . W
W . W W W . W . W W W W W . W . W W . W
W . W . . . . . . . . . . . . . . W . W
W . W . W W W W W . W W W W W W . W . W
W . . . W . . . . . . . . C . W . . . W
W W W . W . W W W W W W W . . W W W . W
W C . . . . W . . . . . W . . . . . . W
W . W W W W W . W W W . W W W W W W . W
W . . . . . . . . C . . . . . . . . . W
W . W W W W W W W W W . W W W W W W . W
W . . . . . . . . . . . W . . . . . . W
W W W W W W W W W W W . W . W W W W . W
W . . . . . . . . . . . . . W . C . E W
W W W W W W W W W W W W W W W W W W W W

W = Stena    P = Igralec    E = Izhod    C = Kovanec    . = Prazno
```

---

## Korak 9: Testiraj Svojo Igro!

1. Klikni **Run** ali pritisni **F5** za testiranje
2. Uporabi puščične tipke za navigacijo skozi labirint
3. Zberi kovance za točke
4. Najdi izhod za zmago!

---

## Izboljšave (Neobvezno)

### Dodaj Sovražnike

Ustvari preprostega patrulirajočega sovražnika:

1. Ustvari `spr_enemy` (rdeča barva, 24x24)
2. Ustvari `obj_enemy` s spritom `spr_enemy`

**Dogodek: Create** — Add Action: **Move** → **Start Moving Direction**
(Directions: `right`, Speed: `2`)

**Dogodek: Collision with obj_wall** — Add Action: **Move** → **Reverse
Horizontal** (obrne sovražnika, ko zadene steno — koda ni potrebna;
skupaj z vgrajenim trdim trkom iz Koraka 6.2 sovražnik nikoli ne more
iti skozi steno)

**Dogodek: Collision with obj_player** — Add Action: **Room** →
**Restart Room**

### Dodaj Sistem Življenj

V dogodku **Create** za `obj_game_controller` dodaj **Score** →
**Set Lives** (Value: `3`).

V dogodku **Collision with obj_player** za `obj_enemy` zamenjaj
**Restart Room** z dvema akcijama: **Score** → **Set Lives** (Value:
`-1`, **Relative** označeno), nato **Move** → **Jump to Start
Position** (uporabljena na igralcu prek **Applies to: Other**), da se
igralec ponovno pojavi namesto ponovnega zagona celega labirinta.

Dodaj `obj_game_controller` še en dogodek: **Other Events** → **No
More Lives** — ta se sproži samodejno takoj, ko življenja dosežejo 0,
zato ga ni treba ročno preverjati. Dodaj **Output** → **Show Message**
(`Game Over!`), nato **Room** → **Restart Game**.

### Dodaj Ključe in Zaklenjena Vrata

1. Ustvari `obj_key` — ob trku z `obj_player`: **Set Variable**
   (Variable: `global.has_key`, Value: `true`, Scope: `global`), nato
   **Destroy Instance** (self).
2. Ustvari `obj_locked_door` z označenim Solid. Dodaj mu dogodek
   **Step** z **Control** → **Test Variable** (Variable:
   `global.has_key`, Value: `true`, Scope: `global`) → **Instance** →
   **Destroy Instance** (self) — vrata izginejo (in prenehajo
   blokirati) takoj, ko je ključ pobran.

### Dodaj Več Ravni

1. Ustvari dodatne sobe (`room_maze2`, `room_maze3`)
2. V `obj_exit` uporabi akcijo **Next Room** namesto **Restart Room**

### Dodaj Zvočne Učinke

Dodaj zvoke za:
- Pobiranje kovancev
- Doseganje izhoda
- Zadevanje sovražnikov (če so dodani)
- Glasbo v ozadju

---

## Odpravljanje Težav

| Težava | Rešitev |
|--------|---------|
| Igralec gre skozi stene | Preveri, da ima `obj_wall` označeno "Solid" |
| Igralec se zatakne v stenah | Poskrbi, da je sprite igralca manjši od vrzeli med stenami |
| Kovanci ne izginejo | Preveri, da dogodek trka uniči Self, ne Other |
| Časovnik ne deluje | Poskrbi, da je game controller postavljen v sobi |
| Gibanje je trzavo | Prilagodi vrednost hitrosti v akcijah Set Horizontal/Vertical Speed (poskusi 3-5) |

---

## Kaj Si Se Naučil

Čestitke! Ustvaril si igro labirinta! Naučil si se:

- **Gladko gibanje** - Preverjanje stanja pridržanih tipk za neprekinjeno gibanje
- **Vgrajeni trdi trk** - Stene samodejno blokirajo gibanje, ko so označene kot Solid, brez ročne kode za preverjanje položaja
- **Zbirateljski predmeti** - Ustvarjanje predmetov, ki povečajo rezultat in izginejo
- **Sistem časovnika** - Sledenje pretečenemu času s spremenljivkami instance
- **Oblikovanje ravni** - Ustvarjanje navigabilnih postavitev labirintov

---

## Ideje za Izzive

1. **Dirka s Časom** - Dodaj odštevalnik. Doseži izhod, preden zmanjka časa!
2. **Popoln Rezultat** - Zahtevaj pobiranje vseh kovancev, preden se izhod odpre
3. **Naključni Labirint** - Raziskuj proceduralno generiranje labirintov
4. **Megla Vojne** - Prikaži samo območje okoli igralca
5. **Minimapa** - Prikaži majhen pregled labirinta

---

## Glej Tudi

- [Vodiči](Tutorials_sl) - Več vodičev za igre
- [Srednja prednastavitev](Intermediate-Preset_sl) - Pregled prednastavitve, potrebne za ta vodič
- [Vodič: Pong](Tutorial-Pong_sl) - Ustvari igro za dva igralca
- [Vodič: Breakout](Tutorial-Breakout_sl) - Ustvari igro razbijanja opek
- [Vodič: Sokoban](Tutorial-Sokoban_sl) - Ustvari uganko s potiskanjem zabojev
- [Referenca Dogodkov](Event-Reference_sl) - Popolna dokumentacija dogodkov
