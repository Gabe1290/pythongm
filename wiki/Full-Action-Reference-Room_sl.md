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

### Nastavi ozadje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_background` |
| **Ikona** | 🖼️ |
| **Kategorija** | Soba |

Nastavi sliko ozadja trenutne sobe, z možnostmi ploščic in drsenja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `background` | Besedilo | — | Ime vira ozadja ali sprite-a |
| `visible` | Da/Ne | Da | Prikaži ozadje; neobvezno |
| `foreground` | Da/Ne | Ne | Nariši pred instancami namesto za njimi; neobvezno |
| `tiled_h` | Da/Ne | Ne | Ponovi ozadje po širini sobe; neobvezno |
| `tiled_v` | Da/Ne | Ne | Ponovi ozadje po višini sobe; neobvezno |
| `hspeed` | Število | `0` | Hitrost vodoravnega samodejnega drsenja v pikslih/sličico; neobvezno |
| `vspeed` | Število | `0` | Hitrost navpičnega samodejnega drsenja v pikslih/sličico; neobvezno |

### Nastavi barvo ozadja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_background_color` |
| **Ikona** | 🎨 |
| **Kategorija** | Soba |

Spremeni barvo ozadja trenutne sobe

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#87CEEB` | Barva ozadja |
| `show_color` | Da/Ne | Da | Ali je barva ozadja vidna (izklopljeno namesto tega zapolni s črno); neobvezno |

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

### Nastavi obstojnost sobe

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_room_persistent` |
| **Ikona** | 💾 |
| **Kategorija** | Soba |

Ali trenutna soba ohrani svoje aktivno stanje (položaje instanc, uničene instance itd.), ko jo igralec zapusti in se kasneje vrne vanjo, namesto da bi se ob vsakem obisku znova zgradila iz svoje izvirne postavitve

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `persistent` | Da/Ne | Da | Ohrani stanje te sobe ob ponovnem obisku |

### Nastavi hitrost sobe

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_room_speed` |
| **Ikona** | ⏱️ |
| **Kategorija** | Soba |

Spremeni hitrost sličic igre (sličice na sekundo)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `30` | Ciljne sličice na sekundo (1-240) |

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
