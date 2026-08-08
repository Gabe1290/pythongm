# Match-3 — 3. stopnja

Nadaljevanje z omejitvijo potez / več stopnjami / posebnimi
ploščicami za [`match3_2`](../match3_2/README.md), obljubljeno v
prvotnem Načrtu match3_1 — zadnja od treh načrtovanih različic
match3. Ista arhitektura ves čas: brez skriptov, celotna igra je še
vedno štiri dogodke `execute_code` na enem nadzornem objektu, le
postavljena v tri sobe namesto v eno.

**Kje se to umešča:** del družine `match3_*` — čist skript
`execute_code`, brez vgrajenih dejanj, brez ploščic na ravni sobe,
zaključuje potek, opisan v
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays).

**Zvok in glasba:** 5 zvočnih datotek — 3 iz `match3_2`
(`snd_swap`/`match`/`cascade`) plus 2 novi (`snd_special`,
`snd_level_up`), vse dejansko uporabljene prek `self._sound_queue`.

## Kako igrati

Enaka pravila zamenjave/ujemanja/kaskade kot match3_1 in match3_2, plus:

- Imate **omejeno število potez** na stopnjo. Poteza se porabi samo
  ob zamenjavi, ki dejansko ustvari ujemanje — neveljavno zamenjavo
  (ki zdrsne nazaj) lahko poskusite znova brezplačno.
- Dosezite **ciljno oceno** stopnje, preden vam zmanjkajo poteze, da
  napredujete v naslednjo sobo. Če vam zmanjkajo prve, se stopnja
  konča — **kliknite kjer koli za ponovni poskus** iste stopnje od
  začetka.
- **Ujemite 4 v vrsti** (natanko 4) in ena od štirih ploščic postane
  **poseben efekt čiščenja vrste**: bela paličica jo označi. Ujemite
  jo znova pozneje (kot del katerega koli drugega ujemanja) in
  počisti **celotno svojo vrsto ali stolpec** — kar koli od obeh je
  izvirni tek 4 potekal.
- **Ujemite 5 ali več v vrsti** in ena ploščica postane **poseben
  efekt barvne bombe**: bel obroč jo označi. Ujemite jo znova
  pozneje in počisti **vsako ploščico ene barve** po vsej plošči.
- Obstajajo **3 stopnje**, vsaka svoja soba z višjim ciljem in
  strožjo omejitvijo potez. Očistite 3. stopnjo, da zmagate v igri.

## Kaj se razlikuje od match3_2

| match3_2 | match3_3 |
| -------- | -------- |
| Ena soba, neomejene poteze, zmaga pri fiksni oceni | **3 sobe** (ena na stopnjo), **omejitev potez** na stopnjo, in **naraščajoč cilj** na stopnjo |
| Ujemanje je vedno v celoti uničeno | Tek **4** ali **5+** za sabo pusti **posebno ploščico** namesto uničenja vsake celice |
| Brez napredovanja med stopnjami | Doseg cilja pokliče `self.advance_level()`, ki nastavi `self.goto_room_target` na naslednjo sobo (ali `self.won` na zadnji stopnji) |

Osrednji avtomat stanj zamenjave/bliskanja/padanja/kaskade,
izrisovanje ploščic s sprite-i, in sprožilci vrste zvokov so sicer
nespremenjeni glede na match3_2 — celoten opis `swap_off`/`falling`/
`find_matches` glejte v README-ju tistega vzorca.

## Struktura projekta

| Datoteka | Namen |
| ---- | ------- |
| `project.json` | manifest projekta — okno 800×800, 60 sličic/s, začetna soba `rm_level1`, `room_order` = vse 3 stopnje |
| `rooms/rm_level1\|2\|3.json` | ena soba na stopnjo, vsaka vsebuje svojo instanco `obj_GridManager` na (0, 0) |
| `objects/obj_GridManager.json` | celotna igra: štirje dogodki, vsak eno dejanje `execute_code` |
| `sprites/`, `sounds/` | ploščice dragih kamnov + učinki, večinoma kopirani iz match3_2 (glejte `CREDITS.txt`); `snd_special` in `snd_level_up` sta nova |

Še vedno ni objekta po posamezni ploščici in ni skriptov — ena
nadzorna instanca na sobo, ustvarjena na novo (prek običajnega
pravila GameMakerja "vsaka soba ima svoje instance") vsakič, ko je
soba vstopljena, kar vsaki stopnji brezplačno da čisto stanje.

## Kako deluje koda

### Nastavitev stopnje (novo v `create`)

```python
self.room_order = ['rm_level1', 'rm_level2', 'rm_level3']
level_config = {
    'rm_level1': (300, 20),   # (ciljna ocena, omejitev potez)
    'rm_level2': (500, 18),
    'rm_level3': (800, 16),
}
```

`create` prebere `game.current_room.name`, ga shrani v
`self.room_name` (potrebno, ker navadna lokalna spremenljivka,
definirana v enem dogodku `execute_code`, **ne** preživi v poznejši
dogodek — glejte opombo o pasti spodaj), in nastavi
`self.target`/`self.moves`/`self.level_num` iz zgornje tabele.

### Poteze in poraz (novo v `mouse_left_press`)

Zamenjava porabi potezo samo, če `find_matches` pove, da se bo
dejansko ujemala (`if marks: self.moves = self.moves - 1`), tako da
je zavrnjena zamenjava, ki zdrsne nazaj, brezplačna. Ko `self.moves`
doseže 0, ne da bi zadel cilj, `step` nastavi `self.lost = True`;
`mouse_left_press` to zastavico preveri **najprej**, pred navadno
zaščito vnosa, in vsak klik spremeni v `self.restart_room_flag =
True` (ista zastavica, ki jo uporablja `restart_room`), kar znova
zgradi sobo — in z njo svežo instanco `obj_GridManager`, katere
dogodek `create` vse ponastavi.

### Posebne ploščice (novo v `step`)

`find_matches` zdaj vrne `(marks, runs)` namesto le `marks` — vsak
tek je `(cells_in_order, 'h' ali 'v')`. Ob izteku bliskanja, **pred**
točkovanjem:

1. Za vsak tek dolžine ≥ 4 postane **srednja celica** posebna
   ploščica namesto uničena: teki dolžine 4 dobijo `('row',)` ali
   `('col',)` (ujemajoč se z usmerjenostjo teka); teki dolžine 5+
   dobijo `('color', <barvni indeks>)`.
2. Za vsako že označeno celico, ki ima vnos v `self.special` (tj.
   posebna ploščica je bila ravnokar zajeta v *to* ujemanje), se
   njen učinek sproži enkrat: posebna `row`/`col` doda celotno svojo
   vrstico/stolpec med celice, ki se čistijo; posebna `color` doda
   vsako celico na plošči svoje shranjene barve. To je **en sam,
   nerekurziven prehod** — če eksplozija ene posebne ploščice zajame
   drugo posebno ploščico, je ta uničena, vendar **ne** sproži
   verižno svojega lastnega učinka. (Poenostavitev, ne napaka —
   ohranja učinek omejen in preprost za razumevanje.)
3. Novoustvarjene posebne celice so zaščitene pred uničenjem v istem
   valu, tudi če bi jih eksplozija iz koraka 2 sicer zajela.
4. `self.special` se v vsakem valu zgradi na novo, sledeč preživelim
   ploščicam, ko padajo (zanka padanja po stolpcih zdaj nosi tretji
   element terke — posebno vrsto ploščice ali `None` — poleg svoje
   vrstice in barve), tako da posebna ploščica, ki še ni bila
   ujemana, zdrsne navzdol z gravitacijo kot vse ostalo.

### Napredovanje stopnje (novo v `create`, uporabljeno iz `step`)

```python
def advance_level():
    idx = self.room_order.index(self.room_name)
    if idx + 1 < len(self.room_order):
        self.goto_room_target = self.room_order[idx + 1]
        self._sound_queue.append('snd_level_up')
    else:
        self.won = True
self.advance_level = advance_level
```

`self.goto_room_target` je ista zastavica instance, ki jo nastavlja
vgrajeno dejanje `goto_room` — glavna zanka igre jo že vsako sličico
poizveduje, tako da je njena neposredna nastavitev iz `execute_code`
dovolj, da sproži pravi prehod sobe, brez potrebe po strukturiranem
dejanju. `step` pokliče `self.advance_level()`, takoj ko
`self.score >= self.target`, in preskoči vsak ponovni pregled kaskade
za preostanek tiste sličice, če je zdaj v teku menjava sobe (ali
končna zmaga), tako da soba, ki jo zapuščamo, ne nadaljuje animiranja.

### Past: zaprtja nad golimi lokalnimi spremenljivkami ne preživijo med dogodki

Izvajalno okolje `execute_code` posreduje **ločena** slovarja
globalnih in lokalnih spremenljivk (`exec(code, exec_globals,
exec_locals)`), kar pomeni, da se obnaša kot notranjost funkcije:
navadna dodelitev na najvišji ravni (`room_name = ...`) pristane v
slovarju *lokalnih* spremenljivk, vendar `def`, definiran na isti
najvišji ravni, razreši svoje proste spremenljivke prek slovarja
*globalnih* spremenljivk, ko je pozneje **klican** — kar se za
gnezdenega pomočnika, shranjenega na `self` (kot `find_matches`,
`arm_swap`, in zdaj `advance_level`), vedno zgodi iz **drugega** klica
`execute_code` z lastnim svežim slovarjem lokalnih spremenljivk. Gola
lokalna spremenljivka, na katero se sklicuje tak pomočnik, sproži
`NameError` ob prvem dejanskem klicu pomočnika iz drugega dogodka —
videti je videti v redu v definirajočem dogodku in odpove tiho, dokler
se ne sproži pozneje. Popravek je tisti, ki ga je `find_matches` iz
match3_1/`arm_swap` iz match3_2 že modeliral, ne da bi to izrecno
povedal: zapirajte se samo nad `self` (vedno prisoten v globalnih
spremenljivkah vsakega dogodka) ali **atributi instance**
(`self.room_name`, ne gola `room_name`) — nikoli nad golo lokalno
spremenljivko. Ujeto z ločenim korakom preverjanja z ogrodjem med
razvojem (glejte opombe o metodologiji revizije v repozitorijskem
`CLAUDE.md`); zanjo zdaj obstaja regresijski test
(`tests/test_match3_3_sample.py`).

### `draw`

Enako izrisovanje plošče/table/izbire/vrstice s točkami/transparenta
zmage kot match3_2, plus: vrstica HUD za številko stopnje in preostale
poteze, prekrivna bela paličica ali obroč nad sprite-om posebne
ploščice (izpuščen, medtem ko je ploščica sredi utripanja), in
transparent "OUT OF MOVES — click to retry", ko je `self.lost`.

### Kaj prilagoditi

- Težavnost po stopnjah: tabela `level_config` v `create` (ciljna
  ocena, omejitev potez) — dodajte četrti vnos in četrto sobo za
  razširitev zaporedja.
- Radij eksplozije posebne ploščice: veje `row`/`col`/`color` v zanki
  aktivacije v `step`.
- Vse, kar je match3_2 že izpostavil (velikost plošče, hitrost
  zamenjave/padanja, glasnost zvoka).

## Načrt

To zaključuje prvotni tridelni načrt match3_1 (match3_1 → match3_2 →
match3_3). Ni nadaljnjih načrtovanih različic.

## Stanje izvoza

- **Test Game (F5) / namizje:** deluje — preverjeno od začetka do
  konca s pravim zagonom `GameRunner`, ki vbrizga dejanski klik miške
  prek standardne poti dogodkov pygame: prisiljeno ujemanje 4-v-vrsti
  → ustvarjena posebna ploščica → dosežen cilj → **soba se je
  dejansko preklopila na `rm_level2`** s svežo instanco
  (`level_num == 2`, ponastavljena ocena/poteze).
- **Android (.apk) / mobilno (Kivy):** zanaša se na isti mehanizem
  `asset_paths.py` / `_drain_sound_queue` / rezervnega razreševanja
  sprite-a po imenu, ki ga je dodal in preveril match3_2 — ta vzorec
  na tem področju ne preizkuša ničesar novega (brez novih vrst ukazov
  risanja, brez novih vrst dejanj; `goto_room` prek zastavice deluje
  identično v izvoženi zanki scene Kivy, ki že poizveduje iste
  zastavice instance vsako sličico). Za izgradnjo dejanske datoteke
  `.apk` je dodatno potreben buildozer (prek WSL na Windows) — glejte
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Splet (HTML5):** ista logika — nobenih novih primitivov vrste
  risanja ali vrste zvokov onkraj tega, kar je match3_2 že dokazal na
  tem cilju.
- **Samostojni zip:** s tem vzorcem nepreizkušeno.
