# Eventos de Tempo

*[Início](Home_pt) | [Referência de Eventos](Event-Reference_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

### Alarme
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `alarm` |
| **Ícone** | ⏰ |
| **Categoria** | Tempo |
| **Preset** | Iniciante |

**Descrição:** Dispara quando uma contagem regressiva de alarme chega a zero.

**Alarmes disponíveis:** 12 alarmes independentes (alarm[0] até alarm[11])

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
| **Preset** | Iniciante |

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
| **Preset** | Iniciante |

**Descrição:** Dispara no final de cada quadro, após as colisões.

**Usos comuns:**
- Ajustes finais de posição
- Operações de limpeza
- Atualizações de estado após colisões

---

## Outras Categorias de Eventos

- [Eventos de Objeto](Event-Reference-Object_pt) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_pt) - Teclado, Mouse
- [Eventos de Colisão](Event-Reference-Collision_pt) - Colisões de objetos
- [Eventos de Desenho](Event-Reference-Drawing_pt) - Renderização personalizada
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Eventos de Jogo](Event-Reference-Game_pt) - Início/Fim do jogo
- [Outros Eventos](Event-Reference-Other_pt) - Limites, Vidas, Saúde

[← Voltar à Referência de Eventos](Event-Reference_pt)
