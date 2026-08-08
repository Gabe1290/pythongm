# Views — 1. stopnja

Demonstracija kamere z rolanjem: soba (2400×800) je **trikrat širša
od okna 800×600**, tako da en sam zaslon ne more prikazati vsega.
Kamera (view 0) sledi igralcu, medtem ko hodi desno, razkrivajoč
stopnjo en zaslon naenkrat — celoten smisel **views** v slogu
GameMakerja. Raziskujte široko sobo in zberite vseh 18 kovancev.

**Kje se to umešča:** to je četrta družina vzorcev, ločena od treh
družin tehnike avtorstva (`maze_*` → `plateforme_*` → `match3_*`). Kar
uvaja, ni nov *slog* avtorstva, ampak nova zmožnost motorja: **soba,
večja od okna** s **kamero, ki rola**. Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za celoten potek. Mehansko ponovno uporablja gibanje v mreži iz
`maze_1` (vgrajena dejanja `test_alignment`/`snap_to_grid`/
`start_moving_direction`) in doda natanko eno novo stvar: kamero,
omogočeno iz dogodka **create** igralca z registriranimi dejanji
`enable_views` + `set_view`.

**Zvok in glasba:** nič — nobena zvočna datoteka ni priložena temu vzorcu.

## Kako igrati

- **Tipke s puščicami** premikajo igralca eno celico mreže (32px)
  naenkrat (gibanje, zaklenjeno na mrežo, enako kot `maze_1`).
- Zidovi (`obj_wall`) obrobljajo mejo sobe in tvorijo nekaj notranjih
  stebrov; so trdni in ustavijo igralca.
- **Kamera sledi igralcu**: hodite proti robu zaslona in view zdrsne,
  da vas ohrani v okvirju, se zaklene na robovih sobe, tako da nikoli
  ne vidite mimo obrobe zidov.
- **Cilj:** zberite vseh 18 kovancev (`obj_coin`). Vsak je vreden 10
  točk (prikazanih v naslovu okna).

## Kako je nastavljena kamera

Dogodek **create** igralca izvede dve registrirani dejanji (brez
surovega `execute_code`):

1. `enable_views` — vklopi sistem views za sobo.
2. `set_view` — konfigurira **view 0**: `view_w`/`view_h` `800×600`,
   vrata na `(0,0)` velikosti `800×600`, `follow` = `obj_player`,
   `hborder` 240 / `vborder` 180 (mrtvo območje, preden kamera
   zdrsne), brez omejitve hitrosti rolanja. Ista konfiguracija je
   vgrajena tudi v blok `views` sobe, tako da je kamera pravilna od
   prve sličice na vsakem cilju izvoza.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest projekta — nastavitve okna/sobe, vgrajene kopije virov, in konfiguracija `views` sobe |
| `rooms/room0.json` | Soba 2400×800 (245 instanc: obroba zidov + stebri, igralec, 18 kovancev) in njen blok `views` |
| `objects/obj_player.json` | Igralec: gibanje v mreži + nastavitev kamere v dogodku create |
| `objects/obj_coin.json` | Zbirljiv predmet: uničen ob dotiku igralca, doda 10 k točkam |
| `objects/obj_wall.json` | Statičen trden zid |
| `sprites/` | `spr_player.png`, `spr_wall.png`, `spr_coin.png` + njihovi metapodatki `.json` |
| `CREDITS.txt` | Obvestilo o licenciranju virov |

## Objekti

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `obj_player` | Lik igralca; gibanje v mreži + omogoča/konfigurira kamero | create (`enable_views`, `set_view`), keyboard (down/right/up/left/nokey), collision_with_obj_wall |
| `obj_coin` | Zbirljiv predmet, vreden 10 točk | collision_with_obj_player (`destroy_instance` self), destroy (`set_score` +10) |
| `obj_wall` | Statičen trden zid / meja zaklepanja kamere | (nič — pasiven trkalnik) |

## Viri

3 sprite-i (`spr_player`, `spr_wall`, `spr_coin`, vsak 32×32, ena
sličica, pikselno natančen trk), 0 zvokov. Vsi trije so preprosta
umetnost polne barve CC0, ustvarjena za ta vzorec — glejte `CREDITS.txt`.

## Kaj prilagoditi

- **Velikost sobe** (`2400×800` v `rooms/room0.json`) — naredite jo
  širšo/višjo za daljše rolanje; kamera se zaklene na to, kar koli
  soba je.
- **Robovi** (`hborder` 240 / `vborder` 180 v dejanju `set_view` *in*
  bloku `views` sobe) — manjši robovi omogočajo igralcu, da se
  približa robu, preden se kamera premakne; večji ga ohranjajo bolj
  centriranega.
- **Hitrost rolanja** — `hspeed`/`vspeed` sta `-1` (takojšnje
  sledenje). Nastavite ju na pozitivno vrednost pikslov na sličico za
  zaostajajočo, glajeno kamero.
- **Kovanci** — dodajte/odstranite instance `obj_coin` v `rooms/room0.json`.

## Stanje izvoza

- **Namizje (pygame):** referenčni cilj — preverjen z
  `tests/test_views_1_sample.py`, ki naloži ta vzorec, izvede dogodek
  create igralca, in potrdi, da se kamera rola in zaklene, medtem ko
  igralec hodi po celotni širini.
- **Splet (HTML5):** izvožen `engine.js` nosi isto kamero z 8 views
  (`tests/test_html5_views.py`, preverjeno v Chromiumu med razvojem);
  konfiguracija `views` tega vzorca in `set_view` dogodka create se
  oba prenašata v izvoz.
- **Mobilno (Kivy/Android):** izvožena scena izriše celotno sobo v
  Fbo in kopira območje vsake vidne view v svoja vrata zaslona, z
  oknom operacijskega sistema dimenzioniranim za view (ne za sobo),
  tako da kamera prikazuje pravo rolajočo rezino in podpira več
  viewportov (`tests/test_kivy_views.py`). Dejanji
  `enable_views`/`set_view` sta izpeljani, tako da deluje tudi
  ponovna konfiguracija kamere med izvajanjem. *Ena preostala
  omejitev:* več-view ciljni izris se zgradi ob ustvarjanju sobe,
  tako da mora imeti soba `views_enabled` v svoji konfiguraciji (kot
  jo ima ta vzorec), da kamera lahko izriše — omogočanje views zgolj
  prek `enable_views` med izvajanjem na sobi, ki je začela brez njih,
  je ne bo retroadaptiralo na Kivyju.
- Skladnost matematike rolanja med cilji je fiksirana z
  `tests/test_views_export_parity.py`.

Izpostavljeno v zavihku Welcome urejevalnika kot "Views — Level 1"
(`widgets/welcome_tab.py`).
