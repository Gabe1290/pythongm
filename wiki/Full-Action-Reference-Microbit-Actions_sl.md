# micro:bit

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Počisti zaslon

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_clear_display` |
| **Ikona** | ⬛ |
| **Kategorija** | micro:bit |

Ugasni vse LED diode in zavrzi vse, kar je čakalo

*Parametri:* brez

### Če je tipka pritisnjena

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_button` |
| **Ikona** | 🔘 |
| **Kategorija** | micro:bit |

Res, dokler je tipka pridržana (A+B = obe)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `button` | Izbira | `a` | Izbire: `a`, `b`, `ab`, `logo` |

### Če je poteza

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_gesture` |
| **Ikona** | 🤝 |
| **Kategorija** | micro:bit |

Res, dokler je ploščica v tej potezi ali legi

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `gesture` | Izbira | `shake` | Izbire: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### Če je svetilnost LED diode

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_pixel` |
| **Ikona** | 🔍 |
| **Kategorija** | micro:bit |

Primerjaj svetilnost LED diode (od 0 do 9) z vrednostjo; privzeto je vprašanje »ali sveti?«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `comparison` | Izbira | `>` | Izbire: `<`, `<=`, `==`, `>=`, `>`, `!=`; neobvezno |
| `value` | Besedilo | `0` | neobvezno |

### Če je nagib

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_if_tilt` |
| **Ikona** | 📐 |
| **Kategorija** | micro:bit |

Primerjaj os pospeškomera (mili-g, od -2048 do 2048) z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `axis` | Izbira | `x` | Izbire: `x`, `y`, `z` |
| `comparison` | Izbira | `>` | Izbire: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Besedilo | `300` |  |

### Zaigraj melodijo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_play_melody` |
| **Ikona** | 🎵 |
| **Kategorija** | micro:bit |

Zaigraj vgrajeno melodijo (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…) ali svoje note, na primer »C4:4 E G C5:8 R:4« (nota, oktava, :trajanje; R je premor)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `melody` | Besedilo | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Besedilo | `120` | neobvezno |

### Zaigraj ton

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_play_tone` |
| **Ikona** | 🔔 |
| **Kategorija** | micro:bit |

Oddaj pisk z dano frekvenco za dano število milisekund. Zvoki se uvrstijo v čakalno vrsto

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `frequency` | Besedilo | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Besedilo | `500` | neobvezno |

### Preberi tipalo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_read_sensor` |
| **Ikona** | 📡 |
| **Kategorija** | micro:bit |

Preberi tipalo micro:bita v spremenljivko tega predmeta (ali v globalno spremenljivko, če se ime začne z »global.«)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sensor` | Izbira | `accelerometer x` | Izbire: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Besedilo | `sensor_value` | Variable that receives the reading |

### Drsi besedilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_scroll_text` |
| **Ikona** | 🔤 |
| **Kategorija** | micro:bit |

Besedilo drsi po zaslonu z LED diodami. Besedilo daj v narekovaje ("Živjo"); sicer se vezaj ali plus prebere kot izračun. Črke s strešico se prikažejo kot ?, tako kot na pravi ploščici

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | `"Hello"` | Text or expression to scroll |
| `delay` | Število | `150` | Scroll speed (MicroPython default 150); neobvezno |

### Pošlji radijsko sporočilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_radio_send` |
| **Ikona** | 📻 |
| **Kategorija** | micro:bit |

Pošlji število ali besedilo drugim micro:bitom iz iste skupine (ne temu). Prejmejo dogodek »Radijsko sporočilo prejeto«, vrednost je v radio_number in radio_string. Besedilo daj v narekovaje; skrajša se na 32 znakov

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Besedilo | `1` | A number, an expression or quoted text |

### Svetilnost zaslona

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_set_brightness` |
| **Ikona** | 🔆 |
| **Kategorija** | micro:bit |

Splošna svetilnost LED diod, od 0 (ugasnjeno) do 255 (največ)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `brightness` | Besedilo | `255` |  |

### Prižgi LED diodo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_set_pixel` |
| **Ikona** | 💡 |
| **Kategorija** | micro:bit |

Takoj prižgi LED diodo (x in y od 0 do 4, svetilnost od 0 do 9)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `brightness` | Besedilo | `9` | neobvezno |

### Nastavi radijsko skupino

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_radio_set_group` |
| **Ikona** | 📡 |
| **Kategorija** | micro:bit |

Izberi radijsko skupino (od 0 do 255). Slišijo se le micro:biti iz iste skupine; vsaka ploščica začne v skupini 0

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `group` | Besedilo | `0` |  |

### Prikaži sliko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_show_image` |
| **Ikona** | ❤️ |
| **Kategorija** | micro:bit |

Prikaži sliko na LED diodah: ime (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL…) ali pet vrstic številk svetilnosti, na primer »09090:99999:99999:09990:00900«. Slike se uvrstijo v čakalno vrsto

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `image` | Besedilo | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Število | `0` | How long it stays before the next queued item (0 = until something else is shown); neobvezno |

### Prikaži število

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_show_number` |
| **Ikona** | 🔢 |
| **Kategorija** | micro:bit |

Prikaži število: ena števka ostane pri miru, daljše število drsi

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Besedilo | `0` | Number or expression |

### Ustavi zvok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `microbit_stop_sound` |
| **Ikona** | 🔇 |
| **Kategorija** | micro:bit |

Izklopi zvočnik in zavrzi zvoke, ki čakajo

*Parametri:* brez

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
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (20)
- [Risanje](Full-Action-Reference-Drawing_sl) (11)
- [Omrežje](Full-Action-Reference-Network-Actions_sl) (22)
- [Delci](Full-Action-Reference-Particles_sl) (8)
- [Rezultat/Življenja/Zdravje](Full-Action-Reference-Score-Lives-Health_sl) (5)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
