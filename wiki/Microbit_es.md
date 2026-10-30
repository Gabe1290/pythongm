# micro:bit (simulador de BBC micro:bit)

*[Inicio](Home_es) | [Referencia completa de acciones](Full-Action-Reference-Microbit-Actions_es) | [Extensiones](Extensions_es)*

---

PyGameMaker puede poner una **BBC micro:bit simulada** en la ventana de tu
juego: una pantalla de 5×5 LED, los botones **A** y **B**, un logotipo táctil,
los pines 0/1/2, un acelerómetro, sensores de luz, temperatura, brújula y
sonido, un altavoz y una radio — todo dibujado en la pantalla y programado con
los mismos eventos y acciones que el resto del IDE. No se necesita ningún
hardware. La proporciona la **extensión** [micro:bit](Extensions_es) integrada,
que viene activada.

El ejemplo incluido **`microbit_1`** («Dado y estados de ánimo») es un juego
completo: A y B muestran una cara feliz y una triste, agitar lanza un dado, y
tocar el logotipo desplaza el número de lanzamientos que has hecho.

---

## Primeros pasos

1. Crea un objeto cuyo **nombre empiece por `microbit`** (por ejemplo
   `microbit_1`) y coloca una instancia suya en una sala. Ese objeto *es* la
   micro:bit: el motor dibuja la placa encima y ejecuta su simulador.
2. En **Configuración del proyecto → Extensiones**, marca **micro:bit**. (Un
   proyecto que ya usa una acción de micro:bit la tiene activada
   automáticamente; uno que no la usa nunca ve los bloques ni las acciones de
   micro:bit.)
3. Pon los eventos en **ese mismo objeto**: cada acción de micro:bit actúa sobre
   la micro:bit que la ejecuta. Por ejemplo *Button A Pressed* → *Show Image*
   `HAPPY`.
4. **Probar juego.** Haz clic en los botones de la placa.

También se puede convertir un objeto en micro:bit marcando `is_microbit` en su
instancia de la sala. Varias micro:bit en una misma sala están bien — eso es lo
que hace útil la radio.

---

## La placa y cómo manejarla

| En pantalla | Ratón | Teclado (opcional) |
|---|---|---|
| Botón **A** / **B** | Clic (se mantiene mientras el ratón está pulsado) | `A` / `B` |
| **A+B** a la vez | Clic derecho en cualquiera de los botones | mantener `A` y `B` |
| **Logotipo** táctil (dorado, sobre la pantalla) | Clic | — |
| Pines **0, 1, 2** (contactos en el borde inferior) | Clic | — |
| **Panel de inclinación** | Arrastrar; el borde equivale a un g y vuelve a nivel al soltar | teclas de flecha |
| Botón **SHAKE** | Clic | `S` |
| Deslizadores **Light / Temp / Compass / Sound** | Arrastrar; el valor se mantiene | — |

Los atajos de teclado están **desactivados por defecto** para que nunca te
quiten las teclas de tu propio juego. Actívalos para una placa con la propiedad
de objeto `microbit_keyboard` (la variable de instancia del mismo nombre también
funciona).

Otras propiedades de objeto: `microbit_scale` (multiplicador de tamaño, `1.0`
por defecto, unos 220 px de ancho) y `microbit_show_sensors` (ponla a `false`
para ocultar la franja de sensores). Si el objeto tiene un **sprite**, se usa
como cuerpo de la placa y solo se dibujan encima los LED y los controles.

Un clic en la placa no dispara además tus propios eventos de ratón.

---

## Las acciones (categoría **micro:bit**)

| Acción | Qué hace |
|--------|----------|
| **Show Image** (`microbit_show_image`) | Un nombre de imagen integrada (`HEART`, `HAPPY`, `SAD`, `YES`, `NO`, `ARROW_N`, `SKULL`… 64 en total) o cinco filas de cinco dígitos de brillo como `09090:99999:99999:09990:00900`. |
| **Scroll Text** (`microbit_scroll_text`) | Desplazar un texto por la pantalla (150 ms por columna por defecto). |
| **Show Number** (`microbit_show_number`) | Un dígito se queda fijo; los números más largos se desplazan. |
| **Set LED** (`microbit_set_pixel`) | Encender un LED ahora mismo: `x`, `y` de 0 a 4, brillo de 0 a 9. |
| **Clear Display** (`microbit_clear_display`) | Apagar todos los LED y descartar lo que estaba en cola. |
| **Set Display Brightness** (`microbit_set_brightness`) | Brillo general, de 0 a 255. |
| **Play Tone** (`microbit_play_tone`) | Un pitido a una frecuencia durante un número de milisegundos. |
| **Play Melody** (`microbit_play_melody`) | Una de las 21 melodías integradas (`DADADADUM`, `ENTERTAINER`, `POWER_UP`…) o tus propias notas: `"C4:4 E G C5:8 R:4"` (nota, octava, `:duración`; `R` es un silencio). |
| **Stop Sound** (`microbit_stop_sound`) | Silenciar el altavoz y descartar los sonidos en cola. |
| **Set Radio Group** (`microbit_radio_set_group`) | Elegir el grupo de radio, de 0 a 255. |
| **Send Radio Message** (`microbit_radio_send`) | Enviar un número o un texto a las demás micro:bit del grupo. |
| **Read Sensor** (`microbit_read_sensor`) | Guardar una lectura (acelerómetro x/y/z, intensidad, brújula, luz, temperatura, nivel de sonido, pin 0–2 analógico) en una variable — o en una variable global si el nombre empieza por `global.`. |
| **If Button Pressed** (`microbit_if_button`) | Condición: A, B, A+B o el logotipo se mantienen pulsados. |
| **If Gesture** (`microbit_if_gesture`) | Condición: la placa está en un gesto o postura (`shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`…`8g`). |
| **If Tilt** (`microbit_if_tilt`) | Condición: comparar un eje del acelerómetro (mili-g) con un valor. |
| **If LED Brightness** (`microbit_if_pixel`) | Condición: comparar el brillo de un LED con un valor. |

Las condiciones protegen la acción o el bloque que las sigue, al estilo de
GameMaker. Consulta la
[Referencia completa de acciones](Full-Action-Reference-Microbit-Actions_es)
para ver todos los parámetros.

> **El texto va entre comillas dobles.** `Scroll Text` y `Send Radio Message`
> leen su valor como cualquier otra expresión, así que `Score - 3` es una
> operación aritmética. Escribe el texto literal como `"Hola"`. La pantalla solo
> tiene ASCII imprimible; las letras con tilde aparecen como `?`, igual que en la
> placa real.

---

## Los eventos

Se disparan en el propio objeto de la micro:bit:

| Evento | Se dispara cuando |
|--------|-------------------|
| **Button A Pressed**, **Button B Pressed**, **Buttons A+B Pressed** | Se pulsan los botones. |
| **Logo Touched** | Se toca el logotipo. |
| **Pin 0 / 1 / 2 Touched** | Se toca ese pin. |
| **Shake**, **Logo Up**, **Logo Down**, **Tilt Left**, **Tilt Right**, **Screen Up**, **Screen Down**, **Free Fall**, **2g / 3g / 6g / 8g Impact** | La placa detecta ese gesto (el mismo algoritmo que la micro:bit real). |
| **Loud Sound** / **Quiet Sound** | El nivel del micrófono cruza el umbral de sonido fuerte / tranquilo. |
| **Display Finished** | La cola de la pantalla ha reproducido todo. |
| **Sound Finished** | Se han reproducido todas las notas y melodías en cola. |
| **Radio Message Received** | Otra micro:bit del mismo grupo envió un mensaje. |

«Forever» es el evento normal **Step**.

### Radio

Todas las placas empiezan en el grupo 0. **Send Radio Message** entrega a cada
*otra* micro:bit del mismo grupo (una placa nunca se oye a sí misma, y un grupo
distinto no oye nada). El receptor recibe el evento y dos variables:
`radio_number` (0 si el texto no es un número) y `radio_string` (siempre el
texto). El texto se recorta a 32 caracteres, como en la radio real.

---

## El tiempo: cola de pantalla y de sonido

En una micro:bit real, desplazar un texto *bloquea* el programa. Un juego no
puede bloquearse, así que las acciones de pantalla se **ponen en cola** y se
reproducen una tras otra (16 como máximo; pedir lo que ya se está mostrando no
hace nada). **Clear Display** vacía la cola y **Display Finished** te avisa de
cuándo se ha agotado, para que puedas encadenar animaciones. Los sonidos se
ponen en cola igual, con **Stop Sound** y **Sound Finished**.

El sonido es una onda cuadrada, como el zumbador de la placa. Si el ordenador no
tiene dispositivo de audio, se omite en silencio (el simulador lo sigue
registrando).

---

## Exportaciones

La exportación de **escritorio** (Windows, Linux, macOS) empaqueta el motor
real, así que la micro:bit funciona exactamente igual que en «Probar juego». La
exportación **HTML5** también tiene el simulador: la placa y la franja de
sensores se dibujan en el navegador, puedes hacer clic o tocar los botones, el
logotipo y los pines, arrastrar el panel de inclinación y los deslizadores, y el
altavoz pita (los navegadores solo permiten sonido tras el primer clic o la
primera pulsación de tecla). La exportación **Android/Kivy** también lo tiene:
la placa y la franja de sensores se dibujan (con un aspecto simplificado, de
esquinas rectas), puedes tocar los botones, el logotipo, los pines, el panel de
inclinación, el botón de agitar y los deslizadores, los eventos se disparan y el
altavoz reproduce sus notas. Los atajos de teclado solo funcionan para una placa
cuya variable `microbit_keyboard` esté activada. Una placa se reconoce por el
nombre de su objeto (debe empezar por `microbit`) o por `is_microbit` en su instancia de la sala.

---

## Exportación a MicroPython (hacia una micro:bit real)

Es una exportación de otro tipo. En lugar de un juego para otro ordenador,
convierte el programa de tus objetos micro:bit en código **MicroPython** real
que se ejecuta en una placa física.

1. Abre **Archivo → Exportar código de micro:bit (MicroPython)...** (debe haber
   un proyecto abierto).
2. Indica qué placa tienes: **V2 (2020 o posterior)**, **V1 (original,
   2016-2020)** o **Ambas (un solo archivo .hex para placas V1 y V2)**.
3. Elige una carpeta. Cada objeto micro:bit tiene su propio programa,
   `<carpeta>/<nombre del objeto>/main.py`.
4. Cuando se ha exportado exactamente un objeto, el IDE ofrece dos formas de
   ponerlo en la placa. **¿Copiar a la micro:bit?** copia `main.py` a una placa
   conectada por USB que ya ejecuta MicroPython (el programa arranca entonces
   solo). **¿Crear un archivo .hex listo para grabar?** genera un archivo `.hex`
   que arrastras a la unidad USB **MICROBIT** de la placa — también funciona en
   una placa nueva que nunca ha ejecutado MicroPython.

Se traducen todas las acciones y condiciones de micro:bit, y también *Set
Variable*, *Test Variable*, los bloques y los comentarios. Cada evento se
convierte en una comprobación dentro de un único bucle. Las acciones de juego
que no significan nada en una placa (salas, sprites, puntuaciones…) no se
exportan. En las expresiones funcionan `irandom`, `random` y `choose`; las
demás funciones de GameMaker no se traducen.

El cuadro de diálogo de exportación enumera lo que no se pudo exportar:

- **Display Finished** y **Sound Finished** (las llamadas de pantalla y de
  sonido de la placa ya esperan a terminar).
- En una placa V1, lo que necesita una V2: leer el nivel de sonido, el
  logotipo táctil (*If Button Pressed* con el logotipo, **Logo Touched**) y los
  eventos **Loud Sound** / **Quiet Sound**.
- Cualquier otra cosa que no tenga equivalente en MicroPython.

**Tamaño:** el programa debe caber en 8.187 bytes en una placa V1 y en 20.150
bytes en una V2. **Ambas** genera un único Universal Hex, así que está limitado
por el tamaño de la V1 y se exporta con las reglas de la V1.

> Los archivos `.hex` se han comprobado con el firmware real de la micro:bit,
> pero todavía no en una placa física.

---

## Y ahora, ¿qué?

- Abre el ejemplo **`microbit_1`** desde la pestaña de bienvenida y lee su guía.
- Prueba dos placas en una sala, cada una con un *Set Radio Group*, y envía un
  mensaje desde un botón.
- Previsto: una conexión en directo con una micro:bit real por USB. Todavía no
  está disponible.

Véase también: [Extensiones](Extensions_es), [Referencia completa de acciones](Full-Action-Reference-Microbit-Actions_es), [Referencia de eventos](Event-Reference_es).
