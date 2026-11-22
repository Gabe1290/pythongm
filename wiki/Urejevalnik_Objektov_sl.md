# Urejevalnik Objektov

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Nazaj na začetno stran](Home_sl)

Objekti so temeljni gradniki vaše igre. Predstavljajo vse, od
igralcev in sovražnikov do zbirateljskih predmetov in elementov
vmesnika.

---

## Odpiranje Urejevalnika Objektov

1. Dvokliknite na obstoječi objekt v drevesu virov, ali
2. Desno kliknite na **Objects** > **Create Object**

![Urejevalnik Objektov: seznam dogodkov na levi (Create, Step, več
dogodkov Collision, Keyboard, No More Lives, Game Start), lastnosti
objekta (sprite, parent, Visible/Persistent/Solid) na desni, ter zavihki
Event List / Blockly / Urejevalnik Kode, ki spremenijo način urejanja
akcij posameznega dogodka](images/object-editor.png)

---

## Lastnosti Objekta

| Lastnost | Opis |
|-----------|-------------|
| **Name** | Edinstven identifikator objekta (npr. `obj_igralec`) |
| **Sprite** | Vizualna predstavitev objekta |
| **Visible** | Ali se objekt izrisuje (privzeto: da) |
| **Solid** | Uporablja se za zaznavanje trkov s trdnimi objekti |
| **Depth** | Vrstni red risanja (nižje = izriše se zgoraj) |
| **Persistent** | Objekt preživi menjave sob |
| **Parent Object** | Deduje skupne lastnosti/dogodke od drugega objekta |

### Konvencija Poimenovanja

Uporabite predpono `obj_` za objekte:
- `obj_igralec`
- `obj_sovraznik`
- `obj_kovanec`
- `obj_stena`

---

## Dogodki

Dogodki so sprožilci, ki povzročijo izvajanje akcij. Kliknite "Add
Event", da ga dodate.

### Pogosti Dogodki

| Dogodek | Kdaj se Sproži |
|-------|------------------|
| **Ustvarjanje** | Enkrat, ko je instanca ustvarjena |
| **Uničenje** | Ko je instanca uničena |
| **Korak** | Vsako sličico igre (60-krat na sekundo) |
| **Risanje** | Med fazo risanja |
| **Alarm [0-11]** | Ko časovnik alarma doseže nič |

### Dogodki Tipkovnice

| Dogodek | Kdaj se Sproži |
|-------|------------------|
| **Key Press** | Enkrat, ko je tipka pritisnjena |
| **Key Release** | Enkrat, ko je tipka spuščena |
| **Keyboard** | Vsako sličico, dokler je tipka pritisnjena |
| **No Key** | Ko ni pritisnjena nobena tipka |

### Dogodki Miške

| Dogodek | Kdaj se Sproži |
|-------|------------------|
| **Mouse Button** | Ob kliku na instanco |
| **Global Mouse** | Ob kliku kjerkoli |
| **Mouse Enter** | Ko kazalec vstopi v instanco |
| **Mouse Leave** | Ko kazalec zapusti instanco |

### Dogodki Trkov

| Dogodek | Kdaj se Sproži |
|-------|------------------|
| **Collision with [objekt]** | Ob dotiku z drugo vrsto objekta |

### Ostali Dogodki

| Dogodek | Kdaj se Sproži |
|-------|------------------|
| **Zunaj sobe** | Ko instanca zapusti sobo |
| **Dotik roba sobe** | Ko se instanca dotakne roba sobe |
| **Začetek igre** | Enkrat, ob zagonu igre |
| **Konec igre** | Enkrat, ob zaprtju igre |
| **Začetek sobe** | Ob vstopu v sobo |
| **Konec sobe** | Ob izstopu iz sobe |

---

## Akcije

Akcije so operacije, ki se izvedejo, ko se sproži dogodek. Vsak
dogodek ima lahko več akcij, ki se izvedejo po vrsti.

### Akcije Gibanja
- **Nastavi hitrost** — Nastavi hitrost gibanja
- **Nastavi smer** — Nastavi smer gibanja (0-360 stopinj)
- **Nastavi vodoravno hitrost** — Nastavi hspeed
- **Nastavi navpično hitrost** — Nastavi vspeed
- **Premakni proti točki** — Premik proti koordinatam
- **Jump to Position** — Trenutna teleportacija na koordinate
- **Skoči na začetni položaj** — Vrni se na položaj ustvarjanja
- **Skoči na naključni položaj** — Teleportiraj na naključni položaj

### Akcije Instance
- **Ustvari instanco** — Ustvari nov objekt
- **Uniči instanco** — Odstrani trenutno instanco
- **Spremeni instanco** — Preobrazi v drugo vrsto objekta

### Akcije Časovnika
- **Nastavi budilko** — Zaženi odštevalni časovnik
- **Premor** — Ustavi izvajanje za kratek trenutek

### Akcije Risanja
- **Nariši sprite** — Nariši sprite
- **Nariši besedilo** — Prikaži besedilo na zaslonu
- **Nariši pravokotnik** — Nariši zapolnjen ali obrobljen pravokotnik
- **Nariši rezultat** — Prikaži trenutni rezultat
- **Nariši življenja** — Prikaži preostala življenja
- **Nariši vrstico zdravja** — Prikaži vrstico zdravja

### Score/Lives/Health
- **Nastavi rezultat** — Spremeni vrednost rezultata
- **Nastavi življenja** — Spremeni število življenj
- **Nastavi zdravje** — Spremeni vrednost zdravja
- **Preveri rezultat** — Preveri pogoj rezultata
- **Preveri življenja** — Preveri pogoj življenj
- **Preveri zdravje** — Preveri pogoj zdravja

### Akcije Sobe
- **Naslednja soba** — Pojdi na naslednjo sobo
- **Prejšnja soba** — Pojdi na prejšnjo sobo
- **Znova zaženi sobo** — Ponastavi trenutno sobo
- **Pojdi v sobo** — Skoči na določeno sobo

### Akcije Zvoka
- **Predvajaj zvok** — Predvajaj zvočni učinek
- **Ustavi zvok** — Ustavi predvajani zvok
- **Predvajaj glasbo** — Predvajaj glasbo v ozadju
- **Ustavi glasbo** — Ustavi glasbo v ozadju

### Akcije Spremenljivk
- **Nastavi spremenljivko** — Dodeli vrednost spremenljivki
- **Preveri spremenljivko** — Preveri pogoj spremenljivke

---

## Vizualno Programiranje z Blockly

Namesto uporabe seznama akcij lahko preklopite na zavihek **Blockly**
za vizualno programiranje:

1. Odprite objekt
2. Kliknite na zavihek **Blockly**
3. Povlecite bloke iz orodne vrstice, da ustvarite logiko
4. Bloki se zaskočijo skupaj in tvorijo celotne programe

Za več podrobnosti glejte [[Vizualno_Programiranje_sl]].

---

## Nasveti in Dobre Prakse

### Organizacija
- Dajte objektom opisna imena
- Skupine povezanih objektov združite s podobnimi predponami
- Uporabite dogodek Create samo za inicializacijo

### Zmogljivost
- Izogibajte se zahtevnim izračunom v dogodku Step
- Uporabite alarme namesto ročnega štetja sličic
- Uničite instance, ki zapustijo sobo

### Odpravljanje Napak
- Za prikaz vrednosti uporabite akcijo **Prikaži sporočilo**
- Preverite izpis konzole za napake
- Med razvojem pogosto testirajte

---

## Primer: Preprosta Umetna Inteligenca za Sovražnika

```
Create Event:
  - Set Alarm[0] = 60 (1 sekunda pri 60 FPS)
  - Set direction = random(360)
  - Set speed = 2

Alarm[0] Event:
  - Set direction = random(360)
  - Set Alarm[0] = 60

Collision with obj_player:
  - Set Lives relative = -1
  - Destroy Instance
```

---

## Naslednji Koraki

- [[Urejevalnik_Sob_sl]] - Postavite objekte v svoje igralne nivoje
- [[Dogodki_in_Akcije_sl]] - Popolna referenca vseh dogodkov in akcij
- [[Vizualno_Programiranje_sl]] - Naučite se blokovnega programiranja z Blockly
