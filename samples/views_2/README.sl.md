# Views — 2. stopnja

Demonstracija **kooperativa z deljenim zaslonom**: soba 2400×800 je
prikazana kot dve kameri druga ob drugi v enem oknu 800×600. **Leva
polovica** (view 0) sledi **igralcu 1** (oranžen, tipke s puščicami);
**desna polovica** (view 1) sledi **igralcu 2** (petrolejsko moder,
WASD). Vsak igralec raziskuje skupno sobo v svojem pasu in zbira
kovance — oba opazujete hkrati.

**Kje se to umešča:** druga stopnja četrte družine vzorcev. `views_1`
je uvedla eno samo kamero z rolanjem; `views_2` uvede **več
viewportov hkrati** — drugo osrednjo zmožnost views GameMakerja.
Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za celoten potek. Gibanje ponovno uporablja idiom mreže iz
`maze_1`/`views_1`.

**Zvok in glasba:** nič — nobena zvočna datoteka ni priložena temu vzorcu.

## Kako igrati

- **Igralec 1 (oranžen):** tipke s puščicami — premika v **levi** view.
- **Igralec 2 (petrolejsko moder):** `W` `A` `S` `D` — premika v
  **desni** view.
- Oba se premikata eno celico mreže (32px) naenkrat; zidovi
  (`obj_wall`) so trdni. Osrednji ločevalnik z odprtinami loči oba pasova.
- **Cilj:** zberite 18 kovancev (`obj_coin`) — katerikoli igralec
  lahko pobere katerikoli kovanec; vsak je vreden 10 točk (prikazano
  v naslovu okna).

## Zakaj se oba igralca ustavita neodvisno (resnična past)

Gibanje v mreži se običajno ustavi ob dogodku `nokey` (sproži se, ko
*nobena* tipka ni pritisnjena). Vendar se stanje tipk sledi globalno
med vsemi instancami, tako da z dvema igralcema `nokey` sproži šele,
ko **oba** izpustita vse — igralec 2 bi nadaljeval z drsenjem, medtem
ko igralec 1 drži tipko. Zato se vsak igralec namesto tega ustavi
prek **`keyboard_release`** za **svoje lastne** tipke (puščice za P1,
WASD za P2), ki se sproži po tipki in po objektu. To je razlika glede
na enega igralca v `views_1`, ki lahko varno uporablja `nokey`.

## Kako je nastavljen deljen zaslon

Nevidni nadzornik, `obj_camera`, konfigurira obe views v svojem
dogodku **create** (registriran `enable_views` + dve dejanji
`set_view`), in ista konfiguracija je vgrajena v blok `views` sobe za
pravilnost v sličici 0 pri izvozu:

- **view 0** — `view`/`port` `400×600`, `port_x` 0 (leva polovica),
  `follow` `obj_player1`.
- **view 1** — `view`/`port` `400×600`, `port_x` 400 (desna
  polovica), `follow` `obj_player2`.

Obe views sta **1:1** (velikost view == velikost vrat) in razdeljeni
**levo/desno** (`port_y` 0, polna višina). To je pomembno za
skladnost med cilji: namizje in HTML5 izrisujeta vsako view v 1:1
(odrezujeta + premikata, **ne** skalirata view na svoja vrata), in
delitev levo/desno se izogne inverziji `port_y` med Kivyjem
(y-navzgor) in namizjem/HTML5 (y-navzdol). Pomanjšan minimapski
prikaz (view večji od svojih vrat) tukaj namerno **ni** uporabljen —
skaliral bi se pravilno samo na Kivyju.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest — nastavitve okna/sobe, vgrajeni viri, in konfiguracija `views` z dvema view |
| `rooms/room0.json` | Soba 2400×800 (284 instanc: kamera, zidovi, 2 igralca, 18 kovancev) + njen blok `views` |
| `objects/obj_camera.json` | Nevidni nadzornik: `enable_views` v dogodku create + dva `set_view` |
| `objects/obj_player1.json` | Igralec 1 (tipke s puščicami); gibanje v mreži + ustavitev z `keyboard_release` |
| `objects/obj_player2.json` | Igralec 2 (WASD); gibanje v mreži + ustavitev z `keyboard_release` |
| `objects/obj_coin.json` | Zbirljiv predmet — uničen s strani katerega koli igralca, doda 10 |
| `objects/obj_wall.json` | Statičen trden zid |
| `sprites/` | `spr_player1.png` (oranžen), `spr_player2.png` (petrolejsko moder), `spr_wall.png`, `spr_coin.png` + metapodatki `.json` |
| `CREDITS.txt` | Obvestilo o licenciranju virov |

## Objekti

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `obj_camera` | Nevidni nadzornik; omogoči + konfigurira obe views | create (`enable_views`, 2× `set_view`) |
| `obj_player1` | Igralec leve view (puščice) | keyboard (up/down/left/right/nokey), keyboard_release (po tipki), collision_with_obj_wall |
| `obj_player2` | Igralec desne view (WASD) | keyboard (w/a/s/d/nokey), keyboard_release (po tipki), collision_with_obj_wall |
| `obj_coin` | Zbirljiv predmet, vreden 10 | collision_with_obj_player1, collision_with_obj_player2, destroy (`set_score` +10) |
| `obj_wall` | Statičen trden zid / meja kamere | (nič — pasiven trkalnik) |

## Viri

4 sprite-i (`spr_player1`, `spr_player2`, `spr_wall`, `spr_coin`,
vsak 32×32, ena sličica, pikselno natančen), 0 zvokov. Vsa umetnost
je polne barve CC0, ustvarjena za ta vzorec — glejte `CREDITS.txt`.

## Kaj prilagoditi

- **Smer delitve** — ta vzorec uporablja delitev levo/desno (`port_x`
  0 in 400, `port_y` 0, polna višina). Delitev zgoraj/spodaj bi
  postavila polovici na različna `port_y`; opomba: to se izriše na
  drugačnem navpičnem položaju na Kivyju (y-navzgor) proti
  namizju/HTML5 (y-navzdol), tako da je levo/desno prenosljiva izbira.
- **Širina view** — vsaka view je široka `400` (polovica okna).
  Razširite okno ali zožite views, da spremenite, koliko sobe vidi
  vsak igralec.
- **Robovi** — `hborder` 120 / `vborder` 150 nastavita mrtvo območje
  vsake kamere.

## Stanje izvoza

- **Namizje (pygame):** referenca — `tests/test_views_2_sample.py`
  naloži vzorec, izvede dogodek create objekta `obj_camera`, in
  potrdi, da se kameri rolata **neodvisno** (premik enega igralca ne
  premakne view drugega) in se zaklepata na robu sobe, plus
  točkovanje kovancev in ustavitev z `keyboard_release` po igralcu.
- **Splet (HTML5):** `engine.js` izriše vsako vidno view (odrezovanje
  po view + translacija 1:1); konfiguracija dveh views se prenaša v
  izvoz.
- **Mobilno (Kivy/Android):** izvoznik izriše sobo v Fbo in kopira
  območje vsake vidne view v svoja vrata zaslona
  (`tests/test_kivy_views.py` pokriva izris več views). Dejanji
  `enable_views`/`set_view` sta izpeljani, tako da nastavitev dveh
  views teče iz dogodka create objekta `obj_camera`, kot tudi iz
  vgrajene konfiguracije sobe. Preostala omejitev (kot v `views_1`):
  ciljni izris se zgradi ob ustvarjanju sobe, tako da mora biti
  `views_enabled` v konfiguraciji sobe (kot je tukaj), da kamera
  izriše na Kivyju.
- Skladnost matematike rolanja med cilji je fiksirana z
  `tests/test_views_export_parity.py`.

Izpostavljeno v zavihku Welcome urejevalnika kot "Views — Level 2"
(`widgets/welcome_tab.py`).
