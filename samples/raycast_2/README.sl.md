# Lansiranje žarkov — 2. stopnja

Druga stopnja v prvi osebi v slogu Doom/Wolfenstein, zgrajena na
istem **motorju lansiranja žarkov 2,5D** kot
[`raycast_1`](../raycast_1/README.md) — ki je popoln na vseh treh
ciljih izvoza (namizje, HTML5, nativno/Kivy): teksturirani zidovi,
premikajoče se nebo, teksturirano lansiranje tal nizke ločljivosti, in
sprite-i panojev, obrnjeni proti kameri.

Kjer je `raycast_1` majhen hodnik, izpeljan iz maze_1, ki uči *pogled
v prvi osebi sam po sebi*, je `raycast_2` **večji labirint z dogajanjem
v 3D pogledu** — zbirljivi dragi kamni, patruljni sovražnik, in izhod,
pogojen z dragimi kamni. Glejte
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) za motor
in [`docs/RAYCAST_2_SAMPLE_PLAN.md`](../../docs/RAYCAST_2_SAMPLE_PLAN.md)
za oblikovanje in načrt enot tega vzorca.

Popolna igra z dvema stopnjama: krmarite skozi vsak labirint v prvi
osebi, zberite vsak dragi kamen, medtem ko se izogibate patruljnim
pošastim, in dosezite izhod, pogojen z dragimi kamni — prva (topla
opečna) soba vodi v drugo (hladno kristalno-jamsko) sobo, in
dokončanje te zmaga. Na voljo v zavihku Welcome urejevalnika
(*"Raycast — Level 2"*) in se izvozi na vse tri cilje (namizje, HTML5,
nativno/Kivy).

## Kako igrati

- **Gor/dol** — premikata naprej/nazaj v smeri, v katero gledate
  (neprekinjeno, ne zaklenjeno na mrežo; zidovi vas blokirajo prek
  običajnega trka s trdno instanco motorja).
- **Levo/desno** — obračata na mestu (vrti `facing_angle`, neodvisno
  od gibanja — obračate se lahko, medtem ko mirno stojite).
- **Zberite drage kamne**, raztresene po labirintu — vsak doda 10 k
  točkam, prikazanim v **HUD-u na zaslonu** (zgoraj levo), izrisanem
  nad pogledom v prvi osebi prek `obj_hud`.
- **Izogibajte se pošastim** — patruljirajo po hodnikih (odbijajo se
  od zidov) in se izrišejo kot panoji, obrnjeni proti kameri. Dotik ene
  stane življenje in ponovno zažene sobo; začnete s 3 življenji,
  prikazanimi zgoraj desno v HUD-u. Če vam zmanjkajo, se igra ponovno
  zažene.
- **Cilj:** zberite **vse** drage kamne v sobi, nato dosezite njen
  cilj. Dosega cilja prezgodaj vas le pozove *"Collect all the gems
  before you leave!"* — odpre se šele, ko izgine vsak dragi kamen.
  Cilj prve (tople opečne) sobe vas popelje v drugo, hladno
  **kristalno jamo**; dokončanje te zmaga v igri.

## Geometrija stopnje

Tako `rooms/room0.json` kot `rooms/room1.json` sta labirinta s celicami
15×15 (480×480), generirana z rekurzivnim vzvratnim sledenjem
(*popoln* labirint — vsaka celica dosegljiva, zagotovljeno rešljiv —
z nekaj dodatnimi prebitimi zidovi za zanke in daljše vidne linije),
nato pretvorjena v model **tankega robnega zidu** iz `raycast_1`:
vsaka meja med odprto celico in zidom postane segment `obj_wall_h`
(32×8) ali `obj_wall_v` (8×32) debeline 8px na mrežni črti, tako da se
hodniki berejo kot resnično proporcionirani v slogu Wolfensteina,
namesto kockasti. Vsaka soba uporablja drugo seme labirinta, tako da
sta stopnji različni postavitvi.

## Tematizacija po sobah

Teksture pogleda lansiranja žarkov so **po sobah**: `enable_raycast_view`
živi na majhnem nevidnem objektu nadzornika kamere, postavljenem v
vsaki sobi — `obj_cam0` (topla opeka: `spr_wall_texture`/`spr_sky`/
`spr_floor`) v room0, `obj_cam1` (hladna kristalna jama:
`spr_wall_ice`/`spr_sky_ice`/`spr_floor_ice`, modro tonirane
različice) v room1. Vsak nadzornik poimenuje `obj_person` kot kamero
prek parametra `camera_object` dejanja, tako da je *igralec* še vedno
kamera, čeprav dejanje sproži *nadzornik*. Zato je videz druge sobe
drugačen — konfiguracija je omejena na nadzornika sobe, ne vpečena v
igralca.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest projekta |
| `rooms/room0.json`, `rooms/room1.json` | Dva generirana labirinta s tankim robnim zidom (avtoritativni podatki instanc) |
| `objects/obj_person.json` | Igralec/kamera — dogodki `keyboard` poganjajo obračanje + naprej/nazaj; `game_start` inicializira točke/življenja; registrira obravnavalce `collision_with_obj_wall_h`/`_v`, ki pogojujejo blokiranje z zidom, in `collision_with_obj_monster` (izgubi življenje + ponovni zagon) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Nadzorniki kamere po sobah, ki izvedejo `enable_raycast_view` s teksturno tematiko te sobe |
| `objects/obj_gem.json` | Zbirljiv predmet — trk ga uniči; njegov dogodek `destroy` doda 10 k točkam |
| `objects/obj_monster.json` | Patruljni panojski sovražnik — se premika, odbija od zidov |
| `objects/obj_goal.json`, `obj_goal_final.json` | Cilj room0 (→ naslednja soba) in cilj room1 (→ zmaga); oba pogojena z dragimi kamni |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Tanki segmenti zidu (32×8 in 8×32) |
| `objects/obj_hud.json` | HUD v zaslonskem prostoru, izrisan nad pogledom v prvi osebi — `draw_score` + `draw_lives`. Opomba: je **visible: true**: GameMaker ne izvede dogodka draw nevidne instance, zato HUD ne more preprosto živeti na `obj_cam0`/`obj_cam1` (ta sta nevidna) |
| `sprites/` | Ponovno uporabljeni iz `raycast_1` (oseba/cilj/zid/nebo/tla + ograjniki zidu), plus `spr_gem` (dragi kamen iz match3), `spr_monster` (pošast iz maze_3), in modro tonirana teksturna zbirka `*_ice` room1 |

## Ponovno uporabljen motor, ponovno uporabljena umetnost

`raycast_2` deli objekte in sprite-e z `raycast_1` — smisel tega
vzorca je *avtorstvo stopnje in igralnosti na dokončanem motorju*, ne
nova koda za izrisovanje. Umetniško delo dragih kamnov in pošasti
(Enoti 2–3) sta edina nova vira, in nobena od igralne logike ni odvisna
od specifičnega umetniškega dela, tako da sta zamenljiva.
