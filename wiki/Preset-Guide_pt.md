# Guia de Predefinições

*[Português](Preset-Guide_pt) | [Voltar ao Início](Home_pt)*

PyGameMaker oferece diferentes predefinições que controlam quais
eventos e ações estão disponíveis — **tanto** na paleta visual de
blocos Blockly quanto no painel estruturado Events/Actions ("Add
Event"/"Add Action") que todo tutorial deste wiki utiliza. Isso ajuda
iniciantes a focar nas funcionalidades essenciais enquanto permite que
usuários experientes acessem o conjunto completo de ferramentas.

A predefinição de um projeto é definida de duas formas:
**`Preferences > IDE Edition`** escolhe a padrão para projetos *novos*
(projetos existentes nunca são alterados ao trocar de edição), e
**`Tools > Configure Action Blocks...`** muda a predefinição do
projeto *atualmente aberto* a qualquer momento. A edição padrão da IDE
é Iniciante, então novos projetos de uma instalação limpa já começam
na predefinição Iniciante.

## Escolha Seu Nível

| IDE Edition | Ideal Para | Predefinição usada |
|--------|------------|----------|
| **Iniciante** (padrão) | Novos usuários | [Predefinição Iniciante](Beginner-Preset_pt) — movimento básico, colisões, pontuação, salas |
| **Avançado** | Alguma experiência | [Predefinição Intermediária](Intermediate-Preset_pt) — + vidas, saúde, som, alarmes, movimento em grade |
| **Desenvolvimento** | Usuários experientes | A predefinição `full` — todos os eventos e ações disponíveis |

Observe que os nomes não correspondem 1:1: a edição "Avançado" usa a
predefinição `intermediate` (não existe uma predefinição "avançada"
separada) — veja
[Predefinição Iniciante](Beginner-Preset_pt)/[Predefinição Intermediária](Intermediate-Preset_pt)
para os números exatos e sempre atualizados de eventos e ações de
cada uma.

---

## Documentação de Predefinições

### Predefinições
| Página | Descrição |
|--------|-----------|
| [Predefinição Iniciante](Beginner-Preset_pt) | Funcionalidades essenciais — números exatos nessa página |
| [Predefinição Intermediária](Intermediate-Preset_pt) | Adiciona vidas, saúde, som, alarmes, movimento em grade — números exatos nessa página |

### Referência
| Página | Descrição |
|--------|-----------|
| [Referência de Eventos](Event-Reference_pt) | Lista completa de todos os eventos |
| [Referência de Ações](Full-Action-Reference_pt) | Lista completa de todas as ações |

---

## Exemplo de Início Rápido

Aqui está um simples jogo de coleta de moedas usando apenas funcionalidades Iniciante:

### 1. Criar Objetos
- `obj_player` - O personagem controlável
- `obj_coin` - Itens colecionáveis
- `obj_wall` - Obstáculos sólidos

### 2. Adicionar Eventos ao Jogador

**Keyboard (Arrow Keys):**
```
Left Arrow  → Set Horizontal Speed: -4
Right Arrow → Set Horizontal Speed: 4
Up Arrow    → Set Vertical Speed: -4
Down Arrow  → Set Vertical Speed: 4
```

**Collision with obj_coin:**
```
Add Score: 10
Destroy Instance: other
```

**Collision with obj_wall:**
```
Stop Movement
```

### 3. Criar uma Sala
- Posicione o jogador
- Adicione algumas moedas
- Adicione paredes ao redor das bordas

### 4. Execute o Jogo!
Pressione o botão Play para testar seu jogo.

---

## Dicas para o Sucesso

1. **Comece Simples** - Use primeiro a predefinição Iniciante
2. **Teste Frequentemente** - Execute seu jogo frequentemente para detectar problemas
3. **Uma Coisa de Cada Vez** - Adicione funcionalidades gradualmente
4. **Use Colisões** - A maioria das mecânicas de jogo envolve eventos de colisão
5. **Leia a Documentação** - Consulte as páginas de referência quando estiver travado

---

## Veja Também

- [Início](Home_pt) - Página principal da wiki
- [Primeiros Passos](Comecar_pt) - Instalação e configuração
- [Eventos e Ações](Eventos_e_Acoes_pt) - Conceitos básicos
- [Crie Seu Primeiro Jogo](Primeiro_Jogo_pt) - Tutorial
- [Tutorial Breakout](Tutorial-Breakout_pt) - Crie um jogo Breakout clássico
- [Introdução à Criação de Jogos](Getting-Started-Breakout_pt) - Tutorial completo para iniciantes
