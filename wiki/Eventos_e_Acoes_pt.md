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
| **Passo** | A cada quadro (60 vezes por segundo) |
| **Início do passo** | Antes das verificações de colisão |
| **Fim do passo** | Depois de todos os outros eventos |

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
| **Fora da sala** | A instância está completamente fora da sala |
| **Toca a borda da sala** | A instância toca a borda da sala |
| **Início do jogo** | O jogo inicia (primeira sala carregada) |
| **Fim do jogo** | O jogo termina |
| **Início da sala** | Ao entrar numa sala |
| **Fim da sala** | Ao sair de uma sala |
| **Sem vidas** | As vidas chegam a 0 |
| **Sem saúde** | A saúde chega a 0 |
| **Fim da animação** | A animação do sprite é concluída |

### Eventos Draw

| Evento | Quando |
|-----------|-------|
| **Desenho** | Durante a fase de renderização |
| **Desenho da interface** | Depois de desenhar a sala (espaço de tela) |

---

## Referência de Ações

### Ações de Movimento

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Definir velocidade** | Define a velocidade de movimento | velocidade, relativo |
| **Definir direção** | Define a direção | direção (0-360), relativo |
| **Definir velocidade horizontal** | Define hspeed | hspeed, relativo |
| **Definir velocidade vertical** | Define vspeed | vspeed, relativo |
| **Definir gravidade** | Define a gravidade | gravity, direction |
| **Definir atrito** | Define o atrito | friction |
| **Mover para um ponto** | Move em direção a coordenadas | x, y, velocidade |
| **Começar a mover (direção)** | Move numa direção | direction, velocidade |
| **Saltar para posição** | Teletransporta para coordenadas | x, y, relativo |
| **Saltar para a posição inicial** | Retorna à posição de criação | - |
| **Saltar para posição aleatória** | Teletransporte para uma posição completamente aleatória (ambos os eixos; ajustável à grade) | snap_h, snap_v |
| **Quicar** | Ricocheteia em objetos sólidos | precise |

### Ações de Instância

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Criar instância** | Cria um novo objeto | object, x, y, relativo |
| **Criar instância em movimento** | Cria com velocidade | object, x, y, speed, direction |
| **Destruir instância** | Remove a instância | - |
| **Mudar instância** | Transforma em outro objeto | object, perform_events |

### Ações de Temporização

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Definir alarme** | Inicia uma contagem regressiva | alarm_number, steps |
| **Pausa** | Pausa a execução | milissegundos |

### Ações Score/Lives/Health

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Definir pontuação** | Altera a pontuação | value, relativo |
| **Definir vidas** | Altera as vidas | value, relativo |
| **Definir saúde** | Altera a saúde | value, relativo |
| **Desenhar pontuação** | Mostra a pontuação | x, y, caption |
| **Desenhar vidas** | Mostra as vidas como imagens de sprite repetidas | x, y, sprite, scale, tiled |
| **Desenhar barra de saúde** | Mostra a saúde como barra de duas cores | x1, y1, x2, y2, back_color, bar_color |

### Ações de Desenho

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Desenhar sprite** | Desenha um sprite | sprite, x, y, subimage |
| **Desenhar texto** | Mostra texto | x, y, text |
| **Desenhar retângulo** | Desenha um retângulo | x1, y1, x2, y2, filled |
| **Desenhar círculo** | Desenha um círculo | x, y, radius, filled |
| **Desenhar linha** | Desenha uma linha | x1, y1, x2, y2 |
| **Definir cor de desenho** | Define a cor para os Draw Text/Draw Rectangle/etc. seguintes | color |
| **Definir cor** | Define a matiz e a transparência de um sprite (não a cor de desenho acima) | color, alpha |
| **Definir fonte de desenho** | Define fonte e alinhamento para o próximo desenho de texto | font, halign, valign |

### Ações de Sala

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Sala seguinte** | Vai para a próxima sala | transition |
| **Sala anterior** | Vai para a sala anterior | transition |
| **Reiniciar sala** | Reinicia a sala | - |
| **Ir para a sala** | Salta para uma sala específica | room, transition |
| **Se existe sala seguinte** | Verifica se existe uma próxima sala | - |
| **Se existe sala anterior** | Verifica se existe uma sala anterior | - |

### Ações Sound

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Reproduzir som** | Reproduz um efeito sonoro | sound, loop |
| **Parar som** | Para um som | sound |
| **Verificar reprodução de som** | Verifica se um som está a ser reproduzido | sound |
| **Reproduzir música** | Reproduz música de fundo | music, loop |
| **Parar música** | Para toda a música | - |

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
| **Início de bloco** | Inicia um grupo de ações | - |
| **Fim de bloco** | Termina um grupo de ações | - |
| **Repetir** | Repete N vezes | count |
| **Sair do evento** | Interrompe o evento atual | - |

### Outras Ações

| Ação | Descrição | Parâmetros |
|--------|-------------|------------|
| **Mostrar mensagem** | Mostra uma mensagem pop-up | message |
| **Reiniciar jogo** | Reinicia o jogo | - |
| **Encerrar jogo** | Fecha o jogo | - |

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
