# Eventos de Objeto

*[Início](Home_pt) | [Referência de Eventos](Event-Reference_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

### Create
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `create` |
| **Ícone** | 🎯 |
| **Categoria** | Objeto |
| **Preset** | Iniciante |

**Descrição:** Executado uma vez quando uma instância é criada pela primeira vez.

**Quando dispara:**
- Quando uma instância é colocada em uma sala no início do jogo
- Quando criada via ação "Criar Instância"
- Após transições de sala para novas instâncias

**Usos comuns:**
- Inicializar variáveis
- Definir valores iniciais
- Configurar estado inicial

---

### Step
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `step` |
| **Ícone** | ⭐ |
| **Categoria** | Objeto |
| **Preset** | Iniciante |

**Descrição:** Executado a cada quadro (tipicamente 60 vezes por segundo).

**Quando dispara:** Continuamente, a cada quadro do jogo.

**Usos comuns:**
- Movimento contínuo
- Verificar condições
- Atualizar posições
- Lógica do jogo

**Nota:** Cuidado com o desempenho - o código aqui executa constantemente.

---

### Destroy
| Propriedade | Valor |
|-------------|-------|
| **Nome** | `destroy` |
| **Ícone** | 💥 |
| **Categoria** | Objeto |
| **Preset** | Intermediário |

**Descrição:** Executado quando uma instância é destruída.

**Quando dispara:** Logo antes da instância ser removida do jogo.

**Usos comuns:**
- Gerar efeitos (explosões, partículas)
- Soltar itens
- Atualizar pontuações
- Tocar sons

---

## Outras Categorias de Eventos

- [Eventos de Entrada](Event-Reference-Input_pt) - Teclado, Mouse
- [Eventos de Colisão](Event-Reference-Collision_pt) - Colisões de objetos
- [Eventos de Tempo](Event-Reference-Timing_pt) - Alarmes, Variantes de Step
- [Eventos de Desenho](Event-Reference-Drawing_pt) - Renderização personalizada
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Eventos de Jogo](Event-Reference-Game_pt) - Início/Fim do jogo
- [Outros Eventos](Event-Reference-Other_pt) - Limites, Vidas, Saúde

[← Voltar à Referência de Eventos](Event-Reference_pt)
