# Dogodki in Akcije

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Nazaj na začetno stran](Home_sl)

To je popolna referenca vseh dogodkov in akcij, ki so na voljo v PyGameMaker.

---

## Referenca Dogodkov

### Dogodek Create
**Kdaj:** Enkrat, ko je instanca ustvarjena
**Uporaba:** Inicializacija, nastavljanje spremenljivk, zagon časovnikov

### Dogodek Destroy
**Kdaj:** Ko je instanca uničena
**Uporaba:** Čiščenje, ustvarjanje učinkov, dodeljevanje točk

### Dogodki Step

| Dogodek | Kdaj |
|-----------|-------|
| **Step** | Vsako sličico (60-krat na sekundo) |
| **Begin Step** | Pred preverjanji trkov |
| **End Step** | Po vseh drugih dogodkih |

### Dogodki Alarm

| Dogodek | Kdaj |
|-----------|-------|
| **Alarm[0-11]** | Ko števec doseže 0 |

Uporabite akcijo `Set Alarm`, da zaženete odštevanje. Vrednosti alarma so v sličicah (60 = 1 sekunda pri 60 FPS).

### Dogodki Tipkovnice

| Dogodek | Kdaj |
|-----------|-------|
| **Keyboard [Tipka]** | Dokler je tipka pridržana (ponavlja se) |
| **Key Press [Tipka]** | Enkrat, ko je tipka pritisnjena |
| **Key Release [Tipka]** | Enkrat, ko je tipka spuščena |
| **No Key** | Ko ni pritisnjena nobena tipka |

Razpoložljive tipke: črke (A-Z), številke (0-9), puščične tipke, preslednica, Enter, Shift, Ctrl, Alt, funkcijske tipke (F1-F12)

### Dogodki Miške

| Dogodek | Kdaj |
|-----------|-------|
| **Left Button** | Levi klik na instanco |
| **Right Button** | Desni klik na instanco |
| **Middle Button** | Klik s srednjim gumbom na instanco |
| **Left Press** | Levi gumb pritisnjen (enkrat) |
| **Left Release** | Levi gumb spuščen (enkrat) |
| **Mouse Enter** | Kazalec vstopi v instanco |
| **Mouse Leave** | Kazalec zapusti instanco |
| **Global Left Button** | Levi klik kjerkoli |
| **Global Right Button** | Desni klik kjerkoli |

### Dogodki Trkov

| Dogodek | Kdaj |
|-----------|-------|
| **Collision with [Objekt]** | Ob stiku z navedenim objektom |

Preverjanja trkov potekajo med dogodkoma Step in Draw.

### Ostali Dogodki

| Dogodek | Kdaj |
|-----------|-------|
| **Outside Room** | Instanca je popolnoma zunaj sobe |
| **Intersect Boundary** | Instanca se dotakne roba sobe |
| **Game Start** | Igra se zažene (naložena prva soba) |
| **Game End** | Igra se konča |
| **Room Start** | Ob vstopu v sobo |
| **Room End** | Ob izstopu iz sobe |
| **No More Lives** | Življenja dosežejo 0 |
| **No More Health** | Zdravje doseže 0 |
| **Animation End** | Animacija sprita je dokončana |

### Dogodki Draw

| Dogodek | Kdaj |
|-----------|-------|
| **Draw** | Med fazo izrisovanja |
| **Draw GUI** | Po izrisu sobe (v prostoru zaslona) |

---

## Referenca Akcij

### Akcije Gibanja

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Nastavi hitrost** | Nastavi hitrost gibanja | hitrost, relativno |
| **Nastavi smer** | Nastavi smer | smer (0-360), relativno |
| **Set Horizontal Speed** | Nastavi hspeed | hspeed, relativno |
| **Set Vertical Speed** | Nastavi vspeed | vspeed, relativno |
| **Set Gravity** | Nastavi gravitacijo | gravity, direction |
| **Set Friction** | Nastavi trenje | friction |
| **Premakni proti točki** | Premik proti koordinatam | x, y, hitrost |
| **Začni se premikati (smer)** | Premik v smeri | direction, hitrost |
| **Jump To Position** | Teleportiraj na koordinate | x, y, relativno |
| **Skoči na začetni položaj** | Vrni se na položaj ustvarjanja | - |
| **Skoči na naključni položaj** | Teleport na povsem naključen položaj (obe osi; možnost pripenjanja na mrežo) | snap_h, snap_v |
| **Odbij se** | Odbij se od trdnih objektov | precise |

### Akcije Instance

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Create Instance** | Ustvari nov objekt | object, x, y, relativno |
| **Create Moving Instance** | Ustvari s hitrostjo | object, x, y, speed, direction |
| **Destroy Instance** | Odstrani instanco | - |
| **Change Instance** | Preobrazi v drug objekt | object, perform_events |

### Akcije Časovnika

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Set Alarm** | Zaženi odštevanje | alarm_number, steps |
| **Sleep** | Ustavi izvajanje | milisekunde |

### Akcije Score/Lives/Health

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Set Score** | Spremeni rezultat | value, relativno |
| **Set Lives** | Spremeni življenja | value, relativno |
| **Set Health** | Spremeni zdravje | value, relativno |
| **Nariši rezultat** | Prikaži rezultat | x, y, caption |
| **Nariši življenja** | Prikaži življenja kot ponovljene slike spritea | x, y, sprite, scale, tiled |
| **Nariši vrstico zdravja** | Prikaži zdravje kot dvobarvno vrstico | x1, y1, x2, y2, back_color, bar_color |

### Akcije Risanja

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Draw Sprite** | Nariši sprite | sprite, x, y, subimage |
| **Draw Text** | Prikaži besedilo | x, y, text |
| **Draw Rectangle** | Nariši pravokotnik | x1, y1, x2, y2, filled |
| **Draw Circle** | Nariši krog | x, y, radius, filled |
| **Draw Line** | Nariši črto | x1, y1, x2, y2 |
| **Nastavi barvo risanja** | Nastavi barvo za naslednje Draw Text/Draw Rectangle/itd. | color |
| **Nastavi barvo** | Nastavi ton in prosojnost spritea (ne barve risanja zgoraj) | color, alpha |
| **Nastavi pisavo risanja** | Nastavi pisavo in poravnavo za naslednje risanje besedila | font, halign, valign |

### Akcije Sobe

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Next Room** | Pojdi na naslednjo sobo | transition |
| **Previous Room** | Pojdi na prejšnjo sobo | transition |
| **Restart Room** | Ponastavi sobo | - |
| **Go to Room** | Skoči na določeno sobo | room, transition |
| **If Next Room Exists** | Preveri, ali obstaja naslednja soba | - |
| **If Previous Room Exists** | Preveri, ali obstaja prejšnja soba | - |

### Akcije Zvoka

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Play Sound** | Predvajaj zvočni učinek | sound, loop |
| **Stop Sound** | Ustavi zvok | sound |
| **Check Sound Playing** | Preveri, ali se zvok predvaja | sound |
| **Play Music** | Predvajaj glasbo v ozadju | music, loop |
| **Stop Music** | Ustavi vso glasbo | - |

### Akcije Spremenljivk

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Nastavi spremenljivko** | Dodeli vrednost | variable, value, relativno |
| **Preveri spremenljivko** | Preveri vrednost | variable, value, operation |
| **Nariši spremenljivko** | Prikaži spremenljivko | x, y, variable |

### Akcije Nadzora Toka

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Preveri izraz** | Pogojno preverjanje (logični izraz Python) | expression |
| **Sicer** | Alternativna veja | - |
| **Start Block** | Začni skupino akcij | - |
| **End Block** | Zaključi skupino akcij | - |
| **Repeat** | Ponovi N-krat | count |
| **Exit Event** | Ustavi trenutni dogodek | - |

### Ostale Akcije

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Show Message** | Prikaži pojavno sporočilo | message |
| **Restart Game** | Ponovno zaženi igro | - |
| **End Game** | Zapri igro | - |

---

## Vgrajene Spremenljivke

Te spremenljivke so na voljo za vse instance:

| Spremenljivka | Opis |
|----------|-------------|
| `x` | Vodoravni položaj |
| `y` | Navpični položaj |
| `xstart` | Začetni položaj x |
| `ystart` | Začetni položaj y |
| `hspeed` | Vodoravna hitrost |
| `vspeed` | Navpična hitrost |
| `speed` | Hitrost animacije spritea (sličic na sekundo) — **ne** hitrost gibanja. Vgrajene spremenljivke za "skupno hitrost" ni; izračunajte jo sami iz `hspeed`/`vspeed`, npr. `(hspeed**2 + vspeed**2)**0.5` |
| `direction` | Smer gibanja (0-360) |
| `gravity` | Gravitacija |
| `gravity_direction` | Smer gravitacije |
| `friction` | Trenje gibanja |
| `image_index` | Trenutna sličica animacije |
| `image_speed` | Hitrost animacije |
| `image_xscale` | Vodoravno merilo |
| `image_yscale` | Navpično merilo |
| `image_angle` | Kot rotacije |
| `visible` | Ali se izriše |
| `solid` | Ali je trden za trke |
| `depth` | Globina risanja |
| `sprite_index` | Trenutni sprite |
| `alarm[0-11]` | Časovniki alarmov |

### Globalne Spremenljivke

| Spremenljivka | Opis |
|----------|-------------|
| `score` | Rezultat igre |
| `lives` | Življenja igralca |
| `health` | Zdravje igralca (0-100) |
| `room` | Trenutna soba |
| `room_width` | Širina trenutne sobe |
| `room_height` | Višina trenutne sobe |
| `mouse_x` | Položaj X miške |
| `mouse_y` | Položaj Y miške |

---

## Naslednji Koraki

- [[Vizualno_Programiranje_sl]] - Uporabite bloke Blockly za isto logiko
- [[Urejevalnik_Objektov_sl]] - Uporabite dogodke in akcije na objektih
- [[Prva_Igra_sl]] - Oglejte si dogodke v akciji
