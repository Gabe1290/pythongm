# Score/Lives/Health

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Počisti tabelo rekordov

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `clear_highscore` |
| **Ikona** | 🗑️🏆 |
| **Kategorija** | Score/Lives/Health |

Počisti vse vnose tabele rekordov

*Parametri:* brez

### Prikaži tabelo rekordov

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_highscore` |
| **Ikona** | 🏆 |
| **Kategorija** | Score/Lives/Health |

Prikaži pogovorno okno tabele rekordov

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `background` | Barva | `#FFFFDD` | Barva ozadja pogovornega okna; neobvezno |
| `new_color` | Barva | `#FF0000` | Barva za nov (kvalificiran) vnos; neobvezno |
| `other_color` | Barva | `#000000` | Barva za druge vnose; neobvezno |
| `allow_new_entry` | Da/Ne | Da | Vprašaj za ime, če se trenutni rezultat kvalificira |

### Preveri zdravje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_health` |
| **Ikona** | ❓💚 |
| **Kategorija** | Score/Lives/Health |

Pogoj: primerjaj trenutno zdravje z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Število | `0` | Vrednost za primerjavo |

### Preveri življenja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_lives` |
| **Ikona** | ❓❤️ |
| **Kategorija** | Score/Lives/Health |

Pogoj: primerjaj število življenj z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `0` | Vrednost za primerjavo |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Preveri rezultat

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_score` |
| **Ikona** | ❓🏆 |
| **Kategorija** | Score/Lives/Health |

Pogoj: primerjaj rezultat z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `0` | Vrednost za primerjavo |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (21)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (6)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (14)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (3)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (18)
- [Risanje](Full-Action-Reference-Drawing_sl) (11)
- [Omrežje](Full-Action-Reference-Network-Actions_sl) (22)
- [Delci](Full-Action-Reference-Particles_sl) (8)
- [micro:bit](Full-Action-Reference-Microbit-Actions_sl) (16)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
