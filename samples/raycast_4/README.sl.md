# 2.5 D — 4. stopnja

Četrta stopnja v prvi osebi v slogu Doom/Wolfenstein, in prva,
zgrajena **okoli trajne spodnje statusne vrstice** — estetika DOOM
namesto kotnih prekrivanj iz `raycast_3`. 3D pogled je namerno
**krajši** (letterbox), da naredi prostor za vrstico; to je del
videza, ne napaka.

Kjer je `raycast_3` dokazal kotni HUD in zdravje kot vir, `raycast_4`
prikaže dve funkciji motorja, zgrajeni za vrstico DOOM:

- **`viewport_height`** na `enable_raycast_view` skrči pogled v prvi
  osebi na vrh okna in rezervira pas pod njim.
- **`draw_doom_hud`** zapolni ta pas: vrstico zdravja + številko,
  **portret obraza, ki se odziva na zdravje**, točke, življenja, in
  števec ključev — vse iz navadnih ukazov risanja, tako da se izriše
  na namizju, HTML5 in nativno (Kivy) enako.

Glejte [`docs/RAYCAST_DOOM_HUD_PLAN.md`](../../docs/RAYCAST_DOOM_HUD_PLAN.md)
za inženiring, in [`raycast_3`](../raycast_3/README.md) za alternativo
kotnega HUD-a, ki je ta vzorec namerno ne retroadaptira.

**Občutek notranjosti.** Dve stvari to naredita, da se bere kot
hodnik znotraj stavbe namesto odprt labirint: izriše **kamnit strop**
(`spr_ceiling`) namesto premikajočega se neba, ki ga uporabljajo drugi
vzorci lansiranja žarkov — nastavljen prek `ceiling_texture` z
`sky_texture` puščenim praznim — in zidovi se izrišejo **višje**. Ta
višina zidu (`RAYCAST_WALL_HEIGHT`, 1,5× kocke) je globalna privzeta
vrednost motorja, tako da vsaka igra lansiranja žarkov dobi višje
zidove; strop je lastna izbira tega vzorca.

**Zvok in glasba:** nič — nobena zvočna datoteka ni priložena temu vzorcu.

## Kako igrati

- **Gor/dol** — premikata naprej/nazaj v smeri, v katero gledate.
- **Levo/desno** — obračata na mestu.
- **Zberite ključe** — vsak prinese 25 točk in poveča števec **KEYS**
  v vrstici za eno. Trije so.
- **Izogibajte se pošastim** — dotik ene stane **25 zdravja** (s
  kratkim oknom neranljivosti zatem). Opazujte **obraz**: skremži se,
  ko vaše zdravje pade, še preden ste sploh prebrali številko.
- **Zmanjka vam zdravja** → izgubite življenje, zdravje se napolni,
  soba se ponovno zažene. **Zmanjkajo vam življenja** → igra se
  ponovno zažene.
- **Dosezite izhod**, ko najdete **vse tri ključe**. Dotik prezgodaj
  vam le pove, da so vrata zaklenjena.
- **Pritisnite `M`**, da prikličete **minimapo** (privzeto
  izklopljeno), ki prikazuje zidove, zlate ključe, ki jih še morate
  najti, in pošasti v rdeči barvi. Izrisana je znotraj 3D pogleda, nad statusno vrstico,
  in se preklaplja vklop/izklop — enaka na zahtevo dostopna zemljevid,
  ki jo uporablja `raycast_3`, tukaj ohranjena stran od vrstice.

## Statusna vrstica (`draw_doom_hud`)

`obj_person` jo izriše vsako sličico, v zaslonskem prostoru, nad
dokončanim 3D pogledom. Od leve proti desni:

| Območje | Prikazuje |
|---|---|
| Levo | oznaka `HEALTH` + sorazmerna vrstica zdravja + številka |
| Sredina | **portret obraza**, trak s 4 sličicami, ki se odziva na zdravje |
| Desno | `SCORE` nad `LIVES` |
| Skrajno desno | števec `KEYS` |

Obraz je bistvo celotnega vzorca. Njegova sličica je izbrana z mapo
enakomernih razponov nad zdravjem — sličica 0 (miren) blizu polnega,
zadnja sličica (umira) blizu praznega — tako da vam portret pove, kako
vam gre, preden to stori številka, natanko kot lastna vrstica DOOM.

**`obj_person` je hkrati kamera *in* izrisovalnik HUD-a.** To je
namerno: števec ključev je tako le spremenljivka instance na
`obj_person` (`keys`), tako da izraz cilja `draw_doom_hud` bere isto
vrednost identično na vseh treh ciljih izvoza. Ločen nevidni objekt
kamere (kot v `raycast_3`) ne bi mogel nositi spremenljivke, ki jo
potrebuje viden HUD.

## Letterbox (`viewport_height`)

`enable_raycast_view` teče v `create` objekta `obj_person` z
`viewport_height: 400` v oknu 640×480 — tako da je 3D pogled visok
400px in spodnjih **80px** je rezerviranih, zapolnjenih s črno s
strani motorja, in prebarvanih z vrstico. Nastavite `viewport_height`
na `0` (privzeto) in pogled zapolni celotno okno brez rezerviranega
pasu, natanko kot to počnejo `raycast_1`–`3`.

Obzorje se pomakne navzgor s krajšim pogledom, in zidovi/nebo/tla se
vsi skalirajo glede na to — je pravi letterbox, ne vrstica, položena
nad pogledom polne višine. (Na Kivyju, ki je y-navzgor, je rezerviran
pas vseeno na dnu okna; motor obravnava inverzijo.)

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest — okno 640×480, ena soba |
| `rooms/room0.json` | Labirint: celice 15×15, 3 ključi, 4 pošasti, izhod, pogojen s ključi |
| `objects/obj_person.json` | Igralec + kamera + statusna vrstica — gibanje, zdravje, ključi, `draw_doom_hud` |
| `objects/obj_key.json` | Ključ (pasiven; trk `obj_person` ga obravnava) |
| `objects/obj_monster.json` | Patruljni panojski sovražnik |
| `objects/obj_goal.json` | Izhod, pogojen s ključi (odpre se, ko ne ostane noben `obj_key`) |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Tanki segmenti zidu |
| `sprites/` | Ponovno uporabljena umetnost zidu/tal/osebe/pošasti, nov **`spr_ceiling`** (notranji kamniti strop, nadomešča nebo), plus nova `spr_face` (portret s 4 sličicami), `spr_key` in `spr_gate` (zaklenjen izhod) |

## Labirint je generiran

`tools/gen_raycast_4_maze.py` zgradi sobo tako, da se **prepusti
dodeljenemu generatorju iz `raycast_3`** — isti labirint rekurzivnega
vzvratnega sledenja, isti tanki robni zidovi, ista disciplina
izbranega semena (začetek se odpira proti vzhodu, vsaka celica
dosegljiva). Razlikuje se samo v tem, kaj je razpršeno (ključi, ne
dragi kamni/kompleti prve pomoči) in v tem, da je `obj_person` kamera.
Ponoven zagon reproducira dostavljeno sobo; test jo fiksira.

## Kaj prilagoditi

- **Višina vrstice vs. viewport:** `height` na `draw_doom_hud` (80) bi
  se moral ujemati z rezerviranim pasom (`640×480 − viewport_height
  400 = 80`). Spremenite eno, spremenite drugo.
- **Odzivnost obraza:** `face_frames` (4) razdeli zdravje po traku.
  Trak s 5 sličicami z `face_frames: 5` da bolj fine izraze.
- **Poškodba / ključi:** `-25` v `collision_with_obj_monster` objekta
  `obj_person`; 3 ključi in 4 pošasti v `counts` generatorja.
- **Barve in oznake vrstice:** parametri `draw_doom_hud` v dogodku
  draw objekta `obj_person`.

## Stanje izvoza

Teče na vseh treh ciljih. Pokrito z zbirko smoke-testov brez
grafičnega vmesnika (`tools/smoke_run_samples.py`) in
`tests/test_raycast_4_sample.py`, ki poganja pravo zanko: vrstica
izriše vse svoje dele nad skrčenim pogledom, poravnano na dno z
rezerviranim pasom; **sličica obraza sledi zdravju** (100/75/50/25 →
0/1/2/3); pobiranje ključa šteje, prinese točke, in je uničeno.

Izvoza Kivy in HTML5 sta bila preverjena za nosenje celotne stvari —
`viewport_height` letterboxa v konfiguraciji kamere, `draw_doom_hud`,
obraz z več sličicami — a **vizualni** preizkus igre po posameznem
cilju je zadnji korak in je vreden opravljanja z lastnimi očmi: to je
prvi vzorec lansiranja žarkov, katerega *oblika pogleda* se
spreminja, tako da je tisti, ki si najbolj zasluži, da ga opazujete
izrisovati v brskalniku in na Androidu.
