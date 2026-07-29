# Začetniški Preset

*[Domov](Home_sl) | [Vodnik po Presetih](Preset-Guide_sl) | [Srednji Preset](Intermediate-Preset_sl)*

**Začetniški** preset je zasnovan za uporabnike, ki so novi v razvoju iger. Ponuja skrbno izbran nabor bistvenih dogodkov in akcij, ki pokrivajo osnove ustvarjanja preprostih 2D iger, ne da bi začetnike preobremenili s prevec možnostmi.

## Pregled

Začetniški preset vključuje:
- **4 vrste dogodkov** - Za odzivanje na situacije v igri
- **17 vrst akcij** - Za nadzor obnašanja igre
- **6 kategorij** - Dogodki, Gibanje, Točke/Življenja/Zdravje, Instanca, Soba, Izhod

---

## Dogodki

Dogodki so prozilci, ki se odzivajo na določene situacije v vaši igri. Ko se dogodek zgodi, se bodo izvedle akcije, ki ste jih definirali za ta dogodek.

### Dogodek Create
| Lastnost | Vrednost |
|----------|----------|
| **Ime bloka** | `event_create` |
| **Kategorija** | Dogodki |
| **Opis** | Sproži se enkrat, ko je instanca prvič ustvarjena |

**Kdaj se sproži:** Takoj, ko je instanca objekta postavljena v sobo ali ustvarjena z akcijo "Ustvari Instanco".

**Pogoste uporabe:**
- Inicializacija spremenljivk
- Nastavitev začetnega položaja
- Nastavitev začetne hitrosti ali smeri
- Ponastavitev točk ob začetku igre

---

### Dogodek Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime bloka** | `event_step` |
| **Kategorija** | Dogodki |
| **Opis** | Sproži se vsak okvir (običajno 60-krat na sekundo) |

**Kdaj se sproži:** Neprekinjeno, vsak okvir igre.

**Pogoste uporabe:**
- Neprekinjeno gibanje
- Preverjanje pogojev
- Posodabljanje stanja igre
- Nadzor animacije

---

### Dogodek Pritiska Tipke
| Lastnost | Vrednost |
|----------|----------|
| **Ime bloka** | `event_keyboard_press` |
| **Kategorija** | Dogodki |
| **Opis** | Sproži se enkrat, ko je določena tipka pritisnjena |

**Kdaj se sproži:** Enkrat v trenutku, ko je tipka pritisnjena (ne medtem ko je drzana).

**Podprte tipke:** Puščične tipke (gor, dol, levo, desno), Preslednica, Enter, črke (A-Z), številke (0-9)

**Pogoste uporabe:**
- Kontrole premikanja igralca
- Skakanje
- Streljanje
- Navigacija po meniju

---

### Dogodek Trka
| Lastnost | Vrednost |
|----------|----------|
| **Ime bloka** | `event_collision` |
| **Kategorija** | Dogodki |
| **Opis** | Sproži se, ko ta instanca trči v drug objekt |

**Kdaj se sproži:** Vsak okvir, ko se dve instanci prekrivata.

**Posebna spremenljivka:** V dogodku trka se `other` nanasa na instanco, s katero je prislo do trka.

**Pogoste uporabe:**
- Zbiranje predmetov (kovanci, ojacitve)
- Prejemanje skode od sovražnikov
- Zadevanje sten ali ovir
- Doseganje ciljev ali kontrolnih točk

---

## Akcije

Akcije so ukazi, ki se izvršijo, ko je dogodek sprožen. Enemu dogodku je mogoce dodati več akcij in se bodo izvršile po vrstnem redu.

---

## Akcije Gibanja

### Nastavi Horizontalno Hitrost
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `set_hspeed` |
| **Ime bloka** | `move_set_hspeed` |
| **Kategorija** | Gibanje |
| **Ikona** | ↔️ |

**Opis:** Nastavi horizontalno hitrost gibanja instance.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Številka | Hitrost v pikslih na okvir. Pozitivno = desno, Negativno = levo |

**Primer:** Nastavite `value` na `4` za premikanje desno s 4 piksli na okvir, ali `-4` za premikanje levo.

---

### Nastavi Vertikalno Hitrost
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `set_vspeed` |
| **Ime bloka** | `move_set_vspeed` |
| **Kategorija** | Gibanje |
| **Ikona** | ↕️ |

**Opis:** Nastavi vertikalno hitrost gibanja instance.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Številka | Hitrost v pikslih na okvir. Pozitivno = dol, Negativno = gor |

**Primer:** Nastavite `value` na `-4` za premikanje gor s 4 piksli na okvir, ali `4` za premikanje dol.

---

### Ustavi Gibanje
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `stop_movement` |
| **Ime bloka** | `move_stop` |
| **Kategorija** | Gibanje |
| **Ikona** | 🛑 |

**Opis:** Ustavi vse gibanje z nastavitvijo horizontalne in vertikalne hitrosti na nic.

**Parametri:** Brez

**Pogoste uporabe:**
- Ustavitev igralca ob zadetku stene
- Ustavitev sovražnikov ob dosegu cilja
- Zacasna prekinitev gibanja

---

### Skoci na Polozaj
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `jump_to_position` |
| **Ime bloka** | `move_jump_to` |
| **Kategorija** | Gibanje |
| **Ikona** | 📍 |

**Opis:** Takoj premakne instanco na določen položaj (brez gladkega gibanja).

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x` | Številka | Ciljna X koordinata |
| `y` | Številka | Ciljna Y koordinata |

**Primer:** Skocite na položaj (100, 200) za teleportacijo igralca na to lokacijo.

---

## Akcije Instance

### Unisti Instanco
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `destroy_instance` |
| **Ime bloka** | `instance_destroy` |
| **Kategorija** | Instanca |
| **Ikona** | 💥 |

**Opis:** Odstrani instanco iz igre.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `target` | Izbira | `self` = unisti to instanco, `other` = unisti trkajočo instanco |

**Pogoste uporabe:**
- Odstranitev zbranih kovancev (`target: other` v dogodku trka)
- Uničenje nabojev ob zadetku necesa
- Odstranitev sovražnikov ob porazu

---

### Ustvari Instanco
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `create_instance` |
| **Ime bloka** | `instance_create` |
| **Kategorija** | Instanca |
| **Ikona** | ✨ |

**Opis:** Ustvari novo instanco objekta na določenem položaju.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `object` | Objekt | Vrsta objekta za ustvarjanje |
| `x` | Številka | X koordinata za novo instanco |
| `y` | Številka | Y koordinata za novo instanco |

**Primer:** Ustvarite naboj na položaju igralca, ko je pritisnjena Preslednica.

---

## Akcije Točk

### Nastavi Točke
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `set_score` |
| **Ime bloka** | `score_set` |
| **Kategorija** | Točke/Življenja/Zdravje |
| **Ikona** | 🏆 |

**Opis:** Nastavi točke na določeno vrednost ali prišteje/odsteje od trenutnih točk.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Številka | Vrednost točk |
| `relative` | Logična | Če je true, prišteje vrednost k trenutnim točkam. Če je false, nastavi točke na vrednost |

**Primeri:**
- Ponastavitev točk: `value: 0`, `relative: false`
- Dodaj 10 točk: `value: 10`, `relative: true`
- Odstej 5 točk: `value: -5`, `relative: true`

---

### Dodaj k Točkam
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `add_score` |
| **Ime bloka** | `score_add` |
| **Kategorija** | Točke/Življenja/Zdravje |
| **Ikona** | ➕🏆 |

**Opis:** Doda vrednost k trenutnim točkam (bliznjica za set_score z relative=true).

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `value` | Številka | Točke za dodajanje (lahko negativno za odštevanje) |

---

### Nariši Točke
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `draw_score` |
| **Ime bloka** | `draw_score` |
| **Kategorija** | Točke/Življenja/Zdravje |
| **Ikona** | 🖼️🏆 |

**Opis:** Prikaze trenutne točke na zaslonu.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `x` | Številka | X položaj za risanje točk |
| `y` | Številka | Y položaj za risanje točk |
| `caption` | Niz | Besedilo za prikaz pred točkami (npr. "Točke: ") |

**Opomba:** To je treba uporabiti v dogodku Draw (na voljo v Srednjem presetu).

---

## Akcije Sobe

### Pojdi v Naslednjo Sobo
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `next_room` |
| **Ime bloka** | `room_goto_next` |
| **Kategorija** | Soba |
| **Ikona** | ➡️ |

**Opis:** Preide v naslednjo sobo v vrstnem redu sob.

**Parametri:** Brez

**Opomba:** Če ste ze v zadnji sobi, ta akcija nima učinka (uporabite "Če Naslednja Soba Obstaja" za preverjanje najprej).

---

### Pojdi v Prejsnjo Sobo
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `previous_room` |
| **Ime bloka** | `room_goto_previous` |
| **Kategorija** | Soba |
| **Ikona** | ⬅️ |

**Opis:** Preide v prejsnjo sobo v vrstnem redu sob.

**Parametri:** Brez

**Opomba:** Če ste ze v prvi sobi, ta akcija nima učinka.

---

### Ponovno Zazeni Sobo
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `restart_room` |
| **Ime bloka** | `room_restart` |
| **Kategorija** | Soba |
| **Ikona** | 🔄 |

**Opis:** Ponovno zazene trenutno sobo in ponastavi vse instance v začetno stanje.

**Parametri:** Brez

**Pogoste uporabe:**
- Ponovni zagon nivoja po smrti igralca
- Ponastavitev uganke po neuspehu
- Ponovitev mini-igre

---

### Pojdi v Sobo
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `goto_room` |
| **Ime bloka** | `room_goto` |
| **Kategorija** | Soba |
| **Ikona** | 🚪 |

**Opis:** Preide v določeno sobo po imenu.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `room` | Soba | Soba, v katero želite iti |

---

### Če Naslednja Soba Obstaja
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `if_next_room_exists` |
| **Ime bloka** | `room_if_next_exists` |
| **Kategorija** | Soba |
| **Ikona** | ❓➡️ |

**Opis:** Pogojni blok, ki izvede vsebovane akcije samo če obstaja naslednja soba.

**Parametri:** Brez (akcije so postavljene znotraj bloka)

**Pogoste uporabe:**
- Preverjanje pred prehodom v naslednjo sobo
- Prikaz sporocila "Zmagali ste!" če ni več sob

---

### Če Prejsnja Soba Obstaja
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `if_previous_room_exists` |
| **Ime bloka** | `room_if_previous_exists` |
| **Kategorija** | Soba |
| **Ikona** | ❓⬅️ |

**Opis:** Pogojni blok, ki izvede vsebovane akcije samo če obstaja prejsnja soba.

**Parametri:** Brez (akcije so postavljene znotraj bloka)

---

## Akcije Izhoda

### Prikaži Sporocilo
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `show_message` |
| **Ime bloka** | `output_message` |
| **Kategorija** | Izhod |
| **Ikona** | 💬 |

**Opis:** Prikaze pojavno okno s sporocilom igralcu.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `message` | Niz | Besedilo za prikaz |

**Opomba:** Igra se zaustavi, medtem ko je sporocilo prikazano. Igralec mora klikniti V redu za nadaljevanje.

**Pogoste uporabe:**
- Navodila za igro
- Zgodbeni dialog
- Sporocila o zmagi/porazu
- Informacije za razhroscevanje

---

### Izvedi Kodo
| Lastnost | Vrednost |
|----------|----------|
| **Ime akcije** | `execute_code` |
| **Ime bloka** | `execute_code` |
| **Kategorija** | Izhod |
| **Ikona** | 💻 |

**Opis:** Izvede poljubno Python kodo.

**Parametri:**
| Parameter | Tip | Opis |
|-----------|-----|------|
| `code` | Niz | Python koda za izvedbo |

**Opomba:** To je napredna funkcija. Uporabljajte previdno, saj lahko nepravilna koda povzroci napake.

---

## Povzetek Kategorij

| Kategorija | Dogodki | Akcije |
|------------|---------|--------|
| **Dogodki** | Create, Step, Pritisk Tipke, Trk | - |
| **Gibanje** | - | Nastavi Horizontalno Hitrost, Nastavi Vertikalno Hitrost, Ustavi Gibanje, Skoci na Polozaj |
| **Instanca** | - | Unisti Instanco, Ustvari Instanco |
| **Točke/Življenja/Zdravje** | - | Nastavi Točke, Dodaj Točke, Nariši Točke |
| **Soba** | - | Naslednja Soba, Prejsnja Soba, Ponovno Zazeni Sobo, Pojdi v Sobo, Če Naslednja Soba Obstaja, Če Prejsnja Soba Obstaja |
| **Izhod** | - | Prikaži Sporocilo, Izvedi Kodo |

---

## Primer: Preprosta Igra Zbiranja Kovancev

Tukaj je opisano, kako nastaviti osnovno igro zbiranja kovancev z uporabo samo funkcij Začetniškega preseta:

### Objekt Igralca (obj_player)

**Pritisk Tipke (Leva Puščica):**
- Nastavi Horizontalno Hitrost: -4

**Pritisk Tipke (Desna Puščica):**
- Nastavi Horizontalno Hitrost: 4

**Pritisk Tipke (Puščica Gor):**
- Nastavi Vertikalno Hitrost: -4

**Pritisk Tipke (Puščica Dol):**
- Nastavi Vertikalno Hitrost: 4

**Trk z obj_coin:**
- Nastavi Točke: 10 (relative: true)
- Unisti Instanco: other

**Trk z obj_wall:**
- Ustavi Gibanje

**Trk z obj_goal:**
- Nastavi Točke: 100 (relative: true)
- Naslednja Soba

### Objekt Kovanec (obj_coin)
Dogodki niso potrebni - samo zbiralni predmet.

### Objekt Stena (obj_wall)
Dogodki niso potrebni - samo trdna ovira.

### Objekt Cilj (obj_goal)
Dogodki niso potrebni - sproži zakljucek nivoja, ko igralec trči.

---

## Nadgradnja na Srednji

Ko boste zadovoljni z Začetniškim presetom, razmislite o nadgradnji na **Srednji** za dostop do:
- Dogodek Draw (za prilagojeno upodabljanje)
- Dogodek Destroy (čiščenje ob uničenju instance)
- Dogodkov Miške (zaznavanje klikov)
- Dogodkov Alarma (časovno določene akcije)
- Sistemov Življenj in Zdravja
- Akcij Zvoka in Glasbe
- Več možnosti gibanja (smer, premikanje proti)

---

## Oglejte si Tudi

- [Vadnice](Tutorials_sl) - Vse vadnice na enem mestu
- [Srednji Preset](Intermediate-Preset_sl) - Funkcije naslednje stopnje
- [Popolna Referenca Akcij](Full-Action-Reference_sl) - Celoten seznam akcij
- [Referenca Dogodkov](Event-Reference_sl) - Celoten seznam dogodkov
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Temeljni koncepti
- [Ustvarjanje Vase Prve Igre](Prva_Igra_sl) - Vodnik po korakih
- [Vadnica Pong](Tutorial-Pong_sl) - Ustvarite klasicno igro Pong za dva igralca
- [Vadnica Breakout](Tutorial-Breakout_sl) - Ustvarite klasicno igro Breakout
- [Uvod v Ustvarjanje Iger](Getting-Started-Breakout_sl) - Celovita vadnica za začetnike
