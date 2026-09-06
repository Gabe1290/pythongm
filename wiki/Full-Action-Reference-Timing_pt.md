# Tempo

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Pausar a linha temporal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `pause_timeline` |
| **Ícone** | ⏸️ |
| **Categoria** | Tempo |

Coloca a reprodução da linha temporal em pausa na posição atual

*Parâmetros:* nenhum

### Definir alarme

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_alarm` |
| **Ícone** | ⏰ |
| **Categoria** | Tempo |

Definir um alarme

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `alarm_number` | Número | `0` | Qual alarme (0-11) |
| `steps` | Número | `30` | Número de passos até o alarme disparar (30 = 0,5 s a 60 FPS) |

### Definir a linha temporal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_timeline` |
| **Ícone** | ⏱️ |
| **Categoria** | Tempo |

Define a etiqueta da linha temporal desta instância e repõe a sua posição a 0 (apenas registo — ver a nota da categoria)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `timeline` | Texto | — | A label for your own reference; not a resource lookup |

### Definir a posição na linha temporal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_timeline_position` |
| **Ícone** | ⏱️ |
| **Categoria** | Tempo |

Define (ou desloca) a posição desta instância na linha temporal

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `position` | Número | `0` | Position in steps |
| `relative` | Sim/Não | Não | Add to the current position instead of setting it absolutely |

### Definir a velocidade da linha temporal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_timeline_speed` |
| **Ícone** | ⏱️ |
| **Categoria** | Tempo |

Define o multiplicador de velocidade da linha temporal

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `speed` | Número | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Pausa

| Propriedade | Valor |
|----------|-------|
| **Nome** | `sleep` |
| **Ícone** | 💤 |
| **Categoria** | Tempo |

Pausar o jogo por um número de milissegundos e depois continuar. Os sons continuam tocando durante a pausa (por exemplo, para deixar um som terminar antes de mudar de sala). Nota: a renderização e a entrada ficam congeladas durante a pausa, então mantenha durações curtas

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `milliseconds` | Número | `1000` | Duração da pausa, em milissegundos (1000 = 1 segundo) |

### Iniciar a linha temporal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_timeline` |
| **Ícone** | ▶️ |
| **Categoria** | Tempo |

Inicia ou retoma a linha temporal a partir da posição atual

*Parâmetros:* nenhum

### Parar a linha temporal

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_timeline` |
| **Ícone** | ⏹️ |
| **Categoria** | Tempo |

Para a linha temporal e repõe a posição a 0

*Parâmetros:* nenhum

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Rede](Full-Action-Reference-Network-Actions_pt) (15)
- [Partículas](Full-Action-Reference-Particles_pt) (8)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
