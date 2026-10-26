# Igra

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

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
| `color` | Barva | — | Barva besedila (npr. #ffffff). Prazno = trenutna barva risanja, sicer črna.; neobvezno |

### Naloži igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `load_game` |
| **Ikona** | 📂 |
| **Kategorija** | Igra |

Iz shranjene datoteke obnovi sobo, točke, življenja, zdravje, globalne spremenljivke in stanje primerkov

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `filename` | Besedilo | `savegame.sav` | Ime shranjene datoteke za nalaganje (iz mape saves/ v projektu) |

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

### Shrani igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `save_game` |
| **Ikona** | 💾 |
| **Kategorija** | Igra |

V datoteko shrani trenutno sobo, točke, življenja, zdravje, globalne spremenljivke in stanje primerkov

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `filename` | Besedilo | `savegame.sav` | Ime shranjene datoteke (zapiše se v mapo saves/ v projektu) |

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

### Predvajaj video

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_video` |
| **Ikona** | 🎬 |
| **Kategorija** | Igra |

Predvaja video datoteko v privzetem predvajalniku sistema: odpre se v svojem oknu in se ne riše znotraj same igre

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `filename` | Besedilo | — | Pot do video datoteke |
| `fullscreen` | Da/Ne | Ne | Zahtevaj predvajanje čez cel zaslon (odvisno od predvajalnika v tvojem sistemu); neobvezno |

### Uvodni zaslon: pokaži sliko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `splash_show_image` |
| **Ikona** | 🖼️ |
| **Kategorija** | Igra |

Pokaže sličico čez ves zaslon in zaustavi igro, dokler je igralec ne zapre

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sličica, ki naj se pokaže čez cel zaslon |

### Uvodni zaslon: pokaži besedilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `splash_show_text` |
| **Ikona** | 💬 |
| **Kategorija** | Igra |

Pokaže sporočilo in zaustavi igro, dokler ga igralec ne zapre

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | — | Sporočilo, ki naj se pokaže |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (21)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (6)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
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
