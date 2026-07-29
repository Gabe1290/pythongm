# Vmesna Prednastavitev

*[Domov](Home_sl) | [Vodič po Prednastavitvah](Preset-Guide_sl) | [Začetna Prednastavitev](Beginner-Preset_sl)*

**Vmesna** prednastavitev nadgrajuje [Začetno Prednastavitev](Beginner-Preset_sl) z dodajanjem naprednejših dogodkov in akcij. Zasnovana je za uporabnike, ki so obvladali osnove in želijo ustvariti bolj kompleksne igre z funkcijami, kot so časovno določeni dogodki, zvok, življenja in zdravstveni sistemi.

## Pregled

Vmesna prednastavitev vključuje vse iz Začetne, plus:
- **4 Dodatne Vrste Dogodkov** - Risanje, Uničenje, Miška, Alarm
- **12 Dodatnih Vrst Akcij** - Življenja, Zdravje, Zvok, Časovnik in več možnosti gibanja
- **3 Dodatne Kategorije** - Časovnik, Zvok, Risanje

---

## Dodatni Dogodki (Preko Začetnega)

### Dogodek Risanja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_draw` |
| **Kategorija** | Risanje |
| **Ikona** | 🎨 |
| **Opis** | Sproži se, ko je potrebno izrisati objekt |

**Kdaj se sproži:** Vsako sličico med fazo risanja, po vseh step dogodkih.

**Pomembno:** Ko dodate dogodek Risanja, se privzeto risanje sprite-a onemogoči. Če želite, da je viden, morate sprite narisati ročno.

**Pogoste uporabe:**
- Prilagojeno izrisovanje
- Risanje zdravstvenih pasic
- Prikaz besedila
- Risanje oblik in učinkov
- Elementi vmesnika

---

### Dogodek Uničenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_destroy` |
| **Kategorija** | Objekt |
| **Ikona** | 💥 |
| **Opis** | Sproži se, ko je instanca uničena |

**Kdaj se sproži:** Tik preden je instanca odstranjena iz igre.

**Pogoste uporabe:**
- Ustvarjanje eksplozijskih učinkov
- Spuščanje predmetov
- Predvajanje zvoka smrti
- Posodobitev rezultata
- Generiranje delcev

---

### Dogodek Miške
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_mouse` |
| **Kategorija** | Vnos |
| **Ikona** | 🖱️ |
| **Opis** | Sproži se ob interakcijah z miško |

**Vrste dogodkov miške:**
- Levi gumb (pritisk, sprostitev, držanje)
- Desni gumb (pritisk, sprostitev, držanje)
- Srednji gumb (pritisk, sprostitev, držanje)
- Miška vstopi (kazalec vstopi v instanco)
- Miška izstopi (kazalec zapusti instanco)
- Globalni dogodki miške (kjerkoli na zaslonu)

**Pogoste uporabe:**
- Klikljivi gumbi
- Vleci in spusti
- Učinki lebdenja
- Interakcije z menijem

---

### Dogodek Alarma
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_alarm` |
| **Kategorija** | Časovnik |
| **Ikona** | ⏰ |
| **Opis** | Sproži se, ko časovnik alarma doseže nic |

**Kdaj se sproži:** Ko ustrezno odštevanje alarma doseže 0.

**Razpoložljivi alarmi:** 12 neodvisnih alarmov (0-11)

**Pogoste uporabe:**
- Časovno generiranje
- Zakasnela dejanja
- Časi ohladitve
- Časovno usklajevanje animacij
- Periodični dogodki

---

## Dodatne Akcije (Preko Začetnega)

### Akcije Gibanja

#### Premik v Smeri
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `move_direction` |
| **Ime Bloka** | `move_direction` |
| **Kategorija** | Gibanje |

**Opis:** Nastavite gibanje z uporabo smeri (0-360 stopinj) in hitrosti.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `direction` | Število | Smer v stopinjah (0=desno, 90=gor, 180=levo, 270=dol) |
| `speed` | Število | Hitrost gibanja |

---

#### Premik Proti Točki
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `move_towards_point` |
| **Ime Bloka** | `move_towards_point` |
| **Kategorija** | Gibanje |

**Opis:** Premik proti določeni poziciji.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x` | Število/Izraz | Ciljna X koordinata |
| `y` | Število/Izraz | Ciljna Y koordinata |
| `speed` | Število | Hitrost gibanja |

---

### Akcije Časovnika

#### Nastavi Alarm
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `set_alarm` |
| **Ime Bloka** | `set_alarm` |
| **Kategorija** | Časovnik |
| **Ikona** | ⏰ |

**Opis:** Nastavite alarm, ki se sproži po določenem številu korakov.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `alarm` | Število | Številka alarma (0-11) |
| `steps` | Število | Koraki do sprožitve alarma (pri 60 FPS, 60 korakov = 1 sekunda) |

**Primer:** Nastavite alarm 0 na 180 korakov za 3-sekundni zamik.

---

### Akcije Življenj

#### Nastavi Življenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `set_lives` |
| **Ime Bloka** | `lives_set` |
| **Kategorija** | Rezultat/Življenja/Zdravje |
| **Ikona** | ❤️ |

**Opis:** Nastavite število življenj.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Število | Vrednost življenj |
| `relative` | Logična | Če je true, prišteje k trenutnim življenjem |

---

#### Dodaj Življenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `add_lives` |
| **Ime Bloka** | `lives_add` |
| **Kategorija** | Rezultat/Življenja/Zdravje |
| **Ikona** | ➕❤️ |

**Opis:** Dodaj ali odštej življenja.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Število | Količina za dodajanje (negativno za odštevanje) |

**Opomba:** Ko življenja dosežejo 0, se sproži dogodek `no_more_lives`.

---

#### Nariši Življenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `draw_lives` |
| **Ime Bloka** | `draw_lives` |
| **Kategorija** | Rezultat/Življenja/Zdravje |
| **Ikona** | 🖼️❤️ |

**Opis:** Prikaži življenja na zaslonu.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x` | Število | X pozicija |
| `y` | Število | Y pozicija |
| `sprite` | Sprite | Neobvezen sprite za uporabo kot ikona življenja |

---

### Akcije Zdravja

#### Nastavi Zdravje
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `set_health` |
| **Ime Bloka** | `health_set` |
| **Kategorija** | Rezultat/Življenja/Zdravje |
| **Ikona** | 💚 |

**Opis:** Nastavite vrednost zdravja (0-100).

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Število | Vrednost zdravja (0-100) |
| `relative` | Logična | Če je true, prišteje k trenutnemu zdravju |

---

#### Dodaj Zdravje
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `add_health` |
| **Ime Bloka** | `health_add` |
| **Kategorija** | Rezultat/Življenja/Zdravje |
| **Ikona** | ➕💚 |

**Opis:** Dodaj ali odštej zdravje.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Število | Količina za dodajanje (negativno za poškodbe) |

**Opomba:** Ko zdravje doseže 0, se sproži dogodek `no_more_health`.

---

#### Nariši Zdravstveno Pasico
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `draw_health_bar` |
| **Ime Bloka** | `draw_health_bar` |
| **Kategorija** | Rezultat/Življenja/Zdravje |
| **Ikona** | 📊💚 |

**Opis:** Narisanje zdravstvene pasice na zaslonu.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x1` | Število | Leva X pozicija |
| `y1` | Število | Zgornja Y pozicija |
| `x2` | Število | Desna X pozicija |
| `y2` | Število | Spodnja Y pozicija |
| `back_color` | Barva | Barva ozadja |
| `bar_color` | Barva | Barva zdravstvene pasice |

---

### Zvočne Akcije

#### Predvajaj Zvok
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `play_sound` |
| **Ime Bloka** | `sound_play` |
| **Kategorija** | Zvok |
| **Ikona** | 🔊 |

**Opis:** Predvajanje zvočnega učinka.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `sound` | Zvok | Zvočni vir za predvajanje |
| `loop` | Logična | Ali naj se zvok ponavlja |

---

#### Predvajaj Glasbo
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `play_music` |
| **Ime Bloka** | `music_play` |
| **Kategorija** | Zvok |
| **Ikona** | 🎵 |

**Opis:** Predvajanje glasbe v ozadju.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `sound` | Zvok | Glasbeni vir za predvajanje |
| `loop` | Logična | Ali naj se ponavlja (običajno true za glasbo) |

---

#### Ustavi Glasbo
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `stop_music` |
| **Ime Bloka** | `music_stop` |
| **Kategorija** | Zvok |
| **Ikona** | 🔇 |

**Opis:** Ustavite vso trenutno predvajajočo glasbo.

**Parametri:** Brez

---

## Celoten Seznam Funkcij

### Dogodki v Vmesni Prednastavitvi

| Dogodek | Kategorija | Opis |
|---------|------------|------|
| Create | Objekt | Instanca ustvarjena |
| Step | Objekt | Vsako sličico |
| Destroy | Objekt | Instanca uničena |
| Draw | Risanje | Faza izrisovanja |
| Keyboard Press | Vnos | Tipka pritisnjena enkrat |
| Mouse | Vnos | Interakcije z miško |
| Collision | Trk | Prekrivanje instanc |
| Alarm | Časovnik | Časovnik dosegel nic |

### Akcije v Vmesni Prednastavitvi

| Kategorija | Akcije |
|------------|--------|
| **Gibanje** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards Point |
| **Instanca** | Create, Destroy |
| **Rezultat** | Set Score, Add Score, Draw Score |
| **Življenja** | Set Lives, Add Lives, Draw Lives |
| **Zdravje** | Set Health, Add Health, Draw Health Bar |
| **Soba** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Časovnik** | Set Alarm |
| **Zvok** | Play Sound, Play Music, Stop Music |
| **Izhod** | Show Message, Execute Code |

---

## Primer: Strelska Igra z Življenji

### Objekt Igralca

**Create:**
- Set Lives: 3

**Keyboard Press (Presledek):**
- Create Instance: obj_bullet na (x, y-20)
- Set Alarm: 0 na 15 (čas ohladitve)

**Trk z obj_enemy:**
- Add Lives: -1
- Play Sound: snd_hurt
- Jump to Position: (320, 400)

**No More Lives:**
- Show Message: "Game Over!"
- Restart Room

### Objekt Sovražnika

**Create:**
- Set Alarm: 0 na 60

**Alarm 0:**
- Create Instance: obj_enemy_bullet na (x, y+20)
- Set Alarm: 0 na 60 (ponovi)

**Trk z obj_bullet:**
- Add Score: 100
- Play Sound: snd_explosion
- Destroy Instance: self

---

## Nadgradnja na Napredne Prednastavitve

Ko potrebujete več funkcij, razmislite o:
- **Platformna Prednastavitev** - Gravitacija, skakanje, platformne mehanike
- **Polna Prednastavitev** - Vsi razpoložljivi dogodki in akcije

---

## Glejte Tudi

- [Začetna Prednastavitev](Beginner-Preset_sl) - Začnite tukaj, če ste novi
- [Celotna Referenca Akcij](Full-Action-Reference_sl) - Celoten seznam akcij
- [Referenca Dogodkov](Event-Reference_sl) - Celoten seznam dogodkov
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Osnovni koncepti
