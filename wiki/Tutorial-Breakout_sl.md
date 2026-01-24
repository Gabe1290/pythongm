# Vadnica: Ustvari igro Breakout

*[Home](Home_sl) | [Beginner Preset](Beginner-Preset_sl) | [English](Tutorial-Breakout)*

Ta vadnica vas bo vodila skozi ustvarjanje klasicne igre Breakout. Je odlicen prvi projekt za ucenje PyGameMaker!

![Koncept igre Breakout](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## Kaj se boste naucili

- Ustvarjanje in uporaba sprite-ov
- Nastavitev igralnih objektov z dogodki in akcijami
- Tipkovnicni kontroli za premikanje igralca
- Zaznavanje trkov in odbijanje
- Unicenje objektov ob trku
- Gradnja igralne sobe

---

## Korak 1: Ustvari sprite-e

Najprej moramo ustvariti vizualne elemente za naso igro.

### 1.1 Ustvari sprite loparja
1. V plosci **Assets** z desnim klikom na **Sprites** → **Create Sprite**
2. Poimenujte ga `spr_paddle`
3. Narisite vodoraven pravokotnik (priblizno 64x16 pik)
4. **Pomembno:** Kliknite **Center** za nastavitev izhodisca na sredino

### 1.2 Ustvari sprite zogice
1. Ustvarite drug sprite z imenom `spr_ball`
2. Narisite majhen krog (priblizno 16x16 pik)
3. Kliknite **Center** za nastavitev izhodisca

### 1.3 Ustvari sprite opeke
1. Ustvarite sprite z imenom `spr_brick`
2. Narisite pravokotnik (priblizno 48x24 pik)
3. Kliknite **Center** za nastavitev izhodisca

### 1.4 Ustvari sprite stene
1. Ustvarite sprite z imenom `spr_wall`
2. Narisite kvadrat (priblizno 32x32 pik) - to bo meja
3. Kliknite **Center** za nastavitev izhodisca

### 1.5 Ustvari ozadje (neobvezno)
1. Z desnim klikom na **Backgrounds** → **Create Background**
2. Poimenujte ga `bg_game`
3. Narisite ali nalozite sliko ozadja

---

## Korak 2: Ustvari objekt loparja

Zdaj bomo programirali lopar, ki ga igralec nadzoruje.

### 2.1 Ustvari objekt
1. Z desnim klikom na **Objects** → **Create Object**
2. Poimenujte ga `obj_paddle`
3. Nastavite **Sprite** na `spr_paddle`
4. Oznacite polje **Solid**

### 2.2 Dodaj premikanje z desno puscico
1. Kliknite **Add Event** → **Keyboard** → izberite **Right Arrow**
2. Dodajte akcijo **Set Horizontal Speed**
3. Nastavite **value** na `5` (ali katerokoli hitrost zelite)

### 2.3 Dodaj premikanje z levo puscico
1. Kliknite **Add Event** → **Keyboard** → izberite **Left Arrow**
2. Dodajte akcijo **Set Horizontal Speed**
3. Nastavite **value** na `-5`

### 2.4 Ustavi ob sprosceni tipki
Lopar se premika tudi po sprosceni tipki! Popravimo to.

1. Kliknite **Add Event** → **Keyboard Release** → izberite **Right Arrow**
2. Dodajte akcijo **Set Horizontal Speed**
3. Nastavite **value** na `0`

4. Kliknite **Add Event** → **Keyboard Release** → izberite **Left Arrow**
5. Dodajte akcijo **Set Horizontal Speed**
6. Nastavite **value** na `0`

Zdaj se lopar ustavi, ko sprostite puscicne tipke.

---

## Korak 3: Ustvari objekt zogice

### 3.1 Ustvari objekt
1. Ustvarite nov objekt z imenom `obj_ball`
2. Nastavite **Sprite** na `spr_ball`
3. Oznacite polje **Solid**

### 3.2 Nastavi zacetno gibanje
1. Kliknite **Add Event** → **Create**
2. Dodajte akcijo **Move in Direction** (ali **Set Horizontal/Vertical Speed**)
3. Nastavite diagonalno smer s hitrostjo `5`
   - Na primer: **hspeed** = `4`, **vspeed** = `-4`

To povzroci, da se zogica zacne premikati ob zacetku igre.

### 3.3 Odbij se od loparja
1. Kliknite **Add Event** → **Collision** → izberite `obj_paddle`
2. Dodajte akcijo **Reverse Vertical** (za odboj)

### 3.4 Odbij se od sten
1. Kliknite **Add Event** → **Collision** → izberite `obj_wall`
2. Dodajte akcijo **Reverse Horizontal** ali **Reverse Vertical** po potrebi
   - Ali uporabite obe za obravnavo odbijanja v kotih

---

## Korak 4: Ustvari objekt opeke

### 4.1 Ustvari objekt
1. Ustvarite nov objekt z imenom `obj_brick`
2. Nastavite **Sprite** na `spr_brick`
3. Oznacite polje **Solid**

### 4.2 Unici ob trku z zogico
1. Kliknite **Add Event** → **Collision** → izberite `obj_ball`
2. Dodajte akcijo **Destroy Instance** s ciljem **self**

To unici opeko, ko jo zogica zadene!

### 4.3 Odbij zogico
V istem dogodku trka dodajte tudi:
1. Dodajte akcijo **Reverse Vertical** (uporabite na **other** - zogico)

Ali se vrnite na `obj_ball` in dodajte:
1. **Add Event** → **Collision** → izberite `obj_brick`
2. Dodajte akcijo **Reverse Vertical**

---

## Korak 5: Ustvari objekt stene

### 5.1 Ustvari objekt
1. Ustvarite nov objekt z imenom `obj_wall`
2. Nastavite **Sprite** na `spr_wall`
3. Oznacite polje **Solid**

To je vse - stena mora biti samo trdna, da se zogica odbije.

---

## Korak 6: Ustvari igralno sobo

### 6.1 Ustvari sobo
1. Z desnim klikom na **Rooms** → **Create Room**
2. Poimenujte jo `room_game`

### 6.2 Nastavi ozadje (neobvezno)
1. V nastavitvah sobe poiscite **Background**
2. Izberite svoje ozadje `bg_game`
3. Oznacite **Stretch**, ce zelite, da zapolni sobo

### 6.3 Postavi objekte

Zdaj postavite svoje objekte v sobo:

1. **Postavi lopar:** Postavite `obj_paddle` na spodnji sredini sobe

2. **Postavi stene:** Postavite instance `obj_wall` ob robovih:
   - Vzdolz vrha
   - Vzdolz leve strani
   - Vzdolz desne strani
   - Pustite dno odprto (tu lahko zogica uide!)

3. **Postavi zogico:** Postavite `obj_ball` nekje na sredino

4. **Postavi opeke:** Razporedite instance `obj_brick` v vrstah na vrhu sobe

---

## Korak 7: Preizkusi svojo igro!

1. Kliknite gumb **Play** (zelena puscica)
2. Uporabite tipki **Levo** in **Desno** za premikanje loparja
3. Poskusite odbiti zogico, da unicite vse opeke!
4. Pritisnite **Escape** za izhod

---

## Kaj sledi?

Vasa osnovna igra Breakout je dokoncana! Tukaj je nekaj izboljsav, ki jih lahko preizkusite:

### Dodaj sistem zivljenj
- Dodajte dogodek **No More Lives** za prikaz "Game Over"
- Izgubite zivljenje, ko zogica uide skozi dno

### Dodaj tocke
- Uporabite akcijo **Add Score** pri unicenju opek
- Prikazite tocke z **Draw Score**

### Dodaj vec nivojev
- Ustvarite vec sob z razlicnimi razporeditvami opek
- Uporabite **Next Room**, ko so vse opeke unicene

### Dodaj zvocne ucinke
- Dodajte zvoke za odbijanje in unicenje opek
- Uporabite akcijo **Play Sound**

---

## Povzetek objektov

| Objekt | Sprite | Trden | Dogodki |
|--------|--------|-------|---------|
| `obj_paddle` | `spr_paddle` | Da | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Da | Create, Collision (paddle, wall, brick) |
| `obj_brick` | `spr_brick` | Da | Collision (ball) - Unici self |
| `obj_wall` | `spr_wall` | Da | Ni potrebno |

---

## Glejte tudi

- [Beginner Preset](Beginner-Preset_sl) - Dogodki in akcije, uporabljeni v tej vadnici
- [Event Reference](Event-Reference_sl) - Vsi razpolozljivi dogodki
- [Full Action Reference](Full-Action-Reference_sl) - Vse razpolozljive akcije
