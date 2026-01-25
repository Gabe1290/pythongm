# Vadnica: Ustvari Igro Labirinta

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Uvod

V tej vadnici boš ustvaril **Igro Labirinta**, kjer igralec navigira skozi hodnike do izhoda, medtem ko se izogiba oviram in zbira kovance. Ta klasična vrsta igre je popolna za učenje gladkega gibanja, zaznavanja trkov in oblikovanja ravni.

**Kaj se boš naučil:**
- Gladko gibanje igralca s tipkovnico
- Obravnavanje trkov s stenami
- Zaznavanje cilja (doseganje izhoda)
- Zbirateljski predmeti
- Preprost sistem časovnika

**Težavnost:** Začetnik
**Preset:** Začetniški Preset

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

## Korak 2: Ustvari Sprite

Vsi sprite za stene in tla naj bodo 32x32 pikslov za pravilno mrežo.

### 2.1 Sprite Igralca

1. V **Drevesu Virov** desno klikni na **Sprite** in izberi **Ustvari Sprite**
2. Poimenuj ga `spr_player`
3. Klikni **Uredi Sprite** za odpiranje urejevalnika
4. Nariši majhen lik (krog, oseba ali oblika puščice)
5. Uporabi živo barvo kot modra ali zelena
6. Velikost: 24x24 pikslov (manjši od sten za lažjo navigacijo)
7. Klikni **V redu** za shranjevanje

### 2.2 Sprite Stene

1. Ustvari nov sprite imenovan `spr_wall`
2. Nariši trden vzorec opeke ali kamna
3. Uporabi sive ali temne barve
4. Velikost: 32x32 pikslov

### 2.3 Sprite Izhoda

1. Ustvari nov sprite imenovan `spr_exit`
2. Nariši vrata, zastavo ali svetel označevalec cilja
3. Uporabi zelene ali zlate barve
4. Velikost: 32x32 pikslov

### 2.4 Sprite Kovanca

1. Ustvari nov sprite imenovan `spr_coin`
2. Nariši majhen rumeno/zlat krog
3. Velikost: 16x16 pikslov

### 2.5 Sprite Tal (Neobvezno)

1. Ustvari nov sprite imenovan `spr_floor`
2. Nariši preprost vzorec talnih ploščic
3. Uporabi svetlo nevtralno barvo
4. Velikost: 32x32 pikslov

---

## Korak 3: Ustvari Objekt Stene

Stena blokira gibanje igralca.

1. Desno klikni na **Objekti** in izberi **Ustvari Objekt**
2. Poimenuj ga `obj_wall`
3. Nastavi sprite na `spr_wall`
4. **Označi potrditveno polje "Trden"**
5. Dogodki niso potrebni

---

## Korak 4: Ustvari Objekt Izhoda

Izhod konča raven, ko ga igralec doseže.

1. Ustvari nov objekt imenovan `obj_exit`
2. Nastavi sprite na `spr_exit`

**Dogodek: Trk z obj_player**
1. Dodaj Dogodek → Trk → obj_player
2. Dodaj Akcijo: **Main2** → **Prikaži Sporočilo**
   - Sporočilo: `Zmagal si! Čas: ` + string(floor(global.timer)) + ` sekund`
3. Dodaj Akcijo: **Main1** → **Naslednja Soba** (ali **Ponastavi Sobo** za eno raven)

---

## Korak 5: Ustvari Objekt Kovanca

Kovanci dodajajo k rezultatu, ko so pobrani.

1. Ustvari nov objekt imenovan `obj_coin`
2. Nastavi sprite na `spr_coin`

**Dogodek: Trk z obj_player**
1. Dodaj Dogodek → Trk → obj_player
2. Dodaj Akcijo: **Rezultat** → **Nastavi Rezultat**
   - Nov Rezultat: `10`
   - Označi "Relativno" za dodajanje 10 točk
3. Dodaj Akcijo: **Main1** → **Uniči Instanco**
   - Velja za: Self

---

## Korak 6: Ustvari Objekt Igralca

Igralec se gladko premika s puščičnimi tipkami.

1. Ustvari nov objekt imenovan `obj_player`
2. Nastavi sprite na `spr_player`

### 6.1 Dogodek Create - Inicializiraj Spremenljivke

**Dogodek: Create**
1. Dodaj Dogodek → Create
2. Dodaj Akcijo: **Nadzor** → **Nastavi Spremenljivko**
   - Spremenljivka: `move_speed`
   - Vrednost: `4`

### 6.2 Gibanje s Trki

**Dogodek: Step**
1. Dodaj Dogodek → Step → Step
2. Dodaj Akcijo: **Nadzor** → **Izvedi Kodo**

```gml
// Vodoravno gibanje
var hspd = 0;
if (keyboard_check(vk_right)) hspd = move_speed;
if (keyboard_check(vk_left)) hspd = -move_speed;

// Navpično gibanje
var vspd = 0;
if (keyboard_check(vk_down)) vspd = move_speed;
if (keyboard_check(vk_up)) vspd = -move_speed;

// Preverjanje vodoravnega trka
if (!place_meeting(x + hspd, y, obj_wall)) {
    x += hspd;
} else {
    // Premakni se čim bližje steni
    while (!place_meeting(x + sign(hspd), y, obj_wall)) {
        x += sign(hspd);
    }
}

// Preverjanje navpičnega trka
if (!place_meeting(x, y + vspd, obj_wall)) {
    y += vspd;
} else {
    // Premakni se čim bližje steni
    while (!place_meeting(x, y + sign(vspd), obj_wall)) {
        y += sign(vspd);
    }
}
```

### 6.3 Alternativa: Preprosto Gibanje z Bloki

Če raje uporabljaš akcijske bloke namesto kode:

**Dogodek: Tipka Pritisnjena - Desna Puščica**
1. Dodaj Dogodek → Tipkovnica → \<Desno\>
2. Dodaj Akcijo: **Nadzor** → **Testiraj Trk**
   - Objekt: `obj_wall`
   - X: `4`
   - Y: `0`
   - Preveri: NOT
3. Dodaj Akcijo: **Gibanje** → **Skoči na Položaj**
   - X: `4`
   - Y: `0`
   - Označi "Relativno"

Ponovi za Levo (-4, 0), Gor (0, -4) in Dol (0, 4).

---

## Korak 7: Ustvari Nadzornik Igre

Nadzornik igre upravlja časovnik in prikazuje informacije.

1. Ustvari nov objekt imenovan `obj_game_controller`
2. Sprite ni potreben

**Dogodek: Create**
1. Dodaj Dogodek → Create
2. Dodaj Akcijo: **Nadzor** → **Nastavi Spremenljivko**
   - Spremenljivka: `global.timer`
   - Vrednost: `0`

**Dogodek: Step**
1. Dodaj Dogodek → Step → Step
2. Dodaj Akcijo: **Nadzor** → **Nastavi Spremenljivko**
   - Spremenljivka: `global.timer`
   - Vrednost: `1/room_speed`
   - Označi "Relativno"

**Dogodek: Draw**
1. Dodaj Dogodek → Draw → Draw
2. Dodaj Akcijo: **Nadzor** → **Izvedi Kodo**

```gml
// Nariši rezultat
draw_set_color(c_white);
draw_text(10, 10, "Točke: " + string(score));

// Nariši časovnik
draw_text(10, 30, "Čas: " + string(floor(global.timer)) + "s");

// Nariši preostale kovance
var coins_left = instance_number(obj_coin);
draw_text(10, 50, "Kovanci: " + string(coins_left));
```

---

## Korak 8: Oblikuj Svoj Labirint

1. Desno klikni na **Sobe** in izberi **Ustvari Sobo**
2. Poimenuj jo `room_maze`
3. Nastavi velikost sobe (npr. 640x480)
4. Omogoči "Pripni na Mrežo" in nastavi mrežo na 32x32

### Postavljanje Objektov

Zgradi svoj labirint po teh smernicah:

1. **Ustvari rob** - Obkroži sobo s stenami
2. **Zgradi hodnike** - Ustvari poti skozi labirint
3. **Postavi izhod** - Postavi ga na konec labirinta
4. **Razporedi kovance** - Postavi jih vzdolž poti
5. **Postavi igralca** - Blizu vhoda
6. **Dodaj nadzornik igre** - Kjerkoli (neviden je)

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

1. Klikni **Zaženi** ali pritisni **F5** za testiranje
2. Uporabi puščične tipke za navigacijo skozi labirint
3. Zberi kovance za točke
4. Najdi izhod za zmago!

---

## Izboljšave (Neobvezno)

### Dodaj Sovražnike

Ustvari preprostega patrulirajočega sovražnika:

1. Ustvari `spr_enemy` (rdeča barva, 24x24)
2. Ustvari `obj_enemy` s spriteom `spr_enemy`

**Dogodek: Create**
```gml
hspeed = 2;  // Premika se vodoravno
```

**Dogodek: Trk z obj_wall**
```gml
hspeed = -hspeed;  // Obrni smer
```

**Dogodek: Trk z obj_player**
```gml
room_restart();  // Igralec izgubi
```

### Dodaj Sistem Življenj

V dogodku Create `obj_game_controller`:
```gml
global.lives = 3;
```

Ko igralec zadene sovražnika (namesto ponastavitve):
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("Konec igre!");
    game_restart();
} else {
    // Ponovno pojavi igralca na začetku
    obj_player.x = start_x;
    obj_player.y = start_y;
}
```

### Dodaj Ključe in Zaklenjenna Vrata

1. Ustvari `obj_key` - izgine ob pobiranju, nastavi `global.has_key = true`
2. Ustvari `obj_locked_door` - odpre se samo ko `global.has_key == true`

### Dodaj Več Ravni

1. Ustvari dodatne sobe (`room_maze2`, `room_maze3`)
2. V `obj_exit` uporabi `room_goto_next()` namesto `room_restart()`

### Dodaj Zvočne Učinke

Dodaj zvoke za:
- Pobiranje kovancev
- Doseganje izhoda
- Zadevanje sovražnikov (če so dodani)
- Glasba v ozadju

---

## Odpravljanje Težav

| Težava | Rešitev |
|--------|---------|
| Igralec gre skozi stene | Preveri, da ima `obj_wall` označeno "Trden" |
| Igralec se zatakne v stenah | Poskrbi, da je sprite igralca manjši od vrzeli med stenami |
| Kovanci ne izginejo | Preveri, da dogodek trka uniči Self, ne Other |
| Časovnik ne deluje | Poskrbi, da je nadzornik igre postavljen v sobi |
| Gibanje je trgano | Prilagodi vrednost `move_speed` (poskusi 3-5) |

---

## Kaj Si Se Naučil

Čestitke! Ustvaril si igro labirinta! Naučil si se:

- **Gladko gibanje** - Preverjanje stanja pritisnjenih tipk za neprekinjeno gibanje
- **Zaznavanje trkov** - Uporaba `place_meeting` za preverjanje pred premikom
- **Pikselsko natančen trk** - Premikanje čim bližje stenam
- **Zbirateljski predmeti** - Ustvarjanje predmetov, ki povečajo rezultat in izginejo
- **Sistem časovnika** - Sledenje pretečenemu času s spremenljivkami
- **Oblikovanje ravni** - Ustvarjanje navigabilnih postavitev labirintov

---

## Ideje za Izzive

1. **Dirka s Časom** - Dodaj odštevalnik. Doseži izhod preden zmanjka časa!
2. **Popoln Rezultat** - Zahtevaj pobiranje vseh kovancev preden se izhod odpre
3. **Naključni Labirint** - Raziskuj proceduralno generiranje labirintov
4. **Megla Vojne** - Prikaži samo območje okoli igralca
5. **Minimapa** - Prikaži majhen pregled labirinta

---

## Glej Tudi

- [Vadnice](Tutorials_sl) - Več vadnic za igre
- [Začetniški Preset](Beginner-Preset_sl) - Pregled funkcij za začetnike
- [Vadnica: Pong](Tutorial-Pong_sl) - Ustvari igro za dva igralca
- [Vadnica: Breakout](Tutorial-Breakout_sl) - Ustvari igro razbijanja opek
- [Vadnica: Sokoban](Tutorial-Sokoban_sl) - Ustvari uganko s potiskanjem zabojev
- [Referenca Dogodkov](Event-Reference_sl) - Popolna dokumentacija dogodkov
