#!/usr/bin/env python3
"""Fix remaining French strings in Spanish translation"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
ts_file = os.path.join(project_dir, 'translations', 'pygm2_es.ts')

with open(ts_file, 'r', encoding='utf-8') as f:
    content = f.read()

# French to Spanish replacements
replacements = {
    # File dialogs
    '>Sélectionner une image de sprite<': '>Seleccionar imagen de sprite<',
    '>Fichiers image (': '>Archivos de imagen (',
    '>Image chargée avec succès<': '>Imagen cargada correctamente<',
    '>Sélectionner un fichier audio<': '>Seleccionar archivo de audio<',
    '>Fichiers audio (': '>Archivos de audio (',

    # Common UI
    '>Nouveau<': '>Nuevo<',
    '>Ouvrir<': '>Abrir<',
    '>Enregistrer<': '>Guardar<',
    '>Fermer<': '>Cerrar<',
    '>Annuler<': '>Cancelar<',
    '>Appliquer<': '>Aplicar<',
    '>Supprimer<': '>Eliminar<',
    '>Modifier<': '>Editar<',
    '>Ajouter<': '>Añadir<',
    '>Renommer<': '>Renombrar<',
    '>Dupliquer<': '>Duplicar<',
    '>Importer<': '>Importar<',
    '>Exporter<': '>Exportar<',
    '>Actualiser<': '>Actualizar<',

    # Status
    '>Prêt<': '>Listo<',
    '>Modifié<': '>Modificado<',
    '>Enregistré<': '>Guardado<',
    '>Erreur<': '>Error<',
    '>Succès<': '>Éxito<',

    # Events
    '>Créer<': '>Crear<',
    '>Détruire<': '>Destruir<',
    '>Pas<': '>Paso<',
    '>Alarme<': '>Alarma<',
    '>Clavier<': '>Teclado<',
    '>Souris<': '>Ratón<',
    '>Dessin<': '>Dibujo<',

    # Actions
    '>Mouvement<': '>Movimiento<',
    '>Contrôle<': '>Control<',
    '>Score<': '>Puntuación<',

    # Menu
    '>Fichier<': '>Archivo<',
    '>Édition<': '>Edición<',
    '>Ressources<': '>Recursos<',
    '>Exécuter<': '>Ejecutar<',
    '>Aide<': '>Ayuda<',
    '>Quitter<': '>Salir<',

    # Preferences
    '>Préférences<': '>Preferencias<',
    '>Général<': '>General<',
    '>Apparence<': '>Apariencia<',
    '>Éditeur<': '>Editor<',
    '>Langue<': '>Idioma<',
    '>Thème<': '>Tema<',

    # Sprite/Object/Room
    '>Origine<': '>Origen<',
    '>Largeur<': '>Ancho<',
    '>Hauteur<': '>Alto<',
    '>Événements<': '>Eventos<',
    '>Propriétés<': '>Propiedades<',
    '>Sprite<': '>Sprite<',
    '>Parent<': '>Padre<',
    '>Profondeur<': '>Profundidad<',
    '>Visible<': '>Visible<',
    '>Solide<': '>Sólido<',
    '>Persistant<': '>Persistente<',
    '>Instances<': '>Instancias<',
    '>Vues<': '>Vistas<',

    # Resources
    '>Ressources de jeu<': '>Recursos del juego<',
}

count = 0
for fr, es in replacements.items():
    if fr in content:
        content = content.replace(fr, es)
        count += 1

with open(ts_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Applied {count} French to Spanish replacements')
