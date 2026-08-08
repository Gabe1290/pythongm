# Ploščad — 3. stopnja

Platformerska igra z bočnim rolanjem, uvožena iz GameMaker 8.x
(`samples/plateforme_3.gmk`). Je daleč največji od treh vzorcev
ploščadi: 2 objekta (plateforme_1) → 4 objekti (plateforme_2) →
**15 objektov** tukaj, kar doda patruljne kopenske in leteče pošasti
(z ubijanjem s poskokom na glavo in ob teku ustvarjenimi različicami
trupla/madeža), nevidno takojšnjo smrtonosno nevarnost, dve vrsti
zbirljivih predmetov, in izhodni objekt, ki napreduje v naslednjo sobo
ali prikaže tabelo najboljših rezultatov in se ponovno zažene.

**Kje se to umešča:** del družine `plateforme_*` — kot `plateforme_2`
uporablja **tlakovano ozadje** (125 kosov ploščic pod trdnimi objekti
opeke, plus slika gradienta `fond_degrade`), korak, ki ga ta družina
doda onkraj `maze_*`. Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za celoten potek.

**Zvok in glasba:** 4 zvočne datoteke, resnično priklopljene: 7 mest
klica `play_sound` za `son_bonus` (pobiranje), `son_monstre_mort`
(ubijanje s poskokom), `son_personnage_mort` (smrt igralca), in
`son_niveaufini` (dokončanje stopnje).

## Kako igrati

- **Puščica levo/desno** — premika Pingusa (`obj_pingus`) levo/desno.
- **Puščica gor** — skok, a samo medtem ko stoji na nečem trdnem
  (preverjeno en piksel pod igralcem).
- **Cilj** — zberite predmete `obj_bonus` (+5 točk) in `obj_power`
  (+20 točk), medtem ko prečkate `niveau_01`, da dosežete
  `obj_sortie`; dotik z njim predvaja melodijo in bodisi napreduje v
  naslednjo sobo (v tem vzorcu je ni, tako da pade v vejo
  najboljših-rezultatov/ponovnega-zagona) bodisi prikaže tabelo
  najboljših rezultatov in ponovno zažene igro.
- **Pošasti** — pristanek na vrhu `obj_monstre` ali
  `obj_monstre_volant` (`vspeed > 0` in nad pošastjo) jo ubije in
  prinese 50 točk; udarec vanjo s strani ali od spodaj stane življenje
  in ponovno zažene sobo. Opomba: trk z `obj_monstre_volant` je brez
  učinka (leteča pošast ne more prizadeti ali biti prizadeta), dokler
  ni bil pobran `obj_power` — glejte Kaj prilagoditi.
- **Pogoj poraza** — dotik `obj_mortel` (nevidno območje takojšnje
  smrti) ali napačen dotik pošasti stane življenje in ponovno zažene
  sobo; ko zmanjkajo življenja (`no_more_lives`), se prikaže tabela
  najboljših rezultatov in ponovno zažene celotna igra. Začetna
  življenja: 3 (nastavitve `project.json`).

## Struktura projekta

| Datoteka | Namen |
| --- | --- |
| `project.json` | Manifest projekta — nastavitve okna/sobe, vgrajene kopije virov. |
| `rooms/niveau_01.json` | Edina soba: 800×640, 194 instanc + 125 ploščic ozadja. Vir resnice za vsebino sobe (vgrajeni seznam `instances` v `project.json` je prazen, enak vzorec kot pri plateforme_2). |
| `objects/*.json` | Stranske datoteke po posameznem objektu za vseh 15 objektov; ob pisanju tega besedila identične vgrajenim kopijam v `project.json` (preverjeno bajt za bajtom, za razliko od datoteke sobe pri plateforme_2). |
| `sprites/` | 18 sprite virov (trakovi hoje/letenja, sprite-i smrti, ploščadni bloki, zbirljivi predmeti, izhod, oznaka). |
| `sounds/` | 4 zvočni učinki (smrt pošasti, smrt igralca, pobiranje bonusa, dokončanje stopnje). |
| `backgrounds/` | Nabor snežnih ploščic (`tuiles_neige.png`, vir avtomatskih ploščic za 125 ploščic sobe) in navpičen gradient (`fond_degrade.png`) kot ozadje sobe. |
| `CREDITS.txt` | Obvestilo o licenciranju umetniškega dela spritov/ozadja (glejte Vire spodaj). |

## Objekti

15 objektov, razvrščenih po vlogi. Prikazano je število postavitev v
sobi (od 194 instanc), kjer se objekt pojavi v `niveau_01`; objekti,
"ustvarjeni ob teku", se pojavijo samo prek `change_instance` med igro.

| Objekt | Vloga | Ključni dogodki |
| --- | --- | --- |
| `obj_pingus` | Igralec — gibanje, skok, gravitacija, vsa obravnava trkov/poraza/zmage | create, step, keyboard (left/right/up), keyboard_release, collision_with_obj_brique/obj_monstre/obj_monstre_volant/obj_mortel/obj_bonus/obj_power/obj_sortie/obj_marqueur, game_start, no_more_lives |
| `obj_brique` | Osnoven trden ploščadni blok, 32×32 (109 postavljenih) | nič (samo zastavica solid) |
| `obj_brique_h` | Široka ploščadna različica, 32×16, otrok `obj_brique` (15 postavljenih) | nič |
| `obj_brique_v` | Ozka ploščadna različica, 16×32, otrok `obj_brique`; definirana, a ni postavljena v `niveau_01` | nič |
| `obj_brique_c` | Majhna ploščadna različica, 16×16, otrok `obj_brique` (1 postavljena) | nič |
| `obj_monstre` | Kopenska pošast — patruljira levo/desno, obrne se ob stiku z zidom (3 postavljene) | create, collision_with_obj_brique |
| `obj_monstre_mort` | Ob teku ustvarjeno truplo pošasti po ubijanju s poskokom; deduje `obj_brique` (postane trdna stopnica) | create |
| `obj_monstre_volant` | Leteča pošast — patruljira desno, odbija se od zidov (2 postavljeni) | create, collision_with_obj_brique |
| `obj_monstre_volant_mort` | Ob teku ustvarjeno truplo leteče pošasti; pade z omejeno gravitacijo, pristane na ploščadih/oznakah | step, collision_with_obj_brique, collision_with_obj_marqueur |
| `obj_mortel` | Nevidno območje takojšnje smrtonosne nevarnosti (4 postavljena) | nič (obravnavano iz dogodka trka `obj_pingus`) |
| `obj_splat` | Ob teku ustvarjena animacija smrti igralca, ponovno zažene sobo ob koncu animacije | create, animation_end |
| `obj_bonus` | Manjši zbirljiv predmet, +5 točk, naključna sličica v mirovanju (52 postavljenih) | create |
| `obj_power` | Večji zbirljiv predmet, +20 točk; tudi pogojuje, ali leteče pošasti lahko prizadenejo ali so prizadete (1 postavljen) | create |
| `obj_sortie` | Izhod stopnje — predvaja melodijo, nato naslednja soba ali najboljši rezultat + ponovni zagon (1 postavljen) | nič (obravnavano iz dogodka trka `obj_pingus`) |
| `obj_marqueur` | Nevidna, netrdna oznaka za oblikovanje sobe; trki so izrecno brez učinka (5 postavljenih) | nič |

## Viri

18 sprite-ov, 4 zvoki, 2 ozadji. Umetniško delo spritov/ozadja je
prilagojeno iz projekta Pingus (GPL-3.0-or-later) — glejte
`CREDITS.txt` za polno navedbo in licenčne pogoje; ta README teh
trditev ne ponavlja niti jim ne dodaja.

## Kaj prilagoditi

- Test poskoka na glavo `obj_pingus` proti `obj_monstre`/
  `obj_monstre_volant` je bil prej `vspeed > 0 and y < other.y+8`, kar
  bi lahko hiter padec presegel (okno 8px je bilo preverjeno glede na
  položaj *po premiku*) in stalo življenje pri navidezno čistem
  poskoku. Zdaj je `vspeed > 0 and y - vspeed < other.y+8`, kar okno
  namesto tega preveri glede na položaj pred premikom.
- Pobiranje `obj_power` tiho pogojuje vso interakcijo z
  `obj_monstre_volant` (prek `if_object_exists(obj_power,
  not_flag=true)` okoli logike poskoka/smrti v `obj_pingus`) — vredno
  bi bilo to narediti vidno igralcem (npr. sprememba sprite-a/palete)
  namesto nevidnega pravila.
- Vodoravna hitrost igralca je fiksna `hspeed = 4`; impulz skoka je
  `vspeed = -10`; gravitacija padca je `0,5` z omejitvijo končne
  hitrosti `vspeed = 24`.
- Velikost sobe je 800×640 pri `room_speed = 30`.

## Stanje izvoza

Ta vzorec je naveden na seznamu `SAMPLES` v
`tools/smoke_run_samples.py`, tako da ob vsakem teku tega ogrodja
dobi smoke-prehod brez grafičnega vmesnika (prava zanka igre teče za
~180 sličic z vbrizganim vnosom tipkovnice). Za ta vzorec posebej ni
bilo izvedeno preverjanje glede na ciljna izvoza (Kivy/HTML5).
Izpostavljen je v zavihku Welcome urejevalnika kot "Platform —
Level 3" (`widgets/welcome_tab.py`).
