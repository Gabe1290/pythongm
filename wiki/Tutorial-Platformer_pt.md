# Tutorial: Criar um Jogo de Plataforma

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introdução

Neste tutorial, você criará um **Jogo de Plataforma** - um jogo de ação de rolagem lateral onde o jogador corre, pula e navega por plataformas enquanto evita perigos e coleta moedas. Este gênero clássico é perfeito para aprender gravidade, mecânicas de pulo e colisão com plataformas.

**O que você aprenderá:**
- Gravidade e física de queda
- Mecânicas de pulo com detecção de chão
- Colisão com plataformas (aterrissar em cima)
- Movimento esquerda/direita
- Colecionáveis e perigos

**Dificuldade:** Iniciante
**Preset:** Preset Iniciante

---

## Passo 1: Entender o Jogo

### Mecânicas do Jogo
1. O jogador é afetado pela gravidade e cai
2. O jogador pode se mover para esquerda e direita
3. O jogador pode pular quando está no chão
4. Plataformas impedem o jogador de cair através
5. Colete moedas para pontos
6. Alcance a bandeira para completar o nível

### O Que Precisamos

| Elemento | Propósito |
|----------|-----------|
| **Jogador** | O personagem que você controla |
| **Chão/Plataforma** | Superfícies sólidas para ficar em pé |
| **Moeda** | Itens colecionáveis para pontuação |
| **Espinho** | Perigo que machuca o jogador |
| **Bandeira** | Meta que termina o nível |

---

## Passo 2: Criar os Sprites

### 2.1 Sprite do Jogador
- Nome: `spr_player`
- Desenhe um personagem simples
- Tamanho: 32x48 pixels

### 2.2 Sprite do Chão
- Nome: `spr_ground`
- Desenhe um bloco de grama/terra
- Tamanho: 32x32 pixels

### 2.3 Sprite da Plataforma
- Nome: `spr_platform`
- Desenhe uma plataforma flutuante
- Tamanho: 64x16 pixels

### 2.4 Sprite da Moeda
- Nome: `spr_coin`
- Pequeno círculo amarelo/dourado
- Tamanho: 16x16 pixels

### 2.5 Sprite do Espinho
- Nome: `spr_spike`
- Triângulos apontando para cima
- Tamanho: 32x32 pixels

### 2.6 Sprite da Bandeira
- Nome: `spr_flag`
- Bandeira em um mastro
- Tamanho: 32x64 pixels

---

## Passo 3-4: Criar Objetos de Chão e Plataforma

**obj_ground** e **obj_platform**: Defina sprite, marque "Sólido"

---

## Passo 5: Criar o Objeto Jogador

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

## Passo 6-8: Colecionáveis e Perigos

**obj_coin** - Colisão com obj_player: Pontuação +10, destruir Self

**obj_spike** - Colisão com obj_player: Mostrar mensagem, reiniciar room

**obj_flag** - Colisão com obj_player: Mostrar mensagem, próxima room

---

## Passo 9: Projete Seu Nível

1. Crie `room_level1` (800x480)
2. Ative ajuste à grade (32x32)
3. Coloque chão embaixo, plataformas no ar
4. Adicione moedas, espinhos
5. Coloque bandeira no final, jogador no início

---

## O Que Você Aprendeu

- **Física de gravidade** - Força constante para baixo
- **Mecânicas de pulo** - Velocidade vertical negativa
- **Detecção de chão** - Usar `place_meeting`
- **Tratamento de colisões** - Mover pixel por pixel

---

## Veja Também

- [Tutoriais](Tutorials_pt) - Mais tutoriais de jogos
- [Tutorial: Labirinto](Tutorial-Maze_pt) - Criar um jogo de labirinto
