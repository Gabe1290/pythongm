# Labirint — 2. stopnja

Igra z labirintom v mreži, pogled od zgoraj, z dvema igralnima
labirintoma plus naslovnim zaslonom: zbirajte bombone za točke, nato
dosezite izhod za napredovanje. Nadgrajuje zanko labirinta/cilja z
eno sobo iz `maze_1` z začetnim zaslonom, zbirljivim predmetom
(bombon za točke), in zaklenjenimi vrati, ki se odprejo šele, ko so
vsi bomboni v sobi pobrani. To je izvorni projekt pygm2 (brez
sosednje datoteke `.gmk` — njegovi viri so bili prvotno preneseni
prek uvoza GameMaker 8.x, glede na `CREDITS.txt`, vendar je projekt
sam napisan/shranjen v lastnem formatu JSON pygm2.

**Kje se to umešča:** del družine `maze_*` — GameObjects + sprite-i,
plus (za razliko od `maze_1`) statična **slika ozadja** na sobo
(`background_main`), brez ploščic na ravni sobe. Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za primerjavo s `plateforme_*` (doda tlakovana ozadja) in `match3_*`
(čist skript, brez vgrajenih dejanj).

**Zvok in glasba:** priložene so 4 zvočne datoteke
(`sound_background.ogg`, `sound_diamond`/`door`/`goal.wav`), a
**nobena od njih dejansko ni priklopljena** — noben objekt se nikjer
ne sklicuje na `play_sound`/`play_music`, tako da je igra v praksi
tiha kljub temu, da nosi zvočne vire. (Za primerjavo z `maze_3`, kjer
je enako oblikovan nabor zvokov dejansko predvajan.)

## Kako igrati

- **Naslovni zaslon (`room_start`):** pritisnite **PRESLEDNICO** za
  začetek (dejanje `keyboard_press` objekta `controller_start` kliče
  `next_room`).
- **Tipke s puščicami** (gor/dol/levo/desno) premikajo igralca eno
  celico mreže (32px) naenkrat; premikanje je zaklenjeno na mrežo
  prek `test_alignment`/`snap_to_grid` (mreža 32×32), enak vzorec kot
  `maze_1`.
- **Cilj:** zberite bombone (`obj_diamond`, sprite `sprite_bonbon`),
  raztresene po vsakem labirintu — vsak je vreden +10 točk — nato
  dosezite cilj (`obj_goal`). V `room2` je izhod dodatno zaprt z
  zaklenjenimi vrati (`obj_door`), ki se sama uničijo šele, ko izgine
  vsak `obj_diamond` v sobi.
- Dotik cilja napreduje v naslednjo sobo (+100 točk), če obstaja;
  dotik v zadnji sobi (`room2`) podeli +100, odpre zaslon za vnos
  najboljšega rezultata, in konča igro.
- **Brez pogoja poraza:** v objektih tega vzorca se nikjer ne pojavi
  dejanje, ki bi vplivalo na življenja/zdravje — `starting_lives: 3`
  je nastavljen v nastavitvah projekta, a nikoli ni prikazan ali
  zmanjšan.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest projekta — nastavitve okna/sobe in vgrajene kopije vseh virov |
| `rooms/room_start.json` | Naslovni zaslon — 1 instanca (`controller_start`) |
| `rooms/room1.json` | Prvi labirint — 134 instanc (zidovi, igralec, cilj, 4 bomboni, `controller_main`) |
| `rooms/room2.json` | Drugi labirint — 112 instanc (zidovi, igralec, cilj, 21 bombonov, zaklenjena vrata, `controller_main`) |
| `objects/*.json` | 9 definicij objektov — preverjene glede na vgrajene kopije v `project.json` in v tem vzorcu identične (brez zastarelosti) |
| `sprites/` | 7 sprite-ov (`sprite_person`, `sprite_bonbon`, `sprite_door`, `sprite_goal`, `sprite_wall_corner`, `sprite_wall_horizontal`, `sprite_wall_vertical`) + metapodatki; `tiles.json` je osirotela stranska datoteka (ni registrirana v `project.json`, slikovna datoteka manjka — neuporabljena) |
| `backgrounds/` | `background_start.png` (naslovni zaslon), `background_tiles.png` (tlakovana tla labirinta) |
| `sounds/` | 4 zvočne datoteke (glejte Vire spodaj) |
| `CREDITS.txt` | Obvestilo o licenciranju virov za ta vzorec |

## Objekti

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `obj_person` | Lik, ki ga upravlja igralec; premikanje na osnovi mreže | keyboard (down, right, up, left, nokey), collision_with_wall_corner |
| `wall_corner` | Osnovni trden zid labirinta; nadrejeni objekt za druga dva tipa zidu | (nič — samo pasiven trkalnik) |
| `wall_horizontal` | Trden vodoraven segment zidu (deduje od `wall_corner`) | (nič — samo pasiven trkalnik) |
| `wall_vertical` | Trden navpičen segment zidu (deduje od `wall_corner`) | (nič — samo pasiven trkalnik) |
| `obj_diamond` | Zbirljiv bombon; ob pobiranju doda točke | destroy, collision_with_obj_person |
| `obj_door` | Zaklenjena izhodna vrata (samo room2); odprejo se, ko izginejo vsi bomboni | step |
| `obj_goal` | Izhod stopnje; napreduje v naslednjo sobo ali konča igro | collision_with_obj_person |
| `controller_start` | Nadzornik naslovnega zaslona; čaka, da igralec začne | create, keyboard_press (PRESLEDNICA) |
| `controller_main` | Nadzornik HUD-a znotraj labirinta; izrisuje točke | draw |

## Viri

7 sprite-ov (32×32, en sličica, pikselno natančen trk razen
`sprite_goal`, ki nima izrecne zastavice `precise`), 2 ozadji, 4 zvoki
(`sound_background.ogg`, `sound_diamond.wav`, `sound_door.wav`,
`sound_goal.wav`). Licenciranje/poreklo vseh virov tega vzorca je
**nedokumentirano** — glejte `CREDITS.txt` v tej mapi, ki kaže na
opravilo "Remaining maze assets" v `docs/ASSET_LICENSES.md`. Za te
datoteke ne predpostavljajte licence CC0 ali katere koli druge.

## Kaj prilagoditi

- Hitrost premikanja igralca je `4` (celice mreže/korak), medtem ko
  ustavitev ob trku z zidom uporablja hitrost `8` — obe sta
  trdo-kodirana parametra dejanja na pritisk tipke v `obj_person`,
  enako kot `maze_1`.
- Vse 4 priložene zvočne datoteke niso referencirane — noben objekt
  trenutno ne kliče `play_sound`; priklop enega za pobiranje bombona
  / odpiranje vrat / dosego cilja bi bil naraven naslednji korak.
- Sobe so `480×480`–`480×512` pri `room_speed: 30` — majhni labirinti
  z eno samo zaslonsko sliko, brez rolanja.
- `sprites/tiles.json` je preostala stranska datoteka, ki ni
  registrirana kot vir projekta (njena `sprites/tiles.png` ne
  obstaja) — varno jo je odstraniti ali prezreti.

## Stanje izvoza

Pokrito z zbirko smoke-testov brez grafičnega vmesnika
(`tools/smoke_run_samples.py`, ki navaja `maze_2` in ga poganja za
~180 sličic z vbrizganim vnosom tipkovnice); ni posebej ponovno
preverjeno po ciljih izvoza (Kivy/splet). Izpostavljeno v zavihku
Welcome urejevalnika kot "Maze — Level 2" (`widgets/welcome_tab.py`).
