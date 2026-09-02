# Nadzor

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Preveri, ali je prazno

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `check_empty` |
| **Ikona** | 🔍 |
| **Kategorija** | Nadzor |

Resnično, ko je (x, y) brez trkov. Uporabi s start_block/end_block za pogojevanje naslednjega dejanja/dejanj, v slogu GM

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `self.x` | Položaj X za preverjanje (izraz dovoljen, npr. self.x + 32) |
| `y` | Besedilo | `self.y` | Položaj Y za preverjanje (izraz dovoljen, npr. self.y + 32) |
| `relative` | Da/Ne | Ne | Obravnavaj X/Y kot odmike od položaja te instance namesto absolutnih koordinat; neobvezno |
| `objects` | Izbira | `solid` | Katere instance štejejo kot zasedajoče položaj; Izbire: `solid`, `all` |

### Komentar

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `comment` |
| **Ikona** | ⚠️ |
| **Kategorija** | Nadzor |

Komentar na seznamu dejanj (brez učinka med izvajanjem)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | — | Prosto oblikovano besedilo komentarja; neobvezno |

### Sicer

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `else_action` |
| **Ikona** | ⚡ |
| **Kategorija** | Nadzor |

Označuje vejo »sicer« pogoja

*Parametri:* brez

### Konec bloka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `end_block` |
| **Ikona** | 📁 |
| **Kategorija** | Nadzor |

Končaj blok dejanj

*Parametri:* brez

### Izvedi kodo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `execute_code` |
| **Ikona** | 📜 |
| **Kategorija** | Nadzor |

Izvedi vgrajeni blok kode Python

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `code` | Koda | — | Koda Python za ovrednotenje glede na instanco |

### Izvedi skripto

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `execute_script` |
| **Ikona** | 📜 |
| **Kategorija** | Nadzor |

Izvedi eno od skript projekta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `script` | Skripta | — | Ime skripte projekta za zagon |
| `arg0` | Besedilo | — | Na voljo v skripti kot argument0; neobvezno |
| `arg1` | Besedilo | — | Na voljo v skripti kot argument1; neobvezno |
| `arg2` | Besedilo | — | Na voljo v skripti kot argument2; neobvezno |
| `arg3` | Besedilo | — | Na voljo v skripti kot argument3; neobvezno |
| `arg4` | Besedilo | — | Na voljo v skripti kot argument4; neobvezno |

### Zapusti dogodek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `exit_event` |
| **Ikona** | 🚪 |
| **Kategorija** | Nadzor |

Ustavi izvajanje preostalih dejanj v tem dogodku

*Parametri:* brez

### Če je mogoče potisniti

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_can_push` |
| **Ikona** | 📦 |
| **Kategorija** | Nadzor |

Preveri, ali je mogoče potisniti škatlo/predmet v trenutni smeri (v slogu Sokoban)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Izbira | `facing` | Smer za preverjanje potiska; Izbire: `facing` |
| `object_type` | Besedilo | `box` | Vrsta potisnjenega predmeta |
| `then_action` | Izbira | `push_and_move` | Dejanje, če je potisk mogoč; Izbire: `push_and_move`, `none` |
| `else_action` | Izbira | `stop_movement` | Dejanje, če je potisk blokiran; Izbire: `stop_movement`, `none` |

### Če trk

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_collision` |
| **Ikona** | ❓💥 |
| **Kategorija** | Nadzor |

Pogoj: resnično, če bi instanca trčila pri odmiku (x, y)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Vodoravni odmik za preverjanje |
| `y` | Število | `0` | Navpični odmik za preverjanje |
| `object` | Besedilo | `any` | »any«, »solid« ali ime predmeta; Izbire: `any`, `solid`; neobvezno |
| `not_flag` | Da/Ne | Ne | Zanikaj rezultat; neobvezno |

### Če trk pri

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_collision_at` |
| **Ikona** | 🎯 |
| **Kategorija** | Nadzor |

Preveri trk na položaju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `self.x + 32` | Izraz položaja X |
| `y` | Besedilo | `self.y` | Izraz položaja Y |
| `object_type` | Izbira | `any` | Vrsta predmeta za preverjanje; Izbire: `any`, `solid` |
| `then_actions` | Seznam dejanj | — | Dejanja, če je najden trk |
| `else_actions` | Seznam dejanj | — | Dejanja, če ni trka |

### Če pogoj

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_condition` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Pogojno preverjanje z dejanji potem/sicer

*Parametri:* brez

### Če predmet obstaja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_object_exists` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Pogoj: resnično, če obstaja vsaj ena instanca predmeta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Vrsta predmeta za preverjanje |
| `not_flag` | Da/Ne | Ne | Zanikaj rezultat (ukrepaj, ko predmet NE obstaja); neobvezno |

### Ponovi

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `repeat` |
| **Ikona** | 🔁 |
| **Kategorija** | Nadzor |

Ponovi naslednje dejanje/blok N-krat

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `times` | Število | `10` | Število ponovitev |
| `actions` | Seznam dejanj | — | Dejanja za ponovitev |

### Nastavi spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_variable` |
| **Ikona** | 📝 |
| **Kategorija** | Nadzor |

Nastavi spremenljivko instance ali globalno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `variable` | Besedilo | — | Ime spremenljivke |
| `value` | Besedilo | `0` | Vrednost (število, niz ali izraz) |
| `scope` | Izbira | `self` | Obseg spremenljivke; Izbire: `self`, `other`, `global` |
| `relative` | Da/Ne | Ne | Prištej trenutni vrednosti namesto zamenjave |

### Začetek bloka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_block` |
| **Ikona** | 📂 |
| **Kategorija** | Nadzor |

Začni blok dejanj (za združevanje)

*Parametri:* brez

### Preveri verjetnost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_chance` |
| **Ikona** | 🎲❓ |
| **Kategorija** | Nadzor |

Pogoj: resnično z verjetnostjo 1 od »sides«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sides` | Število | `6` | Verjetnost 1 od N, da je resnično |

### Preveri izraz

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_expression` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Preveri, ali je izraz resničen

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `expression` | Besedilo | — | Izraz za ovrednotenje (resnično, če >= 0.5) |
| `then_actions` | Seznam dejanj | — | Dejanja, če resnično |
| `else_actions` | Seznam dejanj | — | Dejanja, če neresnično |

### Postavi vprašanje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_question` |
| **Ikona** | ❓💬 |
| **Kategorija** | Nadzor |

Pogoj: prikaži pogovorno okno da/ne; resnično, če uporabnik odgovori z da

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `question` | Besedilo | `Continue?` | Vprašanje, prikazano igralcu |

### Preveri spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_variable` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Preveri vrednost spremenljivke instance ali globalne

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `variable` | Besedilo | — | Ime spremenljivke |
| `value` | Besedilo | `0` | Vrednost za primerjavo |
| `scope` | Izbira | `self` | Obseg spremenljivke; Izbire: `self`, `other`, `global` |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)
- [Réseau](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
