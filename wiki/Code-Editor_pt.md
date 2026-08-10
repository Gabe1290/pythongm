# Editor de Código

> [English](Code-Editor) | [Français](Code-Editor_fr) | [Deutsch](Code-Editor_de) | [Italiano](Code-Editor_it) | [Español](Code-Editor_es) | [Português](Code-Editor_pt)

---

> [Voltar ao Início](Home_pt)

Cada objeto no PyGameMaker tem um separador **Editor de Código** ao lado
de Event List e Blockly — uma terceira forma de trabalhar com os mesmos
eventos e ações, desta vez como Python real. Não é uma exportação de
sentido único: o código que escreve aqui é reanalisado e transformado em
eventos e ações estruturados, mantendo-se assim sincronizado com as
outras duas vistas.

---

## Abrir o Editor de Código

1. Abra um objeto no Editor de Objetos
2. Clique no separador **💻 Editor de Código**

![O Editor de Código no modo "Ver Código Gerado": uma classe com um
método por evento (on_create, on_step, on_collision_obj_power, ...),
mostrando o verdadeiro Python para o qual os seus eventos e ações
visuais compilam](images/code-editor.png)

---

## Dois Modos

Um menu suspenso no topo alterna entre eles:

### 📖 Ver Código Gerado

Apenas leitura. Mostra o Python para o qual os eventos e ações atuais do
seu objeto compilam — um método por evento (`on_create`, `on_step`,
`on_collision_obj_inimigo`, ...), chamando `self.*` e `game.*` exatamente
como faz o motor de execução. Uma ação para a qual o gerador não tem uma
correspondência Python limpa aparece na mesma, assinalada com um
comentário (`# Unknown action: ...`) acima da linha que produziu — nada
fica escondido, mesmo em casos limite. Clique em **🔄 Atualizar** para
regenerar depois de alterar eventos noutro sítio.

### ✏️ Editar Código Personalizado

Editável, com realce de sintaxe Python. Comece a digitar (ou edite o
código inicial herdado do modo Ver) e o PyGameMaker analisa a sua classe
cerca de 1,5 segundos depois de parar de digitar — uma pastilha de
estado junto à barra de ferramentas mostra **idle / busy / error /
empty** entretanto. Após uma análise bem-sucedida, os seus métodos
**substituem** os eventos e ações do objeto (sem fusão) — quaisquer
métodos de evento que o seu código defina tornam-se a lista de eventos
desse objeto, visível de imediato também nos separadores Event List e
Blockly.

Se a análise falhar (um erro de sintaxe, ou código que o analisador não
consegue reconduzir a eventos), a pastilha de estado mostra o erro e
nada é aplicado — os eventos do seu objeto permanecem como estavam até o
código ser analisado corretamente.

---

## Porquê Usá-lo

- **Rapidez** — alguma lógica (um cálculo com vários ramos, um ciclo,
  uma fórmula pontual) escreve-se mais depressa do que se monta com
  blocos ou uma lista de ações.
- **Ponte de aprendizagem** — mude os eventos de um objeto construído
  por um principiante para o modo Ver para ver o equivalente em código
  real, um passo natural seguinte para um aluno que passa da
  programação visual para Python.
- **Precisão** — tudo o que se exprima como um método Python simples no
  objeto funciona, sem esperar que exista uma ação visual correspondente.

Este é o mesmo mecanismo subjacente da ação **Executar Código**
disponível a partir da lista de ações / Blockly (categoria *Control*) —
o separador Editor de Código trabalha simplesmente à escala de um
objeto inteiro em vez de uma única ação.

---

## Próximos Passos

- [[Editor_Objetos_pt|Editor de Objetos]] - Onde se encontra o separador Editor de Código
- [[Programacao_Visual_pt|Programação Visual]] - A vista Blockly dos mesmos eventos
- [[Eventos_e_Acoes_pt|Eventos e Ações]] - O que cada ação realmente faz
