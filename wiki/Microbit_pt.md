# micro:bit (simulador de BBC micro:bit)

*[Início](Home_pt) | [Referência completa de ações](Full-Action-Reference-Microbit-Actions_pt) | [Extensões](Extensions_pt)*

---

O PyGameMaker pode colocar uma **BBC micro:bit simulada** na janela do seu jogo:
um tela de 5×5 LEDs, os botões **A** e **B**, um logotipo tátil, os pinos 0/1/2,
um acelerômetro, sensores de luz, temperatura, bússola e som, um alto-falante e
um rádio — tudo desenhado no tela e programado com os mesmos eventos e ações do
resto do IDE. Não é preciso nenhum hardware. É fornecida pela
[extensão](Extensions_pt) **micro:bit** integrada, que vem ativada.

O exemplo incluído **`microbit_1`** («Dado e humores») é um jogo completo: A e B
mostram uma cara feliz e uma triste, sacudir lança um dado, e tocar no logotipo
faz rolar quantos lançamentos você fez.

---

## Primeiros passos

1. Crie um objeto cujo **nome comece com `microbit`** (por exemplo
   `microbit_1`) e coloque uma instância dele em uma sala. Esse objeto *é* a
   micro:bit: o motor desenha a placa por cima e executa o seu simulador.
2. Em **Configurações do Projeto → Extensões**, marque **micro:bit**. (Um
   projeto que já usa uma ação de micro:bit tem-na ativada automaticamente; um
   que não usa nunca vê os blocos nem as ações de micro:bit.)
3. Coloque os eventos **nesse mesmo objeto**: cada ação de micro:bit atua sobre a
   micro:bit que a executa. Por exemplo *Button A Pressed* → *Show Image*
   `HAPPY`.
4. **Testar Jogo.** Clique nos botões da placa.

Também é possível transformar um objeto numa micro:bit marcando `is_microbit`
na sua instância da sala. Várias micro:bit em uma mesma sala não são problema —
é isso que torna o rádio útil.

---

## A placa e como a controlar

| Na tela | Mouse | Teclado (opcional) |
|---|---|---|
| Botão **A** / **B** | Clique (mantido enquanto o mouse estiver premido) | `A` / `B` |
| **A+B** em conjunto | Clique direito num dos botões | manter `A` e `B` |
| **Logotipo** tátil (dourado, acima do tela) | Clique | — |
| Pinos **0, 1, 2** (contactos na borda inferior) | Clique | — |
| **Painel de inclinação** | Arrastar; a borda vale um g e volta à horizontal ao soltar | teclas de seta |
| Botão **SHAKE** | Clique | `S` |
| Controles deslizantes **Light / Temp / Compass / Sound** | Arrastar; o valor mantém-se | — |

Os atalhos de teclado estão **desativados por padrão** para nunca roubarem
as teclas do seu próprio jogo. Ative-os em uma placa com a propriedade de objeto
`microbit_keyboard` (a variável de instância com o mesmo nome também funciona).

Outras propriedades de objeto: `microbit_scale` (multiplicador de tamanho, `1.0`
por padrão, cerca de 220 px de largura) e `microbit_show_sensors` (ponha
`false` para esconder a faixa de sensores). Se o objeto tiver um **sprite**, este
é usado como corpo da placa e só os LEDs e os controles são desenhados por cima.

Um clique na placa não aciona também os seus próprios eventos de mouse.

---

## As ações (categoria **micro:bit**)

| Ação | O que faz |
|------|-----------|
| **Show Image** (`microbit_show_image`) | O nome de uma imagem integrada (`HEART`, `HAPPY`, `SAD`, `YES`, `NO`, `ARROW_N`, `SKULL`… 64 ao todo) ou cinco linhas de cinco dígitos de brilho como `09090:99999:99999:09990:00900`. |
| **Scroll Text** (`microbit_scroll_text`) | Deslizar um texto pelo tela (150 ms por coluna por padrão). |
| **Show Number** (`microbit_show_number`) | Um dígito fica parado; números mais longos deslizam. |
| **Set LED** (`microbit_set_pixel`) | Acender um LED já: `x`, `y` de 0 a 4, brilho de 0 a 9. |
| **Clear Display** (`microbit_clear_display`) | Apagar todos os LEDs e descartar o que estava em fila. |
| **Set Display Brightness** (`microbit_set_brightness`) | Brilho geral, de 0 a 255. |
| **Play Tone** (`microbit_play_tone`) | Um bip a uma frequência durante um número de milissegundos. |
| **Play Melody** (`microbit_play_melody`) | Uma das 21 melodias integradas (`DADADADUM`, `ENTERTAINER`, `POWER_UP`…) ou as suas próprias notas: `"C4:4 E G C5:8 R:4"` (nota, oitava, `:duração`; `R` é uma pausa). |
| **Stop Sound** (`microbit_stop_sound`) | Silenciar o alto-falante e descartar os sons em fila. |
| **Set Radio Group** (`microbit_radio_set_group`) | Escolher o grupo de rádio, de 0 a 255. |
| **Send Radio Message** (`microbit_radio_send`) | Enviar um número ou um texto às outras micro:bit do grupo. |
| **Read Sensor** (`microbit_read_sensor`) | Colocar uma leitura (acelerômetro x/y/z, intensidade, bússola, luz, temperatura, nível de som, pino 0–2 analógico) em uma variável — ou em uma variável global se o nome começar com `global.`. |
| **If Button Pressed** (`microbit_if_button`) | Condição: A, B, A+B ou o logotipo estão premidos. |
| **If Gesture** (`microbit_if_gesture`) | Condição: a placa está em um gesto ou posição (`shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`…`8g`). |
| **If Tilt** (`microbit_if_tilt`) | Condição: comparar um eixo do acelerômetro (mili-g) com um valor. |
| **If LED Brightness** (`microbit_if_pixel`) | Condição: comparar o brilho de um LED com um valor. |

As condições protegem a ação ou o bloco que as segue, no estilo do GameMaker.
Veja a
[Referência completa de ações](Full-Action-Reference-Microbit-Actions_pt) para
todos os parâmetros.

> **O texto vai entre aspas duplas.** `Scroll Text` e `Send Radio Message` leem
> o seu valor como qualquer outra expressão, por isso `Score - 3` é aritmética.
> Escreva o texto literal como `"Olá"`. O tela só tem ASCII imprimível; as
> letras acentuadas aparecem como `?`, tal como na placa real.

---

## Os eventos

São disparados no próprio objeto da micro:bit:

| Evento | Dispara quando |
|--------|----------------|
| **Button A Pressed**, **Button B Pressed**, **Buttons A+B Pressed** | O(s) botão(ões) são premidos. |
| **Logo Touched** | O logotipo é tocado. |
| **Pin 0 / 1 / 2 Touched** | Esse pino é tocado. |
| **Shake**, **Logo Up**, **Logo Down**, **Tilt Left**, **Tilt Right**, **Screen Up**, **Screen Down**, **Free Fall**, **2g / 3g / 6g / 8g Impact** | A placa detecta esse gesto (o mesmo algoritmo da micro:bit real). |
| **Loud Sound** / **Quiet Sound** | O nível do microfone cruza o limiar de som forte / calmo. |
| **Display Finished** | A fila do tela reproduziu tudo. |
| **Sound Finished** | Todas as notas e melodias em fila foram reproduzidas. |
| **Radio Message Received** | Outra micro:bit do mesmo grupo enviou uma mensagem. |

«Forever» é o evento normal **Step**.

### Rádio

Todas as placas começam no grupo 0. **Send Radio Message** entrega a cada
*outra* micro:bit do mesmo grupo (uma placa nunca se ouve a si própria, e um
grupo diferente não ouve nada). O receptor recebe o evento e duas variáveis:
`radio_number` (0 se o texto não for um número) e `radio_string` (sempre o
texto). O texto é cortado aos 32 caracteres, como no rádio real.

---

## O tempo: a fila do tela e do som

Numa micro:bit real, deslizar texto *bloqueia* o programa. Um jogo não pode
bloquear, por isso as ações do tela são **postas em fila** e reproduzidas uma a
seguir à outra (16 no máximo; pedir o que já está a ser mostrado não faz nada).
**Clear Display** esvazia a fila e **Display Finished** diz-lhe quando acabou,
para encadear animações. Os sons entram em fila da mesma maneira, com **Stop
Sound** e **Sound Finished**.

O som é uma onda quadrada, como o buzzer da placa. Se o computador não tiver
dispositivo de áudio, é ignorado em silêncio (o simulador continua a registá-lo).

---

## Exportações

A exportação para **desktop** (Windows, Linux, macOS) empacota o motor real, por
isso a micro:bit funciona exatamente como em «Testar Jogo». A exportação
**HTML5** também tem o simulador: a placa e a faixa de sensores são desenhadas no
navegador, pode clicar ou tocar nos botões, no logotipo e nos pinos, arrastar o
painel de inclinação e os controles deslizantes, e o alto-falante emite bips (os
navegadores só permitem som depois do primeiro clique ou da primeira tecla). A
exportação **Android/Kivy** também o tem: a placa e a faixa de sensores são
desenhadas (com um aspecto simplificado, de cantos retos), pode tocar nos botões,
no logotipo, nos pinos, no painel de inclinação, no botão de sacudir e nos
controles deslizantes, os eventos disparam e o alto-falante reproduz as suas
notas. Os atalhos de teclado só funcionam em uma placa cuja variável
`microbit_keyboard` esteja ativada. Uma placa é reconhecida pelo nome do seu
objeto (tem de começar com `microbit`).

---

## E agora?

- Abra o exemplo **`microbit_1`** no aba de boas-vindas e leia o seu guia.
- Experimente duas placas em uma sala, cada uma com um *Set Radio Group*, e envie
  uma mensagem a partir de um botão.
- Previsto: uma conexão ao vivo com uma micro:bit real por USB. Ainda não está
  disponível.

Veja também: [Extensões](Extensions_pt), [Referência completa de ações](Full-Action-Reference-Microbit-Actions_pt), [Referência de eventos](Event-Reference_pt).
