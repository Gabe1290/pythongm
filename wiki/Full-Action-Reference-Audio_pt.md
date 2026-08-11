# Áudio

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Verificar reprodução de som

| Propriedade | Valor |
|----------|-------|
| **Nome** | `check_sound` |
| **Ícone** | ❓🔊 |
| **Categoria** | Áudio |

Condição: verdadeiro se o som indicado está sendo reproduzido no momento

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sound` | Som | — | Som a verificar |
| `not_flag` | Sim/Não | Não | Inverter o resultado; opcional |

### Reproduzir música

| Propriedade | Valor |
|----------|-------|
| **Nome** | `play_music` |
| **Ícone** | 🎵 |
| **Categoria** | Áudio |

Reproduzir música de fundo (em loop)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `music` | Som | — | Arquivo de música a reproduzir |
| `loop` | Sim/Não | Sim | Reproduzir a música em loop |
| `volume` | Número | `0.7` | Volume (de 0.0 a 1.0) |

### Reproduzir som

| Propriedade | Valor |
|----------|-------|
| **Nome** | `play_sound` |
| **Ícone** | 🔊 |
| **Categoria** | Áudio |

Reproduzir um efeito sonoro uma vez

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sound` | Som | — | Som a reproduzir |
| `volume` | Número | `1.0` | Volume (de 0.0 a 1.0) |

### Definir volume

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_volume` |
| **Ícone** | 🔉 |
| **Categoria** | Áudio |

Definir o volume geral de som/música

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `volume` | Número | `1.0` | Volume (de 0.0 a 1.0) |

### Parar música

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_music` |
| **Ícone** | 🔇 |
| **Categoria** | Áudio |

Parar a música de fundo

*Parâmetros:* nenhum

### Parar som

| Propriedade | Valor |
|----------|-------|
| **Nome** | `stop_sound` |
| **Ícone** | 🔇 |
| **Categoria** | Áudio |

Parar um som em reprodução

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sound` | Som | — | Som a parar |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (2)
- [Jogo](Full-Action-Reference-Game_pt) (20)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (4)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
