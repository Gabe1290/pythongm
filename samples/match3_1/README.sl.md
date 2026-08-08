# Match-3 — 1. stopnja

Minimalna, popolna uganka match-3 (tri v vrsti). To je prvi vzorec
pygm2, **napisan neposredno v lastnem formatu projekta urejevalnika**
— vzorca labirinta in ploščadi sta bila uvožena iz datotek GameMaker
8.x `.gmk`; ta je bil napisan neposredno za izvajalno okolje pygm2.

Namenoma je majhen: ena soba, en objekt, brez skriptov, brez zvokov.
Celotna igra živi v štirih dogodkih enega samega nadzornega objekta,
zaradi česar je to referenčni vzorec za dejanje `execute_code` in za
izrisovanje prek vrste ukazov za risanje (draw queue). Naprednejše
različice (ploščice na osnovi spritov, zvok, stopnje) so
načrtovane kot `match3_2` itd. — glejte *Načrt* spodaj.

**Kje se to umešča:** `match3_*` je zadnja (in najbolj drugačna) od
treh družin vzorcev — drugačna paradigma, ne postopen korak: brez
vgrajenih dejanj, brez objektov po posamezni ploščici, brez ploščic
na ravni sobe. Vse (stanje mreže, trki, izris) je vodeno neposredno
iz Python kode `execute_code` namesto sestavljeno iz vgrajenih dejanj
prek mnogih objektov, kot to počneta `maze_*` in `plateforme_*`.
Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za celoten potek.

**Zvok in glasba:** brez — namenoma, glede na zgornji odstavek. (Zvok
postane mogoč od `match3_2` naprej, prek primitiva vrste zvokov, ki
ga je uvedel tisti vzorec.)

## Kako igrati

- **Kliknite** ploščico, da jo izberete (bel obris), nato **kliknite
  sosednjo ploščico**, da ju zamenjate.
- Če zamenjava poravna **3 ali več ploščic enake barve** v vrsti ali
  stolpcu, se ujemajoče ploščice za trenutek zabliskajo, uničijo, in
  ploščice nad njimi **zdrsnejo navzdol**, da zapolnijo vrzel; nove
  ploščice padejo z vrha plošče.
- Verižne reakcije ("kaskade") se razrešujejo val za valom, vsaka s
  svojo animacijo bliskanja in drsenja.
- Zamenjava, ki ne ustvari ujemanja, se takoj razveljavi.
- Vsaka uničena ploščica je vredna **10 točk**; za zmago dosezite
  **500 točk**.

## Struktura projekta

| Datoteka | Namen |
| ---- | ------- |
| `project.json` | manifest projekta — okno 800×800, 60 sličic/s (`room_speed`), začetna soba `rm_match3` |
| `rooms/rm_match3.json` | edina soba; vsebuje eno instanco `obj_GridManager` na (0, 0) |
| `objects/obj_GridManager.json` | celotna igra: štirje dogodki, vsak eno dejanje `execute_code` |
| `sprites/spr_red|blue|green|yellow.*` | ploščice 32×32 — **še niso uporabljene**; rezervirane za nadaljevanje na osnovi spritov (glejte `CREDITS.txt`) |

Ni objekta igralca in ni objekta po posamezni ploščici: plošča je
čisti podatek (seznam barvnih indeksov 6×6), ki pripada eni sami
nevidni nadzorni instanci, in vse na zaslonu izriše dogodek `draw`
tega nadzornika prek vrste ukazov za risanje izvajalnega okolja
(`self._draw_queue`).

## Kako deluje koda

Vse stanje živi na nadzorni instanci (`self.…`), ustvarjeno v
dogodku `create`:

| Atribut | Pomen |
| --------- | ------- |
| `grid` | seznam 6×6 celih števil 0–3 (indeksi v `palette`); zasejano brez že obstoječih ujemanj |
| `sel` | trenutno izbrana celica `(gx, gy)` ali `None` |
| `marked` | množica celic, ki trenutno ujemajo in bliskajo |
| `flash` / `flash_total` | preostale sličice faze bliskanja / njena dolžina (36 sličic ≈ 0,6 s pri 60 sličicah/s) |
| `falling` | slovar `(gx, gy) → piksli` — koliko nad svojo počivajočo celico je trenutno vsaka drseča ploščica |
| `fall_speed` | hitrost drsenja v pikslih na sličico (12 → ena vrsta 96 px v ~0,13 s) |
| `score`, `target`, `won` | stanje točkovanja (zmaga pri 500) |
| `find_matches` | pomožna funkcija (definirana v `create`, shranjena na instanci), ki preišče mrežo in vrne množico vseh ujemajočih se celic |

Igra je majhen avtomat stanj, voden z dogodkom `step`:

```
idle ──(kliki zamenjajo, ujemanje najdeno)──▶ FLASH (označene bliskajo, 36 sličic)
                                        │ ploščice uničene, točke dodane
                                        ▼
                                      FALL (odmiki se krčijo za 12 px/sličico)
                                        │ pristanek → ponovno preišči mrežo
                             novo ujemanje ─┴─ brez ujemanja
                                 │            │
                                 ▼            ▼
                               FLASH        idle
```

- **`create`** — zgradi začetno mrežo (znova žreba katero koli
  ploščico, ki bi ustvarila takojšnje ujemanje), inicializira zgornje
  stanje in definira `find_matches`.
- **`mouse_left_press`** — logika izbire/preklica izbire; ob sosednji
  zamenjavi jo izvede in bodisi sproži bliskanje (`marked`, `flash`)
  bodisi jo razveljavi. Vnos se ignorira, dokler poteka bliskanje ali
  padanje, in po tem, ko je igra zmagana.
- **`step`** — odšteva bliskanje; ob izteku prizna točke, prepiše
  vsak prizadeti stolpec na njegovo končno postavitev in zabeleži
  odmik v pikslih v `falling` za vsako ploščico, ki se je premaknila
  (preživele ploščice dobijo `rows_dropped × 96`; ploščice za dopolnitev
  vstopijo od zgoraj plošče). Dokler `falling` ni prazen, se vsak
  odmik krči za `fall_speed`; ko vse pristane, se ponovno preišče za
  kaskadna ujemanja in bodisi ponovno sproži bliskanje bodisi se
  vrne v idle.
- **`draw`** — izriše ploščo, nato vsako ploščico na
  `počivajoči_položaj − odmik_padanja`. Ploščice nad zgornjim robom
  plošče so odrezane (delno prikazane) ali izpuščene (popolnoma
  skrite), tako da se zdi, da dopolnitve zdrsnejo izpod glave. Označene
  ploščice zabliskajo belo vsakih 6 sličic in imajo bel obris; izbira,
  vrstica s točkami, navodila in transparent zmage se izrišejo nazadnje.

### Kaj prilagoditi

- Velikost plošče: `self.cols` / `self.rows` (konstante postavitve
  `ox`, `oy`, `tile` nadzorujejo namestitev — plošča 6×6 s ploščicami
  96 px se prilega oknu 800×800).
- Barve / vrste ploščic: `self.palette` (dodajte nabor za 5. barvo;
  logika ponovnega žrebanja in izrisovalnik jo samodejno zaznata,
  vendar posodobite `random.randrange(4)` v `create` in `step`).
- Težavnost: `self.target` (točke za zmago), `flash_total`,
  `fall_speed`.

## Načrt (načrtovane napredne različice)

- **[match3_2](../match3_2/README.md)** — narejeno: izriše ploščice s
  sprite-i namesto barvnih pravokotnikov, doda zvočne učinke za
  zamenjavo/ujemanje/kaskado in animacijo drsenja pri zamenjavi.
- **[match3_3](../match3_3/README.md)** — narejeno: omejitev potez,
  tri sobe kot stopnje z naraščajočim ciljem, in posebne ploščice iz
  ujemanj 4/5-v-vrsti. Zaključuje ta načrt.

Različice naj bi zrcalile potek maze_1→3: vsaka je berljiva razlika
glede na prejšnjo.

## Stanje izvoza

- **Test Game (F5) / namizje:** deluje — igra teče na standardnem
  izvajalnem okolju pygame. Preizkušena je brez grafičnega vmesnika v
  poganjanjih v slogu CI prek `tools/smoke_run_samples.py`.
- **Android (.apk) / mobilno (Kivy):** **podprto** (od 03.07.2026).
  Izvožen izvajalnik Kivy izriše vrsto ukazov za risanje igre
  (pravokotnike in besedilo, z osjo y pretvorjeno v Kivyjev okvir od
  spodaj navzgor), pošilja dotike kot dogodek `mouse_left_press` s
  koordinatama sobe `mouse_x`/`mouse_y` tako na Androidu (z
  obračanjem transformacije celozaslonskega skaliranja) kot na
  namiznem Kivyju, in — ker ta igra nima dogodkov tipkovnice —
  izpušča prekrivno navidezno smerno tipkovnico (D-pad), ki bi sicer
  prekrila spodnji desni del plošče. Izvožena igra je preizkušena
  brez grafičnega vmesnika v
  `tests/test_kivy_draw_queue_mouse_export.py`, ki odigra popoln krog
  zamenjava → bliskanje → drsenje skozi generirano kodo. Za izgradnjo
  dejanske datoteke `.apk` je dodatno potreben buildozer (prek WSL na
  Windows) — glejte
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md) za celoten
  vodnik (nastavitev, časi gradnje, predpomnjenje za razred/sejo);
  preostale vrzeli v enakovrednosti izvoza za Kivy, ki *ne* vplivajo
  na to igro, so navedene pod "Kivy/Android export" v repozitorijskem
  `TODO.md`.
- **Splet (HTML5):** **podprto** (od 10.07.2026) — in najboljša pot
  do iPhonov (brez namestitve, brez podpisovanja). Izvožena stran
  zazna, da igra vsebuje dogodke Python `execute_code`, in naloži
  izvajalno okolje Pyodide, da jih izvede s semantiko urejevalnika;
  dotiki/kliki se pošljejo kot dogodek pritiska leve miškine tipke, in
  vrsta ukazov za risanje se izriše na platno. Preverjeno od začetka
  do konca v brezglavem Chromiumu (plošča se izriše, klik-zamenjava,
  bliskanje, drsenje, točkovanje). En pomislek: izvajalno okolje
  Python se naloži z omrežja CDN, zato stran ob odpiranju potrebuje
  dostop do interneta — igre s čistimi dejanji (vzorca
  labirinta/ploščadi) ostanejo popolnoma brez povezave.
- **Samostojni zip:** s tem vzorcem nepreizkušeno.
