# micro:bit

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Effacer l'écran

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_clear_display` |
| **Icône** | ⬛ |
| **Catégorie** | micro:bit |

Éteindre toutes les LED et abandonner ce qui était en attente

*Paramètres:* aucun

### Si bouton pressé

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_if_button` |
| **Icône** | 🔘 |
| **Catégorie** | micro:bit |

Vrai tant que le bouton est maintenu enfoncé (A+B = les deux)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `button` | Choix | `a` | Choix: `a`, `b`, `ab`, `logo` |

### Si geste

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_if_gesture` |
| **Icône** | 🤝 |
| **Catégorie** | micro:bit |

Vrai tant que la carte est dans ce geste ou cette position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `gesture` | Choix | `shake` | Choix: `shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`, `3g`, `6g`, `8g` |

### Si luminosité de la LED

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_if_pixel` |
| **Icône** | 🔍 |
| **Catégorie** | micro:bit |

Comparer la luminosité d'une LED (0 à 9) à une valeur ; par défaut, la question est « est-elle allumée ? »

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Texte | `0` |  |
| `y` | Texte | `0` |  |
| `comparison` | Choix | `>` | Choix: `<`, `<=`, `==`, `>=`, `>`, `!=`; optionnel |
| `value` | Texte | `0` | optionnel |

### Si inclinaison

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_if_tilt` |
| **Icône** | 📐 |
| **Catégorie** | micro:bit |

Comparer un axe de l'accéléromètre (milli-g, de -2048 à 2048) à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `axis` | Choix | `x` | Choix: `x`, `y`, `z` |
| `comparison` | Choix | `>` | Choix: `<`, `<=`, `==`, `>=`, `>`, `!=` |
| `value` | Texte | `300` |  |

### Jouer une mélodie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_play_melody` |
| **Icône** | 🎵 |
| **Catégorie** | micro:bit |

Jouer une mélodie intégrée (DADADADUM, ENTERTAINER, PRELUDE, ODE, NYAN, POWER_UP…) ou vos propres notes comme « C4:4 E G C5:8 R:4 » (note, octave, :durée ; R est un silence)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `melody` | Texte | `DADADADUM` | Nom d'une mélodie intégrée, ou notes séparées par des espaces |
| `tempo` | Texte | `120` | optionnel |

### Jouer une note

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_play_tone` |
| **Icône** | 🔔 |
| **Catégorie** | micro:bit |

Émettre un bip à une fréquence pendant un nombre de millisecondes. Les sons se mettent en file d'attente

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `frequency` | Texte | `440` | Hauteur en hertz (440 = la note la) |
| `duration` | Texte | `500` | optionnel |

### Lire un capteur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_read_sensor` |
| **Icône** | 📡 |
| **Catégorie** | micro:bit |

Lire un capteur de la micro:bit dans une variable de cet objet (ou une variable globale si le nom commence par « global. »)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sensor` | Choix | `accelerometer x` | Choix: `accelerometer x`, `accelerometer y`, `accelerometer z`, `acceleration strength`, `compass heading`, `light level`, `temperature`, `sound level`, `pin 0 analog`, `pin 1 analog`, `pin 2 analog` |
| `variable` | Texte | `sensor_value` | Variable qui reçoit la mesure |

### Faire défiler un texte

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_scroll_text` |
| **Icône** | 🔤 |
| **Catégorie** | micro:bit |

Faire défiler un texte sur l'écran LED. Mettez le texte entre guillemets ("Bonjour") ; sinon un tiret ou un plus est lu comme un calcul. Les lettres accentuées s'affichent en ? comme sur la vraie carte

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `text` | Texte | `"Hello"` | Texte ou expression à faire défiler |
| `delay` | Nombre | `150` | Vitesse de défilement (150 par défaut dans MicroPython); optionnel |

### Envoyer un message radio

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_radio_send` |
| **Icône** | 📻 |
| **Catégorie** | micro:bit |

Envoyer un nombre ou un texte aux autres micro:bit du même groupe (pas à celle-ci). Elles reçoivent l'événement « Message radio reçu », avec la valeur dans radio_number et radio_string. Mettez le texte entre guillemets ; il est coupé à 32 caractères

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Texte | `1` | Un nombre, une expression ou un texte entre guillemets |

### Luminosité de l'écran

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_set_brightness` |
| **Icône** | 🔆 |
| **Catégorie** | micro:bit |

Luminosité générale des LED, de 0 (éteint) à 255 (maximum)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `brightness` | Texte | `255` |  |

### Allumer une LED

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_set_pixel` |
| **Icône** | 💡 |
| **Catégorie** | micro:bit |

Allumer une LED tout de suite (x et y de 0 à 4, luminosité de 0 à 9)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Texte | `0` |  |
| `y` | Texte | `0` |  |
| `brightness` | Texte | `9` | optionnel |

### Régler le groupe radio

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_radio_set_group` |
| **Icône** | 📡 |
| **Catégorie** | micro:bit |

Choisir le groupe radio (0 à 255). Seules les micro:bit du même groupe s'entendent ; chaque carte démarre dans le groupe 0

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `group` | Texte | `0` |  |

### Afficher une image

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_show_image` |
| **Icône** | ❤️ |
| **Catégorie** | micro:bit |

Afficher une image sur les LED : un nom (HEART, HAPPY, SAD, YES, NO, ARROW_N, SKULL…) ou cinq lignes de chiffres de luminosité comme « 09090:99999:99999:09990:00900 ». Les affichages se mettent en file d'attente

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `image` | Texte | `HEART` | Nom d'une image intégrée, ou 5 lignes de 5 chiffres (0-9) séparées par des deux-points |
| `hold` | Nombre | `0` | Durée avant l'élément suivant de la file (0 = jusqu'à ce qu'autre chose s'affiche); optionnel |

### Afficher un nombre

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_show_number` |
| **Icône** | 🔢 |
| **Catégorie** | micro:bit |

Afficher un nombre : un chiffre reste fixe, un nombre plus long défile

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Texte | `0` | Nombre ou expression |

### Arrêter le son

| Propriété | Valeur |
|----------|-------|
| **Nom** | `microbit_stop_sound` |
| **Icône** | 🔇 |
| **Catégorie** | micro:bit |

Couper le haut-parleur et abandonner les sons en attente

*Paramètres:* aucun

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (21)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (6)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (14)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (3)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (18)
- [Dessin](Full-Action-Reference-Drawing_fr) (11)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (22)
- [Particules](Full-Action-Reference-Particles_fr) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_fr) (5)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
