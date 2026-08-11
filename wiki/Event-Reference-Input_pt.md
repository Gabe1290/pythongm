# Eventos de Entrada

*[Início](Home_pt) | [Referência de Eventos](Event-Reference_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

### Teclado (Contínuo)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard` |
| **Ícone** | ⌨️ |
| **Categoria** | Entrada |
| **Preset** | Iniciante |

**Descrição:** Dispara continuamente enquanto uma tecla está pressionada.

**Ideal para:** Movimento suave e contínuo

**Teclas Suportadas:**
- Teclas de seta (cima, baixo, esquerda, direita)
- Letras (A-Z)
- Números (0-9)
- Espaço, Enter, Escape
- Teclas de função (F1-F12)
- Teclas modificadoras (Shift, Ctrl, Alt)

---

### Pressionar Teclado
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_press` |
| **Ícone** | 🔘 |
| **Categoria** | Entrada |
| **Preset** | Intermediário |

**Descrição:** Dispara uma vez quando uma tecla é pressionada pela primeira vez.

**Ideal para:** Ações únicas (pular, atirar, selecionar no menu)

**Diferença do Teclado:** Só dispara uma vez por pressionamento, não enquanto mantido.

---

### Soltar Teclado
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_release` |
| **Ícone** | ⬆️ |
| **Categoria** | Entrada |
| **Preset** | Completo (Edição Desenvolvimento) |

**Descrição:** Dispara uma vez quando uma tecla é solta.

**Usos comuns:**
- Parar movimento quando tecla é solta
- Terminar ataques carregados
- Alternar estados

---

### Teclado (Nenhuma tecla)
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `keyboard_no_key` |
| **Ícone** | ⌨️ |
| **Categoria** | Entrada |
| **Preset** | Iniciante |

**Descrição:** Dispara a cada quadro enquanto **nenhuma** tecla está sendo mantida.

**Quando dispara:** A cada quadro em que o teclado está inativo, *antes* do evento Step.

**Usos comuns:**
- Parar o movimento quando o jogador solta todas as teclas (jogos de grade/labirintos)
- Animações em repouso

---

### Mouse
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `mouse` |
| **Ícone** | 🖱️ |
| **Categoria** | Entrada |
| **Preset** | Completo (Edição Desenvolvimento) |

**Descrição:** Eventos de botão do mouse e movimento.

**Tipos de Eventos:**

| Tipo | Descrição |
|------|-----------|
| Botão Esquerdo | Clique com botão esquerdo do mouse |
| Botão Direito | Clique com botão direito do mouse |
| Botão do Meio | Clique com botão do meio/scroll |
| Entrada do Mouse | Cursor entra nos limites da instância |
| Saída do Mouse | Cursor sai dos limites da instância |
| Botão Esquerdo Global | Clique esquerdo em qualquer lugar |
| Botão Direito Global | Clique direito em qualquer lugar |

---

## Outras Categorias de Eventos

- [Eventos de Objeto](Event-Reference-Object_pt) - Create, Step, Destroy
- [Eventos de Colisão](Event-Reference-Collision_pt) - Colisões de objetos
- [Eventos de Tempo](Event-Reference-Timing_pt) - Alarmes, Variantes de Step
- [Eventos de Desenho](Event-Reference-Drawing_pt) - Renderização personalizada
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Eventos de Jogo](Event-Reference-Game_pt) - Início/Fim do jogo
- [Outros Eventos](Event-Reference-Other_pt) - Limites, Vidas, Saúde

[← Voltar à Referência de Eventos](Event-Reference_pt)
