# Fiche 2 : Couleurs

**Exemple à ouvrir :** Thymio — Activités : arène libre  ·  **Durée :** 20 minutes

## Ce que tu vas apprendre

- mélanger du **rouge**, du **vert** et du **bleu** ;
- commander les huit LED du cercle.

## 1. Le mélange des couleurs

Chaque LED de couleur est commandée par trois nombres (**red**, **green**, **blue**) entre **0** et **32**.

- [ ] Associe chaque bouton à une couleur de la LED du dessus (**Set Top LED Color**), puis teste :

| Bouton | red | green | blue | Couleur obtenue |
|---|---|---|---|---|
| **Button Forward** | 32 | 32 | 0 | ……………… |
| **Button Backward** | 32 | 16 | 0 | ……………… |
| **Button Left** | 32 | 0 | 32 | ……………… |
| **Button Right** | 0 | 32 | 32 | ……………… |

- [ ] Complète la dernière colonne en regardant le robot.

> TIP: le mélange est celui de la **lumière**, pas de la peinture : rouge + vert donne du **jaune**, et les trois à fond donnent du **blanc**.

## 2. Le cercle de huit LED

Les LED du cercle sont numérotées de **0 à 7**. Leur intensité va de **0** à **32** (une seule couleur, pas de mélange).

- [ ] Sur **Button Center**, ajoute **Set Circle LED** : **led_index = 0**, **intensity = 32**. Teste : quelle LED s'allume ?
- [ ] Ajoute d'autres actions **Set Circle LED** (index 2, 4, 6) pour allumer une LED sur deux.
- [ ] Remplace-les par une seule action **Set All Circle LEDs**, en donnant 32 aux LED 0, 2, 4, 6 et 0 aux autres.

> DONE: tu peux produire n'importe quelle couleur et dessiner un motif avec le cercle.

## Pour aller plus loin

- Trouve les nombres qui donnent un **rose** et un **vert clair**. Note-les : …………………………
- Fais un **chenille** : un bouton qui allume les LED 0 à 3 seulement.
- Combien de couleurs différentes peut-on faire avec 33 valeurs possibles pour chacun des trois nombres ? (Indice : 33 × 33 × 33.)
