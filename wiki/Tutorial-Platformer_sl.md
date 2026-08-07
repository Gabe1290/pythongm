# Vodič: Ustvari Platformsko Igro

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Uvod

V tem vodiču boš ustvaril **Platformsko Igro** - akcijsko igro s stranskim pomikanjem, kjer igralec teče, skače in navigira po platformah, medtem ko se izogiba nevarnostim in zbira kovance. Ta klasični žanr je odličen za učenje gravitacije, mehanike skakanja in trkov s platformami.

**Kaj se boš naučil:**
- Gravitacijo in fiziko padanja
- Mehaniko skakanja z zaznavanjem tal
- Trk s platformami (pristajanje na vrhu)
- Gibanje levo/desno
- Zbirateljske predmete in nevarnosti

**Težavnost:** Začetnik
**Prednastavitev:** Prednastavitev za začetnike

---

## Korak 1: Razumevanje Igre

### Mehanike Igre
1. Na igralca vpliva gravitacija in pade
2. Igralec se lahko premika levo in desno
3. Igralec lahko skoči, ko stoji na tleh
4. Platforme preprečujejo, da bi igralec padel skozi
5. Zberi kovance za točke
6. Doseži zastavo za dokončanje ravni

### Kaj Potrebujemo

| Element | Namen |
|---------|-------|
| **Igralec** | Lik, ki ga nadziraš |
| **Tla/Platforma** | Trdne površine za stojo |
| **Kovanec** | Zbirateljski predmeti za točke |
| **Bodica** | Nevarnost, ki poškoduje igralca |
| **Zastava** | Cilj, ki konča raven |

---

## Korak 2: Ustvari Sprite-e

### Sprite-i
- `spr_player` (32x48 pikslov) - preprost lik
- `spr_ground` (32x32 pikslov) - ploščica trave/zemlje
- `spr_platform` (64x16 pikslov) - lebdeča platforma
- `spr_coin` (16x16 pikslov) - zlat krog
- `spr_spike` (32x32 pikslov) - trikotne bodice
- `spr_flag` (32x64 pikslov) - zastava na drogu

---

## Korak 3: Ustvari Objekt Tla

Tla so trdna platforma, ki prepreči padec igralca.

1. Desno klikni na **Objects** in izberi **Create Object**
2. Poimenuj ga `obj_ground`
3. Nastavi sprite na `spr_ground`
4. **Označi polje "Solid"**
5. Dogodki niso potrebni

---

## Korak 4: Ustvari Objekt Platforma

Platforme delujejo enako kot tla, vendar jih lahko postaviš v zrak.

1. Ustvari nov objekt z imenom `obj_platform`
2. Nastavi sprite na `spr_platform`
3. **Označi polje "Solid"**

---

## Korak 5: Ustvari Objekt Igralec

Igralec je najbolj zapleten objekt, z gravitacijo, skakanjem in gibanjem.

1. Ustvari nov objekt z imenom `obj_player`
2. Nastavi sprite na `spr_player`

### 5.1 Gravitacija

**Dogodek: Create** — Add Action: **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° pomeni naravnost navzdol;
vrednost se vsako sličico prišteje k navpični hitrosti igralca, zato
igralec od tu naprej sam pospešuje navzdol.

### 5.2 Gibanje, Skakanje in Trk s Tlemi

Dodaj te dogodke po istem vzorcu, ki ga že uporabljajo prejšnji vodiči tega wikija:

| Dogodek | Akcija |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed na `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed na `4` |
| Keyboard: No Key | Set Horizontal Speed na `0` |
| Key Press → Up Arrow | Set Vertical Speed na `-10` |
| Collision with obj_ground | Stop Movement |

Dve podrobnosti, zaradi katerih se to zdi pravilno:

- **No Key nastavi SAMO vodoravno hitrost na 0** — nikoli ne uporabi
  tu Stop Movement, ker Stop Movement izniči tudi navpično hitrost, kar
  bi vsakič izničilo gravitacijo, ko igralec spusti smerno tipko.
- **Key Press (ne held)** je tisto, zaradi česar je Up en sam skočni
  impulz, namesto da bi igralca poganjal navzgor vsako sličico, ko je
  tipka pridržana. **Stop Movement** ob pristanku izniči ta impulz,
  tako da igralec po pristanku ne nadaljuje z vzpenjanjem — vgrajeni
  trdi trk pogona (Korak 3 je `obj_ground` že naredil Solid) že
  prepreči, da bi igralec potonil v tla; dogodek tukaj le počisti
  preostalo hitrost padanja.

---

## Korak 6-8: Zbirateljski Predmeti in Nevarnosti

**obj_coin** - Trk z obj_player: Rezultat +10, uniči Self

**obj_spike** - Trk z obj_player: Prikaži sporočilo, ponastavi sobo

**obj_flag** - Trk z obj_player: Prikaži sporočilo, naslednja soba

---

## Korak 9: Oblikuj Svojo Raven

1. Ustvari `room_level1` (800x480)
2. Omogoči pripenjanje na mrežo (32x32)
3. Postavi tla spodaj, platforme v zraku
4. Dodaj kovance, bodice
5. Postavi zastavo na konec, igralca na začetek

---

## Kaj Si Se Naučil

- **Fizika gravitacije** - Set Gravity vsako sličico uporabi konstantno silo navzdol
- **Mehanika skakanja** - Dogodek Key Press (ne held) da en sam impulz hitrosti navzgor
- **Vgrajeni trdi trk** - Tla samodejno blokirajo igralca, ko so označena kot Solid, brez ročne kode za preverjanje položaja

---

## Glej Tudi

- [Vodiči](Tutorials_sl) - Več vodičev za igre
- [Vodič: Labirint](Tutorial-Maze_sl) - Ustvari igro labirinta
