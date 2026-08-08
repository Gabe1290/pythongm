# Labirint — 1. stopnja

Igra z labirintom v mreži, pogled od zgoraj: vodite sprite igralca
skozi labirint, obdan z zidovi, da dosežete ciljno ploščico, kar
napreduje v naslednjo sobo. To je izvorni projekt pygm2 (brez
sosednje datoteke `.gmk` — njegovi viri so bili prvotno preneseni
prek uvoza GameMaker 8.x, glede na CREDITS.txt, vendar je projekt sam
napisan/shranjen v lastnem formatu JSON pygm2.

**Kje se to umešča:** `maze_*` je prva od treh družin vzorcev v
grobem poteku tehnik avtorstva (vgrajeni objekti/sprite-i →
`plateforme_*`, ki doda tlakovana ozadja → `match3_*`-jeve igre s
čistim skriptom `execute_code`) — glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za celotno sliko. Ta vzorec uporablja samo GameObjects + sprite-e,
brez slike ozadja in brez ploščic na ravni sobe.

**Zvok in glasba:** nič — nobena zvočna datoteka ni priložena temu vzorcu.

## Kako igrati

- **Tipke s puščicami** (gor/dol/levo/desno) premikajo igralca eno
  celico mreže (32px) naenkrat; premikanje je zaklenjeno na mrežo
  prek `test_alignment`/`snap_to_grid` (mreža 32×32).
- Zidovi (`obj_wall`) so trdni — hoja vanje ustavi igralca in ga
  ponovno poravna na mrežo.
- **Cilj:** dosezite ciljno ploščico (`obj_goal`). Dotik z njo
  napreduje v naslednjo sobo, če obstaja, ali ponovno zažene igro,
  če je ni.
- **Bližnjice za razhroščevanje:** pritisk na `N` na cilju skoči v
  naslednjo sobo (če obstaja); pritisk na `P` skoči v prejšnjo sobo
  (če obstaja) — enaka logika napredovanja/ponovnega zagona kot dotik
  cilja.
- V tem vzorcu se ne uporablja sledenje življenjem/točkam/zdravju
  (zdravje se ponastavi prek `set_health` ob napredovanju sobe, a
  nikoli ni prikazano).

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest projekta — nastavitve okna/sobe in vgrajene kopije vseh virov |
| `rooms/room0.json` | Postavitev labirinta za sobo 0 (131 instanc: zidovi, začetek igralca, cilj) |
| `rooms/room1.json` | Postavitev labirinta za sobo 1 (130 instanc) |
| `objects/obj_person.json` | Definicija objekta igralca (vir resnice; ujema se z vgrajeno kopijo v `project.json`) |
| `objects/obj_goal.json` | Definicija ciljnega objekta |
| `objects/obj_wall.json` | Definicija objekta zidu |
| `sprites/` | `spr_person.png`, `spr_wall.png`, `spr_goal.png` + njihovi metapodatki `.json` |
| `CREDITS.txt` | Obvestilo o licenciranju virov za ta vzorec |

Stranske datoteke `objects/*.json` so bile preverjene glede na
vgrajene kopije v `project.json` in so v tem vzorcu identične — brez
zastarelosti.

## Objekti

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `obj_person` | Lik, ki ga upravlja igralec; premikanje na osnovi mreže | implicitno prek create prek tipkovnice, keyboard (down, right, up, left, nokey), collision_with_obj_wall |
| `obj_goal` | Izhod stopnje; napreduje/ponovno zažene ob dotiku ali razhroščevalni tipki | collision_with_obj_person, keyboard_press (p, n) |
| `obj_wall` | Statičen trden zid labirinta, blokira gibanje | (nič — samo pasiven trkalnik) |

## Viri

3 sprite-i (`spr_person`, `spr_wall`, `spr_goal`, vsak 32×32, en
sličica, pikselno natančen trk), 0 zvokov. Licenciranje: `spr_person.png`
in `spr_wall.png` sta deli CC0 (javna last) avtorja pygm2; poreklo
`spr_goal.png` še ni dokumentirano — glejte `CREDITS.txt` v tej mapi
in `docs/ASSET_LICENSES.md` v korenu repozitorija za celotno sliko.

## Kaj prilagoditi

- Hitrost premikanja igralca je `4` (celice mreže/korak), medtem ko
  ustavitev ob trku z zidom uporablja hitrost `8` — obe sta
  trdo-kodirana parametra dejanja na pritisk tipke v `obj_person`.
- Velikost mreže je `32` (ujema se s sprite-i 32×32); sprememba
  zahteva ujemajoče se popravke klicev `snap_to_grid`/`test_alignment`
  in postavitev sob.
- Sobe so `480×480` pri `room_speed: 30` — majhni labirinti z eno
  samo zaslonsko sliko, brez rolanja.
- Razhroščevalni tipki `N`/`P` na `obj_goal` omogočata preskakovanje
  med room0/room1, ne da bi se dotaknili cilja — priročno za
  testiranje, a med igro lahko po nesreči pritisnete nanju.

## Stanje izvoza

Pokrito z zbirko smoke-testov brez grafičnega vmesnika
(`tools/smoke_run_samples.py`, ki navaja `maze_1` in ga poganja za
~180 sličic z vbrizganim vnosom tipkovnice); ni posebej ponovno
preverjeno po ciljih izvoza (Kivy/splet). Izpostavljeno v zavihku
Welcome urejevalnika kot "Maze — Level 1" (`widgets/welcome_tab.py`).
