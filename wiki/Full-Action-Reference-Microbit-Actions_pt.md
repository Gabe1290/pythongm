# micro:bit

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Limpar a tela

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_clear_display` |
| **Ícone** | ⬛ |
| **Categoria** | micro:bit |

Apagar todos os LED e descartar o que estava em espera

*Parâmetros:* nenhum

### Se o botão estiver pressionado

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_button` |
| **Ícone** | 🔘 |
| **Categoria** | micro:bit |

Verdadeiro enquanto o botão se mantiver pressionado (A+B = os dois)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `button` | Escolha | `a` | Opções: `a`, `b`, `ab`, `logo` |

### Se houver um gesto

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_gesture` |
| **Ícone** | 🤝 |
| **Categoria** | micro:bit |

Verdadeiro enquanto a placa estiver neste gesto ou posição

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `gesture` | Escolha | `shake` | Opções: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### Se o brilho do LED

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_pixel` |
| **Ícone** | 🔍 |
| **Categoria** | micro:bit |

Comparar o brilho de um LED (0 a 9) com um valor; por padrão, a pergunta é «está aceso?»

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `comparison` | Escolha | `>` | Opções: `<`, `<=`, `==`, `>=`, `>`, `!=`; opcional |
| `value` | Texto | `0` | opcional |

### Se houver inclinação

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_if_tilt` |
| **Ícone** | 📐 |
| **Categoria** | micro:bit |

Comparar um eixo do acelerômetro (mili-g, de -2048 a 2048) com um valor

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `axis` | Escolha | `x` | Opções: `x`, `y`, `z` |
| `comparison` | Escolha | `>` | Opções: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Texto | `300` |  |

### Tocar uma melodia

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_play_melody` |
| **Ícone** | 🎵 |
| **Categoria** | micro:bit |

Tocar uma melodia incorporada (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…) ou suas próprias notas como «C4:4 E G C5:8 R:4» (nota, oitava, :duração; R é uma pausa)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `melody` | Texto | `DADADADUM` | Built-in name, or notes separated by spaces |
| `tempo` | Texto | `120` | opcional |

### Tocar uma nota

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_play_tone` |
| **Ícone** | 🔔 |
| **Categoria** | micro:bit |

Emitir um bipe a uma frequência durante um número de milissegundos. Os sons ficam em fila

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `frequency` | Texto | `440` | Pitch in hertz (440 = the note A) |
| `duration` | Texto | `500` | opcional |

### Ler um sensor

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_read_sensor` |
| **Ícone** | 📡 |
| **Categoria** | micro:bit |

Ler um sensor da micro:bit para uma variável deste objeto (ou para uma variável global se o nome começar por «global.»)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `sensor` | Escolha | `accelerometer x` | Opções: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Texto | `sensor_value` | Variable that receives the reading |

### Rolar um texto

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_scroll_text` |
| **Ícone** | 🔤 |
| **Categoria** | micro:bit |

Rolar um texto na tela de LEDs. Coloque o texto entre aspas ("Olá"); caso contrário, um hífen ou um sinal de mais é lido como um cálculo. As letras acentuadas aparecem como ? tal como na placa verdadeira

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `text` | Texto | `"Hello"` | Text or expression to scroll |
| `delay` | Número | `150` | Scroll speed (MicroPython default 150); opcional |

### Enviar uma mensagem por rádio

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_radio_send` |
| **Ícone** | 📻 |
| **Categoria** | micro:bit |

Enviar um número ou um texto para as outras micro:bit do mesmo grupo (não a esta). Recebem o evento «Mensagem de rádio recebida», com o valor em radio_number e radio_string. Coloque o texto entre aspas; é cortado em 32 caracteres

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `1` | A number, an expression or quoted text |

### Brilho da tela

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_set_brightness` |
| **Ícone** | 🔆 |
| **Categoria** | micro:bit |

Brilho geral dos LED, de 0 (apagado) a 255 (máximo)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `brightness` | Texto | `255` |  |

### Acender um LED

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_set_pixel` |
| **Ícone** | 💡 |
| **Categoria** | micro:bit |

Acender um LED de imediato (x e y de 0 a 4, brilho de 0 a 9)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `brightness` | Texto | `9` | opcional |

### Definir o grupo de rádio

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_radio_set_group` |
| **Ícone** | 📡 |
| **Categoria** | micro:bit |

Escolher o grupo de rádio (0 a 255). Só as micro:bit do mesmo grupo se escutam; cada placa começa no grupo 0

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `group` | Texto | `0` |  |

### Mostrar uma imagem

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_show_image` |
| **Ícone** | ❤️ |
| **Categoria** | micro:bit |

Mostrar uma imagem nos LEDs: um nome (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL…) ou cinco linhas de dígitos de brilho como «09090:99999:99999:09990:00900». As imagens ficam em fila

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `image` | Texto | `HEART` | Built-in image name, or 5 rows of 5 digits (0-9) separated by colons |
| `hold` | Número | `0` | How long it stays before the next queued item (0 = until something else is shown); opcional |

### Mostrar um número

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_show_number` |
| **Ícone** | 🔢 |
| **Categoria** | micro:bit |

Mostrar um número: um dígito fica fixo, um número mais longo rola

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `value` | Texto | `0` | Number or expression |

### Parar o som

| Propriedade | Valor |
|----------|-------|
| **Nome** | `microbit_stop_sound` |
| **Ícone** | 🔇 |
| **Categoria** | micro:bit |

Desligar o alto-falante e descartar os sons em espera

*Parâmetros:* nenhum

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (21)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (6)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (14)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (3)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (23)
- [Desenho](Full-Action-Reference-Drawing_pt) (11)
- [Rede](Full-Action-Reference-Network-Actions_pt) (22)
- [Partículas](Full-Action-Reference-Particles_pt) (8)
- [Pontuação/Vidas/Saúde](Full-Action-Reference-Score-Lives-Health_pt) (5)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
