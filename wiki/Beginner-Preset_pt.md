# Preset Iniciante

*[Início](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Preset Intermediário](Intermediate-Preset_pt)*

> **Gerado automaticamente** a partir de `get_beginner()` em `config/blockly_config.py` por `tools/gen_preset_docs.py` — não edite manualmente; execute o gerador novamente após alterar o preset.

> **O que este preset realmente restringe:** este preset filtra TANTO a paleta de blocos visuais Blockly QUANTO os menus "Adicionar Evento"/"Adicionar Ação" do painel estruturado Eventos/Ações — qualquer editor que você use, só aparecem os eventos/ações listados abaixo. O preset de um *projeto* é definido de duas formas: **`Preferências > IDE Edition`** escolhe o padrão para *novos* projetos (edição Iniciante -> este preset; projetos existentes nunca são alterados ao trocar de edição), e **`Ferramentas > Configurar Blocos de Ação...`** altera o preset do projeto *atualmente aberto* a qualquer momento. A edição padrão do IDE é Iniciante, então novos projetos de uma instalação limpa começam exatamente nesta lista.

## Visão Geral

Este preset habilita **19** tipos de eventos e **54** tipos de ações.

---

## Eventos

| Evento | Nome do Bloco | Categoria | Descrição |
|-------|------------|----------|-------------|
| Create | `create` | Objeto | Executado uma vez quando a instância é criada pela primeira vez |
| Step | `step` | Objeto | Executado a cada quadro (use para verificações contínuas) |
| Keyboard (held) | `keyboard` | Entrada | Executado continuamente enquanto uma tecla é mantida pressionada (para movimento suave) |
| Keyboard <No Key> | `keyboard_no_key` | Entrada | Executado quando nenhuma tecla está pressionada no momento |
| Collision With... | `collision` | Colisão | Executado ao colidir com outro objeto |
| Begin Step | `begin_step` | Passo | Executado no início de cada passo, antes dos outros eventos |
| End Step | `end_step` | Passo | Executado no final de cada passo, após as colisões mas antes do desenho |
| Alarm | `alarm` | Tempo | Executado quando um alarme chega a zero |
| Draw | `draw` | Desenho | Executado ao desenhar o objeto (substitui o desenho automático do sprite) |
| Draw GUI | `draw_gui` | Desenho | Desenhado por cima de tudo o resto (não afetado pela câmera/vista). Use para HUD, pontuação, vidas. |
| Room End | `room_end` | Sala | Executado quando a sala termina |
| Room Start | `room_start` | Sala | Executado quando a sala começa (após os eventos Create) |
| Game End | `game_end` | Jogo | Executado quando o jogo termina |
| Game Start | `game_start` | Jogo | Executado quando o jogo começa (apenas na primeira sala) |
| Animation End | `animation_end` | Outro | Disparado quando a animação do sprite chega ao último quadro e reinicia |
| Intersect Boundary | `intersect_boundary` | Outro | Executado quando a instância toca a borda da sala |
| No More Health | `no_more_health` | Outro | Executado quando a saúde chega a 0 ou menos |
| No More Lives | `no_more_lives` | Outro | Executado quando as vidas chegam a 0 ou menos |
| Outside Room | `outside_room` | Outro | Executado quando a instância está completamente fora da sala |

---

## Ações

### Movimento

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Quicar | `bounce` | — |
| Saltar para posição | `jump_to_position` | `x`, `y`, `relative` |
| Saltar para a posição inicial | `jump_to_start` | — |
| Mover até o contato | `move_to_contact` | `direction`, `max_distance`, `object` |
| Inverter horizontal | `reverse_horizontal` | — |
| Inverter vertical | `reverse_vertical` | — |
| Definir direção e velocidade | `set_direction_speed` | `direction`, `speed` |
| Definir gravidade | `set_gravity` | `direction`, `gravity` |
| Definir velocidade horizontal | `set_hspeed` | `speed` |
| Definir velocidade vertical | `set_vspeed` | `speed` |
| Começar a mover (direção) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Parar movimento | `stop_movement` | — |

### Grade

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Testar alinhamento à grade | `test_alignment` | `hsnap`, `vsnap` |

### Instância

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Mudar instância | `change_instance` | `object`, `perform_events` |
| Criar instância | `create_instance` | `object`, `x`, `y`, `relative` |
| Destruir instância | `destroy_instance` | — |
| Destruir na posição | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Testar número de instâncias | `test_instance_count` | `object`, `number`, `operation` |

### Pontuação

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Desenhar vidas | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Desenhar pontuação | `draw_score` | `x`, `y`, `caption`, `relative` |
| Definir vidas | `set_lives` | `value`, `relative` |
| Definir pontuação | `set_score` | `value`, `relative` |
| Mostrar tabela de recordes | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |

### Tempo

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Definir alarme | `set_alarm` | `alarm_number`, `steps` |
| Pausa | `sleep` | `milliseconds` |

### Sala

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Encerrar jogo | `game_end` | — |
| Se existe sala seguinte | `if_next_room_exists` | `then_actions`, `else_actions` |
| Se existe sala anterior | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Reiniciar sala | `restart_room` | — |
| Definir fundo | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |

### Áudio

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Verificar reprodução de som | `check_sound` | `sound`, `not_flag` |
| Reproduzir música | `play_music` | `music`, `loop`, `volume` |
| Reproduzir som | `play_sound` | `sound`, `volume` |
| Definir volume | `set_volume` | `volume` |
| Parar música | `stop_music` | — |
| Parar som | `stop_sound` | `sound` |

### Jogo

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Desenhar texto | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Reiniciar jogo | `restart_game` | — |
| Definir cor de desenho | `set_draw_color` | `color` |
| Definir título da janela | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Mostrar mensagem | `show_message` | `message` |

### Controle

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Verificar se vazio | `check_empty` | `x`, `y`, `relative`, `objects` |
| Comentário | `comment` | `text` |
| Senão | `else_action` | — |
| Fim de bloco | `end_block` | — |
| Executar código | `execute_code` | `code` |
| Executar script | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Sair do evento | `exit_event` | — |
| Se colisão | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Se o objeto existe | `if_object_exists` | `object`, `not_flag` |
| Início de bloco | `start_block` | — |
| Testar probabilidade | `test_chance` | `sides` |
| Testar expressão | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Testar variável | `test_variable` | `variable`, `value`, `scope`, `operation` |

---

## Veja Também

- [Guia de Presets](Preset-Guide_pt) — o que são presets e como alterar um
- [Referência de Eventos](Event-Reference_pt) — descrição completa de cada evento
- [Referência Completa de Ações](Full-Action-Reference_pt) — detalhes completos de parâmetros de cada ação
- [Preset Intermediário](Intermediate-Preset_pt) — o próximo nível
