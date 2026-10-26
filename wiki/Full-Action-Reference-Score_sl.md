# Rezultat

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

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

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (21)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
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
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_sl) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_sl) (16)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
