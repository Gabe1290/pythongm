# Vodiči: Ustvari Sokoban Puzzle Igro

> **Izberi svoj jezik / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Uvod

V tem vodiču boš ustvaril **Sokoban** puzzle igro - klasično igro potiskanja skrinje, kjer mora igralec potisniti vse kraje na ciljne lokacije. Sokoban (kar v japonščini pomeni "varaždinski čuvar") je odličen za učenje gibanja na mreži in logike puzzle iger.

**Kaj se boš naučil:**
- Gibanje na mreži (premikanje v fiksnih korakih)
- Mehanika potiskanja za premikanje objektov
- Zaznavanje trkov z več vrstami objektov
- Zaznavanje zmage
- Oblikovanje nivojev za puzzle igre

**Težavnost:** Začetnik
**Prednastavka:** Beginner Preset

---

## Korak 1: Razumevanje Igre

### Pravila Igre
1. Igralec se lahko premika gor, dol, levo ali desno
2. Igralec lahko potiska kraje (vendar jih ne more vlačiti)
3. Naenkrat je mogoče potisniti samo eno škatlico
4. Škatle ne smejo biti potiskane skozi stene ali druge škatle
5. Nivo je dokončan, ko so vse škatle na ciljnih lokacijah

### Kaj Potrebujemo

| Element | Namen |
|---------|---------|
| **Igralec** | Skladiščni čuvar, ki ga nadzoruješ |
| **Škatlica** | Škatle, ki jih igralec potiska |
| **Stena** | Trdne ovire, ki blokirajo gibanje |
| **Cilj** | Ciljna polja, kamor morajo biti postavljene škatle |
| **Tla** | Hodljivo tlo (opciono vizualno) |

---

## Korak 2: Utvari Sprite-e

Vsi sprite-i bi morali biti enake velikosti (dobro deluje 32x32 pikslov), da je mogoče ustvariti pravilno mrežo.

### 2.1 Sprite Igralca

1. V **Resource Tree** (Drevo virov), desno klikni na **Sprites** in izberi **Create Sprite** (Ustvari Sprite)
2. Imenuj ga `spr_player`
3. Klikni **Edit Sprite** (Uredi Sprite) za odpiranje urejevalnika sprite-ov
4. Nariši preprost lik (osebo ali robota)
5. Uporabi značilno barvo, kot je modra ali zelena
6. Velikost: 32x32 pikslov
7. Klikni **OK** za shranjevanje

### 2.2 Sprite Škatlice

1. Ustvari nov sprite z imenom `spr_crate`
2. Nariši leseno škatlico ali obliko škatle
3. Uporabi rjave ali oranžne barve
4. Velikost: 32x32 pikslov

### 2.3 Sprite Škatlice na Cilju

1. Ustvari nov sprite z imenom `spr_crate_ok`
2. Nariši isto škatlico, vendar z drugačno barvo (zeleno), da pokažeš, da je pravilno postavljena
3. Velikost: 32x32 pikslov

### 2.4 Sprite Stene

1. Ustvari nov sprite z imenom `spr_wall`
2. Nariši vzorec trdne opeke ali kamna
3. Uporabi sive ali temne barve
4. Velikost: 32x32 pikslov

### 2.5 Sprite Cilja

1. Ustvari nov sprite z imenom `spr_target`
2. Nariši X oznako ali kazalnik cilja
3. Uporabi svetlo barvo, kot je rdeča ali rumena
4. Velikost: 32x32 pikslov

### 2.6 Sprite Tal (Opciono)

1. Ustvari nov sprite z imenom `spr_floor`
2. Nariši preprost vzorec ploščice tal
3. Uporabi nevtralno barvo
4. Velikost: 32x32 pikslov

---

## Korak 3: Ustvari Objekt Stene

Stena je najpreprostejši predmet - samo blokira gibanje.

1. Desno klikni na **Objects** (Objekti) in izberi **Create Object** (Ustvari Objekt)
2. Imenuj ga `obj_wall`
3. Nastavi sprite na `spr_wall`
4. **Označi polje "Solid" (Trd)**
5. Ni potrebnih dogodkov

---

## Korak 4: Ustvari Objekt Cilja

Cilji označujejo, kamor morajo biti postavljene škatle.

1. Ustvari nov objekt z imenom `obj_target`
2. Nastavi sprite na `spr_target`
3. Ni potrebnih dogodkov - to je samo oznaka
4. Pusti "Solid" neoznačeno (igralec in škatle so lahko na vrhu)

---

## Korak 5: Ustvari Objekt Škatlice

Škatlica je potisnjena s strani igralca in spremeni videz, ko je na cilju.

1. Ustvari nov objekt z imenom `obj_crate`
2. Nastavi sprite na `spr_crate`
3. **Označi polje "Solid" (Trd)**

**Dogodek: Step (Korak)**
1. Dodaj Dogodek → Step → Step
2. Dodaj Akcijo: **Control** (Nadzor) → **Test Variable** (Testiraj Spremenljivko)
   - Variable (Spremenljivka): `place_meeting(x, y, obj_target)`
   - Value (Vrednost): `1`
   - Operation (Operacija): Equal to (Enako)
3. Dodaj Akcijo: **Main1** → **Change Sprite** (Spremeni Sprite)
   - Sprite: `spr_crate_ok`
   - Subimage: `0`
   - Speed (Hitrost): `1`
4. Dodaj Akcijo: **Control** (Nadzor) → **Else** (Sicer)
5. Dodaj Akcijo: **Main1** → **Change Sprite** (Spremeni Sprite)
   - Sprite: `spr_crate`
   - Subimage: `0`
   - Speed (Hitrost): `1`

To naredi, da postane škatlica zelena, ko je na ciljnem polju.

---

## Korak 6: Ustvari Objekt Igralca

Igralec je najbolj zapleten predmet z gibanjem na mreži in mehaniko potiskanja.

1. Ustvari nov objekt z imenom `obj_player`
2. Nastavi sprite na `spr_player`

### 6.1 Premikanje Desno

**Dogodek: Keyboard Press Right Arrow (Tipka Desna Puščica)**
1. Dodaj Dogodek → Keyboard → Press Right (Pritisnjena Desna)

Najprej preverite, ali je v poti stena:
2. Dodaj Akcijo: **Control** (Nadzor) → **Test Collision** (Testiraj Trk)
   - Object (Objekt): `obj_wall`
   - X: `32`
   - Y: `0`
   - Check (Preveri): NOT (kar pomeni "če NI stene")

Če ni stene, preverite, ali je tam škatlica:
3. Dodaj Akcijo: **Control** (Nadzor) → **Test Collision** (Testiraj Trk)
   - Object (Objekt): `obj_crate`
   - X: `32`
   - Y: `0`

Če je tam škatlica, moramo preveriti, ali jo lahko potisnemo:
4. Dodaj Akcijo: **Control** (Nadzor) → **Test Collision** (Testiraj Trk) (za ciljno lokacijo škatlice)
   - Object (Objekt): `obj_wall`
   - X: `64`
   - Y: `0`
   - Check (Preveri): NOT

5. Dodaj Akcijo: **Control** (Nadzor) → **Test Collision** (Testiraj Trk)
   - Object (Objekt): `obj_crate`
   - X: `64`
   - Y: `0`
   - Check (Preveri): NOT

Če oba preverjanja pripadata, potisnite škatlico:
6. Dodaj Akcijo: **Control** (Nadzor) → **Code Block** (Blok Kode)
```
var crate = instance_place(x + 32, y, obj_crate);
if (crate != noone) {
    crate.x += 32;
}
```

Sedaj premaknite igralca:
7. Dodaj Akcijo: **Move** (Premik) → **Jump to Position** (Preskok na Pozicijo)
   - X: `32`
   - Y: `0`
   - Označi "Relative" (Relativno)

### 6.2 Premikanje Levo

**Dogodek: Keyboard Press Left Arrow (Tipka Leva Puščica)**
Sledite istemu vzorcu kot premikanje desno, vendar uporabite:
- X offset: `-32` za preverjanje stene/škatlice
- X offset: `-64` za preverjanje, ali je mogoče škatlico potisniti
- Premaknite škatlico za `-32`
- Preskok na pozicijo X: `-32`

### 6.3 Premikanje Gor

**Dogodek: Keyboard Press Up Arrow (Tipka Gornja Puščica)**
Sledite istemu vzorcu, vendar z vrednostmi Y:
- Y offset: `-32` za preverjanje
- Y offset: `-64` za ciljno lokacijo škatlice
- Premaknite škatlico za Y: `-32`
- Preskok na pozicijo Y: `-32`

### 6.4 Premikanje Dol

**Dogodek: Keyboard Press Down Arrow (Tipka Spodnja Puščica)**
Uporabite:
- Y offset: `32` za preverjanje
- Y offset: `64` za ciljno lokacijo škatlice
- Premaknite škatlico za Y: `32`
- Preskok na pozicijo Y: `32`

---

## Korak 7: Poenostavljeno Gibanje Igralca (Alternativa)

Če se pristop z bloki zgoraj zdi zapleten, tukaj je preprostejši pristop s kodo za vsako smer:

**Dogodek: Keyboard Press Right Arrow (Tipka Desna Puščica)**
Dodaj Akcijo: **Control** (Nadzor) → **Execute Code** (Izvrši Kodo)
```
// Preverite, ali se lahko premikamo desno
if (!place_meeting(x + 32, y, obj_wall)) {
    // Preverite, ali je tam škatlica
    var crate = instance_place(x + 32, y, obj_crate);
    if (crate != noone) {
        // Je tam škatlica - ali jo lahko potisnemo?
        if (!place_meeting(x + 64, y, obj_wall) && !place_meeting(x + 64, y, obj_crate)) {
            crate.x += 32;
            x += 32;
        }
    } else {
        // Ni škatle, samo se premakni
        x += 32;
    }
}
```

Ponovite za druge smeri s primerno spremenjenim koordinatami.

---

## Korak 8: Ustvari Preverko Pogoja za Zmago

Potrebujemo objekt za preverjanje, ali so vse škatle na ciljnih poljih.

1. Ustvari nov objekt z imenom `obj_game_controller`
2. Sprite ni potreben

**Dogodek: Create (Ustvari)**
1. Dodaj Dogodek → Create
2. Dodaj Akcijo: **Score** (Rezultat) → **Set Variable** (Nastavi Spremenljivko)
   - Variable (Spremenljivka): `global.total_targets`
   - Value (Vrednost): `0`
3. Dodaj Akcijo: **Control** (Nadzor) → **Execute Code** (Izvrši Kodo)
```
// Preštejte, koliko ciljev obstaja
global.total_targets = instance_number(obj_target);
```

**Dogodek: Step (Korak)**
1. Dodaj Dogodek → Step → Step
2. Dodaj Akcijo: **Control** (Nadzor) → **Execute Code** (Izvrši Kodo)
```
// Preštejte škatle, ki so na ciljnih poljih
var crates_on_targets = 0;
with (obj_crate) {
    if (place_meeting(x, y, obj_target)) {
        crates_on_targets += 1;
    }
}

// Preverite, ali imajo vsi cilji škatle
if (crates_on_targets >= global.total_targets && global.total_targets > 0) {
    // Nivo je dokončan!
    show_message("Nivo Dokončan!");
    room_restart();
}
```

**Dogodek: Draw (Risba)**
1. Dodaj Dogodek → Draw
2. Dodaj Akcijo: **Draw** (Riši) → **Draw Text** (Riši Besedilo)
   - Text (Besedilo): `Sokoban - Potisni vse škatle na ciljna polja!`
   - X: `10`
   - Y: `10`

---

## Korak 9: Oblikuj Svoj Nivo

1. Desno klikni na **Rooms** (Sobe) in izberi **Create Room** (Ustvari Sobo)
2. Imenuj ga `room_level1`
3. Nastavi velikost sobe na večkratnik 32 (npr. 640x480)
4. Omogoči "Snap to Grid" (Pripni na Mrežo) in nastavi mrežo na 32x32

### Postavljanje Objektov

Zgradite svoj nivo po naslednjih smernicah:

1. **Obdajte nivo s stenami** - Ustvari mejo
2. **Dodajte notranje stene** - Ustvari strukturo puzzle-a
3. **Postavite ciljna polja** - Kamor morajo iti škatle
4. **Postavite škatle** - Enako število kot ciljev!
5. **Postavite igralca** - Začetna pozicija
6. **Postavite krmilnik igre** - Kjerkoli (nevidna je)

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
C = Škatlica
T = Cilj
. = Prazna tla
```

**Pomembno:** Vedno imej enako število škatic in ciljev!

---

## Korak 10: Testiraj Svojo Igro!

1. Klikni **Run** (Zaženi) ali pritisni **F5** za testiranje
2. Uporabi puščične tipke za premikanje
3. Potisni škatle na rdeče X ciljne oznake
4. Ko so vse škatle na ciljih, zmagaš!

---

## Izboljšave (Opciono)

### Dodaj Števec Potez

V `obj_game_controller`:

**Dogodek: Create (Ustvari)** - Dodaj:
```
global.moves = 0;
```

V `obj_player`, po vsaki uspešni potezi, dodaj:
```
global.moves += 1;
```

V `obj_game_controller` **Dogodek: Draw (Risba)** - Dodaj:
```
draw_text(10, 30, "Poteze: " + string(global.moves));
```

### Dodaj Funkcijo Razveljave

Shrani prejšnje pozicije in dovoli pritisku na Z za razveljavitev zadnje poteze.

### Dodaj Več Nivojev

Ustvari več sob (`room_level2`, `room_level3`, itd.) in uporabi:
```
room_goto_next();
```
namesto `room_restart()`, ko dokončaš nivo.

### Dodaj Zvočne Efekte

Dodaj zvoke za:
- Premikanje igralca
- Potiskanje škatlice
- Škatlico, ki pristane na cilju
- Nivo je dokončan

---

## Odpravljanje Napak

| Problem | Rešitev |
|---------|----------|
| Igralec se premika skozi stene | Preverite, da ima `obj_wall` označeno "Solid" |
| Škatlica ne spremeni barve | Preverite, da dogodek Step pravilno preverja `place_meeting` |
| Lahko potisnete škatlico skozi steno | Preverite zaznavanje trkov pred premikanjem škatlice |
| Sporočilo o zmagi se pojavi takoj | Poskrbite, da so ciljna polja postavljena ločeno od škatic |
| Igralec se premika za več kvadratov | Uporabite dogodek Keyboard Press, ne Keyboard |

---

## Kaj Si Se Naučil

Čestitam! Ustvaril si celotno Sokoban puzzle igro! Naučil si se:

- **Gibanje na mreži** - Premikanje v fiksnih korakih 32 pikslov
- **Mehanika potiskanja** - Zaznavanje in premikanje objektov, ki jih igralec potiska
- **Zapletena logika trkov** - Preverjanje več pogojev pred dovoljenim gibanjem
- **Spremembe stanja** - Spreminjanje sprite-a na osnovi pozicije objekta
- **Pogoji za zmago** - Preverjanje, kdaj so vsi cilji doseženi
- **Oblikovanje nivojev** - Ustvarjanje rešljivih puzzle postavitev

---

## Izziv: Oblikuj Svoje Nivoje!

Prava zabava Sokoban-a je oblikovanje puzzle-ov. Poskusi ustvariti nivoje, ki:
- Začnejo enostavno in postajajo progresivno bolj težki
- Zahtevajo razmišljanje vnaprej
- Imajo samo eno rešitev
- Učinkovito uporabljajo minimalen prostor

Spomnite se: Dober Sokoban puzzle bi moral biti zahteven, a pošten!

---

## Glej Tudi

- [Vodiči](Tutorials_sl) - Več game vodičev
- [Beginner Preset](Beginner-Preset_sl) - Pregled funkcij za začetnike
- [Vodiči: Pong](Tutorial-Pong_sl) - Ustvari igro za dva igralca
- [Vodiči: Breakout](Tutorial-Breakout_sl) - Ustvari igro razbijanja opek
- [Referenca Dogodkov](Event-Reference_sl) - Popolna dokumentacija dogodkov
