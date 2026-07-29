# Editor de Objetos

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Voltar ao Inicio](Home_pt)

O Editor de Objetos e a ferramenta central para definir o comportamento dos elementos do jogo.

## Visão geral

Os objetos são os blocos de construção do seu jogo. Eles definem:
- Aparencia (Sprite)
- Comportamento (Eventos e Ações)
- Propriedades físicas
- Interações

## Interface do Editor

### Areas principais
1. **Lista de objetos**: Todos os objetos no projeto
2. **Painel de propriedades**: Configurações básicas
3. **Lista de eventos**: Eventos definidos
4. **Editor de ações**: Ações para eventos

## Propriedades do objeto

### Gerais
- **Nome**: Identificador único (ex. obj_jogador)
- **Sprite**: Grafico atribuido
- **Visivel**: Se o objeto é renderizado
- **Persistente**: Sobrevive a mudancas de sala

### Física
- **Sólido**: Colide com outros objetos
- **Profundidade**: Ordem de desenho
- **Objeto pai**: Heranca de propriedades

## Trabalhar com eventos

### Adicionar um evento
1. Clique em "Adicionar Evento"
2. Selecione o tipo de evento
3. Adicione ações

### Tipos de eventos
- **Create**: Ao criar a instância
- **Step**: Cada frame
- **Draw**: Para desenhar
- **Teclado**: Entrada de teclado
- **Rato**: Interações com o rato
- **Colisão**: Ao tocar outros objetos

## Usar ações

### Adicionar ações
1. Selecione um evento
2. Arraste ações da biblioteca
3. Configure os parametros

### Ações comuns
- Mover numa direção
- Definir variável
- Criar/destruir instância
- Reproduzir som
- Mudar de sala

## Melhores práticas

1. **Nomes claros**: Use prefixos como "obj_"
2. **Modularidade**: Objetos pequenos e reutilizaveis
3. **Use a herança**: Objetos pai para comportamento comum
4. **Documentação**: Comentarios em eventos complexos

## Ver também

- [Eventos e Ações](Eventos_e_Acoes_pt)
- [Programação Visual](Programacao_Visual_pt)
- [Editor de Salas](Editor_Salas_pt)
