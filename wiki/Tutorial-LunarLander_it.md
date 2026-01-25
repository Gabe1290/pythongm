# Tutorial: Creare un Gioco di Atterraggio Lunare

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introduzione

In questo tutorial, creerai un **Gioco di Atterraggio Lunare** - un classico gioco arcade dove controlli un'astronave che scende verso una piattaforma di atterraggio. Devi gestire la spinta per contrastare la gravità e atterrare dolcemente senza schiantarti. Questo gioco è perfetto per imparare concetti fisici come gravità, spinta, velocità e gestione del carburante.

**Cosa imparerai:**
- Fisica della gravità e della spinta
- Rilevamento dell'atterraggio basato sulla velocità
- Sistema di gestione del carburante
- Controllo di rotazione o direzionale
- Zone di atterraggio sicuro

**Difficoltà:** Principiante
**Preset:** Preset Principiante

---

## Passo 1: Capire il Gioco

### Meccaniche del Gioco
1. Il lander è attirato verso il basso dalla gravità
2. Premere SU applica spinta verso l'alto (usa carburante)
3. SINISTRA/DESTRA controlla rotazione o movimento
4. Atterra dolcemente sulla piattaforma per vincere
5. Crash se atterri troppo velocemente o manchi la piattaforma
6. Senza carburante non puoi rallentare!

### Cosa Ci Serve

| Elemento | Scopo |
|----------|-------|
| **Lander** | L'astronave che controlli |
| **Piattaforma** | Zona sicura per atterrare |
| **Terreno** | Suolo che causa crash |
| **Display Carburante** | Mostra carburante rimanente |
| **Display Velocità** | Mostra velocità attuale |

---

## Passo 2: Creare gli Sprite

### Sprite
- `spr_lander` (32x32 pixel) - astronave semplice
- `spr_pad` (64x16 pixel) - piattaforma di atterraggio
- `spr_ground` (32x32 pixel) - terreno roccioso
- `spr_flame` (16x16 pixel) - fiamma di propulsione (opzionale)

---

## Passo 3-4: Creare Oggetti Terreno e Piattaforma

**obj_ground** e **obj_pad**: Imposta sprite, seleziona "Solido"

---

## Passo 5: Creare l'Oggetto Lander

### Evento Create
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

### Evento Step
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

### Collisione con obj_pad
```gml
var total_speed = sqrt(hsp*hsp + vsp*vsp);

if (total_speed <= safe_speed) {
    landed = true;
    hsp = 0;
    vsp = 0;
    show_message("Atterraggio Perfetto! Hai Vinto!");
} else {
    crashed = true;
    show_message("Crash! Troppo veloce!");
    room_restart();
}
```

### Collisione con obj_ground
```gml
crashed = true;
show_message("Crash nel terreno!");
room_restart();
```

---

## Passo 6-7: Controller del Gioco

**obj_game_controller** - Evento Draw: Mostra carburante, velocità, istruzioni

---

## Passo 8: Progetta il Tuo Livello

1. Crea `room_game` (640x480)
2. Sfondo nero (spazio)
3. Posiziona terreno in basso con un'apertura
4. Posiziona piattaforma nell'apertura
5. Posiziona lander in alto
6. Posiziona controller del gioco

---

## Cosa Hai Imparato

- **Fisica della spinta** - Contrastare la gravità
- **Gestione della velocità** - Controllare la velocità
- **Sistema carburante** - Gestione risorse
- **Rilevamento collisioni** - Risultati diversi

---

## Vedi Anche

- [Tutorial](Tutorials_it) - Altri tutorial
- [Tutorial: Platformer](Tutorial-Platformer_it) - Crea un gioco platform

