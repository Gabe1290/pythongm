# Čas

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Pause Timeline

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `pause_timeline` |
| **Ikona** | ⏸️ |
| **Kategorija** | Čas |

Pause timeline playback at the current position

*Parametri:* brez

### Nastavi budilko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_alarm` |
| **Ikona** | ⏰ |
| **Kategorija** | Čas |

Nastavi budilko

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `alarm_number` | Število | `0` | Katera budilka (0-11) |
| `steps` | Število | `30` | Število korakov do sprožitve budilke (30 = 0,5 s pri 60 FPS) |

### Set Timeline

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_timeline` |
| **Ikona** | ⏱️ |
| **Kategorija** | Čas |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `timeline` | Besedilo | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_timeline_position` |
| **Ikona** | ⏱️ |
| **Kategorija** | Čas |

Set (or offset) this instance's timeline position

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `position` | Število | `0` | Position in steps |
| `relative` | Da/Ne | Ne | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_timeline_speed` |
| **Ikona** | ⏱️ |
| **Kategorija** | Čas |

Set the timeline playback speed multiplier

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Premor

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `sleep` |
| **Ikona** | 💤 |
| **Kategorija** | Čas |

Zaustavi igro za določeno število milisekund, nato nadaljuj. Zvoki se med premorom še naprej predvajajo (na primer, da se zvok konča pred menjavo sobe). Opomba: izrisovanje in vnos sta med premorom zamrznjena, zato ohranjaj kratke dolžine

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `milliseconds` | Število | `1000` | Trajanje premora, v milisekundah (1000 = 1 sekunda) |

### Start Timeline

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_timeline` |
| **Ikona** | ▶️ |
| **Kategorija** | Čas |

Begin or resume timeline playback from the current position

*Parametri:* brez

### Stop Timeline

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_timeline` |
| **Ikona** | ⏹️ |
| **Kategorija** | Čas |

Stop timeline playback and reset the position to 0

*Parametri:* brez

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)
- [Réseau](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
