# Labirint — 4. stopnja

Največji vzorec labirinta: **21 sob** ugank labirinta v mreži s
**tekočimi trakovi**, tremi vrstami **pošasti**, **bombami/eksplozijami**,
ki razstrelijo skozi zidove, **obročem moči**, ki prestraši pošasti, in
zbirljivimi predmeti (diamanti, obroči, srca). Izvorni projekt pygm2,
uvožen iz `maze_4.gmk` (GameMaker 8.x), napisan/shranjen v lastnem
formatu JSON pygm2.

**Kje se to umešča:** četrta stopnja `maze_*` in mehansko najbogatejša
— na osnovno gibanje v mreži iz `maze_1..3` doda gibanje s tekočimi
trakovi, več vrst sovražnikov, zanko moči za prestrašitev/pojedanje, in
bombo, ki uniči zidove. Odstranjena je bila v rc.12 zaradi napak pri
uvozu GMK in **ponovno dodana po utrjevanju uvoznika**
(16.07.2026); glejte
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
in [`../../docs/maze_4_testing_pass.md`](../../docs/maze_4_testing_pass.md).

**Zvok in glasba:** priloženih je 10 zvočnih učinkov. Ena starejša
skladba iz dobe GM8 (`sound_background`) je v formatu, ki ga pygame ne
more naložiti, in je izpuščena med tekom (enako kot pri maze_2/maze_3);
igralnost ni prizadeta.

## Kako igrati

- **Tipke s puščicami** premikajo igralca eno celico mreže naenkrat;
  zidovi blokirajo gibanje.
- **Ploščice tekočega traku** (puščice gor/dol/levo/desno na tleh)
  samodejno prenašajo igralca v svojo smer, medtem ko stoji na njih.
- **Pošasti** so treh vrst (`monster_all` prosto tava; `monster_ud`
  patruljira navpično; `monster_lr` vodoravno) — dotik ene stane
  življenje in ponovno zažene sobo.
- Poberite **obroč** in vsaka pošast postane **prestrašena** (sprite se
  spremeni, zamrznejo) za ~10 sekund — dotaknite se je takrat, da jo
  pojeste za točke; vrnejo se, ko čas poteče.
- **Bombe** eksplodirajo v izbruh, ki **uniči okoliške zidove** —
  uporablja se za odpiranje sicer zaprtih delov.
- Zberite **diamante/obroče/srca**; dosezite **cilj** za napredovanje.
  HUD (točke + življenja) izrisuje `controller_main` vzdolž spodnjega
  roba.

## Opomba o ročnem popravku (poštena dokumentacija)

Gibanje pygm2 *zdrsne do stika* z zidom, medtem ko GameMaker 8
*povrne* blokiran premik na položaj pred njim — vedenje GM je igralca
brezplačno ohranjalo poravnanega z mrežo. Brez tega bi pritisk v raven
zid pustil igralca nekaj pikslov stran od mreže 32, kar bi nato
zataknilo preverjanja gibanja/tekočega traku, ki so zaklenjena na
mrežo. Zato `obj_person` nosi namerni **igralni ročni popravek**:
`snap_to_grid(32)` na svojih dogodkih trka `wall_corner`/
`wall_horizontal`/`wall_vertical`. To zrcali isti popravek, dostavljen
v `maze_1`, in je popravek, ne sprememba zvestobe — svež uvoz iz
`.gmk` ga ne bo vseboval (glejte spodaj).

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest — nastavitve okna/sobe, vgrajeni viri, in vrstni red sob |
| `rooms/*.json` | 21 sob; vrstni red igranja `room_start` nato padajoči teki (`room14`, `room13`, …) — lasten vrstni red izvirne igre, zvesto uvožen |
| `objects/*.json` | 24 definicij objektov (vir resnice; ob nalaganju združen z vgrajenimi kopijami) |
| `sprites/` | 24 slikovnih datotek PNG spritov + metapodatki `.json` |
| `sounds/` | 10 zvočnih učinkov |
| `backgrounds/` | 2 ozadji |
| `CREDITS.txt` | Obvestilo o licenciranju virov |

## Objekti (24)

Igralec/HUD: `obj_person`, `controller_main` (izrisuje točke+življenja), `controller_start`.
Zidovi: `wall_horizontal`, `wall_vertical`, `wall_corner`, `block`.
Sovražniki: `monster_all`, `monster_ud`, `monster_lr`.
Predmeti moči / predmeti: `ring` (prestrašitev), `bomb` + `explosion`
(uničenje zidov), `obj_diamond`, `heart`, `bonus`, `obj_door`,
`obj_goal`, `trigger`, `hole`.
Ploščice tekočega traku: `move_up`, `move_down`, `move_left`, `move_right`.

## Viri

24 sprite-ov, 10 zvokov, 2 ozadji, 1 pisava — vse uvoženo iz
`maze_4.gmk`. Za poreklo glejte `CREDITS.txt` in
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md).

## Kaj prilagoditi

- **Hitrost tekočega traku / igralca** — tekoči trakovi se premikajo s
  hitrostjo `8`; premiki mreže s tipkovnico s hitrostjo `4` (parametri
  na dejanje na `obj_person`).
- **Trajanje prestrašitve** — `set_alarm` obroča je `300` sličic na
  `monster_all`.
- **Vrstni red sob** — sobe se igrajo v vrstnem redu ključev slovarja
  sob v `project.json`; preuredite jih v urejevalniku (povlecite v
  drevesu virov) in Test Game sledi.

## Stanje izvoza

Pokrito z zbirko smoke-testov brez grafičnega vmesnika
(`tools/smoke_run_samples.py`, ki navaja `maze_4`) in zbirko regresije
uvoza (`tests/test_gmk_treasure_maze4_import.py`). Preverjeno v
ročnem preizkusu igre med utrjevanjem uvoznika julija 2026 (glejte
dokument o testiranju). Izpostavljeno v zavihku Welcome kot
**"Maze — Level 4"**.

## Ponovno generiranje iz izvirnika `.gmk`

Sosednja datoteka `../maze_4.gmk` je vir GameMaker 8.x. Za ponovno generiranje:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')"
```

Svež uvoz je zvest izvirni igri, **razen** zgoraj opisanega ročnega
popravka zidov `snap_to_grid` — po ponovnem generiranju ga znova
uveljavite (dodajte `snap_to_grid` z `grid_size` 32 na vse tri
dogodke trka z zidom objekta `obj_person`).
