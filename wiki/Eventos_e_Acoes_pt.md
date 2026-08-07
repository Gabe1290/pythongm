# Eventos e Ações

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Voltar ao Início](Home_pt)

Esta é uma referência completa de todos os eventos e ações disponíveis no PyGameMaker.

---

## Referência de Eventos

### Evento Create
**Quando:** Uma vez, quando uma instância é criada
**Uso:** Inicialização, definir variáveis, iniciar temporizadores

### Evento Destroy
**Quando:** Quando a instância é destruída
**Uso:** Limpeza, gerar efeitos, atribuir pontos

### Eventos Step

| Evento | Quando |
|-----------|-------|
| **Step** | A cada quadro (60 vezes por segundo) |
| **Begin Step** | Antes das verificações de colisão |
| **End Step** | Depois de todos os outros eventos |

### Eventos Alarm

| Evento | Quando |
|-----------|-------|
| **Alarm[0-11]** | Quando o contador chega a 0 |

Use a ação `Set Alarm` para iniciar uma contagem regressiva. Os valores do alarme são em quadros (60 = 1 segundo a 60 FPS).

### Eventos de Teclado

| Evento | Quando |
|-----------|-------|
| **Keyboard [Tecla]** | Enquanto a tecla é mantida pressionada (repetido) |
| **Key Press [Tecla]** | Uma vez, quando a tecla é pressionada |
| **Key Release [Tecla]** | Uma vez, quando a tecla é solta |
| **No Key** | Quando nenhuma tecla está pressionada |

Teclas disponíveis: letras (A-Z), números (0-9), teclas de seta, barra de espaço, Enter, Shift, Ctrl, Alt, teclas de função (F1-F12)

### Eventos de Rato

| Evento | Quando |
|-----------|-------|
| **Left Button** | Clique com o botão esquerdo na instância |
| **Right Button** | Clique com o botão direito na instância |
| **Middle Button** | Clique com o botão do meio na instância |
| **Left Press** | Botão esquerdo pressionado (uma vez) |
| **Left Release** | Botão esquerdo solto (uma vez) |
| **Mouse Enter** | O cursor entra na instância |
| **Mouse Leave** | O cursor sai da instância |
| **Global Left Button** | Clique esquerdo em qualquer lugar |
| **Global Right Button** | Clique direito em qualquer lugar |

### Eventos de Colisão

| Evento | Quando |
|-----------|-------|
| **Collision with [Objeto]** | Ao tocar no objeto especificado |

As verificações de colisão ocorrem entre os eventos Step e Draw.

### Outros Eventos

| Evento | Quando |
|-----------|-------|
| **Outside Room** | A instância está completamente fora da sala |
| **Intersect Boundary** | A instância toca a borda da sala |
| **Game Start** | O jogo inicia (primeira sala carregada) |
| **Game End** | O jogo termina |
| **Room Start** | Ao entrar numa sala |
| **Room End** | Ao sair de uma sala |
| **No More Lives** | As vidas chegam a 0 |
| **No More Health** | A saúde chega a 0 |
| **Animation End** | A animação do sprite é concluída |

### Eventos Draw

| Evento | Quando |
|-----------|-------|
| **Draw** | Durante a fase de renderização |
| **Draw GUI** | Depois de desenhar a sala (espaço de tela) |

---

## Referência de Ações

### Ações de Movimento

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Definir velocidade** | Define a velocidade de movimento | velocidade, relativo |
| **Definir direção** | Define a direção | direção (0-360), relativo |
| **Set Horizontal Speed** | Define hspeed | hspeed, relativo |
| **Set Vertical Speed** | Define vspeed | vspeed, relativo |
| **Set Gravity** | Define a gravidade | gravity, direction |
| **Set Friction** | Define o atrito | friction |
| **Mover para um ponto** | Move em direção a coordenadas | x, y, velocidade |
| **Começar a mover (direção)** | Move numa direção | direction, velocidade |
| **Jump To Position** | Teletransporta para coordenadas | x, y, relativo |
| **Saltar para a posição inicial** | Retorna à posição de criação | - |
| **Saltar para posição aleatória** | Teletransporte para uma posição completamente aleatória (ambos os eixos; ajustável à grade) | snap_h, snap_v |
| **Quicar** | Ricocheteia em objetos sólidos | precise |

### Ações de Instância

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Create Instance** | Cria um novo objeto | object, x, y, relativo |
| **Create Moving Instance** | Cria com velocidade | object, x, y, speed, direction |
| **Destroy Instance** | Remove a instância | - |
| **Change Instance** | Transforma em outro objeto | object, perform_events |

### Ações de Temporização

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Set Alarm** | Inicia uma contagem regressiva | alarm_number, steps |
| **Sleep** | Pausa a execução | milissegundos |

### Ações Score/Lives/Health

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Set Score** | Altera a pontuação | value, relativo |
| **Set Lives** | Altera as vidas | value, relativo |
| **Set Health** | Altera a saúde | value, relativo |
| **Desenhar pontuação** | Mostra a pontuação | x, y, caption |
| **Desenhar vidas** | Mostra as vidas como imagens de sprite repetidas | x, y, sprite, scale, tiled |
| **Desenhar barra de saúde** | Mostra a saúde como barra de duas cores | x1, y1, x2, y2, back_color, bar_color |

### Ações de Desenho

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Draw Sprite** | Desenha um sprite | sprite, x, y, subimage |
| **Draw Text** | Mostra texto | x, y, text |
| **Draw Rectangle** | Desenha um retângulo | x1, y1, x2, y2, filled |
| **Draw Circle** | Desenha um círculo | x, y, radius, filled |
| **Draw Line** | Desenha uma linha | x1, y1, x2, y2 |
| **Definir cor de desenho** | Define a cor para os Draw Text/Draw Rectangle/etc. seguintes | color |
| **Definir cor** | Define a matiz e a transparência de um sprite (não a cor de desenho acima) | color, alpha |
| **Definir fonte de desenho** | Define fonte e alinhamento para o próximo desenho de texto | font, halign, valign |

### Ações de Sala

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Next Room** | Vai para a próxima sala | transition |
| **Previous Room** | Vai para a sala anterior | transition |
| **Restart Room** | Reinicia a sala | - |
| **Go to Room** | Salta para uma sala específica | room, transition |
| **If Next Room Exists** | Verifica se existe uma próxima sala | - |
| **If Previous Room Exists** | Verifica se existe uma sala anterior | - |

### Ações Sound

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Play Sound** | Reproduz um efeito sonoro | sound, loop |
| **Stop Sound** | Para um som | sound |
| **Check Sound Playing** | Verifica se um som está a ser reproduzido | sound |
| **Play Music** | Reproduz música de fundo | music, loop |
| **Stop Music** | Para toda a música | - |

### Ações de Variáveis

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Definir variável** | Atribui um valor | variable, value, relativo |
| **Testar variável** | Verifica um valor | variable, value, operation |
| **Desenhar variável** | Mostra uma variável | x, y, variable |

### Ações de Controlo de Fluxo

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Testar expressão** | Verificação condicional (uma expressão booleana Python) | expression |
| **Senão** | Ramo alternativo | - |
| **Start Block** | Inicia um grupo de ações | - |
| **End Block** | Termina um grupo de ações | - |
| **Repeat** | Repete N vezes | count |
| **Exit Event** | Interrompe o evento atual | - |

### Outras Ações

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Show Message** | Mostra uma mensagem pop-up | message |
| **Restart Game** | Reinicia o jogo | - |
| **End Game** | Fecha o jogo | - |

---

## Variáveis Integradas

Estas variáveis estão disponíveis para todas as instâncias:

| Variável | Descrição |
|----------|-------------|
| `x` | Posição horizontal |
| `y` | Posição vertical |
| `xstart` | Posição x inicial |
| `ystart` | Posição y inicial |
| `hspeed` | Velocidade horizontal |
| `vspeed` | Velocidade vertical |
| `speed` | Taxa de animação do sprite (quadros por segundo) — **não** a velocidade de movimento. Não existe uma variável integrada para a "velocidade total"; calcule-a você mesmo a partir de `hspeed`/`vspeed`, por ex. `(hspeed**2 + vspeed**2)**0.5` |
| `direction` | Direção de movimento (0-360) |
| `gravity` | Gravidade |
| `gravity_direction` | Direção da gravidade |
| `friction` | Atrito de movimento |
| `image_index` | Quadro de animação atual |
| `image_speed` | Velocidade de animação |
| `image_xscale` | Escala horizontal |
| `image_yscale` | Escala vertical |
| `image_angle` | Ângulo de rotação |
| `visible` | Se é desenhado |
| `solid` | Se é sólido para colisões |
| `depth` | Profundidade de desenho |
| `sprite_index` | Sprite atual |
| `alarm[0-11]` | Temporizadores de alarme |

### Variáveis Globais

| Variável | Descrição |
|----------|-------------|
| `score` | Pontuação do jogo |
| `lives` | Vidas do jogador |
| `health` | Saúde do jogador (0-100) |
| `room` | Sala atual |
| `room_width` | Largura da sala atual |
| `room_height` | Altura da sala atual |
| `mouse_x` | Posição X do rato |
| `mouse_y` | Posição Y do rato |

---

## Próximos Passos

- [[Programacao_Visual_pt]] - Use blocos Blockly para a mesma lógica
- [[Editor_Objetos_pt]] - Aplique eventos e ações a objetos
- [[Primeiro_Jogo_pt]] - Veja os eventos em ação
