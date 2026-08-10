# Programação Visual

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Voltar ao Início](Home_pt)

O PyGameMaker inclui o Google Blockly para programação visual de arrastar e soltar. Construa a lógica do seu jogo conectando blocos, em vez de escrever código.

---

## Acessar o Blockly

1. Abra um objeto no Editor de Objetos
2. Clique no separador **🧩 Blockly** (ao lado de Event List e Editor de Código)
3. A área de trabalho do Blockly aparece com uma barra de ferramentas à esquerda

![Os separadores Event List / Blockly / Editor de Código do Editor de
Objetos — clicar em Blockly muda as ações do mesmo evento para a vista
de blocos arrastar-e-largar](images/object-editor.png)

*(A própria área de trabalho do Blockly é um componente web e não foi
capturada aqui — veja [[Code-Editor_pt|Editor de Código]] para ver como
é o Python gerado equivalente para o mesmo evento.)*

**Os blocos que você vê dependem da sua predefinição.**
`Tools > Configure Action Blocks...` (ou `Preferences > IDE Edition`,
que define a predefinição padrão para novos projetos) controla o
conjunto de blocos — veja o [Guia de Predefinições](Preset-Guide_pt)
para detalhes. As tabelas abaixo listam todos os blocos que existem em
qualquer predefinição; um projeto concreto pode mostrar menos.

---

## A Área de Trabalho do Blockly

### Barra de Ferramentas
O painel esquerdo contém as categorias de blocos:
- **Events** - Blocos de disparo de evento
- **Control** - Condições, variáveis e agrupamento (os blocos
  condicionais deste projeto são blocos empilháveis, não contêineres
  If/Else clássicos — veja "Tipos de Bloco" abaixo)
- **Movement** - Blocos de movimento, velocidade e física
- **Timing** - Alarmes
- **Drawing** - Blocos de texto e formas
- **Score/Lives/Health** - Blocos de estado do jogo
- **Instance** - Criação/destruição de objetos
- **Room** - Navegação entre salas
- **Values** - Blocos de valor (posição, velocidade, pontuação, vidas,
  saúde, mouse)
- **Sound** - Reprodução de áudio
- **Output** - Mensagens e código Python personalizado
- **Game** - Encerrar/reiniciar o jogo, placar

Não existe uma categoria separada de Math, Text ou Logic — os campos
numéricos/de texto são preenchidos diretamente em cada bloco, e não
existe um bloco de valor booleano/de comparação genérico. Veja "Tipos
de Bloco" abaixo para como as condições funcionam em vez disso.

### Área de Trabalho
A zona central onde você constrói seu programa:
- Arrastando blocos da barra de ferramentas
- Conectando blocos entre si
- Configurando os parâmetros dos blocos

### Lixeira
Arraste blocos indesejados para cá para excluí-los, ou pressione a tecla Delete.

---

## Tipos de Bloco

### Blocos de Chapéu (Events)
Os blocos de chapéu têm um topo arredondado e iniciam uma sequência. Eles representam eventos:

```
┌─────────────────┐
│ When Create     │
└─────────────────┘
```

### Blocos Empilháveis (Ações)
Os blocos empilháveis têm encaixes que se conectam com outros blocos.
Quase todos os blocos fora da categoria Values são blocos empilháveis
— incluindo os blocos condicionais:

```
├─────────────────┤
│ Set Horizontal Speed [5] │
├─────────────────┤
```

### Blocos de Valor (Values)
Os blocos de valor são arredondados e se encaixam em um campo numérico
de outro bloco (por exemplo, o campo de velocidade de Move Direction,
ou o campo de valor de Set Variable). Este projeto tem 9 — X Position,
Y Position, Horizontal Speed, Vertical Speed, Score, Lives, Health,
Mouse X, Mouse Y:

```
( X Position )    ( Score )    ( 100 )
```

Não existe um bloco de valor genérico `( speed )` ou `( direction )` —
esses conceitos não são rastreados como um valor único neste motor (a
velocidade/direção de movimento surgem juntas de Horizontal Speed +
Vertical Speed), e também não existe um bloco de valor para variáveis
personalizadas (leia-as em vez disso através da comparação de Test
Variable).

### Condições — blocos empilháveis, não contêineres em C
Diferente das linguagens visuais estilo Scratch, os blocos If
Condition / Test Variable deste projeto são **blocos empilháveis com
um único slot "then"**, não contêineres If/Else de dois lados, e não
existe um bloco booleano hexagonal para encaixar — a comparação é
construída diretamente através de campos no bloco:

```
┌───────────────────────────────────┐
│ If count of [obj_coin] [==] [0]   │
├───────────────────────────────────┤
│  then [ações aqui]                │
└───────────────────────────────────┘
```

Para adicionar um ramo "else" ou executar várias ações de um lado,
combine-o com mais três blocos Control:
- **Else** - executa seu próprio bloco seguinte apenas se o teste
  anterior era falso
- **Start Block** / **End Block** - agrupam várias ações, para que o
  teste anterior (ou Else) atue sobre todo o grupo, não apenas sobre o
  bloco seguinte

Este é o mesmo fluxo condicional plano, no estilo GM80, usado também
pelo painel estruturado Events/Actions (veja [Eventos e
Ações](Eventos_e_Acoes_pt)) — o Blockly é uma interface de arrastar e
soltar sobre a mesma lista de ações subjacente, não um modelo de
execução separado.

---

## Blocos de Evento

### Evento Create
```
┌─────────────────────┐
│ When Create         │
├─────────────────────┤
│ [ações aqui]          │
└─────────────────────┘
```

### Evento Step
```
┌─────────────────────┐
│ When Step            │
├─────────────────────┤
│ [cada quadro]          │
└─────────────────────┘
```

### Eventos de Teclado
Existem quatro blocos de chapéu de teclado separados — Held, Press,
Release e No Key — cada um com um menu suspenso para o nome da tecla
(No Key não tem um, pois é disparado quando nada está pressionado):
```
┌─────────────────────────┐
│ When key [held: left] ▼ │
├─────────────────────────┤
│ [ações aqui]              │
└─────────────────────────┘
```

### Eventos de Colisão
```
┌────────────────────────────┐
│ When colliding with [obj] ▼│
├────────────────────────────┤
│ [ações aqui]                 │
└────────────────────────────┘
```

---

## Blocos de Movimento

| Bloco | Descrição |
|------|-------------|
| `Set Horizontal Speed [4]` | Define a velocidade X |
| `Set Vertical Speed [-5]` | Define a velocidade Y |
| `Stop Movement` | Zera ambas as velocidades |
| `Move [direction ▼] speed [3]` | Move em uma de 4 direções (ou diagonais, ou "stop") |
| `Move Free [direction] [speed]` | Move com ângulo e velocidade arbitrários |
| `Set Speed [5]` | Define a magnitude da velocidade, mantendo a direção atual |
| `Set Direction [90]` | Define o ângulo de direção, mantendo a velocidade atual |
| `Move Towards x:[100] y:[200] speed:[3]` | Move em direção a um ponto |
| `Snap to Grid` | Alinha a posição à grade |
| `Jump to Position x:[100] y:[200]` | Teletransporte instantâneo |
| `Move Grid [direction]` | Move exatamente uma célula da grade |
| `Stop if No Keys` / `Check Keys and Move` / `If On Grid` | Blocos auxiliares para movimento em grade |
| `Set Gravity` | Aplica uma força constante a cada quadro (para baixo ou em qualquer direção) |
| `Set Friction` | Aplica uma redução de velocidade a cada quadro |
| `Reverse Horizontal` / `Reverse Vertical` | Inverte a direção X ou Y |
| `Bounce` | Ricocheteia em objetos sólidos |
| `Wrap Around Room` | Reaparece do lado oposto |
| `Move to Contact` | Move até tocar em algo |

Não existe um bloco "Jump to Start Position" ou "Jump to Random
Position" — essas duas ações existem apenas no painel estruturado, não
no Blockly.

---

## Blocos de Desenho

| Bloco | Descrição |
|------|-------------|
| `Draw Text [Olá] at x:[10] y:[10]` | Mostra texto |
| `Draw Rectangle from x1,y1 to x2,y2` | Desenha um retângulo preenchido |
| `Draw Circle at x,y radius [r]` | Desenha um círculo preenchido |
| `Set Sprite [spr]` | Muda o sprite da instância |
| `Set Transparency [0-1]` | Define o alfa |

Não existe um bloco "Draw Sprite em Posição" ou "Set Drawing Color" no
Blockly (ambos existem apenas no painel estruturado). Draw Score/Draw
Lives/Draw Health Bar estão listados abaixo em Score/Lives/Health, não
aqui.

---

## Blocos Score/Lives/Health

| Bloco | Descrição |
|------|-------------|
| `Set Score [100]` | Define exatamente a pontuação |
| `Add to Score [10]` | Aumenta/diminui a pontuação |
| `Set Lives [3]` | Define exatamente as vidas |
| `Add to Lives [-1]` | Aumenta/diminui as vidas |
| `Set Health [100]` | Define exatamente a saúde |
| `Add to Health [-25]` | Aumenta/diminui a saúde |
| `Draw Score` | Mostra o texto da pontuação |
| `Draw Lives` | Mostra as vidas como ícones repetidos |
| `Draw Health Bar` | Mostra a saúde como uma barra de duas cores |

---

## Blocos de Instância

| Bloco | Descrição |
|------|-------------|
| `Create Instance [obj] at x:[100] y:[200]` | Cria uma nova instância |
| `Destroy Instance` | Remove a si mesma |
| `Destroy Other` | Remove a instância em colisão (em um evento Collision) |
| `Change Instance [obj]` | Se transforma em outro tipo de objeto |
| `If Can Push [obj] [direction]` | Verificação de empurrar estilo Sokoban |

Não existe um bloco "destruir todos de um tipo" ou "criar nesta posição".

---

## Blocos de Sala

| Bloco | Descrição |
|------|-------------|
| `Next Room` | Vai para a próxima sala |
| `Previous Room` | Volta para a sala anterior |
| `Restart Room` | Reinicia a sala atual |
| `Go to Room [room_name]` | Salta para uma sala específica |
| `If Next Room Exists` / `If Previous Room Exists` | Protege a navegação entre várias salas |

---

## Blocos de Som

| Bloco | Descrição |
|------|-------------|
| `Play Sound [snd]` | Reproduz um efeito sonoro |
| `Play Music [music]` | Reproduz música de fundo (em loop) |
| `Stop Music` | Para a música |

Não existe um bloco "Stop Sound" (por som) ou "Parar todos os sons" no
Blockly (apenas Stop Music, que para especificamente a música).

---

## Blocos de Controle

| Bloco | Descrição |
|------|-------------|
| `If count of [obj] [==] [0] then...` | Compara o número de instâncias de um objeto; executa o(s) bloco(s) seguinte(s) se verdadeiro |
| `If variable [var] [==] [value] then...` | Compara uma variável personalizada; executa o(s) bloco(s) seguinte(s) se verdadeiro |
| `Set Variable [name] to [value]` | Atribui uma variável de instância ou global |
| `Check Empty at x,y` | Verdadeiro se uma posição não tem colisão (movimento em grade) |
| `Exit Event` | Interrompe as ações restantes deste evento |
| `Else` | Executa seu próprio bloco seguinte se o teste anterior era falso |
| `Start Block` / `End Block` | Agrupa várias ações sob um Test/Else |

---

## Blocos de Output e Game

| Bloco | Descrição |
|------|-------------|
| `Show Message [text]` | Mostra uma mensagem pop-up |
| `Execute Code` | Executa Python real (veja [Eventos e Ações](Eventos_e_Acoes_pt)) |
| `End Game` | Fecha o jogo |
| `Restart Game` | Reinicia a partir da primeira sala |
| `Show Highscore` / `Clear Highscore` | Mostra ou limpa o placar |

---

## Blocos de Valor

Blocos de valor — encaixe-os em um campo numérico de outro bloco:

| Bloco | Descrição |
|------|-------------|
| `X Position` | A coordenada X desta instância |
| `Y Position` | A coordenada Y desta instância |
| `Horizontal Speed` | A velocidade X desta instância |
| `Vertical Speed` | A velocidade Y desta instância |
| `Score` | A pontuação atual |
| `Lives` | As vidas atuais |
| `Health` | A saúde atual |
| `Mouse X` / `Mouse Y` | A posição atual do mouse |

---

## Exemplo: Movimento do Jogador

```
┌──────────────────────────┐
│ When key [held: left]    │
├──────────────────────────┤
│ Set Horizontal Speed [-4]│
└──────────────────────────┘

┌──────────────────────────┐
│ When key [held: right]   │
├──────────────────────────┤
│ Set Horizontal Speed [4] │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [no key]        │
├──────────────────────────┤
│ Set Horizontal Speed [0] │
└──────────────────────────┘
```

---

## Exemplo: Coletar Moedas

```
┌─────────────────────────────┐
│ When colliding with obj_coin│
├─────────────────────────────┤
│ Add to Score [10]           │
├─────────────────────────────┤
│ Play Sound [snd_coin]       │
├─────────────────────────────┤
│ Destroy Other                │
└─────────────────────────────┘
```

---

## Dicas

1. **Comece com Events** - Sempre comece com um bloco Event (bloco de chapéu)
2. **Conecte verticalmente** - Os blocos empilháveis se conectam de cima para baixo
3. **Use as cores** - As cores dos blocos indicam sua categoria
4. **Clique direito** - Acesse Duplicar, Excluir e Ajuda
5. **Zoom** - Use a roda do mouse ou os controles de zoom para programas grandes
6. **Mude para o painel estruturado** - Tudo o que o Blockly pode fazer
   corresponde a uma ação na aba Events do painel estruturado, mas não
   o contrário (por exemplo, Jump to Start/Random Position e Stop
   Sound por som não têm bloco no Blockly) — nesses casos, use o
   painel estruturado em vez do Blockly.

---

## Próximos Passos

- [[Eventos_e_Acoes_pt]] - Veja o equivalente como lista de ações
- [[Primeiro_Jogo_pt]] - Construa um jogo completo
- [[Editor_Objetos_pt]] - Onde o Blockly está integrado
- [[Preset-Guide_pt]] - Quais blocos estão disponíveis no seu projeto
