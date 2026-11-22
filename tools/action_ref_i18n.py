# -*- coding: utf-8 -*-
"""Translation tables for tools/gen_action_reference.py.

Page chrome and type labels for the localized Full Action Reference. The action
names, descriptions, parameter notes, categories and event descriptions are NOT
here any more: they are the app's own tables, ``config/ui_names/<lang>.py``
(docs/CORE_NAMES_I18N_PLAN.md), so the wiki and the editor show the same names.
This module exposes views of them (``ACTIONS_FR`` etc.) in the shape the
generators expect.

Anything missing falls back to English AND is reported by the generator at
the end of its run, so a newly added action is never silently half-translated.
When you add or change an action, run the generator and fill in whatever it
lists as untranslated -- in config/ui_names.

French note: this is educational software for French-speaking students —
French strings MUST carry proper accents (é è ê à ç ù î ô …).
"""

# --------------------------------------------------------------------------- #
# Page chrome (titles, navigation, table labels, See Also)
# --------------------------------------------------------------------------- #

CHROME_FR = {
    "title": "Référence Complète des Actions",
    "nav": "*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*",
    "autogen": "> **Généré automatiquement** à partir du registre d'actions de l'IDE par "
               "`tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le "
               "générateur après avoir changé les actions. Les traductions proviennent de "
               "`tools/action_ref_i18n.py`.",
    "intro": "Cette page liste l'ensemble des **{total}** actions disponibles dans "
             "PyGameMaker, exactement telles qu'elles apparaissent dans le sélecteur "
             "d'actions de l'IDE (y compris le plugin Audio et l'extension Vue 3D). Les "
             "actions sont des commandes qui s'exécutent lorsqu'un événement se déclenche.",
    "categories": "Catégories",
    "yes": "Oui", "no": "Non",
    "params": "Paramètres", "none": "aucun",
    "c_param": "Paramètre", "c_type": "Type", "c_default": "Défaut", "c_notes": "Remarques",
    "choices": "Choix", "optional": "optionnel",
    "p_name": "Nom", "p_icon": "Icône", "p_category": "Catégorie", "p_applies": "S'applique à",
    "applies_val": "self / other / object",
    "c_property": "Propriété", "c_value": "Valeur",
    "see_also": "Voir aussi",
    "sa_events": "- [Référence des Événements](Event-Reference_fr) — les événements qui déclenchent les actions",
    "sa_preset": "- [Guide des Préréglages](Preset-Guide_fr) — quelles de ces actions le préréglage de votre projet affiche réellement dans le sélecteur Blockly et le panneau structuré Actions",
    "sa_3d": "- [Vue 3D](3D-View_fr) — les actions de vue à la première personne (raycast)",
    "sa_ext": "- [Extensions](Extensions_fr) — comment les actions de la Vue 3D sont fournies",
    "other_categories": "Autres Catégories",
    "back_to_index": "Retour à la Référence Complète des Actions",
}

CHROME_DE = {
    "title": "Vollständige Aktionsreferenz",
    "nav": "*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*",
    "autogen": "> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch "
               "`tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den "
               "Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen "
               "aus `tools/action_ref_i18n.py`.",
    "intro": "Diese Seite listet alle **{total}** in PyGameMaker verfügbaren Aktionen auf, "
             "genau so, wie sie im Aktionsauswahldialog der IDE erscheinen (einschließlich "
             "des Audio-Plugins und der 3D-Ansicht-Erweiterung). Aktionen sind Befehle, die "
             "ausgeführt werden, wenn ein Ereignis ausgelöst wird.",
    "categories": "Kategorien",
    "yes": "Ja", "no": "Nein",
    "params": "Parameter", "none": "keine",
    "c_param": "Parameter", "c_type": "Typ", "c_default": "Standard", "c_notes": "Hinweise",
    "choices": "Auswahl", "optional": "optional",
    "p_name": "Name", "p_icon": "Symbol", "p_category": "Kategorie", "p_applies": "Gilt für",
    "applies_val": "self / other / object",
    "c_property": "Eigenschaft", "c_value": "Wert",
    "see_also": "Siehe auch",
    "sa_events": "- [Ereignisreferenz](Event-Reference_de) — die Ereignisse, die Aktionen auslösen",
    "sa_preset": "- [Voreinstellungs-Leitfaden](Preset-Guide_de) — welche Aktionen jede Voreinstellung/Edition bereitstellt",
    "sa_3d": "- [3D-Ansicht](3D-View_de) — die First-Person-Raycast-Aktionen",
    "sa_ext": "- [Erweiterungen](Extensions_de) — wie die 3D-Ansicht-Aktionen bereitgestellt werden",
    "other_categories": "Weitere Kategorien",
    "back_to_index": "Zurück zur Vollständigen Aktionsreferenz",
}

# --------------------------------------------------------------------------- #
# Category names and parameter-type labels
# --------------------------------------------------------------------------- #

# Action names/descriptions, parameter notes, categories and event descriptions live in the app's
# own tables, config/ui_names (docs/CORE_NAMES_I18N_PLAN.md), so the editor and the wiki use one
# vocabulary. These are views of those tables in the shape the generators expect. To change a
# translated name, edit config/ui_names/<lang>.py, then regenerate the wiki.
from config.ui_names import language_table as _ui_names  # noqa: E402


def _actions_from_ui(lang):
    table, out = _ui_names(lang), {}
    for key, text in table.get("core.action", {}).items():
        out.setdefault(key, {})["display"] = text
    for key, text in table.get("core.action_description", {}).items():
        out.setdefault(key, {})["desc"] = text
    return out


def _events_from_ui(lang):
    return {key: {"desc": text} for key, text in _ui_names(lang).get("core.event_description", {}).items()}


for _lang in ("fr", "de", "uk", "ru", "it", "es", "pt", "sl"):
    _upper = _lang.upper()
    globals()[f"ACTIONS_{_upper}"] = _actions_from_ui(_lang)
    globals()[f"NOTES_{_upper}"] = dict(_ui_names(_lang).get("core.param_description", {}))
    globals()[f"CATEGORIES_{_upper}"] = dict(_ui_names(_lang).get("core.category", {}))
    globals()[f"EVENTS_{_upper}"] = _events_from_ui(_lang)


TYPES_FR = {
    "Number": "Nombre", "Text": "Texte", "Yes/No": "Oui/Non", "Color": "Couleur",
    "Object": "Objet", "Sprite": "Sprite", "Sound": "Son", "Room": "Salle",
    "Code": "Code", "Script": "Script", "Choice": "Choix",
    "Multiple choice": "Choix multiple", "Action list": "Liste d'actions",
}
TYPES_DE = {
    "Number": "Zahl", "Text": "Text", "Yes/No": "Ja/Nein", "Color": "Farbe",
    "Object": "Objekt", "Sprite": "Sprite", "Sound": "Sound", "Room": "Raum",
    "Code": "Code", "Script": "Skript", "Choice": "Auswahl",
    "Multiple choice": "Mehrfachauswahl", "Action list": "Aktionsliste",
}

CHROME_UK = {
    "title": "Повний довідник дій",
    "nav": "*[Головна](Home_uk) | [Посібник із пресетів](Preset-Guide_uk) | [Довідник подій](Event-Reference_uk)*",
    "autogen": "> **Згенеровано автоматично** з реєстру дій IDE за допомогою "
               "`tools/gen_action_reference.py` — не редагуйте вручну; повторно запустіть "
               "генератор після зміни дій. Переклади взято з `tools/action_ref_i18n.py`.",
    "intro": "Ця сторінка містить усі **{total}** дії, доступні в PyGameMaker, саме так, як "
             "вони відображаються в засобі вибору дій IDE (включно з плагіном Audio та "
             "розширенням 3D-вигляд). Дії — це команди, що виконуються, коли спрацьовує подія.",
    "categories": "Категорії",
    "yes": "Так", "no": "Ні",
    "params": "Параметри", "none": "немає",
    "c_param": "Параметр", "c_type": "Тип", "c_default": "За замовч.", "c_notes": "Примітки",
    "choices": "Варіанти", "optional": "необов'язково",
    "p_name": "Назва", "p_icon": "Значок", "p_category": "Категорія", "p_applies": "Застосовується до",
    "applies_val": "self / other / object",
    "c_property": "Властивість", "c_value": "Значення",
    "see_also": "Дивіться також",
    "sa_events": "- [Довідник подій](Event-Reference_uk) — події, що запускають дії",
    "sa_preset": "- [Посібник із пресетів](Preset-Guide_uk) — які дії надає кожен пресет/видання",
    "sa_3d": "- [3D-вигляд](3D-View_uk) — дії першоособового виду (raycast)",
    "sa_ext": "- [Розширення](Extensions_uk) — як надаються дії 3D-вигляду",
    "other_categories": "Інші Категорії",
    "back_to_index": "Назад до Повного Довідника Дій",
}


TYPES_UK = {
    "Number": "Число", "Text": "Текст", "Yes/No": "Так/Ні", "Color": "Колір",
    "Object": "Об'єкт", "Sprite": "Спрайт", "Sound": "Звук", "Room": "Кімната",
    "Code": "Код", "Script": "Скрипт", "Choice": "Вибір",
    "Multiple choice": "Множинний вибір", "Action list": "Список дій",
}


CHROME_RU = {
    "title": "Полный справочник действий",
    "nav": "*[Главная](Home_ru) | [Руководство по пресетам](Preset-Guide_ru) | [Справочник событий](Event-Reference_ru)*",
    "autogen": "> **Сгенерировано автоматически** из реестра действий IDE с помощью "
               "`tools/gen_action_reference.py` — не редактируйте вручную; повторно запустите "
               "генератор после изменения действий. Переводы взяты из `tools/action_ref_i18n.py`.",
    "intro": "На этой странице перечислены все **{total}** действия, доступные в PyGameMaker, "
             "именно так, как они отображаются в средстве выбора действий IDE (включая плагин "
             "Audio и расширение 3D-вид). Действия — это команды, которые выполняются при "
             "срабатывании события.",
    "categories": "Категории",
    "yes": "Да", "no": "Нет",
    "params": "Параметры", "none": "нет",
    "c_param": "Параметр", "c_type": "Тип", "c_default": "По умолч.", "c_notes": "Примечания",
    "choices": "Варианты", "optional": "необязательно",
    "p_name": "Имя", "p_icon": "Значок", "p_category": "Категория", "p_applies": "Применяется к",
    "applies_val": "self / other / object",
    "c_property": "Свойство", "c_value": "Значение",
    "see_also": "См. также",
    "sa_events": "- [Справочник событий](Event-Reference_ru) — события, запускающие действия",
    "sa_preset": "- [Руководство по пресетам](Preset-Guide_ru) — какие действия предоставляет каждый пресет/издание",
    "sa_3d": "- [3D-вид](3D-View_ru) — действия вида от первого лица (raycast)",
    "sa_ext": "- [Расширения](Extensions_ru) — как предоставляются действия 3D-вида",
    "other_categories": "Другие Категории",
    "back_to_index": "Назад к Полному Справочнику Действий",
}


TYPES_RU = {
    "Number": "Число", "Text": "Текст", "Yes/No": "Да/Нет", "Color": "Цвет",
    "Object": "Объект", "Sprite": "Спрайт", "Sound": "Звук", "Room": "Комната",
    "Code": "Код", "Script": "Скрипт", "Choice": "Выбор",
    "Multiple choice": "Множественный выбор", "Action list": "Список действий",
}


CHROME_IT = {
    "title": "Riferimento completo delle azioni",
    "nav": "*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*",
    "autogen": "> **Generato automaticamente** dal registro delle azioni dell'IDE tramite "
               "`tools/gen_action_reference.py` — non modificare a mano; riesegui il "
               "generatore dopo aver cambiato le azioni. Le traduzioni provengono da "
               "`tools/action_ref_i18n.py`.",
    "intro": "Questa pagina elenca tutte le **{total}** azioni disponibili in PyGameMaker, "
             "esattamente come appaiono nel selettore di azioni dell'IDE (incluso il plugin "
             "Audio e l'estensione Vista 3D). Le azioni sono comandi che vengono eseguiti "
             "quando si attiva un evento.",
    "categories": "Categorie",
    "yes": "Sì", "no": "No",
    "params": "Parametri", "none": "nessuno",
    "c_param": "Parametro", "c_type": "Tipo", "c_default": "Predef.", "c_notes": "Note",
    "choices": "Scelte", "optional": "facoltativo",
    "p_name": "Nome", "p_icon": "Icona", "p_category": "Categoria", "p_applies": "Si applica a",
    "applies_val": "self / other / object",
    "c_property": "Proprietà", "c_value": "Valore",
    "see_also": "Vedi anche",
    "sa_events": "- [Riferimento eventi](Event-Reference_it) — gli eventi che attivano le azioni",
    "sa_preset": "- [Guida ai preset](Preset-Guide_it) — quali azioni espone ogni preset/edizione",
    "sa_3d": "- [Vista 3D](3D-View_it) — le azioni della vista in prima persona (raycast)",
    "sa_ext": "- [Estensioni](Extensions_it) — come vengono fornite le azioni della Vista 3D",
    "other_categories": "Altre Categorie",
    "back_to_index": "Torna al Riferimento Completo delle Azioni",
}


TYPES_IT = {
    "Number": "Numero", "Text": "Testo", "Yes/No": "Sì/No", "Color": "Colore",
    "Object": "Oggetto", "Sprite": "Sprite", "Sound": "Suono", "Room": "Stanza",
    "Code": "Codice", "Script": "Script", "Choice": "Scelta",
    "Multiple choice": "Scelta multipla", "Action list": "Elenco azioni",
}


CHROME_ES = {
    "title": "Referencia completa de acciones",
    "nav": "*[Inicio](Home_es) | [Guía de preajustes](Preset-Guide_es) | [Referencia de eventos](Event-Reference_es)*",
    "autogen": "> **Generado automáticamente** a partir del registro de acciones del IDE "
               "mediante `tools/gen_action_reference.py` — no editar a mano; vuelve a ejecutar "
               "el generador tras cambiar las acciones. Las traducciones provienen de "
               "`tools/action_ref_i18n.py`.",
    "intro": "Esta página enumera todas las **{total}** acciones disponibles en PyGameMaker, "
             "exactamente como aparecen en el selector de acciones del IDE (incluido el "
             "complemento Audio y la extensión Vista 3D). Las acciones son comandos que se "
             "ejecutan cuando se activa un evento.",
    "categories": "Categorías",
    "yes": "Sí", "no": "No",
    "params": "Parámetros", "none": "ninguno",
    "c_param": "Parámetro", "c_type": "Tipo", "c_default": "Predet.", "c_notes": "Notas",
    "choices": "Opciones", "optional": "opcional",
    "p_name": "Nombre", "p_icon": "Icono", "p_category": "Categoría", "p_applies": "Se aplica a",
    "applies_val": "self / other / object",
    "c_property": "Propiedad", "c_value": "Valor",
    "see_also": "Véase también",
    "sa_events": "- [Referencia de eventos](Event-Reference_es) — los eventos que activan las acciones",
    "sa_preset": "- [Guía de preajustes](Preset-Guide_es) — qué acciones expone cada preajuste/edición",
    "sa_3d": "- [Vista 3D](3D-View_es) — las acciones de vista en primera persona (raycast)",
    "sa_ext": "- [Extensiones](Extensions_es) — cómo se proporcionan las acciones de la Vista 3D",
    "other_categories": "Otras Categorías",
    "back_to_index": "Volver a la Referencia Completa de Acciones",
}


TYPES_ES = {
    "Number": "Número", "Text": "Texto", "Yes/No": "Sí/No", "Color": "Color",
    "Object": "Objeto", "Sprite": "Sprite", "Sound": "Sonido", "Room": "Sala",
    "Code": "Código", "Script": "Script", "Choice": "Elección",
    "Multiple choice": "Elección múltiple", "Action list": "Lista de acciones",
}


CHROME_PT = {
    "title": "Referência completa de ações",
    "nav": "*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*",
    "autogen": "> **Gerado automaticamente** a partir do registro de ações do IDE via "
               "`tools/gen_action_reference.py` — não edite manualmente; execute novamente o "
               "gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.",
    "intro": "Esta página lista todas as **{total}** ações disponíveis no PyGameMaker, "
             "exatamente como aparecem no seletor de ações do IDE (incluindo o plugin Audio e "
             "a extensão Vista 3D). Ações são comandos que são executados quando um evento é "
             "acionado.",
    "categories": "Categorias",
    "yes": "Sim", "no": "Não",
    "params": "Parâmetros", "none": "nenhum",
    "c_param": "Parâmetro", "c_type": "Tipo", "c_default": "Padrão", "c_notes": "Notas",
    "choices": "Opções", "optional": "opcional",
    "p_name": "Nome", "p_icon": "Ícone", "p_category": "Categoria", "p_applies": "Aplica-se a",
    "applies_val": "self / other / object",
    "c_property": "Propriedade", "c_value": "Valor",
    "see_also": "Veja também",
    "sa_events": "- [Referência de eventos](Event-Reference_pt) — os eventos que acionam as ações",
    "sa_preset": "- [Guia de predefinições](Preset-Guide_pt) — quais ações cada predefinição/edição expõe",
    "sa_3d": "- [Vista 3D](3D-View_pt) — as ações de vista em primeira pessoa (raycast)",
    "sa_ext": "- [Extensões](Extensions_pt) — como as ações da Vista 3D são fornecidas",
    "other_categories": "Outras Categorias",
    "back_to_index": "Voltar à Referência Completa de Ações",
}


TYPES_PT = {
    "Number": "Número", "Text": "Texto", "Yes/No": "Sim/Não", "Color": "Cor",
    "Object": "Objeto", "Sprite": "Sprite", "Sound": "Som", "Room": "Sala",
    "Code": "Código", "Script": "Script", "Choice": "Escolha",
    "Multiple choice": "Escolha múltipla", "Action list": "Lista de ações",
}


CHROME_SL = {
    "title": "Popolna referenca dejanj",
    "nav": "*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*",
    "autogen": "> **Samodejno ustvarjeno** iz registra dejanj IDE z "
               "`tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova "
               "zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.",
    "intro": "Ta stran navaja vseh **{total}** dejanj, ki so na voljo v PyGameMaker, natanko "
             "tako, kot so prikazana v izbirniku dejanj IDE (vključno z vtičnikom Audio in "
             "razširitvijo Pogled 3D). Dejanja so ukazi, ki se izvedejo, ko se sproži dogodek.",
    "categories": "Kategorije",
    "yes": "Da", "no": "Ne",
    "params": "Parametri", "none": "brez",
    "c_param": "Parameter", "c_type": "Vrsta", "c_default": "Privzeto", "c_notes": "Opombe",
    "choices": "Izbire", "optional": "neobvezno",
    "p_name": "Ime", "p_icon": "Ikona", "p_category": "Kategorija", "p_applies": "Velja za",
    "applies_val": "self / other / object",
    "c_property": "Lastnost", "c_value": "Vrednost",
    "see_also": "Glejte tudi",
    "sa_events": "- [Referenca dogodkov](Event-Reference_sl) — dogodki, ki sprožijo dejanja",
    "sa_preset": "- [Vodnik po prednastavitvah](Preset-Guide_sl) — katera dejanja izpostavlja vsaka prednastavitev/izdaja",
    "sa_3d": "- [Pogled 3D](3D-View_sl) — dejanja pogleda iz prve osebe (raycast)",
    "sa_ext": "- [Razširitve](Extensions_sl) — kako so zagotovljena dejanja Pogleda 3D",
    "other_categories": "Druge Kategorije",
    "back_to_index": "Nazaj na Popolno Referenco Dejanj",
}


TYPES_SL = {
    "Number": "Število", "Text": "Besedilo", "Yes/No": "Da/Ne", "Color": "Barva",
    "Object": "Predmet", "Sprite": "Sprite", "Sound": "Zvok", "Room": "Soba",
    "Code": "Koda", "Script": "Skripta", "Choice": "Izbira",
    "Multiple choice": "Večkratna izbira", "Action list": "Seznam dejanj",
}


# --------------------------------------------------------------------------- #
# EN_OVERRIDES -- English translations for the one action module NOT authored
# English-first: extensions/multiplayer_lan/actions.py's display_name/
# description/ActionParameter.description are the live French UI text
# (docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 7.4). Every other action's "en"
# edition is a pass-through of its own (English) source text -- gen_action_
# reference.py's Tr.display()/Tr.desc()/Tr.note() consult this table ONLY
# when lang == "en", keyed by action name (display/desc) or by
# (action_name, param_name) (notes, since a French source string has no
# natural English key other languages' NOTES_XX tables could share).
# --------------------------------------------------------------------------- #

# The English edition used to override the LAN multiplayer actions, which were authored French-first.
# They are authored in English now (docs/CORE_NAMES_I18N_PLAN.md D2), and the overrides had drifted
# from the IDE's own English ("Host Game" vs "Host a Game"), so the English wiki now shows the live
# text. The hook stays for any future French-first source.
EN_OVERRIDES = {"categories": {}, "actions": {}, "notes": {}}

LANGS = {
    "fr": {"chrome": CHROME_FR, "categories": CATEGORIES_FR, "types": TYPES_FR,
           "actions": ACTIONS_FR, "notes": NOTES_FR, "events": EVENTS_FR},
    "de": {"chrome": CHROME_DE, "categories": CATEGORIES_DE, "types": TYPES_DE,
           "actions": ACTIONS_DE, "notes": NOTES_DE, "events": EVENTS_DE},
    "uk": {"chrome": CHROME_UK, "categories": CATEGORIES_UK, "types": TYPES_UK,
           "actions": ACTIONS_UK, "notes": NOTES_UK, "events": EVENTS_UK},
    "ru": {"chrome": CHROME_RU, "categories": CATEGORIES_RU, "types": TYPES_RU,
           "actions": ACTIONS_RU, "notes": NOTES_RU, "events": EVENTS_RU},
    "it": {"chrome": CHROME_IT, "categories": CATEGORIES_IT, "types": TYPES_IT,
           "actions": ACTIONS_IT, "notes": NOTES_IT, "events": EVENTS_IT},
    "es": {"chrome": CHROME_ES, "categories": CATEGORIES_ES, "types": TYPES_ES,
           "actions": ACTIONS_ES, "notes": NOTES_ES, "events": EVENTS_ES},
    "pt": {"chrome": CHROME_PT, "categories": CATEGORIES_PT, "types": TYPES_PT,
           "actions": ACTIONS_PT, "notes": NOTES_PT, "events": EVENTS_PT},
    "sl": {"chrome": CHROME_SL, "categories": CATEGORIES_SL, "types": TYPES_SL,
           "actions": ACTIONS_SL, "notes": NOTES_SL, "events": EVENTS_SL},
}


# --------------------------------------------------------------------------- #
# micro:bit extension (docs/MICROBIT_EXTENSION_PLAN.md, Stage S12).
# French action names/descriptions come from the extension's OWN table, the
# one the Blockly canvas uses, so the wiki and the editor cannot disagree.
# Only French so far; the other languages fall back to the English schema text
# (the generator reports them as untranslated).
# --------------------------------------------------------------------------- #

from extensions.microbit.translations import PLUGIN_GENERATED_BLOCK_TRANSLATIONS as _MB_TR

for _name, _languages in _MB_TR["actions"].items():
    ACTIONS_FR[_name] = {"display": _languages["fr"]["display_name"],
                         "desc": _languages["fr"]["description"]}

CATEGORIES_FR["micro:bit"] = "micro:bit"


