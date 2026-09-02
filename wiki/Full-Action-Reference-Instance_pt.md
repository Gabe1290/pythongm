# Instância

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Mudar instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `change_instance` |
| **Ícone** | 🔄 |
| **Categoria** | Instância |
| **Aplica-se a** | self / other / object |

Transformar em outro tipo de objeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Novo tipo de objeto |
| `perform_events` | Sim/Não | Sim | Executar os eventos destruir/criar |

### Criar instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_instance` |
| **Ícone** | ✨ |
| **Categoria** | Instância |

Criar uma nova instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a criar |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `relative` | Sim/Não | Não | Posição relativa à instância atual |

### Criar instância em movimento

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_moving_instance` |
| **Ícone** | ✨➡️ |
| **Categoria** | Instância |

Criar uma instância e iniciá-la em uma direção

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a criar |
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `speed` | Número | `0` | Magnitude da velocidade inicial |
| `direction` | Número | `0` | Direção inicial em graus |

### Criar instância aleatória

| Propriedade | Valor |
|----------|-------|
| **Nome** | `create_random_instance` |
| **Ícone** | 🎲 |
| **Categoria** | Instância |

Criar um de vários tipos de objeto escolhido aleatoriamente

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Número | `0` | Posição X |
| `y` | Número | `0` | Posição Y |
| `object1` | Objeto | — | Primeiro objeto candidato; opcional |
| `object2` | Objeto | — | Segundo objeto candidato; opcional |
| `object3` | Objeto | — | Terceiro objeto candidato; opcional |
| `object4` | Objeto | — | Quarto objeto candidato; opcional |

### Destruir instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_instance` |
| **Ícone** | 💥 |
| **Categoria** | Instância |
| **Aplica-se a** | self / other / object |

Destruir uma instância

*Parâmetros:* nenhum

### Destruir na posição

| Propriedade | Valor |
|----------|-------|
| **Nome** | `destroy_at_position` |
| **Ícone** | 💣 |
| **Categoria** | Instância |

Destruir instâncias dentro de um raio de (x, y)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | `all` | Qual tipo de objeto destruir. «all» destrói cada instância no raio; «solid» apenas as sólidas (ex. muros); «non-solid» tudo exceto os sólidos.; Opções: `all`, `solid`, `non-solid` |
| `x` | Texto | `self.x` | Posição X (expressão permitida, ex. self.x) |
| `y` | Texto | `self.y` | Posição Y (expressão permitida, ex. self.y) |
| `relative` | Sim/Não | Não | Tratar X/Y como deslocamentos da posição desta instância em vez de coordenadas absolutas; opcional |
| `radius` | Número | `32` | Raio em pixels ao redor de (x, y). Padrão 32 = ~uma célula da grade. |

### Definir índice de imagem

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_image_index` |
| **Ícone** | 🖼️ |
| **Categoria** | Instância |

Definir o quadro de animação atual do sprite da instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `frame` | Número | `0` | Índice do quadro |

### Definir velocidade de imagem

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_image_speed` |
| **Ícone** | ⏩ |
| **Categoria** | Instância |

Definir a velocidade de reprodução da animação do sprite da instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `1.0` | Quadros avançados por passo (0 = em pausa) |

### Definir sprite

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_sprite` |
| **Ícone** | 🖼️ |
| **Categoria** | Instância |

Mudar o sprite e/ou o quadro/velocidade de animação de uma instância

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite a usar (ou «<self>» para manter o atual) |
| `subimage` | Número | `-1` | Índice do quadro a definir; -1 deixa inalterado |
| `speed` | Número | `-1` | Velocidade de animação; -1 deixa inalterada |

### Iniciar animação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_animation` |
| **Ícone** | ▶️ |
| **Categoria** | Instância |

Retomar a animação do sprite da instância (image_speed = 1)

*Parâmetros:* nenhum

### Parar animação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_animation` |
| **Ícone** | ⏸️ |
| **Categoria** | Instância |

Pausar a animação do sprite da instância (image_speed = 0)

*Parâmetros:* nenhum

### Testar número de instâncias

| Propriedade | Valor |
|----------|-------|
| **Nome** | `test_instance_count` |
| **Ícone** | ❓🔢 |
| **Categoria** | Instância |

Condição: comparar o número de instâncias de um objeto

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | Objeto a contar |
| `number` | Número | `0` | Valor de comparação |
| `operation` | Escolha | `equal` | Operador de comparação; Opções: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Particles](Full-Action-Reference-Particles_pt) (8)
- [Réseau](Full-Action-Reference-Network-Actions_pt) (15)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
