# Risanje

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Nariši puščico

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_arrow` |
| **Ikona** | ➡️ |
| **Kategorija** | Risanje |

Nariši puščico od ene točke do druge

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | Začetni X |
| `y1` | Število | `0` | Začetni Y |
| `x2` | Število | `100` | X konice |
| `y2` | Število | `100` | Y konice |
| `tip_size` | Število | `10` | Velikost konice puščice v pikslih |

### Nariši ozadje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_background` |
| **Ikona** | 🌄 |
| **Kategorija** | Risanje |

Nariši sliko ozadja, izbirno tlakovano po vsem zaslonu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `background` | Besedilo | — | Ime sredstva ozadja |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `tiled` | Da/Ne | Ne | Tlakuj po vsem zaslonu; neobvezno |

### Nariši elipso

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_ellipse` |
| **Ikona** | 🥚 |
| **Kategorija** | Risanje |

Nariši zapolnjeno ali obrisano elipso znotraj okvirja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | X levo |
| `y1` | Število | `0` | Y zgoraj |
| `x2` | Število | `100` | X desno |
| `y2` | Število | `100` | Y spodaj |
| `filled` | Da/Ne | Da | Zapolnjeno ali samo obris; neobvezno |

### Nariši črto

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_line` |
| **Ikona** | 📏 |
| **Kategorija** | Risanje |

Nariši črto med dvema točkama

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | Začetni X |
| `y1` | Število | `0` | Začetni Y |
| `x2` | Število | `100` | Končni X |
| `y2` | Število | `100` | Končni Y |

### Nariši povečano besedilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_scaled_text` |
| **Ikona** | 🖍️ |
| **Kategorija** | Risanje |

Nariši besedilo v poljubnem merilu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | — | Besedilo za risanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `xscale` | Število | `1.0` | Faktor vodoravnega merila |
| `yscale` | Število | `1.0` | Faktor navpičnega merila |

### Nariši sprite

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_sprite` |
| **Ikona** | 🖼️ |
| **Kategorija** | Risanje |

Nariši sličico spritea na položaju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite za risanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `subimage` | Število | `0` | Indeks sličice za risanje |

### Nariši spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_variable` |
| **Ikona** | 🔢 |
| **Kategorija** | Risanje |

Nariši vrednost spremenljivke na zaslonu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `variable` | Besedilo | — | Ime spremenljivke (self.var, global.var ali preprosto ime) |

### Zapolni zaslon z barvo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `fill_color` |
| **Ikona** | 🪣 |
| **Kategorija** | Risanje |

Zapolni celotno območje prikaza z enotno barvo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#000000` | Šestnajstiška barva RGB |

### Nastavi barvo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_color` |
| **Ikona** | 🎨 |
| **Kategorija** | Risanje |

Nastavi barvo in prosojnost risanja za naslednja risanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#FFFFFF` | Šestnajstiška barva RGB |
| `alpha` | Število | `1.0` | Prosojnost 0.0–1.0; neobvezno |

### Nastavi barvo risanja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_draw_color` |
| **Ikona** | 🎨 |
| **Kategorija** | Risanje |

Nastavi barvo, ki jo uporabljajo naslednja dejanja draw_*

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#000000` | Šestnajstiška barva RGB |

### Nastavi pisavo risanja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_draw_font` |
| **Ikona** | 🔤 |
| **Kategorija** | Risanje |

Nastavi pisavo in poravnavo za naslednje risanje besedila

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `font` | Besedilo | — | Ime sredstva pisave (prazno = privzeta pisava); neobvezno |
| `halign` | Izbira | `left` | Vodoravna poravnava besedila; Izbire: `left`, `center`, `right` |
| `valign` | Izbira | `top` | Navpična poravnava besedila; Izbire: `top`, `middle`, `bottom` |

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
- [Omrežje](Full-Action-Reference-Network-Actions_sl) (22)
- [Delci](Full-Action-Reference-Particles_sl) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_sl) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_sl) (16)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
