# Labirint — 3. stopnja

Podzemna raziskava petih labirintov v mreži, ki ji sledi naslovni
zaslon — največji od treh vzorcev labirinta (17 objektov / 6 sob, v
primerjavi z 9 objekti / 3 sobami pri maze_2). Ohranja zanko
zbiranja diamantov in nato dosega cilja iz maze_2 ter zaklenjena
vrata, pogojena z diamanti, in doda tri nove mehanike, ki se
postopoma pojavljajo skozi sobe: uganko s potiskanjem blokov v luknjo
(room5), tri arhetipe patruljnih pošasti, ki ubijejo ob dotiku (sobe
3–5), in skrito bombno past, ki sproži eksplozijski radij (room4). Za
razliko od `maze_1`/`maze_2` je ta vzorec **dejansko** surov uvoz
GameMaker 8.x — njegova sosednja datoteka `samples/maze_3.gmk` je
vključena v repozitorij (za `maze_1`/`maze_2` datoteka `.gmk` ne
obstaja), in projekt pygm2 poleg nje je pretvorjen rezultat.

**Kje se to umešča:** del družine `maze_*` — GameObjects + sprite-i
plus statična **slika ozadja** na sobo (kot pri `maze_2`), brez
ploščic na ravni sobe. Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za primerjavo s `plateforme_*` (doda tlakovana ozadja) in `match3_*`
(čist skript, brez vgrajenih dejanj).

**Zvok in glasba:** 8 zvočnih datotek, in — za razliko od nabora, ki
je pri `maze_2` priložen a tih — resnično priklopljenih: 11 mest
klica `play_sound`/`play_music` prek `sound_background` (glasba),
`sound_diamond`, `sound_door`, `sound_goal`, `sound_dead`,
`sound_explode`, `sound_hole`, in `sound_push`.

## Kako igrati

- **Naslovni zaslon (`room_start`):** pritisnite **PRESLEDNICO** za začetek.
- **Tipke s puščicami** premikajo igralca eno celico mreže 32px
  naenkrat (`test_alignment`/`snap_to_grid`, enak vzorec kot
  `maze_1`/`maze_2`).
- **Cilj:** zberite diamante (`obj_diamond`, +5 točk vsak) in
  dosezite `obj_goal` vsake sobe. Sobe 2–4 dodatno zapirajo izhod za
  zaklenjenimi vrati `obj_door`, ki se same uničijo šele, ko izgine
  vsak diamant v tisti sobi (room3 ima 4 vrata, ki se odprejo vsa
  skupaj). Room5 zamenja diamante za uganko s potiskanjem blokov:
  hodite v `obj_block`, da ga premaknete za eno celico, ali ga
  potisnite v `obj_hole`, da zapolnite jamo (oba sta uničena).
- **Nevarnosti:** trije arhetipi pošasti patruljirajo sobe 3–5 in
  ubijejo ob stiku — `monster_all` odbija od zidov v katero koli od 4
  smeri, `monster_lr`/`monster_ud` patruljirata eno os in se obrneta
  ob udarcu v zid. Room4 skriva tudi ploščo `obj trigger`, ki ob
  dotiku sproži bližnji `obj_bomb` v `obj_explosion` — njegov
  16-sličični izbruh uniči vsako netrdno instanco (vključno z
  igralcem) v radiju 64px.
- **Pogoj poraza:** dotik pošasti stane življenje (`sound_dead` +
  `set_lives -1` + `restart_room`); ob dosegu 0 življenj se prikaže
  zaslon za vnos najboljšega rezultata in igra se ponovno zažene.
  Dotik cilja v zadnji sobi namesto tega prikaže čestitko, podeli
  +100, in konča tek na enak način.
- **Razhroščevalne tipke** živijo na `controller_main`: **R** takoj
  stane življenje in ponovno zažene sobo; **N**/**P** neposredno
  skočita v naslednjo/prejšnjo sobo — uporabno za testiranje, a tudi
  preskok stopnje, v katerega bi igralec lahko po nesreči zabredel.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest projekta — nastavitve okna/sobe in vgrajene kopije virov. Kopije objektov se natanko ujemajo z njihovimi stranskimi datotekami, vendar so **kopije sob zastarele**: vsak vgrajen vnos sobe ima 0 instanc in oznako `_external_file` — dejanski podatki instanc živijo samo v `rooms/*.json` |
| `rooms/room_start.json` | Naslovni zaslon — 1 instanca (`controller_start`) |
| `rooms/room1.json` | Labirint 1 — 134 instanc (zidovi, 4 diamanti, cilj, igralec, nadzornik) |
| `rooms/room2.json` | Labirint 2 — 96 instanc (+20 diamantov, 1 zaklenjena vrata) |
| `rooms/room3.json` | Labirint 3 — 105 instanc (+16 diamantov, 4 zaklenjena vrata, vsi 3 arhetipi pošasti, skupno 6 pošasti) |
| `rooms/room4.json` | Labirint 4 — 95 instanc (+14 diamantov, 1 vrata, 4 `monster_lr`, 2 para ploščic/bomb pasti) |
| `rooms/room5.json` | Labirint 5 — 99 instanc (4 premakljivi bloki, 3 luknje, 2 cilja, 2 `monster_lr` — brez diamantov ali vrat) |
| `objects/*.json` | 17 definicij objektov — preverjene glede na vgrajene kopije v `project.json` in identične (brez zastarelosti). Opomba: `objects/obj trigger.json` ima v imenu datoteke dobeseden presledek |
| `sprites/` | 16 sprite-ov + metapodatki (glejte Vire) |
| `sounds/` | 8 zvočnih datotek, vse referencirane iz vsaj enega objekta |
| `backgrounds/` | 2 ozadji (`background_start.png` za naslovno sobo, `background_main.png` za labirinte) |
| `CREDITS.txt` | Obvestilo o licenciranju virov za ta vzorec |

## Objekti

**Igralec in nadzorniki**

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `obj_person` | Lik, ki ga upravlja igralec; premikanje na osnovi mreže | keyboard (up/down/left/right/nokey), collision_with_obj_block, collision_with_monster_all/_lr/_ud, collision_with_wall_corner |
| `controller_start` | Nadzornik naslovnega zaslona; nastavi točke/življenja, zažene glasbo | create, keyboard (PRESLEDNICA) |
| `controller_main` | HUD znotraj labirinta + razhroščevalne tipke; izrisuje točke/življenja, konča tek pri 0 življenjih | keyboard (R varalna ponovitev), no_more_lives, draw, keyboard_press (N/P preskok sobe) |

**Zidovi in ploščice**

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `wall_corner` | Osnovni trden zid; nadrejeni objekt za druga dva tipa zidu | (nič — pasiven trkalnik) |
| `wall_horizontal` | Vodoraven segment zidu (deduje `wall_corner`) | (nič) |
| `wall_vertical` | Navpičen segment zidu (deduje `wall_corner`) | (nič) |

**Zbirljivi predmeti, vrata, cilji in uganka s potiskanjem blokov (room5)**

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `obj_diamond` | Zbirljiv predmet; +5 točk ob pobiranju | destroy, collision_with_obj_person |
| `obj_door` | Zaklenjena vrata; se sama uničijo, ko izginejo vsi diamanti v sobi | step |
| `obj_goal` | Izhod stopnje; napreduje v naslednjo sobo ali konča igro v zadnji sobi | collision_with_obj_person |
| `obj_block` | Premakljiva zaboj; zdrsne za eno celico ob hoji vanj, ali pade v luknjo | collision_with_obj_person |
| `obj_hole` | Jama; uniči samo sebe in vsak blok, potisnjen vanjo | collision_with_obj_block |

**Pošasti in bombna past (room4)**

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `monster_all` | Odbija od zidov v katero koli od 4 smeri | create, collision_with_wall_corner |
| `monster_lr` | Patruljira levo-desno, obrne se ob stiku z zidom | create, collision_with_wall_corner |
| `monster_ud` | Patruljira gor-dol, obrne se ob stiku z zidom | create, collision_with_wall_corner |
| `obj trigger` | Skrita ploščica; ob dotiku predvaja zvok eksplozije, spremeni parni `obj_bomb` v `obj_explosion`, se sama uniči | collision_with_obj_person |
| `obj_bomb` | Neaktiven ograjnik za oboroženo bombo, dokler se ne sproži sprožilec | (nič) |
| `obj_explosion` | 16-sličični izbruh; ob pojavitvi uniči netrdne instance v radiju 64px, se sam uniči ob koncu animacije | create, animation_end |

## Viri

16 sprite-ov (večinoma 32×32 z eno sličico, pikselno natančnih;
`sprite_explosion` je trak 1536×96 s 16 sličicami brez zastavice
precise), 2 ozadji, 8 zvokov — vseh 8 zvokov je referenciranih iz
vsaj enega objekta, za razliko od `maze_2`, kjer ni bil priklopljen
noben. Licenciranje/poreklo virov tega vzorca je **nedokumentirano**
— glejte `CREDITS.txt` v tej mapi, ki kaže na opravilo "Remaining
maze assets" v `docs/ASSET_LICENSES.md`. Za te datoteke ne
predpostavljajte licence CC0 ali katere koli druge.

## Kaj prilagoditi

- `sprite_lives` (16×16) je registriran vir, ki nikoli ni izrisan —
  dejanje `draw_lives` objekta `controller_main` dejansko uporablja
  `sprite_person` v merilu 0,7, tako da `sprite_lives` ostane
  osirotel (ista kategorija kot `tiles.json` pri `maze_2`).
- Izbruh bombne pasti (dogodek create objekta `obj_explosion`) uniči
  igralca prek navadnega `destroy_instance` v svojem preverjanju
  radija, mimo poti `sound_dead`/`set_lives`/`restart_room`, ki jo
  uporabljajo pošasti — če izbruh zajame igralca, tek ostane v
  čudnem stanju namesto čiste smrti/ponovnega zagona.
- Hitrost pošasti je trdo-kodirana `32/6` px/korak pri vseh treh
  arhetipih, medtem ko se igralec premika s `4` — pošasti niso
  zaklenjene na mrežo tako kot igralec, zato njihovo gibanje sčasoma
  ne ostane poravnano s celicami.
- Razhroščevalne tipke `R`/`N`/`P` na `controller_main` so aktivne v
  dostavljenem nadzorniku (glejte Kako igrati) — vredno bi jih bilo
  zapreti za razhroščevalno zastavico, če bi bil ta vzorec še kdaj
  dodatno izpiljen.

## Stanje izvoza

Pokrito z zbirko smoke-testov brez grafičnega vmesnika
(`tools/smoke_run_samples.py`, ki navaja `maze_3` in ga poganja za
fiksno število sličic z vbrizganim vnosom tipkovnice); ni posebej
ponovno preverjeno po ciljih izvoza (Kivy/splet). Izpostavljeno v
zavihku Welcome urejevalnika kot "Maze — Level 3"
(`widgets/welcome_tab.py`).
