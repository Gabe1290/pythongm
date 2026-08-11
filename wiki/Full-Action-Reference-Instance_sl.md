# Instanca

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Spremeni instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `change_instance` |
| **Ikona** | 🔄 |
| **Kategorija** | Instanca |
| **Velja za** | self / other / object |

Preoblikuj v drugo vrsto predmeta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Nova vrsta predmeta |
| `perform_events` | Da/Ne | Da | Izvedi dogodke uniči/ustvari |

### Ustvari instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_instance` |
| **Ikona** | ✨ |
| **Kategorija** | Instanca |

Ustvari novo instanco

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Predmet za ustvarjanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `relative` | Da/Ne | Ne | Položaj glede na trenutno instanco |

### Ustvari premikajočo se instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_moving_instance` |
| **Ikona** | ✨➡️ |
| **Kategorija** | Instanca |

Ustvari instanco in jo zaženi v smeri

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Predmet za ustvarjanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `speed` | Število | `0` | Začetna velikost hitrosti |
| `direction` | Število | `0` | Začetna smer v stopinjah |

### Ustvari naključno instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_random_instance` |
| **Ikona** | 🎲 |
| **Kategorija** | Instanca |

Ustvari eno od več vrst predmetov, izbrano naključno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `object1` | Predmet | — | Prvi kandidatni predmet; neobvezno |
| `object2` | Predmet | — | Drugi kandidatni predmet; neobvezno |
| `object3` | Predmet | — | Tretji kandidatni predmet; neobvezno |
| `object4` | Predmet | — | Četrti kandidatni predmet; neobvezno |

### Uniči instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_instance` |
| **Ikona** | 💥 |
| **Kategorija** | Instanca |
| **Velja za** | self / other / object |

Uniči instanco

*Parametri:* brez

### Uniči na položaju

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_at_position` |
| **Ikona** | 💣 |
| **Kategorija** | Instanca |

Uniči instance znotraj polmera od (x, y)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | `all` | Katero vrsto predmeta uničiti. »all« uniči vsako instanco v dosegu; »solid« samo trdne (npr. stene); »non-solid« vse razen trdnih.; Izbire: `all`, `solid`, `non-solid` |
| `x` | Besedilo | `self.x` | Položaj X (izraz dovoljen, npr. self.x) |
| `y` | Besedilo | `self.y` | Položaj Y (izraz dovoljen, npr. self.y) |
| `relative` | Da/Ne | Ne | Obravnavaj X/Y kot odmike od položaja te instance namesto absolutnih koordinat; neobvezno |
| `radius` | Število | `32` | Polmer v pikslih okoli (x, y). Privzeto 32 = ~ena celica mreže. |

### Nastavi indeks slike

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_image_index` |
| **Ikona** | 🖼️ |
| **Kategorija** | Instanca |

Nastavi trenutno sličico animacije spritea instance

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `frame` | Število | `0` | Indeks sličice |

### Nastavi hitrost slike

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_image_speed` |
| **Ikona** | ⏩ |
| **Kategorija** | Instanca |

Nastavi hitrost predvajanja animacije spritea instance

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `1.0` | Sličice, napredovane na korak (0 = zaustavljeno) |

### Nastavi sprite

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_sprite` |
| **Ikona** | 🖼️ |
| **Kategorija** | Instanca |

Spremeni sprite in/ali sličico/hitrost animacije instance

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite za uporabo (ali »<self>« za ohranitev trenutnega) |
| `subimage` | Število | `-1` | Indeks sličice za nastavitev; -1 pusti nespremenjeno |
| `speed` | Število | `-1` | Hitrost animacije; -1 pusti nespremenjeno |

### Zaženi animacijo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_animation` |
| **Ikona** | ▶️ |
| **Kategorija** | Instanca |

Nadaljuj animacijo spritea instance (image_speed = 1)

*Parametri:* brez

### Ustavi animacijo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_animation` |
| **Ikona** | ⏸️ |
| **Kategorija** | Instanca |

Zaustavi animacijo spritea instance (image_speed = 0)

*Parametri:* brez

### Preveri število instanc

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_instance_count` |
| **Ikona** | ❓🔢 |
| **Kategorija** | Instanca |

Pogoj: primerjaj število instanc predmeta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Predmet za štetje |
| `number` | Število | `0` | Vrednost za primerjavo |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (2)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (20)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (4)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
