# Vmesna Prednastavitev

*[Domov](Home_sl) | [Vodic po Prednastavitvah](Preset-Guide_sl) | [Zacetna Prednastavitev](Beginner-Preset_sl)*

**Vmesna** prednastavitev nadgrajuje [Zacetno Prednastavitev](Beginner-Preset_sl) z dodajanjem naprednejsih dogodkov in akcij. Zasnovana je za uporabnike, ki so obvladali osnove in zelijo ustvariti bolj kompleksne igre z funkcijami, kot so casovno doloceni dogodki, zvok, zivljenja in zdravstveni sistemi.

## Pregled

Vmesna prednastavitev vkljucuje vse iz Zacetne, plus:
- **4 Dodatne Vrste Dogodkov** - Risanje, Unicenje, Miska, Alarm
- **12 Dodatnih Vrst Akcij** - Zivljenja, Zdravje, Zvok, Casovnik in vec moznosti gibanja
- **3 Dodatne Kategorije** - Casovnik, Zvok, Risanje

---

## Dodatni Dogodki (Preko Zacetnega)

### Dogodek Risanja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_draw` |
| **Kategorija** | Risanje |
| **Ikona** | 🎨 |
| **Opis** | Sprozi se, ko je potrebno izrisati objekt |

**Kdaj se sprozi:** Vsako slicico med fazo risanja, po vseh step dogodkih.

**Pomembno:** Ko dodate dogodek Risanja, se privzeto risanje sprite-a onemogoci. Ce zelite, da je viden, morate sprite narisati rocno.

**Pogoste uporabe:**
- Prilagojeno izrisovanje
- Risanje zdravstvenih pasic
- Prikaz besedila
- Risanje oblik in ucinkov
- Elementi vmesnika

---

### Dogodek Unicenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_destroy` |
| **Kategorija** | Objekt |
| **Ikona** | 💥 |
| **Opis** | Sprozi se, ko je instanca unicena |

**Kdaj se sprozi:** Tik preden je instanca odstranjena iz igre.

**Pogoste uporabe:**
- Ustvarjanje eksplozijskih ucinkov
- Izpustenje predmetov
- Predvajanje zvoka smrti
- Posodobitev rezultata
- Generiranje delcev

---

### Dogodek Miske
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_mouse` |
| **Kategorija** | Vnos |
| **Ikona** | 🖱️ |
| **Opis** | Sprozi se ob interakcijah z misko |

**Vrste dogodkov miske:**
- Levi gumb (pritisk, sprostitev, drzanje)
- Desni gumb (pritisk, sprostitev, drzanje)
- Srednji gumb (pritisk, sprostitev, drzanje)
- Miska vstopi (kazalec vstopi v instanco)
- Miska izstopi (kazalec zapusti instanco)
- Globalni dogodki miske (kjerkoli na zaslonu)

**Pogoste uporabe:**
- Klikljivi gumbi
- Vleci in spusti
- Ucinki lebdenja
- Interakcije z menijem

---

### Dogodek Alarma
| Lastnost | Vrednost |
|----------|----------|
| **Ime Bloka** | `event_alarm` |
| **Kategorija** | Casovnik |
| **Ikona** | ⏰ |
| **Opis** | Sprozi se, ko casovnik alarma doseze nic |

**Kdaj se sprozi:** Ko ustrezno odstevanje alarma doseze 0.

**Razpolozljivi alarmi:** 12 neodvisnih alarmov (0-11)

**Pogoste uporabe:**
- Casovno generiranje
- Zakasnela dejanja
- Casi ohladitve
- Casovno usklajevanje animacij
- Periodicni dogodki

---

## Dodatne Akcije (Preko Zacetnega)

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
| `direction` | Stevilo | Smer v stopinjah (0=desno, 90=gor, 180=levo, 270=dol) |
| `speed` | Stevilo | Hitrost gibanja |

---

#### Premik Proti Tocki
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `move_towards` |
| **Ime Bloka** | `move_towards` |
| **Kategorija** | Gibanje |

**Opis:** Premik proti doloceni poziciji.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x` | Stevilo/Izraz | Ciljna X koordinata |
| `y` | Stevilo/Izraz | Ciljna Y koordinata |
| `speed` | Stevilo | Hitrost gibanja |

---

### Akcije Casovnika

#### Nastavi Alarm
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `set_alarm` |
| **Ime Bloka** | `set_alarm` |
| **Kategorija** | Casovnik |
| **Ikona** | ⏰ |

**Opis:** Nastavite alarm, ki se sprozi po dolocenem stevilu korakov.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `alarm` | Stevilo | Stevilka alarma (0-11) |
| `steps` | Stevilo | Koraki do sprozitve alarma (pri 60 FPS, 60 korakov = 1 sekunda) |

**Primer:** Nastavite alarm 0 na 180 korakov za 3-sekundni zamik.

---

### Akcije Zivljenj

#### Nastavi Zivljenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `set_lives` |
| **Ime Bloka** | `lives_set` |
| **Kategorija** | Rezultat/Zivljenja/Zdravje |
| **Ikona** | ❤️ |

**Opis:** Nastavite stevilo zivljenj.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Stevilo | Vrednost zivljenj |
| `relative` | Logicna | Ce je true, pristeje k trenutnim zivljenjem |

---

#### Dodaj Zivljenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `add_lives` |
| **Ime Bloka** | `lives_add` |
| **Kategorija** | Rezultat/Zivljenja/Zdravje |
| **Ikona** | ➕❤️ |

**Opis:** Dodaj ali odstej zivljenja.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Stevilo | Kolicina za dodajanje (negativno za odstevanje) |

**Opomba:** Ko zivljenja dosezejo 0, se sprozi dogodek `no_more_lives`.

---

#### Narisi Zivljenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `draw_lives` |
| **Ime Bloka** | `draw_lives` |
| **Kategorija** | Rezultat/Zivljenja/Zdravje |
| **Ikona** | 🖼️❤️ |

**Opis:** Prikazi zivljenja na zaslonu.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x` | Stevilo | X pozicija |
| `y` | Stevilo | Y pozicija |
| `sprite` | Sprite | Neobvezen sprite za uporabo kot ikona zivljenja |

---

### Akcije Zdravja

#### Nastavi Zdravje
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `set_health` |
| **Ime Bloka** | `health_set` |
| **Kategorija** | Rezultat/Zivljenja/Zdravje |
| **Ikona** | 💚 |

**Opis:** Nastavite vrednost zdravja (0-100).

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Stevilo | Vrednost zdravja (0-100) |
| `relative` | Logicna | Ce je true, pristeje k trenutnemu zdravju |

---

#### Dodaj Zdravje
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `add_health` |
| **Ime Bloka** | `health_add` |
| **Kategorija** | Rezultat/Zivljenja/Zdravje |
| **Ikona** | ➕💚 |

**Opis:** Dodaj ali odstej zdravje.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Stevilo | Kolicina za dodajanje (negativno za poskodbe) |

**Opomba:** Ko zdravje doseze 0, se sprozi dogodek `no_more_health`.

---

#### Narisi Zdravstveno Pasico
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `draw_health_bar` |
| **Ime Bloka** | `draw_health_bar` |
| **Kategorija** | Rezultat/Zivljenja/Zdravje |
| **Ikona** | 📊💚 |

**Opis:** Narisanje zdravstvene pasice na zaslonu.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x1` | Stevilo | Leva X pozicija |
| `y1` | Stevilo | Zgornja Y pozicija |
| `x2` | Stevilo | Desna X pozicija |
| `y2` | Stevilo | Spodnja Y pozicija |
| `back_color` | Barva | Barva ozadja |
| `bar_color` | Barva | Barva zdravstvene pasice |

---

### Zvocne Akcije

#### Predvajaj Zvok
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `play_sound` |
| **Ime Bloka** | `sound_play` |
| **Kategorija** | Zvok |
| **Ikona** | 🔊 |

**Opis:** Predvajanje zvocnega ucinka.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `sound` | Zvok | Zvocni vir za predvajanje |
| `loop` | Logicna | Ali naj se zvok ponavlja |

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
| `loop` | Logicna | Ali naj se ponavlja (obicajno true za glasbo) |

---

#### Ustavi Glasbo
| Lastnost | Vrednost |
|----------|----------|
| **Ime Akcije** | `stop_music` |
| **Ime Bloka** | `music_stop` |
| **Kategorija** | Zvok |
| **Ikona** | 🔇 |

**Opis:** Ustavite vso trenutno predvajajoco glasbo.

**Parametri:** Brez

---

## Celoten Seznam Funkcij

### Dogodki v Vmesni Prednastavitvi

| Dogodek | Kategorija | Opis |
|---------|------------|------|
| Create | Objekt | Instanca ustvarjena |
| Step | Objekt | Vsako slicico |
| Destroy | Objekt | Instanca unicena |
| Draw | Risanje | Faza izrisovanja |
| Keyboard Press | Vnos | Tipka pritisnjena enkrat |
| Mouse | Vnos | Interakcije z misko |
| Collision | Trk | Prekrivanje instanc |
| Alarm | Casovnik | Casovnik dosegel nic |

### Akcije v Vmesni Prednastavitvi

| Kategorija | Akcije |
|------------|--------|
| **Gibanje** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards |
| **Instanca** | Create, Destroy |
| **Rezultat** | Set Score, Add Score, Draw Score |
| **Zivljenja** | Set Lives, Add Lives, Draw Lives |
| **Zdravje** | Set Health, Add Health, Draw Health Bar |
| **Soba** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Casovnik** | Set Alarm |
| **Zvok** | Play Sound, Play Music, Stop Music |
| **Izhod** | Show Message, Execute Code |

---

## Primer: Strelska Igra z Zivljenji

### Objekt Igralca

**Create:**
- Set Lives: 3

**Keyboard Press (Presledek):**
- Create Instance: obj_bullet na (x, y-20)
- Set Alarm: 0 na 15 (cas ohladitve)

**Trk z obj_enemy:**
- Add Lives: -1
- Play Sound: snd_hurt
- Jump to Position: (320, 400)

**No More Lives:**
- Show Message: "Game Over!"
- Restart Room

### Objekt Sovraznika

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

Ko potrebujete vec funkcij, razmislite o:
- **Platformna Prednastavitev** - Gravitacija, skakanje, platformne mehanike
- **Polna Prednastavitev** - Vsi razpolozljivi dogodki in akcije

---

## Glejte Tudi

- [Zacetna Prednastavitev](Beginner-Preset_sl) - Zacnite tukaj, ce ste novi
- [Celotna Referenca Akcij](Full-Action-Reference_sl) - Celoten seznam akcij
- [Referenca Dogodkov](Event-Reference_sl) - Celoten seznam dogodkov
- [Dogodki in Akcije](Events-and-Actions_sl) - Osnovni koncepti
