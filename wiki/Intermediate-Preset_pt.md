# Preset Intermediário

*[Início](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Preset Iniciante](Beginner-Preset_pt)*

> **Gerado automaticamente** a partir de `get_intermediate()` em `config/blockly_config.py` por `tools/gen_preset_docs.py` — não edite manualmente; execute o gerador novamente após alterar o preset.

> **O que este preset realmente restringe:** este preset filtra TANTO a paleta de blocos visuais Blockly QUANTO os menus "Adicionar Evento"/"Adicionar Ação" do painel estruturado Eventos/Ações — qualquer editor que você use, só aparecem os eventos/ações listados abaixo. O preset de um *projeto* é definido de duas formas: **`Preferências > IDE Edition`** escolhe o padrão para *novos* projetos (edição Iniciante -> este preset; projetos existentes nunca são alterados ao trocar de edição), e **`Ferramentas > Configurar Blocos de Ação...`** altera o preset do projeto *atualmente aberto* a qualquer momento. A edição padrão do IDE é Iniciante, então novos projetos de uma instalação limpa começam exatamente nesta lista.

## Visão Geral

Este preset habilita **21** tipos de eventos e **94** tipos de ações.

---

## Eventos

| Evento | Nome do Bloco | Categoria | Descrição |
|-------|------------|----------|-------------|
| Create | `create` | Objeto | Executado uma vez quando a instância é criada pela primeira vez |
| Destroy | `destroy` | Objeto | Executado quando a instância é destruída |
| Step | `step` | Objeto | Executado a cada quadro (use para verificações contínuas) |
| Keyboard (held) | `keyboard` | Entrada | Executado continuamente enquanto uma tecla é mantida pressionada (para movimento suave) |
| Keyboard <No Key> | `keyboard_no_key` | Entrada | Executado quando nenhuma tecla está pressionada no momento |
| Keyboard Press | `keyboard_press` | Entrada | Executado uma vez quando uma tecla é pressionada pela primeira vez (para movimento baseado em grade) |
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
| Saltar para posição aleatória | `jump_to_random` | `snap_h`, `snap_v` |
| Saltar para a posição inicial | `jump_to_start` | — |
| Mover em direção a um ponto | `move_towards_point` | `x`, `y`, `speed` |
| Inverter horizontal | `reverse_horizontal` | — |
| Inverter vertical | `reverse_vertical` | — |
| Definir direção e velocidade | `set_direction_speed` | `direction`, `speed` |
| Definir atrito | `set_friction` | `friction` |
| Definir gravidade | `set_gravity` | `direction`, `gravity` |
| Definir velocidade horizontal | `set_hspeed` | `speed` |
| Definir velocidade vertical | `set_vspeed` | `speed` |
| Começar a mover (direção) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Parar movimento | `stop_movement` | — |

### Grade

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Se na grade | `if_on_grid` | `grid_size`, `then_actions`, `else_actions` |
| Ajustar à grade | `snap_to_grid` | `grid_size` |
| Testar alinhamento à grade | `test_alignment` | `hsnap`, `vsnap` |

### Instância

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Mudar instância | `change_instance` | `object`, `perform_events` |
| Criar instância | `create_instance` | `object`, `x`, `y`, `relative` |
| Criar instância em movimento | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Criar instância aleatória | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Destruir instância | `destroy_instance` | — |
| Destruir na posição | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Definir índice de imagem | `set_image_index` | `frame` |
| Definir velocidade de imagem | `set_image_speed` | `speed` |
| Definir sprite | `set_sprite` | `sprite`, `subimage`, `speed` |
| Iniciar animação | `start_animation` | — |
| Parar animação | `stop_animation` | — |
| Testar número de instâncias | `test_instance_count` | `object`, `number`, `operation` |

### Pontuação

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Limpar tabela de recordes | `clear_highscore` | — |
| Desenhar barra de saúde | `draw_health_bar` | `x1`, `y1`, `x2`, `y2`, `back_color`, `bar_color` |
| Desenhar vidas | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Desenhar pontuação | `draw_score` | `x`, `y`, `caption`, `relative` |
| Definir saúde | `set_health` | `value`, `relative` |
| Definir vidas | `set_lives` | `value`, `relative` |
| Definir pontuação | `set_score` | `value`, `relative` |
| Mostrar tabela de recordes | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Testar saúde | `test_health` | `operation`, `value` |
| Testar vidas | `test_lives` | `value`, `operation` |
| Testar pontuação | `test_score` | `value`, `operation` |

### Tempo

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Definir alarme | `set_alarm` | `alarm_number`, `steps` |
| Pausa | `sleep` | `milliseconds` |

### Sala

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Verificar sala | `check_room` | `room`, `not_flag` |
| Encerrar jogo | `game_end` | — |
| Ir para a sala | `goto_room` | `room`, `transition` |
| Se existe sala seguinte | `if_next_room_exists` | `then_actions`, `else_actions` |
| Se existe sala anterior | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Sala seguinte | `next_room` | — |
| Sala anterior | `previous_room` | — |
| Reiniciar sala | `restart_room` | — |
| Definir título da sala | `set_room_caption` | `caption` |

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
| Desenhar seta | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Desenhar fundo | `draw_background` | `background`, `x`, `y`, `tiled` |
| Desenhar elipse | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Desenhar linha | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Desenhar texto escalado | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Desenhar sprite | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Desenhar texto | `draw_text` | `text`, `x`, `y`, `relative` |
| Desenhar variável | `draw_variable` | `x`, `y`, `variable` |
| Preencher tela com cor | `fill_color` | `color` |
| Abrir página web | `open_webpage` | `url` |
| Reiniciar jogo | `restart_game` | — |
| Definir cor | `set_color` | `color`, `alpha` |
| Definir cor de desenho | `set_draw_color` | `color` |
| Definir fonte de desenho | `set_draw_font` | `font`, `halign`, `valign` |
| Definir título da janela | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Mostrar informações do jogo | `show_info` | — |
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
| Se pode empurrar | `if_can_push` | `direction`, `object_type`, `then_action`, `else_action` |
| Se colisão | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Se o objeto existe | `if_object_exists` | `object`, `not_flag` |
| Início de bloco | `start_block` | — |
| Testar probabilidade | `test_chance` | `sides` |
| Fazer uma pergunta | `test_question` | `question` |
| Testar variável | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Vistas

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Ativar vistas | `enable_views` | `enable` |
| Configurar vista | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### Vista 3D

| Ação | Nome do Bloco | Parâmetros |
|--------|------------|------------|
| Desenhar HUD DOOM | `draw_doom_hud` | `x`, `y`, `width`, `height`, `back_color`, `divider_color`, `text_color`, `health_label`, `health_bar_width`, `health_bar_height`, `bar_color`, `face_sprite`, `face_frames`, `score_label`, `lives_sprite`, `lives_scale`, `objective_value`, `objective_label` |
| Desenhar minimapa | `draw_minimap` | `x`, `y`, `size`, `back_color`, `wall_color`, `player_color` |
| Ativar vista Raycast | `enable_raycast_view` | `enable`, `camera_object`, `fov`, `render_distance`, `cell_size`, `columns`, `wall_color`, `floor_color`, `ceiling_color`, `wall_texture`, `sky_texture`, `floor_texture`, `ceiling_texture`, `wall_textured`, `floor_cast_res`, `viewport_height` |
| Definir ângulo de visão | `set_facing_angle` | `angle`, `relative` |

---

## Veja Também

- [Guia de Presets](Preset-Guide_pt) — o que são presets e como alterar um
- [Referência de Eventos](Event-Reference_pt) — descrição completa de cada evento
- [Referência Completa de Ações](Full-Action-Reference_pt) — detalhes completos de parâmetros de cada ação
- [Preset Iniciante](Beginner-Preset_pt) — o nível abaixo deste
