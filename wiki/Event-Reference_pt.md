# Referência de Eventos

*[Início](Home_pt) | [Guia de Presets](Preset-Guide_pt) | [Referência Completa de Ações](Full-Action-Reference_pt)*

Esta página documenta todos os eventos disponíveis no PyGameMaker. Eventos são gatilhos que executam ações quando condições específicas ocorrem no seu jogo.

## Categorias de Eventos

- [Eventos de Objeto](#eventos-de-objeto) - Create, Step, Destroy
- [Eventos de Entrada](#eventos-de-entrada) - Teclado, Mouse
- [Eventos de Colisão](#eventos-de-colisão) - Colisões de objetos
- [Eventos de Tempo](#eventos-de-tempo) - Alarmes, Variantes de Step
- [Eventos de Desenho](#eventos-de-desenho) - Renderização personalizada
- [Eventos de Sala](#eventos-de-sala) - Transições de sala
- [Eventos de Jogo](#eventos-de-jogo) - Início/Fim do jogo
- [Outros Eventos](#outros-eventos) - Limites, Vidas, Saúde

---

## Eventos de Objeto

### Create
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `create` |
| **Ícone** | 🎯 |
| **Categoria** | Objeto |
| **Preset** | Iniciante |

**Descrição:** Executado uma vez quando uma instância é criada pela primeira vez.

**Quando dispara:**
- Quando uma instância é colocada em uma sala no início do jogo
- Quando criada via ação "Criar Instancia"
- Após transições de sala para novas instâncias

**Usos comuns:**
- Inicializar variáveis
- Definir valores iniciais
- Configurar estado inicial

---

### Step
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `step` |
| **Ícone** | ⭐ |
| **Categoria** | Objeto |
| **Preset** | Iniciante |

**Descrição:** Executado a cada quadro (tipicamente 60 vezes por segundo).

**Quando dispara:** Continuamente, a cada quadro do jogo.

**Usos comuns:**
- Movimento contínuo
- Verificar condições
- Atualizar posições
- Lógica do jogo

**Nota:** Cuidado com o desempenho - o código aqui executa constantemente.

---

### Destroy
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `destroy` |
| **Ícone** | 💥 |
| **Categoria** | Objeto |
| **Preset** | Intermediário |

**Descrição:** Executado quando uma instância é destruida.

**Quando dispara:** Logo antes da instância ser removida do jogo.

**Usos comuns:**
- Gerar efeitos (explosoes, particulas)
- Soltar itens
- Atualizar pontuações
- Tocar sons

---

## Eventos de Entrada

### Teclado (Contínuo)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard` |
| **Ícone** | ⌨️ |
| **Categoria** | Entrada |
| **Preset** | Iniciante |

**Descrição:** Dispara continuamente enquanto uma tecla está pressionada.

**Ideal para:** Movimento suave e contínuo

**Teclas Suportadas:**
- Teclas de seta (cima, baixo, esquerda, direita)
- Letras (A-Z)
- Números (0-9)
- Espaço, Enter, Escape
- Teclas de função (F1-F12)
- Teclas modificadoras (Shift, Ctrl, Alt)

---

### Pressionar Teclado
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_press` |
| **Ícone** | 🔘 |
| **Categoria** | Entrada |
| **Preset** | Iniciante |

**Descrição:** Dispara uma vez quando uma tecla é pressionada pela primeira vez.

**Ideal para:** Ações únicas (pular, atirar, selecionar no menu)

**Diferença do Teclado:** Só dispara uma vez por pressionamento, não enquanto mantido.

---

### Soltar Teclado
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_release` |
| **Ícone** | ⬆️ |
| **Categoria** | Entrada |
| **Preset** | Avançado |

**Descrição:** Dispara uma vez quando uma tecla é solta.

**Usos comuns:**
- Parar movimento quando tecla é solta
- Terminar ataques carregados
- Alternar estados

---

### Teclado (Nenhuma tecla)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_no_key` |
| **Ícone** | ⌨️ |
| **Categoria** | Entrada |
| **Preset** | Avançado |

**Descrição:** Dispara a cada quadro enquanto **nenhuma** tecla está sendo mantida.

**Quando dispara:** A cada quadro em que o teclado está inativo, *antes* do evento Step.

**Usos comuns:**
- Parar o movimento quando o jogador solta todas as teclas (jogos de grade/labirintos)
- Animações em repouso

---

### Mouse
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `mouse` |
| **Ícone** | 🖱️ |
| **Categoria** | Entrada |
| **Preset** | Intermediário |

**Descrição:** Eventos de botão do mouse e movimento.

**Tipos de Eventos:**

| Tipo | Descrição |
|------|-----------|
| Botão Esquerdo | Clique com botão esquerdo do mouse |
| Botão Direito | Clique com botão direito do mouse |
| Botão do Meio | Clique com botão do meio/scroll |
| Entrada do Mouse | Cursor entra nos limites da instância |
| Saída do Mouse | Cursor sai dos limites da instância |
| Botão Esquerdo Global | Clique esquerdo em qualquer lugar |
| Botão Direito Global | Clique direito em qualquer lugar |

---

## Eventos de Colisão

### Colisão
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `collision` |
| **Ícone** | 💥 |
| **Categoria** | Colisão |
| **Preset** | Iniciante |

**Descrição:** Dispara quando esta instância se sobrepõe com outro tipo de objeto.

**Configuração:** Selecione qual tipo de objeto dispara esta colisão.

**Variável especial:** `other` - Referência a instância em colisão.

**Quando dispara:** A cada quadro em que as instâncias se sobrepõem.

**Usos comuns:**
- Coletar itens
- Receber dano
- Bater em paredes
- Disparar eventos

**Exemplos de eventos de colisão:**
- `collision_with_obj_coin` - Jogador toca uma moeda
- `collision_with_obj_enemy` - Jogador toca um inimigo
- `collision_with_obj_wall` - Instancia bate em uma parede

---

## Eventos de Tempo

### Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `alarm` |
| **Ícone** | ⏰ |
| **Categoria** | Tempo |
| **Preset** | Intermediário |

**Descrição:** Dispara quando uma contagem regressiva de alarme chega a zero.

**Alarmes disponíveis:** 12 alarmes independentes (alarm[0] ate alarm[11])

**Configurar alarmes:** Use a ação "Definir Alarme" com passos (60 passos ≈ 1 segundo a 60 FPS)

**Usos comuns:**
- Geração temporizada
- Tempos de recarga
- Efeitos atrasados
- Ações repetitivas (redefinir alarme no evento de alarme)

---

### Begin Step
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `begin_step` |
| **Ícone** | ▶️ |
| **Categoria** | Step |
| **Preset** | Avançado |

**Descrição:** Dispara no início de cada quadro, antes dos eventos Step regulares.

**Ordem de execução:** Begin Step → Step → End Step

**Usos comuns:**
- Processamento de entrada
- Cálculos pré-movimento

---

### End Step
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `end_step` |
| **Ícone** | ⏹️ |
| **Categoria** | Step |
| **Preset** | Avançado |

**Descrição:** Dispara no final de cada quadro, após as colisões.

**Usos comuns:**
- Ajustes finais de posição
- Operações de limpeza
- Atualizações de estado após colisões

---

## Eventos de Desenho

### Draw
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw` |
| **Ícone** | 🎨 |
| **Categoria** | Desenho |
| **Preset** | Intermediário |

**Descrição:** Dispara durante a fase de renderização.

**Importante:** Adicionar um evento Draw desabilita o desenho automatico do sprite. Voce deve desenhar o sprite manualmente se quiser que ele seja visivel.

**Usos comuns:**
- Renderização personalizada
- Desenhar formas
- Exibir texto
- Barras de saúde
- Elementos de HUD

**Ações de desenho disponíveis:**
- Desenhar Sprite
- Desenhar Texto
- Desenhar Retangulo
- Desenhar Circulo
- Desenhar Linha
- Desenhar Barra de Saúde

---

### Draw GUI
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_gui` |
| **Ícone** | 🖥️ |
| **Categoria** | Desenho |
| **Preset** | Avançado |

**Descrição:** Desenha no **espaço de tela (GUI)**, por cima da sala e sem ser afetado pela rolagem de vistas/câmera.

**Diferença do Draw:** o evento Draw normal está em coordenadas de sala (rola com a vista); Draw GUI permanece fixo à tela — use-o para HUD, pontuações e menus.

---

## Eventos de Sala

### Room Start
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `room_start` |
| **Ícone** | 🚪 |
| **Categoria** | Sala |
| **Preset** | Avançado |

**Descrição:** Dispara ao entrar em uma sala, após todos os eventos Create.

**Usos comuns:**
- Inicialização da sala
- Tocar musica da sala
- Definir variáveis específicas da sala

---

### Room End
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `room_end` |
| **Ícone** | 🚪 |
| **Categoria** | Sala |
| **Preset** | Avançado |

**Descrição:** Dispara ao sair de uma sala.

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
| **Ícone** | 🎮 |
| **Categoria** | Jogo |
| **Preset** | Avançado |

**Descrição:** Dispara uma vez quando o jogo inicia pela primeira vez (apenas na primeira sala).

**Usos comuns:**
- Inicializar variáveis globais
- Carregar dados salvos
- Tocar introdução

---

### Game End
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `game_end` |
| **Ícone** | 🎮 |
| **Categoria** | Jogo |
| **Preset** | Avançado |

**Descrição:** Dispara quando o jogo esta terminando.

**Usos comuns:**
- Salvar dados do jogo
- Liberar recursos

---

## Outros Eventos

### Outside Room
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `outside_room` |
| **Ícone** | 🚫 |
| **Categoria** | Outro |
| **Preset** | Avançado |

**Descrição:** Dispara quando a instância esta completamente fora dos limites da sala.

**Usos comuns:**
- Destruir projeteis fora da tela
- Aparecer do outro lado
- Disparar game over

---

### Intersect Boundary
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `intersect_boundary` |
| **Ícone** | ⚠️ |
| **Categoria** | Outro |
| **Preset** | Avançado |

**Descrição:** Dispara quando a instância toca o limite da sala.

**Usos comuns:**
- Manter o jogador nos limites
- Quicar nas bordas

---

### No More Lives
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `no_more_lives` |
| **Ícone** | 💀 |
| **Categoria** | Outro |
| **Preset** | Intermediário |

**Descrição:** Dispara quando as vidas chegam a 0 ou menos.

**Usos comuns:**
- Tela de game over
- Reiniciar jogo
- Mostrar pontuação final

---

### No More Health
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `no_more_health` |
| **Ícone** | 💔 |
| **Categoria** | Outro |
| **Preset** | Intermediário |

**Descrição:** Dispara quando a saúde chega a 0 ou menos.

**Usos comuns:**
- Perder uma vida
- Reaparecer jogador
- Disparar animação de morte

---

### Animation End
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `animation_end` |
| **Ícone** | 🎞️ |
| **Categoria** | Outro |
| **Preset** | Avançado |

**Descrição:** Dispara quando a animação do sprite da instância completa um ciclo inteiro (volta do último quadro ao primeiro).

**Usos comuns:**
- Destruir um efeito único (explosão) após uma única reprodução
- Mudar para outra animação quando a atual termina
- Avançar uma máquina de estados ao terminar a animação

---

## Ordem de Execução de Eventos

Entender quando os eventos disparam ajuda a criar um comportamento de jogo previsivel:

1. **Begin Step** - Início do quadro
2. **Alarm** - Qualquer alarme disparado
3. **Keyboard/Mouse** - Eventos de entrada
4. **Step** - Lógica principal do jogo
5. **Collision** - Após o movimento
6. **End Step** - Após colisões
7. **Draw** - Fase de renderização

---

## Eventos por Preset

| Preset | Eventos Incluidos |
|--------|-------------------|
| **Iniciante** | Create, Step, Keyboard Press, Collision |
| **Intermediário** | + Draw, Destroy, Mouse, Alarm |
| **Avançado** | + Todas as variantes de teclado, Begin/End Step, Eventos de sala, Eventos de jogo, Eventos de limite |

---

## Veja Tambem

- [Referência Completa de Ações](Full-Action-Reference_pt) - Lista completa de ações
- [Preset Iniciante](Beginner-Preset_pt) - Eventos essenciais para iniciantes
- [Preset Intermediário](Intermediate-Preset_pt) - Eventos adicionais
- [Eventos e Ações](Eventos_e_Acoes_pt) - Visao geral dos conceitos basicos
