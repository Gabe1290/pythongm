# Referenca Dogodkov

*[Domov](Home_sl) | [Vodič po Presetih](Preset-Guide_sl) | [Popolna Referenca Akcij](Full-Action-Reference_sl)*

Ta stran dokumentira vse razpoložljive dogodke v PyGameMaker. Dogodki so sprožilci, ki izvršijo akcije, ko se v vaši igri pojavijo določene pogoji.

## Kategorije Dogodkov

- [Dogodki Objekta](#dogodki-objekta) - Create, Step, Destroy
- [Dogodki Vnosa](#dogodki-vnosa) - Tipkovnica, Miška
- [Dogodki Trkov](#dogodki-trkov) - Trki objektov
- [Časovni Dogodki](#časovni-dogodki) - Alarmi, Variante Step
- [Dogodki Risanja](#dogodki-risanja) - Prilagojeno izrisovanje
- [Dogodki Sobe](#dogodki-sobe) - Prehodi med sobami
- [Dogodki Igre](#dogodki-igre) - Začetek/Konec igre
- [Drugi Dogodki](#drugi-dogodki) - Meje, Življenja, Zdravje

---

## Dogodki Objekta

### Create
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `create` |
| **Ikona** | 🎯 |
| **Kategorija** | Objekt |
| **Preset** | Začetnik |

**Opis:** Izvršeno enkrat, ko je instanca prvič ustvarjena.

**Kdaj se sproži:**
- Ko je instanca postavljena v sobo ob zagonu igre
- Ko je ustvarjena preko akcije "Ustvari Instanco"
- Po prehodih sobe za nove instance

**Pogoste uporabe:**
- Inicializacija spremenljivk
- Nastavitev začetnih vrednosti
- Konfiguracija začetnega stanja

---

### Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `step` |
| **Ikona** | ⭐ |
| **Kategorija** | Objekt |
| **Preset** | Začetnik |

**Opis:** Izvršeno vsak okvir (tipično 60-krat na sekundo).

**Kdaj se sproži:** Neprekinjeno, vsak okvir igre.

**Pogoste uporabe:**
- Neprekinjeno gibanje
- Preverjanje pogojev
- Posodabljanje položajev
- Logika igre

**Opomba:** Bodite previdni z zmogljivostjo - koda tu teče nenehno.

---

### Destroy
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `destroy` |
| **Ikona** | 💥 |
| **Kategorija** | Objekt |
| **Preset** | Srednji |

**Opis:** Izvršeno, ko je instanca uničena.

**Kdaj se sproži:** Tik preden je instanca odstranjena iz igre.

**Pogoste uporabe:**
- Generiranje učinkov (eksplozije, delci)
- Spuščanje predmetov
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
| **Preset** | Začetnik |

**Opis:** Sproži se neprekinjeno, medtem ko je tipka pritisnjena.

**Najboljše za:** Gladko, neprekinjeno gibanje

**Podprte Tipke:**
- Puščične tipke (gor, dol, levo, desno)
- Črke (A-Z)
- Številke (0-9)
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
| **Preset** | Začetnik |

**Opis:** Sproži se enkrat, ko je tipka prvič pritisnjena.

**Najboljše za:** Posamezne akcije (skok, strel, izbira v meniju)

**Razlika od Tipkovnice:** Sproži se samo enkrat na pritisk, ne med drzanjem.

---

### Sprostitev Tipkovnice
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_release` |
| **Ikona** | ⬆️ |
| **Kategorija** | Vnos |
| **Preset** | Napreden |

**Opis:** Sproži se enkrat, ko je tipka sproščena.

**Pogoste uporabe:**
- Ustavitev gibanja ob sprostitvi tipke
- Zaključek polnilnih napadov
- Preklop stanj

---

### Tipkovnica (Nobene tipke)
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_no_key` |
| **Ikona** | ⌨️ |
| **Kategorija** | Vnos |
| **Preset** | Napreden |

**Opis:** Sproži se ob vsakem sličici, medtem ko **nobena** tipka ni pritisnjena.

**Kdaj se sproži:** Ob vsaki sličici, ko je tipkovnica nedejavna, *pred* dogodkom Step.

**Pogoste uporabe:**
- Ustavitev gibanja, ko igralec sprosti vse tipke (igre na mreži/labirinti)
- Animacije mirovanja

---

### Miška
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `mouse` |
| **Ikona** | 🖱️ |
| **Kategorija** | Vnos |
| **Preset** | Srednji |

**Opis:** Dogodki gumbov miške in gibanja.

**Vrste Dogodkov:**

| Vrsta | Opis |
|-------|------|
| Levi Gumb | Klik z levim gumbom miške |
| Desni Gumb | Klik z desnim gumbom miške |
| Srednji Gumb | Klik s srednjim/koleščkom |
| Vstop Miške | Kazalec vstopi v meje instance |
| Izstop Miške | Kazalec izstopi iz mej instance |
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
| **Preset** | Začetnik |

**Opis:** Sproži se, ko se ta instanca prekriva z drugo vrsto objekta.

**Konfiguracija:** Izberite, katera vrsta objekta sproži ta trk.

**Posebna spremenljivka:** `other` - Referenca na trkajočo instanco.

**Kdaj se sproži:** Vsak okvir, ko se instance prekrivajo.

**Pogoste uporabe:**
- Zbiranje predmetov
- Prejemanje poškodbe
- Zadevanje sten
- Sprožitev dogodkov

**Primeri dogodkov trkov:**
- `collision_with_obj_coin` - Igralec se dotakne kovanca
- `collision_with_obj_enemy` - Igralec se dotakne sovražnika
- `collision_with_obj_wall` - Instanca zadene steno

---

## Časovni Dogodki

### Alarm
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `alarm` |
| **Ikona** | ⏰ |
| **Kategorija** | Časovni |
| **Preset** | Srednji |

**Opis:** Sproži se, ko odštevanje alarma doseže nic.

**Razpoložljivi alarmi:** 12 neodvisnih alarmov (alarm[0] do alarm[11])

**Nastavitev alarmov:** Uporabite akcijo "Nastavi Alarm" s koraki (60 korakov ≈ 1 sekunda pri 60 FPS)

**Pogoste uporabe:**
- Časovno generiranje
- Časi ohlajanja
- Zakasneli učinki
- Ponavljajoče akcije (ponovno nastavite alarm v dogodku alarma)

---

### Begin Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `begin_step` |
| **Ikona** | ▶️ |
| **Kategorija** | Step |
| **Preset** | Napreden |

**Opis:** Sproži se na začetku vsakega okvirja, pred rednimi dogodki Step.

**Vrstni red izvajanja:** Begin Step → Step → End Step

**Pogoste uporabe:**
- Obdelava vnosa
- Pred-gibalni izračuni

---

### End Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `end_step` |
| **Ikona** | ⏹️ |
| **Kategorija** | Step |
| **Preset** | Napreden |

**Opis:** Sproži se na koncu vsakega okvirja, po trkih.

**Pogoste uporabe:**
- Končne prilagoditve položaja
- Operacije čiščenja
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

**Opis:** Sproži se med fazo izrisovanja.

**Pomembno:** Dodajanje dogodka Draw onemogoča samodejno risanje sprite-a. Če želite, da je viden, morate sprite narisati ročno.

**Pogoste uporabe:**
- Prilagojeno izrisovanje
- Risanje oblik
- Prikazovanje besedila
- Vrstice zdravja
- Elementi HUD

**Razpoložljive akcije risanja:**
- Nariši Sprite
- Nariši Besedilo
- Nariši Pravokotnik
- Nariši Krog
- Nariši Črto
- Nariši Vrstico Zdravja

---

### Draw GUI
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw_gui` |
| **Ikona** | 🖥️ |
| **Kategorija** | Risanje |
| **Preset** | Napreden |

**Opis:** Riše v **zaslonskem prostoru (GUI)**, čez sobo in neodvisno od drsenja pogledov/kamere.

**Razlika od Draw:** navadni dogodek Draw je v koordinatah sobe (drsi s pogledom); Draw GUI ostane pritrjen na zaslon — uporabite ga za HUD, rezultate in menije.

---

## Dogodki Sobe

### Room Start
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `room_start` |
| **Ikona** | 🚪 |
| **Kategorija** | Soba |
| **Preset** | Napreden |

**Opis:** Sproži se ob vstopu v sobo, po vseh dogodkih Create.

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

**Opis:** Sproži se ob odhodu iz sobe.

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

**Opis:** Sproži se enkrat, ko se igra prvič zazene (samo v prvi sobi).

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

**Opis:** Sproži se, ko se igra koncuje.

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

**Opis:** Sproži se, ko je instanca popolnoma zunaj meja sobe.

**Pogoste uporabe:**
- Uničenje izstrelkov zunaj zaslona
- Ovijanje na drugo stran
- Sprožitev konca igre

---

### Intersect Boundary
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `intersect_boundary` |
| **Ikona** | ⚠️ |
| **Kategorija** | Drugo |
| **Preset** | Napreden |

**Opis:** Sproži se, ko instanca dotakne mejo sobe.

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

**Opis:** Sproži se, ko življenja padejo na 0 ali manj.

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

**Opis:** Sproži se, ko zdravje pade na 0 ali manj.

**Pogoste uporabe:**
- Izguba življenja
- Ponovno pojavitev igralca
- Sprožitev animacije smrti

---

### Animation End
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `animation_end` |
| **Ikona** | 🎞️ |
| **Kategorija** | Drugo |
| **Preset** | Napreden |

**Opis:** Sproži se, ko animacija spritea instance dokonča celoten cikel (se vrne z zadnje sličice na prvo).

**Pogoste uporabe:**
- Uničenje enkratnega učinka (eksplozija) po enkratnem predvajanju
- Preklop na drugo animacijo, ko se trenutna konča
- Napredovanje stanjskega avtomata ob koncu animacije

---

## Vrstni Red Izvajanja Dogodkov

Razumevanje, kdaj se dogodki sprožijo, pomaga ustvariti predvidljivo obnašanje igre:

1. **Begin Step** - Začetek okvirja
2. **Alarm** - Vsi sproženi alarmi
3. **Keyboard/Mouse** - Dogodki vnosa
4. **Step** - Glavna logika igre
5. **Collision** - Po gibanju
6. **End Step** - Po trkih
7. **Draw** - Faza izrisovanja

---

## Dogodki po Presetu

| Preset | Vkljuceni Dogodki |
|--------|-------------------|
| **Začetnik** | Create, Step, Keyboard Press, Collision |
| **Srednji** | + Draw, Destroy, Mouse, Alarm |
| **Napreden** | + Vse variante tipkovnice, Begin/End Step, Dogodki sobe, Dogodki igre, Dogodki meje |

---

## Glejte Tudi

- [Popolna Referenca Akcij](Full-Action-Reference_sl) - Popoln seznam akcij
- [Preset za Začetnike](Beginner-Preset_sl) - Bistveni dogodki za začetnike
- [Srednji Preset](Intermediate-Preset_sl) - Dodatni dogodki
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Pregled osnovnih konceptov
