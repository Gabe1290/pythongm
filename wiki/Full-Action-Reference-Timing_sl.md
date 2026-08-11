# Čas

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

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

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (20)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (4)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
