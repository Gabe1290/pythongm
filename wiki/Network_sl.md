# Omrežje (večigralska igra prek LAN)

*[Domov](Home_sl) | [Popolna referenca dejanj](Full-Action-Reference-Network-Actions_sl) | [Razširitve](Extensions_sl)*

---

PyGameMaker lahko projekt spremeni v **večigralsko igro prek lokalnega omrežja
(LAN)**: en računalnik gosti, drugi se pridružijo prek lokalnega omrežja, igralci
pa si delijo stanje — lestvico točk, lastna sporočila in celo avatarje drug
drugega na zaslonu — brez strežnika, brez računa in brez interneta. To
zagotavlja vgrajena [razširitev](Extensions_sl) **LAN Multiplayer**, ki je
privzeto vklopljena.

Priloženi primeri **`reseau_1`–`reseau_3`** so popolni, igrljivi primeri:
skupna soba, v kateri se dva igralca gibljeta skupaj, razredni kviz z
lestvico točk v živo in sodelovalno iskanje zaklada za dva.

Danes podprto: izvoz za **namizje** (pygame), kot gostitelj in kot odjemalec, ter
izvoz **HTML5** kot odjemalec (brskalniška stran se pridruži gostitelju na
namizju; sama ne more gostiti). Izvoz **Kivy/Android** igro izvaja kot
enoigralsko — omrežna dejanja tam varno ne naredijo ničesar.

---

## Dve stopnji

**Stopnja A — skupna tabla.** Brez avatarjev, samo skupno stanje: spremenljivke,
ki jih lahko bere in piše vsak igralec, lastna sporočila in kdo je povezan. To
je najpreprostejši način, da projektu dodate večigralski način — kviz, skupna
lestvica točk, igra z zvoncem »kdo prvi odgovori«.

**Stopnja B — omrežni primerki.** Primerki, ki jih ustvari gostitelj (igralci,
sovražniki, predmeti za pobiranje) in se samodejno pojavijo ter gibljejo na
vsakem računalniku, ter avatarji v lasti igralca, ki jih vsak upravlja
lokalno, medtem ko drugi vidijo gladko interpolirano kopijo.

---

## Kako deluje

- En igralec pokliče **Gosti igro**, običajno iz dogodka Create predmeta
  krmilnika sobe. Ta računalnik postane **gostitelj** — računalniki vseh
  drugih igralcev se povežejo nanj. `global.player_id` postane `0`.
- Drugi igralci pokličejo **Pridruži se igri** z naslovom IP gostitelja v omrežju LAN
  (ali z `"auto"`, da se prikaže vgrajen zaslon za povezavo, ki gostitelje v
  omrežju najde samodejno). `global.player_id` dodeli gostitelj (`1`, `2`, ...).
- Če gostitelja ni mogoče doseči, **igra teče naprej kot enoigralska** —
  pridružitev igre nikoli ne zablokira ali podre.
- Identiteta igralca in stanje povezave sta vedno berljivi kot globalni
  spremenljivki: `global.is_host`, `global.player_id`, `global.player_count`,
  `global.network_role`, `global.network_connected`.
- **Logiko igre pišite z navadnim dejanjem »Če«**, na primer
  `global.is_host == 1`, da pripravo (npr. ustvarjanje sovražnikov) prepustite
  samo gostitelju — posebna dejanja »omrežnega pogoja« niso potrebna.
- Skupna spremenljivka, nastavljena z **Nastavi skupno spremenljivko**, je berljiva
  *povsod* kot `global.<ime>` — tudi na računalniku, ki jo je nastavil.
- **Lastna sporočila** (**Pošlji omrežno sporočilo**) omogočajo sporočiti
  dogodek po imenu z majhnim priloženim podatkom — pritisk na zvonec, izbran
  odgovor, zastavico »pripravljen«.

---

## Dejanja (kategorija **Omrežje**)

| Dejanje | Kaj naredi |
|---------|------------|
| **Gosti igro** | Postane gostitelj. Po želji prikaže čakalnico z gumbom Začni. |
| **Pridruži se igri** | Poveže se z gostiteljem po naslovu (ali `"auto"` za vgrajen zaslon za povezavo). |
| **Zapusti igro** | Prekine povezavo (ali preneha gostiti) in počisti omrežne globalne spremenljivke. |
| **Začni omrežno igro** | Samo gostitelj: konča čakalnico in vsem sporoči, naj začnejo. |
| **Nastavi skupno spremenljivko** | Zapiše spremenljivko, ki jo lahko vsak računalnik bere kot `global.<ime>`. |
| **Preberi skupno spremenljivko** | Skupno spremenljivko kopira v globalno (za uporabo v izračunu). |
| **Pošlji omrežno sporočilo** | Vsem pošlje lastno poimenovano sporočilo s podatki. |
| **Ustvari omrežni predmet** | Samo gostitelj: ustvari primerek, ki se pojavi pri vseh odjemalcih. |
| **Sinhroniziraj ta primerek** | Označi delujoči primerek kot podvojen med računalniki. |
| **Nastavi lastnika primerka** | Določenemu igralcu da lokalni nadzor nad sinhroniziranim primerkom. |
| **Če upravljam ta primerek** | Pogoj: krmilno logiko omeji, da teče le na računalniku lastnika. |
| **Dodeli omrežno tipko** | Lokalno tipko poveže s poimenovanim vnosom, ki ga gostitelj lahko bere. |
| **Če igralec pritisne** | Pogoj (gostitelj): ali določen igralec drži poimenovani vnos? |
| **Nastavi hitrost sinhronizacije** | Prilagodi hitrost posnetkov gostitelja in zakasnitev interpolacije odjemalcev. |

Vse parametre najdete v [Popolni referenci dejanj](Full-Action-Reference-Network-Actions_sl).

---

## Dogodki (kategorija **Omrežje**)

Sprožijo se na vsakem primerku, katerega predmet jih obravnava, na vsakem
zadevnem računalniku:

| Dogodek | Sproži se, ko |
|---------|---------------|
| **Network Ready** | Odjemalec konča povezovanje z gostiteljem (gostitelj ga zase ne sproži). |
| **Player Joined** | Se poveže nov igralec. `global.network_sender` / `global.network_player_name` ga poimenujeta. |
| **Player Left** | Igralec prekine povezavo. |
| **Network Message** | Prispe **Pošlji omrežno sporočilo** — `global.network_event` / `global.network_data` / `global.network_sender`. |
| **Network Game Started** | Gostitelj pokliče **Začni omrežno igro**. |
| **Connection Lost** | Povezava odjemalca z gostiteljem pade. Igra teče naprej — izginejo le duhovi tega igralca. |

---

## Minimalen primer skupne sobe (stopnja A)

V nevidnem predmetu krmilnika sobe:

- **Create:** `Gosti igro`, če je to učiteljev računalnik, sicer `Pridruži se igri`
  z njegovim IP (ali `"auto"`).
- **Create:** `Nastavi skupno spremenljivko` `round = 1` (samo gostitelj, zaščiteno z
  `global.is_host == 1`).
- Kjerkoli: `draw_text`, ki prikazuje `global.round` — vsi igralci vidijo isto
  vrednost.

## Minimalen primer skupnih avatarjev (stopnja B)

V dogodku Create predmeta igralca:

- `Sinhroniziraj ta primerek` — ta primerek se zdaj podvaja.
- Na **gostitelju**: `Ustvari omrežni predmet` ustvari po en primerek igralca za
  vsakega igralca, ki se poveže (v obravnavi **Player Joined**), nato
  `Nastavi lastnika primerka` s številko tega igralca.
- Koda za gibanje, zaščitena z `Če upravljam ta primerek`, teče le na računalniku
  igralca lastnika; povsod drugje je primerek gladko interpoliran duh.

---

## Opombe in omejitve

- **TCP, samo LAN.** Brez prehoda čez NAT, brez igranja prek interneta — oba
  računalnika morata biti dosegljiva v istem lokalnem omrežju (učilniški Wi-Fi
  ali žična računalniška učilnica). Wi-Fi z izolacijo odjemalcev (običajen v
  upravljanih šolskih omrežjih) enako blokira odkrivanje in neposredno
  povezavo; najzanesljivejša je žična učilnica.
- **Vrati 45782 (TCP)** in **45783 (UDP, odkrivanje)** — pred uporabo v
  upravljanem omrežju vprašajte šolsko informatiko in ob prvem gostovanju
  pričakujte poziv požarnega zidu.
- Brskalniški odjemalec (izvoz HTML5) se poveže na vrata, ki so za ena višja od
  gostiteljevih, npr. `45783`, če gostitelj uporablja privzeta — to se zgodi
  samodejno.
- Izguba gostitelja je obravnavana mehko: odjemalčeva lastna igra teče naprej;
  izginejo le duhovi drugih igralcev, sproži pa se **Connection Lost**, da
  lahko prikažete sporočilo.
- Če je razširitev LAN Multiplayer **onemogočena**, ta dejanja in dogodki
  preprosto ne naredijo ničesar — glejte [Razširitve](Extensions_sl).

---

## Glejte tudi

- [File Exchange Multiplayer](FileExchange) (v angleščini) — potezni sorodnik
  za učilnico, kjer požarni zid blokira neposredne povezave te razširitve
- [Razširitve](Extensions_sl) — kako se LAN Multiplayer dobavlja in kako ga izklopiti
- [Popolna referenca dejanj](Full-Action-Reference-Network-Actions_sl) — vsako dejanje in parameter
- [Referenca dogodkov](Event-Reference_sl)
