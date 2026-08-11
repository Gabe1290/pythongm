# Outros Eventos

*[Início](Home_pt) | [Referência de Eventos](Event-Reference_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

### Outside Room
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `outside_room` |
| **Ícone** | 🚫 |
| **Categoria** | Outro |
| **Preset** | Iniciante |

**Descrição:** Dispara quando a instância está completamente fora dos limites da sala.

**Usos comuns:**
- Destruir projéteis fora da tela
- Aparecer do outro lado
- Disparar game over

---

### Intersect Boundary
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `intersect_boundary` |
| **Ícone** | ⚠️ |
| **Categoria** | Outro |
| **Preset** | Iniciante |

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
| **Preset** | Iniciante |

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
| **Preset** | Iniciante |

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
| **Preset** | Iniciante |

**Descrição:** Dispara quando a animação do sprite da instância completa um ciclo inteiro (volta do último quadro ao primeiro).

**Usos comuns:**
- Destruir um efeito único (explosão) após uma única reprodução
- Mudar para outra animação quando a atual termina
- Avançar uma máquina de estados ao terminar a animação

---

## Outras Categorias de Eventos

- [Eventos de Objeto](Event-Reference-Object_pt) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_pt) - Teclado, Mouse
- [Eventos de Colisão](Event-Reference-Collision_pt) - Colisões de objetos
- [Eventos de Tempo](Event-Reference-Timing_pt) - Alarmes, Variantes de Step
- [Eventos de Desenho](Event-Reference-Drawing_pt) - Renderização personalizada
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Eventos de Jogo](Event-Reference-Game_pt) - Início/Fim do jogo

[← Voltar à Referência de Eventos](Event-Reference_pt)
