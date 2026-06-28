# Eventos e Acoes

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Voltar ao Inicio](Home_pt)

Os Eventos e Acoes formam o coracao da logica do jogo no pyGM.

## Conceito

### Eventos
Os eventos sao gatilhos que reagem a situacoes especificas:
- Inicio do jogo
- Pressao de teclas
- Colisao
- Temporizador

### Acoes
As acoes sao as respostas aos eventos:
- Mover
- Criar/Destruir
- Alterar valores
- Reproduzir sons

## Categorias de eventos

### Eventos de criacao
- **Create**: Uma vez ao criar a instancia
- **Destroy**: Ao eliminar a instancia
- **Room Start**: Ao entrar numa sala

### Eventos Step
- **Step**: Cada frame
- **Begin Step**: Antes da verificacao de colisoes
- **End Step**: Apos a verificacao de colisoes

### Eventos de entrada
- **Teclado**: Pressao/libertacao de teclas
- **Rato**: Cliques e movimento
- **Gamepad**: Entrada do controlador

### Eventos de colisao
- Contacto com outros objetos
- Contacto com paredes
- Verificacoes de area

### Eventos de desenho
- **Draw**: Desenho normal
- **Draw GUI**: Elementos de interface
- **Draw Begin/End**: Antes/Apos o desenho

### Outros eventos
- **Alarm**: Eventos baseados em temporizador
- **Animation End**: Animacao de sprite terminada
- **User Events**: Eventos personalizados

## Biblioteca de acoes

### Movimento
- `move_towards`: Mover para um ponto
- `set_speed`: Definir velocidade
- `set_direction`: Definir direcao
- `bounce`: Ressaltar

### Instancias
- `instance_create`: Criar nova instancia
- `instance_destroy`: Eliminar instancia
- `change_sprite`: Mudar sprite

### Variaveis
- `set_variable`: Definir valor
- `add_to_variable`: Adicionar valor
- `if_variable`: Verificacao condicional

### Audio
- `play_sound`: Reproduzir som
- `stop_sound`: Parar som
- `set_volume`: Alterar volume

### Sala
- `goto_room`: Mudar de sala
- `restart_room`: Reiniciar sala
- `goto_next_room`: Proxima sala

### Desenho
- `draw_sprite`: Desenhar sprite
- `draw_text`: Mostrar texto
- `draw_rectangle`: Desenhar retangulo

## Condicoes e controlo de fluxo

### Acoes condicionais
```
Se Variavel == Valor
  Executar acao
Senao
  Acao alternativa
```

### Ciclos
- Repetir acoes
- Para todas as instancias

## Melhores praticas

1. **Use Step com moderacao**: So quando necessario
2. **Otimize as colisoes**: Considere a propriedade Solid
3. **Agrupe os eventos**: Logica relacionada junta
4. **Use alarmes**: Para acoes temporizadas

## Ver tambem

- [Editor de Objetos](Editor_Objetos_pt)
- [Programacao Visual](Programacao_Visual_pt)
- [FAQ](FAQ_pt)
