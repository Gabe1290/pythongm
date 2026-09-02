# Rezultat

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Počisti tabelo rekordov

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `clear_highscore` |
| **Ikona** | 🗑️🏆 |
| **Kategorija** | Rezultat |

Počisti vse vnose tabele rekordov

*Parametri:* brez

### Nariši vrstico zdravja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_health_bar` |
| **Ikona** | 🩺 |
| **Kategorija** | Rezultat |

Nariši trenutno zdravje kot dvobarvno vrstico

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | X levo |
| `y1` | Število | `0` | Y zgoraj |
| `x2` | Število | `100` | X desno |
| `y2` | Število | `20` | Y spodaj |
| `back_color` | Barva | `#FF0000` | Barva ozadja (prazno) |
| `bar_color` | Barva | `#00FF00` | Barva polnila (zdravje) |

### Nariši življenja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_lives` |
| **Ikona** | 🖍️❤️ |
| **Kategorija** | Rezultat |

Nariši trenutno število življenj kot ponovljene slike spritea

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `sprite` | Sprite | — | Sprite, narisan enkrat na vsako preostalo življenje; neobvezno |
| `scale` | Število | `1.0` | Enakomeren faktor merila za ikono življenja (1.0 = izvirna velikost); neobvezno |
| `relative` | Da/Ne | Ne | Nariši glede na položaj te instance namesto absolutnih zaslonskih koordinat; neobvezno |

### Nariši rezultat

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_score` |
| **Ikona** | 🖍️🏆 |
| **Kategorija** | Rezultat |

Nariši trenutni rezultat na zaslonu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `caption` | Besedilo | `Score: ` | Besedilo, prikazano pred vrednostjo rezultata; neobvezno |
| `relative` | Da/Ne | Ne | Nariši glede na položaj te instance namesto absolutnih zaslonskih koordinat; neobvezno |

### Nastavi zdravje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_health` |
| **Ikona** | 💚 |
| **Kategorija** | Rezultat |

Nastavi zdravje ali mu prištej z »Relativno«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `100` | Vrednost zdravja (0-100) |
| `relative` | Da/Ne | Ne | Prištej trenutnemu zdravju namesto zamenjave |

### Nastavi življenja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_lives` |
| **Ikona** | ❤️ |
| **Kategorija** | Rezultat |

Nastavi življenja ali jim prištej z »Relativno«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `3` | Število življenj |
| `relative` | Da/Ne | Ne | Prištej trenutnim življenjem namesto zamenjave |

### Nastavi rezultat

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_score` |
| **Ikona** | 🏆 |
| **Kategorija** | Rezultat |

Nastavi rezultat ali mu prištej z »Relativno«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `0` | Vrednost rezultata za nastavitev |
| `relative` | Da/Ne | Ne | Prištej trenutnemu rezultatu namesto zamenjave |

### Prikaži tabelo rekordov

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_highscore` |
| **Ikona** | 🏆 |
| **Kategorija** | Rezultat |

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
| **Kategorija** | Rezultat |

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
| **Kategorija** | Rezultat |

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
| **Kategorija** | Rezultat |

Pogoj: primerjaj rezultat z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `0` | Vrednost za primerjavo |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)
- [Réseau](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
