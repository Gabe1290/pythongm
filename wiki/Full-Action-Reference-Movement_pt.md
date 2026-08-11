# Movimento

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Quicar

| Propriedade | Valor |
|----------|-------|
| **Nome** | `bounce` |
| **Categoria** | Movimento |

Quicar em objetos sólidos

*Parâmetros:* nenhum

### Saltar para posição

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump_to_position` |
| **Ícone** | 📍 |
| **Categoria** | Movimento |

Mover instantaneamente para uma posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `relative` | Sim/Não | Não | Somar à posição atual em vez de definir uma absoluta |

### Saltar para posição aleatória

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump_to_random` |
| **Ícone** | 🎲↪️ |
| **Categoria** | Movimento |

Teletransportar para uma posição aleatória (opcionalmente ajustada à grade)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `snap_h` | Número | `1` | Ajuste horizontal à grade (1 = sem ajuste) |
| `snap_v` | Número | `1` | Ajuste vertical à grade (1 = sem ajuste) |

### Saltar para a posição inicial

| Propriedade | Valor |
|----------|-------|
| **Nome** | `jump_to_start` |
| **Ícone** | ↩️ |
| **Categoria** | Movimento |

Retornar a instância à sua posição de criação

*Parâmetros:* nenhum

### Movimento livre

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_free` |
| **Ícone** | 🧭 |
| **Categoria** | Movimento |

Mover em uma direção precisa (0-360 graus)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Direção em graus (0=direita, 90=cima, anti-horário) |
| `speed` | Número | `4.0` | Velocidade de movimento |

### Mover pela grade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_grid` |
| **Ícone** | ▦ |
| **Categoria** | Movimento |

Mover uma célula da grade na direção indicada

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Escolha | `right` | Direção de movimento; Opções: `left`, `right`, `up`, `down` |
| `grid_size` | Número | `32` | Tamanho da célula da grade em pixels |

### Mover em direção a um ponto

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_towards_point` |
| **Ícone** | 🎯 |
| **Categoria** | Movimento |

Mover em direção a um ponto a uma dada velocidade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | X de destino |
| `y` | Número | `0` | Y de destino |
| `speed` | Número | `4.0` | Velocidade de movimento |

### Mover até o contato

| Propriedade | Valor |
|----------|-------|
| **Nome** | `move_to_contact` |
| **Ícone** | 🎯 |
| **Categoria** | Movimento |

Mover em uma direção até tocar um objeto (ou a distância máxima)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Texto | `direction` | Direção em graus (0=direita, 90=cima, 180=esquerda, 270=baixo) ou uma expressão. Padrão «direction» = a orientação atual da instância (ajuste à colisão). |
| `max_distance` | Número | `1000` | Distância máxima de movimento, em pixels |
| `object` | Objeto | `all` | Parar ao contato com: «all» todas as instâncias, «solid» apenas objetos sólidos, ou um nome de objeto específico.; Opções: `all`, `solid`; opcional |

### Inverter horizontal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `reverse_horizontal` |
| **Ícone** | ↔️ |
| **Categoria** | Movimento |

Inverter a direção do movimento horizontal

*Parâmetros:* nenhum

### Inverter vertical

| Propriedade | Valor |
|----------|-------|
| **Nome** | `reverse_vertical` |
| **Ícone** | ↕️ |
| **Categoria** | Movimento |

Inverter a direção do movimento vertical

*Parâmetros:* nenhum

### Definir direção

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_direction` |
| **Ícone** | 🧭 |
| **Categoria** | Movimento |

Definir a direção do movimento

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Direção em graus (0=direita, 90=cima) |

### Definir direção e velocidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_direction_speed` |
| **Ícone** | 🧭 |
| **Categoria** | Movimento |

Definir a direção (em graus) e a magnitude da velocidade da instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `0` | Direção em graus (0=direita, 90=cima) |
| `speed` | Número | `4.0` | Velocidade em pixels por quadro |

### Definir atrito

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_friction` |
| **Ícone** | 🛑 |
| **Categoria** | Movimento |

Definir o atrito (desaceleração)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `friction` | Número | `0.1` | Quantidade de atrito (subtraída da velocidade a cada passo) |

### Definir gravidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_gravity` |
| **Ícone** | ⬇️ |
| **Categoria** | Movimento |

Definir a direção e a intensidade da gravidade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `direction` | Número | `270` | Direção da gravidade em graus (270=baixo) |
| `gravity` | Número | `0.5` | Intensidade da gravidade (adicionada a cada passo) |

### Definir velocidade horizontal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_hspeed` |
| **Ícone** | ↔️ |
| **Categoria** | Movimento |

Definir a velocidade de movimento horizontal

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidade em pixels por quadro |

### Definir velocidade

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_speed` |
| **Ícone** | ⚡ |
| **Categoria** | Movimento |

Definir a velocidade de movimento (magnitude)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidade de movimento |

### Definir velocidade vertical

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_vspeed` |
| **Ícone** | ↕️ |
| **Categoria** | Movimento |

Definir a velocidade de movimento vertical

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `0` | Velocidade em pixels por quadro |

### Começar a mover (direção)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_moving_direction` |
| **Ícone** | ➡️ |
| **Categoria** | Movimento |

Começar a mover em uma direção a uma dada velocidade

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `directions` | Escolha múltipla | right | Direção(ões) de movimento — marque uma, ou várias para escolher uma aleatória a cada passo. A célula central é parar.; Opções: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Texto | — | Alternativa: expressão livre avaliada como graus; opcional |
| `speed` | Número | `4.0` | Velocidade em pixels por quadro |

### Parar movimento

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_movement` |
| **Ícone** | 🛑 |
| **Categoria** | Movimento |

Zerar ambas as velocidades

*Parâmetros:* nenhum

### Envolver ao redor da sala

| Propriedade | Valor |
|----------|-------|
| **Nome** | `wrap_around_room` |
| **Ícone** | 🔄 |
| **Categoria** | Movimento |

Reaparecer no lado oposto da sala

*Parâmetros:* nenhum

---

## Outras Categorias

- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (2)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (20)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (4)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
