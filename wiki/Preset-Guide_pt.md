# Guia de Predefinições

*[Português](Preset-Guide_pt) | [Voltar ao Início](Home_pt)*

PyGameMaker oferece diferentes predefinições que controlam quais eventos e ações estão disponíveis. Isso ajuda iniciantes a focar nas funcionalidades essenciais enquanto permite que usuários experientes acessem o conjunto completo de ferramentas.

## Escolha Seu Nível

| Predefinição | Ideal Para | Funcionalidades |
|--------------|------------|-----------------|
| [**Iniciante**](Beginner-Preset_pt) | Novos em desenvolvimento de jogos | 4 eventos, 17 ações - Movimento, colisões, pontuação, salas |
| [**Intermediário**](Intermediate-Preset_pt) | Alguma experiência | +4 eventos, +12 ações - Vidas, saúde, som, alarmes, desenho |
| **Avançado** | Usuários experientes | Todos os 40+ eventos e ações disponíveis |

---

## Documentação de Predefinições

### Predefinições
| Página | Descrição |
|--------|-----------|
| [Predefinição Iniciante](Beginner-Preset_pt) | 4 eventos, 17 ações - Funcionalidades essenciais |
| [Predefinição Intermediário](Intermediate-Preset_pt) | +4 eventos, +12 ações - Vidas, saúde, som |

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

**Teclado (Teclas de Seta):**
```
Seta Esquerda  → Definir Velocidade Horizontal: -4
Seta Direita   → Definir Velocidade Horizontal: 4
Seta Cima      → Definir Velocidade Vertical: -4
Seta Baixo     → Definir Velocidade Vertical: 4
```

**Colisão com obj_coin:**
```
Adicionar Pontuação: 10
Destruir Instância: other
```

**Colisão com obj_wall:**
```
Parar Movimento
```

### 3. Criar uma Sala
- Posicione o jogador
- Adicione algumas moedas
- Adicione paredes ao redor das bordas

### 4. Execute o Jogo!
Pressione o botão Jogar para testar seu jogo.

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
- [Primeiros Passos](Primeiros_Passos_pt) - Instalação e configuração
- [Eventos e Ações](Eventos_e_Acoes_pt) - Conceitos básicos
- [Crie Seu Primeiro Jogo](Primeiro_Jogo_pt) - Tutorial
