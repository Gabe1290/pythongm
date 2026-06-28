# Programacao Visual

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Voltar ao Inicio](Home_pt)

O pyGM oferece um sistema de programacao visual para o desenvolvimento de jogos facil sem codigo.

## Visao geral

Com a programacao visual pode:
- Criar logica de jogo com arrastar e largar
- Conectar blocos para comportamentos complexos
- Desenvolver sem conhecimentos de programacao

## O Editor Blockly

### Interface
1. **Paleta de blocos**: Blocos disponiveis por categoria
2. **Area de trabalho**: Aqui conecta os blocos
3. **Barra de ferramentas**: Guardar, Carregar, Eliminar

### Categorias de blocos
- **Logica**: Se/Entao, comparacoes, valores booleanos
- **Ciclos**: Repeticoes
- **Matematica**: Calculos
- **Texto**: Operacoes de texto
- **Variaveis**: Armazenar valores
- **Funcoes**: Blocos reutilizaveis
- **Jogo**: Acoes especificas do pyGM

## Usar blocos

### Adicionar um bloco
1. Clique numa categoria
2. Arraste um bloco para a area de trabalho
3. Conecte-o a outros blocos

### Conectar blocos
- Os blocos encaixam automaticamente
- Preste atencao as formas correspondentes
- E possivel aninhar blocos

### Configurar um bloco
- Preencha os campos de entrada
- Escolha opcoes do menu suspenso
- Insira subblocos

## Exemplos

### Movimento simples
```
Quando [seta direita] pressionada
  Definir x para (x + 5)
```

### Logica condicional
```
Se <Vidas <= 0> entao
  Mostrar mensagem "Game Over"
  Ir para sala [rm_gameover]
```

### Ciclo
```
Repetir [10] vezes
  Criar instancia [obj_moeda] na posicao (Aleatorio 0-800, Aleatorio 0-600)
```

## Blocos de jogo

### Movimento
- **Mover para**: Mover para posicao
- **Definir velocidade**: Velocidade de movimento
- **Definir direcao**: Direcao de movimento

### Instancias
- **Criar instancia**: Gerar novo objeto
- **Destruir**: Eliminar objeto
- **Para todos**: Todas as instancias de um tipo

### Variaveis
- **Definir variavel**: Armazenar valor
- **Modificar variavel**: Alterar valor
- **Obter variavel**: Recuperar valor

### Eventos
- **Quando tecla**: Entrada de teclado
- **Quando colisao**: Contacto de objetos
- **Quando temporizador**: Baseado no tempo

## Dicas

1. **Comece pequeno**: Primeiro projetos simples
2. **Teste**: Execute regularmente
3. **Organize**: Agrupe os blocos logicamente
4. **Comentarios**: Adicione notas

## Dos blocos ao codigo

O editor Blockly tambem pode gerar codigo:
1. Aprenda conceitos de programacao visualmente
2. Veja o codigo gerado
3. Mude para Python depois

## Ver tambem

- [Criar o seu primeiro jogo](Primeiro_Jogo_pt)
- [Eventos e Acoes](Eventos_e_Acoes_pt)
- [FAQ](FAQ_pt)
