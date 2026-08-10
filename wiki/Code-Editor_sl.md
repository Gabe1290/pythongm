# Urejevalnik Kode

> [English](Code-Editor) | [Français](Code-Editor_fr) | [Deutsch](Code-Editor_de) | [Italiano](Code-Editor_it) | [Español](Code-Editor_es) | [Português](Code-Editor_pt) | [Русский](Code-Editor_ru) | [Slovenščina](Code-Editor_sl)

---

> [Nazaj na Domov](Home_sl)

Vsak objekt v PyGameMaker ima zavihek **Urejevalnik Kode** poleg Event
List in Blockly — tretji način za delo z istimi dogodki in akcijami,
tokrat kot pravi Python. Ni izvoz v eno smer: koda, ki jo napišete tukaj,
se ponovno analizira nazaj v strukturirane dogodke in akcije, zato ostane
usklajena z drugima dvema pogledoma.

---

## Odpiranje Urejevalnika Kode

1. Odprite objekt v Urejevalniku Objektov
2. Kliknite zavihek **💻 Urejevalnik Kode**

![Urejevalnik Kode v načinu "Prikaži Generirano Kodo": razred z eno
metodo na dogodek (on_create, on_step,
on_collision_obj_power, ...), ki prikazuje pravi Python, v katerega se
prevedejo vaši vizualni dogodki in akcije](images/code-editor.png)

---

## Dva Načina

Spustni meni na vrhu preklaplja med njima:

### 📖 Prikaži Generirano Kodo

Samo za branje. Prikazuje Python, v katerega se prevedejo trenutni
dogodki in akcije vašega objekta — ena metoda na dogodek (`on_create`,
`on_step`, `on_collision_obj_enemy`, ...), ki kliče `self.*` in `game.*`
natanko tako, kot to počne izvajalno okolje. Akcija, za katero generator
nima čistega Python ekvivalenta, se še vedno prikaže, označena s
komentarjem (`# Unknown action: ...`) nad vrstico, ki jo je proizvedla —
nič ni skrito, tudi v mejnih primerih ne. Kliknite **🔄 Osveži** za
ponovno generiranje po spremembi dogodkov drugje.

### ✏️ Uredi Lastno Kodo

Uredljivo, z označevanjem Python skladnje. Začnite tipkati (ali uredite
začetno kodo, podedovano iz načina Prikaži) in PyGameMaker analizira vaš
razred približno 1,5 sekunde po tem, ko nehate tipkati — statusna
oznaka poleg orodne vrstice medtem prikazuje **idle / busy / error /
empty**. Po uspešni analizi vaše metode **nadomestijo** dogodke in
akcije objekta (brez združevanja) — katerekoli metode dogodkov vaša koda
definira, postanejo seznam dogodkov tega objekta, takoj vidne tudi v
zavihkih Event List in Blockly.

Če analiza spodleti (skladenjska napaka, ali koda, ki je analizator ne
more pretvoriti nazaj v dogodke), statusna oznaka prikaže napako in nič
se ne uveljavi — dogodki vašega objekta ostanejo takšni, kot so bili,
dokler se koda ne analizira uspešno.

---

## Zakaj ga Uporabljati

- **Hitrost** — nekatero logiko (izračun z več vejami, zanko, enkratno
  formulo) je hitreje natipkati, kot sestaviti iz blokov ali seznama
  akcij.
- **Most za učenje** — preklopite dogodke objekta, ki ga je zgradil
  začetnik, v način Prikaži, da vidite pravi ekvivalent v kodi, naraven
  naslednji korak za učenca, ki prehaja iz vizualnega programiranja v
  Python.
- **Natančnost** — vse, kar se izrazi kot preprosta Python metoda na
  objektu, deluje, ne da bi čakali, da obstaja ustrezna vizualna akcija.

To je isti temeljni mehanizem kot akcija **Izvedi Kodo**, dostopna iz
seznama akcij / Blockly (kategorija *Control*) — zavihek Urejevalnik
Kode preprosto deluje na ravni celotnega objekta namesto ene same akcije.

---

## Naslednji Koraki

- [[Urejevalnik_Objektov_sl|Urejevalnik Objektov]] - Kje se nahaja zavihek Urejevalnik Kode
- [[Vizualno_Programiranje_sl|Vizualno Programiranje]] - Pogled Blockly istih dogodkov
- [[Dogodki_in_Akcije_sl|Dogodki in Akcije]] - Kaj dejansko naredi vsaka akcija
