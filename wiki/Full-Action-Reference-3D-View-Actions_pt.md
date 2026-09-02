# Vista 3D

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Apply Gravity

| Propriedade | Valor |
|----------|-------|
| **Nome** | `apply_gravity` |
| **Ícone** | ⬇️ |
| **Categoria** | Vista 3D |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Parâmetros:* nenhum

### Break Block

| Propriedade | Valor |
|----------|-------|
| **Nome** | `break_block` |
| **Ícone** | ⛏️ |
| **Categoria** | Vista 3D |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `reach` | Número | `5` | How many cells ahead you can reach, in grid cells; opcional |

### Draw Block World HUD

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_block_world_hud` |
| **Ícone** | 🧰 |
| **Categoria** | Vista 3D |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `slot_size` | Número | `40` | Width and height of each hotbar slot, in pixels; opcional |
| `gap` | Número | `6` | Space between hotbar slots, in pixels; opcional |
| `margin_bottom` | Número | `16` | Space between the hotbar and the bottom of the screen; opcional |
| `back_color` | Cor | `#202020` | Fill colour of an unselected slot; opcional |
| `selected_color` | Cor | `#ffd040` | Fill colour of the currently selected slot; opcional |
| `border_color` | Cor | `#ffffff` | Outline colour of every slot; opcional |
| `text_color` | Cor | `#ffffff` | Colour of each slot's block-type label; opcional |
| `crosshair_size` | Número | `12` | Width and height of the centre crosshair, in pixels; opcional |
| `crosshair_color` | Cor | `#ffffff` | Colour of the centre crosshair; opcional |

### Desenhar HUD DOOM

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_doom_hud` |
| **Ícone** | 🎯 |
| **Categoria** | Vista 3D |

Desenhar uma barra de status inferior no estilo DOOM (barra de saúde + número, pontuação, vidas, um contador de objetivo e um ícone de rosto que reage à saúde) sobre a vista raycast

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borda esquerda da barra, em pixels de tela |
| `y` | Número | `-1` | Borda superior da barra; um valor negativo a alinha automaticamente à parte inferior da janela, sob a vista reduzida; opcional |
| `width` | Número | `0` | Largura da barra (0 = largura total da janela); opcional |
| `height` | Número | `42` | Altura da barra; mantenha-a coerente com a faixa viewport_height reservada em enable_raycast_view; opcional |
| `back_color` | Cor | `#101010` | Painel de fundo da barra; opcional |
| `divider_color` | Cor | `#505050` | Borda superior e fundo da barra de saúde; opcional |
| `text_color` | Cor | `#ffffff` | Cor de todo o texto da barra; opcional |
| `health_label` | Texto | `Health` | opcional |
| `health_bar_width` | Número | `90` | opcional |
| `health_bar_height` | Número | `14` | opcional |
| `bar_color` | Cor | `#20c020` | Cor de preenchimento da barra de saúde; opcional |
| `face_sprite` | Sprite | — | Faixa horizontal de quadros de rosto, o mais saudável primeiro (vazio = sem ícone de rosto); opcional |
| `face_frames` | Número | `4` | Quantos quadros a faixa de rosto tem; a saúde é distribuída uniformemente entre eles; opcional |
| `score_label` | Texto | `Score: ` | opcional |
| `lives_sprite` | Sprite | — | Sprite desenhado uma vez por vida restante; opcional |
| `lives_scale` | Número | `1.0` | opcional |
| `objective_value` | Texto | `0` | Expressão mostrada após o rótulo de objetivo (associe sua própria variável de chave/missão); opcional |
| `objective_label` | Texto | `Keys: ` | opcional |

### Desenhar minimapa

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_minimap` |
| **Ícone** | 🗺️ |
| **Categoria** | Vista 3D |

Desenhar um minimapa orientado ao norte dos muros da sala raycast, com um marcador que mostra onde está a câmera e para onde ela olha

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Borda esquerda do minimapa, em pixels de tela |
| `y` | Número | `0` | Borda superior do minimapa, em pixels de tela |
| `size` | Número | `120` | Largura e altura do quadrado do minimapa, em pixels; opcional |
| `back_color` | Cor | `#101018` | Cor do painel atrás do mapa; opcional |
| `wall_color` | Cor | `#8080a0` | Cor das linhas dos muros; opcional |
| `player_color` | Cor | `#ffd040` | Cor do marcador da câmera e sua linha de direção; opcional |
| `mark_object` | Objeto | — | Also dot every instance of this object onto the map (blank = show walls and player only); opcional |
| `mark_color` | Cor | `#40e0ff` | Colour of the Mark Object dots; opcional |
| `mark_object_2` | Objeto | — | A second object to dot on, in its own colour; opcional |
| `mark_color_2` | Cor | `#ff5050` | Colour of the Mark Object 2 dots; opcional |

### Enable Block World View

| Propriedade | Valor |
|----------|-------|
| **Nome** | `enable_block_world_view` |
| **Ícone** | 🧱 |
| **Categoria** | Vista 3D |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `enable` | Sim/Não | Sim | On = first-person block view; off = normal top-down |
| `camera_object` | Objeto | — | Objeto cuja posição + ângulo de visão é a câmera (vazio = o objeto que executa esta ação); opcional |
| `z_layer` | Número | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); opcional |
| `fov` | Número | `66` | Campo de visão horizontal em graus; opcional |
| `render_distance` | Número | `20` | Comprimento máximo do raio em células da grade; opcional |
| `cell_size` | Número | `32` | Grid cell size in pixels (match the block-placement grid); opcional |
| `columns` | Número | `320` | Colunas da tela para raycast (menos = mais rápido/mais grosseiro); opcional |
| `wall_color` | Cor | `#8a8a8a` | Flat colour used only if Textured Blocks is off; opcional |
| `floor_color` | Cor | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); opcional |
| `ceiling_color` | Cor | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); opcional |
| `pitch` | Número | `0` | Degrees to look up (+) or down (-); 0 is level; opcional |
| `wall_textured` | Sim/Não | Sim | Off forces flat block colours even though real textures are available; opcional |
| `top_cast_res` | Número | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); opcional |
| `eye_height` | Número | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); opcional |
| `gravity` | Número | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; opcional |
| `inventory` | Sim/Não | Não | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; opcional |
| `generate` | Sim/Não | Não | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; opcional |
| `seed` | Número | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; opcional |

### Ativar vista Raycast

| Propriedade | Valor |
|----------|-------|
| **Nome** | `enable_raycast_view` |
| **Ícone** | 🕹️ |
| **Categoria** | Vista 3D |

Renderizar a sala como uma vista 3D em primeira pessoa no estilo Doom/Wolfenstein (muros, céu, chão) em vez da vista de cima

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `enable` | Sim/Não | Sim | Ativado = vista raycast em primeira pessoa; desativado = vista de cima normal |
| `camera_object` | Objeto | — | Objeto cuja posição + ângulo de visão é a câmera (vazio = o objeto que executa esta ação); opcional |
| `fov` | Número | `66` | Campo de visão horizontal em graus; opcional |
| `render_distance` | Número | `20` | Comprimento máximo do raio em células da grade; opcional |
| `cell_size` | Número | `32` | Tamanho da célula da grade em pixels (corresponde à grade de posicionamento dos muros); opcional |
| `columns` | Número | `320` | Colunas da tela para raycast (menos = mais rápido/mais grosseiro); opcional |
| `wall_color` | Cor | `#993333` | Cor uniforme dos muros quando não há textura de muro; opcional |
| `floor_color` | Cor | `#464632` | Cor uniforme do chão quando não há textura de chão; opcional |
| `ceiling_color` | Cor | `#87CEEB` | Cor uniforme do teto quando não há textura de céu/teto; opcional |
| `wall_texture` | Sprite | — | Sprite para texturizar cada muro (vazio = cor uniforme); opcional |
| `sky_texture` | Sprite | — | Sprite para um céu panorâmico sobre o teto (vazio = uniforme); opcional |
| `floor_texture` | Sprite | — | Sprite projetado no chão (vazio = cor uniforme); opcional |
| `ceiling_texture` | Sprite | — | Sprite projetado no teto quando não há céu; opcional |
| `wall_textured` | Sim/Não | Sim | Desativado força cores uniformes dos muros mesmo quando há uma textura; opcional |
| `floor_cast_res` | Número | `4` | Subamostragem do chão projetado (maior = mais rápido + mais grosseiro); opcional |
| `viewport_height` | Número | `0` | Reduz a vista 3D para esta altura em pixels (letterbox), reservando a faixa inferior para uma barra de status no estilo DOOM (0 = altura total da janela, inalterado); opcional |

### Jump

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump` |
| **Ícone** | ⬆️ |
| **Categoria** | Vista 3D |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0.35` | Initial upward velocity, in cells/step; opcional |

### Load Block World

| Propriedade | Valor |
|----------|-------|
| **Nome** | `load_block_world` |
| **Ícone** | 📂 |
| **Categoria** | Vista 3D |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `data_file` | Texto | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_look_pitch` |
| **Ícone** | 🔭 |
| **Categoria** | Vista 3D |

Tilt the block-world view up or down

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `pitch` | Número | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Sim/Não | Não | On = add to the current angle, for a look control you can hold down; off = set it outright; opcional |

### Move And Collide

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_and_collide` |
| **Ícone** | 🚶 |
| **Categoria** | Vista 3D |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `dx` | Número | `0` | How far to move on x this step, in pixels |
| `dy` | Número | `0` | How far to move on y this step, in pixels |
| `collide` | Sim/Não | Sim | Off ignores the block grid entirely (flying/debug); opcional |

### Place Block

| Propriedade | Valor |
|----------|-------|
| **Nome** | `place_block` |
| **Ícone** | 🧱 |
| **Categoria** | Vista 3D |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `block` | Escolha | `stone` | Which kind of block to place; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Número | `5` | How many cells ahead you can build, in grid cells; opcional |

### Select Hotbar Slot

| Propriedade | Valor |
|----------|-------|
| **Nome** | `select_hotbar_slot` |
| **Ícone** | 🔢 |
| **Categoria** | Vista 3D |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `index` | Número | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Sim/Não | Não | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; opcional |

### Set Block Protection

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_block_protection` |
| **Ícone** | 🔒 |
| **Categoria** | Vista 3D |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `block_type` | Escolha | `diamond_block` | Which block type becomes protected; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Escolha | `gold_block` | Which block type must be in inventory to break it; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_block_reward` |
| **Ícone** | 💎 |
| **Categoria** | Vista 3D |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `block_type` | Escolha | `diamond_block` | Which block type awards score when broken; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Número | `10` | Score awarded per block of this type broken |

### Definir ângulo de visão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_facing_angle` |
| **Ícone** | 🧭 |
| **Categoria** | Vista 3D |

Definir a direção do olhar da instância para uma câmera raycast (em primeira pessoa) — independente da velocidade de movimento

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `angle` | Número | `0` | Graus (0=direita, 90=cima, 180=esquerda, 270=baixo) |
| `relative` | Sim/Não | Não | Somar ao ângulo de visão atual em vez de substituí-lo; opcional |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Particles](Full-Action-Reference-Particles_pt) (8)
- [Réseau](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
