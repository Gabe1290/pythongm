# Referenca Dogodkov

*[Domov](Home_sl) | [Vodnik po Prednastavitvah](Preset-Guide_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

Ta stran dokumentira vse razpoložljive dogodke v PyGameMaker. Dogodki so sprožilci, ki izvedejo akcije, ko se v vaši igri pojavijo določeni pogoji.

## Kategorije Dogodkov

- [Dogodki Objekta](Event-Reference-Object_sl) - Create, Step, Destroy
- [Dogodki Vnosa](Event-Reference-Input_sl) - Tipkovnica, Miška
- [Dogodki Trkov](Event-Reference-Collision_sl) - Trki objektov
- [Časovni Dogodki](Event-Reference-Timing_sl) - Alarmi, Variante Step
- [Dogodki Risanja](Event-Reference-Drawing_sl) - Prilagojeno izrisovanje
- [Dogodki Sobe](Event-Reference-Room_sl) - Prehodi med sobami
- [Dogodki Igre](Event-Reference-Game_sl) - Začetek/Konec igre
- [Drugi Dogodki](Event-Reference-Other_sl) - Meje, Življenja, Zdravje

---

## Vrstni Red Izvajanja Dogodkov

Razumevanje, kdaj se dogodki sprožijo, pomaga ustvariti predvidljivo
obnašanje igre (preverjeno proti glavni zanki v
`runtime/game_runner.py`):

1. **Začetek koraka** — Začetek sličice
2. **Budilka** — Vsi sproženi alarmi odštevajo in se sprožijo
3. **Korak** (in **Keyboard (pridržana)**) — Glavna logika igre, nato
   neprekinjena preverjanja pridržanih tipk za isto instanco
4. **Pritisk tipke/Release, Mouse** — Nakopičeni dogodki vnosa za to
   sličico se obdelajo (to se zgodi *po* Step, ne pred njim — koda v
   Step reagira na tipke, ki so bile pritisnjene že na *začetku*
   sličice, ne na tiste, pritisnjene med njo)
5. **Gibanje, nato Trk** — Uveljavi se fizika (gravitacija/trenje/
   hspeed/vspeed), nato se zaznajo trki in sprožijo njihovi dogodki
6. **Konec koraka** (in **Uničenje**) — Po trkih
7. **Risanje** — Faza izrisovanja

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
| **Začetnik** (19 dogodkov) | Create, Step, Keyboard (pridržana), Keyboard \<Brez Tipke\>, Collision, Začetek koraka, Konec koraka, Alarm, Draw, Risanje vmesnika, Začetek sobe, Konec sobe, Začetek igre, Konec igre, Zunaj sobe, Dotik roba sobe, Ni več življenj, Ni več zdravja, Konec animacije |
| **Srednji** (21 dogodkov) | + Destroy, Pritisk tipke |
| **Popoln** (samo Razvojna izdaja, 23 dogodkov) | + Spust tipke, Mouse |

---

## Glejte Tudi

- [Popolna Referenca Akcij](Full-Action-Reference_sl) - Popoln seznam akcij
- [Preset za Začetnike](Beginner-Preset_sl) - Bistveni dogodki za začetnike
- [Srednji Preset](Intermediate-Preset_sl) - Dodatni dogodki
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Pregled osnovnih konceptov
