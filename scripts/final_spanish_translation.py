#!/usr/bin/env python3
"""
Final comprehensive Spanish translation for PyGameMaker IDE
"""

import re
import os

# Complete English to Spanish translations
EN_TO_ES = {
    # About
    "About PyGameMaker IDE": "Acerca de PyGameMaker IDE",
    "PyGameMaker IDE": "PyGameMaker IDE",
    "Version 0.9.0": "Versión 0.9.0",
    "Version 1.0.0": "Versión 1.0.0",
    "About": "Acerca de",
    "Credits": "Créditos",
    "Close": "Cerrar",

    # Common buttons and actions
    "OK": "Aceptar",
    "Cancel": "Cancelar",
    "Apply": "Aplicar",
    "Save": "Guardar",
    "Open": "Abrir",
    "New": "Nuevo",
    "Delete": "Eliminar",
    "Edit": "Editar",
    "Add": "Añadir",
    "Remove": "Quitar",
    "Clear": "Limpiar",
    "Reset": "Restablecer",
    "Yes": "Sí",
    "No": "No",
    "Error": "Error",
    "Warning": "Advertencia",
    "Information": "Información",
    "Confirm": "Confirmar",
    "Help": "Ayuda",
    "Settings": "Configuración",
    "Options": "Opciones",
    "Preferences": "Preferencias",
    "Properties": "Propiedades",
    "Browse...": "Examinar...",
    "Done": "Listo",
    "Finished": "Terminado",
    "Success": "Éxito",
    "Failed": "Falló",

    # Move actions
    "Move Up": "Mover arriba",
    "Move Down": "Mover abajo",
    "⬆️ Move Up": "⬆️ Mover arriba",
    "⬇️ Move Down": "⬇️ Mover abajo",
    "↑ Move Up": "↑ Mover arriba",
    "↓ Move Down": "↓ Mover abajo",
    "Remove Action": "Eliminar acción",
    "Add Action": "Añadir acción",
    "Edit Action": "Editar acción",

    # Object editor
    "Open Blockly editor in a separate window": "Abrir editor Blockly en ventana separada",
    "Instances:": "Instancias:",
    "📋 Configure...": "📋 Configurar...",
    "📋 Event List": "📋 Lista de eventos",
    "💻 Code Editor": "💻 Editor de código",
    "🎮 Test Object": "🎮 Probar objeto",
    "Object: Not loaded": "Objeto: No cargado",
    "Mode:": "Modo:",
    "Event for custom code:": "Evento para código personalizado:",
    "Validation Error": "Error de validación",
    "Persistent": "Persistente",
    "Event": "Evento",
    "Events": "Eventos",
    "Actions": "Acciones",
    "Objects": "Objetos",
    "Sprite:": "Sprite:",
    "Visible": "Visible",
    "Solid": "Sólido",
    "Object persists between rooms": "El objeto persiste entre salas",
    "Solid objects block movement": "Los objetos sólidos bloquean el movimiento",
    "View Code": "Ver código",

    # Event messages
    "Event: {0}": "Evento: {0}",
    "Editing event: {0}": "Editando evento: {0}",
    "Generated code view updated": "Vista de código generado actualizada",
    "Assets loaded: {0} sprites": "Recursos cargados: {0} sprites",
    "No event selected": "Ningún evento seleccionado",
    "Event Exists": "Evento existente",
    "The {0} event already exists.": "El evento {0} ya existe.",
    "Key Event Exists": "Evento de tecla existente",
    "The {0} arrow key event already exists.": "El evento de flecha {0} ya existe.",
    "The {0} key event already exists for {1}.": "El evento de tecla {0} ya existe para {1}.",
    "Mouse Event Exists": "Evento de ratón existente",
    "This mouse event already exists.": "Este evento de ratón ya existe.",
    "Remove Event": "Eliminar evento",
    "Are you sure you want to remove the {0} event and all its actions?": "¿Está seguro de eliminar el evento {0} y todas sus acciones?",
    "Remove Collision Event": "Eliminar evento de colisión",
    "Remove Mouse Event": "Eliminar evento de ratón",
    "Cannot Add Action": "No se puede añadir acción",
    "Remove Key Event": "Eliminar evento de tecla",
    "Are you sure you want to remove the {0} arrow key event and all its actions?": "¿Está seguro de eliminar el evento de flecha {0} y todas sus acciones?",
    "Are you sure you want to remove this action?": "¿Está seguro de eliminar esta acción?",
    "No objects available": "Sin objetos disponibles",

    # Collision events
    "Collision Event Options": "Opciones de evento de colisión",
    "Collision Event Exists": "Evento de colisión existente",
    "This collision event already exists.": "Este evento de colisión ya existe.",
    "Are you sure you want to remove the collision event with {0}?": "¿Está seguro de eliminar el evento de colisión con {0}?",
    "Are you sure you want to remove the {0} event?": "¿Está seguro de eliminar el evento {0}?",

    # Collision action display
    "❌ NOT Colliding with {target_object}": "❌ NO colisionando con {target_object}",
    "💥 Collision with {target_object}": "💥 Colisión con {target_object}",
    "❌ NOT colliding (trigger when NOT touching)": "❌ NO colisionando (activar cuando NO toque)",
    "Check this to trigger actions when the object is NOT colliding with the target": "Marque esto para activar acciones cuando el objeto NO esté colisionando",

    # Action counts
    "{0} actions": "{0} acciones",
    "{0} total actions": "{0} acciones totales",
    "actions": "acciones",
    "action": "acción",
    "parameters": "parámetros",

    # Shortcuts
    "Ctrl+Up": "Ctrl+Arriba",
    "Ctrl+Down": "Ctrl+Abajo",
    "Warning: Could not setup shortcuts: {e}": "Advertencia: No se pudieron configurar atajos: {e}",

    # Menu items
    "&File": "&Archivo",
    "&Edit": "&Editar",
    "&View": "&Ver",
    "&Tools": "&Herramientas",
    "&Run": "&Ejecutar",
    "&Help": "&Ayuda",
    "&Resources": "&Recursos",
    "File": "Archivo",
    "Edit": "Editar",
    "View": "Ver",
    "Run": "Ejecutar",
    "Tools": "Herramientas",
    "Resources": "Recursos",
    "Language": "Idioma",

    # Project
    "Open Project": "Abrir proyecto",
    "New Project": "Nuevo proyecto",
    "Save Project": "Guardar proyecto",
    "Close Project": "Cerrar proyecto",
    "Recent Projects": "Proyectos recientes",
    "Export Project": "Exportar proyecto",

    # Game settings
    "Starting Lives:": "Vidas iniciales:",
    "Show Lives in Caption:": "Mostrar vidas en título:",
    "Starting Score:": "Puntuación inicial:",
    "Show Score in Caption:": "Mostrar puntuación en título:",
    "Starting Health:": "Salud inicial:",
    "Show Health in Caption:": "Mostrar salud en título:",

    # Resources
    "Sprites": "Sprites",
    "Sounds": "Sonidos",
    "Backgrounds": "Fondos",
    "Rooms": "Salas",
    "Scripts": "Scripts",
    "Fonts": "Fuentes",
    "Timelines": "Líneas de tiempo",
    "Paths": "Rutas",
    "Data Files": "Archivos de datos",
    "Game Information": "Información del juego",
    "Global Game Settings": "Configuración global del juego",
    "Game Resources": "Recursos del juego",

    # Sprite
    "Sprite": "Sprite",
    "Sprite Editor": "Editor de sprites",
    "Edit Sprite": "Editar sprite",
    "Image": "Imagen",
    "Frame": "Fotograma",
    "Frames": "Fotogramas",
    "Animation": "Animación",
    "Animation Speed": "Velocidad de animación",
    "Origin": "Origen",
    "Origin X": "Origen X",
    "Origin Y": "Origen Y",
    "Center": "Centro",
    "Width": "Ancho",
    "Height": "Alto",
    "Transparent": "Transparente",
    "Collision Mask": "Máscara de colisión",
    "Bounding Box": "Cuadro delimitador",
    "Precise": "Preciso",
    "Rectangle": "Rectángulo",
    "Ellipse": "Elipse",
    "Diamond": "Rombo",

    # Sound
    "Sound": "Sonido",
    "Sound Editor": "Editor de sonidos",
    "Edit Sound": "Editar sonido",
    "Play": "Reproducir",
    "Stop": "Detener",
    "Pause": "Pausar",
    "Loop": "Bucle",
    "Volume": "Volumen",
    "Preload": "Precargar",
    "Audio": "Audio",
    "Music": "Música",

    # Background
    "Background": "Fondo",
    "Background Editor": "Editor de fondos",
    "Edit Background": "Editar fondo",
    "Tile": "Mosaico",
    "Tile Horizontally": "Mosaico horizontal",
    "Tile Vertically": "Mosaico vertical",
    "Stretch": "Estirar",

    # Object
    "Object": "Objeto",
    "Object Editor": "Editor de objetos",
    "Edit Object": "Editar objeto",
    "Parent": "Padre",
    "Parent Object": "Objeto padre",
    "No Parent": "Sin padre",
    "Mask": "Máscara",
    "Depth": "Profundidad",
    "Add Event": "Añadir evento",
    "Delete Event": "Eliminar evento",
    "Delete Action": "Eliminar acción",
    "Duplicate": "Duplicar",

    # Events
    "Create": "Crear",
    "Destroy": "Destruir",
    "Step": "Paso",
    "Begin Step": "Inicio de paso",
    "End Step": "Fin de paso",
    "Alarm": "Alarma",
    "Keyboard": "Teclado",
    "Key Press": "Tecla presionada",
    "Key Release": "Tecla liberada",
    "Mouse": "Ratón",
    "Collision": "Colisión",
    "Other": "Otro",
    "Draw": "Dibujar",
    "Game Start": "Inicio del juego",
    "Game End": "Fin del juego",
    "Room Start": "Inicio de sala",
    "Room End": "Fin de sala",
    "Animation End": "Fin de animación",
    "Path End": "Fin de ruta",
    "Outside Room": "Fuera de sala",
    "User Defined": "Definido por usuario",
    "Left Button": "Botón izquierdo",
    "Right Button": "Botón derecho",
    "Middle Button": "Botón central",
    "Mouse Enter": "Ratón entra",
    "Mouse Leave": "Ratón sale",
    "Mouse Wheel Up": "Rueda arriba",
    "Mouse Wheel Down": "Rueda abajo",
    "No Key": "Sin tecla",
    "Any Key": "Cualquier tecla",
    "Space": "Espacio",
    "Enter": "Intro",
    "Escape": "Escape",
    "Arrow Left": "Flecha izquierda",
    "Arrow Right": "Flecha derecha",
    "Arrow Up": "Flecha arriba",
    "Arrow Down": "Flecha abajo",

    # Room
    "Room": "Sala",
    "Room Editor": "Editor de salas",
    "Edit Room": "Editar sala",
    "Room Settings": "Configuración de sala",
    "Room Size": "Tamaño de sala",
    "Room Speed": "Velocidad de sala",
    "Room Caption": "Título de sala",
    "Persistent Room": "Sala persistente",
    "Creation Code": "Código de creación",
    "Instances": "Instancias",
    "Instance": "Instancia",
    "Add Instance": "Añadir instancia",
    "Delete Instance": "Eliminar instancia",
    "Views": "Vistas",
    "View": "Vista",
    "Enable Views": "Habilitar vistas",
    "Grid": "Cuadrícula",
    "Show Grid": "Mostrar cuadrícula",
    "Snap to Grid": "Ajustar a cuadrícula",
    "Zoom": "Zoom",
    "Zoom In": "Acercar",
    "Zoom Out": "Alejar",

    # Actions
    "Move": "Mover",
    "Movement": "Movimiento",
    "Main1": "Principal 1",
    "Main2": "Principal 2",
    "Control": "Control",
    "Score": "Puntuación",
    "Extra": "Extra",
    "Drawing": "Dibujo",
    "Code": "Código",
    "Set Motion": "Establecer movimiento",
    "Set Direction": "Establecer dirección",
    "Set Speed": "Establecer velocidad",
    "Set Gravity": "Establecer gravedad",
    "Set Friction": "Establecer fricción",
    "Jump to Position": "Saltar a posición",
    "Jump to Random": "Saltar a aleatorio",
    "Jump to Start": "Saltar al inicio",
    "Bounce": "Rebotar",
    "Set Alarm": "Establecer alarma",
    "Execute Code": "Ejecutar código",
    "Execute Script": "Ejecutar script",
    "Comment": "Comentario",
    "Variable": "Variable",
    "Set Variable": "Establecer variable",
    "Start Block": "Iniciar bloque",
    "End Block": "Terminar bloque",
    "Else": "Si no",
    "Repeat": "Repetir",
    "Exit Event": "Salir de evento",
    "Create Instance": "Crear instancia",
    "Change Instance": "Cambiar instancia",
    "Destroy Instance": "Destruir instancia",
    "Set Sprite": "Establecer sprite",
    "Play Sound": "Reproducir sonido",
    "Stop Sound": "Detener sonido",
    "Previous Room": "Sala anterior",
    "Next Room": "Sala siguiente",
    "Restart Room": "Reiniciar sala",
    "Go to Room": "Ir a sala",
    "Goto Room": "Ir a sala",
    "Set Lives": "Establecer vidas",
    "Set Score": "Establecer puntuación",
    "Set Health": "Establecer salud",
    "Draw Lives": "Dibujar vidas",
    "Draw Score": "Dibujar puntuación",
    "Draw Health": "Dibujar salud",
    "Show Message": "Mostrar mensaje",
    "Restart Game": "Reiniciar juego",
    "End Game": "Terminar juego",
    "Draw Sprite": "Dibujar sprite",
    "Draw Text": "Dibujar texto",
    "Draw Rectangle": "Dibujar rectángulo",
    "Draw Ellipse": "Dibujar elipse",
    "Draw Line": "Dibujar línea",
    "Set Color": "Establecer color",
    "Set Font": "Establecer fuente",

    # Export
    "Run Game": "Ejecutar juego",
    "Stop Game": "Detener juego",
    "Compile": "Compilar",
    "Export": "Exportar",
    "Export to Windows": "Exportar a Windows",
    "Export to HTML5": "Exportar a HTML5",
    "Export to Linux": "Exportar a Linux",
    "Export to Kivy": "Exportar a Kivy",
    "Export Settings": "Configuración de exportación",
    "Target Platform": "Plataforma destino",
    "Output Folder": "Carpeta de salida",
    "Game Name": "Nombre del juego",
    "Exporting...": "Exportando...",
    "Export Complete": "Exportación completada",
    "Export Failed": "Exportación fallida",

    # Preferences
    "General": "General",
    "Appearance": "Apariencia",
    "Editor": "Editor",
    "Compiler": "Compilador",
    "Font Settings": "Configuración de fuente",
    "Font Size": "Tamaño de fuente",
    "Font Family": "Familia de fuente",
    "Theme": "Tema",
    "Dark Theme": "Tema oscuro",
    "Light Theme": "Tema claro",
    "System Theme": "Tema del sistema",
    "Auto-Save": "Guardado automático",
    "Auto-Save Settings": "Configuración de guardado automático",
    "Enable automatic saving": "Habilitar guardado automático",
    "Save Interval": "Intervalo de guardado",
    " seconds": " segundos",
    "seconds": "segundos",
    "Save every:": "Guardar cada:",
    "Presets:": "Preajustes:",

    # Blockly
    "Blockly Editor": "Editor Blockly",
    "Visual Programming": "Programación visual",
    "Blocks": "Bloques",
    "Toolbox": "Caja de herramientas",
    "Workspace": "Espacio de trabajo",
    "Variables": "Variables",
    "Functions": "Funciones",
    "Logic": "Lógica",
    "Loops": "Bucles",
    "Math": "Matemáticas",
    "Text": "Texto",
    "Lists": "Listas",

    # Status
    "Ready": "Listo",
    "Modified": "Modificado",
    "Saved": "Guardado",
    "Running": "Ejecutando",
    "Compiling": "Compilando",

    # Properties panel
    "X": "X",
    "Y": "Y",
    "X:": "X:",
    "Y:": "Y:",
    "Position": "Posición",
    "Scale": "Escala",
    "Rotation": "Rotación",
    "Angle": "Ángulo",
    "Alpha": "Alfa",
    "Color": "Color",
    "Direction": "Dirección",
    "Horizontal": "Horizontal",
    "Vertical": "Vertical",

    # Messages
    "Are you sure?": "¿Está seguro?",
    "Delete confirmation": "Confirmar eliminación",
    "Do you want to save changes?": "¿Desea guardar los cambios?",
    "Unsaved changes": "Cambios sin guardar",
    "This action cannot be undone.": "Esta acción no se puede deshacer.",
    "Project has been saved.": "El proyecto ha sido guardado.",
    "File not found.": "Archivo no encontrado.",
    "Invalid file format.": "Formato de archivo inválido.",
    "Please select an item.": "Por favor seleccione un elemento.",
    "Please enter a name.": "Por favor ingrese un nombre.",
    "Name already exists.": "El nombre ya existe.",
    "Invalid name.": "Nombre inválido.",
    "Select a file": "Seleccione un archivo",
    "Select a folder": "Seleccione una carpeta",
    "Image Files": "Archivos de imagen",
    "Sound Files": "Archivos de sonido",
    "All Files": "Todos los archivos",
    "Project Files": "Archivos de proyecto",

    # Asset operations
    "Create Sprite": "Crear sprite",
    "Create Sound": "Crear sonido",
    "Create Background": "Crear fondo",
    "Create Object": "Crear objeto",
    "Create Room": "Crear sala",
    "Rename": "Renombrar",
    "Show in Explorer": "Mostrar en explorador",
    "Expand All": "Expandir todo",
    "Collapse All": "Contraer todo",
    "Import": "Importar",
    "Import Assets": "Importar recursos",

    # Format strings with placeholders
    "{0} Properties - {1}": "Propiedades de {0} - {1}",
    "Type: {0}": "Tipo: {0}",
    "File: {0}": "Archivo: {0}",
    "Status: {0}": "Estado: {0}",
    "Created: {0}": "Creado: {0}",
    "Modified: {0}": "Modificado: {0}",
    "Size: {0}": "Tamaño: {0}",
    "Dimensions: {0}": "Dimensiones: {0}",
    "Cannot save: {0}": "No se puede guardar: {0}",
    "Saved: {0}": "Guardado: {0}",
    "Save Error": "Error al guardar",
    "Error saving object: {0}": "Error al guardar objeto: {0}",
    "Loaded {0} sprites": "Cargados {0} sprites",
    "Error loading assets: {0}": "Error al cargar recursos: {0}",

    # Action configuration
    "Apply to:": "Aplicar a:",
    "Self": "Propio",
    "Relative": "Relativo",
    "NOT": "NO",
    "Question": "Pregunta",
    "Apply to": "Aplicar a",
    "→ Next Room": "→ Sala siguiente",
    "← Previous Room": "← Sala anterior",
    "↺ Restart Current Room": "↺ Reiniciar sala actual",
    "⚙️ Configure...": "⚙️ Configurar...",
    "🎨 Choose Color...": "🎨 Elegir color...",
    "📥 Import Image...": "📥 Importar imagen...",
    "(No sprites available)": "(Sin sprites disponibles)",
    "(No sounds available)": "(Sin sonidos disponibles)",
    "(No objects available)": "(Sin objetos disponibles)",
    "(No rooms available)": "(Sin salas disponibles)",
    "Enter code here...": "Ingrese código aquí...",
    "Choose Color": "Elegir color",

    # Labels with colons
    "Name:": "Nombre:",
    "Value:": "Valor:",
    "Message:": "Mensaje:",
    "Code:": "Código:",
    "Script:": "Script:",
    "Object:": "Objeto:",
    "Room:": "Sala:",
    "Target:": "Objetivo:",
    "Width:": "Ancho:",
    "Height:": "Alto:",
    "Speed:": "Velocidad:",
    "Caption:": "Título:",
    "Depth:": "Profundidad:",
    "Parent:": "Padre:",

    # Imported status
    "Imported": "Importado",
    "Not imported": "No importado",

    # Welcome screen
    "Welcome to PyGameMaker IDE": "Bienvenido a PyGameMaker IDE",
    "Start a new project or open an existing one": "Inicie un nuevo proyecto o abra uno existente",
    "Create a new project": "Crear un nuevo proyecto",
    "Open an existing project": "Abrir un proyecto existente",
    "Recent projects:": "Proyectos recientes:",
    "No recent projects": "Sin proyectos recientes",
    "Current project:": "Proyecto actual:",
    "No project open": "Sin proyecto abierto",

    # Various UI
    "Note: Some settings require restarting the IDE to take effect.": "Nota: Algunos ajustes requieren reiniciar el IDE para aplicarse.",
    "Documentation": "Documentación",
    "Keyboard Shortcuts": "Atajos de teclado",

    # Room editor specific
    "Show color": "Mostrar color",
    "Background color": "Color de fondo",
    "Visible at start": "Visible al inicio",
    "Foreground image": "Imagen en primer plano",
    "Stretch image": "Estirar imagen",
    "Object to follow:": "Objeto a seguir:",
    "Horizontal border:": "Borde horizontal:",
    "Vertical border:": "Borde vertical:",
    "Horizontal speed:": "Velocidad horizontal:",
    "Vertical speed:": "Velocidad vertical:",

    # Keys
    "Numpad": "Núm",
    "Insert": "Insertar",
    "Home": "Inicio",
    "End": "Fin",
    "PageUp": "Re Pág",
    "PageDown": "Av Pág",
    "Tab": "Tab",
    "Backspace": "Retroceso",
    "Shift": "Mayús",
    "Alt": "Alt",
    "Left": "Izquierda",
    "Right": "Derecha",
    "Up": "Arriba",
    "Down": "Abajo",
}

def translate_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    translations_dir = os.path.join(project_dir, 'translations')

    input_file = os.path.join(translations_dir, 'pygm2_fr.ts')
    output_file = os.path.join(translations_dir, 'pygm2_es.ts')

    print("Creating comprehensive Spanish translation...")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change language
    content = re.sub(r'language="[^"]*"', 'language="es_ES"', content)
    if 'language=' not in content:
        content = content.replace('<TS version="2.1">', '<TS version="2.1" language="es_ES">')

    def translate_message(match):
        message = match.group(0)

        # Get source
        source_match = re.search(r'<source>(.*?)</source>', message, re.DOTALL)
        if not source_match:
            return message

        source_raw = source_match.group(1)
        source = source_raw.replace('&apos;', "'").replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        # Check for direct translation
        if source in EN_TO_ES:
            spanish = EN_TO_ES[source]
            spanish_xml = spanish.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;')
            message = re.sub(
                r'<translation[^>]*>.*?</translation>|<translation[^/>]*/\s*>',
                f'<translation>{spanish_xml}</translation>',
                message,
                flags=re.DOTALL
            )
            return message

        # Check for pattern matches with placeholders
        for en_pattern, es_pattern in EN_TO_ES.items():
            if '{' in en_pattern:
                # Create regex from pattern
                regex_pattern = re.escape(en_pattern)
                regex_pattern = regex_pattern.replace(r'\{0\}', '(.+?)').replace(r'\{1\}', '(.+?)').replace(r'\{2\}', '(.+?)')
                regex_pattern = regex_pattern.replace(r'\{target_object\}', '(.+?)').replace(r'\{e\}', '(.+?)')
                regex_pattern = regex_pattern.replace(r'\{event_type\.icon\}', '(.+?)').replace(r'\{sub_event_key\.title\(\)\}', '(.+?)')
                regex_pattern = regex_pattern.replace(r'\{action_type\.icon\}', '(.+?)').replace(r'\{action_type\.display_name\}', '(.+?)')

                m = re.match(f'^{regex_pattern}$', source)
                if m:
                    spanish = es_pattern
                    for i, g in enumerate(m.groups()):
                        spanish = spanish.replace(f'{{{i}}}', g, 1)
                        # Also replace named placeholders
                        if i == 0:
                            spanish = spanish.replace('{target_object}', g)
                            spanish = spanish.replace('{e}', g)
                            spanish = spanish.replace('{event_type.icon}', g)
                            spanish = spanish.replace('{action_type.icon}', g)

                    spanish_xml = spanish.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;')
                    message = re.sub(
                        r'<translation[^>]*>.*?</translation>|<translation[^/>]*/\s*>',
                        f'<translation>{spanish_xml}</translation>',
                        message,
                        flags=re.DOTALL
                    )
                    return message

        return message

    content = re.sub(r'<message>.*?</message>', translate_message, content, flags=re.DOTALL)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Stats
    total = content.count('<message>')
    unfinished = content.count('type="unfinished"')
    vanished = content.count('type="vanished"')
    translated = total - unfinished - vanished

    print(f"\nResults:")
    print(f"  Total: {total}")
    print(f"  Translated: {translated}")
    print(f"  Unfinished: {unfinished}")
    print(f"  Vanished: {vanished}")
    print(f"  Completion: {translated * 100 // total}%")

if __name__ == '__main__':
    translate_file()
