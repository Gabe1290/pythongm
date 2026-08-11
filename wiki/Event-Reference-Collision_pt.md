# Eventos de Colisão

*[Início](Home_pt) | [Referência de Eventos](Event-Reference_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

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
- `collision_with_obj_wall` - Instância bate em uma parede

---

## Outras Categorias de Eventos

- [Eventos de Objeto](Event-Reference-Object_pt) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_pt) - Teclado, Mouse
- [Eventos de Tempo](Event-Reference-Timing_pt) - Alarmes, Variantes de Step
- [Eventos de Desenho](Event-Reference-Drawing_pt) - Renderização personalizada
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Eventos de Jogo](Event-Reference-Game_pt) - Início/Fim do jogo
- [Outros Eventos](Event-Reference-Other_pt) - Limites, Vidas, Saúde

[← Voltar à Referência de Eventos](Event-Reference_pt)
