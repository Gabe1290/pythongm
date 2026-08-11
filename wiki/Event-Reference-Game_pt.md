# Eventos de Jogo

*[Início](Home_pt) | [Referência de Eventos](Event-Reference_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

### Game Start
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `game_start` |
| **Ícone** | 🎮 |
| **Categoria** | Jogo |
| **Preset** | Iniciante |

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
| **Preset** | Iniciante |

**Descrição:** Dispara quando o jogo está terminando.

**Usos comuns:**
- Salvar dados do jogo
- Liberar recursos

---

## Outras Categorias de Eventos

- [Eventos de Objeto](Event-Reference-Object_pt) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_pt) - Teclado, Mouse
- [Eventos de Colisão](Event-Reference-Collision_pt) - Colisões de objetos
- [Eventos de Tempo](Event-Reference-Timing_pt) - Alarmes, Variantes de Step
- [Eventos de Desenho](Event-Reference-Drawing_pt) - Renderização personalizada
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Outros Eventos](Event-Reference-Other_pt) - Limites, Vidas, Saúde

[← Voltar à Referência de Eventos](Event-Reference_pt)
