# Lansiranje žarkov — 3. stopnja

Tretja stopnja v prvi osebi v slogu Doom/Wolfenstein, zgrajena na
istem **motorju lansiranja žarkov 2,5D** kot
[`raycast_1`](../raycast_1/README.md) in
[`raycast_2`](../raycast_2/README.md) — popolna na vseh treh ciljih
izvoza (namizje, HTML5, nativno/Kivy): teksturirani zidovi,
premikajoče se nebo, teksturirano lansiranje tal nizke ločljivosti, in
sprite-i panojev, obrnjeni proti kameri.

Kjer `raycast_1` uči *pogled v prvi osebi sam po sebi* in `raycast_2`
doda *dogajanje v pogledu* (dragi kamni, patruljni sovražnik, izhod s
pogojem), gre pri `raycast_3` za **stanje, ki ga vidite med igranjem**:
pošasti stanejo **zdravje** namesto neposredno življenja, kompleti
prve pomoči ga vrnejo, in **prikaz na zaslonu**, sestavljen nad 3D
pogledom, vedno prikazuje točke, življenja in vrstico zdravja.

Ta HUD je razlog, da ta vzorec obstaja. Do 20.07.2026 je motor izrisal
pogled v prvi osebi in nato prenehal, tako da so se točke in življenja
igre lansiranja žarkov pojavili samo v naslovu namiznega okna —
nevidni na izvozih HTML5 in Kivy. Glejte
[`docs/RAYCAST_HUD_PLAN.md`](../../docs/RAYCAST_HUD_PLAN.md) za to delo
in [`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) za motor.

Popolna igra z dvema stopnjama: prečkajte vsak labirint v prvi osebi,
zberite vsak dragi kamen, medtem ko preživite pošasti, in dosezite
izhod, pogojen z dragimi kamni — prva (topla opečna) soba vodi v
drugo (hladno kristalno-jamsko) sobo, in dokončanje te zmaga. Na
voljo v zavihku Welcome urejevalnika (*"Raycast — Level 3"*).

**Zvok in glasba:** nič — nobena zvočna datoteka ni priložena temu vzorcu.

## Kako igrati

- **Gor/dol** — premikata naprej/nazaj v smeri, v katero gledate
  (neprekinjeno, ne zaklenjeno na mrežo; zidovi vas blokirajo).
- **Levo/desno** — obračata na mestu (vrti `facing_angle`, neodvisno
  od gibanja — obračate se lahko, medtem ko mirno stojite).
- **Zberite drage kamne** — vsak doda 10 k točkam, prikazanim zgoraj levo.
- **Izogibajte se pošastim** — dotik ene stane **25 zdravja**, ne
  življenja. Po udarcu dobite kratko okno neranljivosti (45 sličic),
  tako da pošast, ki hodi skozi vas, ne more naenkrat izprazniti
  celotne vrstice.
- **Poberite komplete prve pomoči** — škatle z rdečim križem vrnejo
  **40 zdravja**, omejeno na polno.
- **Zmanjka vam zdravja** in izgubite eno življenje, vrstica se
  napolni in soba se ponovno zažene. Zmanjkajo vam **življenja** in
  igra se ponovno zažene.
- **Cilj** — zberite *vse* drage kamne v sobi, nato dosezite njen
  izhod. Doseg izhoda prezgodaj vas le pozove, da zberete preostanek.

## HUD

`obj_hud` ga izrisuje, v **zaslonskem prostoru**, nad dokončanim 3D
okvirjem:

| Element | Kot | Dejanje |
|---|---|---|
| Točke | zgoraj levo | `draw_score` |
| Življenja | zgoraj desno | `draw_text` + `draw_lives` |
| Vrstica zdravja | spodaj levo | `draw_health_bar` |
| Minimapa | sredina, **na zahtevo** | `draw_minimap` |

Točke in zdravje sta namerno v **nasprotnih** kotih: vrstica zdravja
je široka in niz točk raste, medtem ko igrate, tako da bi njuno
skladanje vabilo v trk.

### Minimapa

**Pritisnite `M`, da jo prikažete ali skrijete** — na Androidu se
dotaknite gumba za zemljevid zgoraj levo. Privzeto je *izklopljena*
in izrisana samo, dokler je vklopljena, iz dveh razlogov: polna
zemljevid je ~250 ukazov črt na sličico, in trajno prekrivanje dela
pogleda v prvi osebi je natanko tista nered, ki se ji mora HUD
izogibati. Dokler je izklopljena, ne stane nič.

`draw_minimap` izriše **na sever usmerjen** zemljevid zidov sobe z
oznako, ki prikazuje, kje ste in v katero smer gledate. Ne vrti se —
zemljevid ostane fiksen in oznaka se obrača, kar je lažje brati kot
vrteč se zemljevid.

Ne potrebuje lastnih podatkov: bere iste robove zidov, ki jih je
pogled v prvi osebi že izpeljal iz trdnih instanc sobe, tako da
ostane pravilna, če labirint preoblikujete. Prikazuje **samo zidove**
— ne dragih kamnov ali pošasti — tako da je labirint še vedno vreden
raziskovanja.

**Ni implementirano (namerno):** megla vojne, vrteči se/na smer
usmerjen način, in prikaz predmetov ali sovražnikov. Glejte
[`docs/RAYCAST_MINIMAP_PLAN.md`](../../docs/RAYCAST_MINIMAP_PLAN.md)
za razloge za vsako izpustitev.

**`obj_hud` je `visible: true`, in to je pomembno.** GameMaker ne
izvede dogodka draw nevidne instance — tako da HUD ne more preprosto
živeti na nevidnem nadzorniku kamere (`obj_cam0`/`obj_cam1`). Če
zgradite lasten HUD in se nič ne pojavi, najprej preverite to zastavico.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest — okno 640×480, obe sobi, vgrajene kopije virov |
| `rooms/room0.json` | Labirint tople opeke: celice 15×15 / 480×480, 8 dragih kamnov, 3 pošasti, 3 kompleti prve pomoči |
| `rooms/room1.json` | Labirint kristalne jame: težja polovica — 10 dragih kamnov, 5 pošasti, samo 2 kompleta prve pomoči |
| `objects/obj_person.json` | Igralec/kamera — gibanje, poškodba zdravja + alarm neranljivosti, obravnava smrti |
| `objects/obj_hud.json` | Prikaz na zaslonu (glejte zgoraj) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Nadzorniki kamere po sobah, vsak nosi teksturno tematiko te sobe |
| `objects/obj_gem.json` | Zbirljiv predmet, +10 točk |
| `objects/obj_medkit.json` | Vrne 40 zdravja |
| `objects/obj_monster.json` | Patruljni panojski sovražnik |
| `objects/obj_goal.json`, `obj_goal_final.json` | Izhodi, pogojeni z dragimi kamni: napredovanje in zmaga |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Tanki segmenti zidu (32×8 in 8×32) |
| `sprites/` | 13 sprite-ov, ponovno uporabljenih iz `raycast_2` plus `spr_medkit` |

## Labirint je generiran, ne ročno postavljen

`tools/gen_raycast_3_maze.py` zgradi obe sobi z labirintom
rekurzivnega vzvratnega sledenja, spuščenim skozi postavitev tankega
robnega zidu iz `raycast_1` — predelne stene 8px centrirane na mejah
celic, ne bloki 32px, ki zapolnijo celico. Ponoven zagon natančno
reproducira dostavljene sobe, in test potrjuje, da niso zdrsnile,
tako da postavitev stopnje ostane pregledna in prilagodljiva namesto
nepregledna podatkovna struktura. (Labirint `raycast_2` je izviral iz
zavrgljivega skripta, ki nikoli ni bil dodan v repozitorij, tako da
njegovih sob ni mogoče ponovno generirati — ta popravi to.)

Semena so **izbrana, ne poljubna**: `check_start()` potrdi, da se
začetna celica odpira proti vzhodu (igralec se tam pojavi gledajoč
proti vzhodu, tako da bi zaprt začetek pomenil začetek igre z nosom
ob zidu) in da je vsaka celica dosegljiva.

## Kaj prilagoditi

- **Poškodba in zdravljenje:** `-25` v `collision_with_obj_monster`
  objekta `obj_person`, `+40` v dogodku `destroy` objekta `obj_medkit`.
- **Okno neranljivosti:** `45` sličic na `alarm_0`. Krajše naredi igro
  težjo; odstranite ga in pošast, ki se ponavljajoče prekriva z vami,
  bo raztrgala vrstico.
- **Ravnovesje težavnosti:** `counts` po sobi v generatorju — pošasti
  proti kompletom prve pomoči je glavno kolesce.
- **Postavitev HUD:** koordinate v dogodku draw objekta `obj_hud`.
  Ohranite točke in zdravje v nasprotnih kotih.
- **Minimapa:** `size` na `draw_minimap` skalira celotno sobo v tisti
  kvadrat, tako da večja vrednost pomeni le bolj berljiv zemljevid;
  `wall_color` in `player_color` nastavita njegov videz. Preklop
  živi v dogodku `keyboard_press` → `m` objekta `obj_hud`; uporablja
  `test_variable` + `exit_event` namesto dveh golih pogojnikov, ker
  naivna različica nastavi zastavico na 1 in nato takoj prebere 1 in
  jo takoj vrne nazaj na 0.
- **Teme:** teksturni parametri na `obj_cam0`/`obj_cam1`.

## Opomba o časovni razporeditvi trkov

Izvajalno okolje sproži dogodek trka, ko se dve instanci **začneta**
prekrivati, ne vsako sličico, ko ostaneta prekriti. Stanje znotraj
pošasti torej stane en udarec, ne udarca na sličico. Alarm
neranljivosti si še vedno prisluži svoje mesto: pokrije ponovljen
dotik/nedotik pošasti, ki patruljira *skozi* vas, kar je primer, ki ga
dejansko srečate med igranjem.

## Stanje izvoza

Teče na vseh treh ciljih. Pokrito z zbirko smoke-testov brez
grafičnega vmesnika (`tools/smoke_run_samples.py`) in
`tests/test_raycast_3_sample.py`, ki poganja pravo zanko igre:
poškodbo, odpiranje in zapiranje okna neranljivosti, smrt, ki stane
natanko eno življenje, zdravljenje kompleta prve pomoči in njegovo
omejitev, izhod, pogojen z dragimi kamni, prehod sobe v ledeno temo,
in izrisovanje HUD-a nad pogledom v prvi osebi v **obeh** sobah.

Izvoza Kivy in HTML5 sta bila preverjena za nosenje celotne zanke —
`no_more_health`, `alarm_0`, `draw_health_bar`, `obj_hud` in
`spr_medkit` vsi preživijo generiranje kode — a **vizualni** preizkus
igre po posameznem cilju je vreden opravljanja z lastnimi očmi pred
izdajo.
