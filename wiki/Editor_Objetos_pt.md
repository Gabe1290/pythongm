# Editor de Objetos

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Voltar ao Início](Home_pt)

Os objetos são os blocos fundamentais de construção do seu jogo.
Representam tudo, desde jogadores e inimigos até colecionáveis e
elementos de interface.

---

## Abrir o Editor de Objetos

1. Clique duas vezes num objeto existente na árvore de recursos, ou
2. Clique com o botão direito em **Objects** > **Create Object**

![O Editor de Objetos: uma lista de eventos à esquerda (Create, Step,
vários eventos Collision, Keyboard, No More Lives, Game Start),
propriedades do objeto (sprite, parent, Visible/Persistent/Solid) à
direita, e os separadores Event List / Blockly / Editor de Código que
mudam a forma de editar as ações de cada evento](images/object-editor.png)

---

## Propriedades do Objeto

| Propriedade | Descrição |
|-----------|-------------|
| **Name** | Identificador único para o objeto (ex. `obj_jogador`) |
| **Sprite** | A representação visual do objeto |
| **Visible** | Se o objeto é desenhado (padrão: sim) |
| **Solid** | Usado para deteção de colisão com objetos sólidos |
| **Depth** | Ordem de desenho (menor = desenhado por cima) |
| **Persistent** | O objeto sobrevive a mudanças de sala |
| **Parent Object** | Herda propriedades/eventos comuns de outro objeto |

### Convenção de Nomes

Use o prefixo `obj_` para os objetos:
- `obj_jogador`
- `obj_inimigo`
- `obj_moeda`
- `obj_parede`

---

## Eventos

Eventos são gatilhos que causam a execução de ações. Clique em "Add
Event" para adicionar um.

### Eventos Comuns

| Evento | Quando Dispara |
|-------|------------------|
| **Create** | Uma vez, quando uma instância é criada |
| **Destroy** | Quando a instância é destruída |
| **Step** | A cada quadro do jogo (60 vezes por segundo) |
| **Draw** | Durante a fase de desenho |
| **Alarm [0-11]** | Quando um temporizador de alarme chega a zero |

### Eventos de Teclado

| Evento | Quando Dispara |
|-------|------------------|
| **Key Press** | Uma vez, quando uma tecla é pressionada |
| **Key Release** | Uma vez, quando uma tecla é solta |
| **Keyboard** | A cada quadro enquanto uma tecla está pressionada |
| **No Key** | Quando nenhuma tecla está pressionada |

### Eventos de Rato

| Evento | Quando Dispara |
|-------|------------------|
| **Mouse Button** | Ao clicar na instância |
| **Global Mouse** | Ao clicar em qualquer lugar |
| **Mouse Enter** | Quando o cursor entra na instância |
| **Mouse Leave** | Quando o cursor sai da instância |

### Eventos de Colisão

| Evento | Quando Dispara |
|-------|------------------|
| **Collision with [objeto]** | Ao tocar noutro tipo de objeto |

### Outros Eventos

| Evento | Quando Dispara |
|-------|------------------|
| **Outside Room** | Quando a instância sai da sala |
| **Intersect Boundary** | Quando a instância toca a borda da sala |
| **Game Start** | Uma vez, ao iniciar o jogo |
| **Game End** | Uma vez, ao fechar o jogo |
| **Room Start** | Ao entrar numa sala |
| **Room End** | Ao sair de uma sala |

---

## Ações

Ações são operações executadas quando um evento dispara. Cada evento
pode ter várias ações, executadas em ordem.

### Ações de Movimento
- **Set Speed** — Define a velocidade de movimento
- **Set Direction** — Define a direção de movimento (0-360 graus)
- **Set Horizontal Speed** — Define hspeed
- **Set Vertical Speed** — Define vspeed
- **Mover para um ponto** — Move em direção a coordenadas
- **Jump to Position** — Teletransporta instantaneamente para coordenadas
- **Saltar para a posição inicial** — Retorna à posição de criação
- **Saltar para posição aleatória** — Teletransporta para uma posição aleatória

### Ações de Instância
- **Create Instance** — Cria um novo objeto
- **Destroy Instance** — Remove a instância atual
- **Change Instance** — Transforma-se noutro tipo de objeto

### Ações de Temporização
- **Set Alarm** — Inicia um temporizador de contagem regressiva
- **Sleep** — Pausa a execução por um breve momento

### Ações de Desenho
- **Draw Sprite** — Desenha um sprite
- **Draw Text** — Mostra texto no ecrã
- **Draw Rectangle** — Desenha um retângulo preenchido ou contornado
- **Desenhar pontuação** — Mostra a pontuação atual
- **Desenhar vidas** — Mostra as vidas restantes
- **Desenhar barra de saúde** — Mostra a barra de saúde

### Score/Lives/Health
- **Set Score** — Altera o valor da pontuação
- **Set Lives** — Altera o número de vidas
- **Set Health** — Altera o valor da saúde
- **Testar pontuação** — Verifica uma condição de pontuação
- **Testar vidas** — Verifica uma condição de vidas
- **Testar saúde** — Verifica uma condição de saúde

### Ações de Sala
- **Next Room** — Vai para a próxima sala
- **Previous Room** — Vai para a sala anterior
- **Restart Room** — Reinicia a sala atual
- **Go to Room** — Salta para uma sala específica

### Ações Sound
- **Play Sound** — Reproduz um efeito sonoro
- **Stop Sound** — Para um som em reprodução
- **Play Music** — Reproduz música de fundo
- **Stop Music** — Para a música de fundo

### Ações de Variáveis
- **Set Variable** — Atribui um valor a uma variável
- **Testar variável** — Verifica uma condição de variável

---

## Programação Visual com Blockly

Em vez de usar a lista de ações, pode mudar para a aba **Blockly** para
programação visual:

1. Abra um objeto
2. Clique na aba **Blockly**
3. Arraste blocos da barra de ferramentas para criar a lógica
4. Os blocos encaixam-se para formar programas completos

Veja [[Programacao_Visual_pt]] para mais detalhes.

---

## Dicas e Boas Práticas

### Organização
- Dê nomes descritivos aos objetos
- Agrupe objetos relacionados com prefixos semelhantes
- Use o evento Create apenas para inicialização

### Desempenho
- Evite cálculos pesados no evento Step
- Use alarmes em vez de contar quadros manualmente
- Destrua as instâncias que saem da sala

### Depuração
- Use a ação **Show Message** para mostrar valores
- Verifique a saída da consola para erros
- Teste frequentemente enquanto desenvolve

---

## Exemplo: IA Simples para Inimigo

```
Create Event:
  - Set Alarm[0] = 60 (1 segundo a 60 FPS)
  - Set direction = random(360)
  - Set speed = 2

Alarm[0] Event:
  - Set direction = random(360)
  - Set Alarm[0] = 60

Collision with obj_player:
  - Set Lives relative = -1
  - Destroy Instance
```

---

## Próximos Passos

- [[Editor_Salas_pt]] - Coloque objetos nos seus níveis de jogo
- [[Eventos_e_Acoes_pt]] - Referência completa de todos os eventos e ações
- [[Programacao_Visual_pt]] - Aprenda a programação por blocos com Blockly
