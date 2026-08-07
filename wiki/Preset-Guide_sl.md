# Vodnik po Prednastavitvah

*[Slovenščina](Preset-Guide_sl) | [Nazaj na Domov](Home_sl)*

PyGameMaker ponuja različne prednastavitve, ki nadzorujejo, kateri
dogodki in akcije so na voljo — **tako** v vizualni paleti blokov
Blockly kot v strukturiranem panelu Events/Actions ("Add Event"/"Add
Action"), ki ga uporablja vsak vodič na tem wikiju. To pomaga
začetnikom, da se osredotočijo na bistvene funkcije, medtem ko
izkušenim uporabnikom omogoča dostop do celotnega nabora orodij.

Prednastavitev projekta se določi na dva načina:
**`Preferences > IDE Edition`** izbere privzeto za *nove* projekte
(obstoječi projekti se ob spremembi izdaje nikoli ne spremenijo), in
**`Tools > Configure Action Blocks...`** kadarkoli spremeni
prednastavitev *trenutno odprtega* projekta. Privzeta izdaja IDE-ja je
Začetnik, zato novi projekti čiste namestitve že začnejo s
prednastavitvijo za začetnike.

## Izberite Svojo Raven

| IDE Edition | Primerno Za | Uporabljena prednastavitev |
|----------------|-------------|----------|
| **Začetnik** (privzeto) | Novi uporabniki | [Prednastavitev za Začetnike](Beginner-Preset_sl) — osnovno gibanje, trki, rezultat, sobe |
| **Napredni** | Nekaj izkušenj | [Srednja prednastavitev](Intermediate-Preset_sl) — + življenja, zdravje, zvok, alarmi, gibanje po mreži |
| **Razvoj** | Izkušeni uporabniki | Prednastavitev `full` — vsi dogodki in akcije na voljo |

Upoštevajte, da se imena ne ujemajo 1:1: izdaja "Napredni" uporablja
prednastavitev `intermediate` (ločene "napredne" prednastavitve ni) —
za natančna in vedno posodobljena števila dogodkov in akcij vsake
poglejte [Prednastavitev za Začetnike](Beginner-Preset_sl)/
[Srednjo prednastavitev](Intermediate-Preset_sl).

---

## Dokumentacija Prednastavitev

### Prednastavitve
| Stran | Opis |
|-------|------|
| [Prednastavitev za Začetnike](Beginner-Preset_sl) | Bistvene funkcije — natančna števila na tej strani |
| [Srednja prednastavitev](Intermediate-Preset_sl) | Doda življenja, zdravje, zvok, alarme, gibanje po mreži — natančna števila na tej strani |

### Referenca
| Stran | Opis |
|-------|------|
| [Referenca Dogodkov](Event-Reference_sl) | Popoln seznam vseh dogodkov |
| [Popolna Referenca Akcij](Full-Action-Reference_sl) | Popoln seznam vseh akcij |

---

## Primer za Hiter Začetek

Tukaj je preprosta igra zbiranja kovancev z uporabo samo funkcij za Začetnike:

### 1. Ustvarite Objekte
- `obj_player` - Lik, ki ga upravljate
- `obj_coin` - Zbirni predmeti
- `obj_wall` - Trdne ovire

### 2. Dodajte Dogodke Igralcu

**Keyboard (Arrow Keys):**
```
Left Arrow  → Set Horizontal Speed: -4
Right Arrow → Set Horizontal Speed: 4
Up Arrow    → Set Vertical Speed: -4
Down Arrow  → Set Vertical Speed: 4
```

**Collision with obj_coin:**
```
Add Score: 10
Destroy Instance: other
```

**Collision with obj_wall:**
```
Stop Movement
```

### 3. Ustvarite Sobo
- Postavite igralca
- Dodajte nekaj kovancev
- Dodajte stene okoli robov

### 4. Zaženite Igro!
Pritisnite gumb Play za testiranje vaše igre.

---

## Nasveti za Uspeh

1. **Začnite Preprosto** - Najprej uporabite prednastavitev za Začetnike
2. **Pogosto Testirajte** - Pogosto zaženite igro za odkrivanje težav
3. **Eno Stvar Naenkrat** - Postopoma dodajajte funkcije
4. **Uporabljajte Trke** - Večina igralnih mehanik vključuje dogodke trkov
5. **Berite Dokumentacijo** - Preverite referenčne strani, ko se zatakne

---

## Glejte Tudi

- [Domov](Home_sl) - Glavna stran wikija
- [Kako Začeti](Zacetek_sl) - Namestitev in nastavitev
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Osnovni koncepti
- [Ustvarite Svojo Prvo Igro](Prva_Igra_sl) - Vadnica
- [Vadnica Breakout](Tutorial-Breakout_sl) - Ustvarite klasično igro Breakout
- [Uvod v Ustvarjanje Iger](Getting-Started-Breakout_sl) - Celovita vadnica za začetnike
