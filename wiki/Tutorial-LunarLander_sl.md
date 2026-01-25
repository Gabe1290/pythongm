# Vadnica: Ustvari Igro Lunarnega Pristanka

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Uvod

V tej vadnici boš ustvaril **Igro Lunarnega Pristanka** - klasično arkadno igro, kjer nadziraš vesoljsko plovilo, ki se spušča na pristajalno ploščad. Upravljati moraš potisk, da protiuteži gravitacijo in pristaneš nežno brez trka. Ta igra je popolna za učenje fizikalnih konceptov kot so gravitacija, potisk, hitrost in upravljanje goriva.

**Kaj se boš naučil:**
- Fizika gravitacije in potiska
- Zaznavanje pristanka na podlagi hitrosti
- Sistem upravljanja goriva
- Rotacijski ali smerni nadzor
- Varne pristajalne cone

**Težavnost:** Začetnik
**Preset:** Začetniški Preset

---

## Korak 1: Razumevanje Igre

### Mehanike Igre
1. Pristajalniku gravitacija vleče navzdol
2. Pritisk GOR uporabi potisk navzgor (porabi gorivo)
3. LEVO/DESNO nadzira rotacijo ali gibanje
4. Pristani nežno na ploščadi za zmago
5. Trk če pristaneš prehitro ali zgrešiš ploščad
6. Brez goriva ne moreš upočasniti!

### Kaj Potrebujemo

| Element | Namen |
|---------|-------|
| **Pristajalnik** | Plovilo, ki ga nadziraš |
| **Ploščad** | Varna cona za pristanek |
| **Tla** | Teren, ki povzroči trk |
| **Prikaz Goriva** | Prikazuje preostalo gorivo |
| **Prikaz Hitrosti** | Prikazuje trenutno hitrost |

---

## Korak 2: Ustvari Sprite

### Sprite
- `spr_lander` (32x32 pikslov) - preprosto plovilo
- `spr_pad` (64x16 pikslov) - pristajalna ploščad
- `spr_ground` (32x32 pikslov) - skalnati teren
- `spr_flame` (16x16 pikslov) - potisni plamen (opcijsko)

---

## Korak 3-4: Ustvari Objekte Tal in Ploščadi

**obj_ground** in **obj_pad**: Nastavi sprite, označi "Trden"

---

## Korak 5: Ustvari Objekt Pristajalnika

### Dogodek Create
```gml
gravity_force = 0.05;
thrust_force = 0.1;
max_speed = 5;
hsp = 0;
vsp = 0;
fuel = 100;
fuel_use = 0.5;
landed = false;
crashed = false;
safe_speed = 2;
```

### Dogodek Step
```gml
if (landed || crashed) exit;

vsp += gravity_force;

if (keyboard_check(vk_up) && fuel > 0) {
    vsp -= thrust_force;
    fuel -= fuel_use;
    if (fuel < 0) fuel = 0;
}

if (keyboard_check(vk_left)) hsp -= 0.05;
if (keyboard_check(vk_right)) hsp += 0.05;

hsp = clamp(hsp, -max_speed, max_speed);
vsp = clamp(vsp, -max_speed, max_speed);

x += hsp;
y += vsp;

if (x < 16) { x = 16; hsp = 0; }
if (x > room_width - 16) { x = room_width - 16; hsp = 0; }
if (y < 16) { y = 16; vsp = 0; }
```

### Trk z obj_pad
```gml
var total_speed = sqrt(hsp*hsp + vsp*vsp);

if (total_speed <= safe_speed) {
    landed = true;
    hsp = 0;
    vsp = 0;
    show_message("Popoln Pristanek! Zmagal si!");
} else {
    crashed = true;
    show_message("Trk! Prehitro!");
    room_restart();
}
```

### Trk z obj_ground
```gml
crashed = true;
show_message("Trk v teren!");
room_restart();
```

---

## Korak 6-7: Krmilnik Igre

**obj_game_controller** - Dogodek Draw: Prikaži gorivo, hitrost, navodila

---

## Korak 8: Oblikuj Svojo Raven

1. Ustvari `room_game` (640x480)
2. Črno ozadje (vesolje)
3. Postavi tla spodaj z odprtino
4. Postavi ploščad v odprtino
5. Postavi pristajalnik zgoraj
6. Postavi krmilnik igre

---

## Kaj Si Se Naučil

- **Fizika potiska** - Protiuteži gravitaciji
- **Upravljanje hitrosti** - Nadzor hitrosti
- **Sistem goriva** - Upravljanje virov
- **Zaznavanje trkov** - Različni rezultati

---

## Glej Tudi

- [Vadnice](Tutorials_sl) - Več vadnic
- [Vadnica: Platformer](Tutorial-Platformer_sl) - Ustvari platformsko igro

