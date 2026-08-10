# Izvoz iger

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Nazaj na začetno stran](Home_sl)

PyGameMaker lahko vašo igro izvozi na več platform. Ta vodnik zajema vsako možnost izvoza in kako jo uporabiti.

---

## Pregled izvoza

| Platforma | Format | Zahteve |
|-----------|--------|---------|
| **Windows** | .exe | PyInstaller |
| **macOS** | .app | PyInstaller (na Macu) |
| **HTML5** | .html | Sodoben brskalnik |
| **Linux** | Binarna datoteka | PyInstaller, Python 3.10+ |
| **Kivy / Android** | Izvorna koda / .apk | Buildozer |
| **Projekt (.zip)** | .zip | — (deljenje projekta, ki ga je mogoče urejati) |

> **Nič ni tiho zavrženo.** Če vaša igra uporablja dejanje, ki ga cilj ne more
> reproducirati (na primer, nekaterih dejanj izvoz Kivy/Android ne podpira), izvoz
> vseeno uspe, vendar vam pove, katera dejanja so bila **preskočena**, da lahko
> prilagodite. Če vaš projekt uporablja onemogočeno [razširitev](Extensions_sl)
> (npr. Pogled 3D), vas IDE opozori ob naložitvi.

---

## Izvoz Windows EXE

Ustvarite samostojno izvedljivo datoteko Windows, ki deluje brez nameščenega Pythona.

### Kako izvoziti

1. Odprite **Datoteka → Izvozi projekt…** (Ctrl+E) in izberite **Windows**
2. Izberite izhodno mapo
3. Počakajte, da se postopek gradnje zaključi
4. Poiščite datoteko .exe v izhodni mapi

### Kaj se ustvari

```
izhodna_mapa/
├── MojaIgra.exe      # Glavna izvedljiva datoteka
├── _internal/        # Potrebne knjižnice
└── assets/           # Viri igre
```

### Zahteve

- PyInstaller (nameščen prek `pip install pyinstaller`)
- Sistem Windows za gradnjo (navzkrižno prevajanje ni podprto)

### Distribucija

Za deljenje igre:
1. Celotno izhodno mapo stisnite v zip
2. Distribuirajte datoteko zip
3. Uporabniki jo razpakirajo in zaženejo .exe

### Odpravljanje težav

**Manjkajoče datoteke DLL:** Poskrbite, da so vključene vse odvisnosti. Preverite izhod PyInstaller glede opozoril.

**Opozorila protivirusnih programov:** Nekateri protivirusni programi označijo izvedljive datoteke PyInstaller. To je lažni pozitiven rezultat. Morda boste morali podpisati svojo izvedljivo datoteko.

---

## Izvoz aplikacije macOS

Ustvarite izvorni paket `.app` za macOS s PyInstaller.

### Kako izvoziti

1. Odprite **Datoteka → Izvozi projekt…** (Ctrl+E) in izberite **macOS**
2. Izberite izhodno mapo
3. Počakajte, da se gradnja zaključi
4. Poiščite `MojaIgra.app` v izhodni mapi

### Zahteve

- **Mac** za gradnjo (navzkrižno prevajanje iz Windows/Linux ni podprto)
- PyInstaller in Kivy, nameščena v Pythonu za gradnjo

### Distribucija

Paket `.app` stisnite v zip za deljenje. Nepodpisane aplikacije sprožijo Gatekeeper
na drugih Macih — uporabniki prvič z desnim klikom izberejo → **Odpri**, ali pa
aplikacijo podpišete/notarizirate z računom Apple Developer.

---

## Izvoz HTML5

Ustvarite eno samo datoteko HTML, ki deluje v spletnih brskalnikih.

### Kako izvoziti

1. Pojdite na **Datoteka → Izvozi kot HTML5…**
2. Izberite izhodno mesto
3. Izberite možnosti (kompresija itd.)
4. Kliknite Izvozi

### Kaj se ustvari

```
izhodna_mapa/
└── MojaIgra.html     # Igra v eni datoteki
```

### Značilnosti

- Deluje v katerem koli sodobnem brskalniku (Chrome, Firefox, Edge, Safari)
- Ne zahteva namestitve
- Stisnjeno z gzip za hitro nalaganje
- Primerno za mobilne naprave z dotikom

### Gostovanje vaše igre

Datoteko HTML naložite na:
- Svoj lasten spletni strežnik
- GitHub Pages (brezplačno)
- itch.io (gostovanje, usmerjeno v igre)
- Katero koli gostovanje statičnih datotek

### Združljivost brskalnikov

| Brskalnik | Podpora |
|-----------|---------|
| Chrome 80+ | Polna |
| Firefox 75+ | Polna |
| Edge 80+ | Polna |
| Safari 13+ | Polna |
| Mobilni Chrome | Polna |
| Mobilni Safari | Polna |

### Omejitve

- Nekatere funkcije morda ne delujejo (dostop do datotečnega sistema itd.)
- Zvok morda zahteva uporabnikovo interakcijo za zagon
- Zmogljivost je odvisna od naprave/brskalnika

---

## Izvoz Linux

Ustvarite izvorno izvedljivo datoteko Linux.

### Kako izvoziti

1. Odprite **Datoteka → Izvozi projekt…** (Ctrl+E) in izberite **Linux**
2. Izberite izhodno mapo
3. Počakajte na postopek gradnje

### Zahteve

- Sistem Linux za gradnjo
- Python 3.10+
- PyInstaller

### Distribucija

```bash
# Datoteko naredite izvedljivo
chmod +x MojaIgra

# Zaženite igro
./MojaIgra
```

Distribuirajte kot arhiv .tar.gz:
```bash
tar -czvf MojaIgra-linux.tar.gz MojaIgra/
```

---

## Izvoz Kivy (mobilno)

Ustvarite mobilne aplikacije za iOS in Android z ogrodjem Kivy.

### Kako izvoziti

1. Pojdite na **Datoteka → Izvozi v Kivy…**
2. Izberite izhodno mapo
3. Konfigurirajte mobilne nastavitve
4. Izvozite projekt Kivy

### Gradnja za Android

Izvoženi projekt Kivy uporablja Buildozer za ustvarjanje datotek APK:

```bash
cd izvozeni_projekt
pip install buildozer
buildozer init
buildozer android debug
```

### Gradnja za iOS

Zahteva Mac z Xcode:

```bash
cd izvozeni_projekt
pip install kivy-ios
toolchain build python3 kivy
toolchain create MojaIgra ~/ios_projekt
```

### Mobilni premisleki

- Dotikovni kontrolniki se preslikajo samodejno
- Spreminjanje velikosti zaslona se obravnava samodejno
- Testirajte na več velikostih zaslona
- Optimizirajte velikosti virov za mobilne naprave

---

## Izvoz projekta (.zip)

Delite sam **projekt, ki ga je mogoče urejati** (ne prevedene igre): uporabite
**Datoteka → Izvozi projekt…** (Ctrl+E), da ustvarite arhiv `.zip`, ki ga lahko nekdo
drug znova odpre v PyGameMakerju. Idealno za sodelovanje, varnostne kopije ali oddajo
šolskih nalog.

---

## Nastavitve izvoza

### Splošne nastavitve

| Nastavitev | Opis |
|------------|------|
| **Ime igre** | Ime, prikazano v naslovni vrstici/aplikaciji |
| **Ikona** | Ikona aplikacije (Windows/mobilno) |
| **Različica** | Številka različice (1.0.0) |
| **Avtor** | Ime razvijalca |

### Nastavitve Windows

| Nastavitev | Opis |
|------------|------|
| **Konzola** | Prikaži okno konzole (za razhroščevanje) |
| **Ena datoteka** | En sam .exe proti mapi z _internal |
| **UPX** | Stisni z UPX (manjša velikost) |

### Nastavitve HTML5

| Nastavitev | Opis |
|------------|------|
| **Kompresija** | Omogoči kompresijo gzip |
| **Celozaslonski način** | Zaženi v celozaslonskem načinu |
| **Dotikovni kontrolniki** | Prikaži zaslonske kontrolnike |

---

## Kontrolni seznam pred izvozom

Pred izvozom preverite:

- [ ] Vsi viri so vključeni v projekt
- [ ] Igra pravilno deluje v IDE
- [ ] Brez razhroščevalnih sporočil ali testne kode
- [ ] Vrstni red sob je pravilen (začetna soba prva)
- [ ] Zvočne datoteke so v podprtih formatih
- [ ] Spriti so optimizirani glede na velikost datoteke

---

## Optimiziranje velikosti datotek

### Spriti
- Uporabite ustrezne dimenzije (ne prevelike)
- Stisnite datoteke PNG
- Razmislite o JPEG za slike brez prosojnosti

### Zvok
- Za glasbo uporabite OGG/MP3 (ne WAV)
- Zvočne učinke ohranite kratke
- Nižje frekvence vzorčenja za preproste zvoke

### Splošno
- Odstranite neuporabljene vire
- Zmanjšajte velikosti sob
- Testirajte na ciljnih platformah

---

## Testiranje izvozov

Vedno testirajte svojo izvoženo igro:

1. **Windows:** Testirajte na čistem računalniku brez Pythona
2. **HTML5:** Testirajte v več brskalnikih
3. **Linux:** Če je mogoče, testirajte na različnih distribucijah
4. **Mobilno:** Testirajte na resničnih napravah, ne le v emulatorjih

---

## Distribucijske platforme

### itch.io
- Brezplačno gostovanje za neodvisne igre
- Podpira HTML5, Windows, Linux, Mac
- Vgrajen plačilni sistem

### Steam
- Zahteva integracijo Steamworks SDK
- Uporabite PyInstaller s Steam API
- Plačljiva pristojbina za objavo

### Google Play (Android)
- Zahteva razvijalski račun (25 $)
- Zgradite podpisan APK z Buildozer
- Upoštevajte smernice glede vsebine

### App Store (iOS)
- Zahteva račun Apple Developer (99 $/leto)
- Zgradite s kivy-ios
- Oddajte prek App Store Connect

---

## Naslednji koraki

- [[Zacetek_sl]] - Ponovitev osnov
- [[Troubleshooting_sl|Odpravljanje Težav]] - Napake manjkajočih odvisnosti in druge težave z izvozom
- [[FAQ_sl]] - Pogosta vprašanja o izvozu
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Prijava težav z izvozom
