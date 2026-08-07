# Začetek

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

[Nazaj na začetno stran](Home_sl)

Ta vodič vam bo pomagal, da PyGameMaker zaženete na svojem sistemu.

---

## Sistemske Zahteve

- **Python** 3.10 ali novejši
- **Operacijski Sistem:** Windows, Linux ali macOS
- **Prostor na Disku:** ~500 MB za namestitev
- **RAM:** najmanj 4 GB, priporočeno 8 GB

---

## Namestitev

### Korak 1: Namestite Python

Prenesite Python 3.10+ s [python.org](https://www.python.org/downloads/) in ga namestite. Pri namestitvi na Windows poskrbite, da označite "Add Python to PATH".

### Korak 2: Klonirajte Repozitorij

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Ali prenesite datoteko ZIP s [strani Releases](https://github.com/Gabe1290/pythongm/releases).

### Korak 3: Ustvarite Virtualno Okolje

Ustvarjanje virtualnega okolja loči odvisnosti PyGameMaker:

```bash
python -m venv venv
```

Aktivirajte virtualno okolje:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Korak 4: Namestite Odvisnosti

```bash
pip install -r requirements.txt
```

### Korak 5: Zaženite PyGameMaker

```bash
python main.py
```

---

## Prvi Zagon

Ob prvem zagonu PyGameMaker boste videli:

1. **Menijsko Vrstico** — menije File, Edit, Assets, Build, Tools in Help
2. **Drevo Virov** — levi panel s prikazom virov projekta (Sprite-i, Zvoki, Ozadja, Objekti, Sobe)
3. **Delovno Področje** — osrednje področje za urejanje virov
4. **Panel Lastnosti** — desni panel za lastnosti virov

---

## Ustvarite Svoj Prvi Projekt

1. Pojdite na **File > New Project**
2. Izberite lokacijo in ime za svoj projekt
3. Ustvarjena bo nova mapa projekta s standardno strukturo

---

## Struktura Projekta

Vsak projekt PyGameMaker vsebuje:

```
moj_projekt/
├── project.json      # Nastavitve projekta
├── sprites/          # Slike spritov
├── sounds/           # Zvočne datoteke
├── backgrounds/      # Slike ozadij
├── objects/          # Definicije igralnih objektov
├── rooms/            # Postavitve nivojev
├── fonts/            # Datoteke pisav
├── scripts/          # Prilagojene skripte
└── data/             # Prilagojene podatkovne datoteke
```

---

## Menjava Jezika

PyGameMaker podpira več jezikov:

1. Pojdite na **Tools > Language**
2. Izberite želeni jezik v meniju
3. Ponovno zaženite PyGameMaker, da uveljavite spremembo

Razpoložljivi jeziki: angleščina, francoščina, nemščina, italijanščina, španščina, portugalščina, slovenščina, ukrajinščina, ruščina

---

## Naslednji Koraki

- [[Prva_Igra_sl]] - Zgradite preprosto igro korak za korakom
- [[Urejevalnik_Objektov_sl]] - Naučite se ustvarjati igralne objekte
- [[Urejevalnik_Sob_sl]] - Oblikujte svoje igralne nivoje
- [[Dogodki_in_Akcije_sl]] - Razumite igralno logiko

---

## Odpravljanje Težav

### Python ni najden
Prepričajte se, da je Python nameščen in dodan v PATH. Za preverjanje poskusite zagnati `python --version`.

### Manjkajoče odvisnosti
Če dobite napake pri uvozu, poskusite ponovno namestiti odvisnosti:
```bash
pip install -r requirements.txt --force-reinstall
```

### Težave s prikazom
Na Linuxu Qt (ogrodje GUI, na katerem je zgrajen PyGameMaker) potrebuje
nekaj sistemskih knjižnic, ki jih `pip` ne namesti:
```bash
sudo apt-get install -y libegl1 libxkbcommon0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libasound2-dev libgl1-mesa-dev
```

---

## Pomoč

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Prijavite napake ali predlagajte funkcije
- [[FAQ_sl]] - Pogosta vprašanja in odgovori
