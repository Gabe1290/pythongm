# Tutorial: Criar um Jogo de Pouso Lunar

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introdução

Neste tutorial, você criará um **Jogo de Pouso Lunar** - um jogo arcade clássico onde você controla uma espaçonave descendo em uma plataforma de pouso. Você deve gerenciar seu impulso para contrapor a gravidade e pousar suavemente sem bater. Este jogo é perfeito para aprender conceitos físicos como gravidade, impulso, velocidade e gerenciamento de combustível.

**O que você aprenderá:**
- Física de gravidade e impulso
- Detecção de pouso baseada em velocidade
- Sistema de gerenciamento de combustível
- Controle de rotação ou direcional
- Zonas de pouso seguro

**Dificuldade:** Iniciante
**Preset:** Preset Iniciante

---

## Passo 1: Entender o Jogo

### Mecânicas do Jogo
1. O módulo é puxado para baixo pela gravidade
2. Pressionar CIMA aplica impulso para cima (usa combustível)
3. ESQUERDA/DIREITA controla rotação ou movimento
4. Pouse suavemente na plataforma para vencer
5. Batida se você pousar muito rápido ou errar a plataforma
6. Sem combustível você não pode desacelerar!

### O Que Precisamos

| Elemento | Propósito |
|----------|-----------|
| **Módulo** | A nave que você controla |
| **Plataforma** | Zona segura para pousar |
| **Solo** | Terreno que causa batida |
| **Display Combustível** | Mostra combustível restante |
| **Display Velocidade** | Mostra velocidade atual |

---

## Passo 2: Criar os Sprites

### Sprites
- `spr_lander` (32x32 pixels) - nave espacial simples
- `spr_pad` (64x16 pixels) - plataforma de pouso
- `spr_ground` (32x32 pixels) - terreno rochoso
- `spr_flame` (16x16 pixels) - chama de propulsão (opcional)

---

## Passo 3-4: Criar Objetos de Solo e Plataforma

**obj_ground** e **obj_pad**: Definir sprite, marcar "Sólido"

---

## Passo 5: Criar o Objeto Módulo

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

### Colisão com obj_pad
```gml
var total_speed = sqrt(hsp*hsp + vsp*vsp);

if (total_speed <= safe_speed) {
    landed = true;
    hsp = 0;
    vsp = 0;
    show_message("Pouso Perfeito! Você Venceu!");
} else {
    crashed = true;
    show_message("Batida! Muito rápido!");
    room_restart();
}
```

### Colisão com obj_ground
```gml
crashed = true;
show_message("Batida no terreno!");
room_restart();
```

---

## Passo 6-7: Controlador do Jogo

**obj_game_controller** - Evento Draw: Mostrar combustível, velocidade, instruções

---

## Passo 8: Projete Seu Nível

1. Crie `room_game` (640x480)
2. Fundo preto (espaço)
3. Coloque solo embaixo com uma abertura
4. Coloque plataforma na abertura
5. Coloque módulo no topo
6. Coloque controlador do jogo

---

## O Que Você Aprendeu

- **Física de impulso** - Contrapor a gravidade
- **Gerenciamento de velocidade** - Controlar a velocidade
- **Sistema de combustível** - Gerenciamento de recursos
- **Detecção de colisões** - Resultados diferentes

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais
- [Tutorial: Platformer](Tutorial-Platformer_pt) - Criar um jogo de plataforma

