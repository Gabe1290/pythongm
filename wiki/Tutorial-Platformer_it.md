# Tutorial: Creare un Gioco Platform

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introduzione

In questo tutorial, creerai un **Gioco Platform** - un gioco d'azione a scorrimento laterale dove il giocatore corre, salta e naviga sulle piattaforme evitando pericoli e raccogliendo monete. Questo genere classico è perfetto per imparare la gravità, le meccaniche di salto e la collisione con le piattaforme.

**Cosa imparerai:**
- Gravità e fisica della caduta
- Meccaniche di salto con rilevamento del terreno
- Collisione con le piattaforme (atterrare sopra)
- Movimento sinistra/destra
- Collezionabili e pericoli

**Difficoltà:** Principiante
**Preset:** Preset Principiante

---

## Passo 1: Capire il Gioco

### Meccaniche di Gioco
1. Il giocatore è influenzato dalla gravità e cade
2. Il giocatore può muoversi a sinistra e destra
3. Il giocatore può saltare quando è a terra
4. Le piattaforme impediscono al giocatore di cadere attraverso
5. Raccogli monete per punti
6. Raggiungi la bandiera per completare il livello

### Cosa Ci Serve

| Elemento | Scopo |
|----------|-------|
| **Giocatore** | Il personaggio che controlli |
| **Terreno/Piattaforma** | Superfici solide su cui stare |
| **Moneta** | Oggetti collezionabili per il punteggio |
| **Spuntone** | Pericolo che ferisce il giocatore |
| **Bandiera** | Obiettivo che termina il livello |

---

## Passo 2: Creare gli Sprite

### 2.1 Sprite del Giocatore
- Nome: `spr_player`
- Disegna un personaggio semplice
- Dimensione: 32x48 pixel

### 2.2 Sprite del Terreno
- Nome: `spr_ground`
- Disegna una mattonella erba/terra
- Dimensione: 32x32 pixel

### 2.3 Sprite della Piattaforma
- Nome: `spr_platform`
- Disegna una piattaforma fluttuante
- Dimensione: 64x16 pixel

### 2.4 Sprite della Moneta
- Nome: `spr_coin`
- Piccolo cerchio giallo/dorato
- Dimensione: 16x16 pixel

### 2.5 Sprite dello Spuntone
- Nome: `spr_spike`
- Triangoli che puntano verso l'alto
- Dimensione: 32x32 pixel

### 2.6 Sprite della Bandiera
- Nome: `spr_flag`
- Bandiera su un palo
- Dimensione: 32x64 pixel

---

## Passo 3-4: Creare Oggetti Terreno e Piattaforma

**obj_ground** e **obj_platform**: Imposta sprite, spunta "Solido"

---

## Passo 5: Creare l'Oggetto Giocatore

### Evento Create
```gml
hspeed_max = 4;
vspeed_max = 10;
jump_force = -10;
gravity_force = 0.5;
hsp = 0;
vsp = 0;
on_ground = false;
```

### Evento Step
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

## Passo 6-8: Collezionabili e Pericoli

**obj_coin** - Collisione con obj_player: Punteggio +10, distruggi Self

**obj_spike** - Collisione con obj_player: Mostra messaggio, riavvia room

**obj_flag** - Collisione con obj_player: Mostra messaggio, prossima room

---

## Passo 9: Progetta il Tuo Livello

1. Crea `room_level1` (800x480)
2. Abilita snap alla griglia (32x32)
3. Posiziona terreno in basso, piattaforme in aria
4. Aggiungi monete, spuntoni
5. Metti bandiera alla fine, giocatore all'inizio

---

## Cosa Hai Imparato

- **Fisica della gravità** - Forza costante verso il basso
- **Meccaniche di salto** - Velocità verticale negativa
- **Rilevamento del terreno** - Usare `place_meeting`
- **Gestione delle collisioni** - Muoversi pixel per pixel

---

## Vedi Anche

- [Tutorial](Tutorials_it) - Altri tutorial di giochi
- [Tutorial: Labirinto](Tutorial-Maze_it) - Creare un gioco del labirinto
