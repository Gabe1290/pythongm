# Match-3 — 2. stopnja

Nadaljevanje na osnovi spritov in animacij za
[`match3_1`](../match3_1/README.md), obljubljeno v Načrtu tistega
vzorca: ista plošča in točkovanje, zdaj izrisana z pravimi sprite-i
dragih kamnov namesto barvnih pravokotnikov, z animacijo drsenja pri
zamenjavi in zvočnimi učinki za zamenjavo / ujemanje / kaskado. Še
vedno ena soba, en objekt, brez skriptov — celotna igra je še vedno
štiri dogodke `execute_code` na enem nadzornem objektu.

**Kje se to umešča:** del družine `match3_*` — čist skript
`execute_code`, brez vgrajenih dejanj, brez ploščic na ravni sobe.
Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za razlago, kako se to razlikuje od pristopa
`maze_*`/`plateforme_*` z vgrajenimi dejanji in več objekti.

**Zvok in glasba:** 3 zvočne datoteke (`snd_swap`, `snd_match`,
`snd_cascade`), vse dejansko uporabljene — postavljene v vrsto iz
`execute_code` prek `self._sound_queue` (glejte spodaj), ne prek
dejanja `play_sound`.

## Kako igrati

Enako kot match3_1:

- **Kliknite** ploščico, da jo izberete (bel obris), nato **kliknite
  sosednjo ploščico**, da ju zamenjate. Zamenjava zdaj **zdrsne** na
  mesto namesto takojšnjega preskoka.
- Če zamenjava poravna **3 ali več ploščic enake barve** v vrsti ali
  stolpcu, se ujemajoče ploščice za trenutek zabliskajo, uničijo, in
  ploščice nad njimi **zdrsnejo navzdol**, da zapolnijo vrzel; nove
  ploščice padejo z vrha plošče. Verižne reakcije ("kaskade") se
  razrešujejo val za valom.
- Zamenjava, ki ne ustvari ujemanja, **zdrsne nazaj** na svoj prvotni
  položaj namesto takojšnjega preskoka nazaj.
- Vsaka uničena ploščica je vredna **10 točk**; za zmago dosezite
  **500 točk**.
- Vsak poskus zamenjave predvaja klik; uspešno ujemanje predvaja zvon,
  in vsaka dodatna kaskada v isti kombinaciji predvaja svetlejši,
  naraščajoči zvon.

## Kaj se razlikuje od match3_1

| match3_1 | match3_2 |
| -------- | -------- |
| Ploščice izrisane kot polni barvni pravokotniki | Ploščice izrisane kot **sprite-i** dragih kamnov (ukaz vrste risanja v slogu `draw_sprite`), po ena oblika na barvo zaradi dostopnosti za barvno slepe |
| Zamenjava se uveljavi takoj, ujemanja se ocenijo nemudoma | Zamenjava najprej **zdrsne** na mesto (~4 sličice); neujemajoča se zamenjava zdrsne nazaj namesto takojšnjega preskoka |
| Brez zvoka | **Zvočni učinki** za zamenjavo / ujemanje / kaskado, postavljeni v vrsto iz `execute_code` prek novega primitiva `self._sound_queue` (glejte spodaj) |

Logika plošče same (model mreže, iskanje ujemanj, kaskadno padanje,
točkovanje, pogoj zmage) je nespremenjena glede na match3_1 — to je
resnično berljiva razlika, ne prepis.

## Struktura projekta

| Datoteka | Namen |
| ---- | ------- |
| `project.json` | manifest projekta — okno 800×800, 60 sličic/s, začetna soba `rm_match3` |
| `rooms/rm_match3.json` | edina soba; vsebuje eno instanco `obj_GridManager` na (0, 0) |
| `objects/obj_GridManager.json` | celotna igra: štirje dogodki, vsak eno dejanje `execute_code` |
| `sprites/spr_gem_red\|blue\|green\|yellow.png` | ploščice dragih kamnov 88×88 (glejte `CREDITS.txt`) — dimenzionirane tako, da padejo natanko tja, kjer je bilo prej polnjenje pravokotnika iz match3_1, saj `draw_sprite` izrisuje v naravni velikosti brez skaliranja |
| `sounds/snd_swap\|match\|cascade.wav` | kratki sintetizirani toni (glejte `CREDITS.txt`) |

## Kako deluje koda

Stanje in avtomat stanj `step` sta enaka kot v match3_1 (`grid`,
`sel`, `marked`, `flash`/`flash_total`, `falling`/`fall_speed`,
`score`, `target`, `won`, `find_matches`) — celoten opis glejte v tistem
README-ju. Novo stanje, dodano za to različico:

| Atribut | Pomen |
| --------- | ------- |
| `sprite_names` | `['spr_gem_red', 'spr_gem_blue', 'spr_gem_green', 'spr_gem_yellow']`, indeksirano enako, kot je bil `palette` v match3_1 |
| `swap_off` | slovar `(gx, gy) → (dx, dy)` odmik v pikslih za drsenje zamenjave v teku; upada proti `(0, 0)` s hitrostjo `swap_speed` px/sličico, ista tehnika krčenja-do-mirovanja, ki jo `falling` že uporablja za kaskade, posplošena na dve osi |
| `swap_phase` | `None` / `'forward'` (drsenje na zamenjano mesto) / `'back'` (zavrnjena zamenjava, ki drsi nazaj na svoje prvotne celice) |
| `last_swap` | `(gx, gy, sx, sy)` — dve celici, vključeni v zamenjavo v teku, tako da lahko `step` ju povrne brez potrebe po stanju zaprtja |
| `pending_marks` | množica ujemanj, izračunana takoj po zamenjavi, zadržana, dokler se animacija drsenja ne konča, da bliskanje ne začne sredi drsenja |
| `arm_swap(a, b)` | pomožna funkcija (definirana v `create`, shranjena na instanci kot `find_matches`), ki nastavi `swap_off` za obe celici zgolj iz njunih položajev — ponoven klic z istima celicama proizvede obratno animacijo, kar poganja povratno drsenje brezplačno |

Posodobljen potek:

```
klik na sosednjo ploščico
  → mreža takoj zamenjana (podatki), izračunani pending_marks
  → swap_off aktiviran (forward) — ploščice zdrsnejo na svoje nove celice
       │
       ▼ (drsenje se umiri)
  pending_marks?
    da → sproži bliskanje (utripanje → uničenje → padanje → ponovno preverjanje, kot v match3_1)
    ne → mreža zamenjana nazaj, swap_off ponovno aktiviran z ISTIMA celicama (phase='back')
             │
             ▼ (drsenje se umiri)
          idle
```

- **`create`** — enako sejanje mreže kot match3_1, plus
  `sprite_names`, `swap_off`/`swap_speed`/`swap_phase`/`last_swap`/
  `pending_marks`, in pomožna funkcija `arm_swap`.
- **`mouse_left_press`** — logika izbire je nespremenjena; veljavna
  sosednja zamenjava zdaj uveljavi zamenjavo mreže, izračuna
  `pending_marks`, sproži drsenje naprej in postavi v vrsto `snd_swap`.
- **`step`** — bloki bliskanja/padanja so nespremenjeni glede na
  match3_1 (še vedno postavijo `snd_cascade` v vrsto ob verižnem
  ponovnem ujemanju); nov blok `elif self.swap_off:` upada drsenje in,
  ko se umiri, bodisi sproži bliskanje (postavi v vrsto `snd_match`)
  bodisi sproži povratno drsenje.
- **`draw`** — enako izrisovanje plošče/table/izbire/točk/navodil/
  transparenta zmage kot match3_1, vendar je zdaj vsaka ploščica ukaz
  vrste risanja `{'type': 'sprite', 'sprite_name': ..., 'x': ...,
  'y': ...}` namesto polnega pravokotnika (še vedno zamenjan s
  preprostim belim polnim pravokotnikom med utripanjem označene
  ploščice, natanko kot je počel match3_1), odmaknjen za `swap_off`
  v kombinaciji s `falling`.

### Primitiv `self._sound_queue`

`execute_code` ima živ predmet `game` samo v izvajalnem okolju
namiznega pygame — tako izvoženo izvajalno okolje Kivy kot izvajalno
okolje Web/Pyodide vežeta `game = None` v tem obsegu, zato
`game.sounds[...].play()` (očitna izbira) deluje samo na namizju. Ta
vzorec je spodbudil dodajanje pravega medplatformskega primitiva
namesto tega: kateri koli dogodek `execute_code` lahko naredi

```python
self._sound_queue.append('snd_swap')
# ali, za neprivzeto glasnost:
self._sound_queue.append({'sound': 'snd_swap', 'volume': 0.5})
```

in se predvaja identično na vseh treh ciljih:

- **Namizje** — `ActionExecutor.execute_event` ga izprazni in predvaja
  (prek `game.sounds[...]`) takoj po vsakem dogodku, ne le po `draw`.
- **Izvoz Kivy** — `GameObject._drain_sound_queue` (generirano v
  `base_object.py`) razreši ime prek generiranega `asset_paths.py`
  (`SOUND_PATHS`) in kliče obstoječi pomočnik `play_sound()`;
  izpraznjen enkrat na sličico na živo instanco iz zanke `update()`
  scene, tako da deluje tudi za objekte brez dogodka `draw`.
- **Splet (Pyodide)** — Python zagonski del vrne vse zvoke v vrsti v
  JSON popravku poleg vrste risanja; `engine.js` jih predvaja kot
  prave elemente `<audio>` prek iste poti predpomnjenega zvoka, ki jo
  že uporablja strukturirano dejanje `play_sound`.

Ista vrzel v razreševanju po imenu je obstajala za ukaze v slogu
`draw_sprite`, poslane iz surovega `execute_code` (izrisovanje ploščic
v tem vzorcu) — izrisovalnik vrste risanja Kivy je prej razreševal
sprite samo iz `sprite_path`, zapečenega ob generiranju kode za
*strukturirana* dejanja, tako da ročno napisan slovar
`{'type': 'sprite', 'sprite_name': ...}` tam ni bil izrisan. Popravljeno
enako: `asset_paths.py` prenaša tudi `SPRITE_PATHS`, in primer
`'sprite'` v vrsti risanja Kivy se po imenu vrne nanj, kadar ni
prisotna vnaprej razrešena pot.

### Kaj prilagoditi

Enaki gumbi kot match3_1 (`self.cols`/`self.rows`, `self.palette`,
`self.target`, `flash_total`, `fall_speed`), plus:

- Hitrost animacije zamenjave: `self.swap_speed` (px/sličico; 24 →
  ~4 sličice na drsenje pri `tile=96`).
- Glasnost zvoka: podajte slovar `{'sound': ..., 'volume': ...}`
  namesto golega imena v `self._sound_queue.append(...)`.

## Načrt

**[match3_3](../match3_3/README.md)** — narejeno: omejitev potez, tri
sobe kot stopnje z naraščajočim ciljem, in posebne ploščice (bonusi
za 4/5-v-vrsti). Zaključuje prvotni načrt iz match3_1.

## Stanje izvoza

- **Test Game (F5) / namizje:** deluje — preverjeno od začetka do
  konca s pravim zagonom `GameRunner`, ki vbrizga dejanski klik miške
  prek standardne poti dogodkov pygame (zamenjava → ujemanje →
  kaskada → točke, z opazovanimi dejanskimi klici
  `pygame.mixer.Sound.play()`).
- **Android (.apk) / mobilno (Kivy):** **podprto.** Preverjeno, da se
  izvoz čisto prevede, da `asset_paths.py` prenaša prave
  `SPRITE_PATHS`/`SOUND_PATHS`, in da so slike spritov / zvočne
  datoteke kopirane v `assets/images` / `assets/sounds`. Za izgradnjo
  dejanske datoteke `.apk` je dodatno potreben buildozer (prek WSL na
  Windows) — glejte [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Splet (HTML5):** **podprto.** Zagonski del Pyodide izvožene strani
  izprazni `self._sound_queue` v isti JSON krogotok kot vrsto risanja;
  preverjeno, da se generirani zagonski del prevede in pravilno
  krožno prenese tako ukaze risanja kot postavljene zvoke pod čistim
  CPythonom (za to preverjanje brskalnik ni potreben — sam zagon
  Pyodide v brskalniku ni preizkušen z avtomatizirano zbirko, enak
  pomislek kot pri match3_1). Ob prvem nalaganju potrebuje dostop do
  interneta (Pyodide se naloži z omrežja CDN).
- **Samostojni zip:** s tem vzorcem nepreizkušeno.
