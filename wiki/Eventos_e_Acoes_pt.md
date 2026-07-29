# Eventos e Ações

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Voltar ao Inicio](Home_pt)

Os Eventos e Ações formam o coração da lógica do jogo no pyGM.

## Conceito

### Eventos
Os eventos são gatilhos que reagem a situações específicas:
- Inicio do jogo
- Pressão de teclas
- Colisão
- Temporizador

### Ações
As ações são as respostas aos eventos:
- Mover
- Criar/Destruir
- Alterar valores
- Reproduzir sons

## Categorias de eventos

### Eventos de criação
- **Create**: Uma vez ao criar a instância
- **Destroy**: Ao eliminar a instância
- **Room Start**: Ao entrar numa sala

### Eventos Step
- **Step**: Cada frame
- **Begin Step**: Antes da verificação de colisões
- **End Step**: Apos a verificação de colisões

### Eventos de entrada
- **Teclado**: Pressão/libertação de teclas
- **Rato**: Cliques e movimento

### Eventos de colisão
- Contacto com outros objetos
- Contacto com paredes
- Verificações de área

### Eventos de desenho
- **Draw**: Desenho normal
- **Draw GUI**: Elementos de interface

### Outros eventos
- **Alarm**: Eventos baseados em temporizador
- **Animation End**: Animação de sprite terminada

## Biblioteca de ações

### Movimento
- `move_towards_point`: Mover para um ponto
- `set_speed`: Definir velocidade
- `set_direction`: Definir direção
- `bounce`: Ressaltar

### Instancias
- `create_instance`: Criar nova instância
- `destroy_instance`: Eliminar instância
- `set_sprite`: Mudar sprite

### Variáveis
- `set_variable`: Definir valor
- `test_variable`: Verificação condicional

### Audio
- `play_sound`: Reproduzir som
- `stop_sound`: Parar som
- `set_volume`: Alterar volume

### Sala
- `goto_room`: Mudar de sala
- `restart_room`: Reiniciar sala
- `next_room`: Próxima sala

### Desenho
- `draw_sprite`: Desenhar sprite
- `draw_text`: Mostrar texto
- `draw_rectangle`: Desenhar retangulo

## Condições e controlo de fluxo

### Ações condicionais
```
Se Variavel == Valor
  Executar acao
Senao
  Ação alternativa
```

### Ciclos
- Repetir ações
- Para todas as instâncias

## Melhores práticas

1. **Use Step com moderação**: So quando necessario
2. **Otimize as colisões**: Considere a propriedade Solid
3. **Agrupe os eventos**: Lógica relacionada junta
4. **Use alarmes**: Para ações temporizadas

## Ver também

- [Editor de Objetos](Editor_Objetos_pt)
- [Programação Visual](Programacao_Visual_pt)
- [FAQ](FAQ_pt)
