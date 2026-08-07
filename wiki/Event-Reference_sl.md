# Referenca Dogodkov

*[Domov](Home_sl) | [Vodič po Presetih](Preset-Guide_sl) | [Popolna Referenca Akcij](Full-Action-Reference_sl)*

Ta stran dokumentira vse razpoložljive dogodke v PyGameMaker. Dogodki so sprožilci, ki izvršijo akcije, ko se v vaši igri pojavijo določeni pogoji.

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
| **Preset** | Srednji |

**Opis:** Sproži se enkrat, ko je tipka prvič pritisnjena.

**Najboljše za:** Posamezne akcije (skok, strel, izbira v meniju)

**Razlika od Tipkovnice:** Sproži se samo enkrat na pritisk, ne med držanjem.

---

### Sprostitev Tipkovnice
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_release` |
| **Ikona** | ⬆️ |
| **Kategorija** | Vnos |
| **Preset** | Popoln (Razvojna izdaja) |

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
| **Preset** | Začetnik |

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
| **Preset** | Popoln (Razvojna izdaja) |

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
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

**Opis:** Sproži se ob vstopu v sobo, po vseh dogodkih Create.

**Pogoste uporabe:**
- Inicializacija sobe
- Predvajanje glasbe sobe
- Nastavitev spremenljivk, specifičnih za sobo

---

### Room End
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `room_end` |
| **Ikona** | 🚪 |
| **Kategorija** | Soba |
| **Preset** | Začetnik |

**Opis:** Sproži se ob odhodu iz sobe.

**Pogoste uporabe:**
- Shranjevanje napredka
- Ustavitev glasbe
- Čiščenje

---

## Dogodki Igre

### Game Start
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `game_start` |
| **Ikona** | 🎮 |
| **Kategorija** | Igra |
| **Preset** | Začetnik |

**Opis:** Sproži se enkrat, ko se igra prvič zažene (samo v prvi sobi).

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
| **Preset** | Začetnik |

**Opis:** Sproži se, ko se igra konča.

**Pogoste uporabe:**
- Shranjevanje podatkov igre
- Čiščenje virov

---

## Drugi Dogodki

### Outside Room
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `outside_room` |
| **Ikona** | 🚫 |
| **Kategorija** | Drugo |
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

**Opis:** Sproži se, ko življenja padejo na 0 ali manj.

**Pogoste uporabe:**
- Zaslon konca igre
- Ponovni zagon igre
- Prikaz končnega rezultata

---

### No More Health
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `no_more_health` |
| **Ikona** | 💔 |
| **Kategorija** | Drugo |
| **Preset** | Začetnik |

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
| **Preset** | Začetnik |

**Opis:** Sproži se, ko animacija spritea instance dokonča celoten cikel (se vrne z zadnje sličice na prvo).

**Pogoste uporabe:**
- Uničenje enkratnega učinka (eksplozija) po enkratnem predvajanju
- Preklop na drugo animacijo, ko se trenutna konča
- Napredovanje stanjskega avtomata ob koncu animacije

---

## Vrstni Red Izvajanja Dogodkov

Razumevanje, kdaj se dogodki sprožijo, pomaga ustvariti predvidljivo
obnašanje igre (preverjeno proti glavni zanki v
`runtime/game_runner.py`):

1. **Begin Step** — Začetek sličice
2. **Alarm** — Vsi sproženi alarmi odštevajo in se sprožijo
3. **Step** (in **Keyboard (pridržana)**) — Glavna logika igre, nato
   neprekinjena preverjanja pridržanih tipk za isto instanco
4. **Keyboard Press/Release, Mouse** — Nakopičeni dogodki vnosa za to
   sličico se obdelajo (to se zgodi *po* Step, ne pred njim — koda v
   Step reagira na tipke, ki so bile pritisnjene že na *začetku*
   sličice, ne na tiste, pritisnjene med njo)
5. **Gibanje, nato Trk** — Uveljavi se fizika (gravitacija/trenje/
   hspeed/vspeed), nato se zaznajo trki in sprožijo njihovi dogodki
6. **End Step** (in **Destroy**) — Po trkih
7. **Draw** — Faza izrisovanja

---

## Dogodki po Presetu

Preverjeno proti `events.event_types.get_available_events()`,
napolnjeni z vsako pravo prednastavitvijo iz
`config/blockly_config.py` — za to, kaj "preset" dejansko omeji (tako
izbirnik Blockly kot strukturiran panel Events/Actions) in kako se
določi prednastavitev projekta, glejte [Vodnik po
Prednastavitvah](Preset-Guide_sl).

| Preset | Vključeni Dogodki |
|--------|-------------------|
| **Začetnik** (19 dogodkov) | Create, Step, Keyboard (pridržana), Keyboard \<Brez Tipke\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Srednji** (21 dogodkov) | + Destroy, Keyboard Press |
| **Popoln** (samo Razvojna izdaja, 23 dogodkov) | + Keyboard Release, Mouse |

---

## Glejte Tudi

- [Popolna Referenca Akcij](Full-Action-Reference_sl) - Popoln seznam akcij
- [Preset za Začetnike](Beginner-Preset_sl) - Bistveni dogodki za začetnike
- [Srednji Preset](Intermediate-Preset_sl) - Dodatni dogodki
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Pregled osnovnih konceptov
