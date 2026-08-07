# Editor de Salas

> [English](Room-Editor) | [Français](Editeur_Salles_fr) | [Deutsch](Raum_Editor_de) | [Italiano](Editor_Stanze_it) | [Español](Editor_Salas_es) | [Português](Editor_Salas_pt) | [Slovenščina](Urejevalnik_Sob_sl) | [Українська](Redaktor_Kimnat_uk) | [Русский](Redaktor_Komnat_ru)

---

[Volver al Inicio](Home_es)

Las salas son los niveles, pantallas o escenas de tu juego. El Editor
de Salas te permite diseñar estos espacios colocando objetos y
configurando fondos.

---

## Abrir el Editor de Salas

1. Haz doble clic en una sala existente en el árbol de recursos, o
2. Clic derecho en **Rooms** > **Create Room**

---

## Propiedades de la Sala

| Propiedad | Descripción |
|-----------|-------------|
| **Name** | Identificador único (ej. `room_nivel1`) |
| **Width** | Ancho de la sala en píxeles |
| **Height** | Alto de la sala en píxeles |
| **Speed** | Velocidad del juego en fotogramas por segundo (predeterminado: 60) |
| **Persistent** | Mantiene el estado de la sala al salir/volver a entrar |

### Convención de Nombres

Usa el prefijo `room_` para las salas:
- `room_menu`
- `room_nivel1`
- `room_game_over`

---

## Colocar Objetos

### Agregar Instancias

1. Selecciona un objeto en el panel **Objects**
2. Haz clic en la vista de la sala para colocar una instancia
3. Haz clic y arrastra para colocar varias instancias

### Seleccionar Instancias

- Haz clic en una instancia para seleccionarla
- Mantén presionado **Ctrl** y haz clic para seleccionar varias
- Dibuja un rectángulo para seleccionar todas las instancias dentro

### Mover Instancias

- Arrastra las instancias seleccionadas con el ratón
- Usa las teclas de flecha para un movimiento preciso

### Eliminar Instancias

- Selecciona las instancias y presiona **Supr**, o
- Clic derecho y elige "Eliminar"

---

## Configuración de Cuadrícula

Activa la cuadrícula para una colocación precisa:

1. Ve a **View > Show Grid**
2. Establece el tamaño de la cuadrícula (ej. 32x32)
3. Activa "Snap to Grid"

Tamaños de cuadrícula comunes:
- **16x16** - Baldosas pequeñas
- **32x32** - Baldosas estándar
- **64x64** - Baldosas grandes

---

## Fondos

### Establecer un Fondo

1. Haz clic en la pestaña **Backgrounds**
2. Selecciona un recurso de fondo
3. Configura las opciones de visualización

### Opciones de Fondo

| Opción | Descripción |
|--------|-------------|
| **Visible** | Muestra/oculta el fondo |
| **Foreground** | Dibuja delante de los objetos |
| **Tile Horizontal** | Repite horizontalmente |
| **Tile Vertical** | Repite verticalmente |
| **Stretch** | Estira para llenar la sala |
| **Horizontal Speed** | Velocidad de desplazamiento (parallax) |
| **Vertical Speed** | Velocidad de desplazamiento (parallax) |

### Capas de Fondo

Una sala admite hasta **8 capas de fondo**, cada una con su propia
velocidad de desplazamiento para efectos parallax. Ejemplo de
distribución:
- Capa 0: Cielo (más al fondo)
- Capa 1: Montañas (desplazamiento más lento)
- Capa 2: Árboles (desplazamiento medio)
- Capa 3: Suelo (sin desplazamiento)

---

## Views (Cámara)

Las views controlan qué parte de la sala es visible en pantalla. Se
pueden configurar hasta **8 views** (View 0 a View 7) por sala — View 0
es visible por defecto; activa views adicionales para pantalla dividida
o imagen en imagen.

### Activar las Views

1. Selecciona "Enable Views" en las propiedades de la sala
2. Configura View 0 (la view principal)

### Propiedades de las Views

| Propiedad | Descripción |
|-----------|-------------|
| **View X/Y** | Esquina superior izquierda de la view en la sala |
| **View Width/Height** | Tamaño del área visible |
| **Port X/Y** | Posición en pantalla |
| **Port Width/Height** | Tamaño en pantalla (se puede estirar) |
| **Object Following** | Objeto que sigue la view |
| **Border H/V** | Zona muerta antes de que la cámara se mueva |

### Seguir a un Objeto

Para que la cámara siga al jugador:
1. Establece "Object Following" en `obj_player`
2. Ajusta "Border H" y "Border V" para un desplazamiento suave

---

## Orden de las Salas

El orden de las salas en el árbol de recursos determina:
1. Qué sala carga primero (sala superior = sala inicial)
2. El orden para las acciones "Next Room" y "Previous Room"

### Cambiar el Orden de las Salas

- Arrastra las salas en el árbol de recursos para reordenarlas
- O clic derecho y usa "Subir" / "Bajar"

---

## Consejos y Buenas Prácticas

### Organización
- Nombra las salas claramente según su propósito
- Mantén el menú principal como primera sala
- Usa tamaños de sala coherentes dentro de un juego

### Rendimiento
- No coloques demasiadas instancias en una sala
- Usa baldosas para la geometría estática de los niveles
- Destruye las instancias fuera de pantalla cuando sea posible

---

## Próximos Pasos

- [[Editor_Objetos_es]] - Crea objetos para colocar en las salas
- [[Eventos_y_Acciones_es]] - Añade interactividad a tus niveles
- [[Exportar_Juegos_es]] - Comparte tu juego terminado
