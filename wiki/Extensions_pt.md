# Extensões

*[Início](Home_pt) | [Vista 3D](3D-View_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

---

Uma **extensão** é um complemento autônomo que adiciona capacidades ao PyGameMaker
sem modificar o motor base. Uma extensão pode contribuir:

- novas **ações** (aparecem no seletor de ações como qualquer ação integrada),
- uma nova forma de **desenhar uma sala** (um renderizador personalizado), e
- o **código de exportação** correspondente, para que os jogos que a usam continuem
  exportando para HTML5 e Kivy/Android.

A extensão integrada **2.5D Raycast** (a função [Vista 3D](3D-View_pt)) é o exemplo de
referência: adiciona quatro ações "Vista 3D" e um renderizador em primeira pessoa, e
exporta para os três destinos.

---

## Ativar e desativar

As extensões são entregues **ativadas**. Você pode desativar uma (ou ativar uma que é
entregue desativada) sem editar código, através da chave `extensions` na sua
configuração — um mapa `nome da pasta → ativado/desativado`:

```json
"extensions": { "raycast_2_5d": false }
```

Uma entrada **ausente** significa "usar o valor padrão da extensão", então nada nunca
desaparece porque uma chave estava faltando. As mudanças têm efeito na próxima
inicialização (as ações se registram na inicialização).

Com a extensão 2.5D Raycast desativada, uma sala que ativa a vista em primeira pessoa
simplesmente renderiza de cima.

---

## Quando um projeto precisa de uma extensão

Como uma extensão pode ser desativada, o PyGameMaker ajuda você a evitar surpresas:

- **Ao carregar**, se um projeto usa ações de uma extensão atualmente desativada, o
  IDE mostra um aviso que nomeia a extensão e as funções afetadas (para que um jogo 3D
  não renderize de cima silenciosamente).
- **Ao salvar**, o projeto registra as extensões das quais suas ações dependem em
  `project.json` (uma lista `requires_extensions`) — uma nota duradoura que qualquer
  pessoa com quem você compartilhe o projeto pode ver. Um projeto que não usa ações de
  extensões simplesmente omite o campo.

---

## Extensões e plugins

Ambos adicionam ações; diferem apenas no empacotamento:

| | Plugin | Extensão |
|---|--------|-----------|
| Forma | um único arquivo `.py` em `plugins/` | uma pasta em `extensions/` com um manifesto |
| Ideal para | um pequeno conjunto de ações | uma função que abrange vários arquivos e/ou que desenha/exporta |
| Exemplo | as ações **Audio** (`plugins/audio_actions.py`) | **2.5D Raycast** (`extensions/raycast_2_5d/`) |

---

## Como é uma pasta de extensão

Para os curiosos (e para quem escreve uma), uma extensão é uma pasta legível:

```
extensions/raycast_2_5d/
├── extension.json     # manifesto: nome, versão, ativado, provides_actions
├── actions.py         # os esquemas de ações (mostrados no seletor)
├── handlers.py        # o que as ações fazem em execução
├── renderer.py        # o renderizador de sala personalizado (o raycaster)
├── state.py           # o estado por sala (no espaço de nomes da sala)
├── hud.py             # os geradores de geometria de minimapa / barra DOOM
├── export_html5.js    # o port HTML5, injetado na exportação web
├── export_kivy.py     # o port Kivy, injetado na exportação móvel/computador
└── README.md          # como tudo se encaixa
```

A lista `provides_actions` do manifesto é o que permite ao IDE nomear a extensão exata
quando um projeto precisa de uma desativada.

---

## Veja também

- [Vista 3D](3D-View_pt) — a função que a extensão integrada fornece
- [Referência completa de ações](Full-Action-Reference_pt) — as ações de extensão também aparecem aqui
- [Exportar jogos](Exportar_Jogos_pt) — as funções de extensão são transferidas para as exportações
