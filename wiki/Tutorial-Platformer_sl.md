# Vadnica: Ustvari Platformsko Igro

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Uvod

V tej vadnici boš ustvaril **Platformsko Igro** - akcijsko igro s stranskim pomikanjem, kjer igralec teče, skače in navigira po platformah, medtem ko se izogiba nevarnostim in zbira kovance. Ta klasični žanr je popoln za učenje gravitacije, mehanike skakanja in trkov s platformami.

**Kaj se boš naučil:**
- Gravitacija in fizika padanja
- Mehanika skakanja z zaznavanjem tal
- Trk s platformami (pristajanje na vrhu)
- Gibanje levo/desno
- Zbirateljski predmeti in nevarnosti

**Težavnost:** Začetnik
**Preset:** Začetniški Preset

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

## Korak 2: Ustvari Sprite

### Sprite
- `spr_player` (32x48 pikslov) - preprost lik
- `spr_ground` (32x32 pikslov) - ploščica trave/zemlje
- `spr_platform` (64x16 pikslov) - lebdeča platforma
- `spr_coin` (16x16 pikslov) - zlat krog
- `spr_spike` (32x32 pikslov) - trikotne bodice
- `spr_flag` (32x64 pikslov) - zastava na drogu

---

## Korak 3-4: Ustvari Objekte Tal in Platform

**obj_ground** in **obj_platform**: Nastavi sprite, označi "Trden"

---

## Korak 5: Ustvari Objekt Igralca

### Dogodek Create
```gml
hspeed_max = 4;
vspeed_max = 10;
jump_force = -10;
gravity_force = 0.5;
hsp = 0;
vsp = 0;
on_ground = false;
```

### Dogodek Step
```gml
var move_input = keyboard_check(vk_right) - keyboard_check(vk_left);
hsp = move_input * hspeed_max;

vsp += gravity_force;
if (vsp > vspeed_max) vsp = vspeed_max;

on_ground = place_meeting(x, y + 1, obj_ground);

if (on_ground && (keyboard_check_pressed(vk_up) || keyboard_check_pressed(vk_space))) {
    vsp = jump_force;
}

if (place_meeting(x + hsp, y, obj_ground)) {
    while (!place_meeting(x + sign(hsp), y, obj_ground)) x += sign(hsp);
    hsp = 0;
}
x += hsp;

if (place_meeting(x, y + vsp, obj_ground)) {
    while (!place_meeting(x, y + sign(vsp), obj_ground)) y += sign(vsp);
    vsp = 0;
}
y += vsp;
```

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

- **Fizika gravitacije** - Konstantna sila navzdol
- **Mehanika skakanja** - Negativna navpična hitrost
- **Zaznavanje tal** - Uporaba `place_meeting`
- **Obravnavanje trkov** - Premikanje piksel po piksel

---

## Glej Tudi

- [Vadnice](Tutorials_sl) - Več vadnic za igre
- [Vadnica: Labirint](Tutorial-Maze_sl) - Ustvari igro labirinta
