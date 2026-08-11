# Eventos de Desenho

*[Início](Home_pt) | [Referência de Eventos](Event-Reference_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

### Draw
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw` |
| **Ícone** | 🎨 |
| **Categoria** | Desenho |
| **Preset** | Iniciante |

**Descrição:** Dispara durante a fase de renderização.

**Importante:** Adicionar um evento Draw desabilita o desenho automático do sprite. Você deve desenhar o sprite manualmente se quiser que ele seja visível.

**Usos comuns:**
- Renderização personalizada
- Desenhar formas
- Exibir texto
- Barras de saúde
- Elementos de HUD

**Ações de desenho disponíveis:**
- Desenhar Sprite
- Desenhar Texto
- Desenhar Retângulo
- Desenhar Círculo
- Desenhar Linha
- Desenhar Barra de Saúde

---

### Draw GUI
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `draw_gui` |
| **Ícone** | 🖥️ |
| **Categoria** | Desenho |
| **Preset** | Iniciante |

**Descrição:** Desenha no **espaço de tela (GUI)**, por cima da sala e sem ser afetado pela rolagem de vistas/câmera.

**Diferença do Draw:** o evento Draw normal está em coordenadas de sala (rola com a vista); Draw GUI permanece fixo à tela — use-o para HUD, pontuações e menus.

---

## Outras Categorias de Eventos

- [Eventos de Objeto](Event-Reference-Object_pt) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_pt) - Teclado, Mouse
- [Eventos de Colisão](Event-Reference-Collision_pt) - Colisões de objetos
- [Eventos de Tempo](Event-Reference-Timing_pt) - Alarmes, Variantes de Step
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Eventos de Jogo](Event-Reference-Game_pt) - Início/Fim do jogo
- [Outros Eventos](Event-Reference-Other_pt) - Limites, Vidas, Saúde

[← Voltar à Referência de Eventos](Event-Reference_pt)
