# Editor de Objetos

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Voltar ao Inicio](Home_pt)

O Editor de Objetos e a ferramenta central para definir o comportamento dos elementos do jogo.

## Visao geral

Os objetos sao os blocos de construcao do seu jogo. Eles definem:
- Aparencia (Sprite)
- Comportamento (Eventos e Acoes)
- Propriedades fisicas
- Interacoes

## Interface do Editor

### Areas principais
1. **Lista de objetos**: Todos os objetos no projeto
2. **Painel de propriedades**: Configuracoes basicas
3. **Lista de eventos**: Eventos definidos
4. **Editor de acoes**: Acoes para eventos

## Propriedades do objeto

### Gerais
- **Nome**: Identificador unico (ex. obj_jogador)
- **Sprite**: Grafico atribuido
- **Visivel**: Se o objeto e renderizado
- **Persistente**: Sobrevive a mudancas de sala

### Fisica
- **Solido**: Colide com outros objetos
- **Profundidade**: Ordem de desenho
- **Objeto pai**: Heranca de propriedades

## Trabalhar com eventos

### Adicionar um evento
1. Clique em "Adicionar Evento"
2. Selecione o tipo de evento
3. Adicione acoes

### Tipos de eventos
- **Create**: Ao criar a instancia
- **Step**: Cada frame
- **Draw**: Para desenhar
- **Teclado**: Entrada de teclado
- **Rato**: Interacoes com o rato
- **Colisao**: Ao tocar outros objetos

## Usar acoes

### Adicionar acoes
1. Selecione um evento
2. Arraste acoes da biblioteca
3. Configure os parametros

### Acoes comuns
- Mover numa direcao
- Definir variavel
- Criar/destruir instancia
- Reproduzir som
- Mudar de sala

## Melhores praticas

1. **Nomes claros**: Use prefixos como "obj_"
2. **Modularidade**: Objetos pequenos e reutilizaveis
3. **Use a heranca**: Objetos pai para comportamento comum
4. **Documentacao**: Comentarios em eventos complexos

## Ver tambem

- [Eventos e Acoes](Eventos_e_Acoes_pt)
- [Programacao Visual](Programacao_Visual_pt)
- [Editor de Salas](Editor_Salas_pt)
