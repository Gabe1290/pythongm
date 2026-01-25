# Vadnica: Ustvari klasično igro Pong

> **Izberite svoj jezik / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Pong) | [Français](Tutorial-Pong_fr) | [Deutsch](Tutorial-Pong_de) | [Italiano](Tutorial-Pong_it) | [Español](Tutorial-Pong_es) | [Português](Tutorial-Pong_pt) | [Slovenščina](Tutorial-Pong_sl) | [Українська](Tutorial-Pong_uk) | [Русский](Tutorial-Pong_ru)

---

## Uvod

V tej vadnici boš ustvaril klasično igro **Pong** - eno od prvih videoiger, ki je bila kdaj narejena! Pong je igra za dva igralca, kjer vsak igralec nadzira veslo in poskuša zadeti žogo čez veslo nasprotnika, da zbira točke.

**Kaj se boš naučil:**
- Ustvarjanje likov za vesla, žogo in stene
- Obvladovanje vnosov tipkovnice za dva igralca
- Oteženje objektov med seboj
- Sledenje in prikaz točk obeh igralcev
- Uporaba globalnih spremenljivk

**Težavnost:** Začetnik
**Prednastavka:** Prednastavka za začetnike

---

## Korak 1: Načrtuj svojo igro

Preden začnemo, razumejmo, kaj potrebujemo:

| Element | Namen |
|---------|-------|
| **Žoga** | Skaklje med igralcema |
| **Levo veslo** | Igralec 1 nadzira s tipkama W/S |
| **Desno veslo** | Igralec 2 nadzira z gornjim/spodnjim puščico |
| **Stene** | Zgornja in spodnja meja |
| **Cilji** | Nevidni predeli za vsakim veslom za zaznavanja točkovanja |
| **Prikaz točk** | Prikazuje točke obeh igralcev |

---

## Korak 2: Ustvari like

### 2.1 Lik žoge

1. V **Drevesu virov** desno klikni na **Likove** in izberi **Ustvari lik**
2. Poimenuj ga `spr_ball`
3. Klikni **Uredi lik** da odpreš urejevalnik likov
4. Nariši majhen bel krog (približno 16x16 pikslov)
5. Klikni **V redu** da shranišs

### 2.2 Liki vesla

Ustvarili bomo dve vesli - eno za vsakega igralca:

**Levo veslo (Igralec 1):**
1. Ustvari nov lik imenovan `spr_paddle_left`
2. Nariši dolgo, tanko pravokotnik upognjeno kot oklepaj ")" - priporočena modra barva
3. Velikost: približno 16x64 pikslov

**Desno veslo (Igralec 2):**
1. Ustvari nov lik imenovan `spr_paddle_right`
2. Nariši dolgo, tanko pravokotnik upognjeno kot oklepaj "(" - priporočena rdeča barva
3. Velikost: približno 16x64 pikslov

### 2.3 Lik stene

1. Ustvari nov lik imenovan `spr_wall`
2. Nariši trdno pravokotnik (siva ali bela barva)
3. Velikost: 32x32 pikslov (raztiegnili ga bomo v sobi)

### 2.4 Lik cilja (Nevidno)

1. Ustvari nov lik imenovan `spr_goal`
2. Naredi ga 32x32 pikslov
3. Pusti ga previden ali naredi trdno barvo (v igri bo nevidna)

---

## Korak 3: Ustvari objekt stene

Objekt stene ustvari meje na vrhu in dnu igrišča.

1. Desno klikni na **Predmete** in izberi **Ustvari predmet**
2. Poimenuj ga `obj_wall`
3. Nastavi lik na `spr_wall`
4. **Označite okence "Trdna"** - to je pomembno za odbijanje!
5. Ni potrebnih dogodkov - stena se samo nahaja tam

---

## Korak 4: Ustvari objekte vesla

### 4.1 Levo veslo (Igralec 1)

1. Ustvari nov predmet imenovan `obj_paddle_left`
2. Nastavi lik na `spr_paddle_left`
3. **Označite okence "Trdna"**

**Dodaj dogodke tipkovnice za gibanje:**

**Dogodek: Pritisk na tipko W**
1. Dodaj dogodek → Tipkovnica → Pritisk W
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `-8` (premika se navzgor)

**Dogodek: Spustitev tipke W**
1. Dodaj dogodek → Tipkovnica → Spustitev W
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `0` (preneha se premikati)

**Dogodek: Pritisk na tipko S**
1. Dodaj dogodek → Tipkovnica → Pritisk S
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `8` (premika se navzdol)

**Dogodek: Spustitev tipke S**
1. Dodaj dogodek → Tipkovnica → Spustitev S
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `0` (preneha se premikati)

**Dogodek: Trčenje z obj_wall**
1. Dodaj dogodek → Trčenje → obj_wall
2. Dodaj akcijo: **Gibanje** → **Odbij od predmetov**
3. Izberi "Proti trdnim predmetom"

### 4.2 Desno veslo (Igralec 2)

1. Ustvari nov predmet imenovan `obj_paddle_right`
2. Nastavi lik na `spr_paddle_right`
3. **Označite okence "Trdna"**

**Dodaj dogodke tipkovnice za gibanje:**

**Dogodek: Pritisk na gornji puščico**
1. Dodaj dogodek → Tipkovnica → Pritisk Gor
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `-8`

**Dogodek: Spustitev gornje puščice**
1. Dodaj dogodek → Tipkovnica → Spustitev Gor
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `0`

**Dogodek: Pritisk na spodnjo puščico**
1. Dodaj dogodek → Tipkovnica → Pritisk Dol
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `8`

**Dogodek: Spustitev spodnje puščice**
1. Dodaj dogodek → Tipkovnica → Spustitev Dol
2. Dodaj akcijo: **Gibanje** → **Nastavi navpično hitrost**
3. Nastavi navpično hitrost na `0`

**Dogodek: Trčenje z obj_wall**
1. Dodaj dogodek → Trčenje → obj_wall
2. Dodaj akcijo: **Gibanje** → **Odbij od predmetov**
3. Izberi "Proti trdnim predmetom"

---

## Korak 5: Ustvari objekt žoge

1. Ustvari nov predmet imenovan `obj_ball`
2. Nastavi lik na `spr_ball`

**Dogodek: Ustvari**
1. Dodaj dogodek → Ustvari
2. Dodaj akcijo: **Gibanje** → **Začni se premikati v smeri**
3. Izberi diagonalno smer (ne ravno navzgor ali navzdol)
4. Nastavi hitrost na `6`

**Dogodek: Trčenje z obj_paddle_left**
1. Dodaj dogodek → Trčenje → obj_paddle_left
2. Dodaj akcijo: **Gibanje** → **Odbij od predmetov**
3. Izberi "Proti trdnim predmetom"

**Dogodek: Trčenje z obj_paddle_right**
1. Dodaj dogodek → Trčenje → obj_paddle_right
2. Dodaj akcijo: **Gibanje** → **Odbij od predmetov**
3. Izberi "Proti trdnim predmetom"

**Dogodek: Trčenje z obj_wall**
1. Dodaj dogodek → Trčenje → obj_wall
2. Dodaj akcijo: **Gibanje** → **Odbij od predmetov**
3. Izberi "Proti trdnim predmetom"

---

## Korak 6: Ustvari objekte ciljev

Cilji so nevidni predeli za vsakim veslom. Ko žoga vstopi v cilj, nasprotnik zbere točko.

### 6.1 Levi cilj

1. Ustvari nov predmet imenovan `obj_goal_left`
2. Nastavi lik na `spr_goal`
3. **Odkljukaj "Vidna"** - cilj bi moral biti nevidna
4. **Označite okence "Trdna"**

### 6.2 Desni cilj

1. Ustvari nov predmet imenovan `obj_goal_right`
2. Nastavi lik na `spr_goal`
3. **Odkljukaj "Vidna"**
4. **Označite okence "Trdna"**

### 6.3 Dodaj dogodke trčenja ciljev v žogo

Pojdi nazaj k `obj_ball` in dodaj te dogodke:

**Dogodek: Trčenje z obj_goal_left**
1. Dodaj dogodek → Trčenje → obj_goal_left
2. Dodaj akcijo: **Gibanje** → **Skoči na začetni položaj** (ponastavi žogo)
3. Dodaj akcijo: **Točke** → **Nastavi točke**
   - Spremenljivka: `global.p2score`
   - Vrednost: `1`
   - Označite "Relativna" (dodaja 1 trenutnim točkam)

**Dogodek: Trčenje z obj_goal_right**
1. Dodaj dogodek → Trčenje → obj_goal_right
2. Dodaj akcijo: **Gibanje** → **Skoči na začetni položaj**
3. Dodaj akcijo: **Točke** → **Nastavi točke**
   - Spremenljivka: `global.p1score`
   - Vrednost: `1`
   - Označite "Relativna"

---

## Korak 7: Ustvari objekt za prikaz točk

1. Ustvari nov predmet imenovan `obj_score`
2. Lik ni potreben

**Dogodek: Ustvari**
1. Dodaj dogodek → Ustvari
2. Dodaj akcijo: **Točke** → **Nastavi točke**
   - Spremenljivka: `global.p1score`
   - Vrednost: `0`
3. Dodaj akcijo: **Točke** → **Nastavi točke**
   - Spremenljivka: `global.p2score`
   - Vrednost: `0`

**Dogodek: Risanje**
1. Dodaj dogodek → Risanje
2. Dodaj akcijo: **Risanje** → **Nariši besedilo**
   - Besedilo: `Igralec 1:`
   - X: `10`
   - Y: `10`
3. Dodaj akcijo: **Risanje** → **Nariši spremenljivko**
   - Spremenljivka: `global.p1score`
   - X: `100`
   - Y: `10`
4. Dodaj akcijo: **Risanje** → **Nariši besedilo**
   - Besedilo: `Igralec 2:`
   - X: `10`
   - Y: `30`
5. Dodaj akcijo: **Risanje** → **Nariši spremenljivko**
   - Spremenljivka: `global.p2score`
   - X: `100`
   - Y: `30`

---

## Korak 8: Oblikuj sobo

1. Desno klikni na **Sobe** in izberi **Ustvari sobo**
2. Poimenuj jo `room_pong`
3. Nastavi velikost sobe (npr. 640x480)

**Postavi predmete:**

1. **Stene**: Postavi `obj_wall` naprave vzdolž zgornjih in spodnjih robov sobe
2. **Levo veslo**: Postavi `obj_paddle_left` blizu levega roba, naravnano navpično
3. **Desno veslo**: Postavi `obj_paddle_right` blizu desnega roba, naravnano navpično
4. **Žoga**: Postavi `obj_ball` v sredino sobe
5. **Cilji**:
   - Postavi `obj_goal_left` naprave vzdolž levega roba (za veslom)
   - Postavi `obj_goal_right` naprave vzdolž desnega roba
6. **Prikaz točk**: Postavi `obj_score` kjerkoli (nima lika, samo narisuje besedilo)

**Primer razporeditve sobe:**
```
[STENA STENA STENA STENA STENA STENA STENA STENA STENA STENA]
[CILJ]  [VESLO_L]            [ŽOGA]            [VESLO_D]  [CILJ]
[CILJ]  [VESLO_L]                              [VESLO_D]  [CILJ]
[CILJ]                                                    [CILJ]
[STENA STENA STENA STENA STENA STENA STENA STENA STENA STENA]
```

---

## Korak 9: Testiraj svojo igro!

1. Klikni **Zaženi** ali pritisni **F5** da testirate svojo igro
2. Igralec 1 uporablja **W** (gor) in **S** (dol)
3. Igralec 2 uporablja **Gornji puščico** in **Spodnji puščico**
4. Poskusi zadeti žogo čez veslo nasprotnika!

---

## Izboljšave (Izbirne)

### Povečanje hitrosti
Naredi žogo hitrejšo vsak put, ko zadene veslo z dodajanjem v dogodke trčenja:
- Po akciji odbijanja, dodaj **Gibanje** → **Nastavi hitrost**
- Nastavi hitrost na `speed + 0.5` z označenim "Relativna"

### Zvočni efekti
Dodaj zvoke kadar:
- Žoga zadene veslo
- Žoga zadene steno
- Igralec zbere točko

### Pogoj za zmago
Dodaj preverjanje v dogodek risanja:
- Če `global.p1score >= 10`, prikaži "Igralec 1 je zmagal!"
- Če `global.p2score >= 10`, prikaži "Igralec 2 je zmagal!"

---

## Odpravljanje napak

| Problem | Rešitev |
|---------|---------|
| Žoga gre skozi veslo | Prepričaj se, da imajo vesla označeno "Trdna" |
| Veslo se ne ustavi pri stenah | Dodaj dogodek trčenja z obj_wall |
| Točke se ne posodabljajo | Preveri, da se imena spremenljivk natančno ujemajo (global.p1score, global.p2score) |
| Žoga se ne premika | Preveri, da ima dogodek ustvarjanja akcijo gibanja |

---

## Kaj si se naučil

Čestitke! Ustvaril si popolno igro Pong za dva igralca! Naučil si se:

- Kako upravljati vhode tipkovnice za dva različna igralca
- Kako uporabiti dogodke spustitve tipke za zaustavitev gibanja
- Kako narediti, da se objekti odbijajo med seboj
- Kako uporabiti globalne spremenljivke za sledenje točkam
- Kako prikazati besedilo in spremenljivke na zaslonu

---

## Vidi tudi

- [Prednastavka za začetnike](Beginner-Preset_sl) - Pregled začetniških lastnosti
- [Vadnica: Breakout](Tutorial-Breakout_sl) - Ustvari igro s preslikanim opekam
- [Odporedilo dogodkov](Event-Reference_sl) - Popolna dokumentacija dogodkov
- [Popolno opredilo akcij](Full-Action-Reference_sl) - Vse razpoložljive akcije
