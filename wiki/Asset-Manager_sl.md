# Upravitelj Virov

> [English](Asset-Manager) | [Français](Asset-Manager_fr) | [Deutsch](Asset-Manager_de) | [Italiano](Asset-Manager_it) | [Español](Asset-Manager_es) | [Português](Asset-Manager_pt) | [Русский](Asset-Manager_ru) | [Slovenščina](Asset-Manager_sl) | [Українська](Asset-Manager_uk)

---

> [Nazaj na Domov](Home_sl)

Poleg vsakodnevnega ustvarjanja/preimenovanja/brisanja v drevesu virov
PyGameMaker sledi, **kje se posamezen vir dejansko uporablja**, ohranja
izbrisane vire obnovljive namesto da bi jih izgubili za vedno, in lahko
najde tako neuporabljene vire kot osirotele datoteke, ki zasedajo mapo
projekta. Vse to živi v meniju **Orodja**.

---

## Filtriranje Drevesa Virov

Vtipkajte v filtrsko polje nad drevesom virov, da ga med tipkanjem
zožite na ujemajoča imena. Ujemanje ne razlikuje velikih/malih črk in
deluje na surovem imenu vira; kategorija (Sprites, Objects, ...) se
skrije, ko so vsi njeni podrejeni elementi filtrirani, in se ponovno
prikaže, ko se en spet ujema.

---

## Sledenje Uporabe

Vsako brisanje vira zdaj preveri, kje je ta vir dejansko referenciran —
drugi objekti, sobe, akcije — preden potrdite. Če `spr_player` uporablja
3 objekti, potrditev brisanja to navede namesto splošnega opozorila,
tako da to izveste *pred* brisanjem nečesa, kar bi pokvarilo druge dele
projekta, ne po tem.

**Znana omejitev:** ta analiza vidi samo tisto, kar lahko vidijo lastne
podatkovne strukture PyGameMaker — parametri akcij, cilji kolizij,
instance sob, polja sprite/parent. Ime vira, uporabljeno samo znotraj
surovega Python niza v [[Code-Editor_sl|Urejevalniku Kode]] ali akciji
Izvedi Kodo (na primer `game.sounds['explosion'].play()`), ni vidno tej
analizi.

---

## Obnavljanje Izbrisanih Virov (Koš)

**Orodja > Obnovi Izbrisane Vire...**

Brisanje vira ga ne izbriše takoj — njegove datoteke se premaknejo v Koš,
lokalen za projekt, PyGameMaker pa vodi evidenco o tem, kaj je bilo
izbrisano, kam so šle njegove datoteke, in katere navzkrižne reference so
bile počiščene (na primer, polje sprite objekta, ki se izprazni, ker je
bil sprite, na katerega je kazalo, izbrisan). To pogovorno okno prikaže
vse, kar je trenutno v Košu, s tremi dejanji:

| Dejanje | Učinek |
|--------|--------|
| **Obnovi** | Vrne vir natanko takšen, kot je bil. Zavrne prepisovanje, če zdaj obstaja nov vir z istim imenom — obnovitev prav tako ni destruktivna. |
| **Trajno Izbriši** | Odstrani en vnos koša za vedno |
| **Izprazni Koš** | Odstrani vse, kar je trenutno v Košu |

Navzkrižne reference, počiščene ob brisanju, se pri obnovitvi **ne**
ponovno samodejno povežejo — videli boste, kaj se je spremenilo, tako da
se lahko sami odločite, ali jih želite ponovno povezati, namesto da bi
PyGameMaker ugibal.

Datoteke v košu so izključene iz izvozov projekta (zip/HTML5/itd.) —
izbrisan vir se nikoli tiho ne pojavi v objavljeni igri.

---

## Iskanje Neuporabljenih Virov

**Orodja > Najdi Neuporabljene Vire...**

Analizira celoten projekt z isto analizo uporabe kot zgoraj in navede
vsak vir brez kakršne koli reference, razvrščen po kategorijah, vsak s
potrditvenim poljem. Izberite tiste, ki jih res želite odstraniti (ali
**Izberi Vse**) in **Premakni Izbrano v Koš** — ista varnostna mreža kot
pri vsakem drugem brisanju.

**S sobami ravnajo previdno.** Soba, do katere se nihče izrecno ne
navigira po imenu — igra z eno sobo, ali čisto prva soba igre — se
legitimno prikaže kot "neuporabljena" pod preprostim štetjem referenc,
vendar bi njeno brisanje pokvarilo igro. Sobe so označene kot *"Sobe —
brez izrecne navigacije"*, namesto preprosto "neuporabljene", in
**Izberi Vse namerno preskoči sobe**; posamezno lahko vseeno označite
eno, če ste prepričani.

---

## Iskanje Osirotelih Datotek

**Orodja > Najdi Osirotele Datoteke...**

Obraten problem: datoteke v mapi projekta (`sprites/`, `sounds/`,
`backgrounds/`, `fonts/`, `thumbnails/`), ki nimajo **nobenega**
ustreznega vnosa v projektu — puščene po prekinjeni operaciji, ali ročno
postavljene zunaj IDE. Navede jih po kategorijah z istim vzorcem
potrditveno polje / Izberi Vse / **Premakni Izbrano v Koš** kot
neuporabljene vire, in vključuje lasten mini-panel Koša (Obnovi / Trajno
Izbriši / Izprazni) v istem pogovornem oknu — osirotele datoteke
uporabljajo ločeno shrambo koša od običajnih brisanj virov, saj sploh
niso bile pravi vnos project.json.

---

## Počisti Projekt

**Orodja > Počisti Projekt**

Čiščenje preostalih datotek `.tmp` z enim klikom — začasnih spremljevalnih
datotek, ki jih ustvari PyGameMakerjev atomski postopek shranjevanja in
jih običajno sam odstrani. Dotaknejo se samo datoteke, starejše od
približno minute, tako da trenutno shranjevanje nikoli ni ogroženo.
Poroča, koliko datotek je bilo odstranjenih, ali da ni bilo ničesar za
počistiti. Za razliko od zgornjih pogovornih oken te datoteke nikoli ne
gredo skozi sistem virov ali Koš — datoteka `.tmp` nikoli ni verodostojna
kopija ničesar, zato se izbriše neposredno.

---

## Naslednji Koraki

- [[Urejevalnik_Sob_sl|Urejevalnik Sob]] / [[Urejevalnik_Objektov_sl|Urejevalnik Objektov]] - Od kod prihaja večina referenc virov
- [[FAQ_sl|FAQ]] - Pogosta vprašanja, vključno z varnostjo podatkov
