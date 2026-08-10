# Urejevalnik Sob

> [English](Room-Editor) | [Français](Editeur_Salles_fr) | [Deutsch](Raum_Editor_de) | [Italiano](Editor_Stanze_it) | [Español](Editor_Salas_es) | [Português](Editor_Salas_pt) | [Slovenščina](Urejevalnik_Sob_sl) | [Українська](Redaktor_Kimnat_uk) | [Русский](Redaktor_Komnat_ru)

---

[Nazaj na začetno stran](Home_sl)

Sobe so nivoji, zasloni ali prizori vaše igre. Urejevalnik Sob vam
omogoča oblikovanje teh prostorov s postavljanjem objektov in
nastavljanjem ozadij.

---

## Odpiranje Urejevalnika Sob

1. Dvokliknite na obstoječo sobo v drevesu virov, ali
2. Desno kliknite na **Rooms** > **Create Room**

![Urejevalnik Sob: paleta objektov na levi za izbiro, kaj postaviti,
območje sobe na sredini z zapolnjenim platformskim nivojem (orodja
mreže, lepljenja in izbire v orodni vrstici zgoraj), ter lastnosti
sobe/instance in miniaturni predogled na desni](images/room-editor.png)

---

## Lastnosti Sobe

| Lastnost | Opis |
|-----------|-------------|
| **Name** | Edinstven identifikator (npr. `room_nivo1`) |
| **Width** | Širina sobe v pikslih |
| **Height** | Višina sobe v pikslih |
| **Speed** | Hitrost igre v sličicah na sekundo (privzeto: 60) |
| **Persistent** | Ohrani stanje sobe ob izstopu/ponovnem vstopu |

### Konvencija Poimenovanja

Uporabite predpono `room_` za sobe:
- `room_menu`
- `room_nivo1`
- `room_game_over`

---

## Postavljanje Objektov

### Dodajanje Instanc

1. Izberite objekt v panelu **Objects**
2. Kliknite v pogled sobe, da postavite instanco
3. Kliknite in vlecite, da postavite več instanc

### Izbiranje Instanc

- Kliknite na instanco, da jo izberete
- Držite **Ctrl** in kliknite, da izberete več
- Narišite pravokotnik, da izberete vse instance znotraj njega

### Premikanje Instanc

- Vlecite izbrane instance z miško
- Uporabite puščične tipke za natančno premikanje

### Brisanje Instanc

- Izberite instance in pritisnite **Delete**, ali
- Desno kliknite in izberite "Izbriši"

---

## Nastavitve Mreže

Aktivirajte mrežo za natančno postavljanje:

1. Pojdite na **View > Show Grid**
2. Nastavite velikost mreže (npr. 32x32)
3. Aktivirajte "Snap to Grid"

Pogoste velikosti mreže:
- **16x16** - Majhne ploščice
- **32x32** - Standardne ploščice
- **64x64** - Velike ploščice

---

## Ozadja

### Nastavitev Ozadja

1. Kliknite na zavihek **Backgrounds**
2. Izberite vir ozadja
3. Konfigurirajte možnosti prikaza

### Možnosti Ozadja

| Možnost | Opis |
|--------|-------------|
| **Visible** | Prikaže/skrije ozadje |
| **Foreground** | Nariše pred objekti |
| **Tile Horizontal** | Ponovi vodoravno |
| **Tile Vertical** | Ponovi navpično |
| **Stretch** | Raztegne, da zapolni sobo |
| **Horizontal Speed** | Hitrost drsenja (parallax) |
| **Vertical Speed** | Hitrost drsenja (parallax) |

### Plasti Ozadja

Soba podpira do **8 plasti ozadja**, vsaka s svojo hitrostjo drsenja
za učinke parallax. Primer razporeditve:
- Plast 0: Nebo (najbolj v ozadju)
- Plast 1: Gore (počasnejše drsenje)
- Plast 2: Drevesa (srednje drsenje)
- Plast 3: Tla (brez drsenja)

---

## Views (Kamera)

Views nadzorujejo, kateri del sobe je viden na zaslonu. Na sobo je
mogoče nastaviti do **8 views** (View 0 do View 7) — View 0 je viden
privzeto; dodatne views aktivirajte za deljen zaslon ali sliko v
sliki.

### Aktiviranje Views

1. Izberite "Enable Views" v lastnostih sobe
2. Konfigurirajte View 0 (glavni view)

### Lastnosti Views

| Lastnost | Opis |
|-----------|-------------|
| **View X/Y** | Zgornji levi kot view v sobi |
| **View Width/Height** | Velikost vidnega področja |
| **Port X/Y** | Položaj na zaslonu |
| **Port Width/Height** | Velikost na zaslonu (se lahko raztegne) |
| **Object Following** | Objekt, ki mu view sledi |
| **Border H/V** | Mrtvo območje, preden se kamera premakne |

### Sledenje Objektu

Da kamera sledi igralcu:
1. Nastavite "Object Following" na `obj_player`
2. Prilagodite "Border H" in "Border V" za gladko drsenje

---

## Vrstni Red Sob

Vrstni red sob v drevesu virov določa:
1. Katera soba se naloži prva (soba na vrhu = začetna soba)
2. Vrstni red za akciji "Next Room" in "Previous Room"

### Spreminjanje Vrstnega Reda Sob

- Povlecite sobe v drevesu virov, da jih preuredite
- Ali desno kliknite in uporabite "Premakni Gor" / "Premakni Dol"

---

## Nasveti in Dobre Prakse

### Organizacija
- Sobe jasno poimenujte glede na njihov namen
- Ohranite glavni meni kot prvo sobo
- Uporabljajte dosledne velikosti sob znotraj igre

### Zmogljivost
- Ne postavljajte preveč instanc v eno sobo
- Za statično geometrijo nivojev uporabite ploščice
- Kadar je mogoče, uničite instance zunaj zaslona

---

## Naslednji Koraki

- [[Urejevalnik_Objektov_sl]] - Ustvarite objekte za postavljanje v sobe
- [[Dogodki_in_Akcije_sl]] - Dodajte interaktivnost svojim nivojem
- [[Izvoz_Iger_sl]] - Delite svojo dokončano igro
