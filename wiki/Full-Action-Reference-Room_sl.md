# Soba

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Preveri sobo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `check_room` |
| **Ikona** | ❓🚪 |
| **Kategorija** | Soba |

Pogoj: resnično, če se trenutna soba ujema

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `room` | Soba | — | Soba za primerjavo |
| `not_flag` | Da/Ne | Ne | Obrni rezultat; neobvezno |

### Končaj igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `game_end` |
| **Ikona** | 🛑🎮 |
| **Kategorija** | Soba |

Končaj igro

*Parametri:* brez

### Pojdi v sobo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `goto_room` |
| **Ikona** | 🚪 |
| **Kategorija** | Soba |

Preklopi na določeno sobo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `room` | Soba | — | Ime ciljne sobe |
| `transition` | Izbira | `none` | Učinek prehoda (trenutno sprejet, a ne izrisan); Izbire: `none`; neobvezno |

### Če obstaja naslednja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_next_room_exists` |
| **Ikona** | ❓➡️ |
| **Kategorija** | Soba |

Preveri, ali obstaja naslednja soba za trenutno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `then_actions` | Seznam dejanj | — | Dejanja, če obstaja naslednja soba |
| `else_actions` | Seznam dejanj | — | Dejanja, če naslednja soba ne obstaja |

### Če obstaja prejšnja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_previous_room_exists` |
| **Ikona** | ❓⬅️ |
| **Kategorija** | Soba |

Preveri, ali obstaja prejšnja soba pred trenutno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `then_actions` | Seznam dejanj | — | Dejanja, če obstaja prejšnja soba |
| `else_actions` | Seznam dejanj | — | Dejanja, če prejšnja soba ne obstaja |

### Naslednja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `next_room` |
| **Ikona** | ➡️ |
| **Kategorija** | Soba |

Pojdi v naslednjo sobo

*Parametri:* brez

### Prejšnja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `previous_room` |
| **Ikona** | ⬅️ |
| **Kategorija** | Soba |

Pojdi v prejšnjo sobo

*Parametri:* brez

### Znova zaženi sobo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `restart_room` |
| **Ikona** | 🔄 |
| **Kategorija** | Soba |

Znova zaženi trenutno sobo

*Parametri:* brez

### Set Background

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_background` |
| **Ikona** | 🖼️ |
| **Kategorija** | Soba |

Set the current room's background image, with tiling and scrolling options

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `background` | Besedilo | — | Background or sprite asset name |
| `visible` | Da/Ne | Da | Show the background; neobvezno |
| `foreground` | Da/Ne | Ne | Draw in front of instances instead of behind them; neobvezno |
| `tiled_h` | Da/Ne | Ne | Repeat the background across the width of the room; neobvezno |
| `tiled_v` | Da/Ne | Ne | Repeat the background across the height of the room; neobvezno |
| `hspeed` | Število | `0` | Horizontal auto-scroll speed in pixels/frame; neobvezno |
| `vspeed` | Število | `0` | Vertical auto-scroll speed in pixels/frame; neobvezno |

### Set Background Color

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_background_color` |
| **Ikona** | 🎨 |
| **Kategorija** | Soba |

Change the current room's background color

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#87CEEB` | Background color |
| `show_color` | Da/Ne | Da | Whether the background color is visible (off fills black instead); neobvezno |

### Nastavi naslov sobe

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_room_caption` |
| **Ikona** | 🏷️ |
| **Kategorija** | Soba |

Nastavi naslov okna igre

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `caption` | Besedilo | — | Besedilo naslova okna |

### Set Room Persistent

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_room_persistent` |
| **Ikona** | 💾 |
| **Kategorija** | Soba |

Whether the current room keeps its live state (instance positions, destroyed instances, etc.) when the player leaves and later returns to it, instead of rebuilding fresh from its authored layout every revisit

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `persistent` | Da/Ne | Da | Keep this room's state across a revisit |

### Set Room Speed

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_room_speed` |
| **Ikona** | ⏱️ |
| **Kategorija** | Soba |

Change the game's frame rate (frames per second)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `30` | Target frames per second (1-240) |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Čas](Full-Action-Reference-Timing_sl) (2)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (20)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (4)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
