# Zvok

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Preveri predvajanje zvoka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `check_sound` |
| **Ikona** | ❓🔊 |
| **Kategorija** | Zvok |

Pogoj: resnično, če se navedeni zvok trenutno predvaja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sound` | Zvok | — | Zvok za preverjanje |
| `not_flag` | Da/Ne | Ne | Obrni rezultat; neobvezno |

### Predvajaj glasbo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `play_music` |
| **Ikona** | 🎵 |
| **Kategorija** | Zvok |

Predvajaj glasbo v ozadju (v zanki)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `music` | Zvok | — | Glasbena datoteka za predvajanje |
| `loop` | Da/Ne | Da | Predvajaj glasbo v zanki |
| `volume` | Število | `0.7` | Glasnost (od 0.0 do 1.0) |

### Predvajaj zvok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `play_sound` |
| **Ikona** | 🔊 |
| **Kategorija** | Zvok |

Predvajaj zvočni učinek enkrat

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sound` | Zvok | — | Zvok za predvajanje |
| `volume` | Število | `1.0` | Glasnost (od 0.0 do 1.0) |

### Nastavi glasnost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_volume` |
| **Ikona** | 🔉 |
| **Kategorija** | Zvok |

Nastavi splošno glasnost zvoka/glasbe

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `volume` | Število | `1.0` | Glasnost (od 0.0 do 1.0) |

### Ustavi glasbo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_music` |
| **Ikona** | 🔇 |
| **Kategorija** | Zvok |

Ustavi glasbo v ozadju

*Parametri:* brez

### Ustavi zvok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_sound` |
| **Ikona** | 🔇 |
| **Kategorija** | Zvok |

Ustavi predvajani zvok

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sound` | Zvok | — | Zvok za ustavitev |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (21)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (6)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
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
