# Igra

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Nariši puščico

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_arrow` |
| **Ikona** | ➡️ |
| **Kategorija** | Igra |

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
| **Kategorija** | Igra |

Nariši sliko ozadja, izbirno tlakovano po vsem zaslonu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `background` | Besedilo | — | Ime sredstva ozadja |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `tiled` | Da/Ne | Ne | Tlakuj po vsem zaslonu; neobvezno |

### Nariši krog

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_circle` |
| **Ikona** | ⭕ |
| **Kategorija** | Igra |

Nariši zapolnjen ali obrisan krog

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | X središče |
| `y` | Število | `0` | Y središče |
| `radius` | Število | `50` | Polmer kroga |
| `filled` | Da/Ne | Da | Zapolnjeno ali samo obris; neobvezno |

### Nariši elipso

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_ellipse` |
| **Ikona** | 🥚 |
| **Kategorija** | Igra |

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
| **Kategorija** | Igra |

Nariši črto med dvema točkama

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | Začetni X |
| `y1` | Število | `0` | Začetni Y |
| `x2` | Število | `100` | Končni X |
| `y2` | Število | `100` | Končni Y |

### Nariši pravokotnik

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_rectangle` |
| **Ikona** | 🟥 |
| **Kategorija** | Igra |

Nariši zapolnjen ali obrisan pravokotnik

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | X levo |
| `y1` | Število | `0` | Y zgoraj |
| `x2` | Število | `100` | X desno |
| `y2` | Število | `100` | Y spodaj |
| `filled` | Da/Ne | Da | Zapolnjeno ali samo obris; neobvezno |

### Nariši povečano besedilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_scaled_text` |
| **Ikona** | 🖍️ |
| **Kategorija** | Igra |

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
| **Kategorija** | Igra |

Nariši sličico spritea na položaju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite za risanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `subimage` | Število | `0` | Indeks sličice za risanje |

### Nariši besedilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_text` |
| **Ikona** | 🖍️ |
| **Kategorija** | Igra |

Nariši besedilni niz na položaju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | — | Besedilo za risanje (podpira izraze) |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `relative` | Da/Ne | Ne | Nariši glede na položaj te instance namesto absolutnih zaslonskih koordinat; neobvezno |

### Nariši spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_variable` |
| **Ikona** | 🔢 |
| **Kategorija** | Igra |

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
| **Kategorija** | Igra |

Zapolni celotno območje prikaza z enotno barvo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#000000` | Šestnajstiška barva RGB |

### Odpri spletno stran

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `open_webpage` |
| **Ikona** | 🌐 |
| **Kategorija** | Igra |

Odpri URL v privzetem brskalniku

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `url` | Besedilo | — | Spletni naslov za odprtje |

### Znova zaženi igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `restart_game` |
| **Ikona** | 🔁🎮 |
| **Kategorija** | Igra |

Znova zaženi igro iz začetne sobe

*Parametri:* brez

### Nastavi prosojnost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_alpha` |
| **Ikona** | 🌫️ |
| **Kategorija** | Igra |

Nastavi prosojnost risanja za naslednja risanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `alpha` | Število | `1.0` | Prosojnost od 0.0 (prozorno) do 1.0 (neprozorno) |

### Nastavi barvo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_color` |
| **Ikona** | 🎨 |
| **Kategorija** | Igra |

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
| **Kategorija** | Igra |

Nastavi barvo, ki jo uporabljajo naslednja dejanja draw_*

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#000000` | Šestnajstiška barva RGB |

### Nastavi pisavo risanja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_draw_font` |
| **Ikona** | 🔤 |
| **Kategorija** | Igra |

Nastavi pisavo in poravnavo za naslednje risanje besedila

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `font` | Besedilo | — | Ime sredstva pisave (prazno = privzeta pisava); neobvezno |
| `halign` | Izbira | `left` | Vodoravna poravnava besedila; Izbire: `left`, `center`, `right` |
| `valign` | Izbira | `top` | Navpična poravnava besedila; Izbire: `top`, `middle`, `bottom` |

### Nastavi naslov okna

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_window_caption` |
| **Ikona** | 🪟 |
| **Kategorija** | Igra |

Konfiguriraj prikaz rezultata/življenj/zdravja v naslovu okna

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `show_score` | Da/Ne | Da | Dodaj trenutni rezultat naslovu okna |
| `show_lives` | Da/Ne | Da | Dodaj trenutno število življenj naslovu okna |
| `show_health` | Da/Ne | Ne | Dodaj trenutno vrednost zdravja naslovu okna |
| `caption` | Besedilo | — | Neobvezna predpona naslova, prikazana pred števci; neobvezno |

### Prikaži informacije o igri

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_info` |
| **Ikona** | ℹ️ |
| **Kategorija** | Igra |

Prikaži zaslon z informacijami o igri

*Parametri:* brez

### Prikaži sporočilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_message` |
| **Ikona** | 💬 |
| **Kategorija** | Igra |

Prikaži sporočilo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `message` | Besedilo | `Hello!` | Besedilo sporočila |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (2)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (4)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
