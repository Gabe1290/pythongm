#!/usr/bin/env python3
"""
Complete Spanish translation file for PyGameMaker IDE
Replaces all French translations with Spanish ones
"""

import re
import os

# Complete Spanish translations - all strings
SPANISH_TRANSLATIONS = {
    # About Dialog - HTML content
    "<h3>PyGameMaker IDE</h3><p>A GameMaker-inspired IDE for creating 2D games with Python.</p><h4>Features:</h4><ul><li>Visual scripting with events and actions</li><li>Asset management for sprites, sounds, and objects</li><li>Room-based game development</li><li>Export to standalone Python games</li></ul><h4>Built with:</h4><ul><li>PySide6 for the user interface</li><li>Pygame for game runtime</li><li>Python 3.11+</li></ul>": "<h3>PyGameMaker IDE</h3><p>Un IDE inspirado en GameMaker para crear juegos 2D con Python.</p><h4>Características:</h4><ul><li>Programación visual con eventos y acciones</li><li>Gestión de recursos para sprites, sonidos y objetos</li><li>Desarrollo de juegos basado en salas</li><li>Exportación a juegos Python independientes</li></ul><h4>Desarrollado con:</h4><ul><li>PySide6 para la interfaz de usuario</li><li>Pygame para la ejecución del juego</li><li>Python 3.11+</li></ul>",

    # Credits
    "Credits:\n\nDevelopment:\n- Gabriel Thullen\n\nSpecial Thanks:\n- The GameMaker Studio community for inspiration\n- The Python and Pygame communities\n- All contributors and testers\n\nThird-Party Libraries:\n- PySide6 (Qt for Python) - LGPLv3\n- Pygame (game development library) - LGPLv2.1\n- Pillow (image processing) - HPND\n- Blockly (visual programming) - Apache 2.0\n\nLicense:\nThis software is released under the GNU General Public License v3 (GPLv3).\nCopyright (C) 2024-2025 Gabriel Thullen": "Créditos:\n\nDesarrollo:\n- Gabriel Thullen\n\nAgradecimientos especiales:\n- La comunidad de GameMaker Studio por la inspiración\n- Las comunidades de Python y Pygame\n- Todos los colaboradores y testers\n\nBibliotecas de terceros:\n- PySide6 (Qt para Python) - LGPLv3\n- Pygame (biblioteca de desarrollo de juegos) - LGPLv2.1\n- Pillow (procesamiento de imágenes) - HPND\n- Blockly (programación visual) - Apache 2.0\n\nLicencia:\nEste software se distribuye bajo la Licencia Pública General de GNU v3 (GPLv3).\nCopyright (C) 2024-2025 Gabriel Thullen",

    # UI Elements with emojis
    "⬆️ Move Up": "⬆️ Mover arriba",
    "⬇️ Move Down": "⬇️ Mover abajo",
    "📋 Event List": "📋 Lista de eventos",
    "💻 Code Editor": "💻 Editor de código",
    "🎮 Test Object": "🎮 Probar objeto",
    "📋 Configure...": "📋 Configurar...",
    "📖 View Generated Code": "📖 Ver código generado",
    "✏️ Edit Custom Code": "✏️ Editar código personalizado",
    "✅ Apply Changes": "✅ Aplicar cambios",
    "🔄 Refresh": "🔄 Actualizar",

    # Object editor
    "Open Blockly editor in a separate window": "Abrir editor Blockly en una ventana separada",
    "Apply to Events →": "Aplicar a eventos →",
    "Instances:": "Instancias:",
    "Pick Color": "Seleccionar color",
    "Object: Not loaded": "Objeto: No cargado",
    "No event selected": "Ningún evento seleccionado",
    "Actions are managed through the Object Events panel on the left.  Select an event and right-click to add actions.": "Las acciones se gestionan a través del panel de Eventos de Objetos a la izquierda. Seleccione un evento y haga clic derecho para añadir acciones.",
    "Mode:": "Modo:",
    "Event for custom code:": "Evento para código personalizado:",
    "Validation Error": "Error de validación",
    "Cannot save: {0}": "No se puede guardar: {0}",
    "Saved: {0}": "Guardado: {0}",
    "Save Error": "Error al guardar",
    "Error saving object: {0}": "Error al guardar objeto: {0}",
    "Loaded {0} sprites": "Cargados {0} sprites",
    "Error loading assets: {0}": "Error al cargar recursos: {0}",
    "Object name is required": "El nombre del objeto es obligatorio",
    "Referenced sprite '{0}' does not exist": "El sprite referenciado '{0}' no existe",
    "Event '{0}' has invalid data structure": "El evento '{0}' tiene una estructura de datos inválida",
    "Event '{0}' has invalid actions data": "El evento '{0}' tiene datos de acciones inválidos",
    "Validation error: {0}": "Error de validación: {0}",
    "Object: {0} | Sprite: {1}": "Objeto: {0} | Sprite: {1}",
    "Editing event: {0}": "Editando evento: {0}",
    "Applied {0} events from visual blocks": "Aplicados {0} eventos desde bloques visuales",
    "Selected action: {0} ({1})": "Acción seleccionada: {0} ({1})",
    "Object testing not implemented yet": "Prueba de objeto aún no implementada",
    "Generated code view updated": "Vista de código generado actualizada",
    "Edit mode: Write custom Python code": "Modo edición: Escribir código Python personalizado",
    "View mode: Showing generated code from events": "Modo vista: Mostrando código generado de eventos",
    "Custom code applied to {0} event": "Código personalizado aplicado al evento {0}",
    "Code Applied": "Código aplicado",
    "Custom Python code has been applied to the {0} event.  The code will execute when the event triggers.": "El código Python personalizado se ha aplicado al evento {0}. El código se ejecutará cuando el evento se active.",
    "Assets loaded: {0} sprites": "Recursos cargados: {0} sprites",
    "Event": "Evento",
    "- Remove Event": "- Eliminar evento",
    "↑ Move Up": "↑ Mover arriba",
    "↓ Move Down": "↓ Mover abajo",
    "+ Add Event": "+ Añadir evento",

    # Code comments
    "# No events or actions have been added yet. # Add events in the Object Events panel to see generated code here.": "# Aún no se han añadido eventos ni acciones. # Añada eventos en el panel de Eventos de Objetos para ver el código generado aquí.",
    "# Python code editor # Switch to 'Edit Custom Code' mode to write your own Python code # Or use the visual event/action system and view generated code here": "# Editor de código Python # Cambie al modo 'Editar código personalizado' para escribir su propio código Python # O use el sistema visual de eventos/acciones y vea el código generado aquí",

    # French to Spanish direct mappings for remaining items
    "À propos de PyGameMaker IDE": "Acerca de PyGameMaker IDE",
    "À propos": "Acerca de",
    "Crédits": "Créditos",
    "Fermer": "Cerrar",
    "Configurer {0}": "Configurar {0}",
    "Cette action nécessite une configuration spéciale.": "Esta acción requiere una configuración especial.",
    "Salle suivante": "Sala siguiente",
    "Salle précédente": "Sala anterior",
    "Redémarrer la salle actuelle": "Reiniciar sala actual",
    "Configurer...": "Configurar...",
    "Configurer les actions...": "Configurar acciones...",
    "Choisir une couleur...": "Elegir color...",
    "(Aucun sprite disponible)": "(Sin sprites disponibles)",
    "(Aucun son disponible)": "(Sin sonidos disponibles)",
    "Entrez le code ici...": "Ingrese el código aquí...",
    "Choisir une couleur": "Elegir color",
    "Propriétés de {0} - {1}": "Propiedades de {0} - {1}",
    "Type : {0}": "Tipo: {0}",
    "Fichier : {0}": "Archivo: {0}",
    "Importé": "Importado",
    "Non importé": "No importado",
    "Statut : {0}": "Estado: {0}",
    "Importer une image...": "Importar imagen...",
    "Créé : {0}": "Creado: {0}",
    "Modifié : {0}": "Modificado: {0}",
    "Taille : {0}": "Tamaño: {0}",
    "Dimensions : {0}": "Dimensiones: {0}",
    "Créer un sprite": "Crear sprite",
    "Nom du sprite :": "Nombre del sprite:",
    "Le nom du sprite est requis.": "El nombre del sprite es obligatorio.",
    "Erreur de création": "Error de creación",
    "Erreur lors de la création du sprite : {0}": "Error al crear el sprite: {0}",
    "Ouvrir le sprite": "Abrir sprite",
    "Modifier le sprite...": "Editar sprite...",
    "Renommer le sprite...": "Renombrar sprite...",
    "Dupliquer le sprite...": "Duplicar sprite...",
    "Supprimer le sprite": "Eliminar sprite",
    "Confirmer la suppression": "Confirmar eliminación",
    "Êtes-vous sûr de vouloir supprimer le sprite '{0}' ?": "¿Está seguro de que desea eliminar el sprite '{0}'?",
    "Sprites": "Sprites",
    "Sons": "Sonidos",
    "Arrière-plans": "Fondos",
    "Objets": "Objetos",
    "Salles": "Salas",
    "Ressources de jeu": "Recursos del juego",
    "Créer un son": "Crear sonido",
    "Nom du son :": "Nombre del sonido:",
    "Le nom du son est requis.": "El nombre del sonido es obligatorio.",
    "Erreur lors de la création du son : {0}": "Error al crear el sonido: {0}",
    "Ouvrir le son": "Abrir sonido",
    "Modifier le son...": "Editar sonido...",
    "Renommer le son...": "Renombrar sonido...",
    "Dupliquer le son...": "Duplicar sonido...",
    "Supprimer le son": "Eliminar sonido",
    "Êtes-vous sûr de vouloir supprimer le son '{0}' ?": "¿Está seguro de que desea eliminar el sonido '{0}'?",
    "Créer un arrière-plan": "Crear fondo",
    "Nom de l'arrière-plan :": "Nombre del fondo:",
    "Le nom de l'arrière-plan est requis.": "El nombre del fondo es obligatorio.",
    "Erreur lors de la création de l'arrière-plan : {0}": "Error al crear el fondo: {0}",
    "Ouvrir l'arrière-plan": "Abrir fondo",
    "Modifier l'arrière-plan...": "Editar fondo...",
    "Renommer l'arrière-plan...": "Renombrar fondo...",
    "Dupliquer l'arrière-plan...": "Duplicar fondo...",
    "Supprimer l'arrière-plan": "Eliminar fondo",
    "Êtes-vous sûr de vouloir supprimer l'arrière-plan '{0}' ?": "¿Está seguro de que desea eliminar el fondo '{0}'?",
    "Créer un objet": "Crear objeto",
    "Nom de l'objet :": "Nombre del objeto:",
    "Le nom de l'objet est requis.": "El nombre del objeto es obligatorio.",
    "Erreur lors de la création de l'objet : {0}": "Error al crear el objeto: {0}",
    "Ouvrir l'objet": "Abrir objeto",
    "Modifier l'objet...": "Editar objeto...",
    "Renommer l'objet...": "Renombrar objeto...",
    "Dupliquer l'objet...": "Duplicar objeto...",
    "Supprimer l'objet": "Eliminar objeto",
    "Êtes-vous sûr de vouloir supprimer l'objet '{0}' ?": "¿Está seguro de que desea eliminar el objeto '{0}'?",
    "Créer une salle": "Crear sala",
    "Nom de la salle :": "Nombre de la sala:",
    "Le nom de la salle est requis.": "El nombre de la sala es obligatorio.",
    "Erreur lors de la création de la salle : {0}": "Error al crear la sala: {0}",
    "Ouvrir la salle": "Abrir sala",
    "Modifier la salle...": "Editar sala...",
    "Renommer la salle...": "Renombrar sala...",
    "Dupliquer la salle...": "Duplicar sala...",
    "Supprimer la salle": "Eliminar sala",
    "Êtes-vous sûr de vouloir supprimer la salle '{0}' ?": "¿Está seguro de que desea eliminar la sala '{0}'?",
    "Nouveau projet": "Nuevo proyecto",
    "Ouvrir un projet": "Abrir proyecto",
    "Projets récents": "Proyectos recientes",
    "Enregistrer le projet": "Guardar proyecto",
    "Enregistrer sous...": "Guardar como...",
    "Exporter le projet": "Exportar proyecto",
    "Quitter": "Salir",
    "Préférences": "Preferencias",
    "Annuler": "Deshacer",
    "Rétablir": "Rehacer",
    "Couper": "Cortar",
    "Copier": "Copiar",
    "Coller": "Pegar",
    "Supprimer": "Eliminar",
    "Tout sélectionner": "Seleccionar todo",
    "Exécuter le jeu": "Ejecutar juego",
    "Arrêter le jeu": "Detener juego",
    "Documentation": "Documentación",
    "Raccourcis clavier": "Atajos de teclado",
    "Fichier": "Archivo",
    "Édition": "Edición",
    "Ressources": "Recursos",
    "Exécuter": "Ejecutar",
    "Aide": "Ayuda",
    "Paramètres de police": "Configuración de fuente",
    "Taille de police :": "Tamaño de fuente:",
    "Famille de police :": "Familia de fuente:",
    "Sauvegarde automatique": "Guardado automático",
    "Activer la sauvegarde automatique": "Activar guardado automático",
    "Lorsqu'elle est activée, votre projet sera automatiquement enregistré à intervalles réguliers.": "Cuando está activado, su proyecto se guardará automáticamente a intervalos regulares.",
    "Intervalle de sauvegarde": "Intervalo de guardado",
    "Enregistrer toutes les :": "Guardar cada:",
    "Préréglages :": "Preajustes:",
    "Les intervalles plus courts peuvent affecter les performances sur les grands projets.": "Los intervalos más cortos pueden afectar el rendimiento en proyectos grandes.",
    "Langue": "Idioma",
    "Thème": "Tema",
    "Thème clair": "Tema claro",
    "Thème sombre": "Tema oscuro",
    "Thème système": "Tema del sistema",
    "Editeur de sprites": "Editor de sprites",
    "Editeur de sons": "Editor de sonidos",
    "Editeur d'arrière-plans": "Editor de fondos",
    "Editeur d'objets": "Editor de objetos",
    "Editeur de salles": "Editor de salas",
    "Éditeur de sprite": "Editor de sprite",
    "Éditeur de son": "Editor de sonido",
    "Éditeur d'arrière-plan": "Editor de fondo",
    "Éditeur d'objet": "Editor de objeto",
    "Éditeur de salle": "Editor de sala",
    "Nom :": "Nombre:",
    "Sprite :": "Sprite:",
    "Parent :": "Padre:",
    "Aucun parent": "Sin padre",
    "Visible": "Visible",
    "Solide": "Sólido",
    "Persistant": "Persistente",
    "Profondeur :": "Profundidad:",
    "Événements": "Eventos",
    "Ajouter un événement": "Añadir evento",
    "Supprimer l'événement": "Eliminar evento",
    "Actions": "Acciones",
    "Ajouter une action": "Añadir acción",
    "Supprimer l'action": "Eliminar acción",
    "Créer": "Crear",
    "Détruire": "Destruir",
    "Pas": "Paso",
    "Début du pas": "Inicio de paso",
    "Fin du pas": "Fin de paso",
    "Alarme": "Alarma",
    "Clavier": "Teclado",
    "Touche enfoncée": "Tecla presionada",
    "Touche relâchée": "Tecla liberada",
    "Souris": "Ratón",
    "Collision": "Colisión",
    "Autre": "Otro",
    "Dessin": "Dibujo",
    "Début du jeu": "Inicio del juego",
    "Fin du jeu": "Fin del juego",
    "Début de la salle": "Inicio de sala",
    "Fin de la salle": "Fin de sala",
    "Fin de l'animation": "Fin de animación",
    "Fin du chemin": "Fin de ruta",
    "Hors de la salle": "Fuera de la sala",
    "Intersection avec limite": "Intersección con límite",
    "Défini par l'utilisateur": "Definido por usuario",
    "Bouton gauche global": "Botón izquierdo global",
    "Bouton droit global": "Botón derecho global",
    "Bouton central global": "Botón central global",
    "Bouton gauche": "Botón izquierdo",
    "Bouton droit": "Botón derecho",
    "Bouton central": "Botón central",
    "Gauche enfoncé": "Izquierdo presionado",
    "Droit enfoncé": "Derecho presionado",
    "Central enfoncé": "Central presionado",
    "Gauche relâché": "Izquierdo liberado",
    "Droit relâché": "Derecho liberado",
    "Central relâché": "Central liberado",
    "Entrée souris": "Entrada de ratón",
    "Sortie souris": "Salida de ratón",
    "Molette vers le haut": "Rueda hacia arriba",
    "Molette vers le bas": "Rueda hacia abajo",
    "Aucune touche": "Sin tecla",
    "N'importe quelle touche": "Cualquier tecla",
    "Taille de la salle :": "Tamaño de la sala:",
    "Largeur :": "Ancho:",
    "Hauteur :": "Alto:",
    "Vitesse :": "Velocidad:",
    "Titre :": "Título:",
    "Couleur de fond :": "Color de fondo:",
    "Afficher la couleur": "Mostrar color",
    "Arrière-plans :": "Fondos:",
    "Vues :": "Vistas:",
    "Instances :": "Instancias:",
    "Grille :": "Cuadrícula:",
    "Afficher la grille": "Mostrar cuadrícula",
    "Aligner sur la grille": "Ajustar a cuadrícula",
    "Activer les vues": "Habilitar vistas",
    "Vue dans la salle": "Vista en sala",
    "Port à l'écran": "Puerto en pantalla",
    "Objet à suivre :": "Objeto a seguir:",
    "Bordure horizontale :": "Borde horizontal:",
    "Bordure verticale :": "Borde vertical:",
    "Vitesse horizontale :": "Velocidad horizontal:",
    "Vitesse verticale :": "Velocidad vertical:",
    "Exporter vers Windows": "Exportar a Windows",
    "Exporter vers HTML5": "Exportar a HTML5",
    "Exporter vers Linux": "Exportar a Linux",
    "Exporter vers Kivy": "Exportar a Kivy",
    "Nom du jeu :": "Nombre del juego:",
    "Dossier de sortie :": "Carpeta de salida:",
    "Parcourir...": "Examinar...",
    "Inclure le débogage": "Incluir depuración",
    "Compresser la sortie": "Comprimir salida",
    "Exporter": "Exportar",
    "Annuler": "Cancelar",
    "Exportation en cours...": "Exportando...",
    "Exportation terminée !": "¡Exportación completada!",
    "Erreur d'exportation : {0}": "Error de exportación: {0}",
    "Mouvement": "Movimiento",
    "Principal 1": "Principal 1",
    "Principal 2": "Principal 2",
    "Contrôle": "Control",
    "Puntuación": "Puntuación",
    "Dibujo": "Dibujo",
    "Déplacer fixe": "Mover fijo",
    "Déplacer libre": "Mover libre",
    "Déplacer vers": "Mover hacia",
    "Vitesse horizontale": "Velocidad horizontal",
    "Vitesse verticale": "Velocidad vertical",
    "Inverser horizontal": "Invertir horizontal",
    "Inverser vertical": "Invertir vertical",
    "Établir la gravité": "Establecer gravedad",
    "Établir la friction": "Establecer fricción",
    "Sauter à une position": "Saltar a posición",
    "Sauter au départ": "Saltar al inicio",
    "Sauter aléatoirement": "Saltar aleatoriamente",
    "Aligner sur la grille": "Ajustar a cuadrícula",
    "Entourer l'écran": "Envolver pantalla",
    "Déplacer au contact": "Mover al contacto",
    "Rebondir": "Rebotar",
    "Définir le chemin": "Establecer ruta",
    "Terminer le chemin": "Terminar ruta",
    "Définir l'alarme": "Establecer alarma",
    "Exécuter du code": "Ejecutar código",
    "Exécuter un script": "Ejecutar script",
    "Commentaire": "Comentario",
    "Définir une variable": "Establecer variable",
    "Tester une variable": "Probar variable",
    "Tester une expression": "Probar expresión",
    "Début du bloc": "Inicio de bloque",
    "Fin du bloc": "Fin de bloque",
    "Sinon": "Si no",
    "Répéter": "Repetir",
    "Quitter l'événement": "Salir de evento",
    "Appeler l'événement parent": "Llamar evento padre",
    "Créer une instance": "Crear instancia",
    "Créer en mouvement": "Crear en movimiento",
    "Créer aléatoire": "Crear aleatorio",
    "Changer d'instance": "Cambiar instancia",
    "Détruire l'instance": "Destruir instancia",
    "Détruire à la position": "Destruir en posición",
    "Définir le sprite": "Establecer sprite",
    "Transformer le sprite": "Transformar sprite",
    "Colorier le sprite": "Colorear sprite",
    "Jouer un son": "Reproducir sonido",
    "Arrêter un son": "Detener sonido",
    "Vérifier un son": "Verificar sonido",
    "Salle précédente": "Sala anterior",
    "Salle suivante": "Sala siguiente",
    "Redémarrer la salle": "Reiniciar sala",
    "Aller à la salle": "Ir a sala",
    "Si salle précédente existe": "Si existe sala anterior",
    "Si salle suivante existe": "Si existe sala siguiente",
    "Définir les vies": "Establecer vidas",
    "Définir le score": "Establecer puntuación",
    "Définir la santé": "Establecer salud",
    "Dessiner les vies": "Dibujar vidas",
    "Dessiner le score": "Dibujar puntuación",
    "Dessiner la santé": "Dibujar salud",
    "Définir le titre": "Establecer título",
    "Afficher un message": "Mostrar mensaje",
    "Afficher les informations": "Mostrar información",
    "Redémarrer le jeu": "Reiniciar juego",
    "Terminer le jeu": "Terminar juego",
    "Dessiner un sprite": "Dibujar sprite",
    "Dessiner un arrière-plan": "Dibujar fondo",
    "Dessiner du texte": "Dibujar texto",
    "Dessiner un rectangle": "Dibujar rectángulo",
    "Dessiner une ellipse": "Dibujar elipse",
    "Dessiner une ligne": "Dibujar línea",
    "Dessiner une flèche": "Dibujar flecha",
    "Dessiner un dégradé horizontal": "Dibujar degradado horizontal",
    "Dessiner un dégradé vertical": "Dibujar degradado vertical",
    "Définir la couleur": "Establecer color",
    "Définir la police": "Establecer fuente",
    "Plein écran": "Pantalla completa",
    "Prendre une capture": "Tomar captura",
    "Créer un effet": "Crear efecto",
    "Appliquer à :": "Aplicar a:",
    "Propre": "Propio",
    "Autre": "Otro",
    "Relatif": "Relativo",
    "Prêt": "Listo",
    "Modifié": "Modificado",
    "Enregistré": "Guardado",
    "En cours d'exécution": "Ejecutando",
    "Compilation en cours": "Compilando",
    "Erreur": "Error",
    "Connecté": "Conectado",
    "Déconnecté": "Desconectado",
    "Oui": "Sí",
    "Non": "No",
    "OK": "Aceptar",
    "Appliquer": "Aplicar",
    "Réinitialiser": "Restablecer",
    "Par défaut": "Predeterminado",
    "Personnalisé": "Personalizado",
    "Aucun": "Ninguno",
    "Tout": "Todo",
    "Sélectionner": "Seleccionar",
    "Importer": "Importar",
    "Renommer": "Renombrar",
    "Dupliquer": "Duplicar",
    "Développer tout": "Expandir todo",
    "Réduire tout": "Contraer todo",
    "Afficher dans l'explorateur": "Mostrar en explorador",
    "Général": "General",
    "Apparence": "Apariencia",
    "Éditeur": "Editor",
    "Compilateur": "Compilador",
    "Note : Certains paramètres nécessitent un redémarrage de l'IDE pour prendre effet.": "Nota: Algunos ajustes requieren reiniciar el IDE para aplicarse.",
    "Bienvenue dans PyGameMaker IDE": "Bienvenido a PyGameMaker IDE",
    "Démarrer un nouveau projet ou ouvrir un existant": "Inicie un nuevo proyecto o abra uno existente",
    "Créer un nouveau projet": "Crear un nuevo proyecto",
    "Ouvrir un projet existant": "Abrir un proyecto existente",
    "Projets récents :": "Proyectos recientes:",
    "Aucun projet récent": "Sin proyectos recientes",
    "Projet actuel :": "Proyecto actual:",
    "Aucun projet ouvert": "Sin proyecto abierto",
    "Déplacer vers le haut": "Mover arriba",
    "Déplacer vers le bas": "Mover abajo",
    "Liste des événements": "Lista de eventos",
    "Éditeur de code": "Editor de código",
    "Tester l'objet": "Probar objeto",
}

def create_spanish_translation():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    translations_dir = os.path.join(project_dir, 'translations')

    input_file = os.path.join(translations_dir, 'pygm2_fr.ts')
    output_file = os.path.join(translations_dir, 'pygm2_es.ts')

    print(f"Creating Spanish translation...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change language attribute
    content = re.sub(r'language="[^"]*"', 'language="es_ES"', content)

    # Function to translate a single message block
    def translate_message(match):
        message = match.group(0)

        # Extract source
        source_match = re.search(r'<source>(.*?)</source>', message, re.DOTALL)
        if not source_match:
            return message

        source_raw = source_match.group(1)

        # Decode HTML entities for lookup
        source = source_raw.replace('&apos;', "'").replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        # Check for English translation
        if source in SPANISH_TRANSLATIONS:
            spanish = SPANISH_TRANSLATIONS[source]
            # Encode for XML
            spanish_xml = spanish.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;')
            # Replace translation
            message = re.sub(
                r'<translation[^>]*>.*?</translation>|<translation[^/>]*/\s*>',
                f'<translation>{spanish_xml}</translation>',
                message,
                flags=re.DOTALL
            )
            return message

        # Check if there's already a French translation we can map
        trans_match = re.search(r'<translation>([^<]+)</translation>', message)
        if trans_match:
            french = trans_match.group(1)
            # Decode for lookup
            french_decoded = french.replace('&apos;', "'").replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

            if french_decoded in SPANISH_TRANSLATIONS:
                spanish = SPANISH_TRANSLATIONS[french_decoded]
                spanish_xml = spanish.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;')
                message = re.sub(
                    r'<translation>.*?</translation>',
                    f'<translation>{spanish_xml}</translation>',
                    message,
                    flags=re.DOTALL
                )
                return message

        return message

    # Process all messages
    content = re.sub(r'<message>.*?</message>', translate_message, content, flags=re.DOTALL)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Count results
    total = content.count('<message>')
    unfinished = content.count('type="unfinished"')
    vanished = content.count('type="vanished"')
    translated = total - unfinished - vanished

    print(f"\nResults:")
    print(f"  Total messages: {total}")
    print(f"  Translated: {translated}")
    print(f"  Unfinished: {unfinished}")
    print(f"  Vanished: {vanished}")
    print(f"  Completion: {translated * 100 // total}%")


if __name__ == '__main__':
    create_spanish_translation()
