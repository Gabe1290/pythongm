# Controle

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Verificar se vazio

| Propriedade | Valor |
|----------|-------|
| **Nome** | `check_empty` |
| **Ícone** | 🔍 |
| **Categoria** | Controle |

Verdadeiro quando (x, y) está livre de colisões. Use com start_block/end_block para condicionar a(s) ação(ões) seguinte(s), no estilo GM

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x` | Posição X a verificar (expressão permitida, ex. self.x + 32) |
| `y` | Texto | `self.y` | Posição Y a verificar (expressão permitida, ex. self.y + 32) |
| `relative` | Sim/Não | Não | Tratar X/Y como deslocamentos da posição desta instância em vez de coordenadas absolutas; opcional |
| `objects` | Escolha | `solid` | Quais instâncias contam como ocupando a posição; Opções: `solid`, `all` |

### Comentário

| Propriedade | Valor |
|----------|-------|
| **Nome** | `comment` |
| **Ícone** | ⚠️ |
| **Categoria** | Controle |

Um comentário na lista de ações (sem efeito em execução)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | — | Texto de comentário livre; opcional |

### Senão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `else_action` |
| **Ícone** | ⚡ |
| **Categoria** | Controle |

Marca o ramo «senão» de uma condição

*Parâmetros:* nenhum

### Fim de bloco

| Propriedade | Valor |
|----------|-------|
| **Nome** | `end_block` |
| **Ícone** | 📁 |
| **Categoria** | Controle |

Terminar um bloco de ações

*Parâmetros:* nenhum

### Executar código

| Propriedade | Valor |
|----------|-------|
| **Nome** | `execute_code` |
| **Ícone** | 📜 |
| **Categoria** | Controle |

Executar um bloco de código Python integrado

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `code` | Código | — | Código Python a avaliar em relação à instância |

### Executar script

| Propriedade | Valor |
|----------|-------|
| **Nome** | `execute_script` |
| **Ícone** | 📜 |
| **Categoria** | Controle |

Executar um dos scripts do projeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `script` | Script | — | Nome do script do projeto a executar |
| `arg0` | Texto | — | Disponível no script como argument0; opcional |
| `arg1` | Texto | — | Disponível no script como argument1; opcional |
| `arg2` | Texto | — | Disponível no script como argument2; opcional |
| `arg3` | Texto | — | Disponível no script como argument3; opcional |
| `arg4` | Texto | — | Disponível no script como argument4; opcional |

### Sair do evento

| Propriedade | Valor |
|----------|-------|
| **Nome** | `exit_event` |
| **Ícone** | 🚪 |
| **Categoria** | Controle |

Interromper a execução das ações restantes neste evento

*Parâmetros:* nenhum

### Se pode empurrar

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_can_push` |
| **Ícone** | 📦 |
| **Categoria** | Controle |

Verificar se uma caixa/objeto pode ser empurrado na direção atual (estilo Sokoban)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Escolha | `facing` | Direção a verificar para o empurrão; Opções: `facing` |
| `object_type` | Texto | `box` | Tipo de objeto sendo empurrado |
| `then_action` | Escolha | `push_and_move` | Ação se o empurrão é possível; Opções: `push_and_move`, `none` |
| `else_action` | Escolha | `stop_movement` | Ação se o empurrão está bloqueado; Opções: `stop_movement`, `none` |

### Se colisão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_collision` |
| **Ícone** | ❓💥 |
| **Categoria** | Controle |

Condição: verdadeiro se a instância colidiria no deslocamento (x, y)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Deslocamento horizontal a testar |
| `y` | Número | `0` | Deslocamento vertical a testar |
| `object` | Texto | `any` | «any», «solid» ou um nome de objeto; Opções: `any`, `solid`; opcional |
| `not_flag` | Sim/Não | Não | Negar o resultado; opcional |

### Se colisão em

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_collision_at` |
| **Ícone** | 🎯 |
| **Categoria** | Controle |

Verificar uma colisão em uma posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `self.x + 32` | Expressão da posição X |
| `y` | Texto | `self.y` | Expressão da posição Y |
| `object_type` | Escolha | `any` | Tipo de objeto a verificar; Opções: `any`, `solid` |
| `then_actions` | Lista de ações | — | Ações se colisão encontrada |
| `else_actions` | Lista de ações | — | Ações se nenhuma colisão |

### Se condição

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_condition` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Verificação condicional com ações então/senão

*Parâmetros:* nenhum

### Se o objeto existe

| Propriedade | Valor |
|----------|-------|
| **Nome** | `if_object_exists` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Condição: verdadeiro se existir pelo menos uma instância do objeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Tipo de objeto a verificar |
| `not_flag` | Sim/Não | Não | Negar o resultado (agir quando o objeto NÃO existe); opcional |

### Repetir

| Propriedade | Valor |
|----------|-------|
| **Nome** | `repeat` |
| **Ícone** | 🔁 |
| **Categoria** | Controle |

Repetir a ação/o bloco seguinte N vezes

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `times` | Número | `10` | Número de repetições |
| `actions` | Lista de ações | — | Ações a repetir |

### Definir variável

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_variable` |
| **Ícone** | 📝 |
| **Categoria** | Controle |

Definir uma variável de instância ou global

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nome da variável |
| `value` | Texto | `0` | Valor (número, cadeia ou expressão) |
| `scope` | Escolha | `self` | Escopo da variável; Opções: `self`, `other`, `global` |
| `relative` | Sim/Não | Não | Somar ao valor atual em vez de substituí-lo |

### Início de bloco

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_block` |
| **Ícone** | 📂 |
| **Categoria** | Controle |

Iniciar um bloco de ações (para agrupar)

*Parâmetros:* nenhum

### Testar probabilidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_chance` |
| **Ícone** | 🎲❓ |
| **Categoria** | Controle |

Condição: verdadeiro com probabilidade 1 em «sides»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sides` | Número | `6` | Uma chance de 1 em N de ser verdadeiro |

### Testar expressão

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_expression` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Testar se uma expressão é verdadeira

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `expression` | Texto | — | Expressão a avaliar (verdadeiro se >= 0.5) |
| `then_actions` | Lista de ações | — | Ações se verdadeiro |
| `else_actions` | Lista de ações | — | Ações se falso |

### Fazer uma pergunta

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_question` |
| **Ícone** | ❓💬 |
| **Categoria** | Controle |

Condição: mostrar uma caixa de diálogo sim/não; verdadeiro se o usuário responder sim

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `question` | Texto | `Continue?` | Pergunta mostrada ao jogador |

### Testar variável

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_variable` |
| **Ícone** | ❓ |
| **Categoria** | Controle |

Testar o valor de uma variável de instância ou global

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `variable` | Texto | — | Nome da variável |
| `value` | Texto | `0` | Valor a comparar |
| `scope` | Escolha | `self` | Escopo da variável; Opções: `self`, `other`, `global` |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (2)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (20)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (4)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
