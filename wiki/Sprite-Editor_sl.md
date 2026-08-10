# Urejevalnik Sprite-ov

> [English](Sprite-Editor) | [Français](Sprite-Editor_fr) | [Deutsch](Sprite-Editor_de) | [Italiano](Sprite-Editor_it) | [Español](Sprite-Editor_es) | [Português](Sprite-Editor_pt) | [Русский](Sprite-Editor_ru) | [Slovenščina](Sprite-Editor_sl) | [Українська](Sprite-Editor_uk)

---

> [Nazaj na Domov](Home_sl)

Sprite-i so slike in animacije, pripete na objekte. Urejevalnik
Sprite-ov je vgrajeno orodje za piksel umetnost — rišite sprite-e
neposredno v PyGameMaker, brez zunanjega urejevalnika slik.

---

## Odpiranje Urejevalnika Sprite-ov

1. Dvokliknite na obstoječi sprite v drevesu virov, ali
2. Desni klik na **Sprites** > **Ustvari Sprite**

![Urejevalnik Sprite-ov: orodja za risanje in velikost čopiča na levi,
spodaj izbirnik izhodišča in možnost Precise Collision, paleta barv,
platno na sredini s prikazom lika v piksel umetnosti pri 10x povečavi,
in trak sličic spodaj (8 sličic, gumb Play, dodajanje/podvajanje/
brisanje sličice)](images/sprite-editor.png)

---

## Orodja za Risanje

| Orodje | Bližnjica | Kaj naredi |
|------|----------|---------------|
| **Svinčnik** | P | Riše posamezne piksle |
| **Radirka** | E | Briše piksle (v prosojnost) |
| **Kapalka** | I | Prevzame barvo s platna |
| **Zapolnitev** | G | Zapolni povezano območje (vedro barve) |
| **Črta** | L | Nariše ravno črto |
| **Pravokotnik** | R | Nariše pravokotnik (preklop **Filled** za polno/obris) |
| **Elipsa** | O | Nariše elipso (upošteva tudi **Filled**) |
| **Izbira** | S | Pravokotna izbira — premikanje, kopiranje, izrezovanje, lepljenje ali brisanje izbranih pikslov |

**Velikost čopiča** velja za Svinčnik, Radirko in obrise črt/oblik.
Paleta barv vsebuje delovni nabor barv plus standardno hitro paleto 12
barv; kliknite na vzorec za izbiro, ali uporabite Kapalko za prevzem
barve neposredno s sprite-a.

---

## Operacije na Platnu

- **Mirror H / Mirror V** — zrcali trenutno sličico vodoravno ali navpično
- **Resize** — odpre pogovorno okno z dvema različnima načinoma:
  - **Scale Image** — raztegne obstoječo vsebino na novo velikost
  - **Resize Canvas** — ohrani vsebino v izvirni velikosti in doda/obreže prostor okoli, zasidran na kot, rob ali sredino po izbiri
- **Grid** — vklopi/izklopi prekrivanje pikselne mreže (ne vpliva na shranjeno sliko)
- **Zoom In / Zoom Out** — platno pogosto deluje pri 10x povečavi ali več, saj so sprite-i običajno majhni (16×16 do 64×64 je pogosto)
- **Export PNG…** — shrani trenutno sličico kot samostojno datoteko `.png`
- Desni klik na platno za **Copy / Cut / Paste / Delete / Deselect / Select All** (standardne bližnjice: Ctrl+C / Ctrl+X / Ctrl+V / Del / Esc)

---

## Sličice in Animacija

Sprite lahko vsebuje več sličic, predvajanih kot animacija med izvajanjem
igre. Trak sličic na dnu urejevalnika:

| Kontrola | Učinek |
|---------|--------|
| **+** | Doda novo prazno sličico |
| **D** | Podvoji trenutno sličico |
| **-** | Izbriše trenutno sličico |
| **Play** | Predogled animacije v urejevalniku pri hitrosti sličic sprite-a |

Kliknite na sličico za predogled, da skočite nanjo in rišete posebej na tej sličici.

---

## Izhodišče in Kolizija

- **Origin (izhodišče)** — točka, ki jo objekti, ki uporabljajo ta
  sprite, obravnavajo kot svojo pozicijo `(x, y)`. Prednastavitve:
  Top-Left, Top-Center, Center, Center-Bottom, Bottom-Left, Bottom-Right,
  ali **Custom** (natančna X/Y). Večina platformskih/pogledov od zgoraj
  likov uporablja **Center-Bottom**, da so noge sprite-a na Y-poziciji
  objekta.
- **Precise Collision** — ko je omogočena, kolizije s tem sprite-om
  testirajo dejanske neprosojne piksle namesto omejitvenega okvira
  sprite-a. Natančnejše za nepravilno oblikovane sprite-e, dražje za
  izračun — pustite izklopljeno za preproste oblike (zidovi, kovanci) in
  jo pridržite za sprite-e, kjer bi kolizija po omejitvenem okviru
  izgledala vidno napačna.

---

## Naslednji Koraki

- [[Urejevalnik_Objektov_sl|Urejevalnik Objektov]] - Pripnite sprite na igralni objekt
- [[Urejevalnik_Sob_sl|Urejevalnik Sob]] - Postavite instance objektov, ki uporabljajo vaš sprite
- [[Prva_Igra_sl|Ustvarite Svojo Prvo Igro]] - Celoten vodič, ki se začne z risanjem sprite-ov
