# Tempo

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

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

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (20)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (4)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
