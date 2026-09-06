# Vista 3D

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Aplicar gravidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `apply_gravity` |
| **Ícone** | ⬇️ |
| **Categoria** | Vista 3D |

Física contínua de queda e aterragem para a câmara do Block World: coloca-a no evento Passo (e não num evento de tecla mantida), para que corra em cada fotograma, haja ou não comando de movimento. Não faz nada enquanto o parâmetro Gravidade de «Ativar vista Block World» não for maior do que 0

*Parâmetros:* nenhum

### Quebrar bloco

| Propriedade | Valor |
|----------|-------|
| **Nome** | `break_block` |
| **Ícone** | ⛏️ |
| **Categoria** | Vista 3D |

Remove o bloco para onde a câmara aponta; também o recolhe para o inventário da instância que executa a ação se o inventário de «Ativar vista Block World» estiver ligado, e recusa-se a removê-lo se o bloco estiver protegido («Definir proteção de blocos») e a chave necessária não estiver no inventário

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `reach` | Número | `5` | Até onde alcanças à frente, em células da grelha; opcional |

### Desenhar HUD do Block World

| Propriedade | Valor |
|----------|-------|
| **Nome** | `draw_block_world_hud` |
| **Ícone** | 🧰 |
| **Categoria** | Vista 3D |

Desenha uma mira e uma barra de acesso rápido (com o espaço selecionado realçado e um contador em cada espaço quando o inventário está ligado): chama-a a partir do evento Desenhar do próprio objeto jogador ou câmara

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `slot_size` | Número | `40` | Largura e altura de cada espaço da barra, em píxeis; opcional |
| `gap` | Número | `6` | Espaçamento entre os espaços da barra, em píxeis; opcional |
| `margin_bottom` | Número | `16` | Espaço entre a barra e o fundo do ecrã; opcional |
| `back_color` | Cor | `#202020` | Cor de preenchimento de um espaço não selecionado; opcional |
| `selected_color` | Cor | `#ffd040` | Cor de preenchimento do espaço selecionado; opcional |
| `border_color` | Cor | `#ffffff` | Cor do contorno de todos os espaços; opcional |
| `text_color` | Cor | `#ffffff` | Cor da etiqueta de tipo de bloco em cada espaço; opcional |
| `crosshair_size` | Número | `12` | Largura e altura da mira central, em píxeis; opcional |
| `crosshair_color` | Cor | `#ffffff` | Cor da mira central; opcional |

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
| `mark_object` | Objeto | — | Marcar também no mapa, com um ponto, cada instância deste objeto (vazio = mostrar apenas paredes e jogador); opcional |
| `mark_color` | Cor | `#40e0ff` | Cor dos pontos de «Marcar objeto»; opcional |
| `mark_object_2` | Objeto | — | Um segundo objeto a marcar, com cor própria; opcional |
| `mark_color_2` | Cor | `#ff5050` | Cor dos pontos de «Marcar objeto 2»; opcional |

### Ativar vista Block World

| Propriedade | Valor |
|----------|-------|
| **Nome** | `enable_block_world_view` |
| **Ícone** | 🧱 |
| **Categoria** | Vista 3D |

Mostra a sala como uma vista de voxels na primeira pessoa (uma única camada) em vez da vista de cima

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `enable` | Sim/Não | Sim | Ligado = vista de blocos na primeira pessoa; desligado = vista de cima normal |
| `camera_object` | Objeto | — | Objeto cuja posição + ângulo de visão é a câmera (vazio = o objeto que executa esta ação); opcional |
| `z_layer` | Número | `0` | Que camada do mundo é desenhada (a fase 2a desenha exatamente uma camada: ainda não se olha para cima nem para baixo); opcional |
| `fov` | Número | `66` | Campo de visão horizontal em graus; opcional |
| `render_distance` | Número | `20` | Comprimento máximo do raio em células da grade; opcional |
| `cell_size` | Número | `32` | Tamanho da célula da grelha, em píxeis (a condizer com a grelha onde os blocos são colocados); opcional |
| `columns` | Número | `320` | Colunas da tela para raycast (menos = mais rápido/mais grosseiro); opcional |
| `wall_color` | Cor | `#8a8a8a` | Cor lisa, usada apenas se os blocos com textura estiverem desligados; opcional |
| `floor_color` | Cor | `#3a2f1c` | Cor lisa do chão (a fase 2a ainda não aplica textura ao chão); opcional |
| `ceiling_color` | Cor | `#87CEEB` | Cor lisa do teto ou céu (a fase 2a ainda não tem céu); opcional |
| `pitch` | Número | `0` | Graus para olhar para cima (+) ou para baixo (−); 0 é a horizontal; opcional |
| `wall_textured` | Sim/Não | Sim | Desligado impõe cores lisas nos blocos, mesmo havendo texturas verdadeiras disponíveis; opcional |
| `top_cast_res` | Número | `4` | Detalhe da textura das faces de cima e de baixo: linhas amostradas por cada N linhas do ecrã (mais alto = mais rápido e mais grosseiro, 0 = cor média lisa em vez de textura); opcional |
| `eye_height` | Número | `1.5` | Altura da câmara acima da camada em que assenta, em células (1,5 = um corpo com dois blocos de altura, necessário para ver o topo de um bloco da tua própria camada e subir para cima dele); opcional |
| `gravity` | Número | `0` | Aceleração para baixo, em células/passo², para a ação «Saltar» e para a gravidade e as quedas (nível 7a). 0 (por omissão) mantém o apoio instantâneo original de «Mover com colisão», sem saltos; um valor típico anda à volta de 0,04; opcional |
| `inventory` | Sim/Não | Não | Ligado = «Quebrar bloco» recolhe o que parte e «Colocar bloco» gasta desse inventário (nível 7c); desligado (por omissão) = colocação ilimitada, ao estilo do modo criativo, tal como antes do nível 7c; opcional |
| `generate` | Sim/Não | Não | Ligado = gera por procedimento um terreno ondulado à volta da câmara à medida que ela explora (nível 7e), usando a Semente abaixo; desligado (por omissão) = só existem os blocos colocados à mão ou carregados, tal como antes do nível 7e; opcional |
| `seed` | Número | `0` | Semente do mundo para «Gerar terreno»: a mesma semente produz sempre o mesmo terreno nesta plataforma. É ignorada se «Gerar terreno» estiver desligado; opcional |

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

### Saltar

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump` |
| **Ícone** | ⬆️ |
| **Categoria** | Vista 3D |

Dá à câmara do Block World velocidade para cima, apenas quando está assente em chão sólido (sem duplo salto nem salto no ar). Precisa da Gravidade configurada («Ativar vista Block World») e de «Aplicar gravidade» no evento Passo, senão nada a faz descer

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0.35` | Velocidade inicial para cima, em células por passo; opcional |

### Carregar Block World

| Propriedade | Valor |
|----------|-------|
| **Nome** | `load_block_world` |
| **Ícone** | 📂 |
| **Categoria** | Vista 3D |

Carrega um mundo já preparado (blocos colocados por um gerador ou escritos à mão) na sala atual, substituindo os blocos que lá estiverem

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `data_file` | Texto | — | Caminho para um ficheiro JSON de mundo de blocos, relativo à pasta do projeto (por ex. blocks/room1.json) |

### Olhar para cima / baixo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_look_pitch` |
| **Ícone** | 🔭 |
| **Categoria** | Vista 3D |

Inclina a vista do Block World para cima ou para baixo

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `pitch` | Número | `0` | Graus para olhar para cima (+) ou para baixo (−); 0 é a horizontal |
| `relative` | Sim/Não | Não | Ligado = somar ao ângulo atual, para um comando de olhar que se mantém carregado; desligado = defini-lo diretamente; opcional |

### Mover com colisão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_and_collide` |
| **Ícone** | 🚶 |
| **Categoria** | Vista 3D |

Move um passo, verificando a grelha de blocos, com apoio automático (sobe um bloco, desce qualquer altura): o z_layer da câmara acompanha se esta for a câmara do Block World

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `dx` | Número | `0` | Quanto se move em x neste passo, em píxeis |
| `dy` | Número | `0` | Quanto se move em y neste passo, em píxeis |
| `collide` | Sim/Não | Sim | Desligado ignora por completo a grelha de blocos (voo / depuração); opcional |

### Colocar bloco

| Propriedade | Valor |
|----------|-------|
| **Nome** | `place_block` |
| **Ícone** | 🧱 |
| **Categoria** | Vista 3D |

Põe um bloco na célula vazia para onde a câmara aponta: sem limite, a não ser que o inventário de «Ativar vista Block World» esteja ligado, caso em que usa aquilo que «Quebrar bloco» recolheu

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `block` | Escolha | `stone` | Que tipo de bloco colocar; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Número | `5` | Até onde podes construir à frente, em células da grelha; opcional |

### Escolher espaço da barra

| Propriedade | Valor |
|----------|-------|
| **Nome** | `select_hotbar_slot` |
| **Ícone** | 🔢 |
| **Categoria** | Vista 3D |

Escolhe qual o bloco selecionado na barra de acesso rápido, com o qual «Colocar bloco» vai construir: para o usar, põe a expressão «hotbar_block» no parâmetro Bloco de «Colocar bloco»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `index` | Número | `0` | Índice do espaço na barra de acesso rápido, que dá a volta em ambas as pontas |
| `relative` | Sim/Não | Não | Ligado = somar ao espaço atual, para percorrer com [ ] ou com a roda do rato; desligado = ir diretamente para ele; opcional |

### Definir proteção de blocos

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_block_protection` |
| **Ícone** | 🔒 |
| **Categoria** | Vista 3D |

Exige um tipo de bloco específico no inventário antes de «Quebrar bloco» poder remover um tipo de bloco escolhido: chama-a uma vez por cada tipo protegido; precisa do inventário de «Ativar vista Block World» ligado, senão a condição nunca poderá ser satisfeita

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `block_type` | Escolha | `diamond_block` | Que tipo de bloco fica protegido; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Escolha | `gold_block` | Que tipo de bloco tem de estar no inventário para o poder partir; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Definir recompensa do bloco

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_block_reward` |
| **Ícone** | 💎 |
| **Categoria** | Vista 3D |

Atribui pontos quando «Quebrar bloco» remove com sucesso um tipo de bloco escolhido: chama-a uma vez por cada tipo recompensado (por ex. no evento Criar da sala, logo a seguir a «Ativar vista Block World»). Um bloco de minério ou gema para extrair: coloca-o no terreno, regista a sua recompensa, e parti-lo atribui os pontos automaticamente

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `block_type` | Escolha | `diamond_block` | Que tipo de bloco dá pontos quando é partido; Opções: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Número | `10` | Pontos atribuídos por cada bloco deste tipo partido |

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
- [Rede](Full-Action-Reference-Network-Actions_pt) (15)
- [Partículas](Full-Action-Reference-Particles_pt) (8)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
