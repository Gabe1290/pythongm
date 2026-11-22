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
| **Korak** | Vsako sličico (60-krat na sekundo) |
| **Začetek koraka** | Pred preverjanji trkov |
| **Konec koraka** | Po vseh drugih dogodkih |

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
| **Zunaj sobe** | Instanca je popolnoma zunaj sobe |
| **Dotik roba sobe** | Instanca se dotakne roba sobe |
| **Začetek igre** | Igra se zažene (naložena prva soba) |
| **Konec igre** | Igra se konča |
| **Začetek sobe** | Ob vstopu v sobo |
| **Konec sobe** | Ob izstopu iz sobe |
| **Ni več življenj** | Življenja dosežejo 0 |
| **Ni več zdravja** | Zdravje doseže 0 |
| **Konec animacije** | Animacija sprita je dokončana |

### Dogodki Draw

| Dogodek | Kdaj |
|-----------|-------|
| **Risanje** | Med fazo izrisovanja |
| **Risanje vmesnika** | Po izrisu sobe (v prostoru zaslona) |

---

## Referenca Akcij

### Akcije Gibanja

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Nastavi hitrost** | Nastavi hitrost gibanja | hitrost, relativno |
| **Nastavi smer** | Nastavi smer | smer (0-360), relativno |
| **Nastavi vodoravno hitrost** | Nastavi hspeed | hspeed, relativno |
| **Nastavi navpično hitrost** | Nastavi vspeed | vspeed, relativno |
| **Nastavi gravitacijo** | Nastavi gravitacijo | gravity, direction |
| **Nastavi trenje** | Nastavi trenje | friction |
| **Premakni proti točki** | Premik proti koordinatam | x, y, hitrost |
| **Začni se premikati (smer)** | Premik v smeri | direction, hitrost |
| **Skoči na položaj** | Teleportiraj na koordinate | x, y, relativno |
| **Skoči na začetni položaj** | Vrni se na položaj ustvarjanja | - |
| **Skoči na naključni položaj** | Teleport na povsem naključen položaj (obe osi; možnost pripenjanja na mrežo) | snap_h, snap_v |
| **Odbij se** | Odbij se od trdnih objektov | precise |

### Akcije Instance

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Ustvari instanco** | Ustvari nov objekt | object, x, y, relativno |
| **Ustvari premikajočo se instanco** | Ustvari s hitrostjo | object, x, y, speed, direction |
| **Uniči instanco** | Odstrani instanco | - |
| **Spremeni instanco** | Preobrazi v drug objekt | object, perform_events |

### Akcije Časovnika

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Nastavi budilko** | Zaženi odštevanje | alarm_number, steps |
| **Premor** | Ustavi izvajanje | milisekunde |

### Akcije Score/Lives/Health

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Nastavi rezultat** | Spremeni rezultat | value, relativno |
| **Nastavi življenja** | Spremeni življenja | value, relativno |
| **Nastavi zdravje** | Spremeni zdravje | value, relativno |
| **Nariši rezultat** | Prikaži rezultat | x, y, caption |
| **Nariši življenja** | Prikaži življenja kot ponovljene slike spritea | x, y, sprite, scale, tiled |
| **Nariši vrstico zdravja** | Prikaži zdravje kot dvobarvno vrstico | x1, y1, x2, y2, back_color, bar_color |

### Akcije Risanja

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Nariši sprite** | Nariši sprite | sprite, x, y, subimage |
| **Nariši besedilo** | Prikaži besedilo | x, y, text |
| **Nariši pravokotnik** | Nariši pravokotnik | x1, y1, x2, y2, filled |
| **Nariši krog** | Nariši krog | x, y, radius, filled |
| **Nariši črto** | Nariši črto | x1, y1, x2, y2 |
| **Nastavi barvo risanja** | Nastavi barvo za naslednje Nariši besedilo/Nariši pravokotnik/itd. | color |
| **Nastavi barvo** | Nastavi ton in prosojnost spritea (ne barve risanja zgoraj) | color, alpha |
| **Nastavi pisavo risanja** | Nastavi pisavo in poravnavo za naslednje risanje besedila | font, halign, valign |

### Akcije Sobe

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Naslednja soba** | Pojdi na naslednjo sobo | transition |
| **Prejšnja soba** | Pojdi na prejšnjo sobo | transition |
| **Znova zaženi sobo** | Ponastavi sobo | - |
| **Pojdi v sobo** | Skoči na določeno sobo | room, transition |
| **Če obstaja naslednja soba** | Preveri, ali obstaja naslednja soba | - |
| **Če obstaja prejšnja soba** | Preveri, ali obstaja prejšnja soba | - |

### Akcije Zvoka

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Predvajaj zvok** | Predvajaj zvočni učinek | sound, loop |
| **Ustavi zvok** | Ustavi zvok | sound |
| **Preveri predvajanje zvoka** | Preveri, ali se zvok predvaja | sound |
| **Predvajaj glasbo** | Predvajaj glasbo v ozadju | music, loop |
| **Ustavi glasbo** | Ustavi vso glasbo | - |

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
| **Začetek bloka** | Začni skupino akcij | - |
| **Konec bloka** | Zaključi skupino akcij | - |
| **Ponovi** | Ponovi N-krat | count |
| **Zapusti dogodek** | Ustavi trenutni dogodek | - |

### Ostale Akcije

| Akcija | Opis | Parametri |
|--------|-------------|------------|
| **Prikaži sporočilo** | Prikaži pojavno sporočilo | message |
| **Znova zaženi igro** | Ponovno zaženi igro | - |
| **Končaj igro** | Zapri igro | - |

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
