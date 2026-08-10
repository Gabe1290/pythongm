# Odpravljanje Težav

> [English](Troubleshooting) | [Français](Troubleshooting_fr) | [Deutsch](Troubleshooting_de) | [Italiano](Troubleshooting_it) | [Español](Troubleshooting_es) | [Português](Troubleshooting_pt) | [Русский](Troubleshooting_ru) | [Slovenščina](Troubleshooting_sl) | [Українська](Troubleshooting_uk)

---

> [Nazaj na Domov](Home_sl)

Pogoste težave in kje jih iskati. Za težave, specifične za namestitev
(Python ni najden, manjkajoče odvisnosti, knjižnice za prikaz Linux),
najprej glejte razdelek Odpravljanje Težav v
[[Zacetek_sl|Kako Začeti]] — ta stran pokriva težave, ki se pojavijo, ko
PyGameMaker že teče.

---

## Moja igra se sesuje ali se takoj zapre, ko pritisnem Testiraj Igro (F5)

**Zaženite IDE iz terminala, ne prek bližnjice na namizju, da vidite
napako.** Sled sesutega podprocesa testne igre se zabeleži v izhod
konzole samega IDE (`python main.py` v terminalu) — če ste IDE zagnali
brez vidne konzole (na primer bližnjica Windows), se to sporočilo nima
kje prikazati. Znova zaženite iz terminala in ponovite sesutje, da
vidite pravo Python sled.

Pogosti vzroki:
- Akcija **Izvedi Kodo** ali lastna koda v Urejevalniku Kode s
  skladenjsko napako ali tipkarsko napako v klicu `game.*`/`self.*`
- Akcija kolizije ali primerjave, ki se sklicuje na objekt, ki je bil
  medtem preimenovan ali izbrisan

---

## IDE sam se je sesul, ko sem poskusil odpreti urejevalnik

Preverite **`~/pygamemaker_crash.log`** (v vaši domači mapi) — sesutja
urejevalnika objektov/sob/sprite-ov se zapisujejo tja posebej, da
ostanejo vidna tudi, ko je bil IDE zagnan brez konzolnega okna. Priložite
ustrezen del te datoteke, če prijavite napako.

---

## Izvoz pravi "X ni najden" / manjka odvisnost

Namizni in mobilni izvozi (Windows .exe, macOS .app, binarna datoteka
Linux, Kivy/Android/iOS) vključujejo izvajalno okolje prek PyInstaller
ali Buildozer, in ta orodja morajo biti nameščena v **istem Pythonu, ki
poganja IDE** — sistemska namestitev drugje na računalniku se ne šteje.
Sporočilo o napaki v pogovornem oknu izvoza poda natančno rešitev, na
kratko pa:

- **Skrbniške pravice niso potrebne.** Aktivirajte svoje virtualno okolje
  in zaženite `pip install <paket>`, ali namestite v svoj račun z
  `pip install --user <paket>` — oba delujeta brez skrbniških pravic.
- Namestitev vsega naenkrat: `pip install -r requirements.txt`
- **Ne želite nobene namestitve?** Namesto tega uporabite izvoz **HTML5
  (Spletni Brskalnik)** — ne zahteva ničesar nameščenega lokalno,
  rezultat pa deluje v katerem koli brskalniku. (Upoštevajte, da to velja
  le za *izdelavo* izvoza — dokončan `.exe`/`.app` ne zahteva ničesar
  nameščenega na računalniku, ki ga samo *poganja*.)

---

## Prejel sem opozorilo pred Izvozom ("X uporablja Y, vendar ni Z")

Izvoz najprej izvede validacijo projekta in prikaže vse, kar najde,
preden se prikaže pogovorno okno Izvoz — na primer objekt, ki uporablja
**Naslednjo Sobo** v projektu z eno samo sobo, kar ne bi imelo nobenega
učinka. To so **opozorila, ne napake**: kliknite OK in izvoz se
nadaljuje; kažejo na logiko, ki verjetno ne bo naredila tega, kar
pričakujete, ne da bi vas ovirala pri objavi.

---

## Sprite prikazuje rdečo značko "(ni uvožen)" v drevesu virov

To pomeni, da slikovna datoteka sprite-a manjka na disku (običajno ker
je bil projekt kopiran ali deljen brez mape `sprites/`). To je zgolj
informativno — izvajanje in izvoz to ignorirata — in **se samodejno
popravi ob naslednjem shranjevanju**, ko je datoteka dejansko spet
prisotna. Ročno popravilo ni potrebno, razen zagotovitve, da je slikovna
datoteka tam, kjer jo sprite pričakuje.

---

## Nekaj drugega ne deluje

- Oglejte si [[FAQ_sl|FAQ]] za pogosta vprašanja
- Prijavite napake na [Sledilniku Težav GitHub](https://github.com/Gabe1290/pythongm/issues) — navedite svoj OS, različico Python, in (če je relevantno) izhod konzole ali `~/pygamemaker_crash.log`

---

## Naslednji Koraki

- [[Zacetek_sl|Kako Začeti]] - Odpravljanje težav pri namestitvi
- [[Izvoz_Iger_sl|Izvoz Iger]] - Popolna referenca izvoza
- [[FAQ_sl|FAQ]] - Pogosta vprašanja
