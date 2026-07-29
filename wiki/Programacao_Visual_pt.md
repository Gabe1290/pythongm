# Programação Visual

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Voltar ao Inicio](Home_pt)

O pyGM oferece um sistema de programação visual para o desenvolvimento de jogos fácil sem código.

## Visão geral

Com a programação visual pode:
- Criar lógica de jogo com arrastar e largar
- Conectar blocos para comportamentos complexos
- Desenvolver sem conhecimentos de programação

## O Editor Blockly

### Interface
1. **Paleta de blocos**: Blocos disponíveis por categoria
2. **Área de trabalho**: Aqui conecta os blocos
3. **Barra de ferramentas**: Guardar, Carregar, Eliminar

### Categorias de blocos
- **Lógica**: Se/Então, comparações, valores booleanos
- **Ciclos**: Repetições
- **Matematica**: Calculos
- **Texto**: Operações de texto
- **Variaveis**: Armazenar valores
- **Funções**: Blocos reutilizaveis
- **Jogo**: Ações específicas do pyGM

## Usar blocos

### Adicionar um bloco
1. Clique numa categoria
2. Arraste um bloco para a área de trabalho
3. Conecte-o a outros blocos

### Conectar blocos
- Os blocos encaixam automaticamente
- Preste atenção as formas correspondentes
- E possível aninhar blocos

### Configurar um bloco
- Preencha os campos de entrada
- Escolha opções do menu suspenso
- Insira subblocos

## Exemplos

### Movimento simples
```
Quando [seta direita] pressionada
  Definir x para (x + 5)
```

### Lógica condicional
```
Se <Vidas <= 0> então
  Mostrar mensagem "Game Over"
  Ir para sala [rm_gameover]
```

### Ciclo
```
Repetir [10] vezes
  Criar instância [obj_moeda] na posição (Aleatorio 0-800, Aleatorio 0-600)
```

## Blocos de jogo

### Movimento
- **Mover para**: Mover para posição
- **Definir velocidade**: Velocidade de movimento
- **Definir direção**: Direção de movimento

### Instancias
- **Criar instância**: Gerar novo objeto
- **Destruir**: Eliminar objeto
- **Para todos**: Todas as instâncias de um tipo

### Variaveis
- **Definir variável**: Armazenar valor
- **Modificar variável**: Alterar valor
- **Obter variável**: Recuperar valor

### Eventos
- **Quando tecla**: Entrada de teclado
- **Quando colisão**: Contacto de objetos
- **Quando temporizador**: Baseado no tempo

## Dicas

1. **Comece pequeno**: Primeiro projetos simples
2. **Teste**: Execute regularmente
3. **Organize**: Agrupe os blocos logicamente
4. **Comentarios**: Adicione notas

## Dos blocos ao código

O editor Blockly também pode gerar código:
1. Aprenda conceitos de programação visualmente
2. Veja o código gerado
3. Mude para Python depois

## Ver também

- [Criar o seu primeiro jogo](Primeiro_Jogo_pt)
- [Eventos e Ações](Eventos_e_Acoes_pt)
- [FAQ](FAQ_pt)
