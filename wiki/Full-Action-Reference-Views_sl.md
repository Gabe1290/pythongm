# Pogledi

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Omogoči poglede

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `enable_views` |
| **Ikona** | 🎥 |
| **Kategorija** | Pogledi |

Vklopi ali izklopi sistem kamere/pogleda sobe (omogoča drsenje ravni, ko je večja od okna)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `enable` | Da/Ne | Da | Vklop = pogledi kamere; izklop = nariši celotno sobo naenkrat |

### Nastavi pogled

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_view` |
| **Ikona** | 🎥 |
| **Kategorija** | Pogledi |

Konfiguriraj pogled kamere: kateri del sobe prikazuje, kje se izriše na zaslonu in predmet za sledenje

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `view` | Izbira | `0` | Katerega od 8 pogledov konfigurirati; Izbire: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Da/Ne | Da | Nariši ta pogled |
| `view_x` | Število | `0` | Levi rob prikazanega območja sobe |
| `view_y` | Število | `0` | Zgornji rob prikazanega območja sobe |
| `view_w` | Število | `800` | Širina prikazanega območja sobe |
| `view_h` | Število | `600` | Višina prikazanega območja sobe |
| `port_x` | Število | `0` | Levi rob na zaslonu |
| `port_y` | Število | `0` | Zgornji rob na zaslonu |
| `port_w` | Število | `800` | Širina, narisana na zaslonu |
| `port_h` | Število | `600` | Višina, narisana na zaslonu |
| `follow` | Predmet | — | Predmet, ki mu kamera sledi (prazno = fiksni pogled); neobvezno |
| `hborder` | Število | `32` | Vodoravni rob, preden se kamera pomakne |
| `vborder` | Število | `32` | Navpični rob, preden se kamera pomakne |
| `hspeed` | Število | `-1` | Največja vodoravna hitrost drsenja (-1 = takoj) |
| `vspeed` | Število | `-1` | Največja navpična hitrost drsenja (-1 = takoj) |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (2)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (20)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (4)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
