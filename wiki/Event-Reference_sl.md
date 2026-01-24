# Referenca Dogodkov

*[Domov](Home_sl) | [Vodic po Presetih](Preset-Guide_sl) | [Popolna Referenca Akcij](Full-Action-Reference_sl)*

Ta stran dokumentira vse razpolozljive dogodke v PyGameMaker. Dogodki so sprozilci, ki izvrsijo akcije, ko se v vasi igri pojavijo dolocene pogoji.

## Kategorije Dogodkov

- [Dogodki Objekta](#dogodki-objekta) - Create, Step, Destroy
- [Dogodki Vnosa](#dogodki-vnosa) - Tipkovnica, Miska
- [Dogodki Trkov](#dogodki-trkov) - Trki objektov
- [Casovni Dogodki](#casovni-dogodki) - Alarmi, Variante Step
- [Dogodki Risanja](#dogodki-risanja) - Prilagojeno izrisovanje
- [Dogodki Sobe](#dogodki-sobe) - Prehodi med sobami
- [Dogodki Igre](#dogodki-igre) - Zacetek/Konec igre
- [Drugi Dogodki](#drugi-dogodki) - Meje, Zivljenja, Zdravje

---

## Dogodki Objekta

### Create
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `create` |
| **Ikona** | 🎯 |
| **Kategorija** | Objekt |
| **Preset** | Zacetnik |

**Opis:** Izvrseno enkrat, ko je instanca prvic ustvarjena.

**Kdaj se sprozi:**
- Ko je instanca postavljena v sobo ob zagonu igre
- Ko je ustvarjena preko akcije "Ustvari Instanco"
- Po prehodih sobe za nove instance

**Pogoste uporabe:**
- Inicializacija spremenljivk
- Nastavitev zacetnih vrednosti
- Konfiguracija zacetnega stanja

---

### Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `step` |
| **Ikona** | ⭐ |
| **Kategorija** | Objekt |
| **Preset** | Zacetnik |

**Opis:** Izvrseno vsak okvir (tipicno 60-krat na sekundo).

**Kdaj se sprozi:** Neprekinjeno, vsak okvir igre.

**Pogoste uporabe:**
- Neprekinjeno gibanje
- Preverjanje pogojev
- Posodabljanje polozajev
- Logika igre

**Opomba:** Bodite previdni z zmogljivostjo - koda tu tece nenehno.

---

### Destroy
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `destroy` |
| **Ikona** | 💥 |
| **Kategorija** | Objekt |
| **Preset** | Srednji |

**Opis:** Izvrseno, ko je instanca unicena.

**Kdaj se sprozi:** Tik preden je instanca odstranjena iz igre.

**Pogoste uporabe:**
- Generiranje ucinkov (eksplozije, delci)
- Spuscanje predmetov
- Posodabljanje rezultatov
- Predvajanje zvokov

---

## Dogodki Vnosa

### Tipkovnica (Neprekinjena)
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard` |
| **Ikona** | ⌨️ |
| **Kategorija** | Vnos |
| **Preset** | Zacetnik |

**Opis:** Sprozi se neprekinjeno, medtem ko je tipka pritisnjena.

**Najboljse za:** Gladko, neprekinjeno gibanje

**Podprte Tipke:**
- Puscicne tipke (gor, dol, levo, desno)
- Crke (A-Z)
- Stevilke (0-9)
- Presledek, Enter, Escape
- Funkcijske tipke (F1-F12)
- Modifikacijske tipke (Shift, Ctrl, Alt)

---

### Pritisk Tipkovnice
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_press` |
| **Ikona** | 🔘 |
| **Kategorija** | Vnos |
| **Preset** | Zacetnik |

**Opis:** Sprozi se enkrat, ko je tipka prvic pritisnjena.

**Najboljse za:** Posamezne akcije (skok, strel, izbira v meniju)

**Razlika od Tipkovnice:** Sprozi se samo enkrat na pritisk, ne med drzanjem.

---

### Sprostitev Tipkovnice
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_release` |
| **Ikona** | ⬆️ |
| **Kategorija** | Vnos |
| **Preset** | Napreden |

**Opis:** Sprozi se enkrat, ko je tipka sproascena.

**Pogoste uporabe:**
- Ustavitev gibanja ob sprostitvi tipke
- Zakljucek polnilnih napadov
- Preklop stanj

---

### Miska
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `mouse` |
| **Ikona** | 🖱️ |
| **Kategorija** | Vnos |
| **Preset** | Srednji |

**Opis:** Dogodki gumbov miske in gibanja.

**Vrste Dogodkov:**

| Vrsta | Opis |
|-------|------|
| Levi Gumb | Klik z levim gumbom miske |
| Desni Gumb | Klik z desnim gumbom miske |
| Srednji Gumb | Klik s srednjim/kolesckom |
| Vstop Miske | Kazalec vstopi v meje instance |
| Izstop Miske | Kazalec izstopi iz mej instance |
| Globalni Levi Gumb | Levi klik kjerkoli |
| Globalni Desni Gumb | Desni klik kjerkoli |

---

## Dogodki Trkov

### Trk
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `collision` |
| **Ikona** | 💥 |
| **Kategorija** | Trk |
| **Preset** | Zacetnik |

**Opis:** Sprozi se, ko se ta instanca prekriva z drugo vrsto objekta.

**Konfiguracija:** Izberite, katera vrsta objekta sprozi ta trk.

**Posebna spremenljivka:** `other` - Referenca na trkajoco instanco.

**Kdaj se sprozi:** Vsak okvir, ko se instance prekrivajo.

**Pogoste uporabe:**
- Zbiranje predmetov
- Prejemanje poskodbe
- Zadevanje sten
- Sprozitev dogodkov

**Primeri dogodkov trkov:**
- `collision_with_obj_coin` - Igralec se dotakne kovanca
- `collision_with_obj_enemy` - Igralec se dotakne sovraznika
- `collision_with_obj_wall` - Instanca zadene steno

---

## Casovni Dogodki

### Alarm
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `alarm` |
| **Ikona** | ⏰ |
| **Kategorija** | Casovni |
| **Preset** | Srednji |

**Opis:** Sprozi se, ko odstevanje alarma doseze nic.

**Razpolozljivi alarmi:** 12 neodvisnih alarmov (alarm[0] do alarm[11])

**Nastavitev alarmov:** Uporabite akcijo "Nastavi Alarm" s koraki (60 korakov ≈ 1 sekunda pri 60 FPS)

**Pogoste uporabe:**
- Casovno generiranje
- Casi ohlajanja
- Zakasneli ucinki
- Ponavljajoce akcije (ponovno nastavite alarm v dogodku alarma)

---

### Begin Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `begin_step` |
| **Ikona** | ▶️ |
| **Kategorija** | Step |
| **Preset** | Napreden |

**Opis:** Sprozi se na zacetku vsakega okvirja, pred rednimi dogodki Step.

**Vrstni red izvajanja:** Begin Step → Step → End Step

**Pogoste uporabe:**
- Obdelava vnosa
- Pred-gibalni izracuni

---

### End Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `end_step` |
| **Ikona** | ⏹️ |
| **Kategorija** | Step |
| **Preset** | Napreden |

**Opis:** Sprozi se na koncu vsakega okvirja, po trkih.

**Pogoste uporabe:**
- Koncne prilagoditve polozaja
- Operacije ciscenja
- Posodobitve stanja po trkih

---

## Dogodki Risanja

### Draw
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw` |
| **Ikona** | 🎨 |
| **Kategorija** | Risanje |
| **Preset** | Srednji |

**Opis:** Sprozi se med fazo izrisovanja.

**Pomembno:** Dodajanje dogodka Draw onemogocia samodejno risanje sprite-a. Ce zelite, da je viden, morate sprite narisati rocno.

**Pogoste uporabe:**
- Prilagojeno izrisovanje
- Risanje oblik
- Prikazovanje besedila
- Vrstice zdravja
- Elementi HUD

**Razpolozljive akcije risanja:**
- Narisi Sprite
- Narisi Besedilo
- Narisi Pravokotnik
- Narisi Krog
- Narisi Crto
- Narisi Vrstico Zdravja

---

## Dogodki Sobe

### Room Start
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `room_start` |
| **Ikona** | 🚪 |
| **Kategorija** | Soba |
| **Preset** | Napreden |

**Opis:** Sprozi se ob vstopu v sobo, po vseh dogodkih Create.

**Pogoste uporabe:**
- Inicializacija sobe
- Predvajanje glasbe sobe
- Nastavitev spremenljivk, specificnih za sobo

---

### Room End
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `room_end` |
| **Ikona** | 🚪 |
| **Kategorija** | Soba |
| **Preset** | Napreden |

**Opis:** Sprozi se ob odhodu iz sobe.

**Pogoste uporabe:**
- Shranjevanje napredka
- Ustavitev glasbe
- Ciscenje

---

## Dogodki Igre

### Game Start
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `game_start` |
| **Ikona** | 🎮 |
| **Kategorija** | Igra |
| **Preset** | Napreden |

**Opis:** Sprozi se enkrat, ko se igra prvic zazene (samo v prvi sobi).

**Pogoste uporabe:**
- Inicializacija globalnih spremenljivk
- Nalaganje shranjenih podatkov
- Predvajanje uvoda

---

### Game End
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `game_end` |
| **Ikona** | 🎮 |
| **Kategorija** | Igra |
| **Preset** | Napreden |

**Opis:** Sprozi se, ko se igra koncuje.

**Pogoste uporabe:**
- Shranjevanje podatkov igre
- Ciscenje virov

---

## Drugi Dogodki

### Outside Room
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `outside_room` |
| **Ikona** | 🚫 |
| **Kategorija** | Drugo |
| **Preset** | Napreden |

**Opis:** Sprozi se, ko je instanca popolnoma zunaj meja sobe.

**Pogoste uporabe:**
- Unicenje izstrelkov zunaj zaslona
- Ovijanje na drugo stran
- Sprozitev konca igre

---

### Intersect Boundary
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `intersect_boundary` |
| **Ikona** | ⚠️ |
| **Kategorija** | Drugo |
| **Preset** | Napreden |

**Opis:** Sprozi se, ko instanca dotakne mejo sobe.

**Pogoste uporabe:**
- Ohranitev igralca znotraj meja
- Odboj od robov

---

### No More Lives
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `no_more_lives` |
| **Ikona** | 💀 |
| **Kategorija** | Drugo |
| **Preset** | Srednji |

**Opis:** Sprozi se, ko zivljenja padejo na 0 ali manj.

**Pogoste uporabe:**
- Zaslon konca igre
- Ponovni zagon igre
- Prikaz koncnega rezultata

---

### No More Health
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `no_more_health` |
| **Ikona** | 💔 |
| **Kategorija** | Drugo |
| **Preset** | Srednji |

**Opis:** Sprozi se, ko zdravje pade na 0 ali manj.

**Pogoste uporabe:**
- Izguba zivljenja
- Ponovno pojavitev igralca
- Sprozitev animacije smrti

---

## Vrstni Red Izvajanja Dogodkov

Razumevanje, kdaj se dogodki sprozijo, pomaga ustvariti predvidljivo obnasanje igre:

1. **Begin Step** - Zacetek okvirja
2. **Alarm** - Vsi sprozeni alarmi
3. **Keyboard/Mouse** - Dogodki vnosa
4. **Step** - Glavna logika igre
5. **Collision** - Po gibanju
6. **End Step** - Po trkih
7. **Draw** - Faza izrisovanja

---

## Dogodki po Presetu

| Preset | Vkljuceni Dogodki |
|--------|-------------------|
| **Zacetnik** | Create, Step, Keyboard Press, Collision |
| **Srednji** | + Draw, Destroy, Mouse, Alarm |
| **Napreden** | + Vse variante tipkovnice, Begin/End Step, Dogodki sobe, Dogodki igre, Dogodki meje |

---

## Glejte Tudi

- [Popolna Referenca Akcij](Full-Action-Reference_sl) - Popoln seznam akcij
- [Preset za Zacetnike](Beginner-Preset_sl) - Bistveni dogodki za zacetnike
- [Srednji Preset](Intermediate-Preset_sl) - Dodatni dogodki
- [Dogodki in Akcije](Events-and-Actions_sl) - Pregled osnovnih konceptov
