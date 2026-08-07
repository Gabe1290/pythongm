# Editor de Salas

> [English](Room-Editor) | [Français](Editeur_Salles_fr) | [Deutsch](Raum_Editor_de) | [Italiano](Editor_Stanze_it) | [Español](Editor_Salas_es) | [Português](Editor_Salas_pt) | [Slovenščina](Urejevalnik_Sob_sl) | [Українська](Redaktor_Kimnat_uk) | [Русский](Redaktor_Komnat_ru)

---

[Voltar ao Início](Home_pt)

Salas são os níveis, ecrãs ou cenas do seu jogo. O Editor de Salas
permite-lhe desenhar estes espaços colocando objetos e configurando
fundos.

---

## Abrir o Editor de Salas

1. Clique duas vezes numa sala existente na árvore de recursos, ou
2. Clique com o botão direito em **Rooms** > **Create Room**

---

## Propriedades da Sala

| Propriedade | Descrição |
|-----------|-------------|
| **Name** | Identificador único (ex. `room_nivel1`) |
| **Width** | Largura da sala em píxeis |
| **Height** | Altura da sala em píxeis |
| **Speed** | Velocidade do jogo em quadros por segundo (padrão: 60) |
| **Persistent** | Mantém o estado da sala ao sair/voltar a entrar |

### Convenção de Nomes

Use o prefixo `room_` para as salas:
- `room_menu`
- `room_nivel1`
- `room_game_over`

---

## Colocar Objetos

### Adicionar Instâncias

1. Selecione um objeto no painel **Objects**
2. Clique na vista da sala para colocar uma instância
3. Clique e arraste para colocar várias instâncias

### Selecionar Instâncias

- Clique numa instância para a selecionar
- Mantenha **Ctrl** pressionado e clique para selecionar várias
- Desenhe um retângulo para selecionar todas as instâncias dentro dele

### Mover Instâncias

- Arraste as instâncias selecionadas com o rato
- Use as teclas de seta para um movimento preciso

### Eliminar Instâncias

- Selecione as instâncias e prima **Delete**, ou
- Clique com o botão direito e escolha "Eliminar"

---

## Configuração da Grelha

Ative a grelha para uma colocação precisa:

1. Vá a **View > Show Grid**
2. Defina o tamanho da grelha (ex. 32x32)
3. Ative "Snap to Grid"

Tamanhos de grelha comuns:
- **16x16** - Ladrilhos pequenos
- **32x32** - Ladrilhos padrão
- **64x64** - Ladrilhos grandes

---

## Fundos

### Definir um Fundo

1. Clique na aba **Backgrounds**
2. Selecione um recurso de fundo
3. Configure as opções de exibição

### Opções de Fundo

| Opção | Descrição |
|--------|-------------|
| **Visible** | Mostra/oculta o fundo |
| **Foreground** | Desenha à frente dos objetos |
| **Tile Horizontal** | Repete horizontalmente |
| **Tile Vertical** | Repete verticalmente |
| **Stretch** | Estica para preencher a sala |
| **Horizontal Speed** | Velocidade de deslocamento (parallax) |
| **Vertical Speed** | Velocidade de deslocamento (parallax) |

### Camadas de Fundo

Uma sala suporta até **8 camadas de fundo**, cada uma com a sua
própria velocidade de deslocamento para efeitos parallax. Exemplo de
disposição:
- Camada 0: Céu (mais ao fundo)
- Camada 1: Montanhas (deslocamento mais lento)
- Camada 2: Árvores (deslocamento médio)
- Camada 3: Chão (sem deslocamento)

---

## Views (Câmara)

As views controlam qual parte da sala é visível no ecrã. Podem ser
configuradas até **8 views** (View 0 a View 7) por sala — a View 0 é
visível por padrão; ative views adicionais para ecrã dividido ou
imagem-na-imagem.

### Ativar as Views

1. Selecione "Enable Views" nas propriedades da sala
2. Configure a View 0 (a view principal)

### Propriedades das Views

| Propriedade | Descrição |
|-----------|-------------|
| **View X/Y** | Canto superior esquerdo da view na sala |
| **View Width/Height** | Tamanho da área visível |
| **Port X/Y** | Posição no ecrã |
| **Port Width/Height** | Tamanho no ecrã (pode ser esticado) |
| **Object Following** | Objeto que a view segue |
| **Border H/V** | Zona morta antes de a câmara se mover |

### Seguir um Objeto

Para fazer a câmara seguir o jogador:
1. Defina "Object Following" para `obj_player`
2. Ajuste "Border H" e "Border V" para um deslocamento suave

---

## Ordem das Salas

A ordem das salas na árvore de recursos determina:
1. Qual sala carrega primeiro (sala do topo = sala inicial)
2. A ordem para as ações "Next Room" e "Previous Room"

### Alterar a Ordem das Salas

- Arraste as salas na árvore de recursos para as reordenar
- Ou clique com o botão direito e use "Mover para Cima" / "Mover para Baixo"

---

## Dicas e Boas Práticas

### Organização
- Nomeie as salas claramente conforme o seu propósito
- Mantenha o menu principal como primeira sala
- Use tamanhos de sala consistentes dentro de um jogo

### Desempenho
- Não coloque demasiadas instâncias numa sala
- Use ladrilhos para a geometria estática dos níveis
- Destrua as instâncias fora do ecrã quando possível

---

## Próximos Passos

- [[Editor_Objetos_pt]] - Crie objetos para colocar nas salas
- [[Eventos_e_Acoes_pt]] - Adicione interatividade aos seus níveis
- [[Exportar_Jogos_pt]] - Partilhe o seu jogo terminado
