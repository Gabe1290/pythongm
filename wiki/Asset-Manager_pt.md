# Gestor de Recursos

> [English](Asset-Manager) | [Français](Asset-Manager_fr) | [Deutsch](Asset-Manager_de) | [Italiano](Asset-Manager_it) | [Español](Asset-Manager_es) | [Português](Asset-Manager_pt) | [Русский](Asset-Manager_ru) | [Slovenščina](Asset-Manager_sl) | [Українська](Asset-Manager_uk)

---

> [Voltar ao Início](Home_pt)

Para além do criar/renomear/eliminar do dia a dia na árvore de recursos,
o PyGameMaker regista **onde cada recurso é realmente usado**, mantém os
recursos eliminados recuperáveis em vez de os perder para sempre, e pode
encontrar tanto recursos não utilizados como ficheiros órfãos que
entopem a pasta do projeto. Tudo isto vive no menu **Ferramentas**.

---

## Filtrar a Árvore de Recursos

Digite na caixa de filtro acima da árvore de recursos para a restringir
aos nomes correspondentes à medida que digita. A correspondência ignora
maiúsculas/minúsculas e incide sobre o nome bruto do recurso; uma
categoria (Sprites, Objetos, ...) esconde-se assim que todos os seus
elementos filhos são filtrados, e reaparece assim que um voltar a
corresponder.

---

## Rastreio de Utilização

Cada eliminação de recurso verifica agora onde esse recurso é realmente
referenciado — outros objetos, salas, ações — antes de confirmar. Se
`spr_jogador` for usado por 3 objetos, a confirmação de eliminação
indica isso em vez de um aviso genérico, para que saiba *antes* de
eliminar algo que quebraria outras partes do projeto, não depois.

**Limitação conhecida:** esta análise só vê aquilo que as estruturas de
dados do próprio PyGameMaker conseguem ver — parâmetros de ação, alvos
de colisão, instâncias de sala, campos sprite/parent. Um nome de recurso
usado apenas dentro de uma string Python em bruto no
[[Code-Editor_pt|Editor de Código]] ou na ação Executar Código (por
exemplo `game.sounds['explosion'].play()`) não é visível para esta
análise.

---

## Restaurar Recursos Eliminados (Lixo)

**Ferramentas > Restaurar Recursos Eliminados...**

Eliminar um recurso não o apaga imediatamente — os seus ficheiros são
movidos para um Lixo local ao projeto e o PyGameMaker mantém um registo
do que foi eliminado, para onde foram os seus ficheiros, e quaisquer
referências cruzadas que foram limpas (por exemplo, o campo sprite de
um objeto que fica vazio porque o sprite a que apontava foi eliminado).
Esta caixa de diálogo lista tudo o que está atualmente no Lixo com três
ações:

| Ação | Efeito |
|--------|--------|
| **Restaurar** | Traz o recurso de volta exatamente como estava. Recusa-se a sobrescrever se já existir um novo recurso com o mesmo nome — restaurar também não é destrutivo. |
| **Eliminar Permanentemente** | Remove uma única entrada do lixo para sempre |
| **Esvaziar o Lixo** | Remove tudo o que está atualmente no Lixo |

As referências cruzadas que foram limpas na eliminação **não** são
automaticamente restabelecidas ao restaurar — verá o que mudou, para
poder decidir se quer reconectar em vez de deixar o PyGameMaker adivinhar.

Os ficheiros no lixo são excluídos das exportações do projeto (zip/HTML5/
etc.) — um recurso eliminado nunca reaparece silenciosamente num jogo
publicado.

---

## Encontrar Recursos Não Utilizados

**Ferramentas > Encontrar Recursos Não Utilizados...**

Analisa todo o projeto através da mesma análise de utilização acima e
lista cada recurso sem qualquer referência, agrupado por categoria, cada
um com uma caixa de verificação. Selecione os que realmente quer
eliminar (ou **Selecionar Tudo**) e **Mover Selecionados para o Lixo** —
a mesma rede de segurança de qualquer outra eliminação.

**As salas são tratadas com cuidado.** Uma sala para a qual ninguém
navega explicitamente pelo nome — um jogo de sala única, ou a
primeiríssima sala de um jogo — aparece legitimamente como "não
utilizada" sob uma simples contagem de referências, mas eliminá-la
quebraria o jogo. As salas são etiquetadas *"Salas — não navegadas
explicitamente"* em vez de simplesmente "não utilizadas", e
**Selecionar Tudo ignora as salas** propositadamente; pode sempre
marcar uma individualmente se tiver a certeza.

---

## Encontrar Ficheiros Órfãos

**Ferramentas > Encontrar Ficheiros Órfãos...**

O problema inverso: ficheiros presentes na pasta do projeto (`sprites/`,
`sounds/`, `backgrounds/`, `fonts/`, `thumbnails/`) que não têm
**nenhuma** entrada correspondente no projeto — deixados por uma
operação interrompida, ou colocados à mão fora do IDE. Lista-os por
categoria com o mesmo padrão de caixa de verificação / Selecionar Tudo /
**Mover Selecionados para o Lixo** dos recursos não utilizados, e inclui
o seu próprio mini-painel de Lixo (Restaurar / Eliminar Permanentemente
/ Esvaziar) na mesma caixa de diálogo — os ficheiros órfãos usam um
armazenamento de lixo separado das eliminações normais de recursos, já
que nunca foram uma entrada real de project.json à partida.

---

## Limpar Projeto

**Ferramentas > Limpar Projeto**

Uma limpeza num clique dos ficheiros `.tmp` residuais — os ficheiros
temporários que o processo de gravação atómica do PyGameMaker cria e
normalmente remove sozinho. Só são tocados ficheiros com mais de cerca
de um minuto, para que uma gravação em curso nunca fique em risco.
Reporta quantos ficheiros foram removidos, ou que não havia nada a
limpar. Ao contrário das caixas de diálogo acima, estes ficheiros nunca
passam pelo sistema de recursos nem pelo Lixo — um ficheiro `.tmp` nunca
é a cópia autorizada de nada, por isso é eliminado diretamente.

---

## Próximos Passos

- [[Editor_Salas_pt|Editor de Salas]] / [[Editor_Objetos_pt|Editor de Objetos]] - De onde vem a maioria das referências a recursos
- [[FAQ_pt|FAQ]] - Perguntas comuns, incluindo sobre segurança de dados
