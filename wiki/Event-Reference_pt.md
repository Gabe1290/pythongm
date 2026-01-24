# Referencia de Eventos

*[Inicio](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Referencia Completa de Acoes](Full-Action-Reference_pt)*

Esta pagina documenta todos os eventos disponiveis no PyGameMaker. Eventos sao gatilhos que executam acoes quando condicoes especificas ocorrem no seu jogo.

## Categorias de Eventos

- [Eventos de Objeto](#eventos-de-objeto) - Create, Step, Destroy
- [Eventos de Entrada](#eventos-de-entrada) - Teclado, Mouse
- [Eventos de Colisao](#eventos-de-colisao) - Colisoes de objetos
- [Eventos de Tempo](#eventos-de-tempo) - Alarmes, Variantes de Step
- [Eventos de Desenho](#eventos-de-desenho) - Renderizacao personalizada
- [Eventos de Sala](#eventos-de-sala) - Transicoes de sala
- [Eventos de Jogo](#eventos-de-jogo) - Inicio/Fim do jogo
- [Outros Eventos](#outros-eventos) - Limites, Vidas, Saude

---

## Eventos de Objeto

### Create
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `create` |
| **Icone** | 🎯 |
| **Categoria** | Objeto |
| **Preset** | Iniciante |

**Descricao:** Executado uma vez quando uma instancia e criada pela primeira vez.

**Quando dispara:**
- Quando uma instancia e colocada em uma sala no inicio do jogo
- Quando criada via acao "Criar Instancia"
- Apos transicoes de sala para novas instancias

**Usos comuns:**
- Inicializar variaveis
- Definir valores iniciais
- Configurar estado inicial

---

### Step
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `step` |
| **Icone** | ⭐ |
| **Categoria** | Objeto |
| **Preset** | Iniciante |

**Descricao:** Executado a cada quadro (tipicamente 60 vezes por segundo).

**Quando dispara:** Continuamente, a cada quadro do jogo.

**Usos comuns:**
- Movimento continuo
- Verificar condicoes
- Atualizar posicoes
- Logica do jogo

**Nota:** Cuidado com o desempenho - o codigo aqui executa constantemente.

---

### Destroy
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `destroy` |
| **Icone** | 💥 |
| **Categoria** | Objeto |
| **Preset** | Intermediario |

**Descricao:** Executado quando uma instancia e destruida.

**Quando dispara:** Logo antes da instancia ser removida do jogo.

**Usos comuns:**
- Gerar efeitos (explosoes, particulas)
- Soltar itens
- Atualizar pontuacoes
- Tocar sons

---

## Eventos de Entrada

### Teclado (Continuo)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard` |
| **Icone** | ⌨️ |
| **Categoria** | Entrada |
| **Preset** | Iniciante |

**Descricao:** Dispara continuamente enquanto uma tecla esta pressionada.

**Ideal para:** Movimento suave e continuo

**Teclas Suportadas:**
- Teclas de seta (cima, baixo, esquerda, direita)
- Letras (A-Z)
- Numeros (0-9)
- Espaco, Enter, Escape
- Teclas de funcao (F1-F12)
- Teclas modificadoras (Shift, Ctrl, Alt)

---

### Pressionar Teclado
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_press` |
| **Icone** | 🔘 |
| **Categoria** | Entrada |
| **Preset** | Iniciante |

**Descricao:** Dispara uma vez quando uma tecla e pressionada pela primeira vez.

**Ideal para:** Acoes unicas (pular, atirar, selecionar no menu)

**Diferenca do Teclado:** So dispara uma vez por pressionamento, nao enquanto mantido.

---

### Soltar Teclado
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_release` |
| **Icone** | ⬆️ |
| **Categoria** | Entrada |
| **Preset** | Avancado |

**Descricao:** Dispara uma vez quando uma tecla e solta.

**Usos comuns:**
- Parar movimento quando tecla e solta
- Terminar ataques carregados
- Alternar estados

---

### Mouse
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `mouse` |
| **Icone** | 🖱️ |
| **Categoria** | Entrada |
| **Preset** | Intermediario |

**Descricao:** Eventos de botao do mouse e movimento.

**Tipos de Eventos:**

| Tipo | Descricao |
|------|-----------|
| Botao Esquerdo | Clique com botao esquerdo do mouse |
| Botao Direito | Clique com botao direito do mouse |
| Botao do Meio | Clique com botao do meio/scroll |
| Entrada do Mouse | Cursor entra nos limites da instancia |
| Saida do Mouse | Cursor sai dos limites da instancia |
| Botao Esquerdo Global | Clique esquerdo em qualquer lugar |
| Botao Direito Global | Clique direito em qualquer lugar |

---

## Eventos de Colisao

### Colisao
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `collision` |
| **Icone** | 💥 |
| **Categoria** | Colisao |
| **Preset** | Iniciante |

**Descricao:** Dispara quando esta instancia se sobrepoe com outro tipo de objeto.

**Configuracao:** Selecione qual tipo de objeto dispara esta colisao.

**Variavel especial:** `other` - Referencia a instancia em colisao.

**Quando dispara:** A cada quadro em que as instancias se sobrepoem.

**Usos comuns:**
- Coletar itens
- Receber dano
- Bater em paredes
- Disparar eventos

**Exemplos de eventos de colisao:**
- `collision_with_obj_coin` - Jogador toca uma moeda
- `collision_with_obj_enemy` - Jogador toca um inimigo
- `collision_with_obj_wall` - Instancia bate em uma parede

---

## Eventos de Tempo

### Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `alarm` |
| **Icone** | ⏰ |
| **Categoria** | Tempo |
| **Preset** | Intermediario |

**Descricao:** Dispara quando uma contagem regressiva de alarme chega a zero.

**Alarmes disponiveis:** 12 alarmes independentes (alarm[0] ate alarm[11])

**Configurar alarmes:** Use a acao "Definir Alarme" com passos (60 passos ≈ 1 segundo a 60 FPS)

**Usos comuns:**
- Geracao temporizada
- Tempos de recarga
- Efeitos atrasados
- Acoes repetitivas (redefinir alarme no evento de alarme)

---

### Begin Step
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `begin_step` |
| **Icone** | ▶️ |
| **Categoria** | Step |
| **Preset** | Avancado |

**Descricao:** Dispara no inicio de cada quadro, antes dos eventos Step regulares.

**Ordem de execucao:** Begin Step → Step → End Step

**Usos comuns:**
- Processamento de entrada
- Calculos pre-movimento

---

### End Step
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `end_step` |
| **Icone** | ⏹️ |
| **Categoria** | Step |
| **Preset** | Avancado |

**Descricao:** Dispara no final de cada quadro, apos as colisoes.

**Usos comuns:**
- Ajustes finais de posicao
- Operacoes de limpeza
- Atualizacoes de estado apos colisoes

---

## Eventos de Desenho

### Draw
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw` |
| **Icone** | 🎨 |
| **Categoria** | Desenho |
| **Preset** | Intermediario |

**Descricao:** Dispara durante a fase de renderizacao.

**Importante:** Adicionar um evento Draw desabilita o desenho automatico do sprite. Voce deve desenhar o sprite manualmente se quiser que ele seja visivel.

**Usos comuns:**
- Renderizacao personalizada
- Desenhar formas
- Exibir texto
- Barras de saude
- Elementos de HUD

**Acoes de desenho disponiveis:**
- Desenhar Sprite
- Desenhar Texto
- Desenhar Retangulo
- Desenhar Circulo
- Desenhar Linha
- Desenhar Barra de Saude

---

## Eventos de Sala

### Room Start
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `room_start` |
| **Icone** | 🚪 |
| **Categoria** | Sala |
| **Preset** | Avancado |

**Descricao:** Dispara ao entrar em uma sala, apos todos os eventos Create.

**Usos comuns:**
- Inicializacao da sala
- Tocar musica da sala
- Definir variaveis especificas da sala

---

### Room End
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `room_end` |
| **Icone** | 🚪 |
| **Categoria** | Sala |
| **Preset** | Avancado |

**Descricao:** Dispara ao sair de uma sala.

**Usos comuns:**
- Salvar progresso
- Parar musica
- Limpeza

---

## Eventos de Jogo

### Game Start
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `game_start` |
| **Icone** | 🎮 |
| **Categoria** | Jogo |
| **Preset** | Avancado |

**Descricao:** Dispara uma vez quando o jogo inicia pela primeira vez (apenas na primeira sala).

**Usos comuns:**
- Inicializar variaveis globais
- Carregar dados salvos
- Tocar introducao

---

### Game End
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `game_end` |
| **Icone** | 🎮 |
| **Categoria** | Jogo |
| **Preset** | Avancado |

**Descricao:** Dispara quando o jogo esta terminando.

**Usos comuns:**
- Salvar dados do jogo
- Liberar recursos

---

## Outros Eventos

### Outside Room
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `outside_room` |
| **Icone** | 🚫 |
| **Categoria** | Outro |
| **Preset** | Avancado |

**Descricao:** Dispara quando a instancia esta completamente fora dos limites da sala.

**Usos comuns:**
- Destruir projeteis fora da tela
- Aparecer do outro lado
- Disparar game over

---

### Intersect Boundary
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `intersect_boundary` |
| **Icone** | ⚠️ |
| **Categoria** | Outro |
| **Preset** | Avancado |

**Descricao:** Dispara quando a instancia toca o limite da sala.

**Usos comuns:**
- Manter o jogador nos limites
- Quicar nas bordas

---

### No More Lives
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `no_more_lives` |
| **Icone** | 💀 |
| **Categoria** | Outro |
| **Preset** | Intermediario |

**Descricao:** Dispara quando as vidas chegam a 0 ou menos.

**Usos comuns:**
- Tela de game over
- Reiniciar jogo
- Mostrar pontuacao final

---

### No More Health
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `no_more_health` |
| **Icone** | 💔 |
| **Categoria** | Outro |
| **Preset** | Intermediario |

**Descricao:** Dispara quando a saude chega a 0 ou menos.

**Usos comuns:**
- Perder uma vida
- Reaparecer jogador
- Disparar animacao de morte

---

## Ordem de Execucao de Eventos

Entender quando os eventos disparam ajuda a criar um comportamento de jogo previsivel:

1. **Begin Step** - Inicio do quadro
2. **Alarm** - Qualquer alarme disparado
3. **Keyboard/Mouse** - Eventos de entrada
4. **Step** - Logica principal do jogo
5. **Collision** - Apos o movimento
6. **End Step** - Apos colisoes
7. **Draw** - Fase de renderizacao

---

## Eventos por Preset

| Preset | Eventos Incluidos |
|--------|-------------------|
| **Iniciante** | Create, Step, Keyboard Press, Collision |
| **Intermediario** | + Draw, Destroy, Mouse, Alarm |
| **Avancado** | + Todas as variantes de teclado, Begin/End Step, Eventos de sala, Eventos de jogo, Eventos de limite |

---

## Veja Tambem

- [Referencia Completa de Acoes](Full-Action-Reference_pt) - Lista completa de acoes
- [Preset Iniciante](Beginner-Preset_pt) - Eventos essenciais para iniciantes
- [Preset Intermediario](Intermediate-Preset_pt) - Eventos adicionais
- [Eventos e Acoes](Events-and-Actions_pt) - Visao geral dos conceitos basicos
