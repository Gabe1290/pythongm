# Mreža

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Če na mreži

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_on_grid` |
| **Ikona** | ▦ |
| **Kategorija** | Mreža |

Preveri, ali je predmet poravnan na mrežo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `grid_size` | Število | `32` | Velikost celice mreže v pikslih |
| `then_actions` | Seznam dejanj | — | Dejanja, če na mreži |
| `else_actions` | Seznam dejanj | — | Dejanja, če ne na mreži |

### Pripni na mrežo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `snap_to_grid` |
| **Ikona** | ▦ |
| **Kategorija** | Mreža |

Poravnaj položaj instance na mrežo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `grid_size` | Število | `32` | Velikost celice mreže v pikslih |

### Ustavi, če ni pritisnjenih tipk

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_if_no_keys` |
| **Ikona** | ▦ |
| **Kategorija** | Mreža |

Ustavi gibanje po mreži, ko ni pritisnjena nobena tipka za gibanje (odlično za gladko pripenjanje na mrežo)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `grid_size` | Število | `32` | Velikost celice mreže v pikslih |

### Preveri poravnavo na mrežo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_alignment` |
| **Ikona** | ❓▦ |
| **Kategorija** | Mreža |

Pogoj: resnično, če je instanca poravnana na mrežo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `hsnap` | Število | `32` | Vodoravni razmik mreže v pikslih |
| `vsnap` | Število | `32` | Navpični razmik mreže v pikslih |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)
- [Réseau](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
