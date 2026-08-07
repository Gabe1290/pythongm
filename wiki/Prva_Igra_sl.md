# Ustvarite Svojo Prvo Igro

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Nazaj na začetno stran](Home_sl)

V tem vodiču bomo ustvarili preprosto igro "Ujemi Zvezde", v kateri se igralec premika, da zbira zvezde, ki padajo.

---

## Kaj Se Boste Naučili

- Ustvarjanje sprite-ov
- Ustvarjanje objektov z dogodki in akcijami
- Uporabo urejevalnika sob
- Zagon in testiranje svoje igre

---

## Korak 1: Ustvarite Nov Projekt

1. Zaženite PyGameMaker
2. Pojdite na **File > New Project**
3. Poimenujte svoj projekt "CatchTheStars"
4. Kliknite **Create**

---

## Korak 2: Ustvarite Sprite Igralca

1. Desno kliknite na **Sprites** v drevesu virov
2. Izberite **Create Sprite**
3. Poimenujte ga `spr_player`
4. Kliknite **Edit Sprite**, da odprete urejevalnik sprite-ov
5. Narišite preprost lik (ali uporabite barvni pravokotnik 32x32)
6. Kliknite **Save**

---

## Korak 3: Ustvarite Sprite Zvezde

1. Desno kliknite na **Sprites** > **Create Sprite**
2. Poimenujte ga `spr_star`
3. Narišite obliko zvezde (ali uporabite rumen krog)
4. Kliknite **Save**

---

## Korak 4: Ustvarite Objekt Igralec

1. Desno kliknite na **Objects** v drevesu virov
2. Izberite **Create Object**
3. Poimenujte ga `obj_player`
4. Nastavite **Sprite** na `spr_player`

### Dodajte Dogodke Tipkovnice

**Puščica Levo:**
1. Kliknite **Add Event** > **Keyboard** > **Left**
2. Dodajte akcijo: **Set Horizontal Speed** z vrednostjo `-4`

**Puščica Desno:**
1. Kliknite **Add Event** > **Keyboard** > **Right**
2. Dodajte akcijo: **Set Horizontal Speed** z vrednostjo `4`

**Nobena Tipka Pritisnjena:**
1. Kliknite **Add Event** > **Keyboard** > **No Key**
2. Dodajte akcijo: **Set Horizontal Speed** z vrednostjo `0`

---

## Korak 5: Ustvarite Objekt Zvezda

1. Desno kliknite na **Objects** > **Create Object**
2. Poimenujte ga `obj_star`
3. Nastavite **Sprite** na `spr_star`

### Dodajte Dogodek Create
1. Kliknite **Add Event** > **Create**
2. Dodajte akcijo: **Set Vertical Speed** z vrednostjo `3`
3. Dodajte akcijo: **Jump To Position** z X `irandom(600)`, Y `20` —
   `irandom(n)` izbere naključno celo število od 0 do `n`, kar
   razprši zvezdo na naključno mesto blizu vrha sobe širine 640
   pikslov ob vsakem (ponovnem) pojavu

### Dodajte Dogodek Outside Room
1. Kliknite **Add Event** > **Other** > **Outside Room**
2. Dodajte akcijo: **Jump to Start Position**
3. Dodajte akcijo: **Set Score** z vrednostjo `1` in označenim **Relative**

### Dodajte Trk z Igralcem
1. Kliknite **Add Event** > **Collision** > izberite `obj_player`
2. Dodajte akcijo: **Set Score** z vrednostjo `10` in označenim **Relative**
3. Dodajte akcijo: **Play Sound** (neobvezno, če imate zvok)
4. Dodajte akcijo: **Jump to Random Position**

---

## Korak 6: Ustvarite Sobo

1. Desno kliknite na **Rooms** v drevesu virov
2. Izberite **Create Room**
3. Poimenujte jo `room_game`
4. Nastavite velikost sobe na **640 x 480**

### Postavite Objekte
1. Izberite zavihek **Objects** v urejevalniku sob
2. Kliknite na `obj_player` in ga postavite na sredino spodaj v sobi
3. Kliknite na `obj_star` in postavite 5 do 10 zvezd razporejenih na vrhu

---

## Korak 7: Prikažite Rezultat

1. Odprite `obj_player`
2. Kliknite **Add Event** > **Draw**
3. Dodajte akcijo: **Draw Score** na položaju (10, 10)

---

## Korak 8: Zaženite Svojo Igro!

1. Pritisnite **F5** ali pojdite na **Build > Test Game**
2. Uporabite levo in desno puščično tipko za premikanje
3. Ujemite zvezde, ki padajo, da povečate svoj rezultat!

---

## Izboljšave za Preizkus

### Dodajte Življenja
1. Ustvarite objekt "game over", ki se pojavi, ko življenja dosežejo 0
2. Dodajte dogodek trka s "slabim" objektom, ki zmanjša življenja

### Dodajte Nivoje
1. Ustvarite več sob
2. Uporabite akcijo **Next Room**, ko rezultat doseže prag

### Dodajte Zvok
1. Uvozite zvočne datoteke v vir Sounds
2. Dodajte akcije **Play Sound** dogodkom

### Uporabite Vizualno Programiranje
1. Odprite objekt
2. Kliknite na zavihek **Blockly** za programiranje s povleci-in-spusti
3. Zgradite isto logiko vizualno z bloki

---

## Popolna Struktura Projekta

Po zaključku tega vodiča bi moral vaš projekt vsebovati:

- **Sprite-i:** spr_player, spr_star
- **Objekti:** obj_player, obj_star
- **Sobe:** room_game

---

## Naslednji Koraki

- [[Urejevalnik_Objektov_sl]] - Naučite se več o lastnostih objektov
- [[Dogodki_in_Akcije_sl]] - Raziščite vse razpoložljive dogodke in akcije
- [[Vizualno_Programiranje_sl]] - Preizkusite gradnjo z bloki Blockly
- [[Izvoz_Iger_sl]] - Delite svojo igro z drugimi
