# Lansiranje žarkov — 1. stopnja

Pogled v prvi osebi v slogu Doom/Wolfenstein na **isto postavitev
labirinta kot `maze_1`** — enake sobe, enak cilj, enake rešljive poti.
Kjer `maze_1` prikazuje labirint od zgoraj s polnimi bloki zidov po
celicah, ta vzorec ga izriše kot projekcijo lansiranja žarkov s
**tankimi robnimi zidovi** (predelne stene 8px na mejah celic, ne
bloki 32px, ki zapolnijo celico) — resnično proporcionirani hodniki v
slogu Wolfensteina, ne le kamera v prvi osebi, privita na staro
kockasto postavitev. `rooms/room0.json` in `room1.json` sta bili
ponovno generirani iz izvirne postavitve `maze_1` s pretvorbo, ki
ohranja topologijo (enaka povezljivost/rešljivost, drugačna geometrija
zidov), ne ročno preoblikovani. Glejte
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) v korenu
repozitorija za celoten inženirski načrt, vključno z razdelkom
"Popoln premislek" o tem, zakaj polnocelični zidovi niso delovali za
pravi prostor obračanja.

**To je 2,5D, ne 3D** — igralna logika je popolnoma nespremenjena
glede na `maze_1` (enak 2D položaj `x`/`y`, enak trk s trdnim zidom);
samo *slika* je prevarana, da izgleda tridimenzionalna. Ni navpičnega
pogleda (brez naklona), hodniki morajo biti poravnani z mrežo, in ni
resnične sobe nad sobo. To je namerna, poštena omejitev, ne manjkajoča
funkcija — glejte opombo pedagogike "zakaj lansiranje žarkov" v
dokumentu z načrtom.

**Stanje — popolnoma teksturirano (zidovi, nebo, tla, panoji) na vseh
treh ciljih: namizje (pygame), HTML5, in nativno (Kivy).** Zidovi
vzorčijo **teksturo opeke** (`spr_wall_texture`, prek `wall_texture`):
vsak stolpec zaslona vzorči navpičen trak na položaju zadetka žarka,
skaliran po razdalji, s stranjo zidu, obrnjeno stran, pri polovični
svetlosti kot brezplačen namig globine. Strop je **nebo v slogu
DOOM** (`spr_sky`, prek `sky_texture`) — panorama, ki se vodoravno
premika, medtem ko se obračate (poln obrat 360° jo premakne enkrat) in
se *ne* oddaljuje z razdaljo, tako da se bere kot neskončno oddaljen
obzorje. Tla so **teksturirana z lansiranjem kamna**
(`spr_floor`, prek `floor_texture`) — lansiranje tal pri nizki
ločljivosti (polnoločljivo po pikslu je bilo ~13× prepočasno v čistem
Pythonu; `floor_cast_res` nastavi zmanjšanje vzorčenja, 4 ≈ 5ms), ki
se ploščicasto ponavlja po celici mreže in se brezšivno stika z bazami
zidov. `obj_goal` se izriše kot pano, obrnjen proti kameri (skaliran
po razdalji, zakrit z zidovi) — glejte "Kaj je tukaj novega". Za
vrnitev na ploski videz počistite `wall_texture`/`sky_texture`/
`floor_texture` na dejanju `enable_raycast_view`.

## Kako igrati

- **Gor/dol** se premikata naprej/nazaj v smeri, v katero gledate
  (neprekinjeno gibanje, ne zaklenjeno na mrežo — zidovi vas še vedno
  blokirajo prek običajnega trka s trdno instanco motorja,
  nespremenjeno glede na `maze_1`).
- **Levo/desno** se obračata na mestu (vrti `facing_angle`, neodvisno
  od gibanja — obračate se lahko, medtem ko mirno stojite).
- **Cilj:** poiščite cilj. Dotik z njim napreduje v naslednjo sobo, če
  obstaja (enaka logika `obj_goal` kot pri `maze_1`, bajtno identična
  datoteka).

## Kaj je tukaj novega, glede na motor

- `GameInstance.facing_angle` — trajna smer gledanja (konvencija kota
  GM: 0=desno, 90=gor, 180=levo, 270=dol), nastavljena prek novega
  dejanja `set_facing_angle`. Za razliko od obstoječega lastnosti
  `direction` (izpeljane iz `hspeed`/`vspeed`, vedno 0 pri mirovanju),
  ta preživi mirno stanje — potrebno za nadzor FPS "obrni se na mestu".
- `enable_raycast_view` — preklopi trenutno sobo na kamero za
  lansiranje žarkov (vezano na kličočo instanco, tukaj dogodek
  `create` objekta `obj_person`) ali nazaj na navadno izrisovanje od
  zgoraj.
- Mapa zidov je **izpeljana iz obstoječih trdnih instanc te sobe**, ne
  ločenega formata za avtorstvo — vendar je od predelave s tankimi
  zidovi izpeljana kot prave robove (`GameRoom._build_raycast_walls`),
  ne grobo zasedenost po celici: razmerje stranic sprite-a trdne
  instance določa, ali je vodoraven ali navpičen segment zidu
  (približno kvadratna oblika se privzeto vrne na blokiranje cele
  celice, za povratno združljivost z vsebino brez tankih zidov). To
  omogoča, da debelina 8px `obj_wall_h`/`obj_wall_v` dejansko šteje
  tako za izrisovanje kot za prostor obračanja, ne le vizualno —
  glejte razdelek "Popoln premislek" v dokumentu z načrtom.
- **Sprite-i panojev.** Vsaka vidna, netrdna instanca s sprite-om
  (tukaj `obj_goal`) se izriše kot 2D sprite, obrnjen proti kameri, v
  pogledu lansiranja žarkov, skaliran po razdalji in navpično
  centriran na obzorju kot trak zidu. Zakritje je pravo zakritje po
  stolpcu glede na razdalje zidov, že izračunane za prehod zidov tiste
  sličice, tako da je cilj za zidom pravilno skrit namesto vidnega
  skozenj. To je prvi cut Faze 6 iz dokumenta z načrtom (zidovi
  izrisujejo samo trdne instance; panoji izrisujejo samo netrdne,
  tako da se nič ne izriše dvakrat) — brez delnega prelivanja
  prosojnosti, brez rotacije, ki bi se ujemala z lastno smerjo
  sprite-a, le ploska skalacija in zakritje, ki jih je motor v slogu
  Wolfensteina uporabljal za predmete in sovražnike.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest projekta |
| `rooms/room0.json`, `rooms/room1.json` | Ista *topologija* labirinta kot `maze_1`, ponovno generirana s tankimi robnimi zidovi (glejte algoritem pretvorbe v dokumentu z načrtom) |
| `objects/obj_person.json` | Igralec/kamera — `create` omogoči pogled lansiranja žarkov, dogodki `keyboard` poganjajo obračanje + naprej/nazaj, registrira `collision_with_obj_wall_h`/`_v` |
| `objects/obj_goal.json` | Ciljni objekt — bajtno identičen tistemu v `maze_1` |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Tanki segmenti zidu (32×8 in 8×32) — nadomestijo enoten polnoblokovni `obj_wall` iz `maze_1` |
| `sprites/` | `spr_person`, `spr_goal` (iz `maze_1`) plus lastna `spr_wall_h`/`spr_wall_v` tega vzorca (tanki, ograjniki polne barve — nikoli izrisani v načinu prve osebe, štejejo samo njihove dimenzije za trk/lansiranje žarkov) |

## Kaj prilagoditi

- Hitrost obračanja je `3`°/sličico (`room_speed: 30` → 90°/s) in
  hitrost premikanja je `3` px/sličico, oboje trdo-kodirano v
  dogodkih `keyboard` objekta `obj_person`.
- FOV `66`°, `render_distance` `20` celic, `cell_size` `32` — vse
  parametri `enable_raycast_view` na dogodku `create` objekta
  `obj_person`.
- Barve zidov/tal/stropa so prav tako parametri `enable_raycast_view`
  — rezervni ploski videz, ko je ujemajoča se tekstura počiščena.
- Debelina zidu je `8`px, trdo-kodirana v pretvorbi, ki je generirala
  `rooms/*.json` (ni izvajalni parameter) — za spremembo ponovno
  generirajte sobe.
- `spr_person` je **16×16** z okvirjem trka `(4,4)-(12,12)` — igralec
  je bil prepolovljen iz starega 32×32 (in ponovno centriran v svoji
  začetni celici, tako da kamera še vedno sedi na sredini celice), ker
  je igralec polne velikosti povzročil, da so bili hodniki eno celico
  širine tesnobni; manjši odtis daje veliko več prostora za gibanje.
  **Tekstura opeke** zidu je bila prav tako narejena bolj drobna
  (opeke pri polovičnem merilu), tako da se zidovi berejo bolj
  oddaljeni — oba popravka menjata "vsiljivost" za bolj prostoren
  občutek prostora.

## Stanje izvoza

**Popoln** pogled v prvi osebi se zdaj izriše na **vseh treh ciljih**
— namizje (pygame), **HTML5**
(`export/HTML5/templates/engine.js`), in **nativno/Kivy**
(`export/Kivy/kivy_exporter.py`) — z nadzorom pogleda prek kota
gledanja, teksturiranimi + ploskimi zidovi, premikajočim se nebom,
teksturiranim lansiranjem tal nizke ločljivosti, in panoji z
zakritjem, obrezanim po zaslonu. Trije izrisovalniki ne delijo kode
(tri ročno napisane kopije), zato je njihovo jedro DDA zaklenjeno
skupaj z `tests/test_raycast_export_parity.py` (natančna numerična
enakost namizje↔Kivy prek matrike 260 žarkov; strukturna enakost za
HTML5, saj v CI ni motorja JS).

Lansiranje tal na vsakem cilju uporablja isti pristop nizka
ločljivost-nato-povečava (`floor_cast_res`, privzeto 4); meritve
časov na strojni opremi so potrdile, da se prilega proračunu
(brskalnik ~0,4 ms pri res=2; Kivy/AMD 840M ~5 ms pri res=4). Projekt
lahko še vedno počisti `floor_texture` za ploska tla `floor_color`.

Na voljo v zavihku Welcome urejevalnika — izberite **"Raycast — Level
1"** v spustnem meniju *Choose a sample* (odpiranje vzorca ga kopira
v vaše Documents, tako da priloženi izvirnik ostane nedotaknjen).
