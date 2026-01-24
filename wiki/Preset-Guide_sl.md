# Vodnik po Prednastavitvah

*[Slovenščina](Preset-Guide_sl) | [Nazaj na Domov](Home_sl)*

PyGameMaker ponuja različne prednastavitve, ki nadzorujejo, kateri dogodki in akcije so na voljo. To pomaga začetnikom, da se osredotočijo na bistvene funkcije, medtem ko izkušenim uporabnikom omogoča dostop do celotnega nabora orodij.

## Izberite Svojo Raven

| Prednastavitev | Primerno Za | Funkcije |
|----------------|-------------|----------|
| [**Začetnik**](Beginner-Preset_sl) | Novi v razvoju iger | 4 dogodki, 17 akcij - Gibanje, trki, rezultat, sobe |
| [**Srednji**](Intermediate-Preset_sl) | Nekaj izkušenj | +4 dogodki, +12 akcij - Življenja, zdravje, zvok, alarmi, risanje |
| **Napreden** | Izkušeni uporabniki | Vsi 40+ dogodki in akcije na voljo |

---

## Dokumentacija Prednastavitev

### Prednastavitve
| Stran | Opis |
|-------|------|
| [Prednastavitev za Začetnike](Beginner-Preset_sl) | 4 dogodki, 17 akcij - Bistvene funkcije |
| [Prednastavitev za Srednje](Intermediate-Preset_sl) | +4 dogodki, +12 akcij - Življenja, zdravje, zvok |

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

**Tipkovnica (Puščične Tipke):**
```
Puščica Levo   → Nastavi Vodoravno Hitrost: -4
Puščica Desno  → Nastavi Vodoravno Hitrost: 4
Puščica Gor    → Nastavi Navpično Hitrost: -4
Puščica Dol    → Nastavi Navpično Hitrost: 4
```

**Trk z obj_coin:**
```
Dodaj Rezultat: 10
Uniči Instanco: other
```

**Trk z obj_wall:**
```
Ustavi Gibanje
```

### 3. Ustvarite Sobo
- Postavite igralca
- Dodajte nekaj kovancev
- Dodajte stene okoli robov

### 4. Zaženite Igro!
Pritisnite gumb Predvajaj za testiranje vaše igre.

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
- [Kako Začeti](Kako_Zaceti_sl) - Namestitev in nastavitev
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Osnovni koncepti
- [Ustvarite Svojo Prvo Igro](Prva_Igra_sl) - Vadnica
